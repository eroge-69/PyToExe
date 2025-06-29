import re
import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

market_regions = {
    "Central Florida": {
        "counties": {"Brevard", "Lake", "Marion", "Orange", "Osceola", "Seminole", "Sumter", "Volusia"},
        "color": "🟧 Orange"
    },
    "West Florida": {
        "counties": {"Citrus", "Desoto", "Hardee", "Hernando", "Hillsborough", 
                    "Manatee", "Pasco", "Pinellas", "Polk", "Sarasota"},
        "color": "🟦 Blue"
    },
    "North Florida": {
        "counties": {"Alachua", "Bradford", "Clay", "Duval", "Flagler", 
                    "Nassau", "Putnam", "St. Johns"},
        "color": "🟨 Yellow"
    }
}

all_covered_counties = set()
for region in market_regions.values():
    all_covered_counties.update(region["counties"])

def get_county_from_input(input_str):
    geolocator = Nominatim(user_agent="florida-market-checker")
    try:
        geo = geolocator.geocode(input_str + ", Florida" if not re.search(r",\s*FL", input_str, re.IGNORECASE) else input_str)
        if not geo:
            return None, "Could not geocode input."
            
        rev = geolocator.reverse((geo.latitude, geo.longitude), exactly_one=True)
        if not rev:
            return None, "Could not reverse geocode location."

        addr = rev.raw.get("address", {})
        county = addr.get("county", "").replace(" County", "")
        city = addr.get("city", "") or addr.get("town", "") or addr.get("village", "") or ""
        state = addr.get("state", "")
        
        if state != "Florida":
            return None, "❌ This tool only supports Florida locations."

        return county, city
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None, "❌ Geocoding service unavailable. Please try again later."

def get_region_info(county):
    for region_name, region_data in market_regions.items():
        if county in region_data["counties"]:
            return region_name, region_data["color"]
    return None, None

def is_in_market(input_str):
    cleaned = input_str.strip()
    
    if "county" in cleaned.lower():
        county_name = re.sub(r"(?i)\s*county", "", cleaned).strip().title()
        if county_name in all_covered_counties:
            region, color = get_region_info(county_name)
            return f"✅ {county_name} County is in the market.\nRegion: {region} ({color})"
        return f"❌ {county_name} County is NOT in the market."

    if re.fullmatch(r"\d{5}", cleaned):
        county, city = get_county_from_input(cleaned)
        if not county:
            return county
        if county in all_covered_counties:
            region, color = get_region_info(county)
            return (f"✅ ZIP {cleaned} ({city}, {county} County) is in the market.\n"
                    f"Region: {region} ({color})")
        return f"❌ ZIP {cleaned} ({city}, {county} County) is NOT in the market."

    if "FL" not in cleaned.upper() and "Florida" not in cleaned.title():
        return "❌ Address must include 'FL' or 'Florida'."

    county, city = get_county_from_input(cleaned)
    if not county:
        return county
    if county in all_covered_counties:
        region, color = get_region_info(county)
        return (f"✅ {city}, {county} County is in the market.\n"
                f"Region: {region} ({color})")
    return f"❌ {city}, {county} County is NOT in the market."

def main():
    print("Florida Market Checker")
    print("----------------------")
    print("Enter a Florida address, ZIP code, or county name")
    print("Examples:")
    print("  - 123 Main St, Tampa, FL 33610")
    print("  - 33610")
    print("  - Hillsborough County")
    print("----------------------")
    
    while True:
        try:
            user_input = input("\nEnter input (or 'quit' to exit): ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
                
            result = is_in_market(user_input)
            print("\n" + result + "\n")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")  # Keeps window open after completion