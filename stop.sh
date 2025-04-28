#!/bin/bash
set -e

echo "🛑 Stopping all services in correct order..."

# 1. Dừng crawler trước
echo "Stopping Crawler..."
docker-compose stop crawler || true

# 2. Dừng spark nếu có
echo "Stopping Spark (if exists)..."
docker-compose stop spark || true

# 3. Dừng Kafdrop
echo "Stopping Kafdrop..."
docker-compose stop kafdrop || true

# 4. Dừng Redis
echo "Stopping Redis..."
docker-compose stop redis || true

# 5. Dừng Kafka
echo "Stopping Kafka..."
docker-compose stop kafka || true

# 6. Dừng Zookeeper
echo "Stopping Zookeeper..."
docker-compose stop zookeeper || true

# 7. Clean container kafka-init (vì nó chạy 1 lần)
echo "Removing kafka-init container if exists..."
docker rm -f kafka-init || true

echo "✅ All services stopped cleanly!"
