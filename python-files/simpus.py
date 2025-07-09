import pandas as pd
from selenium import webdriver
# Import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# Import the Keys class to simulate keyboard actions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import sys
import os

# --- Determine the base path for data files ---
# This makes the script work both when run normally and as a PyInstaller .exe
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (e.g., by PyInstaller)
    application_path = os.path.dirname(sys.executable)
else:
    # If run as a normal .py script
    application_path = os.path.dirname(os.path.abspath(__file__))

# --- Configuration ---
# IMPORTANT: Replace these placeholders with your actual information

# 1. SIMPUS Login Credentials
SIMPUS_USERNAME = 'Yani'
SIMPUS_PASSWORD = '@dinkes25'

# 2. Path to your patient data EXCEL (.xlsx) file
#    This will now automatically look for the file in the same directory as the script/.exe
EXCEL_FILE_PATH = os.path.join(application_path, 'BACKUP RME SIMPUS.xlsx')

# --- URLS ---
LOGIN_URL = 'https://simpus.depok.go.id/index.php/user/login'
PATIENT_LIST_URL = 'https://simpus.depok.go.id/index.php/bp/default/periksa'


# --- Helper Functions ---

def get_patient_data(file_path):
    """Reads patient data from the specified Excel file using pandas."""
    print(f"Attempting to read Excel file from: {file_path}")
    try:
        # Use pandas to read the Excel file, specifying the sheet name and ensuring data is read as strings
        df = pd.read_excel(file_path, sheet_name='Sheet2', dtype=str).fillna('')

        # Clean up column names (strip whitespace)
        df.columns = df.columns.str.strip()

        # Convert dataframe to a list of dictionaries
        patients = df.to_dict('records')

        # Filter out rows where the NAMA is empty
        valid_patients = [p for p in patients if p.get('NAMA')]

        print(f"Found {len(valid_patients)} total patient records in the Excel file.")
        return valid_patients

    except FileNotFoundError:
        print(f"Error: The Excel file was not found at {file_path}")
        print("Please make sure 'BACKUP RME SIMPUS.xlsx' is in the same folder as the application.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return None


def login(driver, wait):
    """Handles the login process for SIMPUS."""
    try:
        print("Navigating to login page...")
        driver.get(LOGIN_URL)
        time.sleep(2)

        print("Entering credentials...")
        wait.until(EC.visibility_of_element_located((By.ID, 'UserLogin_username'))).send_keys(SIMPUS_USERNAME)
        driver.find_element(By.ID, 'UserLogin_password').send_keys(SIMPUS_PASSWORD)

        print("Submitting login form...")
        driver.find_element(By.CLASS_NAME, 'btn-login').click()

        # Wait for a reliable element on the dashboard to confirm successful login
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'sidebar-menu')))
        print("Login successful.")
        return True
    except TimeoutException:
        print("Login failed. Timed out waiting for page elements. Check credentials or network.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")
        return False


def process_patient_cppt(driver, wait, patient):
    """Searches for a patient, navigates to CPPT form, and fills it."""
    try:
        print(f"--- Starting CPPT for patient: {patient['NAMA']} ---")
        driver.get(PATIENT_LIST_URL)

        print("Searching for patient...")
        search_box = wait.until(EC.visibility_of_element_located((By.ID, 'Nama')))
        search_box.clear()
        search_box.send_keys(patient['NAMA'])
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        print("Finding and clicking 'CPPT oleh Dokter' link with exact name match...")
        cppt_link_xpath = f"//td[normalize-space()='{str(patient['NAMA']).upper()}']/..//a[@data-title='CPPT oleh Dokter']"
        wait.until(EC.element_to_be_clickable((By.XPATH, cppt_link_xpath))).click()

        print("Filling CPPT form...")
        wait.until(EC.visibility_of_element_located((By.ID, 'Periksa_subjek'))).send_keys(patient['ANAMNESIS'])
        driver.find_element(By.ID, 'Periksa_objek').send_keys(patient['OBJEK/ PEMERIKSAAN FISIK'])
        driver.find_element(By.ID, 'Periksa_penilaian').send_keys(patient['PENILAIAN/ DIAGNOSA'])
        driver.find_element(By.ID, 'Periksa_rencana').send_keys(patient['RENCANA/ TERAPI'])
        driver.find_element(By.ID, 'Periksa_non_obat').send_keys(patient['TERAPI NON OBAT'])
        driver.find_element(By.ID, 'Periksa_instruksi').send_keys(patient['KIE'])

        print("Saving CPPT form...")
        driver.find_element(By.ID, 'save-cppt').click()
        time.sleep(3)
        print("CPPT form saved successfully.")
        return True
    except TimeoutException:
        print(f"A timeout occurred during CPPT processing for {patient['NAMA']}. Could not find an element. Skipping.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during CPPT processing for {patient['NAMA']}: {e}")
        return False


def process_patient_koding(driver, wait, patient):
    """Handles the 'Periksa Koding' and 'Satu Sehat' integration."""
    try:
        print(f"--- Starting Koding for patient: {patient['NAMA']} ---")
        driver.get(PATIENT_LIST_URL)

        print("Re-searching for patient to get to Koding...")
        search_box = wait.until(EC.visibility_of_element_located((By.ID, 'Nama')))
        search_box.clear()
        search_box.send_keys(patient['NAMA'])
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        print("Finding and clicking 'Periksa Koding' link with exact name match...")
        koding_link_xpath = f"//td[normalize-space()='{str(patient['NAMA']).upper()}']/..//a[@data-title='Periksa Koding']"
        wait.until(EC.element_to_be_clickable((By.XPATH, koding_link_xpath))).click()

        print("Switching to 'History CPPT' tab...")
        history_tab_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#tab_list_cppt']")))
        history_tab_link.click()

        try:
            print("Extracting latest ICD code from CPPT history...")
            history_table_xpath = "//div[@id='cppt-grid']//tbody/tr[1]/td[13]"
            icd_code_raw = wait.until(EC.visibility_of_element_located((By.XPATH, history_table_xpath))).text
        except TimeoutException:
            print(f"ERROR: Could not find the CPPT history grid for {patient['NAMA']}. Skipping Koding.")
            return False

        if not icd_code_raw or icd_code_raw.isspace():
            print(f"No ICD code found in the web history for {patient['NAMA']}. Skipping Koding.")
            return False

        print("Switching back to 'ICDX' tab to enter diagnosis...")
        icdx_tab_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#tab_diagnosa']")))
        icdx_tab_link.click()

        icd_codes = re.split(r'[ ,]+', icd_code_raw)
        for code in icd_codes:
            if not code: continue

            processed_code = code.strip().upper()
            print(f"Processing ICD Code: {processed_code}")

            diagnosa_input = wait.until(EC.visibility_of_element_located((By.ID, 'Diagnosa_icdx_bpjs_id')))
            diagnosa_input.clear()
            diagnosa_input.send_keys(processed_code)

            try:
                autocomplete_option_xpath = "//ul[contains(@class, 'ui-autocomplete')]/li[1]"
                first_option = wait.until(EC.visibility_of_element_located((By.XPATH, autocomplete_option_xpath)))
                print(f"Found autocomplete suggestion: {first_option.text}. Selecting it.")
                first_option.click()
            except TimeoutException:
                print("No autocomplete suggestions appeared. Proceeding with the raw code.")

            Select(driver.find_element(By.ID, 'Diagnosa_kasus')).select_by_value('lama')

            driver.find_element(By.ID, 'save-diagnosa').click()

            print("Waiting for success modal...")
            ok_button_xpath = "//div[contains(@class, 'bootbox-alert')]//button[@data-bb-handler='ok']"
            ok_button = wait.until(EC.element_to_be_clickable((By.XPATH, ok_button_xpath)))
            print("Success modal appeared. Clicking OK.")
            ok_button.click()
            time.sleep(1)

        print("Integrating with Satu Sehat...")
        Select(driver.find_element(By.ID, 'nik_dokter')).select_by_value('3276015105620006')
        Select(driver.find_element(By.ID, 'location_identifier')).select_by_value(
            '1e45a9f6-89c8-4f6a-bb9e-3f60ff589922')

        # --- KEY CHANGE HERE: Robust check for Satu Sehat submission ---
        current_url = driver.current_url
        driver.find_element(By.ID, 'integrate-satusehat').click()

        try:
            # Wait up to 10 seconds for one of the success/failure conditions
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//div[contains(@class, 'alert-info') and contains(., 'Integrasi kunjungan, diagnosa, dan icdx satu sehat berhasil')]")),
                    EC.presence_of_element_located((By.XPATH,
                                                    "//div[contains(@class, 'alert-warning') and contains(., 'Integrasi SatuSehat Gagal')]")),
                    EC.url_changes(current_url)
                )
            )

            # Now check which condition was met
            try:
                # Check for success alert
                driver.find_element(By.XPATH,
                                    "//div[contains(@class, 'alert-info') and contains(., 'Integrasi kunjungan, diagnosa, dan icdx satu sehat berhasil')]")
                print("Satu Sehat integration successful (Success message found).")
            except NoSuchElementException:
                try:
                    # Check for failure alert
                    fail_alert = driver.find_element(By.XPATH,
                                                     "//div[contains(@class, 'alert-warning') and contains(., 'Integrasi SatuSehat Gagal')]")
                    print(f"Satu Sehat integration FAILED: {fail_alert.text}")
                    return False
                except NoSuchElementException:
                    # If neither alert is found, it must have been a URL change
                    if driver.current_url != current_url:
                        print("Satu Sehat integration successful (Page redirected).")
                    else:
                        # This case is unlikely but possible if the page just reloads
                        print("Satu Sehat integration status unknown (no message or redirect).")

        except TimeoutException:
            print("Satu Sehat integration FAILED: Timed out waiting for a response after submission.")
            return False

        print("Koding and integration successful.")
        return True
    except TimeoutException:
        print(f"A timeout occurred during Koding for {patient['NAMA']}. Could not find an element. Skipping.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Koding for {patient['NAMA']}: {e}")
        return False


# --- Main Execution ---
if __name__ == "__main__":
    patient_records = get_patient_data(EXCEL_FILE_PATH)
    failed_patients = []

    if patient_records is None:
        print("Halting execution due to file reading error.")
    elif not patient_records:
        print("No valid patient records found in the Excel file.")
    else:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)

        if login(driver, wait):
            for record in patient_records:
                anamnesis_data = str(record.get('ANAMNESIS', '')).strip()

                if not anamnesis_data or 'sudah di input di simpus' in anamnesis_data.lower():
                    print(f"--- Anamnesis for {record['NAMA']} is empty or marked as complete. Skipping CPPT. ---")
                    if not process_patient_koding(driver, wait, record):
                        failed_patients.append({'name': record['NAMA'], 'reason': 'Koding/Satu Sehat Failed'})
                else:
                    if process_patient_cppt(driver, wait, record):
                        if not process_patient_koding(driver, wait, record):
                            failed_patients.append({'name': record['NAMA'], 'reason': 'Koding/Satu Sehat Failed'})
                    else:
                        failed_patients.append({'name': record['NAMA'], 'reason': 'CPPT Processing Failed'})

                print("-" * 40)
                time.sleep(2)

            print("=" * 50)
            print("AUTOMATION SCRIPT FINISHED")
            print("=" * 50)

            if failed_patients:
                print("\n--- SUMMARY OF FAILED PATIENTS ---")
                for failure in failed_patients:
                    print(f"Name: {failure['name']}, Reason: {failure['reason']}")
            else:
                print("\nAll patients were processed successfully!")

        else:
            print("Could not proceed with data entry due to login failure.")

        driver.quit()
