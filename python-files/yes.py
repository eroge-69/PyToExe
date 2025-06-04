import requests
import json

email = input("Enter target: ")

api = f"https://zopztlo.zopz-api.com/api/breachsearch?q={email}&username=Kiro&password=Kiro12345"

log = requests.get(api)

if log.status_code == 200:
    print("Request was successful")
elif log.status_code == 404:
    print("Resource not found")
else:
    print(f"status code: {log.status_code}")

try:
    data = log.json()
    print(json.dumps(data, indent=4))
except ValueError:
    print(log.text)