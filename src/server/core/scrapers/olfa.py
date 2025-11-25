from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from queue import Queue
from typing import List, Dict, Any

from config.settings import PAGE_LOAD_TIMEOUT

def _setup_driver() -> webdriver.Chrome:
    """Configures Chrome driver."""
    options = Options()
    # options.add_argument('--headless') # Uncomment for production
    return webdriver.Chrome(options=options)

def scrape_olfa_product_details(queue: Queue, result_list: List[Dict[str, Any]]) -> None:
    """
    Main worker function for Olfa scraping.
    """
    while not queue.empty():
        url = queue.get()
        driver = _setup_driver()
        
        try:
            print(f"[OLFA] Navigating to: {url}...")
            driver.get(url)
            
            # Wait for title
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product_title"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract Title
            title_tag = soup.find("h1", class_="product_title")
            raw_title = title_tag.get_text().strip() if title_tag else "Unknown"
            # Clean title (remove pipe | if exists)
            title = raw_title.split('|')[0].strip()
            
            # Extract Price
            price = 0.0
            price_tag = soup.find("p", class_="price")
            
            if price_tag:
                price_text = price_tag.get_text().strip()
                # Handle "تومان" and ranges like "1000 - 2000"
                clean_text = price_text.replace("تومان", "").replace(",", "")
                # If range, take the first price
                if '–' in clean_text:
                    clean_text = clean_text.split('–')[0]
                elif '-' in clean_text:
                    clean_text = clean_text.split('-')[0]
                    
                try:
                    price = float(clean_text.strip())
                except ValueError:
                    price = 0.0

            product_data = {
                "name_product": title,
                "price_product": price
            }
            
            result_list.append(product_data)
            print(f"[OLFA] Scraped: {product_data['name_product']} - {product_data['price_product']}")

        except Exception as e:
            print(f"[OLFA] Error processing {url}: {e}")
        finally:
            driver.quit()