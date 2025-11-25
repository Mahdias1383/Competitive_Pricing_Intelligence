from typing import List, Dict, Any

"""
Shared Memory Storage.
This module acts as a temporary in-memory database to store scraped data
from concurrent threads.

Warning:
    Since these lists are accessed by multiple threads, Python's Global Interpreter Lock (GIL)
    and the atomic nature of `append` usually make this safe for simple operations.
    For more complex operations, consider using `queue.Queue` or `threading.Lock`.
"""

# Lists to store dictionaries of scraped products: [{'name_product': '...', 'price_product': 100}]
scraped_data_digikala: List[Dict[str, Any]] = []
scraped_data_olfa: List[Dict[str, Any]] = []
scraped_data_amazon: List[Dict[str, Any]] = []