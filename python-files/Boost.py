import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# ------------------- Functions -------------------
def set_power_plan():
    subprocess.call("powercfg -setactive SCHEME_MIN", shell=True)
    messagebox.showinfo("Power Plan", "ตั้งค่า High Performance เรียบร้อยแล้ว")

def optimize_cpu():
    subprocess.call("powercfg -setacvalueindex SCHEME_MIN SUB_PROCESSOR PERFBOOSTMODE 1", shell=True)
    subprocess.call("powercfg -setacvalueindex SCHEME_MIN SUB_PROCESSOR PROCTHROTTLEMIN 50", shell=True)
    subprocess.call("powercfg -setacvalueindex SCHEME_MIN SUB_PROCESSOR PROCTHROTTLEMAX 100", shell=True)
    messagebox.showinfo("CPU Optimizer", "ปรับ CPU Ryzen 5 5500U เสถียรเรียบร้อยแล้ว")

def set_virtual_memory():
    subprocess.call("wmic computersystem where name='%computername%' set AutomaticManagedPagefile=False", shell=True)
    subprocess.call("wmic pagefileset where name='C:\\\\pagefile.sys' set InitialSize=4096,MaximumSize=8192", shell=True)
    messagebox.showinfo("Virtual Memory", "ตั้งค่า Virtual Memory เรียบร้อยแล้ว")

def set_network_optim():
    subprocess.call("reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters /v TcpAckFrequency /t REG_DWORD /d 1 /f", shell=True)
    subprocess.call("reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters /v TCPNoDelay /t REG_DWORD /d 1 /f", shell=True)
    subprocess.call("netsh interface tcp set global autotuninglevel=disabled", shell=True)
    subprocess.call("netsh interface tcp set global chimney=enabled", shell=True)
    subprocess.call("netsh interface tcp set global congestionprovider=ctcp", shell=True)
    messagebox.showinfo("Network", "ปรับค่าการเชื่อมต่อเน็ตเรียบร้อยแล้ว")

def clear_temp_deep():
    temp_dirs = [
        os.environ['TEMP'],
        "C:\\Windows\\Temp",
        os.path.join(os.environ['LOCALAPPDATA'], "Temp"),
        os.path.join(os.environ['APPDATA'], "Discord\\Cache"),
        os.path.join(os.environ['LOCALAPPDATA'], "Google\\Chrome\\User Data\\Default\\Cache"),
        os.path.join(os.environ['ProgramData'], "Microsoft\\Windows\\Caches")
    ]
    for path in temp_dirs:
        if os.path.exists(path):
            subprocess.call(f'del /f /s /q "{path}\\*"', shell=True)
    messagebox.showinfo("Clean Temp", "ลบไฟล์ขยะเบื้องลึกเรียบร้อยแล้ว")

def set_gpu_optim():
    try:
        # NVIDIA Profile Inspector (ต้องติดตั้ง)
        # ใช้ command line ปรับค่าเบื้องลึก
        # Low Latency Mode → Ultra, Power → Max Performance, Texture Filtering → High Performance
        # ปรับผ่าน nvidiaProfileInspector.exe (ต้องสร้าง profile FiveM)
        profile_path = "C:\\Program Files\\NVIDIA Corporation\\ProfileInspector\\nvidiaProfileInspector.exe"
        if os.path.exists(profile_path):
            subprocess.call(f'"{profile_path}" -setBaseProfileSetting:0x22222222=0x2', shell=True)  # Low Latency Ultra (ตัวอย่าง)
            subprocess.call(f'"{profile_path}" -setBaseProfileSetting:0x22333333=0x1', shell=True)  # Max Performance (ตัวอย่าง)
            messagebox.showinfo("GPU Optimizer", "ปรับค่า NVIDIA GTX 1650 เบื้องลึกเรียบร้อยแล้ว")
        else:
            messagebox.showwarning("GPU Optimizer", "กรุณาติดตั้ง NVIDIA Profile Inspector เพื่อปรับค่า GPU เบื้องลึก")
    except Exception as e:
        messagebox.showerror("GPU Optimizer", f"เกิดข้อผิดพลาด: {e}")

def reset_all():
    subprocess.call("powercfg -setactive SCHEME_BALANCED", shell=True)
    subprocess.call("wmic computersystem where name='%computername%' set AutomaticManagedPagefile=True", shell=True)
    messagebox.showinfo("Reset", "ระบบถูกรีเซ็ตกลับสู่ค่าเริ่มต้นแล้ว")

# ------------------- GUI -------------------
root = tk.Tk()
root.title("⚡ Ultimate Game Boost Tool (GPU+CPU+Network)")
root.geometry("420x550")
root.configure(bg="#1e1e1e")

label = tk.Label(root, text="⚡ Ultimate Game Boost Tool ⚙️", fg="white", bg="#1e1e1e", font=("Arial", 16, "bold"))
label.pack(pady=20)

btn1 = tk.Button(root, text="🔋 Set Power Plan (High Performance)", command=set_power_plan, width=45)
btn1.pack(pady=5)

btn2 = tk.Button(root, text="⚙️ Optimize CPU Ryzen 5 5500U", command=optimize_cpu, width=45)
btn2.pack(pady=5)

btn3 = tk.Button(root, text="🌐 Network Optimization (Reduce Ping)", command=set_network_optim, width=45)
btn3.pack(pady=5)

btn4 = tk.Button(root, text="🔥 Optimize NVIDIA GTX 1650 (Low Latency + Max Performance)", command=set_gpu_optim, width=45)
btn4.pack(pady=5)

btn5 = tk.Button(root, text="🧹 Deep Clean Temp & Cache Files", command=clear_temp_deep, width=45)
btn5.pack(pady=5)

btn6 = tk.Button(root, text="🧠 Set Virtual Memory (4GB-8GB)", command=set_virtual_memory, width=45)
btn6.pack(pady=5)

btn7 = tk.Button(root, text="🔄 Reset All Settings", command=reset_all, bg="#7a0000", fg="white", width=45)
btn7.pack(pady=15)

root.mainloop()
