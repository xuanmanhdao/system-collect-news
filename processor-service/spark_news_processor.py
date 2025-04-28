from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType

# 1. Tạo SparkSession
spark = SparkSession.builder \
    .appName("NewsKafkaConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Đọc dữ liệu từ Kafka
df_kafka_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "raw-news") \
    .option("startingOffsets", "earliest") \
    .option("checkpointLocation", "/tmp/checkpoint-news") \
    .load()

# 3. Định nghĩa schema cho JSON
json_schema = StructType() \
    .add("source", StringType()) \
    .add("url", StringType()) \
    .add("title", StringType()) \
    .add("image", StringType()) \
    .add("body", StringType())

#     # show json
# print("Print df_kafka_raw o day")
# df_kafka_raw.selectExpr("CAST(value AS STRING)").writeStream \
#     .format("console") \
#     .start() \
#     .awaitTermination()
    
# 4. Parse JSON từ cột `value`
df_parsed = df_kafka_raw.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), json_schema).alias("data")) \
    .select("data.*")

# In schema ra terminal
df_parsed.printSchema()

# 5. Ghi vào Elasticsearch
df_parsed.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("checkpointLocation", "/tmp/checkpoint-es") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.resource", "news") \
    .option("es.nodes.wan.only", "false") \
    .option("es.mapping.id", "url") \
    .start() \
    .awaitTermination()
