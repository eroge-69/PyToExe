
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bild-Umbenenner")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.input_folder = ""
        self.output_folder = ""

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="📁 Bild-Umbenenner", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.input_label = tk.Label(self.root, text="Quellordner: nicht gewählt", wraplength=350)
        self.input_label.pack(pady=5)
        tk.Button(self.root, text="Quellordner auswählen", command=self.select_input).pack()

        self.output_label = tk.Label(self.root, text="Zielordner: nicht gewählt", wraplength=350)
        self.output_label.pack(pady=5)
        tk.Button(self.root, text="Zielordner auswählen", command=self.select_output).pack()

        self.start_button = tk.Button(self.root, text="Start", state=tk.DISABLED, command=self.process_images)
        self.start_button.pack(pady=20)

        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=10)

    def select_input(self):
        folder = filedialog.askdirectory(title="Quellordner auswählen")
        if folder:
            self.input_folder = folder
            self.input_label.config(text=f"Quellordner: {folder}")
            self.check_ready()

    def select_output(self):
        folder = filedialog.askdirectory(title="Zielordner auswählen")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"Zielordner: {folder}")
            self.check_ready()

    def check_ready(self):
        if self.input_folder and self.output_folder:
            self.start_button.config(state=tk.NORMAL)

    def process_images(self):
        valid_ext = (".jpg", ".jpeg", ".png")
        files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(valid_ext) and "#" in f]

        if not files:
            messagebox.showinfo("Keine passenden Dateien", "Keine passenden Bilddateien mit '#' gefunden.")
            return

        self.progress["maximum"] = len(files)
        self.progress["value"] = 0
        self.root.update_idletasks()

        count = 0
        for idx, filename in enumerate(files):
            try:
                base_name = filename.split("#")[0]
                ext = os.path.splitext(filename)[1]
                new_name = base_name + ext

                src = os.path.join(self.input_folder, filename)
                dst = os.path.join(self.output_folder, new_name)

                # Doppelte Namen vermeiden
                i = 1
                while os.path.exists(dst):
                    dst = os.path.join(self.output_folder, f"{base_name}_{i}{ext}")
                    i += 1

                shutil.copy2(src, dst)
                count += 1

            except Exception as e:
                print(f"Fehler bei {filename}: {e}")
            finally:
                self.progress["value"] = idx + 1
                self.root.update_idletasks()

        messagebox.showinfo("Fertig", f"{count} Dateien erfolgreich kopiert und umbenannt!")

# GUI starten
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()
