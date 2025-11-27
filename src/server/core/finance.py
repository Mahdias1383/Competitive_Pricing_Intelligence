"""
Finance Module.
Handles dynamic currency conversion and import cost calculations.
"""

import requests
import re
from src.common.logger import setup_logger

logger = setup_logger(__name__)

# Fallback constants if API fails
FALLBACK_USD_IRR = 60_000
CUSTOMS_DUTY_PERCENT = 0.30  # 30% Customs Tax
SHIPPING_COST_USD = 25       # Approx $25 shipping per item

def get_current_usd_rate() -> float:
    """
    Fetches the current USD to IRR rate.
    Tries multiple sources, falls back to constant if all fail.
    """
    # Source 1: Bonbast API (Unofficial/Scraping mirror) or similar lightweight JSON
    # Since stable free APIs for free-market IRR are rare, we use a reliable scraping logic 
    # or a known public API if available. For this project, we'll simulate a request 
    # to a generic rate provider or fall back gracefully.
    
    try:
        # Example: Using a generic crypto-tether rate as a proxy for free market dollar
        # This is often closer to real IRR rate than official bank rates.
        response = requests.get("https://api.tetherland.com/currencies", timeout=5)
        if response.status_code == 200:
            data = response.json()
            usdt_price = float(data['data']['currencies']['USDT']['price'])
            logger.info(f"[FINANCE] Fetched real-time USD(T) rate: {usdt_price:,.0f} IRR")
            return usdt_price
    except Exception as e:
        logger.warning(f"[FINANCE] Source 1 failed: {e}")

    logger.warning(f"[FINANCE] Using fallback rate: {FALLBACK_USD_IRR:,.0f} IRR")
    return float(FALLBACK_USD_IRR)

def calculate_landed_cost(price_usd: float, exchange_rate: float) -> float:
    """
    Calculates the final price of an imported item in IRR.
    Formula: (Price + Shipping) * Rate * (1 + Customs)
    """
    base_cost = price_usd + SHIPPING_COST_USD
    cost_in_irr = base_cost * exchange_rate
    final_cost = cost_in_irr * (1 + CUSTOMS_DUTY_PERCENT)
    
    # Round to nearest 10,000 for cleaner prices
    return round(final_cost, -4)