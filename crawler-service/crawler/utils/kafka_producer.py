import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from crawler.utils.config import KAFKA_HOST, KAFKA_PORT

producer = None

for attempt in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=[f"{KAFKA_HOST}:{KAFKA_PORT}"],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("[KAFKA] KafkaProducer connected successfully.")
        break
    except NoBrokersAvailable as e:
        print(f"[KAFKA] Attempt {attempt + 1}/10 - Kafka not available. Retrying in 3s...")
        time.sleep(3)

if producer is None:
    raise Exception("❌ Failed to connect to Kafka after multiple attempts.")

def send_to_kafka(topic, data):
    print(f"[KAFKA] Sent to topic '{topic}': {data['title'][:60]}")
    producer.send(topic, data)