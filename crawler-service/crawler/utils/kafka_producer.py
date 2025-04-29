import json
import time
import logging
from kafka import KafkaProducer, KafkaAdminClient
from kafka.errors import NoBrokersAvailable, KafkaTimeoutError, KafkaError, TopicAlreadyExistsError
from kafka.admin import NewTopic
from crawler.utils.config import KAFKA_HOST, KAFKA_PORT, MAX_RETRIES, RETRY_DELAY_SECONDS

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tắt log DEBUG của kafka.conn
logging.getLogger('kafka.conn').setLevel(logging.INFO)
logging.getLogger('kafka.protocol.parser').setLevel(logging.INFO)

class KafkaProducerSingleton:
    _producer = None
    _checked_topics = set()

    @classmethod
    def get_producer(cls, topic=None, num_partitions=1, replication_factor=1):
        """Khởi tạo hoặc trả về KafkaProducer singleton, kiểm tra/tạo topic nếu cần."""
        if cls._producer is None:
            for attempt in range(MAX_RETRIES):
                try:
                    cls._producer = KafkaProducer(
                        bootstrap_servers=[f"{KAFKA_HOST}:{KAFKA_PORT}"],
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                        retries=5,
                        request_timeout_ms=10000,
                        acks='all',
                        linger_ms=50,
                        batch_size=131072,
                        max_request_size=2097152
                    )
                    logger.info(f"[KAFKA] KafkaProducer connected to {KAFKA_HOST}:{KAFKA_PORT}")

                    # Kiểm tra/tạo topic nếu được chỉ định
                    if topic and topic not in cls._checked_topics:
                        admin_client = None
                        try:
                            admin_client = KafkaAdminClient(
                                bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}",
                                request_timeout_ms=3000,  # Giảm timeout
                            )
                            # Retry list_topics để đảm bảo metadata đồng bộ
                            for retry in range(2):
                                topics = admin_client.list_topics()
                                if topic in topics:
                                    logger.info(f"[KAFKA] Topic '{topic}' already exists")
                                    break
                                time.sleep(0.5)  # Chờ metadata đồng bộ
                            else:
                                cluster_metadata = admin_client.describe_cluster()
                                num_brokers = len(cluster_metadata.get('brokers', []))
                                if num_brokers == 0:
                                    logger.warning("[KAFKA] No brokers found in cluster metadata. Using replication_factor=1.")
                                    num_brokers = 1

                                logger.info(f"[KAFKA] Number of brokers: {num_brokers}")

                                if num_partitions == 1:
                                    logger.warning(f"[KAFKA] Creating topic '{topic}' with num_partitions=1. Consider increasing for scalability.")
                                if replication_factor == 1 and num_brokers > 1:
                                    logger.warning(f"[KAFKA] Creating topic '{topic}' with replication_factor=1. Consider increasing for fault tolerance.")

                                if replication_factor > num_brokers:
                                    logger.warning(f"[KAFKA] replication_factor={replication_factor} exceeds number of brokers ({num_brokers}). Setting to {num_brokers}.")
                                    replication_factor = num_brokers

                                logger.info(f"[KAFKA] Creating topic '{topic}' with num_partitions={num_partitions}, replication_factor={replication_factor}")
                                new_topic = NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)
                                try:
                                    admin_client.create_topics([new_topic])
                                    logger.info(f"[KAFKA] Topic '{topic}' created")
                                except TopicAlreadyExistsError:
                                    logger.info(f"[KAFKA] Topic '{topic}' already exists (race condition)")
                                    pass

                            cls._checked_topics.add(topic)

                        except KafkaError as e:
                            logger.error(f"[KAFKA] Failed to check or create topic '{topic}': {e}", exc_info=True)
                            raise
                        finally:
                            if admin_client:
                                admin_client.close()
                                logger.debug("[KAFKA] KafkaAdminClient closed")

                    return cls._producer

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
        return cls._producer

    @classmethod
    def close_producer(cls):
        """Đóng KafkaProducer."""
        if cls._producer is not None:
            cls._producer.flush()
            cls._producer.close()
            logger.info("[KAFKA] KafkaProducer closed")
            cls._producer = None
            cls._checked_topics.clear()

def send_to_kafka(topic, data, key=None, callback=None, error_callback=None, num_partitions=1, replication_factor=1):
    """Gửi message tới Kafka topic bất đồng bộ."""
    try:
        message_size = len(json.dumps(data).encode('utf-8'))
        logger.debug(f"[KAFKA] Sending to topic '{topic}', size: {message_size} bytes")

        # Lấy producer và kiểm tra topic nếu cần
        producer = KafkaProducerSingleton.get_producer(topic=topic, num_partitions=num_partitions, replication_factor=replication_factor)
        start_time = time.time()
        future = producer.send(topic, key=key, value=data)
        if callback or error_callback:
            future.add_callback(callback or (lambda rm: logger.debug(f"[KAFKA] Sent to {topic}: {rm}")))
            future.add_errback(error_callback or (lambda exc: logger.error(f"[KAFKA] Error sending to {topic}: {exc}", exc_info=True)))
        else:
            # future.get(timeout=30)
            logger.info(f"[KAFKA] Sent to not callback {topic} in {time.time() - start_time:.3f}s")

    except KafkaTimeoutError as e:
        logger.error(f"[KAFKA] Timeout sending to {topic}: {e}", exc_info=True)
        raise

    except KafkaError as e:
        logger.error(f"[KAFKA] Kafka error for {topic}: {e}", exc_info=True)
        raise

    except Exception as e:
        logger.error(f"[KAFKA] General error for {topic}: {e}", exc_info=True)
        raise