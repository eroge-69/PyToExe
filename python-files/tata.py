import os
import shutil

def intelligent_organizer(folder_path):
    """
    Organizes files in a specific directory by creating folders based on file extensions.

    Args:
        folder_path (str): The absolute path of the folder to be organized.
    """
    print(f"\nProcessing directory: {folder_path}")
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory. Skipping.")
        return

    # A dictionary to map file extensions to folder names
    file_type_mapping = {
        # Images
        '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images',
        '.gif': 'Images', '.bmp': 'Images', '.tiff': 'Images',
        '.webp': 'Images', '.svg': 'Images',

        # Videos
        '.mp4': 'Videos', '.avi': 'Videos', '.mov': 'Videos',
        '.mkv': 'Videos', '.flv': 'Videos', '.wmv': 'Videos',

        # Audio
        '.mp3': 'Audio', '.wav': 'Audio', '.ogg': 'Audio',
        '.flac': 'Audio', '.aac': 'Audio',

        # Documents
        '.pdf': 'PDFs', '.docx': 'Documents', '.doc': 'Documents',
        '.txt': 'Text Files', '.pptx': 'Presentations', '.xlsx': 'Spreadsheets',
        '.csv': 'CSVs',

        # Archives
        '.zip': 'Archives', '.rar': 'Archives', '.tar': 'Archives',
        '.gz': 'Archives',

        # Executables and Installers
        '.exe': 'Executables', '.msi': 'Installers',

        # Other
        '.iso': 'Disk Images',
        # You can add more file types and their corresponding folder names here
    }

    # Iterate over all the files in the given directory
    for filename in os.listdir(folder_path):
        source_path = os.path.join(folder_path, filename)

        # Skip if it's a directory to avoid moving our newly created folders
        if os.path.isdir(source_path):
            continue

        # Get the file extension
        file_extension = os.path.splitext(filename)[1].lower()

        # If the file has no extension, skip it
        if not file_extension:
            continue

        # Determine the destination folder name, defaulting to 'Other'
        destination_folder_name = file_type_mapping.get(file_extension, 'Other')
        destination_folder_path = os.path.join(folder_path, destination_folder_name)

        # Create the destination folder if it doesn't already exist
        if not os.path.exists(destination_folder_path):
            try:
                os.makedirs(destination_folder_path)
                print(f"  Created directory: {destination_folder_path}")
            except OSError as e:
                print(f"  Error creating directory {destination_folder_path}: {e}")
                continue # Skip to the next file if directory creation fails

        # Move the file
        try:
            shutil.move(source_path, destination_folder_path)
            print(f"  Moved '{filename}' to '{destination_folder_name}'")
        except shutil.Error as e:
            # This error often means a file with the same name already exists
            print(f"  Could not move '{filename}': {e}")
        except Exception as e:
            print(f"  An unexpected error occurred with '{filename}': {e}")


if __name__ == "__main__":
    directories_to_organize = []
    while True:
        # Ask for a directory path
        path = input("Please enter a directory path to organize (or press Enter to finish): ")

        # If the user just presses Enter, break the loop
        if not path:
            break

        # Add the path to our list
        directories_to_organize.append(path)

        # Ask if they want to add another
        another = input("Do you want to add another directory? (y/n): ").lower()
        if another != 'y':
            break

    if not directories_to_organize:
        print("\nNo directories were entered. Exiting.")
    else:
        print(f"\nStarting organization for {len(directories_to_organize)} director(y/ies)...")
        # Loop through each provided directory and organize it
        for directory in directories_to_organize:
            intelligent_organizer(directory)
            
# MADE WITH LOVE BY M.A
        print("\nAll tasks are complete.")
