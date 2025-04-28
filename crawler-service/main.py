from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.vnexpress_spider import VnexpressSpider
from crawler.spiders.tuoitre_spider import TuoitreSpider
from crawler.utils.healthcheck import wait_for_services  # <-- Import thêm
from crawler import settings 

def run_spider(spider_cls):
    process = CrawlerProcess(settings.__dict__)
    spider_name = spider_cls.name
    process.crawl(spider_cls)
    print(f"🚀 Starting spider: {spider_name}")
    process.start()

if __name__ == "__main__":
    # 1. Gọi healthcheck trước
    wait_for_services()

    # 2. Sau khi OK thì mới chạy crawler
    spiders = [VnexpressSpider, TuoitreSpider]
    jobs = [Process(target=run_spider, args=(sp,)) for sp in spiders]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
