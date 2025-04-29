#!/bin/bash
set -e

echo "🛑 Stopping all services in correct order..."

# 1. Dừng crawler
echo "Stopping Crawler..."
docker-compose stop crawler || true

# 2. Dừng spark
echo "Stopping Spark (if exists)..."
docker-compose stop spark || true

# 3. Dừng kafdrop
echo "Stopping Kafdrop..."
docker-compose stop kafdrop || true

# 4. Dừng redis
echo "Stopping Redis..."
docker-compose stop redis || true

# 5. Dừng kafka
echo "Stopping Kafka..."
docker-compose stop kafka || true

# 6. Dừng zookeeper
echo "Stopping Zookeeper..."
docker-compose stop zookeeper || true

# 7. Xóa kafka-init container (vì nó chạy 1 lần)
echo "Removing kafka-init container if exists..."
docker rm -f kafka-init || true

echo "✅ All services stopped cleanly!"
