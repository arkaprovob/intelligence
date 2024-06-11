from llama_index.core import SimpleDirectoryReader

from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
# from llama_index.core import PromptTemplate
from huggingface_hub import notebook_login
from llama_index.llms.llama_cpp import LlamaCPP
from transformers import AutoTokenizer

from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from llama_index.core.postprocessor import SentenceTransformerRerank
import time
# from llama_index.core import set_global_tokenizer
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

documents = SimpleDirectoryReader(
    "/home/arko/PycharmProjects/intelligence/test_resources").load_data()
cache_dir = "/media/arko/work/.hfcache"

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_dir=cache_dir)
Settings.embed_model = embed_model
Settings.chunk_size = 512

system_prompt = ("You are a Q&A assistant. Your goal is to answer questions as accurately as "
                 "possible based on the instructions and context provided."
                 "If the required information is not available in the provided context, "
                 "you should inform the user at the end of your response that a ticket will be "
                 "created for further investigation."
                 )


# This will wrap the default prompts that are internal to llama-index
def completion_to_prompt(completion):
    return f"<|USER|>{completion}<|ASSISTANT|>"


notebook_login()

# model_name = "meta-llama/Meta-Llama-3-70B-Instruct"
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    cache_dir=cache_dir
)
stopping_ids = [
    tokenizer.eos_token,
    "<|eot_id|>",
]
print(f'stopping_ids are : {stopping_ids}')
model_url = "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q5_K_S.gguf?download=true"

llm = LlamaCPP(
    model_url=model_url,
    model_path=None,
    temperature=0.1,
    max_new_tokens=256,
    context_window=8192,
    generate_kwargs={"stop": stopping_ids},
    model_kwargs={"n_gpu_layers": 0},
    system_prompt=system_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True
)
Settings.llm = llm
Settings.chunk_size = 512

client = QdrantClient(host="localhost", port=6333)

vector_store = QdrantVectorStore(client=client, collection_name="spaship_docs")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context,
                                        embed_model=embed_model)

rerank = SentenceTransformerRerank(model="cross-encoder/ms-marco-MiniLM-L-2-v2", top_n=3)
query_engine = index.as_query_engine(similarity_top_k=10, streaming=True, node_postprocessors=[
    rerank],
                                     llm=llm)


def generate_answer(query):
    now = time.time()
    response = query_engine.query(query)
    for text in response.response_gen:
        print(text)
    print(f"\nElapsed: {round(time.time() - now, 2)}s")


while True:
    user_query = input("Please enter your query (or type 'exit' to quit): ")
    if user_query.lower() == 'exit':
        break
    now = time.time()
    generate_answer(user_query)
    print(f"\nElapsed: {round(time.time() - now, 2)}s")
    print("\n--- End of Response ---")
