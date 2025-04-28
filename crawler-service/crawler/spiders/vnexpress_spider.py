import scrapy
import hashlib
from crawler.utils.redis_client import RedisClient
from crawler.utils.kafka_producer import send_to_kafka
import logging

class VnexpressSpider(scrapy.Spider):
    name = "vnexpress"
    allowed_domains = ["vnexpress.net"]
    start_urls = ["https://vnexpress.net"]
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',  # Bật debug log
        'CONCURRENT_REQUESTS': 16,  # Giới hạn request đồng thời
        'DOWNLOAD_DELAY': 1,  # Delay để tránh tải nặng server
        'RETRY_TIMES': 3,  # Retry request thất bại
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = RedisClient()  # Khởi tạo Redis một lần
        self.logger.debug("[REDIS] Redis client initialized")

    def parse(self, response):
        """Parse trang chủ để lấy liên kết bài viết."""
        article_links = response.xpath('//article//a[@href and contains(@href, ".html")]/@href').getall()
        for link in set(article_links):
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(url=link, callback=self.parse_article)

    def parse_article(self, response):
        try:
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
                self.redis.set(hash_key, "1", ex=60*60*24*30)  # Lưu 30 ngày

                # Chuẩn bị dữ liệu gửi Kafka
                article_data = {
                    "source": "vnexpress",
                    "url": response.url,
                    "title": title,
                    "image": image,
                    "body": body
                }

                # Gửi bất đồng bộ tới Kafka
                self.logger.debug(f"[SPIDER] Sending article to Kafka: {response.url}")
                send_to_kafka(
                    "raw-news",
                    article_data,
                    callback=lambda rm: self.logger.info(
                        f"[KAFKA] Sent to raw-news: topic={rm.topic}, partition={rm.partition}, offset={rm.offset}, url={response.url}"
                    ),
                    error_callback=lambda exc: self.logger.error(
                        f"[KAFKA] Failed to send to raw-news: {exc}, url={response.url}", exc_info=True
                    )
                )
            else:
                self.logger.debug(f"[REDIS] Skipping duplicate article: {response.url}")

        except Exception as e:
            self.logger.error(f"[SPIDER] Failed to process article {response.url}: {e}", exc_info=True)
            raise

    # def closed(self, reason):
    #     """Đóng Redis client khi spider dừng."""
    #     self.redis.close()
    #     self.logger.debug("[REDIS] Redis client closed")