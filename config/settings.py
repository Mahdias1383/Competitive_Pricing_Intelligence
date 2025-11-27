"""
Project-wide configuration settings.
"""

# --- Network Settings ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9080
BUFFER_SIZE = 8192
ENCODING = 'utf-8'

# --- Crawler Settings ---
CRAWLER_THREAD_COUNT = 2
PAGE_LOAD_TIMEOUT = 10
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
MAX_SEARCH_RESULTS = 20

# --- Search Patterns ---
SEARCH_PATTERNS = {
    "digikala": "https://www.digikala.com/search/?q={}",
    "amazon": "https://www.amazon.com/s?k={}"
}

# --- File Paths ---
OUTPUT_IMAGE_NAME = "comparison_analysis.png"
FINAL_CSV_NAME = "comparison_report.csv"