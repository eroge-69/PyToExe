import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import os
import subprocess
from itertools import cycle

# === 1. YO‘LLAR ===
image_folder = r"F:\Digital Forensic\AutoPlay\Images"
background_image_path = os.path.join(image_folder, "747.jpg")  # yangi yuklangan fon rasmi

# === 2. DASTUR YO‘LLARI ===
tool_paths = {
    "ИНСТРУКЦИЯ": r"F:\Digital Forensic\AutoPlay\Docs\ИНСТРУКЦИЯ_.pdf",  # .pdf
    "Autopsy": r"F:\Digital Forensic\AutoPlay\Docs\Autopsy\bin\autopsy64.exe",
    "BrowsingHistoryView": r"F:\Digital Forensic\AutoPlay\Docs\BrowsingHistoryView\BrowsingHistoryView.exe",
    "DumpIt": r"F:\Digital Forensic\AutoPlay\Docs\DumpIt\DumpIt.exe",
    "FTK Imager": r"F:\Digital Forensic\AutoPlay\Docs\FTK Imager\FTK Imager.exe",
    "Hash calculator": r"F:\Digital Forensic\AutoPlay\Docs\Hash calculator\QuickHash.exe",
    "Lightshots": r"F:\Digital Forensic\AutoPlay\Docs\Lightshots\Lightshot.exe",
    "Magnet": r"F:\Digital Forensic\AutoPlay\Docs\Magnet\MagnetRESPONSE.exe",
    "osTriage2": r"F:\Digital Forensic\AutoPlay\Docs\osTriage2\osTriage2.exe",
    "USB-Devview": r"F:\Digital Forensic\AutoPlay\Docs\USB-Devview\USBDeview\USBDeview.exe",
    "USB-Devview 86": r"F:\Digital Forensic\AutoPlay\Docs\USB-Devview\USBDeviewx86\USBDeview.exe",
    "Wireshark": r"F:\Digital Forensic\AutoPlay\Docs\Wireshark\WiresharkPortable64.exe"
}

# === 3. ASOSIY OYNA ===
root = tk.Tk()
root.title("Digital Forensics Panel")
root.geometry("1000x700")
root.resizable(False, False)


# === 4. ORQA FON RASMI ===
try:
    bg_image = Image.open(background_image_path).resize((1000, 700))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print(f"[!] Orqa fon rasm yuklab bo'lmadi: {e}")
    root.configure(bg="black")

# === LOGO (Yuqoriga markazga) ===
logo_path = r"F:\Digital Forensic\AutoPlay\logo.png"
try:
    logo_image = Image.open(logo_path).resize((120, 120))
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo, bg="white")
    logo_label.image = logo_photo
    logo_label.place(x=100, y=10)
except Exception as e:
    print(f"[!] Logo yuklanmadi: {e}")

# === 5. SLAYD RASMLAR ===
def get_image_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and f != os.path.basename(background_image_path)]

slideshow_paths = get_image_files(image_folder)
slideshow_label = tk.Label(root)
slideshow_label.place(x=70, y=400, width=300, height=200)

slideshow_cycle = cycle(slideshow_paths)

def update_slideshow():
    try:
        img_path = next(slideshow_cycle)
        img = Image.open(img_path).resize((300, 200))
        img_tk = ImageTk.PhotoImage(img)
        slideshow_label.config(image=img_tk)
        slideshow_label.image = img_tk
    except Exception as e:
        print(f"[!] Slayd rasm yuklashda xato: {e}")
    root.after(3000, update_slideshow)

update_slideshow()

# === 6. DASTUR/TUGMA ISHLATISH ===
def run_tool(path):
    try:
        if path.lower().endswith(".pdf"):
            os.startfile(path)  # PDF uchun
        elif path.lower().endswith(".exe"):
            subprocess.Popen([path], shell=True)  # EXE uchun
        else:
            messagebox.showinfo("Ma'lumot", "Fayl ochish formati noma'lum.")
    except Exception as e:
        messagebox.showerror("Xatolik", f"Faylni ochishda muammo:\n{e}")

# === 7. TUGMALAR PANELI ===
buttons_frame = tk.Frame(root, bg="#e0f7fa")
buttons_frame.place(x=700, y=60)

for idx, (label, path) in enumerate(tool_paths.items()):
    btn = tk.Button(buttons_frame, text=label, width=30,border=5, font=("Cambria", 12, "bold"),
                    command=lambda p=path: run_tool(p), bg="white")
    btn.grid(row=idx, column=0, pady=3)

# === 8. KALENDAR ===
calendar = Calendar(root, selectmode='day', year=2025, month=9, day=12, locale='ru_RU')
calendar.place(x=400, y=400)


footer = tk.Label(root, text="Raqamli kriminalistika ilmiy tadqiqot instituti", font=("Cambria", 12),
                  bg="white", fg="black")
footer.place(x=675, y=670)

# === 11. BOSHLASH ===
root.mainloop()

