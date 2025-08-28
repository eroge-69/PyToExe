import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")  # "dark" o "light"
ctk.set_default_color_theme("blue")  # temi: blue, green, dark-blue

# Cartella di destinazione
OUTPUT_DIR = "Musica"
os.makedirs(OUTPUT_DIR, exist_ok=True)

file_path = ""

def select_file():
    global file_path
    file_path = filedialog.askopenfilename(
        title="Seleziona file .txt con i link YouTube",
        filetypes=(("File di testo", "*.txt"),)
    )
    if file_path:
        label_file.configure(text=os.path.basename(file_path))

def download_links():
    if not file_path:
        messagebox.showwarning("Attenzione", "Seleziona prima un file .txt!")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    text_log.configure(state="normal")
    text_log.delete("1.0", "end")
    
    for link in links:
        text_log.insert("end", f"🔗 Processando: {link}\n")
        text_log.update()
        if "youtube.com" in link or "youtu.be" in link:
            try:
                subprocess.run([
                    "yt-dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--output", os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
                    link
                ], check=True)
                text_log.insert("end", f"✅ Scaricato {link}\n\n")
            except subprocess.CalledProcessError:
                text_log.insert("end", f"❌ Errore con {link}\n\n")
        else:
            text_log.insert("end", f"⚠️ Link non riconosciuto: {link}\n\n")
        text_log.update()
    
    text_log.configure(state="disabled")
    messagebox.showinfo("Completato", f"Tutti i download terminati!\nFile in: {OUTPUT_DIR}")

# Finestra principale
app = ctk.CTk()
app.title("Da YouTube -> MP3 Downloader - baikozz")
app.geometry("650x450")
app.resizable(False, False)

label_info = ctk.CTkLabel(app, text="Seleziona un file .txt con i link YouTube:", font=("Arial", 14))
label_info.pack(pady=(15,5))

btn_select = ctk.CTkButton(app, text="Scegli file", command=select_file, width=180, height=40, fg_color="#1D531E")
btn_select.pack(pady=5)

label_file = ctk.CTkLabel(app, text="Nessun file selezionato", font=("Arial", 12))
label_file.pack(pady=5)

btn_download = ctk.CTkButton(app, text="Scarica tutti i link", command=download_links, width=220, height=50, fg_color="#4D4D4D")
btn_download.pack(pady=10)

text_log = ctk.CTkTextbox(app, width=600, height=250)
text_log.pack(pady=10)
text_log.configure(state="disabled")

app.mainloop()
