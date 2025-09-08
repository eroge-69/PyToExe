import os
import glob
import subprocess
import time

# Ask user how many seconds to wait
try:
    delay = int(input("Enter delay time between requests (in seconds): "))
except ValueError:
    print("Invalid input, using default = 2 seconds.")
    delay = 2

# Current working directory
current_dir = os.getcwd()

# Find all .curl files in the folder
curl_files = sorted(glob.glob(os.path.join(current_dir, "*.curl")))

for curl_file in curl_files:
    print(f"Running: {curl_file}")

    # Read the curl command from the file
    with open(curl_file, "r", encoding="utf-8") as f:
        curl_command = f.read().strip()

    try:
        # Execute the curl command
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)

        # Print output and errors
        print("Output:")
        print(result.stdout)
        print("Error:")
        print(result.stderr)

    except Exception as e:
        print(f"Error: {e}")

    # Wait user-defined seconds before the next file
    print(f"Waiting {delay} seconds...\n")
    time.sleep(delay)
