"""
Utility functions for the server core.
Currently handles translation services.
"""

from deep_translator import GoogleTranslator
from src.common.logger import setup_logger

logger = setup_logger(__name__)

def translate_to_english(text: str) -> str:
    """
    Translates Persian text to English automatically.
    Used for creating compatible search queries for Amazon.
    
    Args:
        text (str): The input text (e.g., 'اسپرسوساز')
        
    Returns:
        str: Translated text (e.g., 'Espresso Maker') or original text if failed.
    """
    if not text:
        return ""

    # Check if text contains Persian characters (Basic range check)
    has_persian = any("\u0600" <= char <= "\u06FF" for char in text)
    
    if not has_persian:
        return text

    try:
        # logger.info(f"Translating query '{text}' to English...") # Optional verbosity
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        logger.info(f"[TRANSLATE] '{text}' -> '{translated}'")
        return translated
    except Exception as e:
        logger.warning(f"[TRANSLATE] Failed: {e}. Using original query.")
        return text