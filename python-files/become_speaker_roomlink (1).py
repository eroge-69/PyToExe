
import requests
import concurrent.futures
import logging
import time

# Setup logging
logging.basicConfig(
    filename="become_speaker.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Read tokens from file
try:
    with open("tokens.txt", "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    logging.error("tokens.txt not found.")
    exit("tokens.txt file is missing.")

# Ask user for Clubhouse room link
room_url = input("Enter the Clubhouse room link: ").strip()

# Extract channel id from the room link using API
def get_channel_id_from_link(link):
    api_url = "https://www.clubhouseapi.com/api/get_channel_from_link"
    try:
        res = requests.post(api_url, json={"url": link}, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data.get("channel")
    except Exception as e:
        logging.error(f"Failed to extract channel ID from room link: {e}")
        exit("Could not extract channel ID from the provided room link.")

channel_id = get_channel_id_from_link(room_url)

if not channel_id:
    exit("Channel ID not found in room link. Exiting...")

url = "https://www.clubhouseapi.com/api/become_speaker"

headers_template = {
    "CH-AppVersion": "1.0.37",
    "CH-Locale": "en_US",
    "Content-Type": "application/json"
}

payload = {
    "channel": channel_id
}

def make_request(token):
    headers = headers_template.copy()
    headers["Authorization"] = f"Token {token}"
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        status = response.status_code
        if status == 200:
            logging.info(f"SUCCESS - Token: {token} | Response: {response.json()}")
        elif status == 429:
            logging.warning(f"RATE LIMITED - Token: {token} | Response: {response.text}")
        else:
            logging.error(f"FAILURE - Token: {token} | Status: {status} | Response: {response.text}")
    except requests.exceptions.Timeout:
        logging.error(f"TIMEOUT - Token: {token}")
    except requests.exceptions.RequestException as e:
        logging.error(f"REQUEST ERROR - Token: {token} | Error: {str(e)}")

# Execute all requests concurrently
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    executor.map(make_request, tokens)

total_time = time.time() - start_time
logging.info(f"Completed all requests in {total_time:.2f} seconds")
