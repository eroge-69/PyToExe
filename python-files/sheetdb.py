import requests

api_url = "https://sheetdb.io/api/v1/1527cs9mwax0q"
response = requests.get(api_url)
data = response.json()
print(data)
