import sys
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.vnexpress_spider import VnexpressSpider
from crawler.spiders.tuoitre_spider import TuoitreSpider
from crawler.utils.healthcheck import wait_for_services
from crawler import settings
import time

SPIDER_MAPPING = {
    "vnexpress": VnexpressSpider,
    "tuoitre": TuoitreSpider,
}

def run_spider(spider_cls):
    start_time = time.time()
    process = CrawlerProcess(settings.__dict__)
    spider_name = spider_cls.name
    process.crawl(spider_cls)
    print(f"🚀 Starting spider: {spider_name}")
    process.start()
    print(f"✅ Finished spider: {spider_name} in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    wait_for_services()

    if len(sys.argv) > 1:
        # Nếu chỉ định spider
        spider_name = sys.argv[1]
        spider_cls = SPIDER_MAPPING.get(spider_name)
        if spider_cls:
            run_spider(spider_cls)
        else:
            print(f"❌ Unknown spider '{spider_name}'. Available: {list(SPIDER_MAPPING.keys())}")
            sys.exit(1)
    else:
        # Không chỉ định spider: chạy hết
        jobs = [Process(target=run_spider, args=(sp,)) for sp in SPIDER_MAPPING.values()]
        for job in jobs:
            job.start()
        for job in jobs:
            job.join()
