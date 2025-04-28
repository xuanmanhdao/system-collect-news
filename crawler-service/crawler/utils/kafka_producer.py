import json
import time
import logging
from kafka import KafkaProducer, KafkaAdminClient
from kafka.errors import NoBrokersAvailable, KafkaTimeoutError, KafkaError
from crawler.utils.config import KAFKA_HOST, KAFKA_PORT, MAX_RETRIES, RETRY_DELAY_SECONDS

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Tắt log DEBUG của kafka.conn
logging.getLogger('kafka.conn').setLevel(logging.INFO)

def create_producer():
    """Khởi tạo KafkaProducer với retry."""
    for attempt in range(MAX_RETRIES):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[f"{KAFKA_HOST}:{KAFKA_PORT}"],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=10,  # Tăng số lần retry
                request_timeout_ms=60000,  # Tăng timeout lên 60 giây
                acks='all',
                linger_ms=50,  # Giảm linger_ms để gửi nhanh hơn
                batch_size=32768,  # Tăng batch_size
                max_request_size=2097152  # Tăng giới hạn message size lên 2MB
            )
            logger.debug(f"[KAFKA] KafkaProducer connected to {KAFKA_HOST}:{KAFKA_PORT}")

            # Kiểm tra metadata
            admin_client = KafkaAdminClient(
                bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}",
                request_timeout_ms=10000,
            )
            topics = admin_client.list_topics()
            logger.debug(f"[KAFKA] Available topics: {topics}")
            admin_client.close()
            return producer

        except NoBrokersAvailable:
            logger.warning(f"[KAFKA] Attempt {attempt + 1}/{MAX_RETRIES} - No brokers available. Retrying in {RETRY_DELAY_SECONDS}s...")
            time.sleep(RETRY_DELAY_SECONDS)

        except KafkaTimeoutError:
            logger.warning(f"[KAFKA] Attempt {attempt + 1}/{MAX_RETRIES} - Timeout fetching metadata. Retrying in {RETRY_DELAY_SECONDS}s...")
            time.sleep(RETRY_DELAY_SECONDS)

        except KafkaError as e:
            logger.error(f"[KAFKA] Unexpected Kafka error: {e}", exc_info=True)
            time.sleep(RETRY_DELAY_SECONDS)

    raise Exception("❌ Failed to connect to Kafka after multiple attempts.")

def send_to_kafka(topic, data, callback=None, error_callback=None):
    """
    Gửi message tới Kafka topic bất đồng bộ.
    
    Args:
        topic (str): Tên topic
        data (dict): Dữ liệu cần gửi
        callback (callable): Hàm gọi khi gửi thành công
        error_callback (callable): Hàm gọi khi gửi thất bại
    """
    producer = None
    try:
        # Log kích thước message
        message_size = len(json.dumps(data).encode('utf-8'))
        logger.debug(f"[KAFKA] Sending to topic '{topic}', size: {message_size} bytes, title: {data.get('title', '')[:60]}")

        # Khởi tạo producer
        producer = create_producer()

        # Gửi message bất đồng bộ
        future = producer.send(topic, data)
        if callback or error_callback:
            future.add_callback(callback or (lambda rm: logger.debug(f"[KAFKA] Sent to {topic}: {rm}")))
            future.add_errback(error_callback or (lambda exc: logger.error(f"[KAFKA] Error sending to {topic}: {exc}")))
        else:
            # Chờ xác nhận đồng bộ nếu không có callback
            future.get(timeout=60)  # Tăng timeout lên 60 giây
            logger.debug(f"[KAFKA] Successfully sent to {topic}")

        producer.flush()

    except KafkaTimeoutError as e:
        logger.error(f"[KAFKA] Timeout sending to {topic}: {e}", exc_info=True)
        raise

    except KafkaError as e:
        logger.error(f"[KAFKA] Kafka error for {topic}: {e}", exc_info=True)
        raise

    except Exception as e:
        logger.error(f"[KAFKA] General error for {topic}: {e}", exc_info=True)
        raise

    finally:
        if producer:
            producer.close()
            logger.debug("[KAFKA] Producer closed")