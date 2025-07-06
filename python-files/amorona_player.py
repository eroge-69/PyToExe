
import os
from tkinter import Tk, Label, Button, filedialog, Listbox, Scrollbar, SINGLE, END, messagebox
import subprocess

DEFAULT_DIR = "D:/KARAOKE"

def open_with_karafun(file_path):
    try:
        subprocess.Popen(['start', '', file_path], shell=True)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")

def scan_kfn_files(directory):
    kfn_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".kfn"):
                kfn_files.append(os.path.join(root, file))
    return kfn_files

class AmoronaPlayerApp:
    def __init__(self, master):
        self.master = master
        master.title("Amorona Player")
        master.geometry("600x400")

        self.label = Label(master, text="Liste des fichiers .kfn trouvés :")
        self.label.pack()

        self.scrollbar = Scrollbar(master)
        self.scrollbar.pack(side="right", fill="y")

        self.listbox = Listbox(master, selectmode=SINGLE, yscrollcommand=self.scrollbar.set, width=80)
        self.listbox.pack(pady=10)
        self.scrollbar.config(command=self.listbox.yview)

        self.browse_button = Button(master, text="📁 Choisir un dossier", command=self.browse_folder)
        self.browse_button.pack()

        self.play_button = Button(master, text="▶️ Lire avec KaraFun", command=self.play_selected_file)
        self.play_button.pack(pady=5)

        self.kfn_files = []
        self.load_files(DEFAULT_DIR)

    def load_files(self, directory):
        self.kfn_files = scan_kfn_files(directory)
        self.listbox.delete(0, END)
        for file_path in self.kfn_files:
            self.listbox.insert(END, os.path.basename(file_path))

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.load_files(folder_selected)

    def play_selected_file(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            file_path = self.kfn_files[selected_index[0]]
            open_with_karafun(file_path)
        else:
            messagebox.showinfo("Info", "Veuillez sélectionner un fichier.")

if __name__ == "__main__":
    root = Tk()
    app = AmoronaPlayerApp(root)
    root.mainloop()
