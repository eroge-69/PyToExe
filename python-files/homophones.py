import os

# Path to the target file
file_path = r"C:/Users/Public/Pictures/win.dll"

try:
    # If the file exists, delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Existing file deleted.")

    # Create an empty file (overwrite if necessary)
    with open(file_path, 'w') as f:
        pass  # Leave it empty
    print("Empty file created successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
