import logging
import threading
import time
from typing import Dict

from util import get_config_value
from tenacity import retry, stop_after_attempt, wait_exponential
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core import VectorStoreIndex, StorageContext


class MilVusStore:

    _instances: Dict[str, 'MilVusStore'] = {}
    _lock = threading.Lock()

    def __new__(cls, collection_name: str, host: str = None, port: int = None,
                inactivity_timeout: int = 600):
        with cls._lock:
            instance = cls._instances.get(collection_name)
            if instance is None or not instance.is_connected():
                instance = super().__new__(cls)
                cls._instances[collection_name] = instance
                instance.__init__(collection_name, host, port, inactivity_timeout)

    def __init__(self,collection_name: str, host: str = None, port: int = None,
                 inactivity_timeout: int = 600):
        if hasattr(self, 'initialized'):
            return
        self.collection_name = collection_name
        self.url = f"http://{host or get_config_value('MILVUS_HOST')}:{port or get_config_value('MILVUS_PORT')}"
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
        Establishes a connection to the Milvis database.
        Implements retry logic for resilience against temporary connection issues.
        """
        try:
            logging.debug("attempt to connect to the vector db")
            self.vector_store = self._init_vector_store(self.collection_name)
            self.storage_context = self._init_storage_context()
        except Exception as e:
            logging.error(f"Error connecting to database: {e}", exc_info=True)
            raise


    
    def _init_vector_store(self, collection_name:str,dim:int=384,overwrite:bool=False,
                                enable_sparse:bool=True,hybrid_ranker:str="RRFRanker",
                                hybrid_ranker_params:Dict[str,int]={"k": 60})->MilvusVectorStore:
        try:
            return MilvusVectorStore(uri=self.url,dim=dim,
                                     overwrite=overwrite,
                                     enable_sparse=enable_sparse,
                                     hybrid_ranker=hybrid_ranker,
                                     hybrid_ranker_params=hybrid_ranker_params,)
        except Exception as e:
            logging.error(f"Error instantiating client: {e}", exc_info=True)
            raise
        
    def _init_storage_context(self) -> StorageContext:
        try:
            return StorageContext.from_defaults(vector_store=self.vector_store)
        except Exception as e:
            logging.error(f"Error instantiating storage context: {e}", exc_info=True)
            raise

    def is_connected(self) -> bool  :
        try:
            self.vector_store.client.list_collections()
            return True
        except Exception as e:
            logging.error(f"Error checking connection: {e}", exc_info=True)
            return False

    def _start_health_check(self):
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


    def close(self):
        """
        Closes the connection to the database and cleans up resources.
        Removes the instance from the class-level instances dictionary.
        """
        with self._lock:
            if self.collection_name in self._instances:
                if self.timer:
                    self.timer.cancel()
                if isinstance(self.db_client, MilvusVectorStore):
                    self.db_client.close()
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