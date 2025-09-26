import subprocess
import winreg
import os
import tempfile
import sys
import ctypes
import time

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Relaunch the script with administrative privileges."""
    script = sys.argv[0]
    temp_vbs = os.path.join(tempfile.gettempdir(), "getadmin.vbs")
    with open(temp_vbs, "w") as f:
        f.write(f'Set UAC = CreateObject("Shell.Application")\n')
        f.write(f'UAC.ShellExecute "{script}", "", "", "runas", 1\n')
    
    subprocess.run(["cscript", temp_vbs], shell=True)
    os.remove(temp_vbs)
    sys.exit()

def update_registry():
    """Update FortiClient VPN registry settings."""
    print("Updating....30....50....")
    
    try:
        # Delete the Sslvpn key
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Fortinet\FortiClient\Sslvpn")
        except FileNotFoundError:
            pass  # Key doesn't exist, continue

        # Add registry entries
        base_path = r"SOFTWARE\Fortinet\FortiClient\Sslvpn"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, base_path) as key:
            winreg.SetValueEx(key, "log_level_gui", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "log_level_daemon", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "PreferDtlsTunnel", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "no_warn_invalid_cert", 0, winreg.REG_DWORD, 1)

        # Configure CPCE tunnel settings
        tunnel_path = r"SOFTWARE\Fortinet\FortiClient\Sslvpn\Tunnels\CPCE"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, tunnel_path) as key:
            winreg.SetValueEx(key, "Description", 0, winreg.REG_SZ, "")
            winreg.SetValueEx(key, "Server", 0, winreg.REG_SZ, "vpn.cpce-polyu.edu.hk:443")
            winreg.SetValueEx(key, "promptusername", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "promptcertificate", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "ServerCert", 0, winreg.REG_SZ, "1")
            winreg.SetValueEx(key, "dual_stack", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "sso_enabled", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "use_external_browser", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "azure_auto_login", 0, winreg.REG_DWORD, 0)

        print("Update successfully")
        return 0

    except Exception as e:
        print(f"Error updating registry: {e}")
        return 1

def main():
    if not is_admin():
        print("Requesting administrative privileges...")
        run_as_admin()
    else:
        result = update_registry()
        input("Press Enter to continue...")
        sys.exit(result)

if __name__ == "__main__":
    main()