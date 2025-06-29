import subprocess
import re
import os

def get_wifi_profiles_and_passwords():
    """
    Retrieves Wi-Fi profiles and attempts to extract their passwords
    by calling the 'netsh' command.
    Requires Administrator privileges to get clear text passwords.
    """
    profiles_data = []

    try:
        # Get all Wi-Fi profile names
        # Command: netsh wlan show profiles
        # Encoding 'cp858' is common for Windows console output in some locales
        # You might need 'utf-8' or 'latin-1' depending on your system's locale.
        result_profiles = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True,
            text=True,
            check=True,
            encoding='cp858',
            shell=True # Use shell=True for simpler command execution on Windows
        )
        
        # Regex to find profile names
        # It looks for lines like "All User Profile     : ProfileName"
        # Or "همه پروفایل های کاربر     : ProfileName" for Persian Windows
        profile_names = re.findall(r"All User Profile\s*:\s*(.*)|همه پروفایل های کاربر\s*:\s*(.*)", result_profiles.stdout)

        # Flatten the list of tuples and remove empty strings
        actual_profile_names = [name.strip() for tpl in profile_names for name in tpl if name.strip()]

        if not actual_profile_names:
            print("No Wi-Fi profiles found or failed to parse profile names.")
            return profiles_data

        print("[*] Found Wi-Fi Profiles:")
        for name in actual_profile_names:
            print(f"    - {name}")

        print("\n[*] Attempting to extract passwords...")
        print("    (NOTE: This requires Administrator privileges.)\n")

        for profile_name in actual_profile_names:
            profile_info = {"Name": profile_name, "Password": "N/A (Requires Admin / Not found)"}
            
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

                # Regex to find the Key Content (password)
                # Looks for "Key Content            : YourPassword"
                # Or "محتوای کلید            : رمزعبور شما" for Persian Windows
                password_match = re.search(r"Key Content\s*:\s*(.*)|محتوای کلید\s*:\s*(.*)", result_key.stdout)

                if password_match:
                    # Get the non-empty group from the match
                    password = next(filter(None, password_match.groups()), None)
                    if password:
                        profile_info["Password"] = password.strip()
                    else:
                        profile_info["Password"] = "N/A (Key content not found in output)"
                else:
                    profile_info["Password"] = "N/A (Password not found in output / Requires Admin)"

            except subprocess.CalledProcessError as e:
                # This error often means not running as Administrator
                if "The requested operation requires elevation" in e.stderr:
                    profile_info["Password"] = "N/A (Access Denied - Run as Administrator)"
                elif "Profile" in e.stderr and "is not found" in e.stderr:
                     profile_info["Password"] = f"N/A (Profile '{profile_name}' not found by netsh)"
                else:
                    profile_info["Password"] = f"N/A (Error during key extraction: {e.stderr.strip()})"
            except Exception as e:
                profile_info["Password"] = f"N/A (Unexpected error during key extraction: {e})"
            
            profiles_data.append(profile_info)

    except subprocess.CalledProcessError as e:
        print(f"Error executing netsh command: {e.stderr}")
        print("Please ensure netsh is available in your PATH and you have necessary permissions.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return profiles_data

if __name__ == "__main__":
    if os.name == 'nt': # Check if running on Windows
        print("""
###############################################
#   Wi-Fi Password Extractor (Python)         #
#   Mimics 'netsh wlan show profiles'         #
#   Requires Administrator privileges         #
###############################################
""")
        wifi_data = get_wifi_profiles_and_passwords()

        if wifi_data:
            print("\n--- Extracted Wi-Fi Profiles & Passwords ---")
            for profile in wifi_data:
                print(f"Profile: {profile['Name']}")
                print(f"Password: {profile['Password']}")
                print("-" * 30)
        else:
            print("No data extracted.")
    else:
        print("This script is designed for Windows operating systems.")
        print("The 'netsh' command is not available on non-Windows systems.")