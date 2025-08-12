#!/usr/bin/env python3
# attou_tk.py - Kacemi ECU Tool (lightweight Tkinter)
import os, sys, shutil, webbrowser, tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

APP_NAME = "Kacemi ECU Tool"
PHONE = "0662223662"
LINKS = {
    "V42_1.2": "https://drive.google.com/file/d/1U8a63AjjvT87Zwffqot47RjQUdWjeVuW/view?usp=drivesdk",
    "V42_1.6": "https://drive.google.com/file/d/1U4_4bDTgXZRva0iimcgacIMXtTgLb1ec/view?usp=drivesdk",
    "EMS3132_1.4": "https://drive.google.com/file/d/1U0mzFJQBy9Zz8Lj64iexAN7EUyXfPZ1C/view?usp=drivesdk",
    "EMS3132_1.6": "https://drive.google.com/file/d/1U9j9JrQ8EOXJImwQZZmbWrnvCZB6CFwK/view?usp=drivesdk"
}
TEXT = {
    "en":{"title":APP_NAME,"open":"Open / Drag & Drop BIN/ORI","download":"Download samples","current":"Current values:","apply":"Apply (Preview)","save":"Save Modified File","lang":"Language","phone":"Contact: "+PHONE},
    "fr":{"title":APP_NAME,"open":"Ouvrir / Glisser & Déposer BIN/ORI","download":"Télécharger échantillons","current":"Valeurs actuelles:","apply":"Appliquer (Aperçu)","save":"Enregistrer fichier modifié","lang":"Langue","phone":"Contact: "+PHONE},
    "ar":{"title":APP_NAME,"open":"فتح / سحب وإسقاط BIN/ORI","download":"تحميل العينات","current":"القيم الحالية:","apply":"تطبيق (معاينة)","save":"حفظ الملف المعدل","lang":"اللغة","phone":"الاتصال: "+PHONE}
}

import tkinter as tk
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang='en'
        self.title(APP_NAME)
        self.geometry("1000x700")
        self.resizable(False,False)
        # background
        bg_path = os.path.join(os.path.dirname(__file__),"background.png")
        try:
            from PIL import Image, ImageTk
            pil = Image.open(bg_path).resize((1000,700), Image.LANCZOS)
            self.bg = ImageTk.PhotoImage(pil)
            lbl = tk.Label(self, image=self.bg); lbl.place(x=0,y=0,relwidth=1,relheight=1)
        except Exception:
            self.configure(bg="#f7f7f7")
        frame = tk.Frame(self, bg="#ffffff", bd=2, relief="flat"); frame.place(x=20,y=20,width=960,height=660)
        self.title_lbl = tk.Label(frame, text=APP_NAME, fg="#006400", bg="#ffffff", font=("Arial",18,"bold")); self.title_lbl.place(x=20,y=10)
        self.phone_lbl = tk.Label(frame, text=TEXT['en']['phone'], fg="#006400", bg="#ffffff", font=("Arial",10)); self.phone_lbl.place(x=740,y=14)
        tk.Label(frame, text=TEXT['en']['lang'], fg="#006400", bg="#ffffff").place(x=20,y=50)
        self.lang_var = tk.StringVar(value="English")
        self.lang_menu = tk.OptionMenu(frame, self.lang_var, "English","Français","العربية", command=self.change_lang); self.lang_menu.place(x=100,y=46)
        self.open_btn = tk.Button(frame, text=TEXT['en']['open'], bg="#FFD700", fg="black", font=("Arial",11,"bold"), command=self.open_file); self.open_btn.place(x=260,y=46,width=240,height=34)
        self.download_btn = tk.Button(frame, text=TEXT['en']['download'], bg="#FFD700", fg="black", font=("Arial",11,"bold"), command=self.open_download); self.download_btn.place(x=520,y=46,width=160,height=34)
        left = tk.Frame(frame, bg="#ffffff"); left.place(x=20,y=100,width=420,height=540)
        tk.Label(left, text=TEXT['en']['current'], fg="#006400", bg="#ffffff", font=("Arial",12,"bold")).place(x=10,y=10)
        self.cur_text = tk.Text(left, width=48, height=9, bg="#ffffff", fg="#000000"); self.cur_text.place(x=10,y=40)
        # quick buttons
        btns = [("O2 OFF","#006400"),("EGR OFF","#006400"),("FAP OFF","#006400"),("Stage 1","#006400"),("Vmax OFF","#006400")]
        y=240
        for (t,c) in btns:
            b=tk.Button(left, text=t,bg=c,fg="white",font=("Arial",10,"bold"), command=lambda x=t: self.placeholder(x))
            b.place(x=10 if y==240 else 140,y=y,width=120,height=36)
            if y==240: y+=44
            else:
                y+=46
                if y>320: y=290
        tk.Label(left, text="Fan temps (°C)", fg="#006400", bg="#ffffff", font=("Arial",12,"bold")).place(x=10,y=400)
        self.f1 = tk.IntVar(value=88); self.f2 = tk.IntVar(value=92)
        tk.Spinbox(left, from_=30, to=150, textvariable=self.f1, width=6).place(x=10,y=430)
        tk.Spinbox(left, from_=30, to=150, textvariable=self.f2, width=6).place(x=110,y=430)
        self.apply_btn = tk.Button(left, text=TEXT['en']['apply'], bg="#FFD700", fg="black", font=("Arial",10,"bold"), command=self.apply); self.apply_btn.place(x=200,y=430,width=120,height=30)
        self.save_btn = tk.Button(left, text=TEXT['en']['save'], bg="#FFD700", fg="black", font=("Arial",10,"bold"), command=self.save); self.save_btn.place(x=10,y=480,width=400,height=36)
        right = tk.Frame(frame, bg="#ffffff"); right.place(x=460,y=100,width=480,height=540)
        tk.Label(right, text="Engine Info", fg="#006400", bg="#ffffff", font=("Arial",12,"bold")).place(x=10,y=10)
        self.info = tk.Text(right, width=56, height=10, bg="#ffffff", fg="#000000"); self.info.place(x=10,y=40)
        tk.Label(right, text="Action Log", fg="#006400", bg="#ffffff", font=("Arial",12,"bold")).place(x=10,y=260)
        self.log = tk.Text(right, width=56, height=10, bg="#ffffff", fg="#000000"); self.log.place(x=10,y=290)
        self.current_file=None; self.data=None; self.modified=None
    def change_lang(self, choice):
        mapping={"English":"en","Français":"fr","العربية":"ar"}
        self.lang=mapping.get(choice,"en"); t=TEXT[self.lang]
        self.open_btn.config(text=t['open']); self.download_btn.config(text=t['download']); self.apply_btn.config(text=t['apply']); self.save_btn.config(text=t['save']); self.phone_lbl.config(text=t['phone'])
    def open_download(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="V42 1.2", command=lambda: webbrowser.open(LINKS['V42_1.2']))
        menu.add_command(label="V42 1.6", command=lambda: webbrowser.open(LINKS['V42_1.6']))
        menu.add_command(label="EMS3132 1.4", command=lambda: webbrowser.open(LINKS['EMS3132_1.4']))
        menu.add_command(label="EMS3132 1.6", command=lambda: webbrowser.open(LINKS['EMS3132_1.6']))
        try: menu.tk_popup(self.winfo_rootx()+520, self.winfo_rooty()+106)
        finally: menu.grab_release()
    def placeholder(self, name):
        self.log.insert("end", f"Requested action: {name} (placeholder)\\n"); self.log.see("end"); messagebox.showinfo(APP_NAME, f"{name} requested (placeholder).")
    def open_file(self):
        path = filedialog.askopenfilename(title="Open ECU BIN/ORI", filetypes=[("BIN/ORI Files","*.bin *.ori *.hex"),("All files","*.*")])
        if not path: return
        try:
            with open(path,"rb") as f: self.data=bytearray(f.read())
            self.current_file=path; self.modified=bytearray(self.data); self.file_loaded(path)
        except Exception as e: messagebox.showerror(APP_NAME, f"Failed to open file: {e}")
    def file_loaded(self, path):
        name=os.path.basename(path); ecu="Unknown"
        if b"V42" in self.data or b"VALEO" in self.data: ecu="V42"
        elif b"EMS" in self.data or b"3132" in self.data: ecu="EMS3132"
        info=f"Detected: {ecu}\\nFile: {name}\\nSize: {len(self.data)} bytes\\n(Engine fields placeholder)"
        self.info.delete("1.0","end"); self.info.insert("end", info)
        self.cur_text.delete("1.0","end"); self.cur_text.insert("end", "Fan1 ON: -\\nFan1 OFF: -\\nFan2 ON: -\\nFan2 OFF: -")
        self.log.insert("end", f"Loaded {name}; detected {ecu}\\n"); self.log.see("end")
    def apply(self): 
        if not self.data: messagebox.showinfo(APP_NAME, "Open a file first."); return
        f1=self.f1.get(); f2=self.f2.get(); self.modified=bytearray(self.data)
        self.log.insert("end", f"Preview applied: Fan1 ON={f1}, Fan2 ON={f2}\\n"); self.log.see("end"); messagebox.showinfo(APP_NAME, "Preview applied in memory. Use Save to write file.")
    def save(self):
        if self.modified is None: messagebox.showinfo(APP_NAME, "Apply changes first."); return
        save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("BIN files","*.bin"),("All files","*.*")], initialfile=os.path.splitext(self.current_file)[0]+"_mod.bin")
        if not save_path: return
        backup = self.current_file + ".backup.bin"
        try:
            if not os.path.exists(backup): shutil.copy2(self.current_file, backup)
            with open(save_path,"wb") as f: f.write(self.modified)
            self.log.insert("end", f"Saved modified file: {save_path} (backup: {backup})\\n"); self.log.see("end"); messagebox.showinfo(APP_NAME, f"Saved modified file. Backup: {backup}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to save: {e}")

if __name__ == "__main__":
    app = App(); app.mainloop()
