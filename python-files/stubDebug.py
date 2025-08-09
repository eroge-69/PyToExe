import base64, requests

URL = ""

try:
    resp = requests.get(URL, timeout=(30, 60))  
    resp.raise_for_status()
    encoded = resp.text.strip()
except requests.Timeout:
    print(e)
except requests.RequestException as e: 
    print(e)
    

