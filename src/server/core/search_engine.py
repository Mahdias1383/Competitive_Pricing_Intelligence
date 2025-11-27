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
    # options.add_argument('--headless') # Headless OFF recommended for Amazon
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1366,768")
    
    # --- ULTRA STEALTH SETTINGS ---
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(options=options)

def _human_type(element, text):
    """Types text with random delays to simulate human behavior."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def _handle_potential_captcha(driver):
    """Checks for the specific error page structure provided."""
    try:
        time.sleep(2)
        src = driver.page_source.lower()
        title = driver.title.lower()
        
        # Indicators from error_page.html
        if "type the characters" in src or "opfcaptcha" in src or "something went wrong" in src:
            logger.warning("[AMAZON AGENT] Captcha/Error detected!")
            
            # Check for simple "Continue" buttons
            try:
                buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue')]")
                if buttons:
                    buttons[0].click()
                    return
            except: pass
            
            # Refresh strategy
            logger.info("[AMAZON AGENT] Refreshing page to bypass...")
            driver.refresh()
            time.sleep(5)
    except: pass

def search_digikala(query: str) -> List[str]:
    # (Standard robust Digikala logic)
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
        # 1. Start at Home Page (Safest entry point)
        logger.info("[AMAZON AGENT] Going to Amazon Homepage...")
        driver.get("https://www.amazon.com/")
        
        # 2. Check for Error Page immediately
        _handle_potential_captcha(driver)
        
        # 3. Find Search Box & Type
        try:
            # Wait for the search box (id found in amazon_home_page.html)
            search_box = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
            )
            logger.info("[AMAZON AGENT] Typing query...")
            search_box.clear()
            _human_type(search_box, english_query)
            time.sleep(1)
            
            # 4. Click Search Button
            search_btn = driver.find_element(By.ID, "nav-search-submit-button")
            search_btn.click()
            logger.info("[AMAZON AGENT] Search submitted.")
            time.sleep(random.uniform(3.0, 5.0))
            
        except Exception as e:
            logger.error(f"[AMAZON AGENT] Interaction failed: {e}")
            # Last resort fallback: direct link
            driver.get(SEARCH_PATTERNS['amazon'].format(quote_plus(english_query)))

        # 5. Extract Results
        _handle_potential_captcha(driver) # Check again after search
        
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        
        # Robust Selector for any product-like link
        elements = driver.find_elements(By.TAG_NAME, "a")
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                if href and ('/dp/' in href or '/gp/product/' in href):
                    # Filter junk
                    if 'customerReviews' in href or 'offer-listing' in href or 'signin' in href: continue
                    
                    if href.startswith("/"): href = "https://www.amazon.com" + href
                    
                    if '/dp/' in href:
                        try:
                            # Extract ASIN to clean URL
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