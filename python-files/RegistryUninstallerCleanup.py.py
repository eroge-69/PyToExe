import sys
import ctypes
import winreg
import os

# --- Constants for Registry Access ---
# HKEY_LOCAL_MACHINE for system-wide installations
# HKEY_CURRENT_USER for user-specific installations
REGISTRY_HIVES = {
    "system": winreg.HKEY_LOCAL_MACHINE,
    "user": winreg.HKEY_CURRENT_USER
}

# Paths to the Uninstall keys for 64-bit and 32-bit (on 64-bit OS) applications
UNINSTALL_PATHS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" # For 32-bit apps on 64-bit Windows
]

class RegistryCleaner:
    """
    A tool to find and remove orphaned uninstaller entries from the Windows Registry.
    """

    def __init__(self):
        self.programs = []

    def is_admin(self):
        """Check if the script is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        """
        Re-launches the script with administrator privileges if not already running as admin.
        """
        if self.is_admin():
            return True
            
        print("Administrator privileges required. Attempting to re-launch...")
        try:
            # Re-run the script with "runas" verb to prompt for elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            # Exit the non-elevated instance
            sys.exit(0)
        except Exception as e:
            print(f"\n[ERROR] Failed to elevate privileges: {e}")
            print("Please run this script from an Administrator Command Prompt or PowerShell.")
            sys.exit(1)

    def scan_registry(self):
        """
        Scans the relevant registry paths and collects information about installed programs.
        """
        print("Scanning registry for installed programs...")
        
        found_programs = []
        for hive_name, hive_key in REGISTRY_HIVES.items():
            for path in UNINSTALL_PATHS:
                try:
                    # Open the main 'Uninstall' key
                    with winreg.OpenKey(hive_key, path) as key:
                        # Enumerate all subkeys (each is a program)
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            subkey_name = winreg.EnumKey(key, i)
                            try:
                                # Open the program's specific subkey
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    # Attempt to read the display name
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    
                                    # Skip entries without a display name (often system components)
                                    if display_name:
                                        found_programs.append({
                                            "name": display_name,
                                            "hive_name": hive_name,
                                            "hive_key": hive_key,
                                            "path": path,
                                            "subkey": subkey_name
                                        })
                            except (FileNotFoundError, OSError):
                                # This can happen if a subkey is malformed or lacks a DisplayName
                                continue
                except FileNotFoundError:
                    # This path might not exist (e.g., WOW6432Node on a 32-bit OS)
                    continue
        
        # Sort programs alphabetically for easier selection
        self.programs = sorted(found_programs, key=lambda p: p['name'].lower())
        print(f"Found {len(self.programs)} program entries.")

    def display_and_select_program(self):
        """
        Displays the list of found programs and prompts the user to select one.
        """
        if not self.programs:
            print("\nNo program entries found in the standard registry locations.")
            return None

        print("\n--- List of Installed Program Entries ---")
        for i, program in enumerate(self.programs):
            print(f"  [{i+1:3d}] {program['name']}")
        
        print("\n-----------------------------------------")
        
        while True:
            try:
                choice = input("Enter the number of the program to remove (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(self.programs):
                    return self.programs[index]
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except (KeyboardInterrupt, EOFError):
                 print("\nOperation cancelled.")
                 return None

    def remove_program_entry(self, program_info):
        """
        Removes the selected program's registry key after user confirmation.
        """
        print("\n" + "="*50)
        print(f"You have selected to remove:")
        print(f"  Program Name: {program_info['name']}")
        print(f"  Registry Key: HKEY_{program_info['hive_name'].upper()}\\{program_info['path']}\\{program_info['subkey']}")
        print("="*50)
        print("\n[WARNING] This action is irreversible and only removes the entry from the")
        print("'Add or remove programs' list. It does NOT delete any files on disk.")
        
        try:
            confirm = input("Are you absolutely sure you want to proceed? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled by user.")
                return

            print(f"\nAttempting to remove registry key for '{program_info['name']}'...")
            
            # Open the parent key with write access
            parent_key = winreg.OpenKey(program_info['hive_key'], program_info['path'], 0, winreg.KEY_WRITE)
            
            # Delete the specific subkey for the program
            winreg.DeleteKey(parent_key, program_info['subkey'])
            
            winreg.CloseKey(parent_key)
            
            print("\n[SUCCESS] The registry entry has been successfully removed.")

        except PermissionError:
            print("\n[ERROR] Permission denied. This script must be run with administrator privileges.")
        except FileNotFoundError:
            print("\n[ERROR] The registry key could not be found. It may have already been removed.")
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")


def main():
    """Main function to run the cleaner."""
    cleaner = RegistryCleaner()
    
    # Ensure the script is running with administrator rights
    cleaner.run_as_admin()

    print("="*60)
    print("      Windows Uninstaller Entry Cleanup Tool")
    print("="*60)
    print("\nThis tool helps remove orphaned entries from 'Add or remove programs'.")
    print("Use this ONLY after you have manually deleted the program's files.")
    print("\nDISCLAIMER: Modifying the registry can be risky. Use with caution.")
    
    cleaner.scan_registry()
    
    selected_program = cleaner.display_and_select_program()
    
    if selected_program:
        cleaner.remove_program_entry(selected_program)

    print("\nProgram finished. Press Enter to exit.")
    input()


if __name__ == "__main__":
    main()