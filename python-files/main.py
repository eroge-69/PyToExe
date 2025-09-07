import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
from datetime import datetime

# Fungsi membuat PDF tagihan profesional
def generate_pdf(name, room, months, price_per_month, total):
    if not os.path.exists("tagihan"):
        os.makedirs("tagihan")
    
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"tagihan/{name}_{now}.pdf"
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFillColor(colors.HexColor("#007acc"))  # biru
    c.rect(0, height-100, width, 100, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(170, height-70, "KOS KOSAN MAKMUR")
    c.setFont("Helvetica", 12)
    c.drawString(170, height-90, "Jl. Contoh Alamat No.123, Kota Anda | Telp: 0812-XXXX-XXXX")

    # Informasi penyewa
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height-130, "Tagihan Penyewa")
    c.setFont("Helvetica", 12)
    c.drawString(50, height-150, f"Nama Penyewa: {name}")
    c.drawString(50, height-170, f"Kamar: {room}")
    c.drawString(50, height-190, f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

    # Tabel tagihan
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height-220, "Keterangan")
    c.drawString(300, height-220, "Bulan")
    c.drawString(400, height-220, "Harga (Rp)")
    c.drawString(500, height-220, "Total (Rp)")
    c.line(50, height-225, width-50, height-225)

    c.setFont("Helvetica", 12)
    c.drawString(50, height-245, f"Sewa Kosan")
    c.drawString(300, height-245, f"{months}")
    c.drawString(400, height-245, f"{price_per_month}")
    c.drawString(500, height-245, f"{total}")
    c.line(50, height-260, width-50, height-260)

    # Total bayar
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, height-290, "TOTAL BAYAR:")
    c.drawString(500, height-290, f"Rp {total}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Terima kasih telah memilih Kos Kosan Makmur!")
    c.drawString(50, 35, "www.kosmakmur.com | info@kosmakmur.com")

    c.save()
    messagebox.showinfo("Sukses", f"Tagihan berhasil disimpan!\n{filename}")

# Fungsi menghitung total
def hitung_total():
    try:
        name = entry_name.get()
        room = entry_room.get()
        months = int(entry_months.get())
        price_per_month = int(entry_price.get())
        total = months * price_per_month
        generate_pdf(name, room, months, price_per_month, total)
    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid untuk bulan dan harga per bulan")

# GUI Tkinter tema putih-biru
root = tk.Tk()
root.title("Aplikasi Kasir Kos-Kosan")
root.geometry("450x350")
root.config(bg="white")

label_color = "#007acc"

# Input data
tk.Label(root, text="Nama Penyewa", bg="white", fg=label_color).grid(row=0, column=0, padx=10, pady=10, sticky="w")
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Kamar", bg="white", fg=label_color).grid(row=1, column=0, padx=10, pady=10, sticky="w")
entry_room = tk.Entry(root)
entry_room.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Lama Sewa (bulan)", bg="white", fg=label_color).grid(row=2, column=0, padx=10, pady=10, sticky="w")
entry_months = tk.Entry(root)
entry_months.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Harga per Bulan (Rp)", bg="white", fg=label_color).grid(row=3, column=0, padx=10, pady=10, sticky="w")
entry_price = tk.Entry(root)
entry_price.grid(row=3, column=1, padx=10, pady=10)

# Tombol cetak tagihan
tk.Button(root, text="Cetak Tagihan", bg=label_color, fg="white", command=hitung_total).grid(row=5, column=0, columnspan=2, pady=20)

# Jalankan GUI
root.mainloop()
