import os
import shutil
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, MULTIPLE

def get_available_drives():
    system = platform.system()
    drives = []
    if system == "Windows":
        import string
        from ctypes import windll
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:/")
            bitmask >>= 1
    else:
        # Su Unix, montaggi tipici
        drives = ["/mnt", "/media", "/"]
    return drives

class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Selettore di cartelle per copia file")

        self.file_path = None
        self.selected_folders = []

        self.btn_select_file = tk.Button(root, text="Scegli file da copiare", command=self.select_file)
        self.btn_select_file.pack(pady=5)

        self.lbl_file = tk.Label(root, text="Nessun file selezionato")
        self.lbl_file.pack(pady=5)

        self.lbl_disks = tk.Label(root, text="Scegli una cartella da un disco:")
        self.lbl_disks.pack()

        self.disk_listbox = Listbox(root)
        for drive in get_available_drives():
            self.disk_listbox.insert(tk.END, drive)
        self.disk_listbox.pack()

        self.btn_browse_folders = tk.Button(root, text="Aggiungi cartella di destinazione", command=self.select_folder)
        self.btn_browse_folders.pack(pady=5)

        self.lbl_selected = tk.Label(root, text="Cartelle selezionate:")
        self.lbl_selected.pack()

        self.listbox_folders = Listbox(root, selectmode=MULTIPLE, width=80)
        self.listbox_folders.pack()

        self.btn_copy = tk.Button(root, text="Copia file nelle cartelle selezionate", command=self.copy_file)
        self.btn_copy.pack(pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path = file_path
            self.lbl_file.config(text=f"File selezionato: {file_path}")

    def select_folder(self):
        selected_drive = self.disk_listbox.get(tk.ACTIVE)
        folder = filedialog.askdirectory(initialdir=selected_drive)
        if folder:
            self.selected_folders.append(folder)
            self.listbox_folders.insert(tk.END, folder)

    def copy_file(self):
        if not self.file_path:
            messagebox.showerror("Errore", "Seleziona prima un file.")
            return
        if not self.selected_folders:
            messagebox.showerror("Errore", "Seleziona almeno una cartella.")
            return

        filename = os.path.basename(self.file_path)
        for folder in self.selected_folders:
            try:
                destinazione = os.path.join(folder, filename)
                shutil.copy2(self.file_path, destinazione)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante la copia in {folder}:\n{e}")
                return

        messagebox.showinfo("Successo", "File copiato con successo!")

# Avvia il programma
if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()
