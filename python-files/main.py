miyav = input("Lütfen enlem giriniz:")
miyav1 = input("Lütfen boylam giriniz:")
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
	"latitude": miyav1,
	"longitude": miyav,
	"hourly": ["pm10", "carbon_monoxide", "carbon_dioxide", "sulphur_dioxide", "ozone", "nitrogen_dioxide"],
	"current": "us_aqi",
	"timezone": "auto",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_aqi = current.Variables(0).Value()

print(f"\nCurrent time: {current.Time()}")
print(f"Enlem ve boylama göre hava kalitesi: {current_aqi}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
hourly_carbon_monoxide = hourly.Variables(1).ValuesAsNumpy()#Numpy librarysiyle website den veri çekmek için API kullanıyorum
hourly_carbon_dioxide = hourly.Variables(2).ValuesAsNumpy()
hourly_sulphur_dioxide = hourly.Variables(3).ValuesAsNumpy()
hourly_ozone = hourly.Variables(4).ValuesAsNumpy()
hourly_nitrogen_dioxide = hourly.Variables(5).ValuesAsNumpy()
print(f"\nVerilen {miyav} enlemi {miyav1} boylamı için saatlik karbondiyoksit: {hourly_carbon_dioxide}")
print(f"\nVerilen {miyav} enlemi {miyav1} boylamı için saatlik karbon monoksit: {hourly_carbon_monoxide}")
print(f"\nVerilen {miyav} enlemi {miyav1} boylamı için saatlik nitrojen dioksit: {hourly_nitrogen_dioxide}")
print(f"\nVerilen {miyav} enlemi {miyav1} boylamı için saatlik ozon: {hourly_ozone}")
print(f"\nVerilen {miyav} enlemi {miyav1} boylamı için saatlik : partkül madde (PM10): {hourly_pm10}")
print(f"\nVerilen {miyav} enlemi {miyav1} boylamı için saatlik kükürt dioksit: {hourly_sulphur_dioxide}")
if current_aqi is not None:
	if current_aqi <= 50:
		print("Hava Kalitesi: İyi")
	elif current_aqi <= 100:
		print("Hava Kalitesi: Orta")
	elif current_aqi <= 150:
		print("Hava Kalitesi: Hassas Gruplar İçin Sağlıksız")
	elif current_aqi <= 200:
		print("Hava Kalitesi: Sağlıksız")
	elif current_aqi <= 300:
		print("Hava Kalitesi: Çok Sağlıksız")
	elif current_aqi < 0:
		print("verdiğiniz enlem ve boylam hatalı olabilir tekrar deneyin")
	else:
		print("Hava Kalitesi: Tehlikeli")