import uuid

import llama_index.core as lc
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import IndexNode
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.vector_stores.milvus import MilvusVectorStore

lc.set_global_handler("simple")

# load documents
documents = SimpleDirectoryReader(
    input_files=["/Users/arbhatta/Documents/2024/instructlab-fusion/intelligence/backup_docs/Spaship_FAQ.md"]
).load_data()

print("Document ID:", documents[0].doc_id)

vector_store = MilvusVectorStore(
    uri="http://localhost:19530", dim=384, overwrite=True
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
embedding = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5",
                                 cache_dir=None)



llm: LlamaCPP = LlamaCPP(
                model_path="/Users/arbhatta/Documents/2024/instructlab-fusion/intelligence/model/gemma-2b_it_v2.gguf",
                temperature=0.1,
                max_new_tokens=360,
                context_window=2048,
                verbose=False,
                # callback_manager=CallbackManager([LlamaDebugHandler(print_trace_on_end=True)])
            )

splitter = SentenceSplitter(chunk_size=256, chunk_overlap=35)
nodes = splitter.get_nodes_from_documents(documents)
final_nodes = []

for node in nodes:
    node.metadata["custom"] = "custom metadata"
    final_node = IndexNode(
        text=node.text or "None",
        index_id=str(uuid.uuid4()),
        metadata=node.metadata
    )
    final_nodes.append(final_node)

print(f" no of nodes are {len(final_nodes)}")

# for fn in final_nodes:
#     print(fn)

# Ingestion starts here, it's not a part of the database
index = VectorStoreIndex(
    final_nodes, storage_context=storage_context, embed_model=embedding
)
query_engine = index.as_query_engine(llm = llm,streaming=True, similarity_top_k=2)
streaming_response = query_engine.query("contribution")
# for text in streaming_response.response_gen:
#     print(text)
streaming_response.print_response_stream()