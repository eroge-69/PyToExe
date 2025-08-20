import tkinter as tk
import platform
import psutil
import winreg
a = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion')
t = winreg.QueryValueEx(a, "UBR")[0]
a.Close()
def start_os():
    os_info = {
        "Your see this information because of PosOS running\n"
        "Name": "PosOS",
        "Version": "1.5",        
        "Status": "Running",
        "Features": "All information about your PC and it's OS"
    }
    print("Starting Operating System...")
    for key, value in os_info.items():
        print(f"{key}: {value}")
def get_os_info():
    os_name = platform.system()  
    os_version = platform.version() 
    os_architecture = platform.architecture()  
    return {
        "OS Name": os_name,
        "OS Version": os_version+"."+str(t),
        "OS Architecture": os_architecture
    }
def get_device_info():
    cpu_info = platform.processor()  
    ram_total = psutil.virtual_memory().total  
    disk_total = psutil.disk_usage('/').total  
    return {
        "CPU": cpu_info,
        "RAM Total": ram_total / (1024 ** 3), 
        "Disk Total": disk_total / (1024 ** 3)  
    }
os_information = get_os_info()
device_information = get_device_info()
def open_os_window():
    window = tk.Tk()
    window.title("PosOS 1")
    window.geometry("1080x1920")
    label = tk.Label(window, text='''Welcome to the PosOS\U000000AE!\U0001F44B
  \U0001F600
    
  PosOS\U000000AE
Version: 1.5
Status: Running
Features: All information about your PC and it's OS
    ''', font=("Arial", 21))    
    label.pack(pady=60)
    window.mainloop()
open_os_window( )                     
start_os()
print("OS Information:")
for key, value in os_information.items():
    print(f"{key}: {value}")
print("\nDevice Information:")
for key, value in device_information.items():
    print(f"{key}: {value}")
platform.python_build()
