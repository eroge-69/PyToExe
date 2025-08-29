import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# ระบุ path ที่เก็บไฟล์ (ตอนใช้งานจริงเปลี่ยนเป็น path ของคุณ)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ไฟล์ทั้งหมดที่คุณส่งมา
batch_files = [
    "Ghost.bat",
    "Set1.bat",
    "Set2.bat",
    "Uninstall_Ghost.bat",
    "RESET.cmd",
    "Network_fix.bat"
]

reg_files = [
    "Key.reg",
    "mousekeyStepha.reg",
    "MouseStepha.reg",
    "SETTING 1-1.reg",
    "SETTING TEAM.reg",
    "Stepha.reg",
    "default.reg",
    "default2.reg"
]

# ฟังก์ชันรัน batch/cmd
def run_batch(file):
    try:
        filepath = os.path.join(BASE_DIR, file)
        subprocess.run(["cmd", "/c", filepath], check=True)
        messagebox.showinfo("🎉 สำเร็จ", f"รัน {file} เสร็จสิ้น")
    except Exception as e:
        messagebox.showerror("😢 ผิดพลาด", f"รัน {file} ไม่ได้\n{e}")

# ฟังก์ชัน import reg
def run_reg(file):
    try:
        filepath = os.path.join(BASE_DIR, file)
        subprocess.run(["reg", "import", filepath], check=True)
        messagebox.showinfo("🎉 สำเร็จ", f"นำเข้า {file} เรียบร้อย")
    except Exception as e:
        messagebox.showerror("😢 ผิดพลาด", f"นำเข้า {file} ไม่ได้\n{e}")

# ---------- GUI ----------
root = tk.Tk()
root.title("🌸 System Tools GUI น่ารักๆ 🌸")
root.geometry("540x680")
root.config(bg="#fdfdff")  # พื้นหลังขาวอมฟ้า

font_btn = ("Comic Sans MS", 11, "bold")

# ส่วน Batch
frame_batch = tk.LabelFrame(root, text="🖥️⚡ Batch / CMD", padx=10, pady=10, bg="#ffe4f1", fg="#d63384", font=("Comic Sans MS", 12, "bold"))
frame_batch.pack(fill="both", expand="yes", padx=10, pady=10)

for f in batch_files:
    btn = tk.Button(frame_batch, text=f"🖥️ {f}", font=font_btn, width=42,
                    bg="#ffb6c1", fg="black", relief="raised", bd=3,
                    activebackground="#ff69b4", activeforeground="white",
                    command=lambda file=f: run_batch(file))
    btn.pack(pady=4)

# ส่วน Registry
frame_reg = tk.LabelFrame(root, text="🔑📋 Registry (.reg)", padx=10, pady=10, bg="#e6ffe6", fg="#2e8b57", font=("Comic Sans MS", 12, "bold"))
frame_reg.pack(fill="both", expand="yes", padx=10, pady=10)

for f in reg_files:
    btn = tk.Button(frame_reg, text=f"🔑 {f}", font=font_btn, width=42,
                    bg="#98fb98", fg="black", relief="raised", bd=3,
                    activebackground="#3cb371", activeforeground="white",
                    command=lambda file=f: run_reg(file))
    btn.pack(pady=4)

# Label footer
footer = tk.Label(root, text="✨ Made with Love ✨", bg="#fdfdff", fg="#ff69b4", font=("Comic Sans MS", 11, "italic"))
footer.pack(pady=12)

root.mainloop()
