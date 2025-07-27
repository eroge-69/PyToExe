import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pywhatkit
import schedule
import threading
import time
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

data_target = None
date_vars = []

def load_file():
    global data_target
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        try:
            df = pd.read_excel(file_path)
            if 'Nomor WhatsApp' not in df.columns:
                messagebox.showerror("Error", "Kolom 'Nomor WhatsApp' tidak ditemukan di file Excel.")
                return
            data_target = df[['Nomor WhatsApp']]
            tree.delete(*tree.get_children())
            for _, row in data_target.iterrows():
                tree.insert("", "end", values=(row['Nomor WhatsApp'],))
            messagebox.showinfo("Sukses", "Nomor berhasil dimuat.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file: {e}")

def tulis_log(teks):
    log_box.configure(state="normal")
    log_box.insert("end", teks + "\n")
    log_box.see("end")
    log_box.configure(state="disabled")

def get_selected_dates():
    selected = []
    for i, var in enumerate(date_vars, start=1):
        if var.get() == 1:
            selected.append(i)
    return selected

def kirim_semua():
    global data_target
    if data_target is None:
        messagebox.showwarning("Peringatan", "Mohon muat file Excel terlebih dahulu.")
        return
    pesan = text_pesan.get("0.0", "end").strip()
    if not pesan:
        messagebox.showwarning("Peringatan", "Pesan tidak boleh kosong.")
        return

    progress_bar.set(0)
    tulis_log("=== Mulai proses pengiriman ===")
    for idx, row in data_target.iterrows():
        nomor = f"+{row['Nomor WhatsApp']}"
        try:
            jam = datetime.now().hour
            menit = datetime.now().minute
            pywhatkit.sendwhatmsg(nomor, pesan, jam, menit + 1, wait_time=20, tab_close=True)
            tulis_log(f"[SUKSES] Pesan ke {nomor} dijadwalkan.")
        except Exception as e:
            tulis_log(f"[GAGAL] Pesan ke {nomor} - {e}")
        progress_bar.set((idx + 1) / len(data_target))
        app.update_idletasks()
        time.sleep(10)

    tulis_log("=== Selesai semua pengiriman ===")
    messagebox.showinfo("Selesai", "Semua pesan telah diproses.")

def start_schedule():
    jam_str = entry_jam.get()
    try:
        schedule.clear()
        schedule.every().day.at(jam_str).do(check_and_send)
        threading.Thread(target=run_schedule, daemon=True).start()
        tulis_log(f"[INFO] Jadwal aktif setiap hari jam {jam_str}")
        messagebox.showinfo("Jadwal Aktif", f"Pesan akan dikirim setiap hari jam {jam_str} pada tanggal yang dicentang.")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal mengatur jadwal: {e}")

def check_and_send():
    today_day = datetime.now().day
    selected_days = get_selected_dates()
    if today_day in selected_days:
        tulis_log(f"[INFO] Hari ini tanggal {today_day}, termasuk daftar pengiriman.")
        kirim_semua()
    else:
        tulis_log(f"[INFO] Hari ini tanggal {today_day}, tidak termasuk daftar pengiriman.")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def export_log():
    log_content = log_box.get("0.0", "end").strip()
    if not log_content:
        messagebox.showinfo("Info", "Log masih kosong.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(log_content)
            messagebox.showinfo("Sukses", f"Log berhasil disimpan:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan log: {e}")

app = ctk.CTk()
app.title("WhatsApp Scheduler Modern")
app.geometry("1000x700")

frame_top = ctk.CTkFrame(app)
frame_top.pack(padx=10, pady=10, fill="x")

btn_load = ctk.CTkButton(frame_top, text="📂 Muat File Excel", command=load_file)
btn_load.grid(row=0, column=0, padx=10, pady=5)

text_pesan = ctk.CTkTextbox(frame_top, width=300, height=80)
text_pesan.grid(row=0, column=1, padx=10, pady=5)
text_pesan.insert("0.0", "Tulis pesan di sini...")

entry_jam = ctk.CTkEntry(frame_top, width=100)
entry_jam.insert(0, "08:00")
entry_jam.grid(row=0, column=2, padx=10, pady=5)

btn_jadwal = ctk.CTkButton(frame_top, text="⏰ Aktifkan Jadwal", command=start_schedule)
btn_jadwal.grid(row=0, column=3, padx=10, pady=5)

btn_kirim_sekarang = ctk.CTkButton(frame_top, text="🚀 Kirim Sekarang", command=kirim_semua)
btn_kirim_sekarang.grid(row=0, column=4, padx=10, pady=5)

frame_middle = ctk.CTkFrame(app)
frame_middle.pack(padx=10, pady=10, fill="both", expand=True)

frame_left = ctk.CTkFrame(frame_middle)
frame_left.pack(side="left", padx=10, pady=10, fill="y")

label_tanggal = ctk.CTkLabel(frame_left, text="Centang tanggal:")
label_tanggal.pack(pady=5)
frame_check = ctk.CTkFrame(frame_left)
frame_check.pack(pady=5)
for i in range(31):
    var = ctk.IntVar()
    cb = ctk.CTkCheckBox(frame_check, text=str(i+1), variable=var)
    cb.grid(row=i//7, column=i%7, padx=3, pady=3, sticky="w")
    date_vars.append(var)

frame_right = ctk.CTkFrame(frame_middle)
frame_right.pack(side="left", padx=10, pady=10, fill="both", expand=True)

progress_bar = ctk.CTkProgressBar(frame_right)
progress_bar.pack(padx=10, pady=10, fill="x")
progress_bar.set(0)

log_box = ctk.CTkTextbox(frame_right, height=200)
log_box.pack(padx=10, pady=10, fill="both", expand=True)
log_box.configure(state="disabled")

btn_export_log = ctk.CTkButton(frame_right, text="💾 Export Log", command=export_log)
btn_export_log.pack(pady=5)

frame_bottom = ctk.CTkFrame(app)
frame_bottom.pack(padx=10, pady=10, fill="both", expand=True)

tree = ttk.Treeview(frame_bottom, columns=("Nomor"), show="headings")
tree.heading("Nomor", text="Nomor WhatsApp")
tree.pack(fill="both", expand=True)

app.mainloop()
