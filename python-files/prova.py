import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Serve pip install pillow
import os
import psutil
import subprocess

# === CONFIGURAZIONE ===
file_paths = [
    r"C:\sagra\stampe\stampa_bar.html",
    r"C:\sagra\stampe\stampa_cliente.html",
    r"C:\sagra\stampe\stampa_cucina.html"
]

process_name = "sagra.exe"
process_path = r"C:\Program Files (x86)\Gestione stand gastronomico\sagra.exe"
anteprima_img_path = r"C:\sagra\stampe\anteprima.png"  # Percorso immagine PNG

# === FUNZIONI ===
# (Mantieni le tue funzioni di aggiornamento file e riavvio processo così come sono,
# qui cambio solo la parte anteprima)

def carica_immagine_anteprima():
    if not os.path.exists(anteprima_img_path):
        messagebox.showerror("Errore", f"Immagine anteprima non trovata:\n{anteprima_img_path}")
        return None
    try:
        img = Image.open(anteprima_img_path)
        # Se vuoi ridimensiona qui img = img.resize((larghezza, altezza), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile caricare immagine:\n{e}")
        return None

# === GUI ===

root = tk.Tk()
root.title("Editor HTML - Sagra")
root.geometry("900x500")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=tk.BOTH, expand=True)

titolo_var = tk.StringVar()
sottotitolo_var = tk.StringVar()
fine_var = tk.StringVar()
ringraziamenti_var = tk.StringVar()

left_frame = ttk.Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="nw")

ttk.Label(left_frame, text="Titolo:").grid(row=0, column=0, sticky="w", pady=2)
titolo_entry = ttk.Entry(left_frame, textvariable=titolo_var, width=50)
titolo_entry.grid(row=1, column=0, pady=2)

ttk.Label(left_frame, text="Sottotitolo:").grid(row=2, column=0, sticky="w", pady=2)
sottotitolo_entry = ttk.Entry(left_frame, textvariable=sottotitolo_var, width=50)
sottotitolo_entry.grid(row=3, column=0, pady=2)

ttk.Label(left_frame, text="Fine pagina:").grid(row=4, column=0, sticky="w", pady=2)
fine_entry = ttk.Entry(left_frame, textvariable=fine_var, width=50)
fine_entry.grid(row=5, column=0, pady=2)

ttk.Label(left_frame, text="Ringraziamenti:").grid(row=6, column=0, sticky="w", pady=2)
ringr_entry = ttk.Entry(left_frame, textvariable=ringraziamenti_var, width=50)
ringr_entry.grid(row=7, column=0, pady=2)

ttk.Button(left_frame, text="Conferma e riavvia", command=lambda: messagebox.showinfo("Info", "Funzione da integrare")).grid(row=8, column=0, pady=20)

right_frame = ttk.Frame(main_frame)
right_frame.grid(row=0, column=1, padx=20, sticky="nsew")

# Label per immagine anteprima
anteprima_img_label = ttk.Label(right_frame)
anteprima_img_label.pack(fill="both", expand=True)

# Carica immagine
img_preview = carica_immagine_anteprima()
if img_preview:
    anteprima_img_label.configure(image=img_preview)
    anteprima_img_label.image = img_preview  # reference per evitare garbage collection

main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

root.mainloop()
