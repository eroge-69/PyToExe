import webbrowser
import subprocess
import time

def open_browsers():
    # Define URLs for the tabs
    tab1_url = "https://www.google.com"
    tab2_url = "https://www.x.com"

    try:
        # Open Opera browser
        opera_path = r"C:\Program Files\Opera\opera.exe"  # Adjust path if needed
        subprocess.Popen([opera_path, tab1_url, tab2_url])
        
        # Small delay to prevent simultaneous launch issues
        time.sleep(2)
        
        # Open Chrome browser
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Adjust path if needed
        subprocess.Popen([chrome_path, tab1_url, tab2_url])
        
        print("Both browsers opened successfully with two tabs each!")
        
    except FileNotFoundError as e:
        print(f"Error: Browser not found. Please check the browser paths. {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    open_browsers()