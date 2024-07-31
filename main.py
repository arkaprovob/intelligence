import os
import tempfile
from contextlib import asynccontextmanager
from typing import Optional

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from huggingface_hub import notebook_login
from pydantic import BaseModel
from fastapi import FastAPI, Body, HTTPException, UploadFile, File, Form, Query as FQuery
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from cache.cache_ops import RedisCache
from data_store_engine import DataStore
from llmacpp import LLMPool
from prompt import PromptProvider, completion_to_prompt
from query_engine_setup import QueryEngineSetup
from ingestion_engine import Ingestion
from fastapi.staticfiles import StaticFiles

from tinydb import TinyDB
import ssl

from utility import get_config_value
import logging
import json

import uvicorn

# Configure the logging with a specific format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Now use the logger
logger = logging.getLogger(__name__)
logger.info("Executing startup code")


class Query(BaseModel):
    query: str


class FeedbackRequest(BaseModel):
    message: str
    feedback: int
    UserQuestion: str


class CacheRecord(BaseModel):
    question: str
    response: str
    metadata: Optional[dict] = None
    workspace: str


cert_file = get_config_value("SSL_CERT_PATH")
key_file = get_config_value("SSL_KEY_PATH")
no_of_llm_instances = get_config_value("NO_OF_LLM_INSTANCES")
print(f"no_of_llm_instances : {no_of_llm_instances}")

db = get_config_value("TINY_DB_PATH")

cache_dir = get_config_value("CACHE_DIR")

embed_model = FastEmbedEmbedding(model_name=get_config_value("EMBEDDING_MODEL"),
                                 cache_dir=cache_dir)
Settings.embed_model = embed_model
model_name = get_config_value("INFERENCING_MODEL")
notebook_login()
model_url = get_config_value("MODEL_URL")

prompt_provider = PromptProvider(model_name, cache_dir=cache_dir)

llm_pool = LLMPool(
    num_instances=no_of_llm_instances,
    model_url=model_url,
    system_prompt=prompt_provider.get_system_prompt(),
    completion_to_prompt=completion_to_prompt,
    stopping_ids=prompt_provider.get_stopping_ids(),
    model_path=get_config_value("MODEL_PATH")
)

# todo check if this llm param can set in settings and use it from there instead of explicitly passing it
ingestion_engine: Ingestion = None  # Will be initialized in lifespan
query_engine: QueryEngineSetup = None  # Will be initialized in lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Executing startup code")
    # Startup
    await llm_pool.initialize()
    global query_engine
    global ingestion_engine
    try:
        query_engine = QueryEngineSetup(llm_pool)
        ingestion_engine = Ingestion(llm_pool=llm_pool)
        yield
    finally:
        print("Executing cleanup code")


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
    logger.warning("SSL files not found, proceeding without SSL configuration.")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    return {"status": "UP", "message": "Service is running"}


@app.post('/query-stream/')
async def stream(query: Query = Body(...)):
    return {"status": "UP", "message": "method not supported use get instead"}


@app.get('/query-stream/')
async def stream(query: str = None, workspace: str = "spaship_docs", nocache: int = 1):
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


@app.post("/docsbot-feedback")
async def save_feedback(feedback_request: FeedbackRequest):
    try:
        # Insert the feedback data into the TinyDB database
        db.insert(feedback_request.model_dump())
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
            docs = SimpleDirectoryReader(temp_dir).load_data()

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
        raise HTTPException(status_code=500, detail=f"An error occurred during ingestion: {str(e)}")


@app.get('/collections')
async def get_collections(query: str = FQuery(...)):
    try:
        store = DataStore("none")
        collections = store.get_list_of_collections(query)
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", log_config=None, log_level="info")
