import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

#Download Path
download_directory = 'I:\MIF\Restricted\oracle_data_imports\Apprenticeship_Standards\To_Import'

# Clear download directory
file_list = os.listdir(download_directory)
for file_name in file_list:
    file_path = os.path.join(download_directory, file_name)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error: {e}")

#EdgeOptions with download directory preference
edge_options = webdriver.EdgeOptions()
edge_options.add_argument("--headless") 
prefs = {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
edge_options.add_experimental_option("prefs", prefs)

# Launch Edge with EdgeOptions
driver = webdriver.Edge(options=edge_options)
driver.get('https://skillsengland.education.gov.uk/apprenticeships/')

btn1 = driver.find_element(
    By.XPATH,
    "/html/body/div[1]/div[2]/div/div/div[2]/button[1]/span"
)
time.sleep(4)
#click cookies button
btn1.click()

btn = driver.find_element(
    By.XPATH,
    "/html/body/main/div/div/div/div[2]/div/div[2]/div[2]/div[2]/a"
)
time.sleep(5)
#click download button
btn.click() 
time.sleep(10)
driver.quit()
#driver.close()
