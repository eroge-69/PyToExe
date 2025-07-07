import xml.etree.ElementTree as ET
import requests
import os
import json

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEwMTU1NzQsIm9yZ2FuaXphdGlvbklkIjozNzYyODUsImlhdCI6MTc1MTM1NDUxMSwic3ViIjoiUkVTVF9BUElfQVVUSCIsImp0aSI6ImY5MjNkYjQ0LTA5MTQtNGNlNC1iZTk0LWJiNzRlYTNlZjg5YyJ9.QXyOgC0GYmdcf7zu1CDrrYt9OYQ41pb7_G_YmphcJww"

MAINTENANCE_WARNING_THRESHOLD = 900  # Operating hours threshold for maintenance alert

with open("config.json", "r") as f:
    config = json.load(f)

ASSET_ID = config["ASSET_ID"]
MACHINE_STATUS_FILE = config["MACHINE_STATUS_FILE"]
METERS_FILE = f"meters_{ASSET_ID}.json"

def send_alert_email(subject, body):
    # Email sending disabled
    pass

def read_xml_values():
    try:
        status_tree = ET.parse(MACHINE_STATUS_FILE)
        status_root = status_tree.getroot()

        operating_minutes = int(status_root.find("OperatingMinutes").text)
        operating_hours = round(operating_minutes / 60, 2)
        service_interval_hours = int(status_root.find("ServiceIntervalHours").text)
        articles_count = int(status_root.find("TotalArticles").text)
        remaining_hours = round(service_interval_hours - (operating_hours % service_interval_hours), 2)

        return operating_hours, articles_count, remaining_hours
    except Exception as e:
        print("[✖] XML Read Error:", e)
        raise

def load_local_meters():
    if os.path.exists(METERS_FILE):
        with open(METERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_local_meters(meters):
    with open(METERS_FILE, "w") as f:
        json.dump(meters, f)

def create_and_send_readings(operating_hours, articles_count, remaining_hours):
    API_BASE_URL = "https://api.getmaintainx.com/v1"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    meters_to_create = [
        {
            "name": "Operating Hours",
            "unit": "Hours",
            "value": operating_hours
        },
        {
            "name": "Articles Count",
            "unit": "Count",
            "value": articles_count
        },
        {
            "name": "Remaining Hours to Next Service",
            "unit": "Hours",
            "value": remaining_hours
        }
    ]

    print("\n[ℹ️] Loading local meters cache...")
    local_meters = load_local_meters()

    for meter in meters_to_create:
        print(f"\n[ℹ️] Processing meter: '{meter['name']}'")
        meter_id = local_meters.get(meter["name"])
        if meter_id:
            print(f"[ℹ️] Meter '{meter['name']}' already exists (ID: {meter_id}). Sending reading only.")
        else:
            print(f"[ℹ️] Meter '{meter['name']}' not found locally. Creating new meter...")
            create_payload = {
                "assetId": ASSET_ID,
                "name": meter["name"],
                "unit": meter["unit"],
                "description": f"{meter['name']} created from daily sync"
            }
            create_resp = requests.post(f"{API_BASE_URL}/meters", json=create_payload, headers=headers)
            if create_resp.status_code == 201:
                meter_id = create_resp.json().get("id")
                print(f"[✔] Meter '{meter['name']}' created successfully → ID: {meter_id}")
                local_meters[meter["name"]] = meter_id
                save_local_meters(local_meters)
            else:
                print(f"[✖] Failed to create meter '{meter['name']}': {create_resp.text}")
                continue  # Skip sending reading if meter creation failed

        # Send readings as an array (required by MaintainX API) and use 'value' not 'reading'
        reading_payload = [{
            "meterId": meter_id,
            "value": meter["value"]
        }]
        print(f"[ℹ️] Sending reading '{meter['name']}' with value: {meter['value']}...")
        reading_resp = requests.post(f"{API_BASE_URL}/meterReadings", json=reading_payload, headers=headers)

        print(f"[DEBUG] Status Code: {reading_resp.status_code}, Response: {reading_resp.text}")

        if reading_resp.status_code == 201:
            print(f"[✔] Reading sent successfully for '{meter['name']}'")
        else:
            print(f"[✖] Failed to send reading for '{meter['name']}': {reading_resp.text}")

def main():
    try:
        operating_hours, articles_count, remaining_hours = read_xml_values()

        print(f"Operating Hours: {operating_hours}")
        print(f"Articles Count: {articles_count}")
        print(f"Remaining Hours to Maintenance: {remaining_hours}")

        if operating_hours >= MAINTENANCE_WARNING_THRESHOLD:
            print(f"[!] Maintenance Alert: Machine {ASSET_ID} reached {operating_hours} operating hours.")

        create_and_send_readings(operating_hours, articles_count, remaining_hours)

    except Exception as e:
        print("[✖] Script error:", e)

if __name__ == "__main__":
    main()
