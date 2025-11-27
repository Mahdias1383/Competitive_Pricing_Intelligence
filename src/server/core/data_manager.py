"""
Data Manager Module.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from src.common.logger import setup_logger

logger = setup_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_scraped_data_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    file_path = DATA_DIR / filename
    
    # Standard Columns
    cols = ['product_name', 'final_price', 'product_link']

    if not data:
        logger.warning(f"[DATA] No data to save for {filename}. Creating empty file.")
        df = pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(data)
        # Ensure only expected columns exist (and in order)
        # Fill missing columns if any
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df = df[cols]

    try:
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        logger.info(f"[DATA] Saved {len(df)} records to {filename}")
    except Exception as e:
        logger.error(f"[DATA] Failed to save {filename}: {e}")