"""
Concurrency Engine Module.

This module handles the parallel execution of scraper tasks using separate threads.
It ensures that I/O bound tasks (like web scraping) run efficiently.
"""

import threading
from queue import Queue
from typing import Callable, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from src.common.logger import setup_logger

logger = setup_logger(__name__)

def run_crawler_threads(
    target_func: Callable[[Queue, List[Dict[str, Any]]], None], 
    url_queue: Queue, 
    result_list: List[Dict[str, Any]],
    worker_count: int = 2
) -> None:
    """
    Executes a scraping function concurrently using a thread pool.

    Args:
        target_func (Callable): The scraping function to run.
        url_queue (Queue): The queue containing URLs to scrape.
        result_list (List): The shared list to store results.
        worker_count (int): Number of concurrent threads.
    """
    logger.info(f"Starting crawler engine with {worker_count} workers for {target_func.__name__}...")
    
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = []
        for _ in range(worker_count):
            futures.append(executor.submit(target_func, url_queue, result_list))
        
        # Wait for all threads to complete
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Thread execution failed: {e}")

    logger.info("All crawler threads finished execution.")