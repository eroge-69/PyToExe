import os

def rename_tmp_files_to_jpg(folder_path):
    """
    Renames all files with a .tmp extension in a specified folder to .jpg.

    Args:
        folder_path (str): The absolute path to the folder to process.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: The provided path '{folder_path}' is not a valid directory.")
        return

    print(f"Scanning folder: {folder_path}\n")
    renamed_count = 0
    try:
        # Loop through all files and subdirectories in the given path.
        for filename in os.listdir(folder_path):
            # Check if the file is a regular file and ends with '.tmp'.
            if os.path.isfile(os.path.join(folder_path, filename)) and filename.endswith('.tmp'):
                # Construct the old and new file paths.
                old_filepath = os.path.join(folder_path, filename)
                new_filename = os.path.splitext(filename)[0] + '.jpg'
                new_filepath = os.path.join(folder_path, new_filename)

                # Rename the file.
                os.rename(old_filepath, new_filepath)
                print(f"Renamed: '{filename}' -> '{new_filename}'")
                renamed_count += 1

        if renamed_count > 0:
            print(f"\nCompleted! Renamed {renamed_count} files.")
        else:
            print("No .tmp files found in the specified folder.")

    except PermissionError:
        print(f"\nError: Permission denied. Please run the script as an administrator or check your folder permissions.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    # Prompt the user for the folder path.
    # Note: On Windows, you may need to use double backslashes (e.g., C:\\Users\\YourName\\Desktop).
    # On macOS/Linux, it will be a single forward slash (e.g., /Users/YourName/Desktop).
    user_path = input("Enter the full path of the folder you want to process: ")
    rename_tmp_files_to_jpg(user_path)
