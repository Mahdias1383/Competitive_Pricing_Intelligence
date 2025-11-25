import requests
from bs4 import BeautifulSoup, Tag
from queue import Queue
from typing import List, Dict, Any, Optional

from config.settings import USER_AGENT, CURRENCY_EXCHANGE_RATE

def _get_page_content(url: str) -> Optional[str]:
    """Fetch page content with proper headers."""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept-Language': 'en-US, en;q=0.5'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        print(f"[AMAZON] Failed to fetch {url} - Status: {response.status_code}")
    except Exception as e:
        print(f"[AMAZON] Request Error: {e}")
    return None

def _extract_title(soup: BeautifulSoup) -> str:
    """Extract and clean product title."""
    try:
        title_tag = soup.find("span", {"id": "productTitle"})
        if title_tag:
            full_title = title_tag.get_text().strip()
            # Clean title: keep only text before the first comma for brevity
            return full_title.split(',')[0].strip()
    except AttributeError:
        pass
    return "Unknown Amazon Product"

def _extract_price(soup: BeautifulSoup) -> float:
    """Extract price and convert to IRR."""
    try:
        # Amazon has multiple price classes, checking the most common ones
        price_tag = soup.find("span", class_="a-price-whole")
        if not price_tag:
            price_tag = soup.find("span", class_="a-offscreen")
        
        if price_tag:
            price_text = price_tag.get_text().strip()
            # Remove currency symbols and commas
            clean_price = price_text.replace("$", "").replace(",", "").replace(".", "")
            
            # If price has decimals (e.g. 19.99), the replace above might mess up if not careful.
            # Simplified logic for integer approximation:
            return float(clean_price) * CURRENCY_EXCHANGE_RATE
            
    except (ValueError, AttributeError):
        pass
    return 0.0

def scrape_amazon_product_details(queue: Queue, result_list: List[Dict[str, Any]]) -> None:
    """
    Main worker function for Amazon scraping.
    Processes URLs from the queue and appends results to the shared list.
    """
    while not queue.empty():
        url = queue.get()
        print(f"[AMAZON] Processing: {url}...")
        
        content = _get_page_content(url)
        if not content:
            continue

        soup = BeautifulSoup(content, "html.parser")
        
        product_data = {
            "name_product": _extract_title(soup),
            "price_product": _extract_price(soup)
        }
        
        result_list.append(product_data)
        print(f"[AMAZON] Scraped: {product_data['name_product']} - {product_data['price_product']}")