import platform
import subprocess
import csv

CSV_FILE = "system_audit_report.csv"

def run_command(cmd, os_label):
    print(f"\n> {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout.strip() if result.stdout else result.stderr.strip()
        print(output)

        with open(CSV_FILE, mode="a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([os_label, cmd, output])

    except Exception as e:
        print("Exception:", e)
        with open(CSV_FILE, mode="a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([os_label, cmd, f"Exception: {e}"])

def run_windows_11_commands():
    print("Running Windows 11 specific commands...\n")
    os_label = "Windows11"
    commands = [            
        "wmic logicaldisk get DeviceID,Size,FreeSpace",
        "netsh interface show interface",
        "wmic path Win32_PnPEntity where \"Name like '%%Bluetooth%%'\" get Name, Status",
        "sc query schedule",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\cdrom /v Start",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR /v Start",
        "reg query \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\" /v fDenyTSConnections",
        "wmic nicconfig where (IPEnabled=TRUE) get Description, TcpipNetbiosOptions",
        "netstat -an",
        "net share",
        "net user administrator",
        "net user guest",
        "net accounts",
        "net accounts",
        "wmic /namespace:\\\\root\\SecurityCenter2 path AntiVirusProduct get displayName",
        "wmic product get name | findstr /i solidcore",
        "wmic qfe list brief",
        "dir \"C:\\Program Files\" /s /T:W | findstr /i \"definitions\"",
        "powershell Get-MpComputerStatus | findstr \"LastFullScan\"",
        "wevtutil gl security | findstr /i \"retention\"",
        "wevtutil gl security | findstr /i \"maxsize\"",
        "systeminfo | findstr /B /C:\"OS Name\"",
        "wmic computersystem get Manufacturer, Model",
        "wmic bios get version, releasedate",
        "wmic computersystem get TotalPhysicalMemory",
        "wmic OS get FreePhysicalMemory",
        "systeminfo | findstr /C:\"Domain\"",
        "wmic diskdrive get size, caption",
        "wmic logicaldisk get DeviceID, Size, FreeSpace",
        "reg query \"HKCU\\Control Panel\\Desktop\" /v ScreenSaveActive",
        "reg query \"HKCU\\Control Panel\\Desktop\" /v ScreenSaveTimeOut",
        "net share",
        "net accounts",
        "net accounts"
    ]
    for cmd in commands:
        run_command(cmd, os_label)

def run_windows_xp_commands():
    print("Running Windows XP specific commands...\n")
    os_label = "WindowsXP"
    commands = [
        "wmic logicaldisk get deviceid, freespace, size",
        "netsh interface set interface",
        "sc query schedule",
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Cdrom" /v Start',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v Start',
        'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections',
        'wmic nicconfig where (IPEnabled=TRUE) get Description, TcpipNetbiosOptions',
        "netstat -an",
        "net share",
        "net user Administrator",
        "net user Guest",
        "net accounts",
        "net accounts",
        'wmic /namespace:\\root\\SecurityCenter path AntiVirusProduct get displayName',
        'wmic product get name | findstr /i solidcore',
        'systeminfo | find "Hotfix"',
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Eventlog\\Security" /v Retention',
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Eventlog\\Security"',
        "wmic os get Caption,CSDVersion /value",
        "wmic computersystem get manufacturer, model",
        "wmic bios get version, releasedate",
        "wmic computersystem get TotalPhysicalMemory",
        "wmic OS get FreePhysicalMemory",
        'systeminfo | findstr /C:"Domain"',
        "wmic diskdrive get size,caption",
        "wmic logicaldisk get deviceid, freespace, size",
        'reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaveActive',
        'reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaveTimeOut',
        "net share",
        "net accounts",
        "net accounts"
    ]
    for cmd in commands:
        run_command(cmd, os_label)

def run_windows_server_2003_commands():
    print("Running Windows Server 2003 commands...\n")
    os_label = "Server2003"
    commands = [
        "wmic logicaldisk get DeviceID,Size,FreeSpace",
        "netsh interface show interface",
        "wmic path Win32_PnPEntity where \"Name like '%%Bluetooth%%'\" get Name, Status",
        "sc query schedule",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\cdrom /v Start",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR /v Start",
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections',
        "wmic nicconfig where (IPEnabled=TRUE) get Description, TcpipNetbiosOptions",
        "netstat -an",
        "net share",
        "net user administrator",
        "net user guest",
        "net accounts",
        "net accounts",
        'wmic /namespace:\\root\\SecurityCenter path AntiVirusProduct get displayName',
        'wmic product get name | findstr /i solidcore',
        'wmic qfe list brief',
        'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Eventlog\\Security" /v Retention',
        'eventquery /l security /v | findstr /i "Maximum"',
        'systeminfo | findstr /B /C:"OS Name"',
        'wmic computersystem get Manufacturer,Model',
        'wmic bios get version, releasedate',
        'wmic computersystem get TotalPhysicalMemory',
        'wmic os get FreePhysicalMemory',
        'systeminfo | findstr /C:"Domain"',
        'wmic diskdrive get Size,Caption',
        'wmic logicaldisk get DeviceID,Size,FreeSpace',
        'reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaveActive',
        'reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaveTimeOut',
        'net share',
        'net accounts',
        'net accounts'
    ]
    for cmd in commands:
        run_command(cmd, os_label)

def run_windows_7_8_10_vista_commands():
    print("Running Windows 7/8/10/Vista commands...\n")
    os_label = "Win7to10"
    commands = [
        "wmic logicaldisk get DeviceID,Size,FreeSpace",
        "netsh interface show interface",
        "wmic path Win32_PnPEntity where \"Name like '%%Bluetooth%%'\" get Name, Status",
        "sc query schedule",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\cdrom /v Start",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR /v Start",
        "reg query \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\" /v fDenyTSConnections",
        "wmic nicconfig where (IPEnabled=TRUE) get Description, TcpipNetbiosOptions",
        "netstat -an",
        "net share",
        "net user administrator",
        "net user guest",
        "net accounts",
        "net accounts",
        "wmic /namespace:\\root\\SecurityCenter2 path AntiVirusProduct get displayName",
        "wmic product get name | findstr /i solidcore",
        "wmic qfe list brief /format:table",
        "wevtutil gl security | findstr /i \"retention\"",
        "wevtutil gl security | findstr /i \"maxsize\"",
        "systeminfo | findstr /B /C:\"OS Name\"",
        "wmic computersystem get Manufacturer,Model",
        "wmic bios get version, releasedate",
        "wmic computersystem get TotalPhysicalMemory",
        "wmic OS get FreePhysicalMemory",
        "systeminfo | findstr /C:\"Domain\"",
        "wmic diskdrive get size, caption",
        "wmic logicaldisk get DeviceID,Size,FreeSpace",
        "reg query \"HKCU\\Control Panel\\Desktop\" /v ScreenSaveActive",
        "reg query \"HKCU\\Control Panel\\Desktop\" /v ScreenSaveTimeOut",
        "net share",
        "net accounts",
        "net accounts"
    ]
    for cmd in commands:
        run_command(cmd, os_label)

def run_server_2008_plus_commands():
    print("Running Windows Server 2008/2012/2016/2019/2022 commands...\n")
    os_label = "Server2008plus"
    commands = [
        "wmic logicaldisk get DeviceID,Size,FreeSpace",
        "netsh interface show interface",
        "wmic path Win32_PnPEntity where \"Name like '%%Bluetooth%%'\" get Name, Status",
        "sc query schedule",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\cdrom /v Start",
        "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR /v Start",
        "reg query \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\" /v fDenyTSConnections",
        "wmic nicconfig where (IPEnabled=TRUE) get Description, TcpipNetbiosOptions",
        "netstat -an",
        "net share",
        "net user administrator",
        "net user guest",
        "net accounts",
        "net accounts",
        "wmic /namespace:\\root\\SecurityCenter2 path AntiVirusProduct get displayName",
        "wmic product get name | findstr /i solidcore",
        "wmic qfe list brief",
        "dir /T:W \"C:\\ProgramData\\AV Folder\\Definitions\"",
        "wevtutil gl security | findstr /i \"retention\"",
        "wevtutil gl security | findstr /i \"maxsize\"",
        "systeminfo | findstr /B /C:\"OS Name\"",
        "wmic computersystem get Manufacturer,Model",
        "wmic bios get version, releasedate",
        "wmic computersystem get TotalPhysicalMemory",
        "wmic OS get FreePhysicalMemory",
        "systeminfo | findstr /C:\"Domain\"",
        "wmic diskdrive get size, caption",
        "wmic logicaldisk get DeviceID,Size,FreeSpace",
        "reg query \"HKCU\\Control Panel\\Desktop\" /v ScreenSaveActive",
        "reg query \"HKCU\\Control Panel\\Desktop\" /v ScreenSaveTimeOut",
        "net share",
        "net accounts",
        "net accounts"
    ]
    for cmd in commands:
        run_command(cmd, os_label)

def detect_windows_version():
    if platform.system() != "Windows":
        return "Non-Windows"

    release, version, _, _ = platform.win32_ver()
    build_number = int(version.split('.')[2]) if version.count('.') >= 2 else 0

    if release == "2003Server":
        return "Server2003"
    elif release == "XP":
        return "WindowsXP"
    elif release in ["2008Server", "2012Server", "2016Server", "2019Server", "2022Server"]:
        return "Server2008plus"
    elif build_number >= 22000:
        return "Windows11"
    elif release in ["10", "8", "7", "Vista"]:
        return "Win7to10"
    else:
        return "Unsupported"

def main():
    with open(CSV_FILE, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["OS", "Command", "Output"])

    os_version = detect_windows_version()
    print(f"Detected OS version category: {os_version}")

    if os_version == "Server2008plus":
        run_server_2008_plus_commands()
    elif os_version == "Windows11":
        run_windows_11_commands()
    elif os_version == "Win7to10":
        run_windows_7_8_10_vista_commands()
    elif os_version == "WindowsXP":
        run_windows_xp_commands()
    elif os_version == "Server2003":
        run_windows_server_2003_commands()
    else:
        print("Unsupported OS or non-Windows platform.")

if __name__ == "__main__":
    main()