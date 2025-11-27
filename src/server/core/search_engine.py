import time
from queue import Queue
from typing import List, Set
from urllib.parse import quote_plus 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.common.logger import setup_logger
from src.server.core.utils import translate_to_english
from config.settings import SEARCH_PATTERNS, MAX_SEARCH_RESULTS, PAGE_LOAD_TIMEOUT

logger = setup_logger(__name__)

def _setup_driver():
    options = Options()
    # options.add_argument('--headless') 
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    
    # Anti-detection settings
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

def search_digikala(query: str) -> List[str]:
    search_url = SEARCH_PATTERNS['digikala'].format(query)
    logger.info(f"[SEARCH] Digikala: '{query}'")
    driver = _setup_driver()
    links: Set[str] = set()
    
    try:
        driver.get(search_url)
        # Scroll to load items
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(2)

        # Broad Selector for Digikala
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/dkp-')]")
        
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                if href:
                    clean_link = href.split('?')[0]
                    links.add(clean_link)
                    if len(links) >= MAX_SEARCH_RESULTS: break
            except: continue
    except Exception as e:
        logger.error(f"[DIGIKALA] Search Error: {e}")
    finally:
        driver.quit()
        
    logger.info(f"[DIGIKALA] Found {len(links)} links.")
    return list(links)

def search_amazon(query: str) -> List[str]:
    english_query = translate_to_english(query)
    search_url = SEARCH_PATTERNS['amazon'].format(quote_plus(english_query))
    logger.info(f"[SEARCH] Amazon: '{english_query}'")
    
    driver = _setup_driver()
    links: Set[str] = set()
    
    try:
        driver.get(search_url)
        time.sleep(3)
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        # ULTRA-ROBUST SELECTOR: Find ALL links containing '/dp/' (Product pages)
        # We verify they are title links by ensuring they have text or are inside headings
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/dp/')]")
        
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                # Filter out sponsored redirects if possible, or keep simple
                if href and '/dp/' in href and not '#customerReviews' in href:
                    # Construct clean URL
                    if href.startswith("/"):
                        full_link = "https://www.amazon.com" + href
                    else:
                        full_link = href
                    
                    # Clean up URL (remove ref=...)
                    if '/dp/' in full_link:
                        # Extract basic product ID part
                        base_part = full_link.split('/dp/')[1].split('/')[0]
                        clean_link = full_link.split('/dp/')[0] + '/dp/' + base_part
                        links.add(clean_link)
                    
                    if len(links) >= MAX_SEARCH_RESULTS: break
            except: continue

    except Exception as e:
        logger.error(f"[AMAZON] Search Error: {e}")
    finally:
        driver.quit()
        
    logger.info(f"[AMAZON] Found {len(links)} links.")
    return list(links)

def perform_search_and_queue(query: str, target_site: str) -> Queue:
    links = []
    if target_site == "digikala":
        links = search_digikala(query)
    elif target_site == "amazon":
        links = search_amazon(query)
    
    q = Queue()
    for link in links:
        q.put(link)
    return q