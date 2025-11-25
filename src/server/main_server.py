"""
Main Server Application.

Listens for client connections and orchestrates the crawling and analysis workflow.
"""

import socket
import os
from pathlib import Path
from src.common.logger import setup_logger
from config.settings import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, ENCODING
from src.server.core.utils import create_url_queue  # Changed name in Step 1
from src.server.core.engine import run_crawler_threads
from src.server.core.data_manager import save_scraped_data_to_csv, combine_dataframes
from src.server.core.analytics import perform_pricing_analysis, generate_analytics_plot

# Import Scrapers
from src.server.core.scrapers.digikala import scrape_digikala_product_details
from src.server.core.scrapers.amazon import scrape_amazon_product_details
from src.server.core.scrapers.olfa import scrape_olfa_product_details

logger = setup_logger(__name__)

def handle_client_connection(conn: socket.socket) -> None:
    """
    Handles the communication workflow with a connected client.
    """
    try:
        # 1. Receive Start Command
        request = conn.recv(BUFFER_SIZE).decode(ENCODING)
        logger.info(f"Received request: {request}")
        
        conn.send("ACK: Server started processing...".encode(ENCODING))
        
        # 2. Start Scraping Process
        logger.info("--- Starting Scraping Phase ---")
        
        # We create local lists for thread safety (State is not global anymore)
        list_amazon = []
        list_digikala = []
        list_olfa = []
        
        # Amazon
        q_amazon = create_url_queue("amazon")
        run_crawler_threads(scrape_amazon_product_details, q_amazon, list_amazon)
        save_scraped_data_to_csv(list_amazon, "amazon.csv")
        
        # Digikala
        q_digikala = create_url_queue("digikala")
        run_crawler_threads(scrape_digikala_product_details, q_digikala, list_digikala)
        save_scraped_data_to_csv(list_digikala, "digikala.csv")
        
        # Olfa
        q_olfa = create_url_queue("olfa")
        run_crawler_threads(scrape_olfa_product_details, q_olfa, list_olfa)
        save_scraped_data_to_csv(list_olfa, "olfa.csv")
        
        # 3. Merge Data (Re-loading from CSVs to ensure consistency with data_manager logic)
        # Or you could convert lists to DF directly here, but let's stick to the flow
        from src.server.core.data_manager import load_csv_as_df
        df_amazon = load_csv_as_df("amazon.csv")
        df_digikala = load_csv_as_df("digikala.csv")
        df_olfa = load_csv_as_df("olfa.csv")
        
        combine_dataframes([df_amazon, df_digikala, df_olfa])
        
        # 4. Analytics
        logger.info("--- Running Analytics ---")
        final_csv_path = perform_pricing_analysis()
        plot_path = generate_analytics_plot()
        
        # 5. Send Result Path
        if final_csv_path:
            conn.send(final_csv_path.encode(ENCODING))
        else:
            conn.send("ERROR: Analysis failed.".encode(ENCODING))
            return

        # Wait for Client Acknowledgement
        client_ack = conn.recv(BUFFER_SIZE).decode(ENCODING)
        logger.info(f"Client ACK: {client_ack}")
        
        # 6. Send Plot Image
        if plot_path and os.path.exists(plot_path):
            logger.info(f"Sending plot image: {plot_path}")
            with open(plot_path, "rb") as f:
                image_data = f.read()
                conn.sendall(image_data)
            logger.info("Image sent successfully.")
        else:
            logger.warning("Plot image not found.")

    except Exception as e:
        logger.error(f"Error handling client: {e}")
        error_msg = f"SERVER_ERROR: {str(e)}"
        conn.send(error_msg.encode(ENCODING))
    finally:
        conn.close()
        logger.info("Connection closed.")

def start_server_app() -> None:
    """Initializes the socket server and listens for connections."""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen(1)
        logger.info(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
        
        while True:
            conn, addr = server.accept()
            logger.info(f"Accepted connection from {addr}")
            handle_client_connection(conn)
            # Break after one client for this demo, or remove break to keep running
            # break 
            
    except Exception as e:
        logger.critical(f"Server crash: {e}")
    finally:
        server.close()