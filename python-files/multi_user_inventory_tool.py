import csv
import time
import threading
import wmi

CREDENTIALS = [
    ("activesourcing0.org\\Administrator", "TIKPTOLPTF@225"),
    ("Administrator", "TIKPTOLPTF@225"),
    # Add more (username, password) as needed
]

def get_remote_info(ip):
    for user, pwd in CREDENTIALS:
        try:
            conn = wmi.WMI(computer=ip, user=user, password=pwd)
            os_info = conn.Win32_OperatingSystem()[0]
            cs = conn.Win32_ComputerSystem()[0]
            bios = conn.Win32_BIOS()[0]
            processor = conn.Win32_Processor()[0]
            ram = sum(int(mem.Capacity) for mem in conn.Win32_PhysicalMemory())
            ram_gb = round(ram / (1024**3), 2)
            video = conn.Win32_VideoController()[0]
            disk = conn.Win32_DiskDrive()[0]
            net = conn.Win32_NetworkAdapterConfiguration(IPEnabled=True)[0]
            total_disk_size = round(sum(int(d.Size) for d in conn.Win32_LogicalDisk() if d.Size), 2)

            return {
                "S.NO": "", "EMP_CODE": "", "NAME": "", "EMAIL ID": "",
                "USER_NAME": cs.UserName or "", "PASSWORD": "", "DEPARTMENT": "",
                "COMPUTER_NAME": cs.Name, "Admin_Password": pwd, "BRAND": cs.Manufacturer,
                "PROCESSOR": processor.Name.strip(), "GRAPHIC_CARD": video.Description,
                "GRAPHIC_CARD_MODEL": video.Name, "GRAPHIC_CARD_SIZE": round((int(video.AdapterRAM or 0)) / (1024**2), 2),
                "SSD": "Yes" if "SSD" in disk.Model.upper() else "No",
                "HARD DRIVE": disk.Model, "DISK_SIZE": total_disk_size,
                "RAM": ram_gb, "WINDOWS": f"{os_info.Caption} {os_info.Version}",
                "WINDOWS_SERIAL": bios.SerialNumber.strip(), "MAC_ADDRESS": net.MACAddress,
                "IP_ADDRESS": ip, "COMPUTER_TYPE": "Laptop" if "laptop" in cs.SystemType.lower() else "Desktop",
                "BATTERY_PRESENT": "Yes" if conn.Win32_Battery() else "No",
                "TOUCH_SUPPORT": "No", "OUTLOOK_EMAIL_ID": "", "ERROR": ""
            }
        except Exception as e:
            last_error = str(e)
    return {
        "S.NO": "", "EMP_CODE": "", "NAME": "", "EMAIL ID": "", "USER_NAME": "",
        "PASSWORD": "", "DEPARTMENT": "", "COMPUTER_NAME": "", "Admin_Password": "",
        "BRAND": "", "PROCESSOR": "", "GRAPHIC_CARD": "", "GRAPHIC_CARD_MODEL": "",
        "GRAPHIC_CARD_SIZE": "", "SSD": "", "HARD DRIVE": "", "DISK_SIZE": "",
        "RAM": "", "WINDOWS": "", "WINDOWS_SERIAL": "", "MAC_ADDRESS": "", "IP_ADDRESS": ip,
        "COMPUTER_TYPE": "", "BATTERY_PRESENT": "", "TOUCH_SUPPORT": "",
        "OUTLOOK_EMAIL_ID": "", "ERROR": last_error
    }

def write_info(ip, output_file, fieldnames, lock):
    info = get_remote_info(ip)
    with lock:
        with open(output_file, "a", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(info)

def scan_network():
    output_file = "NetworkInventory_Full.csv"
    fieldnames = [
        "S.NO", "EMP_CODE", "NAME", "EMAIL ID", "USER_NAME", "PASSWORD", "DEPARTMENT",
        "COMPUTER_NAME", "Admin_Password", "BRAND", "PROCESSOR", "GRAPHIC_CARD",
        "GRAPHIC_CARD_MODEL", "GRAPHIC_CARD_SIZE", "SSD", "HARD DRIVE", "DISK_SIZE", "RAM",
        "WINDOWS", "WINDOWS_SERIAL", "MAC_ADDRESS", "IP_ADDRESS", "COMPUTER_TYPE",
        "BATTERY_PRESENT", "TOUCH_SUPPORT", "OUTLOOK_EMAIL_ID", "ERROR"
    ]
    with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    threads = []
    lock = threading.Lock()

    for i in range(0, 16):  # 192.168.0.1 to 192.168.15.254
        for j in range(1, 255):
            ip = f"192.168.{i}.{j}"
            t = threading.Thread(target=write_info, args=(ip, output_file, fieldnames, lock))
            threads.append(t)
            t.start()
            time.sleep(0.01)  # avoid overload

    for t in threads:
        t.join()

if __name__ == "__main__":
    scan_network()
