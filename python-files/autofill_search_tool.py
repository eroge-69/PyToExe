import os
import sys
from datetime import datetime

def search_in_file(file_path, search_word):
    """Search for word in a text file and return matches with line numbers."""
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line_num, line in enumerate(file, 1):
                if search_word.lower() in line.lower():
                    matches.append((line_num, line.strip()))
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return matches

def find_autofill_in_subfolder(subfolder_path):
    """Find 'Autofill' folder inside a subfolder (case insensitive)."""
    try:
        for item in os.listdir(subfolder_path):
            item_path = os.path.join(subfolder_path, item)
            if os.path.isdir(item_path) and item.lower() == 'autofill':
                return item_path
    except Exception as e:
        print(f"Error accessing subfolder {subfolder_path}: {e}")
    return None

def search_txt_files_in_autofill(autofill_folder, search_word):
    """Search for word in all .txt files within an Autofill folder."""
    results = []
    txt_files = []
    
    # Find all .txt files in the Autofill folder (including nested folders)
    try:
        for root, dirs, files in os.walk(autofill_folder):
            for file in files:
                if file.lower().endswith('.txt'):
                    txt_files.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error scanning Autofill folder {autofill_folder}: {e}")
        return [], 0
    
    # Search in each .txt file
    for txt_file in txt_files:
        matches = search_in_file(txt_file, search_word)
        if matches:
            results.append({
                'file': txt_file,
                'matches': matches
            })
    
    return results, len(txt_files)

def get_subfolders(main_folder):
    """Get all direct subfolders from the main folder."""
    subfolders = []
    try:
        for item in os.listdir(main_folder):
            item_path = os.path.join(main_folder, item)
            if os.path.isdir(item_path):
                subfolders.append(item_path)
    except Exception as e:
        print(f"Error accessing folder {main_folder}: {e}")
    return subfolders

def create_results_folder():
    """Create a results folder with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_folder = f"SearchResults_{timestamp}"
    
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    
    return results_folder

def save_results(results_folder, search_word, all_results, summary_info):
    """Save all results to files."""
    
    # Save summary
    summary_file = os.path.join(results_folder, "SUMMARY.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("AUTOFILL SEARCH RESULTS\n")
        f.write("=" * 50 + "\n")
        f.write(f"Search Word: {search_word}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Main Folder: {summary_info['main_folder']}\n")
        f.write(f"Subfolders Checked: {summary_info['subfolders_found']}\n")
        f.write(f"Autofill Folders Found: {summary_info['autofill_folders']}\n")
        f.write(f"Text Files Scanned: {summary_info['txt_files']}\n")
        f.write(f"Total Matches: {summary_info['total_matches']}\n")
        f.write("=" * 50 + "\n\n")
        
        for subfolder_path, subfolder_data in all_results.items():
            folder_name = os.path.basename(subfolder_path)
            f.write(f"📁 SUBFOLDER: {folder_name}\n")
            f.write(f"   Path: {subfolder_path}\n")
            f.write("-" * 40 + "\n")
            
            if not subfolder_data['has_autofill']:
                f.write("   No 'Autofill' folder found\n\n")
                continue
            
            f.write(f"   ✅ Autofill folder found: {subfolder_data['autofill_path']}\n")
            f.write(f"   Text files found: {subfolder_data['txt_count']}\n")
            
            if subfolder_data['matches']:
                f.write(f"   Files with matches: {len(subfolder_data['matches'])}\n")
                for match_file in subfolder_data['matches']:
                    file_name = os.path.basename(match_file['file'])
                    f.write(f"   📄 {file_name}\n")
                    f.write(f"      Matches: {len(match_file['matches'])}\n")
                    for line_num, line_content in match_file['matches'][:3]:  # Show first 3 matches
                        if len(line_content) > 60:
                            line_content = line_content[:57] + "..."
                        f.write(f"      Line {line_num}: {line_content}\n")
                    if len(match_file['matches']) > 3:
                        f.write(f"      ... and {len(match_file['matches']) - 3} more matches\n")
            else:
                f.write("   No matches found\n")
            f.write("\n")
    
    # Save detailed matches
    if summary_info['total_matches'] > 0:
        details_folder = os.path.join(results_folder, "DetailedMatches")
        os.makedirs(details_folder, exist_ok=True)
        
        file_counter = 1
        for subfolder_path, subfolder_data in all_results.items():
            if subfolder_data['has_autofill']:
                for match_file in subfolder_data['matches']:
                    if match_file['matches']:
                        subfolder_name = os.path.basename(subfolder_path)
                        file_name = os.path.basename(match_file['file'])
                        filename = f"{file_counter:03d}_{subfolder_name}_{file_name}"
                        detail_file = os.path.join(details_folder, filename)
                        
                        with open(detail_file, 'w', encoding='utf-8') as f:
                            f.write(f"DETAILED MATCHES\n")
                            f.write("=" * 40 + "\n")
                            f.write(f"Search Word: {search_word}\n")
                            f.write(f"Subfolder: {subfolder_name}\n")
                            f.write(f"Autofill Path: {subfolder_data['autofill_path']}\n")
                            f.write(f"Source File: {match_file['file']}\n")
                            f.write(f"Total Matches: {len(match_file['matches'])}\n")
                            f.write("=" * 40 + "\n\n")
                            
                            for line_num, line_content in match_file['matches']:
                                f.write(f"LINE {line_num}:\n{line_content}\n\n")
                        
                        file_counter += 1

def main():
    print("=" * 60)
    print("           AUTOFILL SEARCH TOOL")
    print("=" * 60)
    print("Searches for words in .txt files inside 'Autofill' folders")
    print("Structure: MainFolder/Subfolders/Autofill/*.txt")
    print()
    
    # Get main folder
    print("📁 STEP 1: Enter the main folder path")
    print("   (This folder should contain the subfolders to search)")
    print()
    
    main_folder = input("Main folder path: ").strip()
    
    if not main_folder or not os.path.isdir(main_folder):
        print("❌ Invalid folder path. Exiting...")
        input("Press Enter to exit...")
        return
    
    # Get subfolders
    print(f"\n🔍 Finding subfolders in: {main_folder}")
    subfolders = get_subfolders(main_folder)
    
    if not subfolders:
        print("❌ No subfolders found. Exiting...")
        input("Press Enter to exit...")
        return
    
    print(f"✅ Found {len(subfolders)} subfolders:")
    for i, folder in enumerate(subfolders, 1):
        print(f"   {i}. {os.path.basename(folder)}")
    
    # Get search word
    print(f"\n🔍 STEP 2: What word do you want to search for?")
    search_word = input("Search word: ").strip()
    
    if not search_word:
        print("❌ No search word provided. Exiting...")
        input("Press Enter to exit...")
        return
    
    # Start searching
    print(f"\n⚡ STEP 3: Searching for '{search_word}' in .txt files...")
    print()
    
    # Create results folder
    results_folder = create_results_folder()
    
    # Store all results
    all_results = {}
    summary_info = {
        'main_folder': main_folder,
        'subfolders_found': len(subfolders),
        'autofill_folders': 0,
        'txt_files': 0,
        'total_matches': 0
    }
    
    # Search each subfolder
    for subfolder in subfolders:
        subfolder_name = os.path.basename(subfolder)
        print(f"🔎 Checking subfolder: {subfolder_name}")
        
        # Look for Autofill folder in this subfolder
        autofill_folder = find_autofill_in_subfolder(subfolder)
        
        if not autofill_folder:
            print(f"   No 'Autofill' folder found")
            all_results[subfolder] = {
                'has_autofill': False,
                'autofill_path': None,
                'txt_count': 0,
                'matches': []
            }
        else:
            print(f"   ✅ Found Autofill folder")
            summary_info['autofill_folders'] += 1
            
            # Search for txt files and matches in the Autofill folder
            matches, txt_count = search_txt_files_in_autofill(autofill_folder, search_word)
            summary_info['txt_files'] += txt_count
            
            match_count = sum(len(m['matches']) for m in matches)
            summary_info['total_matches'] += match_count
            
            all_results[subfolder] = {
                'has_autofill': True,
                'autofill_path': autofill_folder,
                'txt_count': txt_count,
                'matches': matches
            }
            
            if txt_count == 0:
                print(f"      No .txt files in Autofill folder")
            elif matches:
                print(f"      ✅ Found {match_count} matches in {len(matches)} files ({txt_count} total files)")
            else:
                print(f"      No matches found ({txt_count} files checked)")
        print()
    
    # Save results
    print("💾 STEP 4: Saving results...")
    try:
        save_results(results_folder, search_word, all_results, summary_info)
        
        print("✅ SEARCH COMPLETE!")
        print("=" * 50)
        print(f"📊 SUMMARY:")
        print(f"   Main folder: {os.path.basename(main_folder)}")
        print(f"   Subfolders checked: {summary_info['subfolders_found']}")
        print(f"   Autofill folders found: {summary_info['autofill_folders']}")
        print(f"   Text files scanned: {summary_info['txt_files']}")
        print(f"   Total matches found: {summary_info['total_matches']}")
        print()
        print(f"📁 Results saved in: {results_folder}")
        print(f"   📄 SUMMARY.txt - Overview of all results")
        if summary_info['total_matches'] > 0:
            print(f"   📂 DetailedMatches/ - Individual files with full matches")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        input("Press Enter to exit...")