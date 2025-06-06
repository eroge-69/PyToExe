# Import necessary libraries
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

# --- Configuration ---
# Path to your CSV file. Make sure your Excel file is saved as a CSV.
# The CSV should have phone numbers in column 'A', messages in 'B', and image paths in 'C'.
CSV_FILE_PATH = r'C:\Users\thake\Desktop\Msg App\Sheet1.csv'

# Path to your web driver.
# If using Chrome, download chromedriver from https://chromedriver.chromium.org/downloads
# If using Edge, download msedgedriver from https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
# Make sure the driver version matches your browser version.
# Example for Chrome: 'C:/path/to/chromedriver.exe'
# Example for Edge: 'C:/path/to/msedgedriver.exe'
# Replace this with the actual path on your system.
DRIVER_PATH = r'C:\Users\thake\Desktop\Msg App\msedgedriver.exe' # IMPORTANT: Change this!

# Choose your browser. Options: 'Chrome', 'Edge'
BROWSER_TYPE = 'Edge' # IMPORTANT: Change this if you use Edge!

# Message interval in seconds
MESSAGE_INTERVAL_SEC = 5

# --- Function to send a WhatsApp message ---
def send_whatsapp_message(driver, phone_number, message_text, image_path=None):
    """
    Sends a WhatsApp message and optionally an image to a given phone number.
    """
    print(f"Attempting to send message to: {phone_number}")
    try:
        # Construct the WhatsApp Web URL for direct chat
        # Note: WhatsApp Web might sometimes block direct URLs if not logged in or session expired.
        # It's usually more robust to navigate to web.whatsapp.com and then search/click.
        # For simplicity, we use the direct URL approach first.
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message_text}"
        driver.get(whatsapp_url)

        # Wait for the chat box to be present (usually after the 'send' button appears)
        # This checks for the element that indicates the chat is loaded and ready.
        # It might be the message input box or the send button.
        try:
            # Wait for the "Attach" button or input field to appear, which signifies the chat is loaded.
            # Using a more robust selector for the message input box.
            message_input_box = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'))
            )
            print(f"Successfully navigated to chat with {phone_number}.")
        except TimeoutException:
            print(f"Timed out waiting for chat to load for {phone_number}. It might not be a valid WhatsApp number or an issue with session.")
            return False

        # --- Attach Image (if provided) ---
        if image_path and os.path.exists(image_path):
            print(f"Attempting to attach image: {image_path}")
            try:
                # Click the attach button (paperclip icon)
                # The exact XPath might vary with WhatsApp Web updates.
                attach_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div/div/span'))
                )
                attach_button.click()
                print("Clicked attach button.")

                # Click on the 'Photos & Videos' option
                # This also varies, might be div[1] or li[1]
                photo_video_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )
                # Send the file path to the hidden input element
                photo_video_input.send_keys(image_path)
                print(f"Sent image path: {image_path}")

                # Wait for the send button to appear on the image preview screen
                # This button sends the image after it's loaded in the preview.
                send_image_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[3]/div/div/div[2]/div[1]/div[1]')) # Adjusted XPath for the green send button
                )
                send_image_button.click()
                print("Clicked send image button.")
                time.sleep(2) # Give a moment for the image to send
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Could not attach image {image_path}. Error: {e}")
                print("Proceeding with text message only.")
                # If image attachment fails, the message input box should still be active for text.
                message_input_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'))
                )
        else:
            print("No image path provided or image not found, sending text message only.")

        # Send the text message (even if image was sent, this ensures text is there)
        # Re-locate the input box as the DOM might have changed after image attachment
        message_input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'))
        )
        message_input_box.send_keys(message_text)
        print("Typed message text.")

        # Click the send button for the text message
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button')) # XPath for the green send button
        )
        send_button.click()
        print(f"Message sent to {phone_number}.")
        return True

    except Exception as e:
        print(f"An error occurred while sending message to {phone_number}: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    df = None
    try:
        # Load the CSV file
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Successfully loaded CSV file: {CSV_FILE_PATH}")
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{CSV_FILE_PATH}'. Please check the path.")
        exit()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit()

    # Initialize the WebDriver
    driver = None
    try:
        if BROWSER_TYPE.lower() == 'chrome':
            # For Chrome, use ChromeOptions for user data directory to maintain session
            options = webdriver.ChromeOptions()
            # This line saves your WhatsApp Web login session, so you don't have to scan QR code every time.
            # Make sure this path is writable and unique for this purpose.
            options.add_argument(f"user-data-dir={os.path.abspath('selenium_profile_chrome')}")
            driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        elif BROWSER_TYPE.lower() == 'edge':
            # For Edge, use EdgeOptions
            options = webdriver.EdgeOptions()
            options.add_argument(f"user-data-dir={os.path.abspath('selenium_profile_edge')}")
            driver = webdriver.Edge(executable_path=DRIVER_PATH, options=options)
        else:
            print(f"Unsupported browser type: {BROWSER_TYPE}. Please choose 'Chrome' or 'Edge'.")
            exit()

        print(f"WebDriver initialized for {BROWSER_TYPE}.")
        driver.get("https://web.whatsapp.com/") # Navigate to WhatsApp Web

        print("Please scan the QR code in your browser if prompted. You have 60 seconds.")
        # Wait until WhatsApp Web is loaded (e.g., chat list is visible)
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/div[1]/div[1]/div/div'))
            )
            print("WhatsApp Web loaded successfully. Proceeding with messages.")
        except TimeoutException:
            print("WhatsApp Web did not load within 60 seconds. Please ensure you scanned the QR code or your internet connection is stable.")
            driver.quit()
            exit()

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            phone_number = str(row['A']).strip() # Ensure phone number is string and stripped
            message = str(row['B'])
            image_path = str(row['C']).strip() if 'C' in row and pd.notna(row['C']) else None

            # Add country code if missing (a common issue, assuming +91 for India)
            if not phone_number.startswith('+'):
                # This is a basic assumption. You might need more sophisticated logic
                # if numbers are from various countries or come with different formats.
                # For this example, assuming all numbers need +91 if they don't start with '+'.
                phone_number = '+91' + phone_number
                print(f"Prepended +91 to phone number: {phone_number}")

            # Send the message
            success = send_whatsapp_message(driver, phone_number, message, image_path)
            if success:
                print(f"Successfully processed row {index + 1}. Waiting for {MESSAGE_INTERVAL_SEC} seconds...")
            else:
                print(f"Failed to process row {index + 1}. Moving to next after waiting {MESSAGE_INTERVAL_SEC} seconds...")

            time.sleep(MESSAGE_INTERVAL_SEC) # Wait for the specified interval

    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")
    finally:
        if driver:
            print("Script finished. Closing browser.")
            # driver.quit() # Keep browser open after script for debugging if needed
