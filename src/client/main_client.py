"""
Client App (Comparison Mode).
"""

import socket
import sys
import os
import json
import pandas as pd
import subprocess
from src.common.logger import setup_logger
from config.settings import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, ENCODING

logger = setup_logger(__name__)

def open_file(filepath):
    if sys.platform == "win32": os.startfile(filepath)
    else: subprocess.call(["xdg-open", filepath])

def start_client_app() -> None:
    print("\n--- Global Price Comparison System ---")
    query = input("What product do you want to compare? (e.g. iPhone 13): ").strip()
    
    if not query: return

    # Simplified payload, we always check both sites now
    payload = {"query": query}
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        client.send(json.dumps(payload).encode(ENCODING))
        
        print(f"\n[SERVER] {client.recv(BUFFER_SIZE).decode(ENCODING)}")
        print("Gathering data from Digikala & Amazon (20 items each)... Please wait.\n")
        
        report_path = client.recv(BUFFER_SIZE).decode(ENCODING)
        if "ERROR" in report_path:
            print("Server Failed.")
            return

        print(f"\nReport Saved: {report_path}")
        if os.path.exists(report_path):
            df = pd.read_csv(report_path)
            print(df[['name_product', 'final_price', 'source']].head(5))

        client.send("ACK".encode(ENCODING))
        
        img_data = b""
        while True:
            chunk = client.recv(BUFFER_SIZE)
            if not chunk: break
            img_data += chunk
            
        with open("comparison_result.png", "wb") as f: f.write(img_data)
        open_file("comparison_result.png")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.close()