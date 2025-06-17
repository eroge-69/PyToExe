import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

class ImageConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Strumenti di Conversione Immagini")
        master.geometry("400x200") # Dimensione iniziale della finestra

        # Menu principale
        self.menubar = tk.Menu(master)
        master.config(menu=self.menubar)

        # Menu "Strumenti"
        self.strumenti_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Strumenti", menu=self.strumenti_menu)

        # Opzioni del menu "Strumenti"
        self.strumenti_menu.add_command(label="Converti in JPEG", command=self.convert_to_jpeg)
        self.strumenti_menu.add_command(label="Converti in PNG", command=self.convert_to_png)
        self.strumenti_menu.add_separator()
        self.strumenti_menu.add_command(label="Esci", command=master.quit)

        # Label informativo (opzionale, per dare un feedback)
        self.status_label = tk.Label(master, text="Seleziona un'opzione dal menu 'Strumenti'.", pady=20)
        self.status_label.pack()

    def select_files(self, filetypes):
        """Apre la finestra di dialogo per selezionare più file."""
        files = filedialog.askopenfilenames(
            title="Seleziona i file immagine",
            filetypes=filetypes
        )
        return files

    def select_destination_folder(self):
        """Apre la finestra di dialogo per selezionare la cartella di destinazione."""
        folder = filedialog.askdirectory(
            title="Seleziona la cartella di destinazione"
        )
        return folder

    def convert_images(self, files, output_format):
        """Logica di conversione delle immagini."""
        if not files:
            messagebox.showwarning("Nessun File Selezionato", "Non è stato selezionato alcun file per la conversione.")
            return

        destination_folder = self.select_destination_folder()
        if not destination_folder:
            messagebox.showwarning("Nessuna Cartella Selezionata", "Nessuna cartella di destinazione selezionata. Conversione annullata.")
            return

        converted_count = 0
        error_count = 0

        for file_path in files:
            try:
                img = Image.open(file_path)
                base_name = os.path.basename(file_path)
                name_without_ext = os.path.splitext(base_name)[0]
                output_path = os.path.join(destination_folder, f"{name_without_ext}.{output_format.lower()}")

                if output_format == "JPEG":
                    # Per JPEG, assicurati che l'immagine sia in modalità RGB
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img.save(output_path, output_format, quality=90) # Quality per JPEG
                else: # PNG
                    img.save(output_path, output_format)
                converted_count += 1
            except Exception as e:
                error_count += 1
                print(f"Errore durante la conversione di {file_path}: {e}")

        messagebox.showinfo(
            "Conversione Completata",
            f"Convertite con successo {converted_count} immagini in {output_format}.\n"
            f"Errori: {error_count}.\n"
            f"File salvati in: {destination_folder}"
        )
        self.status_label.config(text=f"Conversione completata. Controlla {destination_folder}")

    def convert_to_jpeg(self):
        """Gestisce l'opzione "Converti in JPEG"."""
        # Tipi di file accettati per la conversione in JPEG
        filetypes = [
            ("Immagini (PNG, PSD, JPG, BMP, TIFF, GIF, WEBP)", "*.png *.psd *.jpeg *.jpg *.bmp *.tiff *.tif *.gif *.webp"),
            ("File PNG", "*.png"),
            ("File PSD (Photoshop)", "*.psd"),
            ("Tutti i file immagine", "*.jpeg *.jpg *.bmp *.tiff *.tif *.gif *.webp *.psd *.png"),
            ("Tutti i file", "*.*")
        ]
        files_to_convert = self.select_files(filetypes)
        self.convert_images(files_to_convert, "JPEG")

    def convert_to_png(self):
        """Gestisce l'opzione "Converti in PNG"."""
        # Tipi di file accettati per la conversione in PNG
        filetypes = [
            ("Immagini (JPEG, JPG, PSD, BMP, TIFF, GIF, WEBP)", "*.jpeg *.jpg *.psd *.bmp *.tiff *.tif *.gif *.webp"),
            ("File JPEG", "*.jpeg *.jpg"),
            ("File PSD (Photoshop)", "*.psd"),
            ("Tutti i file immagine", "*.jpeg *.jpg *.bmp *.tiff *.tif *.gif *.webp *.psd *.png"),
            ("Tutti i file", "*.*")
        ]
        files_to_convert = self.select_files(filetypes)
        self.convert_images(files_to_convert, "PNG")

# Creazione della finestra principale
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()