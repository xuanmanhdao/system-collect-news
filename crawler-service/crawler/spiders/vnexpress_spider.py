import scrapy
import hashlib
from crawler.utils.redis_client import RedisClient
from crawler.utils.kafka_producer import send_to_kafka

class VnexpressSpider(scrapy.Spider):
    name = "vnexpress"

    def start_requests(self):
        yield scrapy.Request(url="https://vnexpress.net", callback=self.parse_homepage)

    def parse_homepage(self, response):
        # Lấy các link bài viết nổi bật
        article_links = response.xpath('//article//a[@href and contains(@href, ".html")]/@href').getall()
        # Loại trùng, chuẩn hóa
        for link in set(article_links):
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(url=link, callback=self.parse_article)

    def parse_article(self, response):
        title = response.xpath('//h1/text()').get()
        paragraphs = response.xpath('//article//p//text()').getall()
        body = " ".join(paragraphs)
        image = response.xpath('//article//img/@data-src | //article//img/@src').get()

        if not title or not body:
            self.logger.warning(f"Bỏ qua bài viết không có title/body: {response.url}")
            return  # Không xử lý bài viết thiếu dữ liệu

        content = title + body
        hash_key = hashlib.sha256(content.encode()).hexdigest()

        redis = RedisClient()
        print("Check ton tai bai viet trong redis")
        if not redis.exists(hash_key):
            print("Khong co trong redis")
            redis.set(hash_key, "1", ex=60*60*24*30)
            print("Call send_to_kafka")
            send_to_kafka("raw-news", {
                "source": "vnexpress",
                "url": response.url,
                "title": title,
                "image": image,
                "body": body
            })
