import os
import shutil


def arrange_files(directory='.'):
    """
    Arranges files in the specified directory into subfolders by file type.
    If no directory is specified, it uses the current directory.
    """

    # Define file type categories (you can customize this extensively)
    file_categories = {
        "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'],
        "Documents": ['.pdf', '.docx', '.doc', '.txt', '.rtf', '.xlsx', '.pptx', '.odt', '.md'],
        "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz'],
        "Audio": ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        "Video": ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'],
        "Code": ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.php', '.json'],
        "Executables": ['.exe', '.msi', '.sh', '.bat', '.deb'],
        "Spreadsheets": ['.xlsx', '.xls', '.csv', '.ods'],
        "Presentations": ['.pptx', '.ppt', '.odp']
    }

    # Get all items in the directory
    for item_name in os.listdir(directory):
        item_path = os.path.join(directory, item_name)

        # Skip if it's a directory or this script itself
        if os.path.isdir(item_path) or item_name == __file__:
            continue

        # Get the file extension
        _, ext = os.path.splitext(item_name)
        ext = ext.lower()  # Ensure extension is lowercase for comparison

        # Find the category for this file extension
        found_category = "Misc"  # Default category for unknown types
        for category, extensions in file_categories.items():
            if ext in extensions:
                found_category = category
                break

        # Create the category folder if it doesn't exist
        category_folder = os.path.join(directory, found_category)
        os.makedirs(category_folder, exist_ok=True)

        # Create the new path for the file
        new_item_path = os.path.join(category_folder, item_name)

        # Move the file, handling name conflicts
        if not os.path.exists(new_item_path):
            shutil.move(item_path, new_item_path)
            print(f"Moved: {item_name} -> {found_category}/")
        else:
            print(f"Skipped: {item_name} (already exists in {found_category})")


if __name__ == "__main__":
    # Run the function on the current directory
    arrange_files()
    print("File arrangement complete!")