import os

from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from huggingface_hub import notebook_login
from pydantic import BaseModel
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from llmacpp import LlamaProvider
from prompt import PromptProvider, completion_to_prompt
from llama_index_query_engine import QueryEngineProvider
from store import Ingestion
from fastapi.staticfiles import StaticFiles

from tinydb import TinyDB
import ssl

from utility import get_config_value
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


class Query(BaseModel):
    query: str


class FeedbackRequest(BaseModel):
    message: str
    feedback: int
    UserQuestion: str


cert_file = get_config_value("SSL_CERT_PATH")
key_file = get_config_value("SSL_KEY_PATH")

db = get_config_value("TINY_DB_PATH")

documents = SimpleDirectoryReader(get_config_value("SDR_DIR")).load_data()

cache_dir = get_config_value("CACHE_DIR")

embed_model = FastEmbedEmbedding(model_name=get_config_value("EMBEDDING_MODEL"),
                                 cache_dir=cache_dir)
Settings.embed_model = embed_model
model_name = get_config_value("INFERENCING_MODEL")
notebook_login()
model_url = get_config_value("MODEL_URL")

prompt_provider = PromptProvider(model_name, cache_dir=cache_dir)
llm = LlamaProvider(model_url, prompt_provider.get_system_prompt(), completion_to_prompt,
                    prompt_provider.get_stopping_ids(), model_path=get_config_value("MODEL_PATH"))

ingestion = Ingestion(documents, get_config_value("COLLECTION_NAME"),
                      embed_model, llm.get_llm(), transform=get_config_value(
        "TRANSFORM"), use_node_parser=get_config_value("USE_NODE_PARSER"))
query_engine_provider = QueryEngineProvider(llm.get_llm(),
                                            ingestion.get_index())

app = FastAPI()
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
    return StreamingResponse(query_engine_provider.generate_answer(query.query),
                             media_type='text/event-stream')


@app.get('/query-stream/')
async def stream(query: str = None):
    if not query:
        return {"error": "Query parameter is required."}
    return StreamingResponse(query_engine_provider.generate_answer(query),
                             media_type='text/event-stream')


@app.post("/docsbot-feedback")
async def save_feedback(feedback_request: FeedbackRequest):
    try:
        # Insert the feedback data into the TinyDB database
        db.insert(feedback_request.dict())
        return {"status": "success", "data": feedback_request}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
