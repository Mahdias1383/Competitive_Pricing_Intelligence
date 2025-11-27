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
from config.settings import SEARCH_PATTERNS, MAX_SEARCH_RESULTS, PAGE_LOAD_TIMEOUT

logger = setup_logger(__name__)

def _setup_driver():
    options = Options()
    # options.add_argument('--headless') # Headless OFF is recommended for Amazon
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    
    # Anti-detection: Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

def _handle_captcha_interstitial(driver):
    """
    Analyzes the page to see if it's the error page uploaded by user.
    """
    try:
        time.sleep(2)
        page_source = driver.page_source.lower()
        title = driver.title.lower()
        
        # Check for specific signatures found in 'error_page.html'
        is_captcha = (
            "type the characters" in page_source or
            "enter the characters" in page_source or
            "opfcaptcha" in page_source or
            "something went wrong" in page_source
        )
        
        if is_captcha:
            logger.warning("[AMAZON AGENT] Captcha/Error Page Detected!")
            
            # Check if there is a 'Continue to Amazon' button (rare but possible)
            try:
                buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue')]")
                if buttons:
                    buttons[0].click()
                    return
            except: pass
            
            # Since solving captcha automatically is hard without API, 
            # we refresh once or wait for manual input if visible mode.
            logger.info("[AMAZON AGENT] Refreshing to bypass...")
            driver.refresh()
            time.sleep(4)
    except: pass

def _human_type(element, text):
    """Types text with random delays like a human."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def search_digikala(query: str) -> List[str]:
    # (Same robust Digikala logic as before)
    search_url = SEARCH_PATTERNS['digikala'].format(query)
    logger.info(f"[SEARCH] Digikala: '{query}'")
    driver = _setup_driver()
    links: Set[str] = set()
    
    try:
        driver.get(search_url)
        time.sleep(2)
        for _ in range(3):
            driver.execute_script(f"window.scrollBy(0, {random.randint(800, 1500)});")
            time.sleep(1.5)

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
    return list(links)

def search_amazon(query: str) -> List[str]:
    """
    New 'Agent' Strategy: Go Home -> Find Box -> Type -> Search
    """
    english_query = translate_to_english(query)
    logger.info(f"[SEARCH] Amazon Agent starting for: '{english_query}'")
    
    driver = _setup_driver()
    links: Set[str] = set()
    
    try:
        # 1. Go to Home Page (Safest Entry)
        logger.info("[AMAZON AGENT] Navigating to Homepage...")
        driver.get("https://www.amazon.com/")
        
        # 2. Check for Error Page immediately
        _handle_captcha_interstitial(driver)
        
        # 3. Find Search Box
        try:
            # ID from 'amazon_home_page.html'
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            logger.info("[AMAZON AGENT] Search box found. Typing...")
            
            # 4. Clear and Type like a human
            search_box.clear()
            _human_type(search_box, english_query)
            time.sleep(1)
            
            # 5. Click Search Button
            try:
                search_btn = driver.find_element(By.ID, "nav-search-submit-button")
                search_btn.click()
            except:
                search_box.send_keys(Keys.RETURN) # Fallback
            
            logger.info("[AMAZON AGENT] Search submitted. Waiting for results...")
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"[AMAZON AGENT] Failed to perform search on homepage: {e}")
            # Fallback to direct link if homepage method fails completely
            driver.get(SEARCH_PATTERNS['amazon'].format(quote_plus(english_query)))

        # 6. Extract Results (Using the robust logic)
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        # Ultra-Robust Selector
        elements = driver.find_elements(By.TAG_NAME, "a")
        
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                if href and ('/dp/' in href or '/gp/product/' in href):
                    if '#customerReviews' in href or 'offer-listing' in href or 'signin' in href: continue
                    
                    if href.startswith("/"): href = "https://www.amazon.com" + href
                    
                    if '/dp/' in href:
                        try:
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