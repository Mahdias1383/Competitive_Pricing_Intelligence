import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from queue import Queue
from typing import List, Dict, Any
from src.common.logger import setup_logger

logger = setup_logger(__name__)

def scrape_amazon_product_details(queue: Queue, result_list: List[Dict[str, Any]]) -> None:
    options = Options()
    # options.add_argument('--headless') 
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
            time.sleep(2)
            
            # Anti-Interstitial
            try:
                buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button")
                for btn in buttons:
                    if "continue" in str(btn.get_attribute("aria-label")).lower():
                        btn.click()
                        time.sleep(2)
                        break
            except: pass
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            title_tag = soup.find("span", {"id": "productTitle"})
            title = title_tag.get_text().strip() if title_tag else "Unknown Amazon Product"
            
            price_usd = 0.0
            
            # Price Logic
            price_elements = soup.select(".a-price .a-offscreen")
            for p in price_elements:
                text = p.get_text().strip().replace("$", "").replace(",", "")
                try:
                    val = float(text)
                    if val > 0:
                        price_usd = val
                        break 
                except: continue
            
            if price_usd == 0:
                apex = soup.select_one("span.apexPriceToPay span.a-offscreen")
                if apex:
                    try: price_usd = float(apex.get_text().replace("$", "").replace(",", ""))
                    except: pass

            if price_usd > 0:
                # FIXED KEYS
                result_list.append({
                    "product_name": title,
                    "final_price": price_usd,
                    "product_link": url
                })
                logger.info(f"[AMAZON] Scraped: {title[:15]}... - ${price_usd}")
                
        except Exception as e:
            logger.error(f"[AMAZON] Scrape Error: {e}")
        finally:
            driver.quit()