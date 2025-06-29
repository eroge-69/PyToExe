"""
Image Merger Tool - Bilder zusammenfügen
Erstellt eine GUI zum Auswählen, Anordnen und Zusammenfügen von Bildern
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path


class ImageMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bilder Zusammenfügen Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variablen
        self.selected_images = []
        self.preview_images = []
        self.merge_direction = tk.StringVar(value="horizontal")

        self.setup_ui()

    def setup_ui(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Konfiguration für responsive Layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Titel
        title_label = ttk.Label(main_frame, text="Bilder Zusammenfügen Tool",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Kontrollbereich
        control_frame = ttk.LabelFrame(main_frame, text="Einstellungen", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Richtung auswählen
        ttk.Label(control_frame, text="Zusammenfügen:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        direction_frame = ttk.Frame(control_frame)
        direction_frame.grid(row=0, column=1, sticky=tk.W)

        ttk.Radiobutton(direction_frame, text="Horizontal (nebeneinander)",
                        variable=self.merge_direction, value="horizontal",
                        command=self.update_preview).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(direction_frame, text="Vertikal (untereinander)",
                        variable=self.merge_direction, value="vertical",
                        command=self.update_preview).pack(side=tk.LEFT)

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)

        ttk.Button(button_frame, text="Bilder hinzufügen",
                   command=self.add_images).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Alle entfernen",
                   command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Zusammenfügen & Speichern",
                   command=self.merge_and_save,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))

        # Bilderliste mit Vorschau
        list_frame = ttk.LabelFrame(main_frame, text="Ausgewählte Bilder (Reihenfolge ändern durch Drag & Drop)",
                                    padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Listbox mit Scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.image_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        self.image_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.image_listbox.configure(yscrollcommand=v_scrollbar.set)

        # Reihenfolge-Buttons
        order_frame = ttk.Frame(list_frame)
        order_frame.grid(row=1, column=0, pady=(10, 0))

        ttk.Button(order_frame, text="↑ Nach oben",
                   command=self.move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(order_frame, text="↓ Nach unten",
                   command=self.move_down).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(order_frame, text="Entfernen",
                   command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))

        # Vorschau
        preview_frame = ttk.LabelFrame(main_frame, text="Vorschau", padding="10")
        preview_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Canvas für Vorschau mit Scrollbars
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(canvas_frame, bg="white", width=400, height=300)
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Canvas Scrollbars
        canvas_v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        canvas_v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas_h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        canvas_h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.preview_canvas.configure(yscrollcommand=canvas_v_scroll.set, xscrollcommand=canvas_h_scroll.set)

    def add_images(self):
        """Bilder zum Zusammenfügen hinzufügen"""
        filetypes = [
            ("Alle Bildformate", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("Alle Dateien", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="Bilder auswählen",
            filetypes=filetypes
        )

        for file_path in files:
            if file_path not in self.selected_images:
                self.selected_images.append(file_path)
                filename = os.path.basename(file_path)
                self.image_listbox.insert(tk.END, filename)

        self.update_preview()

    def clear_all(self):
        """Alle Bilder entfernen"""
        self.selected_images.clear()
        self.image_listbox.delete(0, tk.END)
        self.preview_canvas.delete("all")
        self.preview_images.clear()

    def remove_selected(self):
        """Ausgewähltes Bild entfernen"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_images.pop(index)
            self.image_listbox.delete(index)
            self.update_preview()

    def move_up(self):
        """Ausgewähltes Bild nach oben verschieben"""
        selection = self.image_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # In Liste verschieben
            self.selected_images[index], self.selected_images[index - 1] = \
                self.selected_images[index - 1], self.selected_images[index]

            # In Listbox verschieben
            item = self.image_listbox.get(index)
            self.image_listbox.delete(index)
            self.image_listbox.insert(index - 1, item)
            self.image_listbox.selection_set(index - 1)

            self.update_preview()

    def move_down(self):
        """Ausgewähltes Bild nach unten verschieben"""
        selection = self.image_listbox.curselection()
        if selection and selection[0] < len(self.selected_images) - 1:
            index = selection[0]
            # In Liste verschieben
            self.selected_images[index], self.selected_images[index + 1] = \
                self.selected_images[index + 1], self.selected_images[index]

            # In Listbox verschieben
            item = self.image_listbox.get(index)
            self.image_listbox.delete(index)
            self.image_listbox.insert(index + 1, item)
            self.image_listbox.selection_set(index + 1)

            self.update_preview()

    def update_preview(self):
        """Vorschau aktualisieren"""
        self.preview_canvas.delete("all")

        if not self.selected_images:
            return

        try:
            # Bilder laden und skalieren für Vorschau
            preview_images = []
            max_preview_size = 150

            for img_path in self.selected_images:
                img = Image.open(img_path)
                # Skalieren für Vorschau
                img.thumbnail((max_preview_size, max_preview_size), Image.Resampling.LANCZOS)
                preview_images.append(img)

            # Zusammengefügtes Bild erstellen
            if self.merge_direction.get() == "horizontal":
                total_width = sum(img.width for img in preview_images)
                max_height = max(img.height for img in preview_images)
                merged_img = Image.new("RGB", (total_width, max_height), "white")

                x_offset = 0
                for img in preview_images:
                    y_offset = (max_height - img.height) // 2
                    merged_img.paste(img, (x_offset, y_offset))
                    x_offset += img.width
            else:  # vertical
                max_width = max(img.width for img in preview_images)
                total_height = sum(img.height for img in preview_images)
                merged_img = Image.new("RGB", (max_width, total_height), "white")

                y_offset = 0
                for img in preview_images:
                    x_offset = (max_width - img.width) // 2
                    merged_img.paste(img, (x_offset, y_offset))
                    y_offset += img.height

            # Für Canvas konvertieren
            self.preview_tk_img = ImageTk.PhotoImage(merged_img)
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_tk_img)

            # Scroll-Region setzen
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Vorschau: {str(e)}")

    def merge_and_save(self):
        """Bilder zusammenfügen und speichern"""
        if not self.selected_images:
            messagebox.showwarning("Warnung", "Bitte wählen Sie mindestens ein Bild aus.")
            return

        # Speicherort auswählen
        save_path = filedialog.asksaveasfilename(
            title="Zusammengefügtes Bild speichern",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg"),
                ("PNG", "*.png"),
                ("TIFF", "*.tiff"),
                ("BMP", "*.bmp")
            ]
        )

        if not save_path:
            return

        try:
            # Bilder in Originalgröße laden
            images = []
            for img_path in self.selected_images:
                img = Image.open(img_path)
                # Konvertiere zu RGB falls nötig
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)

            # Zusammenfügen
            if self.merge_direction.get() == "horizontal":
                total_width = sum(img.width for img in images)
                max_height = max(img.height for img in images)
                merged_image = Image.new("RGB", (total_width, max_height), "white")

                x_offset = 0
                for img in images:
                    y_offset = (max_height - img.height) // 2
                    merged_image.paste(img, (x_offset, y_offset))
                    x_offset += img.width
            else:  # vertical
                max_width = max(img.width for img in images)
                total_height = sum(img.height for img in images)
                merged_image = Image.new("RGB", (max_width, total_height), "white")

                y_offset = 0
                for img in images:
                    x_offset = (max_width - img.width) // 2
                    merged_image.paste(img, (x_offset, y_offset))
                    y_offset += img.height

            # Speichern
            merged_image.save(save_path, quality=95)
            messagebox.showinfo("Erfolg", f"Bild erfolgreich gespeichert unter:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")


def main():
    root = tk.Tk()
    app = ImageMergerApp(root)

    # Icon setzen (optional, falls vorhanden)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass

    root.mainloop()


if __name__ == "__main__":
    main()
