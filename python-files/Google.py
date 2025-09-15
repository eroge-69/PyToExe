import asyncio
import pandas as pd
import urllib.parse
from playwright.async_api import async_playwright
import os
import sys
from pathlib import Path
import uuid
import subprocess

def get_system_uuid():
    try:
        output = subprocess.check_output('wmic csproduct get uuid', shell=True).decode()
        for line in output.split('\n'):
            line = line.strip()
            if line and line != 'UUID':
                return line
    except Exception as e:
        print(f"Error getting system UUID: {e}")
        return None

def verify_license_and_uuid(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/1nj7HreoDhgaWAZ3bvET4h5ko6bVgo45r5hjUoqev2D4/export?format=csv"
    df = pd.read_csv(url)

    username_input = input("Enter username: ").strip().lower()
    license_input = input("Enter license number: ").strip()
    system_uuid = get_system_uuid()
    if system_uuid is None:
        print("Could not get system UUID. Exiting.")
        sys.exit()
    print(f"System UUID: {system_uuid}")

    # Columns assumed: 'User Name', 'License Number', 'Active Status', 'UUID'
    usernames = df['User Name'].astype(str).str.strip().str.lower()
    licenses = df['License Number'].astype(str).str.strip()
    active_status = df['Active Status'].astype(str).str.strip().str.lower()
    uuids = df['UUID'].astype(str).str.strip().str.upper()

    # Filter rows where username matches exactly
    user_rows = df[usernames == username_input]

    if user_rows.empty:
        print("Username not found. Exiting.")
        sys.exit()

    # Indexes of user matched rows
    idx = user_rows.index

    # Filter with exact license, active status "yes" and uuid match
    valid_rows = user_rows[
        (licenses[idx] == license_input) &
        (active_status[idx] == 'yes') &
        (uuids[idx] == system_uuid.upper())
    ]

    if not valid_rows.empty:
        print("License, active status 'Yes' and UUID verified! Proceeding...")
    else:
        print("License, active status or UUID mismatch. Exiting.")
        sys.exit()

SHEET_ID = "APNA_SHEET_ID_YAHAN_DALEN"
verify_license_and_uuid(SHEET_ID)

print("Code is now running...")
# Yahan se original scraping/logic start karo



# 🔧 Set Playwright browser path (handles .exe too)
if getattr(sys, 'frozen', False):
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(Path(sys._MEIPASS) / "ms-playwright")
else:
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(Path.home() / "AppData" / "Local" / "ms-playwright")

# Load keywords and locations
def load_list_from_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

# Get domain based on country
def get_domain_for_country(country_name, filename="Domains.xlsx"):
    df = pd.read_excel(filename)
    match = df[df['Country'].str.lower() == country_name.lower()]
    if not match.empty:
        return match.iloc[0]['Domain']
    else:
        return None

def save_to_excel_append(filename, data):
    df = pd.DataFrame(data, columns=[
        "Business Name", "Category", "Website URL"])
    try:
        if os.path.exists(filename):
            existing_df = pd.read_excel(filename)
            combined_df = pd.concat([existing_df, df]).drop_duplicates()
        else:
            combined_df = df
    except Exception as e:
        print(f"⚠️ Warning: Could not read existing Excel file '{filename}'. It may be corrupted. Overwriting. Error: {e}")
        combined_df = df

    combined_df.to_excel(filename, index=False)


INDIAN_CITIES = {
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune",
    "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam",
    "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
    "Rajkot", "Kalyan", "Vasai", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar",
    "Navi Mumbai", "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior",
    "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota", "Chandigarh", "Guwahati", "Solapur"
}

async def scrape_google_local_services(page, base_url, keyword, location):
    page_index = 0
    all_websites = []
    while True:
        url = base_url.replace("{Keyword}", urllib.parse.quote(keyword)) \
                      .replace("{Location}", urllib.parse.quote(location)) \
                      .replace("{PageIndex}", str(page_index))
        print(f"🔍 Scraping: '{keyword}' in '{location}', Page {page_index // 20 + 1}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=50000)
            await page.wait_for_selector("div[jscontroller='xkZ6Lb']", timeout=5000)
            websites = await page.evaluate(r'''() => {
                return Array.from(document.querySelectorAll("div[jscontroller='xkZ6Lb']")).map(card => {
                    let websiteUrl = card.querySelector("a[data-no-redirect='1'] div[data-website-url]")?.getAttribute("data-website-url") || "N/A";
                    if (websiteUrl === "N/A") {
                        let href = card.querySelector("a[data-no-redirect='1']")?.getAttribute("href");
                        if (href && href.startsWith("https://www.google.com/url?")) {
                            const match = href.match(/url=([^&]+)/);
                            if (match) websiteUrl = decodeURIComponent(match[1]);
                        }
                    }
                    let businessName = card.querySelector("div.rgnuSb")?.textContent?.trim() || "N/A";
                    let category = card.querySelector("span.hGz87c")?.textContent?.trim() || "N/A";
                    return {
                        "Business Name": businessName,
                        "Category": category,
                        "Website URL": websiteUrl.startsWith("http") ? new URL(websiteUrl).origin : "N/A"
                    };
                });
            }''')
            if not websites:
                print(f"⚠️ No new results on Page {page_index // 20 + 1}. Stopping.")
                break
            for site in websites:
                if site["Website URL"] != "N/A" and site.get("City", "UNKNOWN") not in INDIAN_CITIES:
                    all_websites.append(site)
            print(f"✅ Collected {len(websites)} websites from Page {page_index // 20 + 1}")
            page_index += 20
        except Exception as e:
            print(f"⚠️ Error: {e}")
            break
    return all_websites


async def main():
    country = input("🌍 Enter country to scrape data for: ").strip()
    domain = get_domain_for_country(country)

    if not domain:
        print(f"❌ Domain not found for country '{country}' in Domains.xlsx")
        return

    base_url = f"{domain}localservices/prolist?g2lbs=AIQllVx0jVIxOKIsOu84T6QkjrjvCj3gX-MFsv_gDwctn0YrJbORxlM_9M9wFIsZ-uwNT5C8CwcfiEs15XElAtXsJJdHq0dQyLpdn_MhL8zHhqCV2Nei-LVdG_MaKU5agLDTy6fZ0Pv7xEdJzPxR02oXvzg2iHxPcJg&hl=en_GB&gl=in&cs=1&ssta=1&oq=Architects&src=2&sa=X&start=400&scp=CgASABoAKgA%3D&q={{Keyword}}%20in%20{{Location}}&ved=0CAUQjdcJahcKEwjwiL31n82MAxUAAAAAHQAAAAAQAQ&slp=MgBAAVIECAIgAIgBAA%3D%3D&lci={{PageIndex}}"

    keywords = load_list_from_file("Keywords.txt")
    locations = load_list_from_file("Locations.txt")
    output_file = "Google Maps Data.xlsx"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0"
        })

        for location in locations:
            print(f"\n🏙️ Processing city: {location}")
            for sn, keyword in enumerate(keywords, start=1):
                print(f"\n🔢 SN {sn} - Keyword: {keyword}")
                results = await scrape_google_local_services(page, base_url, keyword, location)
                if results:
                    save_to_excel_append(output_file, results)

        await browser.close()
        print(f"\n✅ Done! Data saved to '{output_file}'")

# Run it
asyncio.run(main())
