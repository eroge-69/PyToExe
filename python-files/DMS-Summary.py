from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")

# Initialize Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open your SharePoint-hosted Power BI dashboard
driver.get("https://blueenergymotors.sharepoint.com/SitePages/DMS-Summary.aspx")

print("Dashboard opened. Close the window manually when done.")
input("Press Enter here to close the browser...")  # Keeps the script alive

# Close the browser only after manual input
driver.quit()
