FROM python:3.10-slim

# Làm việc tại /app
WORKDIR /app

# Copy toàn bộ source code
COPY . .

# Cài Python package
RUN pip install --no-cache-dir -r requirements.txt

# Cài cron và công cụ cần thiết
RUN apt-get update && apt-get install -y iputils-ping cron coreutils gettext-base procps

# Copy crontab template
COPY crontab.template.txt /app/crontab.template.txt

# ENTRYPOINT: khi container khởi động sẽ generate file crontab theo timestamp
ENTRYPOINT ["/bin/bash", "-c", "\
  export LOG_TIMESTAMP=$(date +%Y%m%d_%H%M%S) && \
  envsubst < /app/crontab.template.txt > /etc/cron.d/crawler-cron && \
  chmod 0644 /etc/cron.d/crawler-cron && \
  crontab /etc/cron.d/crawler-cron && \
  mkdir -p /var/log/crawler && \
  cron -f \
"]
