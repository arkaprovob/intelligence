from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from huggingface_hub import notebook_login
from pydantic import BaseModel
from qdrant_client import QdrantClient
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

from prompt import PromptProvider
from llama_index_query_engine import QueryEngineProvider
from store import IndexProvider
from fastapi.staticfiles import StaticFiles


class Query(BaseModel):
    query: str


documents = SimpleDirectoryReader(
    "/home/arko/PycharmProjects/intelligence/test_resources").load_data()
cache_dir = "/media/arko/work/.hfcache"
embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_dir=cache_dir)
Settings.embed_model = embed_model
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
notebook_login()
model_url = "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q5_K_S.gguf?download=true"
client = QdrantClient(host="localhost", port=6333)

prompt_provider = PromptProvider(model_name, cache_dir)
index_provider = IndexProvider(documents, client, "spaship_docs", embed_model)
query_engine_provider = QueryEngineProvider(model_url, prompt_provider.get_system_prompt(),
                                            prompt_provider.completion_to_prompt,
                                            prompt_provider.get_stopping_ids(),
                                            index_provider.get_index(), embed_model)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post('/query-stream/')
async def stream(query: Query = Body(...)):
    return StreamingResponse(query_engine_provider.generate_answer(query.query),
                             media_type='text/event-stream')
