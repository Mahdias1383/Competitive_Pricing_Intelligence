import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
import logging

from src.server.core.finance import get_current_usd_rate, calculate_landed_cost
from config.settings import FINAL_CSV_NAME, OUTPUT_IMAGE_NAME

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
LOGS_DIR = BASE_DIR / 'logs'

def analyze_purchase_options() -> str:
    df_digikala = pd.DataFrame()
    df_amazon = pd.DataFrame()
    
    try:
        if (DATA_DIR / "digikala.csv").exists():
            df_digikala = pd.read_csv(DATA_DIR / "digikala.csv")
        if (DATA_DIR / "amazon.csv").exists():
            df_amazon = pd.read_csv(DATA_DIR / "amazon.csv")
    except Exception as e:
        logger.error(f"Error loading CSVs: {e}")

    if df_digikala.empty and df_amazon.empty:
        return ""

    current_rate = get_current_usd_rate()

    # Process Amazon (Input: final_price is USD)
    if not df_amazon.empty and 'final_price' in df_amazon.columns:
        # Convert USD -> IRR (Landed Cost)
        df_amazon['final_price_irr'] = df_amazon['final_price'].apply(lambda x: calculate_landed_cost(x, current_rate))
        df_amazon['source'] = 'Amazon (Imported)'
        df_amazon['original_price_display'] = df_amazon['final_price'].map('${:,.2f}'.format)
    else:
        df_amazon = pd.DataFrame()

    # Process Digikala (Input: final_price is IRR)
    if not df_digikala.empty and 'final_price' in df_digikala.columns:
        df_digikala['final_price_irr'] = df_digikala['final_price']
        df_digikala['source'] = 'Digikala (Domestic)'
        df_digikala['original_price_display'] = df_digikala['final_price'].map('{:,.0f} IRR'.format)
    else:
        df_digikala = pd.DataFrame()

    # Combine
    df_final = pd.concat([df_digikala, df_amazon], ignore_index=True)
    if df_final.empty: return ""

    df_final = df_final.sort_values(by='final_price_irr')
    
    # Create Final Standard Report
    export_df = pd.DataFrame()
    export_df['product_name'] = df_final['product_name']
    export_df['source'] = df_final['source']
    export_df['final_price'] = df_final['final_price_irr'] # Calculated IRR
    export_df['original_price'] = df_final['original_price_display']
    export_df['product_link'] = df_final['product_link']

    output_path = DATA_DIR / FINAL_CSV_NAME
    export_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"Report saved to {output_path}")
    
    return str(output_path)

def generate_comparison_plot() -> Optional[str]:
    final_path = DATA_DIR / FINAL_CSV_NAME
    if not final_path.exists(): return None

    try:
        plt.switch_backend('Agg')
        df = pd.read_csv(final_path)
        if df.empty: return None

        # Use 'final_price' column which is now the calculated IRR
        summary = df.groupby('source')['final_price'].mean()
        if summary.empty: return None
        
        plt.figure(figsize=(10, 6))
        colors = ['#e74c3c' if 'Amazon' in idx else '#3498db' for idx in summary.index]
        summary.plot(kind='bar', color=colors)
        
        plt.title(f'Average Final Cost Comparison (IRR)', fontsize=14)
        plt.ylabel('Price (IRR)', fontsize=12)
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        output_path = LOGS_DIR / OUTPUT_IMAGE_NAME
        plt.savefig(output_path, dpi=100)
        plt.close()
        return str(output_path)
    except Exception as e:
        logger.error(f"Plot generation failed: {e}")
        return None