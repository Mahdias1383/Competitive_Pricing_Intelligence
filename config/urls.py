from typing import Dict

"""
This module contains the initial URLs for the target products across different e-commerce websites.
It serves as the primary data source for the crawlers.
"""

# Dictionary containing target URLs grouped by website name.
# Structure: { "website_name": { "url_id": "actual_url" } }
PRODUCT_URLS: Dict[str, Dict[str, str]] = {
    "digikala": {
        "url1": "https://www.digikala.com/product/dkp-14664702/اسپرسو-ساز-گوسونیک-مدل-gem-873/",
        "url2": "https://www.digikala.com/product/dkp-1901244/اسپرسوساز-نوا-مدل-nova-ncm-128exps/",
        "url3": "https://www.digikala.com/product/dkp-4836058/اسپرسو-ساز-دولچه-گوستو-مدل-mini-me/",
        "url4": "https://www.digikala.com/product/dkp-3665287/اسپرسو-ساز-نسپرسو-مدل-pixie-en124s/",
        "url5": "https://www.digikala.com/product/dkp-4043003/اسپرسوساز-زیگما-مدل-rl-222/",
        "url6": "https://www.digikala.com/product/dkp-6220336/اسپرسو-ساز-مباشی-مدل-me-ecm-2034/",
        "url7": "https://www.digikala.com/product/dkp-3473783/اسپرسو-ساز-مباشی-مدل-ecm2010/",
        "url8": "https://www.digikala.com/product/dkp-3559135/اسپرسوساز-مباشی-مدل-ecm2013/",
        "url9": "https://www.digikala.com/product/dkp-235026/اسپرسو-ساز-دلونگی-مدل-ec685/",
        "url10": "https://www.digikala.com/product/dkp-2454645/اسپرسو-ساز-فیلیپس-مدل-ep3246/"
    },
    "olfa": {
        "url1": "https://olfashop.com/product/اسپرسو-ساز-فیلیپس-مدل-ep5443-70/",
        "url2": "https://olfashop.com/product/اسپرسوساز-نوا-مدل-128/",
        "url3": "https://olfashop.com/product/قهوه-ساز-مدل-tis30129rw-بوش/",
        "url4": "https://olfashop.com/product/اسپرسو-ساز-دلونگی-ec-235/",
        "url5": "https://olfashop.com/product/اسپرسوساز-دلونگی-مدل-ec7/",
        "url6": "https://olfashop.com/product/قهوه-ساز-مدل-2034-مباشی/",
        "url7": "https://olfashop.com/product/اسپرسوساز-مباشی-مدل-2010-me-ecm/",
        "url8": "https://olfashop.com/product/قهوه-ساز-مدل-ep3246-فیلیپس/",
        "url9": "https://olfashop.com/product/قهوه-ساز-مدل-2013-مباشی/",
        "url10": "https://olfashop.com/product/قهوه-ساز-مدل-685-دلونگی/"
    },
    "amazon": {
        "url1": "https://www.amazon.com/Breville-BES840XL-Infuser-Espresso-Machine/dp/B0089SSOR6/",
        "url2": "https://www.amazon.com/Breville-Espresso-Machine-Impress-BES876DBL/dp/B0B5F4K1R7/",
        "url3": "https://www.amazon.com/Yabano-Espresso-Machine-Cappuccino-Frother/dp/B07T7H15M7/",
        "url4": "https://www.amazon.com/Yabano-Espresso-Machine-Cappuccino-Frother/dp/B0BTRWQFZJ/",
        "url5": "https://www.amazon.com/Lavazza-Single-Serve-Espresso-Machine/dp/B07CLF8L51/"
    }
}