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
    # options.add_argument('--headless') # در صورت نیاز فعال کنید
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    
    # تنظیمات ضد تشخیص ربات
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
        try:
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/product/dkp-')]"))
            )
        except: pass

        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(2)

        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/dkp-')]")
        
        for elem in elements:
            try:
                href = elem.get_attribute('href')
                if href and '/product/dkp-' in href:
                    clean_link = href.split('?')[0]
                    links.add(clean_link)
                    if len(links) >= MAX_SEARCH_RESULTS:
                        break
            except: continue

    except Exception as e:
        logger.error(f"[DIGIKALA] Search Error: {e}")
    finally:
        driver.quit()
        
    logger.info(f"[DIGIKALA] Found {len(links)} links.")
    return list(links)

def search_amazon(query: str) -> List[str]:
    english_query = translate_to_english(query)
    # استفاده از quote_plus برای تبدیل فاصله به +
    search_url = SEARCH_PATTERNS['amazon'].format(quote_plus(english_query))
    logger.info(f"[SEARCH] Amazon: '{english_query}' -> {search_url}")
    
    driver = _setup_driver()
    links: Set[str] = set()
    
    try:
        driver.get(search_url)
        time.sleep(3) # صبر برای ریدارکت‌های احتمالی
        
        # اسکرول واقعی برای رفتار انسانی
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)
        
        # سلکتور جامع برای آمازون
        # ابتدا تلاش برای یافتن لینک‌های استاندارد در گرید
        results = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']//h2//a")
        
        # اگر پیدا نشد، تلاش برای ساختار لیستی
        if not results:
             results = driver.find_elements(By.XPATH, "//a[contains(@class, 'a-link-normal') and contains(@href, '/dp/')]")

        for elem in results:
            try:
                href = elem.get_attribute('href')
                if href and ('/dp/' in href or '/gp/' in href):
                    if href.startswith("/"):
                        href = "https://www.amazon.com" + href
                    links.add(href)
                    if len(links) >= MAX_SEARCH_RESULTS:
                        break
            except: continue

    except Exception as e:
        logger.error(f"[AMAZON] Search Error: {e}")
    finally:
        driver.quit()
        
    logger.info(f"[AMAZON] Found {len(links)} links.")
    return list(links)

def perform_search_and_queue(query: str, target_site: str) -> Queue:
    if target_site == "digikala":
        links = search_digikala(query)
    elif target_site == "amazon":
        links = search_amazon(query)
    else:
        return Queue()

    q = Queue()
    for link in links:
        q.put(link)
    return q