from kafka import KafkaConsumer
import json

def consume():
    consumer = KafkaConsumer(
        'raw-news',
        bootstrap_servers=['localhos:9093'],
        auto_offset_reset='earliest',  # đọc từ đầu topic
        enable_auto_commit=True,
        group_id='crawler-monitor-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("🎯 Listening to Kafka topic: raw-news ...\n")

    for message in consumer:
        data = message.value
        print("📰 Bài viết:")
        print(f"→ Tiêu đề: {data.get('title')}")
        print(f"→ URL: {data.get('url')}")
        print(f"→ Nội dung: {data.get('body')[:200]}...\n")
        print("-" * 60)

if __name__ == '__main__':
    consume()
