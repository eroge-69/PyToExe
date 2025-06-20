
import time
import requests
from openpyxl import load_workbook

def fetch_nifty_price():
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        response = session.get(url, headers=headers, timeout=10)
        data = response.json()
        return data['data'][0]['last']
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_excel_price(file_path, sheet_name='LivePrice', cell='B2'):
    try:
        wb = load_workbook(file_path)
        sheet = wb[sheet_name]
        while True:
            price = fetch_nifty_price()
            if price:
                print(f"Updating {cell} with price: {price}")
                sheet[cell] = price
                wb.save(file_path)
            else:
                print("Failed to fetch price")
            time.sleep(5)
    except Exception as e:
        print(f"Excel update failed: {e}")

# Usage
update_excel_price("Offline_NiftyBot_v1.xlsx")
