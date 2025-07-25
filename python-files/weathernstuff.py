import requests
from datetime import datetime
import sys
import re

def format_dt(dt_str):
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return dt_str

def parse_coord(coord_str):
    """
    Parses coordinate strings like '37.7495° N' or '85.9700° W'
    Returns decimal degrees as float with proper sign.
    """
    pattern = r'([0-9.+-]+)[°\s]*([NSEW])'
    match = re.search(pattern, coord_str.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid coordinate format: {coord_str}")

    degrees = float(match.group(1))
    direction = match.group(2).upper()

    if direction == 'S' or direction == 'W':
        degrees = -degrees
    return degrees

def get_point_metadata(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching point metadata: {e}")
        sys.exit(1)

def fetch_alerts_for_area(area_code):
    url = f"https://api.weather.gov/alerts/active?zone={area_code}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        sys.exit(1)

def main():
    user_input = input("Enter coordinates like '37.7495° N, 85.9700° W': ").strip()
    if ',' not in user_input:
        print("Invalid input format. Please enter as: lat°, N/S, lon°, E/W")
        sys.exit(1)

    lat_str, lon_str = [x.strip() for x in user_input.split(',', 1)]

    try:
        lat = parse_coord(lat_str)
        lon = parse_coord(lon_str)
    except ValueError as e:
        print(e)
        sys.exit(1)

    print(f"\nParsed coordinates: lat={lat}, lon={lon}\n")
    print(f"Getting NWS metadata for point ({lat}, {lon})...\n")
    metadata = get_point_metadata(lat, lon)
    properties = metadata.get("properties", {})

    zone_id = properties.get("forecastZone") or properties.get("countyZone")

    if not zone_id:
        print("Could not find forecast or county zone for the coordinates.")
        sys.exit(1)

    zone_code = zone_id.split("/")[-1]

    print(f"Using zone: {zone_code} to fetch active alerts...\n")

    alerts_json = fetch_alerts_for_area(zone_code)
    features = alerts_json.get("features", [])

    if not features:
        print("No active warnings or advisories for this location.")
        return

    for feature in features:
        props = feature.get("properties", {})
        event = props.get("event", "Unknown Event")
        onset = props.get("onset")
        expires = props.get("expires")
        description = props.get("description", "").strip()

        print(f"Event: {event}")
        print(f"Starts: {format_dt(onset)}")
        print(f"Expires: {format_dt(expires)}")
        print(f"Description: {description}")
        print("-" * 50)

if __name__ == "__main__":
    main()