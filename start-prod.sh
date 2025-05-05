#!/bin/bash
set -e

echo "🚀 [START] Building and starting services for PROD..."

# Bước 1: Build tất cả các service
docker-compose -f docker-compose.yml build

# Bước 2: Start tuần tự Zookeeper -> Kafka -> Redis -> Kafdrop -> Elasticsearch -> Kibana -> Spark -> Crawler
services=(zookeeper kafka kafka-init redis kafdrop elasticsearch kibana spark crawler)

for service in "${services[@]}"; do
  echo "👉 Starting $service..."
  docker-compose -f docker-compose.yml up -d $service

  # Nếu có healthcheck thì đợi healthy
  if docker inspect --format='{{.State.Health.Status}}' $service &>/dev/null; then
    echo "⏳ Waiting for $service to be healthy..."
    until [ "$(docker inspect --format='{{.State.Health.Status}}' $service)" == "healthy" ]; do
      sleep 2
    done
    echo "✅ $service is healthy!"
  else
    echo "⚡ $service does not have healthcheck. Continue..."
  fi
done

echo "🎯 [DONE] All PROD services built and started successfully!"