from typing import Dict
from config.urls import PRODUCT_URLS

"""
This module provides a simplified accessor for product URLs.
It maps the crawler names to their respective URL dictionaries.
"""

# Mapping crawler names to their URL list for easier access in loops.
CRAWLER_TARGETS: Dict[str, Dict[str, str]] = {
    "digikala": PRODUCT_URLS["digikala"],
    "olfa": PRODUCT_URLS["olfa"],
    "amazon": PRODUCT_URLS["amazon"]
}