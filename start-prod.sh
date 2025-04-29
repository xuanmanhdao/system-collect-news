#!/bin/bash
set -e

echo "👉 Build and start Zookeeper (Prod)..."
docker-compose -f docker-compose.yml build zookeeper
docker-compose -f docker-compose.yml up -d zookeeper

echo "⏳ Waiting for Zookeeper to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' zookeeper)" == "healthy" ]; do
  sleep 2
done
echo "✅ Zookeeper is healthy!"

# --------------------------------------------------

echo "👉 Build and start Kafka (Prod)..."
docker-compose -f docker-compose.yml build kafka
docker-compose -f docker-compose.yml up -d kafka

echo "⏳ Waiting for Kafka to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' kafka)" == "healthy" ]; do
  sleep 2
done
echo "✅ Kafka is healthy!"

# --------------------------------------------------

echo "👉 Build and start Redis (Prod)..."
docker-compose -f docker-compose.yml build redis
docker-compose -f docker-compose.yml up -d redis

echo "⏳ Waiting for Redis to be healthy..."
until [ "$(docker inspect --format='{{.State.Health.Status}}' redis)" == "healthy" ]; do
  sleep 2
done
echo "✅ Redis is healthy!"

# --------------------------------------------------

echo "👉 Build and start Kafdrop (Prod)..."
docker-compose -f docker-compose.yml build kafdrop
docker-compose -f docker-compose.yml up -d kafdrop

# --------------------------------------------------

echo "👉 Build and start Crawler (Prod)..."
docker-compose -f docker-compose.yml build crawler
docker-compose -f docker-compose.yml up -d crawler

echo "✅ All containers for Production environment are built and started!"