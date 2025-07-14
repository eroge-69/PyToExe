# btc_scanner_client.py
# Python client for BTC Wallet Scanner that controls clBitCrack.exe

import requests
import json
import time
import uuid
import re
import configparser
import logging
import sys
import subprocess
import os

# --- Configuration and Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load Configuration ---
def load_config(config_file='client_config.ini'):
    """Loads configuration from a .ini file."""
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        logger.error(f"Configuration file '{config_file}' not found. Please create it.")
        sys.exit(1)
    config.read(config_file)

    server_url = config.get('Client', 'SERVER_URL')
    client_id = config.get('Client', 'CLIENT_ID', fallback=str(uuid.uuid4()))
    bitcrack_path = config.get('Client', 'BITCRACK_PATH')

    if not server_url:
        logger.error("SERVER_URL not found in config.ini. Please specify it.")
        sys.exit(1)
    if not bitcrack_path:
        logger.error("BITCRACK_PATH not found in config.ini. Please specify it.")
        sys.exit(1)

    return server_url, client_id, bitcrack_path

# --- API Client Functions ---
class ApiClient:
    def __init__(self, server_url, client_id):
        self.server_url = server_url
        self.client_id = client_id
        self.session = requests.Session() # Use a session for persistent connections

    def get_task(self):
        """Requests the next available scanning task from the server."""
        # FIXED: Removed .php from the URL
        url = f"{self.server_url}/api/get_task"
        params = {'client_id': self.client_id}
        logger.info(f"Requesting task from: {url} with client_id={self.client_id}")
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            task_response = response.json()
            logger.info(f"Received task response: {task_response}")
            return task_response
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get task: {e}")
            return None

    def report_result(self, task_id, address, private_key):
        """Reports a found wallet (Bitcoin address and private key) to the server."""
        # FIXED: Removed .php from the URL
        url = f"{self.server_url}/api/report_result"
        payload = {
            "task_id": task_id,
            "address": address,
            "private_key": private_key,
            "client_id": self.client_id
        }
        logger.info(f"Reporting result for task {task_id}: Address={address}, PrivateKey={private_key}")
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info(f"Successfully reported result. Server response: {response.text}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to report result for task {task_id}: {e}")
            return False

    def send_heartbeat(self):
        """Sends a heartbeat to the server to indicate the client is alive."""
        # FIXED: Removed .php from the URL
        url = f"{self.server_url}/api/heartbeat"
        payload = {"client_id": self.client_id}
        logger.debug(f"Sending heartbeat for client: {self.client_id}")
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.debug(f"Heartbeat sent successfully. Server response: {response.text}")
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to send heartbeat: {e}")
            return False

# --- BitCrack Control Function ---
def run_bitcrack(bitcrack_path, start_key, end_key, target_address):
    """
    Executes clBitCrack.exe with the given keyspace and target address.
    Parses its output to find a match.
    """
    keyspace_arg = f"{start_key}:{end_key}"
    command = [
        bitcrack_path,
        "--keyspace", keyspace_arg,
        "-c", target_address,
        # Add any other necessary arguments for clBitCrack.exe here
        # For example, if it needs a specific device: "-d", "0"
        # "--device", "0"
    ]

    logger.info(f"Executing clBitCrack command: {' '.join(command)}")

    # Regex to parse clBitCrack.exe output for a found key and address.
    # This regex assumes an output format like:
    # "Found private key: <hex_priv_key> for address: <btc_address>"
    # You might need to adjust this regex based on the actual output format of your clBitCrack.exe.
    # It captures the hex private key (starting with 0x) and the Bitcoin address.
    found_regex = re.compile(r"(?i)(?:private key|privkey):\s*(0x[0-9a-fA-F]+)\s*(?:address|addr)?:\s*([13][a-km-zA-HJ-NP-Z1-9]{25,34})")

    try:
        # Use subprocess.Popen for real-time output processing (optional, but good for long-running processes)
        # or subprocess.run for simpler blocking execution.
        # For this scenario, subprocess.run is simpler as we wait for it to finish anyway.
        process = subprocess.run(
            command,
            capture_output=True,
            text=True, # Decode stdout/stderr as text
            check=False, # Do not raise CalledProcessError for non-zero exit codes
            encoding='utf-8', # Specify encoding for output
            errors='ignore' # Ignore decoding errors
        )

        stdout = process.stdout
        stderr = process.stderr

        logger.info(f"clBitCrack stdout:\n{stdout}")
        if stderr:
            logger.warning(f"clBitCrack stderr:\n{stderr}")

        if process.returncode != 0:
            logger.error(f"clBitCrack.exe exited with non-zero code: {process.returncode}")
            # Consider if a non-zero code always means an error or just no match found.
            # For now, we'll treat it as a potential error in execution.

        # Parse clBitCrack output for a found key
        for line in stdout.splitlines():
            match = found_regex.search(line)
            if match:
                private_key_hex = match.group(1)
                address = match.group(2)
                logger.info(f"clBitCrack reported a match! Address: {address}, Private Key: {private_key_hex}")
                return private_key_hex, address # Return the first found match

        logger.info("clBitCrack finished without finding a wallet in this range.")
        return None, None # No match found

    except FileNotFoundError:
        logger.error(f"Error: clBitCrack.exe not found at '{bitcrack_path}'. Please check the path in client_config.ini.")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred during clBitCrack execution: {e}")
        return None, None

# --- Main Client Logic Loop ---
def main_loop():
    server_url, client_id, bitcrack_path = load_config()
    api_client = ApiClient(server_url, client_id)

    # Initial heartbeat
    api_client.send_heartbeat()

    # Schedule heartbeats every minute
    # Using a simple loop and sleep here. For more robust scheduling,
    # you might consider a separate thread or a library like `APScheduler`.
    last_heartbeat_time = time.time()

    while True:
        # Send heartbeat every minute
        if time.time() - last_heartbeat_time >= 60:
            api_client.send_heartbeat()
            last_heartbeat_time = time.time()

        task_response = api_client.get_task()

        if task_response:
            status = task_response.get('status')
            if status == "wait":
                logger.info("Server replied 'wait'. No tasks available. Sleeping for 10 seconds...")
                time.sleep(600)
            elif status == "done":
                logger.info("Server replied 'done'. All tasks completed. Exiting.")
                break # Exit the main loop
            else: # A task with start/end/task_id should be present
                task_id = task_response.get('task_id')
                start_key = task_response.get('start')
                end_key = task_response.get('end')
                target_address = task_response.get('target_address')

                if all([task_id, start_key, end_key, target_address]):
                    logger.info(f"Received task_id: {task_id}, range: {start_key} to {end_key}, target: {target_address}")

                    found_private_key, found_address = run_bitcrack(bitcrack_path, start_key, end_key, target_address)

                    if found_private_key and found_address:
                        logger.info("Wallet found! Reporting result to server...")
                        api_client.report_result(task_id, found_address, found_private_key)
                        # After reporting, immediately ask for a new task
                    else:
                        logger.info("clBitCrack finished without finding a wallet in this range. Reporting task complete to server.")
                        api_client.report_result(task_id, "N/A", "N/A") # Report task as complete with N/A
                else:
                    logger.error(f"Unexpected task response format: {task_response}. Retrying in 10 seconds.")
                    time.sleep(10)
        else:
            # API call failed, sleep and retry
            logger.warning("Failed to get task from server. Retrying in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    main_loop()
