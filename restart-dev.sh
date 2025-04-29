#!/bin/bash
set -e

echo "🔄 [RESTART] Restarting all DEV services..."

# Bước 1: Dừng tất cả container PROD đang chạy
echo "🛑 Stopping services..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml down -v --remove-orphans

# Bước 2: Build lại images (nếu có thay đổi)
echo "🛠️ Building services..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml build

# Bước 3: Start lại toàn bộ theo đúng flow
echo "🚀 Starting services..."
bash ./start-dev.sh

echo "✅ [DONE] Restarted all DEV services successfully!"
