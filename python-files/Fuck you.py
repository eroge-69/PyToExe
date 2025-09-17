import os

# Choose the base path where you want the folders created
base_path = "./test_folders"

# Make sure the base path exists
os.makedirs(base_path, exist_ok=True)

# Create 50 folders
for i in range(1, 51):
    folder_name = f"fuck you {i}"
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

print("50 folders created successfully ✅")
