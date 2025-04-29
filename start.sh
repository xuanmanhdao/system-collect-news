#!/bin/bash
set -e

echo "👉 Build and start Zookeeper..."
docker-compose build zookeeper
docker-compose up -d zookeeper

echo "⏳ Waiting for Zookeeper to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' zookeeper)" == "healthy" ]; do
  sleep 2
done

echo "✅ Zookeeper is healthy!"

# --------------------------------------------------

echo "👉 Build and start Kafka..."
docker-compose build kafka
docker-compose up -d kafka

echo "⏳ Waiting for Kafka to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' kafka)" == "healthy" ]; do
  sleep 2
done

echo "✅ Kafka is healthy!"

# --------------------------------------------------

# echo "👉 Initialize Kafka topics (running kafka-init)..."
# docker-compose build kafka-init
# docker-compose up kafka-init

# # Optional: remove kafka-init container after done
# docker rm -f kafka-init || true

# echo "✅ Kafka topics created!"

# --------------------------------------------------

echo "👉 Build and start Redis..."
docker-compose build redis
docker-compose up -d redis

echo "⏳ Waiting for Redis to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' redis)" == "healthy" ]; do
  sleep 2
done

echo "✅ Redis is healthy!"

# --------------------------------------------------

echo "👉 Build and start Kafdrop UI..."
docker-compose build kafdrop
docker-compose up -d kafdrop

# --------------------------------------------------

echo "👉 Build and start Crawler service..."
docker-compose build crawler
docker-compose up -d crawler

echo "✅ All containers built and started in correct order!"
