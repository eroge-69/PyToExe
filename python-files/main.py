import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import json, os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

DATA_FILE = "students.json"

# --- Veri yükleme ve kaydetme ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                today = datetime.today().strftime("%Y-%m-%d")
                for s in data:
                    if "records" not in s:
                        s["records"] = {today: {"book":None,"homework":None,"present":"✔"}}
                    else:
                        if today not in s["records"]:
                            s["records"][today] = {"book":None,"homework":None,"present":"✔"}
                return data
            except json.JSONDecodeError:
                return []
    return []

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4, ensure_ascii=False)

# --- GUI Fonksiyonları ---
def add_student():
    name = name_entry.get().strip()
    number = number_entry.get().strip()
    if not name or not number:
        messagebox.showwarning("Hata", "Ad ve okul numarası boş olamaz!")
        return
    for s in students:
        if s["number"] == number:
            messagebox.showwarning("Hata", "Bu okul numarası zaten ekli!")
            return
    today = datetime.today().strftime("%Y-%m-%d")
    student = {"name": name, "number": number, "records": {today: {"book":None,"homework":None,"present":"✔"}}}
    students.append(student)
    update_table()
    save_data()
    name_entry.delete(0, "end")
    number_entry.delete(0, "end")

def remove_student():
    selected = table.selection()
    if not selected:
        return
    for idx in reversed(selected):
        del students[int(idx)]
    update_table()
    save_data()

def update_table(selected_date=None, custom_list=None):
    if not selected_date:
        selected_date = date_var.get()
    target_students = custom_list if custom_list is not None else students

    for s in target_students:
        if selected_date not in s["records"]:
            s["records"][selected_date] = {"book":None,"homework":None,"present":"✔"}

    for row in table.get_children():
        table.delete(row)

    for idx, s in enumerate(target_students):
        rec = s["records"][selected_date]
        book = rec["book"] if rec["book"] else "✖"
        hw = rec["homework"] if rec["homework"] else "✖"
        present = rec["present"]
        # Renk kodlama
        tags = ()
        if book=="✔" and hw=="✔" and present=="✔":
            tags=("ok",)
        elif present=="✖":
            tags=("no",)
        table.insert("", "end", iid=str(idx), values=(s["name"], s["number"], book, hw, present), tags=tags)

def select_student():
    selected = table.selection()
    if not selected:
        return
    global current_student, current_date
    current_date = date_var.get()
    idx = int(selected[-1])
    current_student = idx
    rec = students[idx]["records"].setdefault(current_date, {"book":None,"homework":None,"present":"✔"})
    book_var.set(rec["book"] if rec["book"] else "✖")
    homework_var.set(rec["homework"] if rec["homework"] else "✖")
    present_var.set(rec["present"])

def on_treeview_click(event):
    row_id = table.identify_row(event.y)
    if not row_id:
        return
    if row_id in table.selection():
        table.selection_remove(row_id)
    else:
        table.selection_add(row_id)
    select_student()

def toggle_book():
    selected = table.selection()
    if not selected:
        return
    for idx in selected:
        rec = students[int(idx)]["records"].setdefault(date_var.get(), {"book":None,"homework":None,"present":"✔"})
        rec["book"] = "✔" if rec["book"]!="✔" else "✖"
    update_table(date_var.get())
    save_data()

def toggle_homework():
    selected = table.selection()
    if not selected:
        return
    for idx in selected:
        rec = students[int(idx)]["records"].setdefault(date_var.get(), {"book":None,"homework":None,"present":"✔"})
        rec["homework"] = "✔" if rec["homework"]!="✔" else "✖"
    update_table(date_var.get())
    save_data()

def toggle_present():
    selected = table.selection()
    if not selected:
        return
    for idx in selected:
        rec = students[int(idx)]["records"].setdefault(date_var.get(), {"book":None,"homework":None,"present":"✔"})
        rec["present"] = "✔" if rec["present"]!="✔" else "✖"
    update_table(date_var.get())
    save_data()

def change_date(event=None):
    global current_date
    current_date = date_var.get()
    update_table(current_date)

# --- Arama / Filtreleme ---
def search_students():
    query = search_var.get().strip().lower()
    filtered = [s for s in students if query in s["name"].lower() or query in s["number"]]
    update_table(date_var.get(), filtered)

# --- Toplu İşlem ---
def mark_all_book():
    for s in students:
        rec = s["records"].setdefault(date_var.get(), {"book":None,"homework":None,"present":"✔"})
        rec["book"]="✔"
    update_table(date_var.get())
    save_data()

def mark_all_homework():
    for s in students:
        rec = s["records"].setdefault(date_var.get(), {"book":None,"homework":None,"present":"✔"})
        rec["homework"]="✔"
    update_table(date_var.get())
    save_data()

def mark_all_present():
    for s in students:
        rec = s["records"].setdefault(date_var.get(), {"book":None,"homework":None,"present":"✔"})
        rec["present"]="✔"
    update_table(date_var.get())
    save_data()

# --- Tüm Listeyi Göster ---
def show_all(tarihli=True):
    top = ctk.CTkToplevel(root)
    top.title("Tüm Liste")
    top.geometry("900x500")
    top.configure(fg_color="#111111")

    if tarihli:
        cols = ("Tarih","Ad Soyad","Okul No","Kitap","Ödev","Gelme")
    else:
        cols = ("Ad Soyad","Okul No","Kitap Toplam","Ödev Toplam","Gelme Toplam")

    all_table = ttk.Treeview(top, columns=cols, show="headings")
    for c in cols:
        all_table.heading(c, text=c)
        all_table.column(c, width=130, anchor="center")
    all_table.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(top, orient="vertical", command=all_table.yview)
    hsb = ttk.Scrollbar(top, orient="horizontal", command=all_table.xview)
    all_table.configure(yscroll=vsb.set, xscroll=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#111111",
                    foreground="white",
                    fieldbackground="#111111",
                    rowheight=25,
                    font=("Arial", 12))
    style.map("Treeview",
              background=[('selected', '#333333')],
              foreground=[('selected', 'white')])

    sorted_students = sorted(students, key=lambda x: x["name"])

    if tarihli:
        for s in sorted_students:
            for day, rec in sorted(s["records"].items()):
                book = rec["book"] if rec["book"] else "✖"
                hw = rec["homework"] if rec["homework"] else "✖"
                all_table.insert("", "end", values=(day, s["name"], s["number"], book, hw, rec["present"]))
    else:
        for s in sorted_students:
            total_days = len([r for r in s["records"].values() if r["book"]=="✔" or r["homework"]=="✔" or r["present"]=="✔"])
            if total_days==0: total_days=1
            book_days = [r for r in s["records"].values() if r["book"]=="✔"]
            hw_days   = [r for r in s["records"].values() if r["homework"]=="✔"]
            present_days = [r for r in s["records"].values() if r["present"]=="✔"]
            all_table.insert("", "end", values=(s["name"], s["number"],
                                                f"{len(book_days)}/{total_days}",
                                                f"{len(hw_days)}/{total_days}",
                                                f"{len(present_days)}/{total_days}"))

# --- Excel / PDF Çıktısı ---
def export_excel():
    data = []
    for s in students:
        for day, rec in s["records"].items():
            data.append([day, s["name"], s["number"], rec["book"] if rec["book"] else "✖",
                         rec["homework"] if rec["homework"] else "✖", rec["present"]])
    df = pd.DataFrame(data, columns=["Tarih","Ad Soyad","Okul No","Kitap","Ödev","Gelme"])
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if filename:
        df.to_excel(filename, index=False)
        messagebox.showinfo("Başarılı", "Excel dosyası kaydedildi.")

def export_pdf():
    data = [["Tarih","Ad Soyad","Okul No","Kitap","Ödev","Gelme"]]
    for s in students:
        for day, rec in s["records"].items():
            data.append([day, s["name"], s["number"], rec["book"] if rec["book"] else "✖",
                         rec["homework"] if rec["homework"] else "✖", rec["present"]])
    filename = filedialog.asksaveasfilename(defaultextension=".pdf")
    if filename:
        pdf = SimpleDocTemplate(filename)
        table_pdf = Table(data)
        table_pdf.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.gray),
                                       ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                                       ('ALIGN',(0,0),(-1,-1),'CENTER'),
                                       ('GRID',(0,0),(-1,-1),1,colors.black)]))
        pdf.build([table_pdf])
        messagebox.showinfo("Başarılı", "PDF dosyası kaydedildi.")

# --- Grafiksel Özet ---
def show_stats():
    names = [s["name"] for s in students]
    books = [sum(1 for r in s["records"].values() if r["book"]=="✔") for s in students]
    homeworks = [sum(1 for r in s["records"].values() if r["homework"]=="✔") for s in students]
    presents = [sum(1 for r in s["records"].values() if r["present"]=="✔") for s in students]
    days = [len(s["records"]) for s in students]

    book_perc = [b/d*100 if d>0 else 0 for b,d in zip(books,days)]
    hw_perc = [h/d*100 if d>0 else 0 for h,d in zip(homeworks,days)]
    present_perc = [p/d*100 if d>0 else 0 for p,d in zip(presents,days)]

    plt.figure(figsize=(10,6))
    plt.bar(names, book_perc, label="Kitap %")
    plt.bar(names, hw_perc, bottom=book_perc, label="Ödev %")
    plt.bar(names, present_perc, bottom=[b+h for b,h in zip(book_perc,hw_perc)], label="Gelme %")
    plt.ylabel("Yüzde")
    plt.title("Öğrenci Başarı Özetleri")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    class_book = sum(book_perc)/len(book_perc) if book_perc else 0
    class_hw = sum(hw_perc)/len(hw_perc) if hw_perc else 0
    class_present = sum(present_perc)/len(present_perc) if present_perc else 0
    messagebox.showinfo("Sınıf Ortalaması", f"Kitap: %{class_book:.1f}, Ödev: %{class_hw:.1f}, Gelme: %{class_present:.1f}")

# --- Başlat ---
students = load_data()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("Dönemlik Kitap & Ödev Takip")
root.geometry("1200x650")

# Üst panel
top_frame = ctk.CTkFrame(root)
top_frame.pack(fill="x", padx=10, pady=10)

ctk.CTkLabel(top_frame, text="Ad Soyad:").grid(row=0, column=0, padx=5, pady=5)
name_entry = ctk.CTkEntry(top_frame, width=150)
name_entry.grid(row=0, column=1, padx=5, pady=5)

ctk.CTkLabel(top_frame, text="Okul No:").grid(row=0, column=2, padx=5, pady=5)
number_entry = ctk.CTkEntry(top_frame, width=100)
number_entry.grid(row=0, column=3, padx=5, pady=5)

ctk.CTkButton(top_frame, text="Öğrenci Ekle", command=add_student).grid(row=0, column=4, padx=5, pady=5)
ctk.CTkButton(top_frame, text="Öğrenci Sil", command=remove_student).grid(row=0, column=5, padx=5, pady=5)
ctk.CTkButton(top_frame, text="Tüm Listeyi Tarihli Göster", command=lambda: show_all(tarihli=True)).grid(row=0, column=6, padx=5, pady=5)
ctk.CTkButton(top_frame, text="Tüm Listeyi Tarihsiz Göster", command=lambda: show_all(tarihli=False)).grid(row=0, column=7, padx=5, pady=5)

# Arama paneli
search_var = tk.StringVar()
ctk.CTkEntry(top_frame, textvariable=search_var, width=150, placeholder_text="Ara...").grid(row=0, column=8, padx=5)
ctk.CTkButton(top_frame, text="Ara", command=search_students).grid(row=0, column=9, padx=5)

# Tarih paneli
date_frame = ctk.CTkFrame(root)
date_frame.pack(fill="x", padx=10, pady=5)

ctk.CTkLabel(date_frame, text="Tarih:", width=80, anchor="w").pack(side="left", padx=5)
date_var = tk.StringVar()
date_var.set(datetime.today().strftime("%Y-%m-%d"))

date_entry = DateEntry(
    date_frame,
    textvariable=date_var,
    date_pattern="yyyy-mm-dd",
    background="black",
    foreground="white",
    borderwidth=2,
    year=datetime.today().year,
    month=datetime.today().month,
    day=datetime.today().day
)
date_entry.pack(side="left", padx=5)
date_entry.bind("<<DateEntrySelected>>", change_date)

# Orta panel
table_frame = ctk.CTkFrame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Ad Soyad", "Okul No", "Kitap", "Ödev", "Gelme")
table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150, anchor="center")

# Renk kodlama
table.tag_configure("ok", background="#1e4620", foreground="white")
table.tag_configure("no", background="#5a1d1d", foreground="white")

vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
table.configure(yscroll=vsb.set, xscroll=hsb.set)
vsb.pack(side="right", fill="y")
hsb.pack(side="bottom", fill="x")
table.pack(fill="both", expand=True)

table.bind("<Button-1>", on_treeview_click)

# Sağ panel
right_frame = ctk.CTkFrame(root)
right_frame.pack(side="right", fill="y", padx=10, pady=10)

book_var = ctk.StringVar(value="✖")
homework_var = ctk.StringVar(value="✖")
present_var = ctk.StringVar(value="✔")

ctk.CTkLabel(right_frame, text="Kitap Durumu:").pack(pady=5)
ctk.CTkButton(right_frame, text="Kitap ✔/✖", command=toggle_book, width=120).pack(pady=5)
ctk.CTkButton(right_frame, text="Tüm Sınıf Kitap ✔", command=mark_all_book, width=120).pack(pady=5)

ctk.CTkLabel(right_frame, text="Ödev Durumu:").pack(pady=5)
ctk.CTkButton(right_frame, text="Ödev ✔/✖", command=toggle_homework, width=120).pack(pady=5)
ctk.CTkButton(right_frame, text="Tüm Sınıf Ödev ✔", command=mark_all_homework, width=120).pack(pady=5)

ctk.CTkLabel(right_frame, text="Gelme Durumu:").pack(pady=5)
ctk.CTkButton(right_frame, text="Gelme ✔/✖", command=toggle_present, width=120).pack(pady=5)
ctk.CTkButton(right_frame, text="Tüm Sınıf Geldi ✔", command=mark_all_present, width=120).pack(pady=5)

ctk.CTkLabel(right_frame, text="Çıktılar:").pack(pady=10)
ctk.CTkButton(right_frame, text="Excel Çıkışı", command=export_excel, width=120).pack(pady=5)
ctk.CTkButton(right_frame, text="PDF Çıkışı", command=export_pdf, width=120).pack(pady=5)
ctk.CTkButton(right_frame, text="Grafik & Özet", command=show_stats, width=120).pack(pady=5)

update_table()
root.mainloop()
