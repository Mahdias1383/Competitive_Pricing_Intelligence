import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from queue import Queue
from typing import List, Dict, Any
from src.common.logger import setup_logger

logger = setup_logger(__name__)

def scrape_digikala_product_details(queue: Queue, result_list: List[Dict[str, Any]]) -> None:
    options = Options()
    # options.add_argument('--headless') 
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    while not queue.empty():
        url = queue.get()
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            time.sleep(4)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            title_tag = soup.find("h1")
            title = title_tag.get_text().strip() if title_tag else "Unknown Digikala Product"
            
            price_irr = 0.0
            
            # 1. JSON-LD Strategy (Best)
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product':
                                data = item
                                break
                    
                    if data.get('@type') == 'Product':
                        offers = data.get('offers', {})
                        if isinstance(offers, list): offers = offers[0]
                        
                        price_val = offers.get('price')
                        if price_val:
                            # Check currency logic
                            if offers.get('priceCurrency') == 'IRR':
                                price_irr = float(price_val)
                            else:
                                # Assume Toman if not IRR explicit, convert to IRR
                                price_irr = float(price_val) * 10
                            break
                except: continue

            # 2. Meta Tag Fallback
            if price_irr == 0:
                meta_price = soup.find("meta", property="product:price:amount")
                if meta_price and meta_price.get("content"):
                    try: price_irr = float(meta_price["content"])
                    except: pass

            if price_irr > 100_000:
                # Standardized Output Structure
                result_list.append({
                    "product_name": title,
                    "final_price": price_irr, # Rial
                    "product_link": url
                })
                logger.info(f"[DIGIKALA] Scraped: {title[:20]}... - {price_irr:,.0f} IRR")
            else:
                logger.warning(f"[DIGIKALA] Price not found/valid for: {title[:20]}...")
            
        except Exception as e:
            logger.error(f"[DIGIKALA] Scrape Error: {e}")
        finally:
            driver.quit()