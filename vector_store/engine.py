import threading
import time
from typing import Union, List, Dict
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
from qdrant_client import QdrantClient, models
import logging
from util import get_config_value
from vector_store import sparse_doc_vectors, sparse_query_vectors

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DataStore:
    _instances: Dict[str, 'DataStore'] = {}
    _lock = threading.Lock()

    def __new__(cls, collection_name: str, async_support: bool = False, host: str = None, port: int = None,
                inactivity_timeout: int = 300):
        with cls._lock:
            if collection_name not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[collection_name] = instance
                instance.__init__(collection_name, async_support, host, port, inactivity_timeout)
            return cls._instances[collection_name]

    def __init__(self, collection_name: str, async_support: bool = False, host: str = None, port: int = None,
                 inactivity_timeout: int = 300):
        if hasattr(self, 'initialized'):
            return
        self.collection_name = collection_name
        self.host = host or get_config_value("QDRANT_HOST")
        self.port = port or get_config_value("QDRANT_PORT")
        self.async_support = async_support
        self.db_client = self._instantiate_client()
        self.vector_store = self._init_vector_store(collection_name)
        self.storage_context = self._init_storage_context()
        self.last_activity_time = time.time()
        self.inactivity_timeout = inactivity_timeout  # in seconds
        self.timer = None
        self.lock = threading.Lock()
        self._start_inactivity_timer()
        self.initialized = True

    def _instantiate_client(self) -> Union[QdrantClient, qdrant_client.AsyncQdrantClient]:
        try:
            if self.async_support:
                return qdrant_client.AsyncQdrantClient(host=self.host, port=self.port)
            else:
                return QdrantClient(host=self.host, port=self.port)
        except Exception as e:
            logger.error(f"Error instantiating client: {e}", exc_info=True)
            raise

    def _init_vector_store(self, collection: str) -> QdrantVectorStore:
        try:
            if not self.db_client.collection_exists(collection):
                self.db_client.create_collection(
                    collection_name=collection,
                    vectors_config={
                        "text-dense": models.VectorParams(
                            size=1536,  # openai vector size
                            distance=models.Distance.COSINE,
                        )
                    },
                    sparse_vectors_config={
                        "text-sparse": models.SparseVectorParams(
                            index=models.SparseIndexParams()
                        )
                    },
                )
            return QdrantVectorStore(client=self.db_client, collection_name=collection,
                                     prefer_grpc=self.async_support, enable_hybrid=True,
                                     sparse_doc_fn=sparse_doc_vectors,sparse_query_fn=sparse_query_vectors,)
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}", exc_info=True)
            raise

    def _init_storage_context(self) -> StorageContext:
        try:
            return StorageContext.from_defaults(vector_store=self.vector_store)
        except Exception as e:
            logger.error(f"Error initializing storage context: {e}", exc_info=True)
            raise

    def _start_inactivity_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.inactivity_timeout, self._close_if_inactive)
        self.timer.start()

    def _close_if_inactive(self):
        with self.lock:
            if time.time() - self.last_activity_time > self.inactivity_timeout:
                logger.info(f"Closing connection for {self.collection_name} due to inactivity")
                self.close()
            else:
                self._start_inactivity_timer()

    def _update_activity(self):
        with self.lock:
            self.last_activity_time = time.time()
            self._start_inactivity_timer()

    def get_index(self) -> VectorStoreIndex:
        self._update_activity()
        try:
            return VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
        except Exception as e:
            logger.error(f"Error getting index: {e}", exc_info=True)
            raise

    def get_storage_context(self) -> StorageContext:
        self._update_activity()
        return self.storage_context

    def get_list_of_collections(self, excerpt: str) -> List[str]:
        self._update_activity()
        try:
            cs = self.db_client.get_collections()
            return [cs.name for cs in cs.collections if excerpt in cs.name]
        except Exception as e:
            logger.error(f"Error getting list of collections: {e}", exc_info=True)
            raise

    def close(self):
        with self._lock:
            if self.collection_name in self._instances:
                if self.timer:
                    self.timer.cancel()
                if isinstance(self.db_client, QdrantClient):
                    self.db_client.close()
                elif isinstance(self.db_client, qdrant_client.AsyncQdrantClient):
                    import asyncio
                    asyncio.get_event_loop().run_until_complete(self.db_client.close())
                logger.info(f"Connection closed for {self.collection_name}")
                del self._instances[self.collection_name]

    @classmethod
    def close_all(cls):
        with cls._lock:
            for instance in list(cls._instances.values()):
                instance.close()

    def __del__(self):
        self.close()
