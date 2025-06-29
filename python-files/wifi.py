import subprocess
import re
import os
import sys # Added for argument parsing

def get_wifi_profiles_and_passwords():
    """
    Retrieves Wi-Fi profiles and attempts to extract their passwords
    by calling the 'netsh' command.
    Requires Administrator privileges to get clear text passwords.
    """
    profiles_data = []

    try:
        # Get all Wi-Fi profile names
        # Using encoding 'cp858' which is common for Windows console output in many locales.
        # If you encounter issues with non-English characters, try 'utf-8' or 'latin-1'.
        result_profiles = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True,
            text=True,
            check=True,
            encoding='cp858',
            shell=True # Use shell=True for simpler command execution on Windows
        )
        
        # Regex to find profile names, handles both English ("All User Profile")
        # and Persian ("همه پروفایل های کاربر") outputs.
        profile_names = re.findall(r"(?:All User Profile|همه پروفایل های کاربر)\s*:\s*(.*)", result_profiles.stdout)

        # Flatten the list of tuples and remove empty strings
        actual_profile_names = [name.strip() for tpl in profile_names for name in tpl if name.strip()]

        if not actual_profile_names:
            print("No Wi-Fi profiles found or failed to parse profile names.")
            return profiles_data

        print("[*] Found {} Wi-Fi Profiles.".format(len(actual_profile_names)))
        print("    (Processing details... This might take a moment)\n")

        # Determine if passwords should be shown based on command line arguments
        show_passwords_arg = "-showpasswords" in [arg.lower() for arg in sys.argv]

        for profile_name in actual_profile_names:
            profile_info = {
                "ProfileName": profile_name,
                "SecurityType": "N/A",
                "Password": "N/A", # Default, will be updated
                "ErrorMessage": None
            }
            
            try:
                # Get detailed profile info including clear text key
                # Command: netsh wlan show profiles name="ProfileName" key=clear
                result_key = subprocess.run(
                    ['netsh', 'wlan', 'show', 'profiles', 'name', f'"{profile_name}"', 'key=clear'],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='cp858',
                    shell=True
                )

                # Extract Security Type
                security_match = re.search(r"(?:Authentication|احراز هویت)\s*:\s*(.*)", result_key.stdout)
                if security_match:
                    profile_info["SecurityType"] = security_match.groups()[0].strip()
                    # If it's an "Open" network, there's no password
                    if profile_info["SecurityType"].lower() == "open":
                        profile_info["Password"] = "N/A (Open Network)"
                
                # Extract Key Content (password)
                if show_passwords_arg:
                    password_match = re.search(r"(?:Key Content|محتوای کلید)\s*:\s*(.*)", result_key.stdout)
                    if password_match:
                        # Find the first non-empty group from the regex match
                        password = next(filter(None, password_match.groups()), None)
                        if password:
                            profile_info["Password"] = password.strip()
                        else:
                            profile_info["Password"] = "N/A (Key content not found in output)"
                    else:
                        # If Key Content not found, it might be an encrypted network without easily retrievable key
                        if profile_info["SecurityType"].lower() != "open":
                             profile_info["Password"] = "N/A (Password Not Found / Encrypted)"
                else:
                    profile_info["Password"] = "N/A (Use -ShowPasswords)"


            except subprocess.CalledProcessError as e:
                # This error often means not running as Administrator or profile not found
                if "The requested operation requires elevation" in e.stderr:
                    profile_info["Password"] = "N/A (Access Denied - Run as Administrator)"
                    profile_info["ErrorMessage"] = "Requires Administrator privileges"
                elif "Profile" in e.stderr and "is not found" in e.stderr:
                    profile_info["ErrorMessage"] = f"Profile '{profile_name}' not found by netsh"
                    profile_info["Password"] = "N/A (Error)"
                else:
                    profile_info["ErrorMessage"] = f"Error during key extraction: {e.stderr.strip()}"
                    profile_info["Password"] = "N/A (Error)"
            except Exception as e:
                profile_info["ErrorMessage"] = f"Unexpected error during key extraction: {e}"
                profile_info["Password"] = "N/A (Error)"
            
            profiles_data.append(profile_info)

    except subprocess.CalledProcessError as e:
        print(f"Error executing netsh command: {e.stderr}")
        print("Please ensure netsh is available in your PATH and you have necessary permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return profiles_data

if __name__ == "__main__":
    if os.name != 'nt': # Check if running on Windows
        print("This script is designed for Windows operating systems as it relies on 'netsh'.")
        sys.exit(1) # Exit with an error code

    print("""
###############################################
#   Wi-Fi Password Extractor (Python)         #
#   Outputs to Shell (No GUI)                 #
#   Requires Administrator privileges for passwords
###############################################
""")
    wifi_data = get_wifi_profiles_and_passwords()

    if wifi_data:
        # Determine column widths for tabular formatting
        max_name = max([len(p['ProfileName']) for p in wifi_data]) if wifi_data else len("Profile Name")
        max_security = max([len(p['SecurityType']) for p in wifi_data]) if wifi_data else len("Security Type")
        max_password = max([len(p['Password']) for p in wifi_data]) if wifi_data else len("Password")
        
        # Adjust for header length if header text is longer than content
        max_name = max(max_name, len("Profile Name"))
        max_security = max(max_security, len("Security Type"))
        max_password = max(max_password, len("Password"))

        # Add some padding for better readability
        padding = 4
        max_name += padding
        max_security += padding
        max_password += padding

        print("\n--- Extracted Wi-Fi Profiles & Passwords ---")
        
        # Print header row
        header = f"{'Profile Name':<{max_name}}{'Security Type':<{max_security}}{'Password':<{max_password}}"
        print(header)
        print("-" * len(header))

        # Print data rows
        for profile in wifi_data:
            # Shorten password display if it's too long for the column, for visual clarity only
            password_to_display = profile['Password']
            if len(password_to_display) > max_password - padding:
                 password_to_display = password_to_display[:max_password - padding - 3] + "..." # Add "..." for truncation

            print(f"{profile['ProfileName']:<{max_name}}{profile['SecurityType']:<{max_security}}{password_to_display:<{max_password}}")
            # Print error messages separately if they exist
            if profile["ErrorMessage"]:
                print(f"  [!] Error for {profile['ProfileName']}: {profile['ErrorMessage']}")
            
        print("-" * len(header)) # Footer line for table
    else:
        print("No Wi-Fi data could be extracted or processed.")