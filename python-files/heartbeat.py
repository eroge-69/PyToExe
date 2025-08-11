import requests, time

KIOSKO_ID = "K0001"
API_URL = "https://thrarion.com/totems/config/scripts/heartbeat.php"

while True:
    try:
        requests.post(API_URL, data={"id_kiosko": KIOSKO_ID})
    except:
        pass
    time.sleep(60)
