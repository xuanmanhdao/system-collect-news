import time
from kafka import KafkaProducer
import redis
from crawler.utils.config import KAFKA_HOST, KAFKA_PORT, REDIS_HOST, REDIS_PORT

def wait_for_kafka(max_retries=10, wait_time=3):
    for attempt in range(1, max_retries + 1):
        try:
            producer = KafkaProducer(bootstrap_servers=[f"{KAFKA_HOST}:{KAFKA_PORT}"])
            producer.close()
            print("✅ Kafka is available!")
            break
        except Exception as e:
            print(f"[KAFKA] Attempt {attempt}/{max_retries} - Kafka not available. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    else:
        raise Exception("❌ Failed to connect to Kafka after multiple attempts.")

def wait_for_redis(max_retries=10, wait_time=3):
    for attempt in range(1, max_retries + 1):
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
            client.ping()
            print("✅ Redis is available!")
            break
        except Exception as e:
            print(f"[REDIS] Attempt {attempt}/{max_retries} - Redis not available. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    else:
        raise Exception("❌ Failed to connect to Redis after multiple attempts.")

def wait_for_services():
    wait_for_kafka()
    wait_for_redis()
