from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from queue import Queue
from typing import List, Dict, Any

from config.settings import PAGE_LOAD_TIMEOUT

def _setup_driver() -> webdriver.Chrome:
    """Configures and returns a headless Chrome driver."""
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run without UI
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def scrape_digikala_product_details(queue: Queue, result_list: List[Dict[str, Any]]) -> None:
    """
    Main worker function for Digikala scraping using Selenium with Explicit Waits.
    """
    while not queue.empty():
        url = queue.get()
        driver = _setup_driver()
        
        try:
            print(f"[DIGIKALA] Navigating to: {url}...")
            driver.get(url)
            
            # Smart Wait: Wait until the H1 tag (title) is present
            try:
                WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            except TimeoutException:
                print(f"[DIGIKALA] Timeout waiting for page load: {url}")
            
            # Pass HTML to BeautifulSoup for faster parsing than Selenium
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract Title
            title_tag = soup.find("h1")
            title = title_tag.get_text().strip() if title_tag else "عنوان محصول یافت نشد"
            
            # Extract Price (Digikala class names change often, try to be generic or use specific classes)
            # Based on user's provided selector:
            # class="text-h4 ml-1 text-neutral-800" (Check if this still works, usually regex is safer for classes)
            price = 0.0
            price_tag = soup.find("span", class_=lambda x: x and "text-neutral-800" in x)
            
            if price_tag:
                try:
                    price_text = price_tag.get_text().strip().replace(",", "")
                    price = float(price_text)
                except ValueError:
                    price = 0.0
            
            product_data = {
                "name_product": title,
                "price_product": price
            }
            
            result_list.append(product_data)
            print(f"[DIGIKALA] Scraped: {product_data['name_product']} - {product_data['price_product']}")

        except Exception as e:
            print(f"[DIGIKALA] Error: {e}")
        finally:
            driver.quit()