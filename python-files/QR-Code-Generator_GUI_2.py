import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import qrcode.image.svg
import os
'''
März 2025
#Importe
pip install qrcode

'''
class QRCodeApp:
    MAX_CHARACTERS_PER_VERSION = {
        "L": {1: 25, 2: 47, 3: 77, 4: 114, 5: 154, 6: 195, 7: 224, 8: 279, 9: 335, 10: 395,
              11: 468, 12: 535, 13: 619, 14: 667, 15: 758, 16: 854, 17: 938, 18: 1046,
              19: 1153, 20: 1249, 21: 1352, 22: 1460, 23: 1588, 24: 1704, 25: 1853,
              26: 1990, 27: 2132, 28: 2223, 29: 2369, 30: 2520, 31: 2677, 32: 2840,
              33: 3009, 34: 3183, 35: 3351, 36: 3537, 37: 3729, 38: 3927, 39: 4087,
              40: 4296},
        "M": {1: 20, 2: 38, 3: 61, 4: 90, 5: 122, 6: 154, 7: 178, 8: 221, 9: 262, 10: 311,
              11: 366, 12: 419, 13: 483, 14: 528, 15: 600, 16: 656, 17: 734, 18: 816,
              19: 909, 20: 970, 21: 1086, 22: 1174, 23: 1276, 24: 1370, 25: 1468,
              26: 1588, 27: 1704, 28: 1852, 29: 1972, 30: 2085, 31: 2181, 32: 2358,
              33: 2473, 34: 2670, 35: 2805, 36: 2949, 37: 3081, 38: 3244, 39: 3417,
              40: 3599},
        "Q": {1: 16, 2: 29, 3: 47, 4: 67, 5: 87, 6: 108, 7: 125, 8: 157, 9: 189, 10: 221,
              11: 259, 12: 296, 13: 352, 14: 376, 15: 426, 16: 470, 17: 531, 18: 574,
              19: 644, 20: 702, 21: 742, 22: 823, 23: 890, 24: 963, 25: 1041, 26: 1094,
              27: 1172, 28: 1263, 29: 1322, 30: 1429, 31: 1499, 32: 1618, 33: 1700,
              34: 1787, 35: 1867, 36: 1966, 37: 2071, 38: 2181, 39: 2298, 40: 2420},
        "H": {1: 10, 2: 20, 3: 35, 4: 50, 5: 64, 6: 84, 7: 93, 8: 122, 9: 143, 10: 174,
              11: 200, 12: 227, 13: 259, 14: 283, 15: 321, 16: 365, 17: 408, 18: 452,
              19: 493, 20: 557, 21: 587, 22: 640, 23: 672, 24: 744, 25: 779, 26: 864,
              27: 910, 28: 958, 29: 1016, 30: 1080, 31: 1150, 32: 1226, 33: 1307,
              34: 1394, 35: 1431, 36: 1530, 37: 1591, 38: 1658, 39: 1774, 40: 1852}
    }

    def __init__(self, root):
        self.root = root
        self.root.title("QR-Code Generator_2")
        self.root.geometry("500x700")

        # Initial default values
        self.output_formats = {"svg": tk.BooleanVar(value=True), "png": tk.BooleanVar(value=True), "jpg": tk.BooleanVar(value=True)}
        self.version = tk.IntVar(value=1)
        self.box_size = tk.IntVar(value=10)
        self.border = tk.IntVar(value=4)
        self.data_content = tk.StringVar(value="https://example.com")
        self.output_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.error_correction = tk.StringVar(value="L")

        self.create_widgets()

    def create_widgets(self):
        # Eingabe für QR-Daten
        ttk.Label(self.root, text="QR-Inhalt eingeben:").pack(anchor=tk.W, pady=5, padx=10)
        ttk.Entry(self.root, textvariable=self.data_content, width=60).pack(anchor=tk.W, padx=10)

        # Zeichenzähler hinzufügen
        ttk.Label(self.root, text="Eingegebene Zeichen:").pack(anchor=tk.W, pady=5, padx=10)
        self.char_count_label = ttk.Label(self.root, text="0 Zeichen")
        self.char_count_label.pack(anchor=tk.W, padx=10)

        # Trace-Listener für Textänderungen
        self.data_content.trace_add("write", self.update_char_count)

        # QR-Code Vorschau Bild
        self.qr_image_frame = ttk.LabelFrame(self.root, text="QR-Code Beispiel (ISO/IEC 18004)")
        self.qr_image_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        img = self.generate_sample_qr_code()
        self.qr_image_label = ttk.Label(self.qr_image_frame, image=img)
        self.qr_image_label.image = img
        self.qr_image_label.pack()

        # Auswahl der Ausgabeformate
        ttk.Label(self.root, text="Ausgabeformate auswählen:").pack(anchor=tk.W, pady=5, padx=10)
        output_frame = ttk.Frame(self.root)
        output_frame.pack(anchor=tk.W, padx=10)
        for fmt in self.output_formats:
            ttk.Checkbutton(output_frame, text=fmt.upper(), variable=self.output_formats[fmt]).pack(side=tk.LEFT, padx=5)

        # Version des QR Codes
        version_frame = ttk.Frame(self.root)
        version_frame.pack(anchor=tk.W, pady=5, padx=10)
        ttk.Label(version_frame, text="QR-Version (1 bis 40):").pack(side=tk.LEFT)
        ttk.Spinbox(version_frame, from_=1, to=40, textvariable=self.version, width=5, command=self.update_character_info).pack(side=tk.LEFT, padx=5)
        self.char_info_label = ttk.Label(version_frame, text=f"Max Zeichen: {self.MAX_CHARACTERS_PER_VERSION['L'][1]}")
        self.char_info_label.pack(side=tk.LEFT, padx=10)

        # Sicherheitsstufen
        ttk.Label(self.root, text="Fehlerkorrekturstufe auswählen:").pack(anchor=tk.W, pady=5, padx=10)
        error_frame = ttk.Frame(self.root)
        error_frame.pack(anchor=tk.W, padx=10)
        for level, label in zip(["L", "M", "Q", "H"], ["L (7%)", "M (15%)", "Q (25%)", "H (30%)"]):
            ttk.Radiobutton(error_frame, text=label, variable=self.error_correction, value=level, command=self.update_character_info).pack(side=tk.LEFT, padx=5)

        # Box Size und Border Settings
        ttk.Label(self.root, text="Box Size (Pixel pro Modul):").pack(anchor=tk.W, pady=5, padx=10)
        ttk.Spinbox(self.root, from_=1, to=20, textvariable=self.box_size, width=5).pack(anchor=tk.W, padx=10)

        ttk.Label(self.root, text="Border Size (Rand in Modulen):").pack(anchor=tk.W, pady=5, padx=10)
        ttk.Spinbox(self.root, from_=1, to=10, textvariable=self.border, width=5).pack(anchor=tk.W, padx=10)

        # Auswahl des Ausgabepfads
        ttk.Label(self.root, text="Ausgabepfad:").pack(anchor=tk.W, pady=5, padx=10)
        path_frame = ttk.Frame(self.root)
        path_frame.pack(anchor=tk.W, padx=10)
        ttk.Entry(path_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="Durchsuchen", command=self.browse_directory).pack(side=tk.LEFT, padx=5)

        # Generate Button
        ttk.Button(self.root, text="QR-Code generieren", command=self.generate_qr_code).pack(pady=20)

    def update_char_count(self, *args):
        current_length = len(self.data_content.get())
        self.char_count_label.config(text=f"{current_length} Zeichen")
        max_chars = self.MAX_CHARACTERS_PER_VERSION[self.error_correction.get()].get(self.version.get(), 0)
        
        # Farbe bei Überschreitung ändern
        if current_length > max_chars:
            self.char_count_label.config(foreground="red")
        else:
            self.char_count_label.config(foreground="black")

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_path.get())
        if directory:
            self.output_path.set(directory)

    def update_character_info(self):
        version = self.version.get()
        error_correction = self.error_correction.get()
        max_chars = self.MAX_CHARACTERS_PER_VERSION[error_correction].get(version, "Unbekannt")
        self.char_info_label.config(text=f"Max Zeichen: {max_chars}")
        self.update_char_count()  # Aktualisiere die Farbe bei Änderung der Einstellungen

    def generate_sample_qr_code(self):
        sample_qr = qrcode.make("https://example.com")
        img = sample_qr.resize((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        return img_tk

    def generate_qr_code(self):
        # Daten aus GUI auslesen
        data = self.data_content.get()
        version = self.version.get() if self.version.get() != 0 else None
        box_size = self.box_size.get()
        border = self.border.get()
        output_dir = self.output_path.get()
        error_level = getattr(qrcode.constants, f"ERROR_CORRECT_{self.error_correction.get()}")

        # Überprüfen der maximal möglichen Zeichen
        max_chars = self.MAX_CHARACTERS_PER_VERSION[self.error_correction.get()].get(version, 0)
        if len(data) > max_chars:
            messagebox.showerror("Fehler", f"Die Eingabe überschreitet die maximale Anzahl von {max_chars} Zeichen für Version {version} und Fehlerkorrekturstufe {self.error_correction.get()}.")
            return

        if not data.strip():
            messagebox.showerror("Fehler", "Bitte geben Sie Inhalte für den QR-Code ein.")
            return

        qr = qrcode.QRCode(
            version=version,
            error_correction=error_level,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        try:
            if self.output_formats["svg"].get():
                svg_file = os.path.join(output_dir, "qrcode.svg")
                factory = qrcode.image.svg.SvgPathImage
                img_svg = qr.make_image(image_factory=factory)
                img_svg.save(svg_file)

            if self.output_formats["png"].get():
                png_file = os.path.join(output_dir, "qrcode.png")
                img_png = qr.make_image(fill_color="black", back_color="white")
                img_png.save(png_file)

            if self.output_formats["jpg"].get():
                jpg_file = os.path.join(output_dir, "qrcode.jpg")
                img_jpg = qr.make_image(fill_color="black", back_color="white")
                img_jpg = img_jpg.convert("RGB")
                img_jpg.save(jpg_file)

            messagebox.showinfo("Erfolg", f"QR-Code(s) erfolgreich gespeichert in {output_dir}.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der QR-Codes: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()
