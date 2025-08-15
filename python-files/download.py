import requests
import os
import time

# Define the base URL
base_url = "https://cscservices.mahaonline.gov.in/Edistrict/Handler/GetFile.ashx"
start_serial = 2551890011253600378235
end_serial = 2551890011253600378335
output_folder = "downloads"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

for serial in range(start_serial, end_serial + 1):
    params = {
        "From": "ApplicationStatus",
        "ID": str(serial),
        "sDist": "518"
    }

    try:
        response = requests.get(base_url, params=params)
        
        # Check for valid file content
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("application"):
            filename = os.path.join(output_folder, f"{serial}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {serial}")
        else:
            print(f"Skipped (not a valid file): {serial}")
        
        # Sleep to avoid hammering the server
        time.sleep(0.5)

    except Exception as e:
        print(f"Error downloading {serial}: {e}")
