#!/bin/bash
set -e

echo "🔄 [RESTART] Restarting all PROD services..."

# Bước 1: Dừng tất cả container PROD đang chạy
echo "🛑 Stopping services..."
docker-compose -f docker-compose.yml down -v --remove-orphans

# Bước 2: Build lại images (nếu có thay đổi)
echo "🛠️ Building services..."
docker-compose -f docker-compose.yml build

# Bước 3: Start lại toàn bộ theo đúng flow
echo "🚀 Starting services..."
bash ./start-prod.sh

echo "✅ [DONE] Restarted all PROD services successfully!"