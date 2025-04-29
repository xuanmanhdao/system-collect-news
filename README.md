# 📚 System Collect News - README
## 🧩 Tổng Quan
Dự án System Collect News là một hệ thống crawler tự động đa nguồn (VnExpress, Tuổi Trẻ, ...), thu thập tin tức về Kafka, xử lý dữ liệu với Spark và lưu trữ vào Elasticsearch.
Hệ thống thiết kế microservices chạy bằng Docker để đảm bảo khả năng scale, tối ưu và dễ dàng maintain.

## 🛠 Thành phần chính

| Service             | Mô tả                                               |
|---------------------|-----------------------------------------------------|
| **Zookeeper**       | Quản lý cluster Kafka                               |
| **Kafka**           | Message broker trung tâm                            |
| **Kafdrop**         | UI web quản lý Kafka                                |
| **Redis**           | Cache chống duplicate bài viết                      |
| **Elasticsearch**   | Lưu trữ dữ liệu tin tức dạng document               |
| **Kibana**          | Giao diện search/visualize dữ liệu từ Elasticsearch |
| **Spark**           | Xử lý dữ liệu Kafka trước khi đưa vào Elasticsearch |
| **Crawler Service** | Thu thập dữ liệu từ các báo điện tử                 |

## 🚀 Cách chạy hệ thống
### 1. Clone project
```
git clone https://github.com/yourname/system-collect-news.git
cd system-collect-news/source-code
```
### 2. Chạy môi trường DEV
```
# Bắt đầu services môi trường dev
./start-dev.sh
```
Crawler service sẽ chạy và push tin tức vào Kafka.

Kafdrop mở tại: http://localhost:9000

Elasticsearch tại: http://localhost:9200

Kibana tại: http://localhost:5601

Ghi chú: Dev mặc định chạy cron mỗi 1 phút, dễ test.

### 3. Chạy môi trường PROD
```
# Bắt đầu services môi trường prod
./start-prod.sh
```
Prod cấu hình tối ưu hơn (log chuẩn hóa, crontab phân chia rõ).

### 4. Các lệnh quản lý khác
```
# Stop tất cả containers
./stop-all.sh

# Restart nhanh môi trường dev
./restart-dev.sh

# Restart nhanh môi trường prod
./restart-prod.sh
```
## 🧩 Cấu trúc thư mục
```
source-code/
│
├── crawler-service/
│   ├── crontab.template.txt
│   ├── Dockerfile
│   ├── main.py
│   ├── crawler/
│       ├── spiders/
│           ├── vnexpress_spider.py
│           ├── tuoitre_spider.py
│       ├── utils/
│           ├── kafka_producer.py
│           ├── redis_client.py
│           ├── config.py
│           ├── healthcheck.py
│   └── requirements.txt
│
├── processor-service/    # (Xử lý Spark, nếu cần)
│   ├── spark_news_processor.py
│
├── news-service/    # (Expose Restful API)
│
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.dev
├── .env.prod
├── start-dev.sh
├── start-prod.sh
├── stop-and-clean-dev.sh
├── stop-and-clean-prod.sh
├── restart-dev.sh
├── restart-prod.sh
└── README.md  # (file này)
```
### ⚙️ Tùy chỉnh cấu hình
Bạn có thể thay đổi file:
.env.dev
.env.prod
để config:

| Key                      | Ý nghĩa                               |
|--------------------------|---------------------------------------|
| **KAFKA_HOST**           | Địa chỉ kafka broker                  |
| **KAFKA_PORT**           | Port kafka                            |
| **REDIS_HOST**           | Địa chỉ redis                         |
| **REDIS_PORT**           | Port redis                            |
| **Elasticsearch**        | Lưu trữ dữ liệu tin tức dạng document |
| **MAX_RETRIES**          | Số lần retry connect Kafka/Redis      |
| **RETRY_DELAY_SECONDS**  | Khoảng delay giữa các lần retry       |

## ⏳ Hệ thống chạy như thế nào?
crawler-service dùng cron để chạy định kỳ mỗi phút và bắn dữ liệu lên Kafka topic raw-news.

spark đọc dữ liệu Kafka, làm sạch, enrich và ghi xuống Elasticsearch.

kafdrop hỗ trợ xem topic Kafka realtime.

## 📅 Cấu hình lịch crawl (crawler-service/crontab.txt)
```
* * * * * cd /app && python main.py vnexpress 2>&1 | tee -a /var/log/vnexpress_$(date +\%Y\%m\%d\%H\%M\%S).log
* * * * * cd /app && python main.py tuoitre 2>&1 | tee -a /var/log/tuoitre_$(date +\%Y\%m\%d\%H\%M\%S).log
```

Cứ mỗi phút, crawler tự động lấy bài mới và lưu log theo timestamp mới để dễ quản lý.

## 🔥 Một số ghi chú quan trọng
Topic Kafka được tự động tạo nếu chưa tồn tại (3 partition, replication 1).

Redis dùng kiểm tra duplicate bài viết theo hash SHA256.

Elasticsearch lưu tin tức theo chuẩn schema có source, title, body, image, url.

Spark hỗ trợ mở rộng batch hoặc micro-batch để tối ưu tốc độ xử lý lớn hơn.

Nếu cần thêm website crawler → chỉ cần thêm Spider mới ở crawler/spiders/ và khai báo main.py.

## 🛠️ TODO trong tương lai
 Thêm hệ thống Prometheus + Grafana để giám sát.

 Mở rộng sang crawl thêm các báo khác (Vietnamnet, Zingnews...).

 Thêm chức năng gửi alert khi gặp lỗi lớn (Kafka consumer lag, Spark job failed).

 Build UI phân tích dữ liệu đã crawl (Top trending, category classification).
 
 Tích hợp thêm lưu backup dữ liệu tin tức ra file JSON hoặc Database.
 
 Cân nhắc scale multiple crawler container.



