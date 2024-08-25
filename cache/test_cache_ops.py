import unittest
from unittest.mock import patch

from cache.cache_ops import RedisCache


class TestRedisCache(unittest.TestCase):

    def setUp(self):
        self.redis_cache = RedisCache()

    @patch('cache.cache_ops.RedisCache')
    def test_store(self, mock_semantic_cache):
        question = "Test question"
        response = "Test response"
        metadata = {"key": "value"}

        self.redis_cache.store(question, response, metadata)

        mock_semantic_cache.return_value.store.assert_called_once_with(
            prompt=question, response=response, metadata=metadata
        )

    @patch('cache.cache_ops.RedisCache')
    def test_find_similar(self, mock_semantic_cache):
        question = "Test question"
        expected_response = "Test response"
        mock_semantic_cache.return_value.check.return_value = [{"response": expected_response}]

        result = self.redis_cache.find_similar(question)

        self.assertEqual(result, expected_response)
        mock_semantic_cache.return_value.check.assert_called_once_with(
            prompt=question, return_fields=["prompt", "response", "metadata"]
        )

    @patch('cache.cache_ops.RedisCache')
    def test_clear_cache(self, mock_semantic_cache):
        self.redis_cache.clear_cache()
        mock_semantic_cache.return_value.clear.assert_called_once()

    @patch('cache.cache_ops.RedisCache')
    def test_set_time_to_live(self, mock_semantic_cache):
        ttl = 7200
        self.redis_cache.set_time_to_live(ttl)
        mock_semantic_cache.return_value.set_ttl.assert_called_once_with(ttl)

    @patch('cache.cache_ops.RedisCache')
    def test_del_cache_index(self, mock_semantic_cache):
        self.redis_cache.del_cache_index()
        mock_semantic_cache.return_value.delete.assert_called_once()


if __name__ == '__main__':
    unittest.main()
