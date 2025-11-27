import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from queue import Queue
from typing import List, Dict, Any
from src.common.logger import setup_logger

logger = setup_logger(__name__)

def bypass_interstitial(driver):
    """
    Handles Amazon error pages (Captcha/Something went wrong).
    """
    try:
        page_source = driver.page_source.lower()
        
        # Check based on 'error_page.html' analysis
        is_blocked = (
            "robot check" in driver.title.lower() or 
            "type the characters" in page_source or
            "opfcaptcha" in page_source or
            "something went wrong" in page_source
        )
        
        if is_blocked:
            logger.warning("[AMAZON] Blocked. Attempting bypass...")
            
            # Try reloading first
            driver.refresh()
            time.sleep(random.uniform(3.0, 5.0))
            
            # If still blocked, look for 'Continue' buttons
            try:
                # Some error pages have a "Try different image" or "Continue"
                buttons = driver.find_elements(By.XPATH, "//button | //a[contains(@href, 'home')]")
                if buttons:
                    # Random interaction
                    pass 
            except: pass
            
            return True
    except: pass
    return False

def scrape_amazon_product_details(queue: Queue, result_list: List[Dict[str, Any]]) -> None:
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    while not queue.empty():
        url = queue.get()
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            time.sleep(random.uniform(2.0, 4.0))
            
            bypass_interstitial(driver)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            title_tag = soup.find("span", {"id": "productTitle"})
            title = title_tag.get_text().strip() if title_tag else "Unknown Amazon Product"
            
            price_usd = 0.0
            
            price_elements = soup.select(".a-price .a-offscreen")
            for p in price_elements:
                text = p.get_text().strip().replace("$", "").replace(",", "")
                try:
                    val = float(text)
                    if val > 5: 
                        price_usd = val
                        break 
                except: continue
            
            if price_usd == 0:
                apex = soup.select_one("span.apexPriceToPay span.a-offscreen")
                if apex:
                    try: price_usd = float(apex.get_text().replace("$", "").replace(",", ""))
                    except: pass

            if price_usd > 0:
                result_list.append({
                    "product_name": title,
                    "final_price": price_usd,
                    "product_link": url
                })
                logger.info(f"[AMAZON] Scraped: {title[:15]}... - ${price_usd}")
            else:
                logger.warning(f"[AMAZON] Price missing for: {title[:15]}...")
                
        except Exception as e:
            logger.error(f"[AMAZON] Scrape Error: {e}")
        finally:
            driver.quit()