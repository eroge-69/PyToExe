import os
import random
from datetime import datetime

# --- Configuration ---
# Set to True to see detailed diagnostic messages in the console (useful for debugging).
# Set to False to run silently for most background operations.
DEBUG_MODE = False
# --- End Configuration ---

# ANSI escape codes for text colors and styles
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _print_debug(message):
    """Helper function to print messages only if DEBUG_MODE is True."""
    if DEBUG_MODE:
        print(message)

def create_folders():
    """
    Creates the 'Combo', 'Wordlist', 'ErrorWords', and 'RawdataNames' folders
    if they don't already exist.
    Displays messages indicating which folders were created (in bold red) or
    if they already exist (in green).
    """
    folders_to_create = ["Combo", "Wordlist", "ErrorWords", "RawdataNames"]
    created_folders = []
    existing_folders = []

    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder)
            created_folders.append(folder)
        else:
            existing_folders.append(folder)

    if created_folders:
        print(f"The following folders were created: {BOLD}{RED}{', '.join(created_folders)}{RESET}")
    if existing_folders:
        print(f"The following folders already exist: {BOLD}{GREEN}{', '.join(existing_folders)}{RESET}")

def find_random_combo_generator_directory():
    """
    Attempts to locate the 'RandomComboGenerator' directory.
    Checks common relative paths. If none, prompts the user for the path.
    """
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    current_working_directory = os.getcwd()

    _print_debug(f"\n--- Locating 'RandomComboGenerator' ---")
    _print_debug(f"Script's full path: {script_path}")
    _print_debug(f"Script's directory: {script_directory}")
    _print_debug(f"Current Working Directory (where you ran 'python' from): {current_working_directory}")

    possible_paths = []

    # Check 1: Is CWD 'RandomComboGenerator'?
    if os.path.basename(current_working_directory).lower() == "randomcombogenerator":
        possible_paths.append(current_working_directory)
        _print_debug(f"  Candidate: CWD is 'RandomComboGenerator': {current_working_directory}")
    # Check 2: Is script's immediate directory 'RandomComboGenerator'?
    if os.path.basename(script_directory).lower() == "randomcombogenerator":
        possible_paths.append(script_directory)
        _print_debug(f"  Candidate: Script's directory is 'RandomComboGenerator': {script_directory}")
    # Check 3: Is script's parent directory 'RandomComboGenerator'?
    parent_of_script_directory = os.path.dirname(script_directory)
    if os.path.basename(parent_of_script_directory).lower() == "randomcombogenerator":
        possible_paths.append(parent_of_script_directory)
        _print_debug(f"  Candidate: Script's parent directory is 'RandomComboGenerator': {parent_of_script_directory}")
    # Check 4: Is 'RandomComboGenerator' a sibling to the script's directory?
    sibling_path = os.path.join(parent_of_script_directory, "RandomComboGenerator")
    if os.path.isdir(sibling_path):
        possible_paths.append(sibling_path)
        _print_debug(f"  Candidate: 'RandomComboGenerator' is a sibling of script's directory: {sibling_path}")
    # Check 5: Is 'RandomComboGenerator' a child of the current working directory?
    child_of_cwd_path = os.path.join(current_working_directory, "RandomComboGenerator")
    if os.path.isdir(child_of_cwd_path):
        possible_paths.append(child_of_cwd_path)
        _print_debug(f"  Candidate: 'RandomComboGenerator' is a child of CWD: {child_of_cwd_path}")

    found_paths = list(set(possible_paths)) # Remove duplicates

    if found_paths:
        for path in possible_paths: # Iterate through possible_paths to maintain some order of preference
            if os.path.isdir(path):
                _print_debug(f"  Selected 'RandomComboGenerator' location: {path}")
                return path

    print("\n--- Automatic 'RandomComboGenerator' location failed. ---")
    print("Could not automatically locate the 'RandomComboGenerator' directory based on common placements.")
    print("This is the directory that *contains* the folders you want to select from (e.g., 'NamesData', 'MoreFiles').")

    while True:
        user_input_path = input("Please manually enter the full path to your 'RandomComboGenerator' directory: ").strip()
        if os.path.isdir(user_input_path):
            _print_debug(f"Manually provided 'RandomComboGenerator' path: {user_input_path}")
            return user_input_path
        else:
            print(f"{RED}Invalid path or directory not found: '{user_input_path}'. Please try again.{RESET}")

def read_names_from_file(filepath):
    """
    Reads names from a specified text file, ensuring uniqueness.
    Also, saves words containing special characters to 'ErrorWords.txt'.
    This function is used by the combination generator.

    Args:
        filepath (str): The path to the wordlist file.

    Returns:
        tuple: A tuple containing:
            - list: A list of unique names read from the file (excluding those with special characters).
            - int: The total number of records (lines) found in the file.
    """
    names = set()
    total_records = 0
    error_words = [] # Collect error words here

    # Generate filename with short date stamp for ErrorWords file
    timestamp = datetime.now().strftime("%Y%m%d")
    error_words_filename = f"ErrorWords_{timestamp}.txt"
    # Define path for error words file in the main directory
    error_words_path = os.path.join("ErrorWords", error_words_filename)

    try:
        # Open the input file for reading
        with open(filepath, 'r', encoding="utf-8", errors="ignore") as file:
            for line in file:
                word = line.strip()
                total_records += 1
                # Check if the word contains any non-alphanumeric characters
                # This check is for the combination generator's purpose,
                # to ensure clean names for combinations.
                if not word.replace(',', '').replace(':', '').isalnum(): # Allow comma and colon for parsing
                    error_words.append(word) # Add to list, don't write immediately
                    _print_debug(f"Found special character in '{word}'. Will be saved to ErrorWords/{error_words_filename}")
                else:
                    # For combination generation, we only need the name part
                    # Assuming format is Name,Gender,Number or just Name
                    name_part = word.split(',')[0].strip()
                    if name_part:
                        names.add(name_part)
    except Exception as e:
        print(f"{RED}Error reading {filepath}: {e}{RESET}")

    # Write all collected error words at once
    if error_words:
        try:
            with open(error_words_path, 'a', encoding="utf-8") as error_file:
                for word in error_words:
                    error_file.write(word + '\n')
            print(f"{YELLOW}Warning: {len(error_words)} words with special characters found and saved to {error_words_path}{RESET}")
        except Exception as e:
            print(f"{RED}Error writing error words to {error_words_path}: {e}{RESET}")

    return list(names), total_records

def get_wordlist_files():
    """
    Retrieves a sorted list of .txt files present in the 'Wordlist' folder.

    Returns:
        list: A sorted list of filenames (e.g., ['file1.txt', 'file2.txt']).
    """
    files = []
    if os.path.exists("Wordlist"):
        for filename in os.listdir("Wordlist"):
            if filename.lower().endswith('.txt') and os.path.isfile(os.path.join("Wordlist", filename)):
                files.append(filename)
    return sorted(files)

def generate_random_names(names, combo_type, num_digits, num_records, year_range=None):
    """
    Generates name combinations based on the specified type and parameters.

    Args:
        names (list): A list of names to use for combination generation.
        combo_type (str): The type of combination to generate (e.g., '01', '02').
        num_digits (int): The number of digits for random numbers (if applicable).
        num_records (int): The desired number of records to generate.
        year_range (tuple, optional): A tuple (start_year, end_year) for year-based combos. Defaults to None.

    Returns:
        tuple: A tuple containing:
            - list: The list of generated combinations.
            - list: A list of up to 5 sample combinations.
    """
    combinations = []
    examples = []
    num_names = len(names)

    # Handle Type 01 (Name:Name) specifically for record generation
    if combo_type in ['1', '01']:
        records_to_generate = min(num_records, num_names)

        if records_to_generate < num_names:
            sampled_names = random.sample(names, records_to_generate)
            for name in sampled_names:
                combination = f"{name}:{name}"
                combinations.append(combination)
        else:
            for name in names:
                combination = f"{name}:{name}"
                combinations.append(combination)
        print(f"\nGenerating combinations for Type {combo_type}: {len(combinations)} records...", end="")
        examples = combinations[:5]
    else:
        for i in range(num_records):
            if not names: # Avoid error if names list is empty
                _print_debug("No names available for combination generation.")
                break
            name = random.choice(names)
            combination = ""

            # Combination logic as per TestComboInput.py
            if combo_type in ['2', '02', '03']:
                random_number = str(random.randint(0, 9))
                if combo_type in ['2', '02']:
                    combination = f"{name}{random_number}:{name}{random_number}"
                else:
                    combination = f"{name}{random_number}:{random_number}{name}"
            elif combo_type in ['4', '04', '5', '05', '23', '28']:
                random_number = f"{random.randint(0, 99):02d}"
                if combo_type in ['4', '04', '28']:
                    combination = f"{name}{random_number}:{name}{random_number}"
                elif combo_type in ['5', '05']:
                    combination = f"{random_number}:{random_number}"
                else:
                    combination = f"{name}:{name}{random_number}"
            elif combo_type in ['6', '06']:
                random_number = f"{random.randint(100, 999):03d}"
                combination = f"{random_number}:{random_number}"
            elif combo_type in ['7', '07']:
                random_number = f"{random.randint(1000, 9999):04d}"
                combination = f"{random_number}:{random_number}"
            elif combo_type in ['8', '08']:
                if year_range:
                    random_year = random.randint(year_range[0], year_range[1])
                    combination = f"{name}{random_year}:{name}{random_year}"
            elif combo_type == '24':
                if year_range:
                    random_year = random.randint(year_range[0], year_range[1])
                    combination = f"{name}{random_year}:{random_year}{name}"
            elif combo_type == '29':
                if year_range:
                    random_year = random.randint(year_range[0], year_range[1])
                    combination = f"{name.lower()}{random_year}:{name.lower()}{random_year}"
            elif combo_type == '30':
                if year_range:
                    random_year = random.randint(year_range[0], year_range[1])
                    combination = f"{name}:{name}{random_year}"
            elif combo_type in ['9', '09']:
                combination = f"{name}123:{name}123"
            elif combo_type == '10':
                combination = f"{name}123:123{name}"
            elif combo_type == '11':
                combination = f"{name}123:{name}321"
            elif combo_type == '12':
                combination = f"{name}@123:{name}@123"
            elif combo_type == '13':
                combination = f"{name}1234:{name}1234"
            elif combo_type == '14':
                combination = f"{name}1234:1234{name}"
            elif combo_type == '25':
                combination = f"{name}:{name}123"
            elif combo_type == '41':
                combination = f"{name}1:{name}123"
            elif combo_type == '26':
                combination = f"{name}:{name}1234"
            elif combo_type == '15':
                combination = f"{name}1:{name}1"
            elif combo_type == '27':
                combination = f"{name}:{name}1"
            elif combo_type == '16':
                combination = f"{name}2:{name}2"
            elif combo_type == '31':
                combination = f"{name}12345:{name}54321"

            elif combo_type == '32':
                combination = f"{name}1234:{name}4321"

            elif combo_type == '42':
                combination = f"{name}2025:{name}2025"

            elif combo_type == '33':
                combination = f"{name}1:{name}12"

            elif combo_type == '34':
                combination = f"{name}1:{name}1234"

            elif combo_type == '35':
                combination = f"{name.lower()}:{name.lower()}123"

            elif combo_type == '36':
                combination = f"{name}1:{name}12345"

            elif combo_type == '37':
                combination = f"{name}12:{name}21"

            elif combo_type == '38':
                combination = f"{name.lower()}:{name.lower()}12"

            elif combo_type == '39':
                combination = f"{name.lower()}:{name.lower()}1234"

            elif combo_type == '40':
                combination = f"{name.lower()}:{name.lower()}12345"

            elif combo_type == '17':
                if num_names >= 2:
                    other_name = random.choice([n for n in names if n != name])
                    combination = f"{name}1:{other_name}2"
                else:
                    _print_debug("Warning: Not enough unique names to generate examples for Type 17.")
            elif combo_type == '18':
                combination = f"{name}01:{name}01"
            elif combo_type == '19':
                combination = f"{name}02:{name}02"
            elif combo_type == '20':
                combination = f"{name}:{name.lower()}".replace(" ", "")
            elif combo_type == '21':
                combination = f"{name.upper()}:{name.upper()}".replace(" ", "")
            elif combo_type == '22':
                random_number = str(random.randint(0, 9))
                combination = f"{name}:{name}{random_number}"

            if combination:
                combinations.append(combination)

            print(f"\rGenerating records for Type {combo_type}: {i+1}/{num_records}", end="")
            if len(examples) < 5:
                examples.append(combination)
        print()

    final_combinations = combinations[:num_records]
    return final_combinations, examples

def display_sample_combination(combo_type, names, num_digits, year_range):
    """Displays a sample combination based on the selected combo type."""
    if not names:
        print("No names available to generate a sample.")
        return

    sample_name = random.choice(names)

    # Sample combination logic as per TestComboInput.py
    if combo_type in ['1', '01']:
        print(f"Sample combination (Type 01): {sample_name}:{sample_name}")
    elif combo_type in ['2', '02', '03']:
        sample_number = str(random.randint(0, 9))
        if combo_type in ['2', '02']:
            print(f"Sample combination (Type {combo_type}): {sample_name}{sample_number}:{sample_name}{sample_number}")
        else:
            print(f"Sample combination (Type {combo_type}): {sample_name}{sample_number}:{sample_number}{sample_name}")
    elif combo_type in ['4', '04', '5', '05', '23', '28']:
        sample_number = f"{random.randint(0, 99):02d}"
        if combo_type in ['4', '04', '28']:
            print(f"Sample combination (Type {combo_type}): {sample_name}{sample_number}:{sample_name}{sample_number}")
        elif combo_type in ['5', '05']:
            print(f"Sample combination (Type {combo_type}): {sample_number}:{sample_number}")
        else:
            print(f"Sample combination (Type {combo_type}): {sample_name}:{sample_name}{sample_number}")
    elif combo_type in ['6', '06']:
        sample_number = f"{random.randint(100, 999):03d}"
        print(f"Sample combination (Type {combo_type}): {sample_number}:{sample_number}")
    elif combo_type in ['7', '07']:
        sample_number = f"{random.randint(1000, 9999):04d}"
        print(f"Sample combination (Type {combo_type}): {sample_number}:{sample_number}")
    elif combo_type in ['8', '08']:
        if year_range:
            sample_year = random.randint(year_range[0], year_range[1])
            print(f"Sample combination (Type 08): {sample_name}{sample_year}:{sample_name}{sample_year}")
        else:
            print("Sample combination (Type 08): Year range not provided.")
    elif combo_type == '24':
        if year_range:
            sample_year = random.randint(year_range[0], year_range[1])
            print(f"Sample combination (Type 24): {sample_name}{sample_year}:{sample_year}{sample_name}")
        else:
            print("Sample combination (Type 24): Year range not provided.")
    elif combo_type == '29':
        if year_range:
            sample_year = random.randint(year_range[0], year_range[1])
            print(f"Sample combination (Type 29): {sample_name.lower()}{sample_year}:{sample_name.lower()}{sample_year}")
        else:
            print("Sample combination (Type 29): Year range not provided.")
    elif combo_type == '30':
        if year_range:
            sample_year = random.randint(year_range[0], year_range[1])
            print(f"Sample combination (Type 30): {sample_name}:{sample_name}{sample_year}")
        else:
            print("Sample combination (Type 30): Year range not provided.")
    elif combo_type in ['9', '09']:
        print(f"Sample combination (Type 09): {sample_name}123:{sample_name}123")
    elif combo_type == '10':
        print(f"Sample combination (Type 10): {sample_name}123:123{sample_name}")
    elif combo_type == '11':
        print(f"Sample combination (Type 11): {sample_name}123:{sample_name}321")
    elif combo_type =='25':
        print(f"Sample combination (Type 25): {sample_name}:{sample_name}123")

    elif combo_type =='41':
        print(f"Sample combination (Type 41): {sample_name}1:{sample_name}123")
    elif combo_type =='26':
        print(f"Sample combination (Type 26): {sample_name}:{sample_name}1234")
    elif combo_type == '12':
        print(f"Sample combination (Type 12): {sample_name}@123:{sample_name}@123")
    elif combo_type == '13':
        print(f"Sample combination (Type 13): {sample_name}1234:{sample_name}1234")
    elif combo_type == '14':
        print(f"Sample combination (Type 14): {sample_name}1234:1234{sample_name}")
    elif combo_type == '15':
        print(f"Sample combination (Type 15): {sample_name}1:{sample_name}1")
    elif combo_type == '27':
        print(f"Sample combination (Type 27): {sample_name}:{sample_name}1")
    elif combo_type == '16':
        print(f"Sample combination (Type 16): {sample_name}2:{sample_name}2")

    elif combo_type == '31':
        print(f"Sample combination (Type 31): {sample_name}12345:{sample_name}54321")
        
    elif combo_type == '32':
        print(f"Sample combination (Type 32): {sample_name}1234:{sample_name}4321")    
        
    elif combo_type == '42':
        print(f"Sample combination (Type 42): {sample_name}2025:{sample_name}2025")
        
    elif combo_type == '33':
        print(f"Sample combination (Type 33): {sample_name}1:{sample_name}12")
        
    elif combo_type == '34':
        print(f"Sample combination (Type 34): {sample_name}1:{sample_name}1234")
        
    elif combo_type == '35':
        print(f"Sample combination (Type 35): {sample_name.lower()}:{sample_name.lower()}123")

    elif combo_type == '36':
        print(f"Sample combination (Type 36): {sample_name}1:{sample_name}12345")

    elif combo_type == '37':
        print(f"Sample combination (Type 37): {sample_name}12:{sample_name}21")

    elif combo_type == '38':
        print(f"Sample combination (Type 38): {sample_name.lower()}:{sample_name.lower()}12")

    elif combo_type == '39':
        print(f"Sample combination (Type 39): {sample_name.lower()}:{sample_name.lower()}1234")

    elif combo_type == '40':
        print(f"Sample combination (Type 40): {sample_name.lower()}:{name.lower()}12345")

    elif combo_type == '17':
        if len(names) >= 2:
            other_name = random.choice([n for n in names if n != sample_name])
            print(f"Sample combination (Type 17): {sample_name}1:{other_name}2")
        else:
            print("Sample combination (Type 17): Not enough names to generate sample.")
    elif combo_type == '18':
        print(f"Sample combination (Type 18): {sample_name}01:{sample_name}01")
    elif combo_type == '19':
        print(f"Sample combination (Type 19): {sample_name}02:{sample_name}02")
    elif combo_type == '20':
        print(f"Sample combination (Type 20): {sample_name}:{sample_name.lower()}")
    elif combo_type == '21':
        print(f"Sample combination (Type 21): {sample_name.upper()}:{sample_name.upper()}")
    elif combo_type == '22':
        sample_number = str(random.randint(0, 9))
        print(f"Sample combination (Type 22): {sample_name}:{sample_name}{sample_number}")
    else:
        print("Invalid combo type.")

def combine_and_clean_files_option():
    """
    Implements the functionality of the original FileReading.py.
    Locates the 'RandomComboGenerator' directory, lists its subfolders,
    allows the user to select one, combines *only text files* from the selected subfolder,
    processes each line (preserves Name,Gender, removes duplicates),
    and saves the combined output into a 'Wordlist' directory.
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))

    target_base_directory = find_random_combo_generator_directory()
    if not target_base_directory:
        _print_debug("Script cannot proceed without a valid 'RandomComboGenerator' directory.")
        return

    _print_debug(f"\n--- Listing folders inside 'RandomComboGenerator' ({target_base_directory}) ---")

    folders = []
    try:
        all_items_in_target = os.listdir(target_base_directory)
        for item in all_items_in_target:
            item_path = os.path.join(target_base_directory, item)
            if os.path.isdir(item_path):
                folders.append(item)
    except FileNotFoundError:
        print(f"{RED}ERROR: The 'RandomComboGenerator' directory '{target_base_directory}' was not found after selection.{RESET}")
        print(f"{YELLOW}This should not happen if auto-detection or manual input was successful.{RESET}")
        return
    except PermissionError:
        print(f"{RED}ERROR: Permission denied to access contents of '{target_base_directory}'.{RESET}")
        print(f"{YELLOW}Please check read permissions for this directory.{RESET}")
        return
    except Exception as e:
        print(f"{RED}ERROR: An unexpected error occurred while listing subdirectories in '{target_base_directory}': {e}{RESET}")
        return

    if not folders:
        print(f"\n{YELLOW}No subfolders found inside '{target_base_directory}'.{RESET}")
        print(f"{YELLOW}This means there are no data folders for the script to combine files from.{RESET}")
        print(f"{YELLOW}Please ensure your data folders (e.g., 'NamesData', 'MoreFiles') are *inside* 'RandomComboGenerator'.{RESET}")
        return

    print(f"\n{BOLD}Available folders inside RandomComboGenerator to select from:{RESET}")
    for i, folder in enumerate(folders):
        print(f"{i + 1}. {folder}")

    selected_folder_index = -1
    while True:
        try:
            choice = input(f"{BOLD}Enter the number of the folder you want to read files from (1-{len(folders)}): {RESET}")
            selected_folder_index = int(choice) - 1
            if 0 <= selected_folder_index < len(folders):
                break
            else:
                print(f"{RED}Invalid number. Please enter a number within the given range.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a number.{RESET}")

    input_folder_name = folders[selected_folder_index]
    full_input_path = os.path.join(target_base_directory, input_folder_name)
    _print_debug(f"\nYou selected the subfolder: '{input_folder_name}'")
    _print_debug(f"Full path to the selected input subfolder: '{full_input_path}'")

    wordlist_directory = os.path.join(script_directory, "Wordlist")
    _print_debug(f"Output will be saved in 'Wordlist' directory at: {wordlist_directory}")

    # Prompt user for custom filename or use default
    while True:
        use_default_name = input(f"{BOLD}Do you want to use the default filename (CombinedNames_YYYYMMDD.txt)? (yes/no): {RESET}").lower().strip()
        current_date = datetime.now().strftime("%Y%m%d")
        if use_default_name in ['yes', 'y']:
            output_filename = f"CombinedNames_{current_date}.txt"
            break
        elif use_default_name in ['no', 'n']:
            custom_name_raw = input(f"{BOLD}Enter your desired filename (e.g., my_names): {RESET}").strip()
            if not custom_name_raw: # If empty input for custom name, fallback to default logic
                 print(f"{YELLOW}No custom name entered. Using default naming convention.{RESET}")
                 output_filename = f"CombinedNames_{current_date}.txt"
            else:
                # Remove any existing .txt to re-add consistently
                if custom_name_raw.lower().endswith('.txt'):
                    custom_name_raw = custom_name_raw[:-4]
                output_filename = f"{custom_name_raw}_{current_date}.txt"
            break
        else:
            print(f"{RED}Invalid input. Please enter 'yes' or 'no'.{RESET}")

    output_file_path = os.path.join(wordlist_directory, output_filename)
    _print_debug(f"Output file will be saved as: '{output_file_path}'")

    try:
        unique_lines = set()
        files_processed_count = 0

        _print_debug(f"\n--- Reading and processing files from '{full_input_path}' ---")
        all_files_in_input_folder = []
        try:
            all_files_in_input_folder = os.listdir(full_input_path)
        except PermissionError:
            print(f"{RED}ERROR: Permission denied to list files in '{full_input_path}'.{RESET}")
            print(f"{YELLOW}Please check read permissions for this selected data folder.{RESET}")
            return
        except Exception as e:
            print(f"{RED}ERROR: An unexpected error occurred while listing files in '{full_input_path}': {e}{RESET}")
            return

        if not all_files_in_input_folder:
            print(f"{YELLOW}No files found in the selected folder: '{full_input_path}'. The output file will be empty.{RESET}")
        
        for filename in all_files_in_input_folder:
            filepath = os.path.join(full_input_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith('.txt'):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                        for line in infile:
                            stripped_line = line.strip()
                            if not stripped_line:
                                continue

                            # --- MODIFIED: Preserve Name,Gender,Number if present ---
                            # Keep only the part before the second comma, if it exists.
                            # This means "Name,Gender,Number" becomes "Name,Gender"
                            # and "Name,Gender" remains "Name,Gender"
                            parts = stripped_line.split(',', 2) # Split into at most 3 parts
                            processed_line = ""
                            if len(parts) >= 2:
                                processed_line = f"{parts[0].strip()},{parts[1].strip()}"
                            else: # If only name or name,gender
                                processed_line = parts[0].strip()

                            if processed_line:
                                unique_lines.add(processed_line)
                    _print_debug(f"  Processed content from: {filename}")
                    files_processed_count += 1
                except UnicodeDecodeError:
                    _print_debug(f"WARNING: Could not read text file '{filename}' (likely not a plain text file or incorrect encoding). Skipping.")
                except Exception as e:
                    _print_debug(f"ERROR: An unexpected error occurred while reading text file '{filename}': {e}")
            else:
                _print_debug(f"  Skipping non-text file or non-file item: {filename}")
        
        if files_processed_count == 0 and not unique_lines:
            print(f"{YELLOW}No .txt files were found or processed from '{full_input_path}', or no valid lines were extracted. The output file will be empty.{RESET}")


        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            sorted_unique_lines = sorted(list(unique_lines))
            for line in sorted_unique_lines:
                outfile.write(line + "\n")

        print(f"\n{BOLD}{GREEN}--- Process Complete ---{RESET}")
        print(f"All relevant files from '{input_folder_name}' combined, duplicates removed, and formatted into '{output_file_path}'.")

    except PermissionError:
        print(f"{RED}ERROR: Permission denied to write the output file to '{output_file_path}'.{RESET}")
        print(f"{YELLOW}Please check your file permissions for the 'Wordlist' directory.{RESET}")
    except Exception as e:
        print(f"{RED}ERROR: An unexpected error occurred during file combination or writing: {e}{RESET}")

def generate_combinations_option():
    """
    Implements the functionality of the original TestComboInput.py.
    Handles user interaction for generating various name combinations.
    """
    wordlist_files = get_wordlist_files()

    if not wordlist_files:
        print(f"{YELLOW}No .txt files found in the 'Wordlist' folder. Please run Option 1 first or place your wordlist files in the 'Wordlist' folder.{RESET}")
        return

    print(f"\n{BOLD}Available wordlist files:{RESET}")
    for i, filename in enumerate(wordlist_files):
        print(f"{i + 1}. {filename}")

    names = []
    total_records = 0
    selected_file = ""

    while True:
        try:
            choice = int(input(f"{BOLD}Enter the number of the file you want to use: {RESET}"))
            if 1 <= choice <= len(wordlist_files):
                selected_file = wordlist_files[choice - 1]
                filepath = os.path.join("Wordlist", selected_file)
                # Note: read_names_from_file here will strip gender/number for combination generation
                names, total_records = read_names_from_file(filepath)
                break
            else:
                print(f"{RED}Invalid choice. Please enter a number from the list.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a number.{RESET}")

    if not names:
        print(f"{YELLOW}The selected file '{selected_file}' is empty or contains only words with special characters.{RESET}")
        return

    print(f"\nTotal number of records found in '{selected_file}': {total_records}")
    print(f"Total unique alphanumeric names loaded: {len(names)}")

    print(f"\n{BOLD}{GREEN}List of possible types of Combo to generate{RESET}")
    print("")
    print("01. Name:Name")
    print("02. NameNum:NameNum (1 Digit)")
    print("03. NameNum:NumName (1 Digit)")
    print("")
    print(f"{BOLD}{RED}===================================================={RESET}")
    print("Pick 1 for digits to create")
    print("04. NameNum:NameNum (2 Digits)")
    print("05. Number:Number (Max 2 Digits)")
    print("06. Number:Number (Max 3 Digits)")
    print("07. Number:Number (Max 4 Digits)")
    print(f"{BOLD}{RED}===================================================={RESET}")
    print("")
    print("08. NameYear:NameYear")
    print("09. Name123:Name123")
    print("10. Name123:123Name")
    print("11. Name123:Name321")
    print("12. Name@123:Name@123")
    print("13. Name1234:Name1234")
    print("14. Name1234:1234Name")
    print("15. Name1:Name1")
    print("16. Name2:Name2")
    print("17. Name1:Name2")
    print("18. Name01:Name01")
    print("19. Name02:Name02")
    print("20. Name:name")
    print("21. NAME:NAME")
    print("22. Name:NameNum (1 Digit)")
    print("23. Name:NameNum (2 Digits)")
    print("24. NameYear:YearName")
    print("25. Name:Name123")
    print("26. Name:Name1234")
    print("27. Name:Name1")
    print("28. NameNum:NameNum (2 Digit)")
    print("29. nameyear:nameyear")
    print("30. Name:NameYear")
    print("31. Name12345:Name54321")
    print("32. Name1234:Name4321")
    print("33. Name1:Name12")
    print("34. Name1:Name1234")
    print("35. name:name123")
    print("36. Name1:Name12345")
    print("37. Name12:Name21")
    print("38. name:name12")    
    print("39. name:name1234")
    print("40. name:name12345")
    print("41. Name1:Name123")
    print("42. Name2025:Name2025")
    
    print("43. Generate custom number of random records for ALL types")
    print("")

    combo_type = input(f"{BOLD}Enter the number corresponding to your choice (1-43): {RESET}")

    if combo_type == '43':
        while True:
            try:
                num_records_all_types = int(input(f"\n{BOLD}How many records would you like to generate for EACH type? {RESET}"))
                if num_records_all_types <= 0:
                    print(f"{RED}Please enter a positive number of records.{RESET}")
                else:
                    break
            except ValueError:
                print(f"{RED}Invalid input. Please enter an integer for the number of records.{RESET}")

        print(f"\n{BOLD}Initiating bulk generation of {num_records_all_types} records for each combo type...{RESET}")
        all_combo_types = [
            '01', '02', '03', '04',
            '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
            '31', '32', '33', '34', '35', '36', '37', '38', '39', '40',
            '41', '42'
        ]

        all_combined_records = []
        all_examples = []

        for current_combo_type in all_combo_types:
            num_digits = 0
            year_range = None

            if current_combo_type in ['02', '03', '22']:
                num_digits = 1
            elif current_combo_type in ['04', '23', '28']:
                num_digits = 2

            if current_combo_type in ['08', '24', '29', '30']:
                year_range = (1990, datetime.now().year)

            print(f"\n--- Generating for Type {current_combo_type} ---")
            generated_combos, type_examples = generate_random_names(names, current_combo_type, num_digits, num_records_all_types, year_range)
            all_combined_records.extend(generated_combos)
            all_examples.extend(type_examples)
            print(f"--- Finished Type {current_combo_type} ---\n")

        initial_record_count = len(all_combined_records)
        all_combined_records = list(set(all_combined_records)) # Deduplicate for bulk generation
        deduplicated_count = len(all_combined_records)
        if initial_record_count > deduplicated_count:
            print(f"Removed {initial_record_count - deduplicated_count} duplicate records.")

        # Prompt user for custom filename or use default for bulk generation
        while True:
            use_default_name = input(f"{BOLD}Do you want to use the default filename ({{num_records}}K_BulkCombo_YYYYMMDD.txt)? (yes/no): {RESET}").lower().strip()
            current_date = datetime.now().strftime("%Y%m%d")
            if use_default_name in ['yes', 'y']:
                if num_records_all_types % 1000 == 0:
                    records_prefix = f"{num_records_all_types // 1000}K"
                else:
                    records_prefix = str(num_records_all_types)
                output_filename = f"{records_prefix}_BulkCombo_{current_date}.txt"
                break
            elif use_default_name in ['no', 'n']:
                custom_name_raw = input(f"{BOLD}Enter your desired filename for the bulk file (e.g., my_bulk_combos): {RESET}").strip()
                if not custom_name_raw:
                    print(f"{YELLOW}No custom name entered. Using default naming convention.{RESET}")
                    if num_records_all_types % 1000 == 0:
                        records_prefix = f"{num_records_all_types // 1000}K"
                    else:
                        records_prefix = str(num_records_all_types)
                    output_filename = f"{records_prefix}_BulkCombo_{current_date}.txt"
                else:
                    if custom_name_raw.lower().endswith('.txt'):
                        custom_name_raw = custom_name_raw[:-4]
                    output_filename = f"{custom_name_raw}_{current_date}.txt"
                break
            else:
                print(f"{RED}Invalid input. Please enter 'yes' or 'no'.{RESET}")

        output_path = os.path.join("Combo", output_filename)

        with open(output_path, 'w') as output_file:
            for combo in all_combined_records:
                output_file.write(combo + '\n')

        print(f"\n{BOLD}{GREEN}All generated combinations have been saved to {output_path}.{RESET}")
        print(f"Total unique records created across all types: {len(all_combined_records)}")

        print(f"\n{BOLD}Top 5 generated combinations from all types (samples):{RESET}")
        for i, example in enumerate(all_examples[:5]):
            print(f"{i+1}. {example}")

        print(f"\n{BOLD}{GREEN}All bulk generation complete!{RESET}")
        return
    else:
        num_digits = 0
        if combo_type in ['2', '3', '4', '5', '6', '7', '22', '23', '28', '02', '03', '04', '05', '06', '07']:
            while True:
                try:
                    num_digits_input = input(f"{BOLD}Enter the number of digits for the random number (e.g., 1 for 0-9, 2 for 00-99): {RESET}")
                    num_digits = int(num_digits_input)
                    if num_digits < 1:
                        print(f"{RED}Number of digits must be positive.{RESET}")
                    else:
                        break
                except ValueError:
                    print(f"{RED}Invalid input. Please enter an integer for the number of digits.{RESET}")
                # Removed 'return' here to allow re-prompting on invalid input

        year_range = None
        if combo_type in ['8', '08', '24', '29', '30']:
            while True:
                year_input = input(f"{BOLD}Enter the year range (e.g., {RED}1500-2030{RESET}{BOLD}): {RESET}")
                try:
                    start_year_str, end_year_str = year_input.split('-')
                    start_year = int(start_year_str.strip())
                    end_year = int(end_year_str.strip())
                    if start_year > end_year:
                        print(f"{RED}Error: Start year cannot be greater than the end year.{RESET}")
                    else:
                        year_range = (start_year, end_year)
                        break
                except ValueError:
                    print(f"{RED}Invalid input. Please enter the year range in the format 'start-end' (e.g., 1500-2030).{RESET}")

        print(f"\n{BOLD}Generating a sample combination...{RESET}\n")
        display_sample_combination(combo_type, names, num_digits, year_range)

        if combo_type in ['1', '01']:
            print(f"\nGenerating all possible combinations ({total_records}) for Type 01...")
            num_records = total_records
        else:
            while True:
                try:
                    num_records = int(input(f"\n{BOLD}How many records would you like to generate? {RESET}"))
                    if num_records <= 0:
                        print(f"{RED}Please enter a positive number of records.{RESET}")
                    else:
                        break
                except ValueError:
                    print(f"{RED}Invalid input. Please enter an integer for the number of records.{RESET}")
                # Removed 'return' here to allow re-prompting on invalid input

        generated_combos, examples = generate_random_names(names, combo_type, num_digits, num_records, year_range)
        
        # Ensure unique records for single-type generation
        generated_combos = list(set(generated_combos))


        # Prompt user for custom filename or use default
        while True:
            use_default_name = input(f"{BOLD}Do you want to use the default filename (Type{{combo_type}}_YYYYMMDD.txt)? (yes/no): {RESET}").lower().strip()
            current_date = datetime.now().strftime("%Y%m%d")
            if use_default_name in ['yes', 'y']:
                output_filename = f"Type{combo_type}_{current_date}.txt"
                break
            elif use_default_name in ['no', 'n']:
                custom_name_raw = input(f"{BOLD}Enter your desired filename (e.g., my_combos): {RESET}").strip()
                if not custom_name_raw:
                    print(f"{YELLOW}No custom name entered. Using default naming convention.{RESET}")
                    output_filename = f"Type{combo_type}_{current_date}.txt"
                else:
                    if custom_name_raw.lower().endswith('.txt'):
                        custom_name_raw = custom_name_raw[:-4]
                    output_filename = f"{custom_name_raw}_{current_date}.txt"
                break
            else:
                print(f"{RED}Invalid input. Please enter 'yes' or 'no'.{RESET}")

        output_path = os.path.join("Combo", output_filename)

        with open(output_path, 'w') as output_file:
            for combo in generated_combos:
                output_file.write(combo + '\n')

        print(f"\n{BOLD}{GREEN}Random names have been saved to {output_path}.{RESET}")
        print(f"Total records created: {len(generated_combos)}")

        print(f"\n{BOLD}Top 5 generated combinations:{RESET}")
        for i, example in enumerate(examples):
            print(f"{i+1}. {example}")

def main_menu():
    """Presents the main menu to the user for choosing an operation."""
    while True:
        print(f"\n{BOLD}{YELLOW}--- Main Menu ---{RESET}")
        print(f"1. {BOLD}Combine and Clean Text Files{RESET} (from 'RandomComboGenerator' subfolders)")
        print(f"2. {BOLD}Generate Name Combinations{RESET} (from 'Wordlist' files)")
        print(f"3. {BOLD}Exit{RESET}")
        choice = input(f"{BOLD}Enter your choice (1-3): {RESET}")

        if choice == '1':
            combine_and_clean_files_option()
        elif choice == '2':
            generate_combinations_option()
        elif choice == '3':
            print(f"{BOLD}Exiting application. Goodbye!{RESET}")
            break
        else:
            print(f"{RED}Invalid choice. Please enter 1, 2, or 3.{RESET}")

# --- Run the main application ---
if __name__ == "__main__":
    create_folders() # Ensure all necessary folders exist at startup
    main_menu()