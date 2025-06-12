import requests
from bs4 import BeautifulSoup

def check_parent_resident_visa_eoi(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors

        if "24363994" in response.text: 
            print("✅ Results found on the page.")
        else:
            print("❌ No results found on the page.")
    except Exception as e:
        print(f"Error occurred: {e}")

# URL to check
url = "https://www.immigration.govt.nz/process-to-apply/once-you-have-a-visa/bringing-family-to-new-zealand/coming-to-new-zealand-on-the-parent-resident-visa/parent-resident-visa-successful-expressions-of-interest-eois/?page=1"

check_parent_resident_visa_eoi(url)