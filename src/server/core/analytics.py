"""
Analytics Core Module.

This module handles the business logic for pricing strategies, data cleaning,
and visualization generation. It follows the Single Responsibility Principle
by separating data ingestion, processing, and reporting.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
import logging

from config.settings import (
    TRANSPORT_COST,
    MARKETING_COST,
    PROFIT_MARGIN_PERCENT,
    BASE_PRICE_MULTIPLIER,
    SHOPPING_PRICES,
    FINAL_CSV_NAME,
    OUTPUT_IMAGE_NAME
)

# Setup Logger
logger = logging.getLogger(__name__)

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_combined_data() -> Optional[pd.DataFrame]:
    """Loads the combined raw data from CSV."""
    file_path = DATA_DIR / 'df_combined.csv'
    if not file_path.exists():
        logger.error(f"Input file not found: {file_path}")
        return None
    try:
        return pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return None


def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans raw data and handles missing values."""
    # Ensure numeric types
    df['price_product'] = pd.to_numeric(df['price_product'], errors='coerce').fillna(0)
    return df


def _apply_pricing_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies business logic to calculate costs, margins, and competitive prices.
    
    Logic:
        Our Price = Cost + Transport + Marketing + (Profit Margin * Cost)
    """
    # Align shopping prices with dataset length
    # If dataset is larger than price list, pad with 0. If smaller, slice the list.
    current_len = len(df)
    adjusted_prices = SHOPPING_PRICES[:current_len] + [0] * (current_len - len(SHOPPING_PRICES))

    # Vectorized assignments
    df['others_price'] = df['price_product']
    df['shopping_price'] = adjusted_prices
    df['transport_price'] = TRANSPORT_COST
    df['marketing_price'] = MARKETING_COST

    # Calculate Our Price
    cost_basis = df['shopping_price']
    overheads = df['transport_price'] + df['marketing_price']
    profit_amount = cost_basis * PROFIT_MARGIN_PERCENT
    
    df['our_price'] = cost_basis + overheads + profit_amount

    # Calculate Metrics
    df['base_price'] = df['our_price'] * BASE_PRICE_MULTIPLIER  # Using constant from settings
    df['final_profit'] = profit_amount
    df['competitve_product'] = df['our_price'] < df['others_price']

    return df


def _save_results(df: pd.DataFrame) -> str:
    """Saves the processed dataframe to CSV."""
    output_path = DATA_DIR / FINAL_CSV_NAME
    try:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Pricing analysis saved to: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        return ""


def perform_pricing_analysis() -> str:
    """
    Orchestrates the full pricing analysis workflow.
    
    Steps:
        1. Load Data
        2. Clean Data
        3. Apply Logic
        4. Save Results
    
    Returns:
        str: Path to the generated CSV file, or empty string on failure.
    """
    df = _load_combined_data()
    if df is None or df.empty:
        return ""

    df = _clean_data(df)
    df = _apply_pricing_strategy(df)
    result_path = _save_results(df)
    
    return result_path


def generate_analytics_plot() -> Optional[str]:
    """
    Generates and saves a static analysis plot.
    Uses 'Agg' backend to ensure thread-safety in non-GUI environments.
    """
    final_path = DATA_DIR / FINAL_CSV_NAME
    if not final_path.exists():
        logger.error("Cannot generate plot: Source data missing.")
        return None

    try:
        # Use non-interactive backend
        plt.switch_backend('Agg')
        
        df = pd.read_csv(final_path, encoding='utf-8-sig')
        
        # Plot Logic
        plt.figure(figsize=(12, 7))
        plt.plot(df.index, df['final_profit'], label='Expected Profit', marker='o', color='green')
        plt.plot(df.index, df['our_price'], label='Our Price', linestyle='--', color='blue')
        plt.plot(df.index, df['others_price'], label='Competitor Price', alpha=0.5, color='red')
        
        plt.title('Competitive Pricing Landscape', fontsize=14)
        plt.xlabel('Product Index', fontsize=12)
        plt.ylabel('Price (IRR)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        output_path = LOGS_DIR / OUTPUT_IMAGE_NAME
        plt.savefig(output_path, dpi=100)
        plt.close()
        
        logger.info(f"Analytics plot generated: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Failed to generate plot: {e}")
        return None