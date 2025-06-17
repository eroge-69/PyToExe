import os
import time
import pandas as pd
import subprocess
import keyboard
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tkinter import Tk, filedialog, messagebox, simpledialog
import random

# === STEP 1: SELECT EXCEL OR CSV FILE ===
def select_excel_file():
    root = Tk()
    root.withdraw()

    # Get current user's desktop path
    try:
        username = os.getlogin()
    except Exception:
        import getpass
        username = getpass.getuser()
    desktop_path = os.path.join("C:\\Users", username, "Desktop")

    file_path = filedialog.askopenfilename(
        title="📄 Select Excel or CSV File",
        initialdir=desktop_path,
        filetypes=[("Excel or CSV files", "*.xlsx *.xls *.csv")]
    )

    if not file_path:
        print("❌ No file selected. Exiting.")
        exit()
    return file_path

# === STEP 2: SELECT EXCEL SHEET NAME ===
def select_excel_sheet(file_path):
    try:
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        root = Tk()
        root.withdraw()
        sheet_name = simpledialog.askstring(
            "Select Sheet",
            f"Enter the sheet name from {sheet_names}:",
            parent=root
        )
        root.destroy()
        if not sheet_name or sheet_name not in sheet_names:
            print(f"❌ Invalid or no sheet selected. Available sheets: {sheet_names}. Exiting.")
            exit()
        return sheet_name
    except Exception as e:
        print(f"❌ Error reading Excel sheets: {e}. Exiting.")
        exit()

# === STEP 3: CONNECT TO CHROME ===
def connect_to_chrome(port=9222):
    options = Options()
    options.debugger_address = f"localhost:{port}"
    driver = webdriver.Chrome(options=options)
    return driver

# === STEP 4: FILL FORM FIELDS ===
def fill_fields(driver, df, field_map):
    tabs = driver.window_handles
    rows_to_fill = min(len(tabs), len(df))

    print(f"\n🧩 Filling {rows_to_fill} tab(s)...")

    for i in range(rows_to_fill):
        row = df.iloc[i]
        driver.switch_to.window(tabs[i])
        print(f"\n➡️ Processing tab {i + 1} with data: {row.to_dict()}")

        # Fill form fields
        for column, field_id in field_map.items():
            if column not in row:
                continue
            value = str(row[column]).replace('.0', '') if pd.notna(row[column]) else ''
            if column == 'state_province_name' and value.strip() == '':
                continue

            try:
                driver.execute_script(f"document.getElementById('{field_id}').value = '';")
                driver.execute_script(f"document.getElementById('{field_id}').value = arguments[0];", value)
            except Exception as e:
                print(f"⚠️ Error updating field '{field_id}': {e}")

        # Set cursor focus to srch_id field (ql2id1 column)
        try:
            srch_id_field = driver.find_element(By.ID, 'srch_id')
            srch_id_field.click()  # Ensure the field is focused
            srch_id_field.send_keys(Keys.NULL)  # Clear any residual keypress
        except Exception as e:
            print(f"⚠️ Error setting focus to 'srch_id': {e}")
            continue

        # Simulate pressing Tab twice, then Enter
        try:
            srch_id_field.send_keys(Keys.TAB)  # First Tab
            time.sleep(0.1)  # Brief pause to ensure tab action registers
            driver.switch_to.active_element.send_keys(Keys.TAB)  # Second Tab
            time.sleep(0.1)  # Brief pause
            driver.switch_to.active_element.send_keys(Keys.ENTER)  # Press Enter
            print(f"✅ Tab x2 and Enter pressed for tab {i + 1}")
        except Exception as e:
            print(f"❌ Error performing Tab x2 and Enter in tab {i + 1}: {e}")

        # Wait briefly to ensure action completes
        time.sleep(0.5)

    print("\n✅ Done processing all tabs!")

# === MAIN ===
def main():
    print("🔧 Chrome Auto Form Filler")

    # Step 1: Select Excel/CSV
    file_path = select_excel_file()
    ext = file_path.lower()

    # Step 2: Load data
    if ext.endswith(".csv"):
        df = pd.read_csv(file_path, dtype={"ql2id": str})
    else:
        # Prompt for sheet name
        sheet_name = select_excel_sheet(file_path)
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if 'ql2id' in df.columns:
            df['ql2id'] = df['ql2id'].astype(str).str.replace(r'\.0$', '', regex=True)

    # Clean up optional columns
    if 'state_province_name' in df.columns:
        df['state_province_name'] = df['state_province_name'].fillna('').astype(str)

    # Step 3: Wait for hotkey
    print("🕹️ Waiting for Ctrl+Shift+F to begin autofill...")

    keyboard.wait('ctrl+shift+f')
    print("\n⌨️ Hotkey detected. Connecting to Chrome...")

    # Step 4: Connect to Chrome
    driver = connect_to_chrome(port=9222)

    # === FIELD MAPPING: Excel/CSV column → Form field ID ===
    field_map = {
        "ql2id1": "srch_id",  # Use ql2id1 for srch_id
        "ql2id": "lnk_ql2id",  # Use ql2id for lnk_ql2id
        "expedia_id": "lnk_prpid"
    }

    # Step 5: Fill tabs automatically
    fill_fields(driver, df, field_map)

    # Close the driver after completion
    driver.quit()

if __name__ == "__main__":
    main()