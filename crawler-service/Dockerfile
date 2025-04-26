FROM python:3.10-slim
WORKDIR /app
# Copy toàn bộ source code vào trong container
COPY . .
# Cài đặt các thư viện cần thiết
# Add dòng này để có lệnh ping
RUN apt-get update && apt-get install -y iputils-ping
RUN pip install -r requirements.txt
# Lệnh để chạy file main.py khi container start
CMD ["python", "main.py"]