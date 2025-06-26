from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import zipfile
import os
import logging

# Configure logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.FileHandler(os.path.join("E:\\logs","bios.log")),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)


def unzip_file(zip_file_path, extract_to_path):
    # Ensure the extraction directory exists
    os.makedirs(extract_to_path, exist_ok=True)

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Extract all files to the specified directory
        zip_ref.extractall(extract_to_path)
        logging.info(f"Extracted all files to: {extract_to_path}")



def download_asus_bios(model: str, current_version: int, download_path: str):
    
    # Set up the WebDriver (e.g., ChromeDriver)
    options = webdriver.ChromeOptions()
    chrome_driver_path = "E:/chromedriver/chromedriver.exe"  # Adjust the path to your ChromeDriver
    #options.add_argument("--headless")  # Run in headless mode if you don't need
    prefs = {"download.default_directory": download_path}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=chrome_driver_path,options=options)

    # Navigate to the ASUS support website
    driver.get("https://www.asus.com/supportonly/"+model.lower()+"/helpdesk_bios/")
    driver.maximize_window()
    # Search for the model

    # Find all div elements with a class name that includes "roductSupportDriverBIOS__fileInfo"
    div_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='ProductSupportDriverBIOS__contentLeft'] div")
   
    for div in div_elements:
 
        # Check if the div element contains the text "BIOS for ASUS EZ Flash Utility"
        
        if "BIOS for ASUS EZ Flash Utility" in div.text:
            logging.info(f"Locating the wording")
            next_div = div.find_elements(By.XPATH, "following-sibling::div/div")
            for div2_ in next_div:
                # Check if the div2_ element contains the text "Version"
                if "Version" in div2_.text:
                    version = div2_.text.replace("Version", "").strip()
                    
                    #If the version is greater than the current version, print it
                    if int(version) > current_version:
                        logging.info(f"New BIOS version available: {version}")

                        ## Find the download link
                        download_link =  div.find_element(By.XPATH, "../../div[contains(@class,'ProductSupportDriverBIOS__contentRight')]/div[contains(@class,'ProductSupportDriverBIOS__downloadBtn__')]")
                        logging.info(f"Downloading BIOS of Model:{model} with version {version}...")
                        driver.execute_script("arguments[0].scrollIntoView();", download_link)
                        download_link.click()
                        time.sleep(7)  # Wait for the download to start
            
                         # Unzip the downloaded file
                        
                        downloaded_zip = os.path.join(download_path, model.upper()+"AS"+version+".zip")  # Replace with the actual file name
                        logging.info(f"unzip file: {downloaded_zip}")
                        unzip_file(downloaded_zip, download_path)
                        logging.info("BIOS downloaded and unzipped successfully.")
                        # Remove the original zip file
                        if os.path.exists(downloaded_zip):
                            os.remove(downloaded_zip)
                            logging.info(f"Removed original zip file: {downloaded_zip}")
                    else:
                        logging.info(f"No new BIOS version available. Current version: {current_version}, Latest version: {version}")

    # Close the browser
    driver.quit()
    logging.info("Browser closed.")


m = input("Enter the model name (e.g., gx650py): ")
current_version = int(input("Enter the current BIOS version (e.g., 314): "))
download_path = input("Enter the download path (e.g., E:\\): " ,default="E:\\")  # Default download path if not provided
download_asus_bios(model=m, current_version=current_version, download_path=download_path)
