import sys
import os

# اضافه کردن مسیر فعلی به مسیرهای پایتون تا پکیج‌ها شناخته شوند
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def main():
    print("Welcome to Competitive Pricing Intelligence System")
    print("1. Run Server (Crawler & Analyzer)")
    print("2. Run Client (Dashboard & Monitor)")
    
    choice = input("Select an option (1/2): ").strip()
    
    if choice == '1':
        print("Starting Server...")
        # ایمپورت داخل تابع انجام می‌شود تا اگر dependency خاصی نصب نبود، کل برنامه کرش نکند
        from src.server.main_server import start_server_app
        start_server_app()
    elif choice == '2':
        print("Starting Client...")
        from src.client.main_client import start_client_app
        start_client_app()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()