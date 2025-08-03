# qr_logger.py
import requests

print("System is running... waiting for QR input (type manually to test)")

while True:
    try:
        qr = input("QR Input: ").strip()
        if not qr:
            continue

        payload = {"qr": qr}
        response = requests.post(
            "https://raneemapi.app.n8n.cloud/webhook-test/c9e1dc06-f993-48a2-a429-a7f6bfd24bd9",
            json=payload
        )

        if response.status_code == 200:
            print("Data sent successfully to n8n.")
        else:
            print(f"Failed to send. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
