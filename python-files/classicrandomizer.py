import os
import random

# CONFIGURATION
source_dir = 'source_files'        # Folder containing random text files
destination_file = 'destination.txt'  # Constant file to be overwritten

# Step 1: Get list of .txt files in source directory
text_files = [f for f in os.listdir(source_dir) if f.endswith('.txt')]

# Step 2: Choose one at random
if not text_files:
    print("No text files found in the source directory.")
else:
    random_file = random.choice(text_files)
    random_file_path = os.path.join(source_dir, random_file)

    # Step 3: Read content from random file
    with open(random_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Step 4: Write content to the destination file
    with open(destination_file, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"Copied content from '{random_file}' to '{destination_file}'.")
