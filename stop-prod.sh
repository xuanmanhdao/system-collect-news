#!/bin/bash
set -e

echo "🛑 [STOP] Stopping all PROD services..."

# Dừng tất cả service theo đúng thứ tự phụ thuộc
services=(crawler spark kafdrop redis kafka zookeeper elasticsearch kibana)

for service in "${services[@]}"; do
  echo "👉 Stopping $service..."
  docker-compose -f docker-compose.yml stop $service || true
done

echo "✅ [DONE] All PROD services stopped!"