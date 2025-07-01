
import wmi
import socket
import uuid
import psutil
import platform
import subprocess
import os

def get_system_info():
    c = wmi.WMI()
    info = {}

    # Serial Number
    for bios in c.Win32_BIOS():
        info["Serial Number"] = bios.SerialNumber.strip()

    # Computer Name
    info["Computer Name"] = socket.gethostname()

    # Username
    info["Username"] = os.getlogin()

    # Domain or Workgroup
    for sys in c.Win32_ComputerSystem():
        info["Domain/Workgroup"] = sys.Domain

    # IP Address
    ip_address = socket.gethostbyname(socket.gethostname())
    info["IP Address"] = ip_address

    # MAC Address
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(0,8*6,8)][::-1])
    info["MAC Address"] = mac_address

    # RAM
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    info["RAM (GB)"] = ram_gb

    # HDD
    hdd_gb = round(psutil.disk_usage('/').total / (1024 ** 3), 2)
    info["HDD (GB)"] = hdd_gb

    # Processor
    info["Processor"] = platform.processor()

    # System Manufacturer and Model
    for cs in c.Win32_ComputerSystem():
        info["System Manufacturer"] = cs.Manufacturer
        info["System Model"] = cs.Model

    # OS Name
    for os_info in c.Win32_OperatingSystem():
        info["OS Name"] = os_info.Caption

    # MS Office Version
    try:
        office_versions = []
        for app in c.Win32_Product():
            if "Microsoft Office" in app.Name:
                office_versions.append(app.Name)
        info["MS Office Version"] = ', '.join(office_versions) if office_versions else "Not Found"
    except:
        info["MS Office Version"] = "Access Denied or Not Installed"

    # External Antivirus
    try:
        antivirus_list = []
        for av in c.root\SecurityCenter2.AntiVirusProduct():
            antivirus_list.append(av.displayName)
        info["External Antivirus"] = ', '.join(antivirus_list) if antivirus_list else "Not Found"
    except:
        info["External Antivirus"] = "Access Denied or Not Installed"

    return info

if __name__ == "__main__":
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
