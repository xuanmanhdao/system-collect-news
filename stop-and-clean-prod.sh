#!/bin/bash
set -e

echo "🛑 [STOP] Stopping all PROD services..."

# Dừng tất cả service theo đúng thứ tự phụ thuộc
services=(crawler spark kafdrop redis kafka zookeeper elasticsearch kibana)

for service in "${services[@]}"; do
  echo "👉 Stopping $service..."
  docker-compose -f docker-compose.yml stop $service || true
done

# Xóa bỏ các container không cần thiết
echo "🧹 Cleaning dangling containers..."
docker-compose -f docker-compose.yml down -v --remove-orphans

echo "✅ [DONE] All PROD services stopped and cleaned!"