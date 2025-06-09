from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd
from dotenv import load_dotenv
import os
import re
import time
import requests

# Load the .env file
load_dotenv()

cp_id = "ca.3340598"
cp_pwd = "WHwqr7RHKTA3"
warehouse_id = os.getenv("WAREHOUSE_ID")
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxcnemlqfpUrOD597xj-hlzxBk48VhDLRaSfpewfVc9KgISG19xnbG1Nb7B1p4qyjOzXw/exec"
SHEET_ID = "1vfeIRGcOFA15zVvBW-xFnvStnJsU6wn2jr3uLUhPfVU"
DESTINATION_FOLDER = r"C:\Users\anushka.thakur2\Desktop\DF"
RESULT_SHEET_NAME = "Import Data From Py"

def setup_browser():
    """Set up the Playwright browser instance and log in."""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        accept_downloads=True,
        viewport={'width': 1366, 'height': 768}
    )
    page = context.new_page()
    page.goto("http://10.24.1.53/")

    # Login
    page.fill("xpath=/html/body/div[2]/div[2]/div/div/form/div/div[4]/input[1]", cp_id)
    page.fill("xpath=/html/body/div[2]/div[2]/div/div/form/div/div[4]/input[2]", cp_pwd)
    page.click("xpath=/html/body/div[2]/div[2]/div/div/form/div/div[4]/div[4]/button/span")
    page.wait_for_timeout(3000)

    # Select warehouse
    page.select_option("xpath=/html/body/div[3]/div[1]/div[2]/div[1]/div/div[2]/select", label="Anjaneya_Hyperlocal_01")
    return playwright, browser, context, page

def TL_Report():
    """Retrieve the TL report from a public Google Sheet."""
    sheet_id = SHEET_ID
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    try:
        df = pd.read_csv(csv_url)
        print("Loaded TL Report:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error reading Google Sheet: {e}")
        return None

def Tl_Details_down(context, page, TL_Ids):
    """Download details for each TL ID and extract WID, Shelf, Floor_No, Qty."""
    extracted_data = []

    for TL_Id in TL_Ids:
        try:
            TL_Id = str(TL_Id).strip()
            url = f"http://10.24.1.53/transfer_list/{TL_Id}"
            print(f"Navigating to: {url}")
            page.goto(url)
            page.wait_for_selector("table")

            rows = page.locator("//table/tbody/tr")
            row_count = rows.count()

            for i in range(row_count):
                try:
                    row = rows.nth(i)
                    cells = row.locator("td")
                    text_list = [cells.nth(j).inner_text().strip() for j in range(cells.count())]

                    # Skip rows with too few cells
                    if len(text_list) < 5:
                        continue

                    row_text = " ".join(text_list)
                    wid_match = re.search(r"WID:\s*(\S+)", row_text)
                    shelf_match = re.search(r"Shelf:\s*([^\n]+)", row_text)
                    floor_match = re.search(r"Floor_No:\s*(\d+)", row_text)
                    fsn_match = re.search(r"FSN:\s*(\S+)", row_text)

                    wid = wid_match.group(1) if wid_match else None
                    shelf = shelf_match.group(1) if shelf_match else None
                    floor = floor_match.group(1) if floor_match else None
                    fsn = fsn_match.group(1) if fsn_match else None
                    qty = text_list[2] if len(text_list) > 2 else None
                    

                    # Only append complete rows
                    if wid and shelf and floor and qty:
                        extracted_data.append({
                            "TL_Id": TL_Id,
                            "WID": wid,
                            "Shelf": shelf,
                            "Qty": qty,
                            "Floor_No": floor,
                            "FSN" : fsn
                        })

                except Exception as row_e:
                    print(f"Error processing row: {row_e}")

            page.wait_for_timeout(1000)

        except Exception as e:
            print(f"Error processing TL_ID {TL_Id}: {e}")

    # Convert list of dicts to DataFrame
    df_result = pd.DataFrame(extracted_data)
    print("Final Extracted Data:")
    print(df_result)

    return df_result


def write_results_to_sheet_via_webapp(results):
    """Write results back to Google Sheet using Google Apps Script Web App."""
    
    try:
        if not results:
            print("No results to write to Google Sheet.")
            return False
            
        # Create list of dictionaries from results
        data_to_send = results
            
        # Save a local backup first
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_csv_path = os.path.join(DESTINATION_FOLDER, f"STN_Data_Backup_{timestamp}.csv")
        os.makedirs(DESTINATION_FOLDER, exist_ok=True)
        pd.DataFrame(data_to_send).to_csv(output_csv_path, index=False)
        
        # Prepare payload
        payload = {
            "spreadsheetId": SHEET_ID,
            "sheetName": RESULT_SHEET_NAME,
            "data": data_to_send
        }
        
        print("Sending data to Google Apps Script Web App...")
        print(f"URL: {WEB_APP_URL}")
        print(f"Payload size: {len(data_to_send)} records")
        
        # Send data to Google Apps Script Web App with timeout
        response = requests.post(
            WEB_APP_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        # Check response
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("success"):
                    print(f"Results written to Google Sheet '{RESULT_SHEET_NAME}' successfully.")
                    return True
                else:
                    print(f"Error from Web App: {result.get('error', 'Unknown error')}")
            except ValueError:
                print(f"Could not parse JSON response: {response.text}")
        else:
            print(f"HTTP error: {response.status_code} - {response.text}")
            
        return False
        
    except Exception as e:
        print(f"Failed to write results to Google Sheet via Web App: {e}")
        return False

if __name__ == "__main__":
    playwright, browser, context, page = setup_browser()

    try:
        df = TL_Report()
        if df is not None and "TL_Id" in df.columns:
            TL_Ids = df["TL_Id"].dropna().unique()
            results = Tl_Details_down(context, page, TL_Ids)
            
            if not results.empty:
                success = write_results_to_sheet_via_webapp(results.to_dict(orient="records"))
                if success:
                    print("Data successfully sent to Google Sheets!")
                else:
                    print("Failed to send data to Google Sheets.")
            else:
                print("No data extracted to send to Google Sheet.")
    except Exception as e:
        print(f"An error occurred in the main process: {e}")
    finally:
        browser.close()
        playwright.stop()