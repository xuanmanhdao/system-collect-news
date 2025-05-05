#!/bin/bash

# --- Cấu hình các tham số ---
KAFKA_BROKER=${KAFKA_BROKER:-kafka:9092}   # Broker nội bộ docker
TOPIC_NAME=${TOPIC_NAME:-raw-news}         # Tên topic cần tạo
PARTITIONS=${PARTITIONS:-3}                # Số partition
REPLICATION_FACTOR=${REPLICATION_FACTOR:-1} # Số replication factor

# --- Hàm tạo topic ---
create_topic() {
  echo "⚡ Checking if topic '$TOPIC_NAME' exists..."

  EXIST=$(kafka-topics.sh --bootstrap-server "$KAFKA_BROKER" --list | grep "^${TOPIC_NAME}$")

  if [ "$EXIST" != "" ]; then
    echo "✅ Topic '$TOPIC_NAME' already exists."
  else
    echo "🚀 Creating topic '$TOPIC_NAME'..."
    kafka-topics.sh --bootstrap-server "$KAFKA_BROKER" \
      --create \
      --topic "$TOPIC_NAME" \
      --partitions "$PARTITIONS" \
      --replication-factor "$REPLICATION_FACTOR"

    echo "✅ Topic '$TOPIC_NAME' created successfully."
  fi
}

# --- Chờ Kafka Broker sẵn sàng ---
wait_for_kafka() {
  echo "⏳ Waiting for Kafka to be ready at $KAFKA_BROKER..."
  RETRIES=0
  until kafka-topics.sh --bootstrap-server "$KAFKA_BROKER" --list >/dev/null 2>&1; do
    sleep 2
    RETRIES=$((RETRIES+1))
    if [ "$RETRIES" -ge 30 ]; then
      echo "❌ Timeout waiting for Kafka broker."
      exit 1
    fi
  done
  echo "✅ Kafka broker is ready!"
}

# --- Main ---
wait_for_kafka
create_topic

echo "🏁 Kafka initialization completed."
