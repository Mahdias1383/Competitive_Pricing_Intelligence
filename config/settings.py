"""
Project-wide configuration settings.
All constants related to network, paths, and business logic should be defined here.
"""

from typing import List

# --- Network Settings ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9080
BUFFER_SIZE = 1024
ENCODING = 'utf-8'

# --- Crawler Settings ---
CRAWLER_THREAD_COUNT = 2
PAGE_LOAD_TIMEOUT = 5
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

# --- Business Logic (Pricing) ---
TRANSPORT_COST = 40_000
MARKETING_COST = 3_000_000
PROFIT_MARGIN_PERCENT = 0.30  # 30%
BASE_PRICE_MULTIPLIER = 0.95  # 95% of our calculated price
CURRENCY_EXCHANGE_RATE = 60_000 

# Cost prices (The price we buy the product for).
# In a real scenario, this might come from a DB or an external CSV API.
SHOPPING_PRICES: List[int] = [
    44860600, 14054400, 44860600, 2151400, 44860600,
    9576960, 59000000, 5783840, 11980000, 8217190,
    2950000, 5295000, 4795000, 320000000, 7620460,
    43700000, 10300000, 25100000, 6240000, 7750000,
    3160000, 5780000, 34500000, 4950000, 7750000,
]

# --- File Paths ---
OUTPUT_IMAGE_NAME = "price_analysis_plot.png"
FINAL_CSV_NAME = "final_data.csv"