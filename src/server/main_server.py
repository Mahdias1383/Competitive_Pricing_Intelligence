"""
Main Server (Digikala vs Amazon Only).
"""

import socket
import os
import json
from src.common.logger import setup_logger
from config.settings import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, ENCODING
from src.server.core.engine import run_crawler_threads
from src.server.core.data_manager import save_scraped_data_to_csv
from src.server.core.analytics import analyze_purchase_options, generate_comparison_plot
from src.server.core.search_engine import perform_search_and_queue

from src.server.core.scrapers.digikala import scrape_digikala_product_details
from src.server.core.scrapers.amazon import scrape_amazon_product_details

logger = setup_logger(__name__)

def handle_client_connection(conn: socket.socket) -> None:
    try:
        raw_data = conn.recv(BUFFER_SIZE).decode(ENCODING)
        try:
            client_request = json.loads(raw_data)
            search_query = client_request.get("query", "")
        except:
            return

        conn.send(f"ACK: Comparing Prices for '{search_query}'...".encode(ENCODING))
        
        # 1. Digikala
        list_digikala = []
        q_digikala = perform_search_and_queue(search_query, "digikala")
        run_crawler_threads(scrape_digikala_product_details, q_digikala, list_digikala)
        save_scraped_data_to_csv(list_digikala, "digikala.csv")

        # 2. Amazon
        list_amazon = []
        q_amazon = perform_search_and_queue(search_query, "amazon")
        run_crawler_threads(scrape_amazon_product_details, q_amazon, list_amazon)
        save_scraped_data_to_csv(list_amazon, "amazon.csv")
        
        # 3. Analyze
        logger.info("--- Analyzing & Comparing ---")
        report_path = analyze_purchase_options()
        plot_path = generate_comparison_plot()
        
        if report_path:
            conn.send(report_path.encode(ENCODING))
        else:
            conn.send("ERROR: Analysis failed.".encode(ENCODING))
            return

        conn.recv(BUFFER_SIZE) # Wait for ACK
        
        if plot_path and os.path.exists(plot_path):
            with open(plot_path, "rb") as f:
                conn.sendall(f.read())
        
    except Exception as e:
        logger.error(f"Server Error: {e}")
    finally:
        conn.close()

def start_server_app() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(1)
    logger.info(f"Server Ready on {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        conn, _ = server.accept()
        handle_client_connection(conn)