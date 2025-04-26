import socket
import sys

def check_host(host, port):
    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        return True
    except Exception:
        return False

if not check_host('kafka', 9093):
    print("Kafka not ready")
    sys.exit(1)

if not check_host('redis', 6379):
    print("Redis not ready")
    sys.exit(1)

print("Kafka and Redis are ready!")
sys.exit(0)