import time
import redis
from crawler.utils.config import REDIS_HOST, REDIS_PORT, MAX_RETRIES, RETRY_DELAY_SECONDS

class RedisClient:
    def __init__(self):
        self.client = None
        for attempt in range(MAX_RETRIES):
            try:
                self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
                self.client.ping()
                print("[REDIS] Connected successfully.")
                break
            except redis.ConnectionError:
                print(f"[REDIS] Attempt {attempt + 1}/{MAX_RETRIES} - Redis not available. Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
        if self.client is None:
            raise Exception("❌ Failed to connect to Redis after multiple attempts.")

    def exists(self, key):
        return self.client.exists(key)

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)