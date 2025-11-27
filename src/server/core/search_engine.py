import time
import random
from queue import Queue
from typing import List, Set
from urllib.parse import quote_plus 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.common.logger import setup_logger
from src.server.core.utils import translate_to_english
from config.settings import SEARCH_PATTERNS, MAX_SEARCH_RESULTS

logger = setup_logger(__name__)

def _setup_driver():
    options = Options()
    # options.add_argument('--headless') # Headless OFF for better Stealth
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1366,768")
    
    # --- ULTRA STEALTH SETTINGS ---
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Real User Agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(options=options)

def _human_type(element, text):
    """Types text with random delays between keystrokes."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def search_digikala(query: str) -> List[str]:
    # (Existing logic maintained)
    search_url = SEARCH_PATTERNS['digikala'].format(query)
    logger.info(f"[SEARCH] Digikala: '{query}'")
    driver = _setup_driver()
    links: Set[str] = set()
    try:
        driver.get(search_url)
        time.sleep(2)
        for _ in range(3):
            driver.execute_script(f"window.scrollBy(0, {random.randint(800, 1500)});")
            time.sleep(1)
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/dkp-')]")
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                if href:
                    links.add(href.split('?')[0])
                    if len(links) >= MAX_SEARCH_RESULTS: break
            except: continue
    except Exception as e:
        logger.error(f"[DIGIKALA] Error: {e}")
    finally:
        driver.quit()
    logger.info(f"[DIGIKALA] Found {len(links)} links.")
    return list(links)

def search_amazon(query: str) -> List[str]:
    english_query = translate_to_english(query)
    logger.info(f"[SEARCH] Amazon Agent: '{english_query}'")
    
    driver = _setup_driver()
    links: Set[str] = set()
    
    try:
        # 1. Navigate to Home Page (Safest Entry)
        logger.info("[AMAZON] Navigating to Homepage...")
        driver.get("https://www.amazon.com/")
        time.sleep(random.uniform(2.0, 4.0))
        
        # 2. Check for Captcha/Error immediately
        if "type the characters" in driver.page_source.lower():
            logger.warning("[AMAZON] Captcha detected! Please solve it manually in the browser window if visible.")
            time.sleep(10) # Give user time or wait for refresh
            driver.refresh()
        
        # 3. Perform Search via Search Bar
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
            )
            search_box.clear()
            _human_type(search_box, english_query)
            time.sleep(1)
            
            search_btn = driver.find_element(By.ID, "nav-search-submit-button")
            search_btn.click()
            
            logger.info("[AMAZON] Search submitted.")
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"[AMAZON] Search bar interaction failed: {e}")
            # Fallback to direct URL if homepage interaction fails
            driver.get(SEARCH_PATTERNS['amazon'].format(quote_plus(english_query)))

        # 4. Validate we are on Search Results page
        # If we are still on homepage or error page, don't scrape random links
        if "s?k=" not in driver.current_url and "search" not in driver.title.lower():
            logger.warning("[AMAZON] Not on search result page. Aborting scrape.")
            return []

        # 5. Scrape Results
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        
        elements = driver.find_elements(By.TAG_NAME, "a")
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                # Must look like a product link
                if href and ('/dp/' in href or '/gp/product/' in href):
                    if 'customerReviews' in href or 'offer-listing' in href: continue
                    
                    if href.startswith("/"): href = "https://www.amazon.com" + href
                    
                    if '/dp/' in href:
                        try:
                            # Clean URL to ASIN
                            base = href.split('/dp/')[1].split('/')[0].split('?')[0]
                            clean = href.split('/dp/')[0] + '/dp/' + base
                            links.add(clean)
                        except: links.add(href)
                    else:
                        links.add(href)
                        
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