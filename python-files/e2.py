

import requests
import cv2
import time
from pyzbar.pyzbar import decode


def get_user_input():

    subdomain = input("Please enter your subdomain: ")
    token = input("Please enter your API token: ")
    return subdomain, token



def send_to_api(subdomain, token, serial_number):

    try:

        api_url = f"https://{subdomain}.elitetalab.online"
        station_value = "POS-1"

        payload = {
            "serial_number": serial_number,
            "station": station_value
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print("Data successfully sent to the API.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error sending data to the API: {e}")
        return False



def scan_and_process_barcodes():

    subdomain, token = get_user_input()
    print("Program is running in the background. Scan a barcode now.")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open video device. Check camera index or connection.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Failed to grab frame from camera. Exiting.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow('Barcode Scanner', gray)

        barcodes = decode(gray)

        if barcodes:
            for barcode in barcodes:
                serial_number = barcode.data.decode('utf-8')
                print(f"Barcode detected. Serial Number: {serial_number}")

                print(f"Barcode Type: {barcode.type}")

                success = send_to_api(subdomain, token, serial_number)
                if success:
                    time.sleep(2)
                else:
                    time.sleep(5)

                break

        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_and_process_barcodes()