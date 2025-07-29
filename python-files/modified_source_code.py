import requests
import time

def extract_source_code(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            break
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 503:
                print(f"503 Service Unavailable. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"HTTP error occurred: {http_err}")
                return
        except Exception as err:
            print(f"An error occurred: {err}")
            return

    source_code = response.text
    print("Source Code:")
    print(source_code)

    with open("source_code.html", "w", encoding="utf-8") as file:
        file.write(source_code)
    print("\nSource code saved to 'source_code.html'.")

target_url =input("enter website ") 
extract_source_code(target_url)