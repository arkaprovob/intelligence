from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore


class IndexProvider:
    def __init__(self, documents, client, collection_name, embed_model):
        self.vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_documents(documents, storage_context=self.storage_context,
                                                     embed_model=embed_model)

    def get_index(self):
        return self.index