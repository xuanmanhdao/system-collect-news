import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env nếu đang chạy local
dotenv_path = os.path.join(os.path.dirname(__file__), '../../../.env.dev')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("[CONFIG] .env loaded for local debug")

# Lấy biến môi trường
KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = int(os.getenv("KAFKA_PORT", "9092"))

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "10"))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "3"))
