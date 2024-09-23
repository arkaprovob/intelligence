import logging
import threading
import time
from typing import Union, List, Dict

import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from tenacity import retry, stop_after_attempt, wait_exponential

from util import get_config_value
from vector_store import sparse_doc_vectors, sparse_query_vectors

class DataStore:
    """
       DataStore: A resilient and self-managing interface for Qdrant vector database.

       This class provides a connection to a Qdrant vector database, implementing
        resilience and management features:

       1. Singleton-like behavior: One instance per collection name.
       2. Automatic connection management:
          - Retries connection attempts with exponential backoff.
          - Periodic health checks and automatic reconnection.
       3. Self-destruction after inactivity:
          - Closes connection after 5 minutes of inactivity by default.
       4. Thread-safe operations.
       5. Support for both synchronous and asynchronous clients.

       Main methods:
       - get_index(): Retrieves the VectorStoreIndex for the collection.
       - get_storage_context(): Gets the StorageContext for the collection.
       - get_list_of_collections(excerpt): Lists collections matching the given excerpt.
       - close(): Manually close the connection.
       - close_all(): Class method to close all active connections.

       The class implements automatic retries on connection failures, periodic health checks,
       and reconnection attempts in case of lost connections, making it resilient to
       temporary network issues or database unavailability.

       Usage:
           ds = DataStore("my_collection")
           index = ds.get_index()
           # Use index for operations...

       Note: Inactivity timeout and other parameters can be customized during instantiation.
       """

    _instances: Dict[str, 'DataStore'] = {}
    _lock = threading.Lock()

    def __new__(cls, collection_name: str, async_support: bool = False, host: str = None, port: int = None,
                inactivity_timeout: int = 600):
        """
        Implements the singleton pattern for DataStore instances.
        Ensures only one instance per collection name is created or an existing one is returned.
        """

        with cls._lock:
            instance = cls._instances.get(collection_name)
            if instance is None or not instance.is_connected():
                instance = super().__new__(cls)
                cls._instances[collection_name] = instance
                instance.__init__(collection_name, async_support, host, port, inactivity_timeout)
            return instance

    def __init__(self, collection_name: str, async_support: bool = False, host: str = None, port: int = None,
                 inactivity_timeout: int = 300):
        """
        Initializes the DataStore instance with the given parameters.
        Sets up the connection, inactivity timer, and health check.
        """
        if hasattr(self, 'initialized'):
            return
        self.collection_name = collection_name
        self.host = host or get_config_value("QDRANT_HOST")
        self.port = port or get_config_value("QDRANT_PORT")
        self.async_support = async_support
        self.db_client = None
        self.vector_store = None
        self.storage_context = None
        self.last_activity_time = time.time()
        self.inactivity_timeout = inactivity_timeout
        self.timer = None
        self.lock = threading.Lock()
        self._connect()
        self._start_inactivity_timer()
        self._start_health_check()
        self.initialized = True

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _connect(self):
        """
        Establishes a connection to the Qdrant database.
        Implements retry logic for resilience against temporary connection issues.
        """
        try:
            print("attempt to connect to the vector db")
            self.db_client = self._instantiate_client()
            self.vector_store = self._init_vector_store(self.collection_name)
            self.storage_context = self._init_storage_context()
        except Exception as e:
            logging.error(f"Error connecting to database: {e}", exc_info=True)
            raise

    def _instantiate_client(self) -> Union[QdrantClient, qdrant_client.AsyncQdrantClient]:
        """
        Creates and returns either a synchronous or asynchronous Qdrant client based on the configuration.
        """
        try:
            if self.async_support:
                return qdrant_client.AsyncQdrantClient(host=self.host, port=self.port)
            else:
                return QdrantClient(host=self.host, port=self.port)
        except Exception as e:
            logging.error(f"Error instantiating client: {e}", exc_info=True)
            raise

    def _init_vector_store(self, collection: str) -> QdrantVectorStore:
        """
            This function would be pretty costly with respect to resources during embedding
            depending on the size of the document. In the future, the scope of improvement would
            be making it asynchronous so it does not block the call and prevent users from
            using the other APIs.

            Also, since the hybrid retrieval strategy with sparse vector is on and with the
            increase in dimension will result in a prolific retrieval accuracy at the same
            time it will take a huge toll on resources and ingestion process would be time
            consuming. For the time being, to keep things manageable, I am using a weak
            embedding model with 384 dimension, yet to test on a large embedding model with
            1024 dimension eg: `BAAI/bge-large-en-v1.5`.
            """
        try:
            if not self.db_client.collection_exists(collection):
                self.db_client.create_collection(
                    collection_name=collection,
                    vectors_config={
                        "text-dense": models.VectorParams(
                            size=384,
                            # todo Automate embedding model vector size calculation to avoid dimension mismatches.
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
                                     sparse_doc_fn=sparse_doc_vectors, sparse_query_fn=sparse_query_vectors,
                                     batch_size=32,
                                     # hybrid_fusion_fn=relative_score_fusion
                                     ) #batch_size controls how many nodes are encoded with sparse vectors at once, in a better hardware the batch size can be increased,
        except Exception as e:
            logging.error(f"Error initializing vector store: {e}", exc_info=True)
            raise

    def _init_storage_context(self) -> StorageContext:
        """
        Initializes and returns the storage context using the vector store.
        """
        try:
            return StorageContext.from_defaults(vector_store=self.vector_store)
        except Exception as e:
            logging.error(f"Error initializing storage context: {e}", exc_info=True)
            raise

    def is_connected(self):
        """
        Checks if the connection to the Qdrant database is active and working.
        """
        try:
            self.db_client.get_collections()
            return True
        except:
            return False

    def _start_health_check(self):
        """
        Starts a background thread that periodically checks the database connection health.
        Attempts to reconnect if the connection is lost.
        """

        def health_check():
            while True:
                time.sleep(60)  # Check every minute
                if not self.is_connected():
                    logging.warning("Database connection lost. Attempting to reconnect...")
                    self._connect()

        threading.Thread(target=health_check, daemon=True).start()

    def _start_inactivity_timer(self):
        """
        Starts or restarts the inactivity timer.
        The timer will trigger connection closure after a period of inactivity.
        """
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.inactivity_timeout, self._close_if_inactive)
        self.timer.start()

    def _close_if_inactive(self):
        """
        Closes the connection if there has been no activity for the specified timeout period.
        Restarts the timer if there has been recent activity.
        """
        with self.lock:
            if time.time() - self.last_activity_time > self.inactivity_timeout:
                logging.info(f"Closing connection for {self.collection_name} due to inactivity")
                self.close()
            else:
                self._start_inactivity_timer()

    def _update_activity(self):
        """
        Updates the last activity timestamp and restarts the inactivity timer.
        Called before performing any operation to prevent unnecessary connection closure.
        """
        with self.lock:
            self.last_activity_time = time.time()
            self._start_inactivity_timer()

    def get_index(self) -> VectorStoreIndex:
        """
        Retrieves the VectorStoreIndex for the current collection.
        If a collection already exists then return the VectorStoreIndex against that collection
        Ensures the connection is active before returning the index.
        """
        self._update_activity()
        if not self.is_connected():
            self._connect()
        try:
            return VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
        except Exception as e:
            logging.error(f"Error getting index: {e}", exc_info=True)
            raise

    def get_storage_context(self) -> StorageContext:
        """
        Retrieves the StorageContext for the current collection.
        Ensures the connection is active before returning the context.
        """
        self._update_activity()
        if not self.is_connected():
            self._connect()
        return self.storage_context

    def get_list_of_collections(self, excerpt: str) -> List[str]:
        """
        Retrieves a list of collection names that contain the specified excerpt.
        Ensures the connection is active before querying for collections.
        """
        self._update_activity()
        if not self.is_connected():
            self._connect()
        try:
            cs = self.db_client.get_collections()
            return [cs.name for cs in cs.collections if excerpt in cs.name]
        except Exception as e:
            logging.error(f"Error getting list of collections: {e}", exc_info=True)
            raise

    def close(self):
        """
        Closes the connection to the database and cleans up resources.
        Removes the instance from the class-level instances dictionary.
        """
        with self._lock:
            if self.collection_name in self._instances:
                if self.timer:
                    self.timer.cancel()
                if isinstance(self.db_client, QdrantClient):
                    self.db_client.close()
                elif isinstance(self.db_client, qdrant_client.AsyncQdrantClient):
                    import asyncio
                    asyncio.get_event_loop().run_until_complete(self.db_client.close())
                logging.info(f"Connection closed for {self.collection_name}")
                del self._instances[self.collection_name]

    @classmethod
    def close_all(cls):
        """
        Class method to close all active DataStore connections.
        Useful for shutting down the application or freeing resources.
        """
        with cls._lock:
            for instance in list(cls._instances.values()):
                instance.close()

    def __del__(self):
        """
        Destructor to ensure the connection is closed when the object is garbage collected.
        """
        self.close()
