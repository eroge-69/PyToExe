
import os
import sys
import ctypes
import traceback

def is_admin():
    """Check if script is running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def remove_extension_safely(file_path, new_name):
    """Safely rename a file with error handling"""
    try:
        os.rename(file_path, new_name)
        return True, ""
    except Exception as e:
        return False, str(e)

def process_drive(drive, extension):
    """Process all files on a drive with the given extension"""
    print(f"\nProcessing drive {drive}...")
    
    total = 0
    renamed = 0
    errors = 0
    
    for root, dirs, files in os.walk(drive):
        for file in files:
            if file.endswith(extension):
                total += 1
                old_path = os.path.join(root, file)
                new_name = file[:-len(extension)]
                new_path = os.path.join(root, new_name)
                
                success, error = remove_extension_safely(old_path, new_path)
                
                if success:
                    renamed += 1
                    print(f"Renamed: {file} → {new_name}")
                else:
                    errors += 1
                    print(f"Error renaming {file}: {error}")
    
    return total, renamed, errors

def main():
    if not is_admin():
        print("This script requires administrator privileges!")
        print("Please run it as administrator.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    extension = ".2Z4LZHxsd"
    drives = ['C:\\', 'D:\\', 'E:\\', 'F:\\', 'G:\\']
    
    print("=== File Extension Removal Tool ===")
    print(f"Removing '{extension}' extension from all files on {', '.join(drives)}")
    print("This may take several minutes...\n")
    
    for drive in drives:
        if not os.path.exists(drive):
            print(f"Drive {drive} not found. Skipping...")
            continue
        
        total, renamed, errors = process_drive(drive, extension)
        
        print(f"\nDrive {drive} results:")
        print(f"  Files found: {total}")
        print(f"  Successfully renamed: {renamed}")
        print(f"  Errors: {errors}\n")
    
    print("Operation completed!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user!")
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        traceback.print_exc()
        input("Press Enter to exit...")
