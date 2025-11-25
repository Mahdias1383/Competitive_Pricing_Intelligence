import pandas as pd
import os
from typing import List, Dict, Any
from pathlib import Path

# Define the data directory relative to this file
# Structure: src/server/core/../../../data/processed
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'

# Ensure directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_scraped_data_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Converts a list of dictionaries to a CSV file and saves it in the processed data directory.

    Args:
        data: List of product dictionaries (e.g., [{'name_product': '...', 'price_product': 100}])
        filename: Name of the file (e.g., 'amazon.csv')
    """
    if not data:
        print(f"[WARNING] No data to save for {filename}")
        # Create an empty dataframe with columns to avoid errors later
        df = pd.DataFrame(columns=['name_product', 'price_product'])
    else:
        df = pd.DataFrame(data)

    file_path = DATA_DIR / filename
    try:
        df.to_csv(file_path, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility in Persian
        print(f"[DATA] Saved {len(df)} records to {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save {filename}: {e}")

def combine_dataframes(dfs: List[pd.DataFrame], output_filename: str = 'df_combined.csv') -> pd.DataFrame:
    """
    Combines multiple DataFrames into one and saves the result.
    """
    if not dfs:
        print("[WARNING] No DataFrames to combine.")
        return pd.DataFrame()

    try:
        df_combined = pd.concat(dfs, ignore_index=True)
        file_path = DATA_DIR / output_filename
        df_combined.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"[DATA] Combined data saved to {file_path}")
        return df_combined
    except Exception as e:
        print(f"[ERROR] Failed to combine dataframes: {e}")
        return pd.DataFrame()

def load_csv_as_df(filename: str) -> pd.DataFrame:
    """Helper to load a CSV from the data directory."""
    file_path = DATA_DIR / filename
    if file_path.exists():
        return pd.read_csv(file_path, encoding='utf-8-sig')
    return pd.DataFrame()