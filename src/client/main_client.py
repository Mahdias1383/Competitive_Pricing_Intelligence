"""
Main Client Application.

Connects to the analysis server, triggers the workflow, and displays results.
"""

import socket
import sys
import subprocess
import os
import pandas as pd
from pathlib import Path
from src.common.logger import setup_logger
from config.settings import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, ENCODING

logger = setup_logger(__name__)

def open_file_default(filepath: str) -> None:
    """Opens a file with the default OS application."""
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.call(["open", filepath])
        else:
            subprocess.call(["xdg-open", filepath])
    except Exception as e:
        logger.error(f"Could not open file {filepath}: {e}")

def start_client_app() -> None:
    """Runs the client-side logic."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        logger.info(f"Connecting to server at {SERVER_HOST}:{SERVER_PORT}...")
        client.connect((SERVER_HOST, SERVER_PORT))
        
        # 1. Send Start Signal
        client.send("START_WORKFLOW".encode(ENCODING))
        
        # 2. Receive Initial Response
        response = client.recv(BUFFER_SIZE).decode(ENCODING)
        logger.info(f"Server Status: {response}")
        
        print("\n[INFO] Waiting for server to crawl and process data. This may take a while...\n")
        
        # 3. Receive Result Path (Blocking wait)
        result_path_str = client.recv(BUFFER_SIZE).decode(ENCODING)
        
        if "ERROR" in result_path_str:
            logger.error(f"Server reported error: {result_path_str}")
            return

        logger.info(f"Received data file path: {result_path_str}")
        result_path = Path(result_path_str)
        
        if result_path.exists():
            df = pd.read_csv(result_path)
            print("\n--- ANALYSIS RESULT PREVIEW ---")
            print(df.head())
            print("-------------------------------\n")
        
        # 4. Send Acknowledgement
        client.send("DATA_RECEIVED".encode(ENCODING))
        
        # 5. Receive Image (Robust Loop)
        logger.info("Receiving analysis plot...")
        image_data = b""
        while True:
            # Set a timeout just in case server hangs, though blocking is default
            chunk = client.recv(BUFFER_SIZE)
            if not chunk:
                break
            image_data += chunk
            
            # Simple check: if chunk is smaller than buffer, it MIGHT be the end
            # but socket streams are tricky. The server closes connection at the end
            # which causes 'chunk' to be empty, breaking the loop safely.
            
        # Save Image
        output_image = "received_analysis_plot.png"
        with open(output_image, "wb") as f:
            f.write(image_data)
            
        logger.info(f"Plot saved to local file: {output_image}")
        
        # Open image automatically
        open_file_default(output_image)

    except ConnectionRefusedError:
        logger.error("Connection failed. Is the server running?")
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        client.close()