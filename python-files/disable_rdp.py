import os
import winreg

def disable_rdp_idle_timeout():
    """
    Disables the RDP idle session time limit by removing the MaxIdleTime
    registry value.

    This script must be run with administrator privileges to modify the
    HKEY_LOCAL_MACHINE registry hive.
    """
    # The registry path corresponding to the Group Policy setting
    # "Set time limit for active but idle Remote Desktop Services sessions"
    registry_path = r"SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"
    value_name = "MaxIdleTime"

    print("Attempting to disable the RDP idle session time limit...")

    try:
        # Open the registry key with write permissions
        # HKEY_LOCAL_MACHINE is represented as winreg.HKEY_LOCAL_MACHINE
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            registry_path,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
        )

        try:
            # Check if the registry value exists before attempting to delete it
            # This prevents an error if the policy is already set to disabled.
            _ = winreg.QueryValueEx(reg_key, value_name)
            
            # If the value exists, delete it
            winreg.DeleteValue(reg_key, value_name)
            print(f"Successfully deleted the registry value '{value_name}'.")
            print("The RDP idle session time limit is now disabled.")
            print("A logoff/logon or reboot may be required for the change to take full effect.")

        except FileNotFoundError:
            print(f"The registry value '{value_name}' does not exist.")
            print("The RDP idle session time limit is already disabled.")

        finally:
            # Always close the key
            winreg.CloseKey(reg_key)

    except FileNotFoundError:
        print(f"The registry path '{registry_path}' was not found.")
        print("This may be an issue with your system configuration.")

    except PermissionError:
        print("Permission denied: Please run the script as an administrator.")
        print("Right-click the script file and select 'Run as administrator'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    disable_rdp_idle_timeout()
