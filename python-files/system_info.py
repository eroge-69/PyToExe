import psutil
import socket
import platform
import os
import pandas as pd

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_hostname():
    return socket.gethostname()

def get_os_info():
    return platform.platform()

def get_ram_info():
    ram = psutil.virtual_memory()
    return ram.total / (1024 ** 3)  # Convert bytes to GB

def get_storage_info():
    partitions = psutil.disk_partitions()
    storage_info = []
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        storage_info.append({
            'Device': partition.device,
            'Total Size (GB)': usage.total / (1024 ** 3),
            'Free Space (GB)': usage.free / (1024 ** 3)
        })
    return storage_info

def get_usb_status():
    # This is a placeholder; actual implementation may vary
    return "USB status check not implemented"

def get_antivirus_status():
    # This is a placeholder; actual implementation may vary
    return "Antivirus status check not implemented"

def get_temp_folder_info():
    temp_folder = os.environ['TEMP']
    temp_size = sum(os.path.getsize(os.path.join(temp_folder, f)) for f in os.listdir(temp_folder) if os.path.isfile(os.path.join(temp_folder, f)))
    is_clean = temp_size < 1024 * 1024  # Less than 1 MB considered clean
    return temp_folder, temp_size / (1024 ** 2), is_clean  # Size in MB

def main():
    data = {
        'IP Address': get_ip_address(),
        'Hostname': get_hostname(),
        'OS Info': get_os_info(),
        'RAM (GB)': get_ram_info(),
        'Storage Info': get_storage_info(),
        'USB Status': get_usb_status(),
        'Antivirus Status': get_antivirus_status(),
        'Temp Folder': get_temp_folder_info()[0],
        'Temp Size (MB)': get_temp_folder_info()[1],
        'Temp Folder Clean': get_temp_folder_info()[2]
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Export to Excel
    df.to_excel('system_info.xlsx', index=False)

if __name__ == "__main__":
    main()
