import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from datetime import datetime
import re
import csv

# Static array capacity
MAX_PARTICIPANTS = 100

@dataclass
class Participant:
    name: str
    email: str
    institution: str
    reg_time: datetime

# Storage
participants = [None] * MAX_PARTICIPANTS
participant_count = 0

# Regex
EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"

# Model Functions

def add_participant(name, email, institution):
    global participant_count
    if participant_count >= MAX_PARTICIPANTS:
        messagebox.showerror("Error", "Kapasitas penuh!")
        return False
    if not re.match(EMAIL_REGEX, email):
        messagebox.showerror("Error", "Format email tidak valid!")
        return False
    for i in range(participant_count):
        if participants[i].email.lower() == email.lower():
            messagebox.showerror("Error", "Email sudah terdaftar!")
            return False
    participants[participant_count] = Participant(name, email, institution, datetime.now())
    participant_count += 1
    return True


def linear_search(keyword, by_email=False): 
    key = keyword.lower()
    return [(i, p) for i, p in enumerate(participants[:participant_count])
            if key in (p.email.lower() if by_email else p.name.lower())]


def linear_search_inst(keyword):
    key = keyword.lower()
    return [(i, p) for i, p in enumerate(participants[:participant_count])
            if key in p.institution.lower()]


def selection_sort(by="name", ascending=True):
    for i in range(participant_count - 1):
        idx = i
        for j in range(i+1, participant_count):
            a, b = participants[idx], participants[j]
            if by == "name":
                comp = b.name.lower() < a.name.lower()
            else:
                comp = b.reg_time < a.reg_time
            if (comp and ascending) or (not comp and not ascending):
                idx = j
        participants[i], participants[idx] = participants[idx], participants[i]


def delete_participant_at(index):
    global participant_count
    for i in range(index, participant_count-1):
        participants[i] = participants[i+1]
    participants[participant_count-1] = None
    participant_count -= 1


def export_csv():
    if participant_count == 0:
        messagebox.showinfo("Export CSV", "Tidak ada data untuk diekspor.")
        return
    fp = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
    if not fp: return
    try:
        with open(fp, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["Nama","Email","Institusi","Waktu Daftar"])
            for p in participants[:participant_count]:
                w.writerow([p.name, p.email, p.institution, p.reg_time.strftime("%Y-%m-%d %H:%M:%S")])
        messagebox.showinfo("Export CSV", "Berhasil diekspor.")
    except Exception as e:
        messagebox.showerror("Error Export", str(e))


def import_csv():
    fp = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
    if not fp: return
    global participant_count, participants
    try:
        with open(fp, newline='', encoding='utf-8') as f:
            rd = csv.DictReader(f)
            participants = [None]*MAX_PARTICIPANTS
            participant_count = 0
            for row in rd:
                if participant_count >= MAX_PARTICIPANTS: break
                t = datetime.strptime(row["Waktu Daftar"], "%Y-%m-%d %H:%M:%S")
                participants[participant_count] = Participant(row["Nama"], row["Email"], row["Institusi"], t)
                participant_count += 1
        update_table()
        messagebox.showinfo("Import CSV", "Berhasil diimpor.")
    except Exception as e:
        messagebox.showerror("Error Import", str(e))


def update_table(data=None):
    table.delete(*table.get_children())
    for idx, p in (data if data is not None else enumerate(participants[:participant_count])):
        table.insert("", "end", iid=idx,
    values=(p.name, p.email, p.institution, p.reg_time.strftime("%Y-%m-%d %H:%M:%S")))
    status_var.set(f"Total peserta: {participant_count}")

# GUI

def main():
    global table, ent_name, ent_email, ent_inst, ent_search, status_var
    root = tk.Tk()
    root.title("Sistem Pendaftaran Event/Seminar")
    # Menu
    mb = tk.Menu(root)
    fm = tk.Menu(mb, tearoff=0)
    fm.add_command(label="Export CSV", command=export_csv)
    fm.add_command(label="Import CSV", command=import_csv)
    fm.add_separator(); fm.add_command(label="Exit", command=root.quit)
    mb.add_cascade(label="File", menu=fm)
    root.config(menu=mb)
    
    # Input
    tf = ttk.LabelFrame(root, text="Form Pendaftaran", padding=10)
    tf.pack(fill="x", padx=10, pady=5)
    labels = [("Nama",0),("Email",1),("Institusi",2)]
    entries = []
    for txt, r in labels:
        ttk.Label(tf, text=f"{txt}:").grid(row=r,column=0,sticky="w", pady=2)
        e = ttk.Entry(tf, width=30); e.grid(row=r,column=1,padx=5,pady=2)
        entries.append(e)
    ent_name, ent_email, ent_inst = entries
    ttk.Button(tf, text="Daftar", command=on_add).grid(row=3,column=0,columnspan=2,pady=5)
    
    # Search & Sort
    sf = ttk.LabelFrame(root, text="Cari & Urut", padding=10)
    sf.pack(fill="x", padx=10, pady=5)
    ent_search = ttk.Entry(sf, width=30); ent_search.grid(row=0,column=0, padx=5)
    ttk.Button(sf, text="Cari Nama", command=lambda: on_search(False)).grid(row=0,column=1,padx=2)
    ttk.Button(sf, text="Cari Email", command=lambda: on_search(True)).grid(row=0,column=2,padx=2)
    ttk.Button(sf, text="Cari Institusi", command=lambda: on_search_inst()).grid(row=0,column=3,padx=2)
    ttk.Button(sf, text="Tampilkan Semua", command=lambda: update_table()).grid(row=0,column=4,padx=5)
    ttk.Button(sf, text="Nama ↑", command=lambda: on_sort("name",True)).grid(row=1,column=0,pady=5)
    ttk.Button(sf, text="Nama ↓", command=lambda: on_sort("name",False)).grid(row=1,column=1)
    ttk.Button(sf, text="Waktu ↑", command=lambda: on_sort("time",True)).grid(row=1,column=2)
    ttk.Button(sf, text="Waktu ↓", command=lambda: on_sort("time",False)).grid(row=1,column=3)

    # Actions
    af = ttk.LabelFrame(root, text="Aksi", padding=10)
    af.pack(fill="x", padx=10, pady=5)
    ttk.Button(af, text="Edit Terpilih", command=on_edit).grid(row=0,column=0,padx=5)
    ttk.Button(af, text="Hapus Terpilih", command=on_delete).grid(row=0,column=1,padx=5)
    ttk.Button(af, text="Export CSV", command=export_csv).grid(row=0,column=2,padx=5)
    ttk.Button(af, text="Import CSV", command=import_csv).grid(row=0,column=3,padx=5)

    # Table
    tfm = ttk.Frame(root, padding=10)
    tfm.pack(fill="both", expand=True, padx=10, pady=5)
    cols = ("Nama","Email","Institusi","Waktu Daftar")
    table = ttk.Treeview(tfm, columns=cols, show="headings")
    for c in cols: table.heading(c,text=c); table.column(c,width=150)
    table.pack(fill="both", expand=True)

    # Status
    status_var = tk.StringVar()
    ttk.Label(root, textvariable=status_var, relief="sunken", anchor="w").pack(fill="x")

    update_table()
    root.mainloop()

# Handlers

def on_add():
    name, email, inst = ent_name.get().strip(), ent_email.get().strip(), ent_inst.get().strip()
    if not (name and email and inst): messagebox.showwarning("Peringatan","Semua kolom harus diisi!"); return
    if add_participant(name,email,inst):
        update_table(); ent_name.delete(0,tk.END); ent_email.delete(0,tk.END); ent_inst.delete(0,tk.END)

def on_search(by_email=False):
    key = ent_search.get().strip()
    update_table(linear_search(key,by_email)) if key else None

def on_search_inst():
    key = ent_search.get().strip()
    update_table(linear_search_inst(key)) if key else None

def on_sort(by,asc):
    selection_sort(by=("name" if by=="name" else "time"),ascending=asc); update_table()

def on_delete():
    sel = table.selection();
    if sel and messagebox.askyesno("Konfirmasi","Hapus peserta ini? "):
        delete_participant_at(int(sel[0])); update_table()


def on_edit():
    sel=table.selection();
    if not sel: return
    idx=int(sel[0]); p=participants[idx]
    w=tk.Toplevel(); w.title("Edit Peserta")
    ttk.Label(w,text="Nama:").grid(row=0,column=0,pady=2)
    e1=ttk.Entry(w); e1.insert(0,p.name); e1.grid(row=0,column=1,pady=2)
    ttk.Label(w,text="Email:").grid(row=1,column=0,pady=2)
    e2=ttk.Entry(w); e2.insert(0,p.email); e2.grid(row=1,column=1,pady=2)
    ttk.Label(w,text="Institusi:").grid(row=2,column=0,pady=2)
    e3=ttk.Entry(w); e3.insert(0,p.institution); e3.grid(row=2,column=1,pady=2)
    def se():
        nn, ee, ii = e1.get().strip(), e2.get().strip(), e3.get().strip()
        if not (nn and ee and ii): messagebox.showwarning("Peringatan","Semua kolom harus diisi!"); return
        if not re.match(EMAIL_REGEX,ee): messagebox.showerror("Error","Email invalid!"); return
        p.name,p.email,p.institution = nn,ee,ii
        update_table(); w.destroy()
    ttk.Button(w,text="Simpan",command=se).grid(row=3,column=0,columnspan=2,pady=5)

if __name__ == "__main__":
    main()
