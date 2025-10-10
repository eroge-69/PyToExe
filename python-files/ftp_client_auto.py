import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
from ftplib import FTP
import os

class FTPClientAutoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Client FTP - Connessione Automatica")
        self.ftp = None

        # Pulsanti per upload e download
        self.upload_button = tk.Button(root, text="Carica File", command=self.upload_file, state="disabled")
        self.upload_button.grid(row=0, column=0, pady=5, padx=5)

        self.download_button = tk.Button(root, text="Scarica File", command=self.download_file, state="disabled")
        self.download_button.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(root, text="File disponibili sul server FTP:").grid(row=1, column=0, columnspan=2)

        self.file_listbox = Listbox(root, width=50)
        self.file_listbox.grid(row=2, column=0, columnspan=2)

        self.scrollbar = Scrollbar(root, orient="vertical", command=self.file_listbox.yview)
        self.scrollbar.grid(row=2, column=2, sticky="ns")
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)

        # Connessione automatica all'avvio
        self.connect_ftp()

    def connect_ftp(self):
        host = "2.40.100.234"
        try:
            self.ftp = FTP()
            self.ftp.connect(host, 21)
            self.ftp.login()
            messagebox.showinfo("Connessione", f"Connessione riuscita a {host}")
            self.upload_button.config(state="normal")
            self.download_button.config(state="normal")
            self.refresh_file_list()
        except Exception as e:
            messagebox.showerror("Errore", f"Connessione fallita: {e}")

    def refresh_file_list(self):
        try:
            self.file_listbox.delete(0, tk.END)
            files = self.ftp.nlst()
            for f in files:
                self.file_listbox.insert(tk.END, f)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile ottenere la lista dei file: {e}")

    def upload_file(self):
        filepath = filedialog.askopenfilename(title="Seleziona file da caricare")
        if filepath:
            filename = os.path.basename(filepath)
            try:
                with open(filepath, 'rb') as f:
                    self.ftp.storbinary(f'STOR {filename}', f)
                messagebox.showinfo("Upload", f"File '{filename}' caricato con successo.")
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'upload: {e}")

    def download_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona un file da scaricare.")
            return
        filename = self.file_listbox.get(selected[0])
        save_path = filedialog.asksaveasfilename(title="Salva file come", initialfile=filename)
        if save_path:
            try:
                with open(save_path, 'wb') as f:
                    self.ftp.retrbinary(f'RETR {filename}', f.write)
                messagebox.showinfo("Download", f"File '{filename}' scaricato con successo.")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante il download: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClientAutoApp(root)
    root.mainloop()
