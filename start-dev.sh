#!/bin/bash
set -e

echo "👉 Build and start Zookeeper (Dev)..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml build zookeeper
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d zookeeper

echo "⏳ Waiting for Zookeeper to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' zookeeper)" == "healthy" ]; do
  sleep 2
done
echo "✅ Zookeeper is healthy!"

# --------------------------------------------------

echo "👉 Build and start Kafka (Dev)..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml build kafka
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d kafka

echo "⏳ Waiting for Kafka to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' kafka)" == "healthy" ]; do
  sleep 2
done
echo "✅ Kafka is healthy!"

# --------------------------------------------------

echo "👉 Build and start Redis (Dev)..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml build redis
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d redis

echo "⏳ Waiting for Redis to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' redis)" == "healthy" ]; do
  sleep 2
done
echo "✅ Redis is healthy!"

# --------------------------------------------------

echo "👉 Build and start Kafdrop (Dev)..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml build kafdrop
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d kafdrop

# --------------------------------------------------

echo "👉 Build and start Crawler (Dev)..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml build crawler
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d crawler

echo "✅ All containers for Dev environment are built and started!"