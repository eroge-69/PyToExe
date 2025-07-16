import tkinter as tk
from tkinter import messagebox

def format_output():
    a = entry_a.get()
    b = entry_b.get()
    c = entry_c.get()
    d = entry_d.get()
    e = entry_e.get()
    f = entry_f.get()

    try:
        harga = int(e)
        harga_formatted = f"Rp{harga:,}".replace(",", ".")
    except ValueError:
        harga_formatted = e

    hasil = f"{a} order:\n\n{b}\n\n{c} - QTY {d} - H {harga_formatted} - {f}"
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, hasil)

def copy_to_clipboard():
    result = output_text.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(result)
    messagebox.showinfo("Tersalin", "Teks berhasil disalin ke clipboard!")

def clear_inputs():
    for entry in [entry_a, entry_b, entry_c, entry_d, entry_e, entry_f]:
        entry.delete(0, tk.END)
    output_text.delete("1.0", tk.END)

def keluar():
    root.quit()

# Buat jendela utama
root = tk.Tk()
root.title("Auto Output by van ")
root.geometry("600x600")

# Label & Entry untuk input a-f
labels = [
    "a (Contoh: AP. FAWWAS 2)",
    "b (Keterangan, contoh: Keterangan : Harga ED)",
    "c (Nama Obat, contoh: VENTOLIN INHALER)",
    "d (QTY, contoh: 10)",
    "e (Harga H, contoh: 138000)",
    "f (Harga H1, contoh: H3 146700)"
]

entries = []
for i, label_text in enumerate(labels):
    label = tk.Label(root, text=label_text)
    label.pack(anchor='w', padx=10)
    entry = tk.Entry(root, width=50)
    entry.pack(padx=10, pady=2)
    entries.append(entry)

entry_a, entry_b, entry_c, entry_d, entry_e, entry_f = entries

# Tombol Format
btn_format = tk.Button(root, text="Tampilkan Hasil", command=format_output, bg="lightblue")
btn_format.pack(pady=10)

# Output Text
output_text = tk.Text(root, height=10, width=70)
output_text.pack(padx=10, pady=5)

# Tombol Copy, Ulangi, dan Keluar
frame_btn = tk.Frame(root)
frame_btn.pack(pady=10)

btn_copy = tk.Button(frame_btn, text="Copy Text", command=copy_to_clipboard, bg="lightgreen")
btn_copy.grid(row=0, column=0, padx=5)

btn_ulang = tk.Button(frame_btn, text="Ulangi", command=clear_inputs, bg="orange")
btn_ulang.grid(row=0, column=1, padx=5)

btn_exit = tk.Button(frame_btn, text="Keluar", command=keluar, bg="red")
btn_exit.grid(row=0, column=2, padx=5)

# Jalankan GUI
root.mainloop()
