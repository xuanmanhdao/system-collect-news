import redis
from crawler.utils.config import REDIS_HOST, REDIS_PORT

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)

    def exists(self, key):
        return self.client.exists(key)
