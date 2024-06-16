from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


class IndexProvider:
    def __init__(self, documents, client, collection_name, embed_model):
        try:
            self.vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            self.index = VectorStoreIndex.from_documents(documents,
                                                         storage_context=self.storage_context,
                                                         embed_model=embed_model)
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)

    def get_index(self):
        return self.index
