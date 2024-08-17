import os
import tempfile
import time
import traceback
from contextlib import asynccontextmanager
from typing import Optional, List

from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from huggingface_hub import notebook_login
from pydantic import BaseModel
from fastapi import FastAPI, Body, HTTPException, UploadFile, File, Form, Query as FQuery
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from appstate import init_database, db_manager, feedback, application

from cache import RedisCache
from ingestion import read_docs_bot_file, Ingestion

from fastapi.staticfiles import StaticFiles

import ssl

from llm import LLMPool
from qna.query_setup import QueryEngineSetup


import json

import logging
import sys

from util import get_config_value, get_services_status
from vector_store import DataStore

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
import llama_index.core

llama_index.core.set_global_handler("simple")


class Query(BaseModel):
    query: str


class FeedbackRequest(BaseModel):
    answer: str
    feedback: int
    question: str
    user: str
    description: str


class CacheRecord(BaseModel):
    question: str
    response: str
    metadata: Optional[dict] = None
    workspace: str

class Application(BaseModel):
    name: str
    domain: str
    tag: str
    hidden: bool = False

cert_file = get_config_value("SSL_CERT_PATH")
key_file = get_config_value("SSL_KEY_PATH")
no_of_llm_instances = get_config_value("NO_OF_LLM_INSTANCES")
print(f"no_of_llm_instances : {no_of_llm_instances}")

cache_dir = get_config_value("CACHE_DIR")

embed_model = FastEmbedEmbedding(model_name=get_config_value("EMBEDDING_MODEL"),
                                 cache_dir=cache_dir)
Settings.embed_model = embed_model
model_name = get_config_value("INFERENCING_MODEL")
notebook_login()
model_url = get_config_value("MODEL_URL")

llm_pool = LLMPool(
    num_instances=no_of_llm_instances,
    model_url=model_url,
    model_path=get_config_value("MODEL_PATH")
)

# todo check if this llm param can set in settings and use it from there instead of explicitly passing it
ingestion_engine: Ingestion = None  # Will be initialized in lifespan
query_engine: QueryEngineSetup = None  # Will be initialized in lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await llm_pool.initialize()
    await init_database()  # Initialize and set up the database
    global query_engine
    global ingestion_engine
    try:
        query_engine = QueryEngineSetup(llm_pool)
        ingestion_engine = Ingestion(llm_pool=llm_pool)
        yield
    finally:
        print("Executing cleanup code")
        await db_manager.close()  # Close the database connection pool


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

if cert_file is not None or key_file is not None:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('cert.pem', keyfile='key.pem')
else:
    print("SSL files not found, proceeding without SSL configuration.")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    return get_services_status()


@app.post('/query-stream/')
async def stream(query: Query = Body(...)):
    return {"status": "UP", "message": "method not supported use get instead"}


@app.get('/query-stream/')
async def stream(query: str = None, workspace: str = "spaship_docs", nocache: int = 1):
    logging.info("wow it working")
    if not query:
        return {"error": "Query parameter is required."}
    if not workspace:
        return {"error": "Collection name is required."}

    try:
        if nocache == 0:
            cache_result = await RedisCache(
                name=workspace, prefix="{}-{}".format("db", workspace)
            ).find_similar(query)

            if cache_result is not None:
                # return cached result instead of querying the lm
                return StreamingResponse(cache_result, media_type='text/event-stream')

        ds = DataStore(workspace)
        return StreamingResponse(query_engine.generate_answer(query, ds.get_index()),  # todo fix the intellisense issue
                                 media_type='text/event-stream')
    except Exception as e:
        logging.error(f"Error in stream endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.post('/cache')
async def insert_into_redis_cache(cache_record: CacheRecord):
    try:
        cache = RedisCache(name=cache_record.workspace, prefix="{}-{}".format("db", cache_record.workspace))
        cache.store(cache_record.question, cache_record.response, cache_record.metadata)
    except Exception as e:
        logging.error(f"Error inserting into cache: {str(e)}")


@app.post("/feedback")
async def save_feedback(feedback_request: FeedbackRequest):
    try:
        await  feedback.save(
            user_question=feedback_request.question, answer=feedback_request.answer,
            feedback=feedback_request.feedback, user=feedback_request.user, description=feedback_request.description
        )
        return {"status": "success", "data": feedback_request}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.post("/ingest/file")
async def ingest_documents(
        file: UploadFile = File(...),
        use_node_parser: Optional[bool] = Form(True),
        async_support: Optional[bool] = Form(False),
        collection_name: str = Form(...),
        metadata: Optional[str] = Form(None)
):
    try:
        # Create a temporary directory to store the uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file to the temporary directory
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            # Create documents using SimpleDirectoryReader
            docs = read_docs_bot_file(file_path)

            # apply metadata to the documents
            if metadata and len(metadata) > 0:
                try:
                    metadata_dict = json.loads(metadata)
                    for doc in docs:
                        if not hasattr(doc, 'metadata'):
                            doc.metadata = {}
                        for key, value in metadata_dict.items():
                            doc.metadata[key] = value
                except json.JSONDecodeError:
                    print("Error: Metadata is not a valid JSON string.")

        # Perform ingestion
        await ingestion_engine.ingest_documents(
            documents=docs,
            use_node_parser=use_node_parser,
            async_support=async_support,
            show_progress=True,
            bucket=DataStore(collection_name)
        )

        return {"status": "success", "message": "Documents ingested successfully"}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"something went wrong in the backend; please contact with the "
                                                    f"app dev team with this {time.time()} for more details")


@app.get("/ingest/file")
async def ingest_documents(workspace: str = "spaship_docs"):
    try:
        docs = read_docs_bot_file()

        # Perform ingestion
        await ingestion_engine.ingest_documents(
            documents=docs,
            bucket=DataStore(workspace)
        )

        return {"status": "success", "message": "Documents ingested successfully"}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"something went wrong in the backend; please contact with the "
                                                    f"app dev team with this {time.time()} for more details")


@app.get('/collections')
async def get_collections(query: str = FQuery(...)):
    try:
        store = DataStore("none")
        collections = store.get_list_of_collections(query)
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@app.post("/application")
async def create_application(app_data: Application):
    try:
        await application.save(
            name=app_data.name,
            domain=app_data.domain,
            tag=app_data.tag,
            hidden=app_data.hidden
        )
        return {"message": f"Application '{app_data.name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while creating the application")


@app.get("/application", response_model=List[Application])
async def get_applications():
    try:
        applications = await application.fetch()
        return [Application(**app) for app in applications]
    except Exception as e:
        # TODO log the error here if you have a logging system set up
        raise HTTPException(status_code=500, detail="An error occurred while fetching applications")

@app.delete("/application/{name}")
async def delete_application(name: str):
    try:
        await application.delete(name)
        return {"message": f"Application '{name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the application")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app",host="0.0.0.0", port=8000, log_config=None, log_level="info")
