import asyncio
import json
import re
import threading
import time
from typing import Optional

from redisvl.extensions.llmcache import SemanticCache
from redisvl.utils.vectorize import HFTextVectorizer

from util import get_config_value
from util.utility import configure_logging


class RedisCache:
    """
    A class for managing Redis-based semantic caches.

    This class ensures that only one instance of the cache is created and used
    for each unique combination of name and prefix. It provides methods for
    storing, retrieving, and managing cache entries using the SemanticCache
    from redisvl.extensions.llmcache.

    The class also implements an idle timer that destroys instances that have
    been inactive for more than 2 hours.

    Usage:
        cache = RedisCache(name="cache1", prefix="prefix1")  # Creates a new instance or returns an existing one
    """

    _instances = {}
    _lock = threading.Lock()
    configure_logging()

    def __new__(cls, name: str = "common_cache", prefix: str = "docsbot", *args, **kwargs):
        key = (name, prefix)
        with cls._lock:
            if key not in cls._instances:
                print(f"Creating new cache instance for {name} with prefix {prefix}")
                instance = super(RedisCache, cls).__new__(cls)
                cls._instances[key] = instance
            return cls._instances[key]

    def __init__(self, name: str = "docsbot_cache", prefix: str = "docsbot_cache",
                 redis_url: str = f"redis://{get_config_value('REDIS_HOST')}:{get_config_value('REDIS_PORT')}",
                 distance_threshold=0.06, vectorizer=None):
        # need to be strict about the value of distance_threshold specially
        # when using BAAI/bge-large-en it's a powerful model hence the threshold should be low,
        # compared to the efault model
        if not hasattr(self, '_initialized'):
            self.name = name
            self.prefix = prefix

            if vectorizer is None:
                vectorizer = HFTextVectorizer(model="sentence-transformers/all-mpnet-base-v2")

            self._cache = SemanticCache(
                name=name,  # underlying search index name
                prefix=prefix,  # redis key prefix for hash entries
                redis_url=redis_url,  # redis connection url string
                distance_threshold=distance_threshold,  # semantic cache distance threshold
                vectorizer=vectorizer
            )
            # self.set_time_to_live()
            self._last_activity = time.time()
            self._timer = threading.Timer(7200, self._destroy_if_idle)
            self._timer.start()
            self._initialized = True

    def _destroy_if_idle(self):
        if time.time() - self._last_activity > 7200:  # 2 hours
            key = (self.name, self.prefix)
            with self.__class__._lock:
                if key in self.__class__._instances:
                    del self.__class__._instances[key]
        else:
            self._timer = threading.Timer(7200, self._destroy_if_idle)
            self._timer.start()

    def _reset_timer(self):
        self._last_activity = time.time()

    @property
    def cache(self):
        return self._cache

    def store(self, question: str, response: str, metadata: Optional[dict] = None):
        self._reset_timer()
        self.cache.store(prompt=question, response=response, metadata=metadata)

    async def find_similar(self, question: str, return_fields=None):
        if return_fields is None:
            return_fields = ["prompt", "response", "metadata"]
        start_time = time.time()
        response = self.cache.check(prompt=question, return_fields=return_fields)
        end_time = time.time()
        time_taken = end_time - start_time
        if not response:
            return None

        cached_response = response[0]["response"]

        async def stream_cached_response():
            # simulate streaming for cached response
            words = re.split(r'(\s+)', cached_response)

            for word in words:
                send_as = word + " "
                yield f"data: {json.dumps({'text': send_as})}\n\n"
                await asyncio.sleep(0.001)  # simulate delay between chunks

            # Send the done message
            yield f"data: {json.dumps({'time_taken': time_taken, 'done': True, 'source': 'cache'})}\n\n"

        return stream_cached_response()

    def override_cache_threshold(self, threshold):
        self._reset_timer()
        self.cache.set_threshold(threshold)

    def clear_cache(self):
        self._reset_timer()
        self.cache.clear()

    def set_time_to_live(self, ttl=3600):
        self._reset_timer()
        self.cache.set_ttl(ttl)

    def del_cache_index(self):
        self._reset_timer()
        self.cache.delete()

    def __del__(self):
        if hasattr(self, '_timer'):
            self._timer.cancel()
