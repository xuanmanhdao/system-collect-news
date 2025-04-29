#!/bin/bash
set -e

echo "🛑 Stopping and removing all containers..."
docker-compose down -v --remove-orphans
echo "✅ All containers stopped and removed!"