import time
import logging
import redis
from redis.exceptions import ConnectionError, AuthenticationError, TimeoutError
from crawler.utils.config import REDIS_HOST, REDIS_PORT, MAX_RETRIES, RETRY_DELAY_SECONDS

# # Thiết lập logging
logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=5):
        """
        Khởi tạo RedisClient với ConnectionPool và retry logic.
        
        Args:
            host (str): Redis host
            port (int): Redis port
            decode_responses (bool): Tự động decode response thành string
            socket_timeout (int): Timeout cho socket operations
        """
        self.pool = None
        self.client = None

        for attempt in range(MAX_RETRIES):
            try:
                # Tạo ConnectionPool
                self.pool = redis.ConnectionPool(
                    host=host,
                    port=port,
                    decode_responses=decode_responses,
                    socket_timeout=socket_timeout,
                    max_connections=50  # Giới hạn số kết nối trong pool
                )
                # Tạo Redis client từ pool
                self.client = redis.Redis(connection_pool=self.pool)
                # Kiểm tra kết nối
                self.client.ping()
                logger.info(f"[REDIS] Connected successfully to {host}:{port}")
                break

            except (ConnectionError, AuthenticationError, TimeoutError) as e:
                logger.warning(
                    f"[REDIS] Attempt {attempt + 1}/{MAX_RETRIES} - Failed to connect to {host}:{port}: {e}. "
                    f"Retrying in {RETRY_DELAY_SECONDS}s..."
                )
                time.sleep(RETRY_DELAY_SECONDS)

            except Exception as e:
                logger.error(f"[REDIS] Unexpected error connecting to {host}:{port}: {e}", exc_info=True)
                time.sleep(RETRY_DELAY_SECONDS)

        if self.client is None:
            logger.error(f"[REDIS] Failed to connect to {host}:{port} after {MAX_RETRIES} attempts")
            raise Exception(f"❌ Failed to connect to Redis at {host}:{port} after multiple attempts")

    def exists(self, key):
        """Kiểm tra key tồn tại trong Redis."""
        try:
            return self.client.exists(key)
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"[REDIS] Error checking key {key}: {e}", exc_info=True)
            raise

    def set(self, key, value, ex=None):
        """Lưu key-value vào Redis với expiration time (nếu có)."""
        try:
            self.client.set(key, value, ex=ex)
            logger.debug(f"[REDIS] Set key {key} with expiration {ex}s")
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"[REDIS] Error setting key {key}: {e}", exc_info=True)
            raise

    def disconnect(self):
        """Ngắt kết nối Redis bằng cách đóng connection pool."""
        if self.pool:
            self.pool.disconnect()
            logger.info("[REDIS] Connection pool disconnected")
            self.pool = None
            self.client = None