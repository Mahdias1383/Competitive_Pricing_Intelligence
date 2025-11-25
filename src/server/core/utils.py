from queue import Queue
from typing import Optional
from config.menu_urls import CRAWLER_TARGETS

def create_url_queue(crawler_name: str) -> Queue:
    """
    Creates and populates a FIFO (First-In-First-Out) Queue with URLs for a specific crawler.

    Args:
        crawler_name (str): The key name of the website (e.g., 'digikala', 'amazon').

    Returns:
        Queue: A queue containing all URLs to be scraped. 
               Returns an empty queue if the crawler_name is invalid.
    """
    if crawler_name not in CRAWLER_TARGETS:
        print(f"[ERROR] Crawler target '{crawler_name}' not found in configuration.")
        return Queue()
        
    url_queue = Queue()
    urls_dict = CRAWLER_TARGETS[crawler_name]
    
    for key, url in urls_dict.items():
        url_queue.put(url)
        
    return url_queue