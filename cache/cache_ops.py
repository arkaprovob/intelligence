from typing import Optional
from redisvl.extensions.llmcache import SemanticCache
import time
import threading


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

    def __new__(cls, name: str = "docsbot_cache", prefix: str = "docsbot_cache", *args, **kwargs):
        key = (name, prefix)
        with cls._lock:
            if key not in cls._instances:
                instance = super(RedisCache, cls).__new__(cls)
                cls._instances[key] = instance
            return cls._instances[key]

    def __init__(self, name: str = "docsbot_cache", prefix: str = "docsbot_cache",
                 redis_url: str = "redis://localhost:6379", distance_threshold=0.2):
        if not hasattr(self, '_initialized'):
            self._cache = SemanticCache(
                name=name,
                prefix=prefix,
                redis_url=redis_url,
                distance_threshold=distance_threshold
            )
            self.name = name
            self.prefix = prefix
            self.set_time_to_live()
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

    def find_similar(self, question: str, return_fields=None):
        self._reset_timer()
        if return_fields is None:
            return_fields = ["prompt", "response", "metadata"]
        response = self.cache.check(prompt=question, return_fields=return_fields)
        if not response:
            return None
        print(f"length of response is : {len(response)}")
        return response[0]["response"]

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
