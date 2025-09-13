import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kopiranje Datoteke")
        self.root.geometry("400x200")

        self.source_file = ""
        self.destination_folder = "//ad.sigov.si/DAT/MOP/GURS_VSI/Programi/Kuverte/OGU-Nmesto/IR-Kuverte"

        # Če omrežna pot ni dostopna, uporabi lokalno mapo
        if not os.path.exists(self.destination_folder):
            self.destination_folder = "c:/temp"

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Izberite datoteko za kopiranje:").pack(pady=10)

        self.source_label = tk.Label(self.root, text="")
        self.source_label.pack()

        tk.Button(self.root, text="Izberi Datoteko", command=self.select_source_file).pack(pady=10)
        tk.Button(self.root, text="Kopiraj Datoteko", command=self.copy_file).pack(pady=10)

    def select_source_file(self):
        self.source_file = filedialog.askopenfilename((initialdir="//ad.sigov.si/DAT/MOP/GURS_OGU_NMesto/ZKN", title="Izberite datoteko"))
        if self.source_file:
            self.source_label.config(text="Izbrana datoteka: " + os.path.basename(self.source_file))

    def copy_file(self):
        if self.source_file:
            try:
                shutil.copy(self.source_file, self.destination_folder)
                messagebox.showinfo("Kopiranje Uspešno", "Datoteka je bila uspešno skopirana.")
            except Exception as e:
                messagebox.showerror("Napaka pri Kopiranju", f"Napaka: {str(e)}")
        else:
            messagebox.showerror("Napaka", "Izberite datoteko za kopiranje.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()
