from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType
import logging

# 1. Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SparkNewsProcessor")

# 2. Khởi tạo SparkSession,
# spark.sql.shuffle.partitions giảm số lượng shuffle partition nếu nhỏ, spark.streaming.backpressure.enabled bật cơ chế chống bão
spark = SparkSession.builder \
    .appName("NewsKafkaConsumer") \
    .config("spark.sql.shuffle.partitions", "3") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
logger.info("✅ SparkSession started.")

# 3. Đọc dữ liệu từ Kafka
try:
    df_kafka_raw = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "raw-news") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .option("checkpointLocation", "/tmp/checkpoint-kafka") \
        .load()
    logger.info("✅ Connected to Kafka topic: raw-news")
except Exception as e:
    logger.error(f"❌ Failed to connect to Kafka: {e}", exc_info=True)
    raise

# 4. Định nghĩa schema cho JSON
json_schema = StructType() \
    .add("source", StringType()) \
    .add("url", StringType()) \
    .add("title", StringType()) \
    .add("image", StringType()) \
    .add("body", StringType())

# 5. Parse JSON từ Kafka value
df_parsed = df_kafka_raw.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), json_schema).alias("data")) \
    .select("data.*")

logger.info("✅ Schema parsed from Kafka:")
df_parsed.printSchema()

# 6. Ghi dữ liệu vào Elasticsearch
try:
    query = df_parsed.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("checkpointLocation", "/tmp/checkpoint-es") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "news") \
        .option("es.nodes.wan.only", "false") \
        .option("es.mapping.id", "url") \
        .start()

    logger.info("🚀 Streaming started: Kafka -> Elasticsearch")
    query.awaitTermination()

except Exception as e:
    logger.error(f"❌ Failed to start streaming to Elasticsearch: {e}", exc_info=True)
    raise