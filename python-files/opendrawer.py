import os
from datetime import datetime

# Define the file name
file_name = "log.txt"

# Check if the file exists
if not os.path.exists(file_name):
    # Create the file if it doesn't exist
    with open(file_name, 'w') as file:
        file.write("Log File Created\n")
        print(f"{file_name} created.")
else:
    # Append the current date and time to the file if it exists
    with open(file_name, 'a') as file:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{current_time}\n")
        print(f"Appended current date and time to {file_name}.")
