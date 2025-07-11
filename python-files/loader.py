import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
from PIL import Image, ImageTk
import requests
from io import BytesIO

def get_adb_path():
    possible_paths = [
        r"D:\Program Files\TxGameAssistant\ui\adb.exe",
        os.path.join(os.getcwd(), "adb.exe")
    ]
    return next((path for path in possible_paths if os.path.exists(path)), "adb")

def run_commands_directly():
    try:
        adb_path = get_adb_path()
        commands = [
            "kill-server", "devices", "start-server",
            "push libGVoicePlugin.so /data/data/com.tencent.ig/lib/libGVoicePlugin.so",
            "shell monkey -p com.tencent.ig -c android.intent.category.LAUNCHER 1"
        ]
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        for cmd in commands:
            subprocess.Popen([adb_path] + cmd.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            startupinfo=startupinfo,
                            shell=False).communicate()
        
        messagebox.showinfo("HAXBEY CHEAT", "Successful injection")
    except Exception as e:
        messagebox.showerror("ERORR", f"Erorr: {str(e)}")

def create_window():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("500x300")
    root.config(bg="#404040")
    
    # Pencere pozisyonu
    root.update_idletasks()
    w, h = 500, 300
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    
    # Fotoğrafı direkt olarak haxbeycheat.xyz'den al
    try:
        response = requests.get("https://haxbeycheat.xyz/photo.jpg", timeout=5)
        img = Image.open(BytesIO(response.content)).resize((200, 150), Image.LANCZOS)
        photo_img = ImageTk.PhotoImage(img)
        tk.Label(root, image=photo_img, bg="#404040").place(relx=0.5, rely=0.35, anchor=tk.CENTER)  # Fotoğraf pozisyonu yukarı alındı
    except:
        tk.Frame(root, width=200, height=150, bg="black").place(relx=0.5, rely=0.35, anchor=tk.CENTER)
    
    # HAXBEY CHEAT yazısı (fotoğrafın altında)
    tk.Label(root, text="HAXBEY CHEAT", bg="#404040", fg="white", 
            font=("Arial", 15, "bold")).place(relx=0.5, rely=0.65, anchor=tk.CENTER)  # rely değeri 0.55 yapıldı
    
    # INJECT butonu
    tk.Button(root, text="Inject", command=run_commands_directly,
             bg="#A0A0A0", fg="black", activebackground="#C0C0C0",
             font=("Arial", 9, "bold"), relief=tk.FLAT,
             borderwidth=0, highlightthickness=0, width=15
             ).place(relx=0.5, rely=0.75, anchor=tk.CENTER)  # Buton daha aşağıya alındı
    
    # Kapatma butonu
    tk.Button(root, text="✕", command=root.destroy,
             bg="#606060", fg="white", activebackground="red",
             font=("Arial", 10, "bold"), relief=tk.FLAT,
             borderwidth=0, highlightthickness=0
             ).place(x=460, y=10)
    
    # Pencere taşıma
    root.bind("<B1-Motion>", lambda e: root.geometry(f"+{e.x_root}+{e.y_root}"))
    
    root.mainloop()

if __name__ == "__main__":
    create_window()
