import ctypes, sys, subprocess, tkinter as tk
from tkinter import ttk, messagebox
import os, re, shutil

APP_TITLE = "USB Fix & Format (Thonny-Friendly)"
IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin() != 0

def run(cmd, capture=True):
    try:
        if capture:
            p = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return p.returncode, (p.stdout or "") + (p.stderr or "")
        else:
            p = subprocess.run(cmd, shell=True)
            return p.returncode, ""
    except Exception as e:
        return 1, str(e)

def human_size(bytes_str):
    try:
        b = int(bytes_str)
    except:
        return "N/A"
    units = ["B","KB","MB","GB","TB"]
    i, val = 0, float(b)
    while val >= 1024 and i < len(units)-1:
        val /= 1024.0; i += 1
    return f"{val:.2f} {units[i]}"

def list_removable_drives():
    drives = []
    code, out = run('wmic logicaldisk where "drivetype=2" get DeviceID,VolumeName,Size /format:list')
    if code == 0 and "DeviceID=" in out:
        chunks = [c for c in out.split("\n\n") if c.strip()]
        for c in chunks:
            dev = re.search(r"DeviceID=([A-Z]:)", c)
            size = re.search(r"Size=(\d+)", c)
            vol  = re.search(r"VolumeName=(.*)", c)
            if dev:
                drives.append({
                    "letter": dev.group(1),
                    "size": size.group(1) if size else "0",
                    "label": (vol.group(1).strip() if vol else "") or ""
                })
    return [d for d in drives if os.path.exists(d["letter"] + "\\")]

def get_disk_number_for_letter(letter):
    ps = f"""powershell -NoProfile -Command "(Get-Partition -DriveLetter '{letter[0]}').DiskNumber" """
    code, out = run(ps)
    if code == 0:
        m = re.search(r"(\d+)", out)
        if m:
            return int(m.group(1))
    return None

def diskpart_script(text):
    tmp = os.path.join(os.getenv("TEMP", "."), "dp_script.txt")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    code, out = run(f'diskpart /s "{tmp}"')
    try:
        os.remove(tmp)
    except:
        pass
    return code, out

def format_drive(letter, fs, quick, label):
    q = "/Q" if quick else ""
    lbl = f' /V:"{label}"' if label else ""
    cmd = f'format {letter} /FS:{fs} {q} /Y {lbl}'
    return run(cmd)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("700x520")
        self.resizable(False, False)

        # ==== MENIU SUS ====
        menu_bar = tk.Menu(self)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Despre", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

        frm = ttk.Frame(self, padding=12); frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Unități USB")
        top.pack(fill="x")
        self.tree = ttk.Treeview(top, columns=("letter","label","size"), show="headings", height=5)
        for c, w, t in [("letter",90,"Litră"),("label",230,"Etichetă"),("size",160,"Capacitate")]:
            self.tree.heading(c, text=t); self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="x", padx=6, pady=6)

        btns = ttk.Frame(top); btns.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(btns, text="Reîmprospătează", command=self.refresh).pack(side="left")

        opt = ttk.LabelFrame(frm, text="Opțiuni")
        opt.pack(fill="x", pady=8)
        self.fs_var = tk.StringVar(value="exFAT")
        ttk.Label(opt, text="Sistem fișiere:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Combobox(opt, textvariable=self.fs_var, values=["exFAT","FAT32","NTFS"], state="readonly", width=10).grid(row=0, column=1, sticky="w", padx=6)

        self.quick_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Quick Format", variable=self.quick_var).grid(row=0, column=2, sticky="w", padx=6)

        ttk.Label(opt, text="Etichetă:").grid(row=0, column=3, sticky="e", padx=6)
        self.label_var = tk.StringVar(value="USB")
        ttk.Entry(opt, textvariable=self.label_var, width=18).grid(row=0, column=4, sticky="w", padx=6)

        self.dry_run_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Dry Run (doar afișează scriptul)", variable=self.dry_run_var).grid(row=1, column=0, columnspan=5, sticky="w", padx=6)

        conf = ttk.LabelFrame(frm, text="Confirmare")
        conf.pack(fill="x", pady=8)
        ttk.Label(conf, text="Tastează FORMAT ca să confirmi:").pack(side="left", padx=6)
        self.confirm_var = tk.StringVar()
        ttk.Entry(conf, textvariable=self.confirm_var, width=16).pack(side="left", padx=6)

        actions = ttk.Frame(frm); actions.pack(fill="x", pady=6)
        ttk.Button(actions, text="Repară & Formatează", command=self.repair).pack(side="left")
        ttk.Button(actions, text="Ieșire", command=self.destroy).pack(side="right")

        logf = ttk.LabelFrame(frm, text="Jurnal")
        logf.pack(fill="both", expand=True)
        self.log = tk.Text(logf, height=16, state="disabled")
        self.log.pack(fill="both", expand=True, padx=6, pady=6)

        self.refresh()

    def show_about(self):
        messagebox.showinfo(
            "Despre acest program",
            "Creat de Dragnea Cătălin Nicolae din Târgoviște, România 🇷🇴\n\n"
            "Acest mic program este făcut cu drag pentru toți cei care au nevoie "
            "să-și repare stick-urile USB. Indiferent cine ești, îți mulțumesc că "
            "folosești această aplicație și îți doresc să ai o zi plină de energie "
            "și zâmbete! 💻😊"
        )

    def log_write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        drives = list_removable_drives()
        for d in drives:
            self.tree.insert("", "end", values=(d["letter"], d["label"], human_size(d["size"])))
        if not drives:
            self.log_write("Nu s-au găsit unități USB.")

    def selected_letter(self):
        sel = self.tree.selection()
        if not sel: return None
        vals = self.tree.item(sel[0], "values")
        return vals[0] if vals else None

    def repair(self):
        if not IS_ADMIN:
            messagebox.showwarning(APP_TITLE, "Nu rulezi ca Administrator!\nPoți testa doar Dry Run.\nPentru formatare reală, rulează Thonny ca Administrator.")
        if self.confirm_var.get().strip().upper() != "FORMAT":
            messagebox.showerror(APP_TITLE, "Confirmarea nu corespunde (tastează FORMAT).")
            return

        letter = self.selected_letter()
        if not letter:
            messagebox.showerror(APP_TITLE, "Selectează o unitate.")
            return

        disk_no = get_disk_number_for_letter(letter)
        if disk_no is None:
            messagebox.showerror(APP_TITLE, "Nu pot determina discul fizic.")
            return

        fs = self.fs_var.get()
        quick = self.quick_var.get()
        label = self.label_var.get().strip()
        dry_run = self.dry_run_var.get()

        self.log_write(f"Selectat: {letter} (Disk #{disk_no}) • FS={fs} • Quick={quick} • Label='{label}' • DryRun={dry_run}")

        script = f"""
select disk {disk_no}
attributes disk clear readonly
clean
convert mbr
create partition primary
select partition 1
active
format fs={fs.lower()} {'quick' if quick else ''} label="{label}" unit=64k
assign
exit
""".strip()

        self.log_write("=== DiskPart Script ===")
        self.log_write(script)
        self.log_write("=======================")

        if dry_run or not IS_ADMIN:
            messagebox.showinfo(APP_TITLE, "Dry Run: nimic nu a fost modificat.")
            return

        code, out = diskpart_script(script + "\n")
        self.log_write(out.strip())
        if code != 0:
            messagebox.showerror(APP_TITLE, "A apărut o eroare la diskpart. Vezi jurnalul.")
        else:
            messagebox.showinfo(APP_TITLE, "Operația s-a încheiat.")
        self.refresh()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
    import ctypes, sys, subprocess, tkinter as tk
from tkinter import ttk, messagebox
import os, re, shutil

APP_TITLE = "USB Fix & Format (cu Parolă)"
IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin() != 0
PASSWORD = "1989"  # parola setată

def run(cmd, capture=True):
    try:
        if capture:
            p = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return p.returncode, (p.stdout or "") + (p.stderr or "")
        else:
            p = subprocess.run(cmd, shell=True)
            return p.returncode, ""
    except Exception as e:
        return 1, str(e)

def human_size(bytes_str):
    try:
        b = int(bytes_str)
    except:
        return "N/A"
    units = ["B","KB","MB","GB","TB"]
    i, val = 0, float(b)
    while val >= 1024 and i < len(units)-1:
        val /= 1024.0; i += 1
    return f"{val:.2f} {units[i]}"

def list_removable_drives():
    drives = []
    code, out = run('wmic logicaldisk where "drivetype=2" get DeviceID,VolumeName,Size /format:list')
    if code == 0 and "DeviceID=" in out:
        chunks = [c for c in out.split("\n\n") if c.strip()]
        for c in chunks:
            dev = re.search(r"DeviceID=([A-Z]:)", c)
            size = re.search(r"Size=(\d+)", c)
            vol  = re.search(r"VolumeName=(.*)", c)
            if dev:
                drives.append({
                    "letter": dev.group(1),
                    "size": size.group(1) if size else "0",
                    "label": (vol.group(1).strip() if vol else "") or ""
                })
    return [d for d in drives if os.path.exists(d["letter"] + "\\")]

def get_disk_number_for_letter(letter):
    ps = f"""powershell -NoProfile -Command "(Get-Partition -DriveLetter '{letter[0]}').DiskNumber" """
    code, out = run(ps)
    if code == 0:
        m = re.search(r"(\d+)", out)
        if m:
            return int(m.group(1))
    return None

def diskpart_script(text):
    tmp = os.path.join(os.getenv("TEMP", "."), "dp_script.txt")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    code, out = run(f'diskpart /s "{tmp}"')
    try:
        os.remove(tmp)
    except:
        pass
    return code, out

def format_drive(letter, fs, quick, label):
    q = "/Q" if quick else ""
    lbl = f' /V:"{label}"' if label else ""
    cmd = f'format {letter} /FS:{fs} {q} /Y {lbl}'
    return run(cmd)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("700x520")
        self.resizable(False, False)

        # ==== MENIU SUS ====
        menu_bar = tk.Menu(self)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Despre", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

        frm = ttk.Frame(self, padding=12); frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Unități USB")
        top.pack(fill="x")
        self.tree = ttk.Treeview(top, columns=("letter","label","size"), show="headings", height=5)
        for c, w, t in [("letter",90,"Litră"),("label",230,"Etichetă"),("size",160,"Capacitate")]:
            self.tree.heading(c, text=t); self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="x", padx=6, pady=6)

        btns = ttk.Frame(top); btns.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(btns, text="Reîmprospătează", command=self.refresh).pack(side="left")

        opt = ttk.LabelFrame(frm, text="Opțiuni")
        opt.pack(fill="x", pady=8)
        self.fs_var = tk.StringVar(value="exFAT")
        ttk.Label(opt, text="Sistem fișiere:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Combobox(opt, textvariable=self.fs_var, values=["exFAT","FAT32","NTFS"], state="readonly", width=10).grid(row=0, column=1, sticky="w", padx=6)

        self.quick_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Quick Format", variable=self.quick_var).grid(row=0, column=2, sticky="w", padx=6)

        ttk.Label(opt, text="Etichetă:").grid(row=0, column=3, sticky="e", padx=6)
        self.label_var = tk.StringVar(value="USB")
        ttk.Entry(opt, textvariable=self.label_var, width=18).grid(row=0, column=4, sticky="w", padx=6)

        self.dry_run_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt, text="Dry Run (doar afișează scriptul)", variable=self.dry_run_var).grid(row=1, column=0, columnspan=5, sticky="w", padx=6)

        conf = ttk.LabelFrame(frm, text="Confirmare")
        conf.pack(fill="x", pady=8)
        ttk.Label(conf, text="Tastează FORMAT ca să confirmi:").pack(side="left", padx=6)
        self.confirm_var = tk.StringVar()
        ttk.Entry(conf, textvariable=self.confirm_var, width=16).pack(side="left", padx=6)

        actions = ttk.Frame(frm); actions.pack(fill="x", pady=6)
        ttk.Button(actions, text="Repară & Formatează", command=self.repair).pack(side="left")
        ttk.Button(actions, text="Ieșire", command=self.destroy).pack(side="right")

        logf = ttk.LabelFrame(frm, text="Jurnal")
        logf.pack(fill="both", expand=True)
        self.log = tk.Text(logf, height=16, state="disabled")
        self.log.pack(fill="both", expand=True, padx=6, pady=6)

        self.refresh()

    def show_about(self):
        messagebox.showinfo(
            "Despre acest program",
            "Creat de Dragnea Cătălin Nicolae din Târgoviște, România 🇷🇴\n\n"
            "Acest mic program este făcut cu drag pentru toți cei care au nevoie "
            "să-și repare stick-urile USB. Indiferent cine ești, îți mulțumesc că "
            "folosești această aplicație și îți doresc să ai o zi plină de energie "
            "și zâmbete! 💻😊"
        )

    def log_write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        drives = list_removable_drives()
        for d in drives:
            self.tree.insert("", "end", values=(d["letter"], d["label"], human_size(d["size"])))
        if not drives:
            self.log_write("Nu s-au găsit unități USB.")

    def selected_letter(self):
        sel = self.tree.selection()
        if not sel: return None
        vals = self.tree.item(sel[0], "values")
        return vals[0] if vals else None

    def repair(self):
        if not IS_ADMIN:
            messagebox.showwarning(APP_TITLE, "Nu rulezi ca Administrator!\nPoți testa doar Dry Run.\nPentru formatare reală, rulează aplicația ca Administrator.")
        if self.confirm_var.get().strip().upper() != "FORMAT":
            messagebox.showerror(APP_TITLE, "Confirmarea nu corespunde (tastează FORMAT).")
            return

        letter = self.selected_letter()
        if not letter:
            messagebox.showerror(APP_TITLE, "Selectează o unitate.")
            return

        disk_no = get_disk_number_for_letter(letter)
        if disk_no is None:
            messagebox.showerror(APP_TITLE, "Nu pot determina discul fizic.")
            return

        fs = self.fs_var.get()
        quick = self.quick_var.get()
        label = self.label_var.get().strip()
        dry_run = self.dry_run_var.get()

        self.log_write(f"Selectat: {letter} (Disk #{disk_no}) • FS={fs} • Quick={quick} • Label='{label}' • DryRun={dry_run}")

        script = f"""
select disk {disk_no}
attributes disk clear readonly
clean
convert mbr
create partition primary
select partition 1
active
format fs={fs.lower()} {'quick' if quick else ''} label="{label}" unit=64k
assign
exit
""".strip()

        self.log_write("=== DiskPart Script ===")
        self.log_write(script)
        self.log_write("=======================")

        if dry_run or not IS_ADMIN:
            messagebox.showinfo(APP_TITLE, "Dry Run: nimic nu a fost modificat.")
            return

        code, out = diskpart_script(script + "\n")
        self.log_write(out.strip())
        if code != 0:
            messagebox.showerror(APP_TITLE, "A apărut o eroare la diskpart. Vezi jurnalul.")
        else:
            messagebox.showinfo(APP_TITLE, "Operația s-a încheiat.")
        self.refresh()

# ==== FEREASTRA DE PAROLĂ ====
class PasswordWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Autentificare")
        self.geometry("300x150")
        self.resizable(False, False)

        ttk.Label(self, text="Introdu parola pentru a continua:", font=("Segoe UI", 10)).pack(pady=10)
        self.pass_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.pass_var, show="●", width=20)
        entry.pack(pady=5)
        entry.focus()

        ttk.Button(self, text="OK", command=self.check_password).pack(pady=10)
        self.bind("<Return>", lambda e: self.check_password())

    def check_password(self):
        if self.pass_var.get() == PASSWORD:
            self.destroy()
            main_app = App()
            main_app.mainloop()
        else:
            messagebox.showerror("Eroare", "Parola este incorectă!")

def main():
    pw = PasswordWindow()
    pw.mainloop()

if __name__ == "__main__":
    main()
