import os

def rename_first_file_by_extension(extension, new_name):
    """Renames the first file found with the given extension to new_name."""
    files = [f for f in os.listdir('.') if f.endswith(extension)]
    if files:
        print(f"Renaming {files[0]} to {new_name}")
        os.rename(files[0], new_name)
    else:
        print(f"No file with extension {extension} found.")

def rename_edi_files_sequentially():
    """Renames files in the EDI directory sequentially (edi_one, edi_two, etc.)."""
    num_to_word = {
        1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
        6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'
    }
    edi_dir = 'EDI'
    if not os.path.exists(edi_dir):
        print(f"Directory {edi_dir} does not exist.")
        return

    files = [f for f in os.listdir(edi_dir) if os.path.isfile(os.path.join(edi_dir, f))]
    files.sort() # Ensure consistent ordering

    print(f"Renaming files in {edi_dir}...")
    for i, old_name in enumerate(files):
        if (i + 1) in num_to_word:
            new_name = f"edi_{num_to_word[i + 1]}{os.path.splitext(old_name)[1]}"
            old_path = os.path.join(edi_dir, old_name)
            new_path = os.path.join(edi_dir, new_name)
            print(f"  Renaming {old_name} to {new_name}")
            os.rename(old_path, new_path)
        else:
            print(f"  Skipping {old_name}: No word mapping for index {i+1}")

if __name__ == "__main__":
    # Rename .csv file
    rename_first_file_by_extension('.csv', 'ADMIN.csv')

    # Rename .xls file
    rename_first_file_by_extension('.xls', 'Account_Reconciliation.xls')

    # Batch rename files in EDI directory
    rename_edi_files_sequentially()