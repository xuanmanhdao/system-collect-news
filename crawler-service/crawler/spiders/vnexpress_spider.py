import scrapy
import hashlib
from crawler.utils.redis_client import RedisClient
from crawler.utils.kafka_producer import send_to_kafka, KafkaProducerSingleton
import time
import json

class VnexpressSpider(scrapy.Spider):
    name = "vnexpress"
    allowed_domains = ["vnexpress.net"]
    start_urls = ["https://vnexpress.net"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = RedisClient()
        self.logger.debug("[REDIS] Redis client initialized")
        # Khởi tạo KafkaProducer sớm để kiểm tra kết nối và tạo topic raw-news
        # Có thể bỏ nếu topic đã tồn tại và Kafka luôn khả dụng
        KafkaProducerSingleton.get_producer(topic="raw-news", num_partitions=3, replication_factor=1)
        self.logger.debug("[KAFKA] KafkaProducer initialized")

    def parse(self, response):
        """Parse trang chủ để lấy liên kết bài viết."""
        article_links = response.xpath('//article//a[@href and contains(@href, ".html")]/@href').getall()
        for link in set(article_links):
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(url=link, callback=self.parse_article)

    def parse_article(self, response):
        try:
            start_time = time.time()
            # Trích xuất dữ liệu
            title = response.xpath('//h1/text()').get(default='').strip()
            paragraphs = response.xpath('//article//p//text()').getall()
            body = " ".join(p.strip() for p in paragraphs if p.strip())
            image = response.xpath('//article//img/@data-src | //article//img/@src').get(default='')

            if not title or not body:
                self.logger.warning(f"[SPIDER] Skipping article without title or body: {response.url}")
                return

            # Tạo hash để kiểm tra trùng lặp
            content = title + body
            hash_key = hashlib.sha256(content.encode('utf-8')).hexdigest()

            # Kiểm tra Redis
            self.logger.debug(f"[REDIS] Checking hash {hash_key} for {response.url}")
            if not self.redis.exists(hash_key):
                self.logger.debug(f"[REDIS] Article not in Redis, adding {hash_key}")
                self.redis.set(hash_key, "1", ex=60*60*24*30) # Lưu 30 ngày

                # Chuẩn bị dữ liệu gửi Kafka
                article_data = {
                    "source": "vnexpress",
                    "url": response.url,
                    "title": title,
                    "image": image,
                    "body": body
                }

                message_size = len(json.dumps(article_data).encode('utf-8'))
                self.logger.info(f"[SPIDER] Message size: {message_size} bytes for {response.url}")

                # Gửi bất đồng bộ tới Kafka
                self.logger.debug(f"[SPIDER] Sending article to Kafka: {response.url}")
                # Dùng URL + timestamp làm key để phân phối
                message_key = (response.url + str(time.time())).encode('utf-8')
                send_to_kafka(
                    "raw-news",
                    article_data,
                    key=message_key,
                    num_partitions=3,  # Tăng partition
                    replication_factor=1,
                    callback=lambda rm: self.logger.info(
                        f"[KAFKA] Sent to raw-news: topic={rm.topic}, partition={rm.partition}, offset={rm.offset}, url={response.url}"
                    ),
                    error_callback=lambda exc: self.logger.error(
                        f"[KAFKA] Failed to send to raw-news: {exc}, url={response.url}", exc_info=True
                    )
                )
            else:
                self.logger.debug(f"[REDIS] Skipping duplicate article: {response.url}")
            self.logger.info(f"[SPIDER] Processed article {response.url} in {time.time() - start_time:.3f}s")
        except Exception as e:
            self.logger.error(f"[SPIDER] Failed to process article {response.url}: {e}", exc_info=True)
            raise

    def closed(self, reason):
        try:
            self.redis.disconnect()
            self.logger.debug("[REDIS] Redis connection closed")
            KafkaProducerSingleton.close_producer()
            self.logger.debug("[KAFKA] KafkaProducer closed")
        except Exception as e:
            self.logger.error(f"[SPIDER] Error during close: {e}", exc_info=True)