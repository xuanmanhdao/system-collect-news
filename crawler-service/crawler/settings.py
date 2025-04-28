# crawler/settings.py

# ⚡ Enable AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.1
AUTOTHROTTLE_MAX_DELAY = 2
AUTOTHROTTLE_TARGET_CONCURRENCY = 20.0
AUTOTHROTTLE_DEBUG = False

# ⚡ Increase concurrency
CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 32

# ⚡ Retry logic
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# ⚡ Disable Telnet console (security)
TELNETCONSOLE_ENABLED = False

# ⚡ Respect Robots.txt? (no, you are internal system)
ROBOTSTXT_OBEY = False

# ⚡ Enable HTTP caching? (optional)
HTTPCACHE_ENABLED = False

# ⚡ Timeout each request
DOWNLOAD_TIMEOUT = 30  # seconds

# ⚡ Default Request Headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

# ⚡ Other optional configs
DOWNLOAD_MAXSIZE = 10 * 1024 * 1024  # 10 MB max page size
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 5

# ⚡ Logging
LOG_LEVEL = 'INFO'
