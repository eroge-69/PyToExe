import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext

# ADB Detect
def adb_detect():
    try:
        subprocess.run(["adb", "kill-server"], check=True)
        subprocess.run(["adb", "start-server"], check=True)
        messagebox.showinfo("ADB Detect", "ADB server restarted.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restart ADB:\n{e}")

# ADB Read Info
def read_info():
    try:
        devices_output = subprocess.check_output(["adb", "devices"], universal_newlines=True)
        info_output = subprocess.check_output(["adb", "shell", "getprop"], universal_newlines=True)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Devices:\n" + devices_output + "\nInfo:\n" + info_output)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read info:\n{e}")

# FRP Bypass (placeholder)
def frp_bypass():
    output_text.insert(tk.END, "FRP Bypass function will be added here...\n")

# Flashing (placeholder)
def flash_device():
    output_text.insert(tk.END, "Flashing function will be added here...\n")

# Read NV File (save to file)
def read_nv_file():
    try:
        output = subprocess.check_output(["adb", "shell", "dd if=/dev/block/bootdevice/by-name/nvram"], stderr=subprocess.STDOUT)
        with open("nv_backup.img", "wb") as f:
            f.write(output)
        output_text.insert(tk.END, "NV File saved as nv_backup.img\n")
    except Exception as e:
        output_text.insert(tk.END, f"Failed to read NV file: {e}\n")

# Read NV Data (print to screen)
def read_nv_data():
    try:
        output = subprocess.check_output(["adb", "shell", "strings /dev/block/bootdevice/by-name/nvram"], universal_newlines=True)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "NV Data:\n" + output)
    except Exception as e:
        output_text.insert(tk.END, f"Failed to read NV Data: {e}\n")

# GUI
window = tk.Tk()
window.title("ZMT PRO")
window.geometry("730x520")

label = tk.Label(window, text="ZMT PRO - Mobile Tool", font=("Arial", 16, "bold"))
label.pack(pady=10)

frame1 = tk.Frame(window)
frame1.pack(pady=5)

btn_detect = tk.Button(frame1, text="ADB DETECT", command=adb_detect, font=("Arial", 11), bg="green", fg="white", width=15)
btn_detect.grid(row=0, column=0, padx=5)

btn_info = tk.Button(frame1, text="READ INFO", command=read_info, font=("Arial", 11), bg="blue", fg="white", width=15)
btn_info.grid(row=0, column=1, padx=5)

frame2 = tk.Frame(window)
frame2.pack(pady=5)

btn_frp = tk.Button(frame2, text="FRP BYPASS", command=frp_bypass, font=("Arial", 11), bg="#e91e63", fg="white", width=15)
btn_frp.grid(row=0, column=0, padx=5)

btn_flash = tk.Button(frame2, text="FLASH", command=flash_device, font=("Arial", 11), bg="#9c27b0", fg="white", width=15)
btn_flash.grid(row=0, column=1, padx=5)

btn_nvfile = tk.Button(frame2, text="READ NV FILE", command=read_nv_file, font=("Arial", 11), bg="#3f51b5", fg="white", width=15)
btn_nvfile.grid(row=0, column=2, padx=5)

btn_nvdata = tk.Button(frame2, text="READ NV DATA", command=read_nv_data, font=("Arial", 11), bg="#009688", fg="white", width=15)
btn_nvdata.grid(row=0, column=3, padx=5)

output_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=90, height=18)
output_text.pack(pady=10)

window.mainloop()
