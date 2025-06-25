import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import shutil
import zipfile
import base64
import uuid
import re

# Directorios y archivos
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
ITEMS_FILE = os.path.join(DATA_DIR, "items.json")
COLORS_FILE = os.path.join(DATA_DIR, "colors.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Imagen placeholder
PLACEHOLDER_IMAGE = os.path.join(IMAGES_DIR, "placeholder.png")
PLACEHOLDER_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYGD4DwABBAH9P5zV7gAAAABJRU5ErkJggg=="

# Colores predefinidos
TAMIYA_COLORS = {
    "X-1": {"name": "Black", "color": "#000000"},
    "XF-2": {"name": "Flat White", "color": "#F5F5F5"},
    "TS-3": {"name": "Dark Yellow", "color": "#C4A100"}
}
A_STAND_COLORS = {"A.MIG-2300": {"name": "Olive Green", "color": "#4B5320"}}
MR_HOBBY_COLORS = {"C001": {"name": "Red", "color": "#FF0000"}}
ALL_COLORS = {
    **{code: {"brand": "Tamiya", **data} for code, data in TAMIYA_COLORS.items()},
    **{code: {"brand": "A-Stand", **data} for code, data in A_STAND_COLORS.items()},
    **{code: {"brand": "Mr. Hobby", **data} for code, data in MR_HOBBY_COLORS.items()}
}

# Crear directorios y placeholder
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
if not os.path.exists(PLACEHOLDER_IMAGE):
    with open(PLACEHOLDER_IMAGE, "wb") as f:
        f.write(base64.b64decode(PLACEHOLDER_BASE64))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Base de Datos de Artículos")
        self.items = self.load_items()
        self.colors = self.load_colors()
        self.settings = self.load_settings()
        self.temp_additional_photos = []
        self.edit_added_photos = []
        self.edit_removed_photos = []
        self.setup_ui()

    def load_items(self):
        try:
            with open(ITEMS_FILE, "r") as f:
                items = json.load(f)
                print(f"Cargados {len(items)} ítems")
                return self.validate_items(items)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Inicializando ítems vacíos")
            return []

    def load_colors(self):
        try:
            with open(COLORS_FILE, "r") as f:
                existing_colors = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_colors = []
        existing_by_code = {c["code"]: c for c in existing_colors}
        colors = [
            {
                "code": code,
                "brand": ALL_COLORS[code]["brand"],
                "name": ALL_COLORS[code]["name"],
                "color": ALL_COLORS[code]["color"],
                "have": existing_by_code.get(code, {}).get("have", False),
                "buy": existing_by_code.get(code, {}).get("buy", False)
            }
            for code in sorted(ALL_COLORS.keys(), key=lambda x: (ALL_COLORS[x]["brand"], x.split("-")[0], int(x.split("-")[1] if "-" in x else x.replace("A.MIG", ""))))
        ]
        self.save_colors(colors)
        print(f"Cargados {len(colors)} colores")
        return colors

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {"item_height": 300, "items_per_row": 4, "items_per_column": 3}
            self.save_settings(settings)
            return settings

    def save_items(self):
        with open(ITEMS_FILE, "w") as f:
            json.dump(self.items, f, indent=2)
        self.clean_images()

    def save_colors(self, colors):
        with open(COLORS_FILE, "w") as f:
            json.dump(colors, f, indent=2)

    def save_settings(self, settings):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)

    def validate_items(self, items):
        valid_items = []
        invalid_count = 0
        for item in items:
            if not all([item.get("name"), item.get("code"), item.get("brand")]):
                print(f"Ítem inválido: {item}")
                invalid_count += 1
                continue
            cover_photo = item.get("coverPhoto")
            cover_photo_src = PLACEHOLDER_IMAGE
            if cover_photo and os.path.exists(os.path.join(IMAGES_DIR, cover_photo)):
                cover_photo_src = os.path.join(IMAGES_DIR, cover_photo)
            else:
                print(f"No se encontró imagen para {item['name']}: {cover_photo}")
            additional_photos = [
                photo for photo in item.get("additionalPhotos", [])
                if os.path.exists(os.path.join(IMAGES_DIR, photo))
            ]
            valid_items.append({
                **item,
                "coverPhoto": cover_photo,
                "coverPhotoSrc": cover_photo_src,
                "additionalPhotos": additional_photos
            })
        if invalid_count:
            messagebox.showwarning("Advertencia", f"Se encontraron {invalid_count} ítems inválidos.")
        print(f"Ítems válidos después de validación: {len(valid_items)}")
        return valid_items

    def store_image(self, file_path):
        if not os.path.exists(file_path):
            print(f"Archivo no encontrado: {file_path}")
            return None
        try:
            img = Image.open(file_path)
            if img.width > 800:
                img = img.resize((800, int(800 * img.height / img.width)), Image.Resampling.LANCZOS)
            file_name = f"image_{uuid.uuid4()}.jpg"
            img.save(os.path.join(IMAGES_DIR, file_name), "JPEG", quality=70)
            print(f"Imagen almacenada: {file_name}")
            return file_name
        except Exception as e:
            print(f"Error al almacenar imagen: {e}")
            return None

    def clean_images(self):
        used_images = set()
        for item in self.items:
            if item.get("coverPhoto"):
                used_images.add(item["coverPhoto"])
            for photo in item.get("additionalPhotos", []):
                used_images.add(photo)
        for file_name in os.listdir(IMAGES_DIR):
            if file_name not in used_images and file_name != "placeholder.png":
                os.remove(os.path.join(IMAGES_DIR, file_name))
                print(f"Imagen eliminada: {file_name}")

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Pestaña Añadir Objeto
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="Añadir Objeto")
        ttk.Label(self.add_frame, text="Nombre").grid(row=0, column=0, padx=5, pady=5)
        self.add_name = ttk.Entry(self.add_frame)
        self.add_name.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.add_frame, text="Código").grid(row=1, column=0, padx=5, pady=5)
        self.add_code = ttk.Entry(self.add_frame)
        self.add_code.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.add_frame, text="Marca").grid(row=2, column=0, padx=5, pady=5)
        self.add_brand = ttk.Combobox(self.add_frame, values=["Tamiya", "Hasegawa", "Fujimi", "Aoshima", "Revell", "Beemax", "Brach Model"])
        self.add_brand.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(self.add_frame, text="Foto de portada").grid(row=3, column=0, padx=5, pady=5)
        self.add_cover = ttk.Button(self.add_frame, text="Seleccionar", command=self.select_cover_photo)
        self.add_cover.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(self.add_frame, text="Fotos adicionales (máx 20)").grid(row=4, column=0, padx=5, pady=5)
        self.add_additional = ttk.Button(self.add_frame, text="Seleccionar", command=self.select_additional_photos)
        self.add_additional.grid(row=4, column=1, padx=5, pady=5)
        self.add_photos_preview = ttk.Frame(self.add_frame)
        self.add_photos_preview.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(self.add_frame, text="Añadir", command=self.add_item).grid(row=6, column=0, columnspan=2, pady=10)

        # Pestaña Galería
        self.gallery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gallery_frame, text="Galería")
        self.gallery_canvas = tk.Canvas(self.gallery_frame)
        self.gallery_scroll = ttk.Scrollbar(self.gallery_frame, orient="vertical", command=self.gallery_canvas.yview)
        self.gallery_scroll.pack(side="right", fill="y")
        self.gallery_canvas.pack(side="left", fill="both", expand=True)
        self.gallery_canvas.configure(yscrollcommand=self.gallery_scroll.set)
        self.gallery_inner = ttk.Frame(self.gallery_canvas)
        self.gallery_canvas.create_window((0, 0), window=self.gallery_inner, anchor="nw")
        self.gallery_inner.bind("<Configure>", lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all")))
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Pestaña Colores
        self.colors_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.colors_frame, text="Colores")
        ttk.Label(self.colors_frame, text="Marca").grid(row=0, column=0, padx=5, pady=5)
        self.brand_filter = ttk.Combobox(self.colors_frame, values=["Todas", "Tamiya", "A-Stand", "Mr. Hobby"])
        self.brand_filter.grid(row=0, column=1, padx=5, pady=5)
        self.brand_filter.bind("<<ComboboxSelected>>", lambda e: self.load_colors_tab())
        ttk.Label(self.colors_frame, text="Prefijo").grid(row=1, column=0, padx=5, pady=5)
        self.color_filter = ttk.Combobox(self.colors_frame, values=["Todos", "X", "XF", "TS", "A.MIG", "C"])
        self.color_filter.grid(row=1, column=1, padx=5, pady=5)
        self.color_filter.bind("<<ComboboxSelected>>", lambda e: self.load_colors_tab())
        ttk.Label(self.colors_frame, text="Buscar").grid(row=2, column=0, padx=5, pady=5)
        self.color_search = ttk.Entry(self.colors_frame)
        self.color_search.grid(row=2, column=1, padx=5, pady=5)
        self.color_search.bind("<KeyRelease>", lambda e: self.load_colors_tab())
        self.colors_list = ttk.Frame(self.colors_frame)
        self.colors_list.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Pestaña Configuración
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Configuración")
        ttk.Button(self.settings_frame, text="Exportar Datos", command=self.export_data).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.settings_frame, text="Importar Datos", command=self.import_data).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.settings_frame, text="Configurar Galería", command=self.show_gallery_settings).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.settings_frame, text="Limpiar Imágenes", command=self.clear_images).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.settings_frame, text="Exportar Imágenes como ZIP", command=self.export_images).grid(row=4, column=0, padx=5, pady=5)

    def select_cover_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if file_path:
            self.add_cover.config(text=os.path.basename(file_path))
            self.add_cover.file_path = file_path

    def select_additional_photos(self):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if len(self.temp_additional_photos) + len(files) > 20:
            messagebox.showerror("Error", "Máximo 20 fotos adicionales.")
            return
        self.temp_additional_photos.extend(files)
        self.update_photos_preview()

    def update_photos_preview(self):
        for widget in self.add_photos_preview.winfo_children():
            widget.destroy()
        for i, file_path in enumerate(self.temp_additional_photos):
            img = Image.open(file_path).resize((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            frame = ttk.Frame(self.add_photos_preview)
            frame.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            label = ttk.Label(frame, image=photo)
            label.image = photo
            label.pack()
            btn = ttk.Button(frame, text="×", command=lambda i=i: self.remove_additional_photo(i))
            btn.pack()

    def remove_additional_photo(self, index):
        self.temp_additional_photos.pop(index)
        self.update_photos_preview()

    def add_item(self):
        if len(self.items) >= 1000:
            messagebox.showerror("Error", "Límite de 1000 ítems alcanzado.")
            return
        name = self.add_name.get().strip()
        code = self.add_code.get().strip()
        brand = self.add_brand.get()
        cover_file = getattr(self.add_cover, "file_path", None)
        if not all([name, code, brand, cover_file]):
            messagebox.showerror("Error", "Por favor, completa todos los campos y selecciona una foto de portada.")
            return
        cover_photo = self.store_image(cover_file)
        if not cover_photo:
            messagebox.showerror("Error", "Error al almacenar la foto de portada.")
            return
        additional_photos = [self.store_image(file) for file in self.temp_additional_photos]
        additional_photos = [p for p in additional_photos if p]
        self.items.append({
            "name": name,
            "code": code,
            "brand": brand,
            "coverPhoto": cover_photo,
            "coverPhotoSrc": os.path.join(IMAGES_DIR, cover_photo),
            "additionalPhotos": additional_photos,
            "colors": []
        })
        self.save_items()
        self.add_name.delete(0, tk.END)
        self.add_code.delete(0, tk.END)
        self.add_brand.set("")
        self.add_cover.config(text="Seleccionar")
        self.temp_additional_photos = []
        self.update_photos_preview()
        self.notebook.select(self.gallery_frame)
        self.load_gallery()
        print(f"Ítem añadido: {name}")

    def load_gallery(self):
        self.items = self.validate_items(self.items)
        for widget in self.gallery_inner.winfo_children():
            widget.destroy()
        max_items = 100
        if len(self.items) > max_items:
            print(f"Advertencia: Se encontraron {len(self.items)} ítems, mostrando solo {max_items}")
        for i, item in enumerate(self.items[:max_items]):
            frame = ttk.Frame(self.gallery_inner)
            frame.grid(row=i // self.settings["items_per_row"], column=i % self.settings["items_per_row"], padx=10, pady=10)
            img = Image.open(item["coverPhotoSrc"]).resize((200, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(frame, image=photo)
            label.image = photo
            label.pack()
            label.bind("<Button-1>", lambda e, i=i: self.open_popup(i))
            ttk.Label(frame, text=item["name"]).pack()
            ttk.Button(frame, text="✎", command=lambda i=i: self.edit_item(i)).pack(side="left")
            ttk.Button(frame, text="×", command=lambda i=i: self.delete_item(i)).pack(side="right")
        print(f"Renderizados {len(self.items[:max_items])} ítems en la galería")

    def delete_item(self, index):
        if messagebox.askyesno("Confirmar", f"¿Eliminar {self.items[index]['name']}?"):
            self.items.pop(index)
            self.save_items()
            self.load_gallery()

    def edit_item(self, index):
        item = self.items[index]
        self.edit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_frame, text="Editar Objeto")
        self.notebook.select(self.edit_frame)
        ttk.Label(self.edit_frame, text="Nombre").grid(row=0, column=0, padx=5, pady=5)
        edit_name = ttk.Entry(self.edit_frame)
        edit_name.grid(row=0, column=1, padx=5, pady=5)
        edit_name.insert(0, item["name"])
        ttk.Label(self.edit_frame, text="Código").grid(row=1, column=0, padx=5, pady=5)
        edit_code = ttk.Entry(self.edit_frame)
        edit_code.grid(row=1, column=1, padx=5, pady=5)
        edit_code.insert(0, item["code"])
        ttk.Label(self.edit_frame, text="Marca").grid(row=2, column=0, padx=5, pady=5)
        edit_brand = ttk.Combobox(self.edit_frame, values=["Tamiya", "Hasegawa", "Fujimi", "Aoshima", "Revell", "Beemax", "Brach Model"])
        edit_brand.grid(row=2, column=1, padx=5, pady=5)
        edit_brand.set(item["brand"])
        ttk.Label(self.edit_frame, text="Foto de portada").grid(row=3, column=0, padx=5, pady=5)
        edit_cover = ttk.Button(self.edit_frame, text="Seleccionar", command=lambda: self.select_edit_cover(edit_cover))
        edit_cover.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(self.edit_frame, text="Fotos adicionales").grid(row=4, column=0, padx=5, pady=5)
        edit_additional = ttk.Button(self.edit_frame, text="Seleccionar", command=lambda: self.select_edit_additional(index))
        edit_additional.grid(row=4, column=1, padx=5, pady=5)
        self.edit_photos_preview = ttk.Frame(self.edit_frame)
        self.edit_photos_preview.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.edit_added_photos = item["additionalPhotos"].copy()
        self.edit_removed_photos = []
        self.update_edit_photos_preview()
        ttk.Button(self.edit_frame, text="Guardar", command=lambda: self.save_edit(index, edit_name, edit_code, edit_brand, edit_cover)).grid(row=6, column=0, pady=10)
        ttk.Button(self.edit_frame, text="Cancelar", command=self.cancel_edit).grid(row=6, column=1, pady=10)

    def select_edit_cover(self, button):
        file_path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if file_path:
            button.config(text=os.path.basename(file_path))
            button.file_path = file_path

    def select_edit_additional(self, index):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if len(self.edit_added_photos) + len(files) > 20:
            messagebox.showerror("Error", "Máximo 20 fotos adicionales.")
            return
        self.edit_added_photos.extend([f for f in files if f not in self.edit_added_photos])
        self.update_edit_photos_preview()

    def update_edit_photos_preview(self):
        for widget in self.edit_photos_preview.winfo_children():
            widget.destroy()
        for i, file_path in enumerate(self.edit_added_photos):
            img = Image.open(os.path.join(IMAGES_DIR, file_path) if os.path.exists(os.path.join(IMAGES_DIR, file_path)) else file_path).resize((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            frame = ttk.Frame(self.edit_photos_preview)
            frame.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            label = ttk.Label(frame, image=photo)
            label.image = photo
            label.pack()
            btn = ttk.Button(frame, text="×", command=lambda i=i: self.remove_edit_additional(i))
            btn.pack()

    def remove_edit_additional(self, index):
        self.edit_removed_photos.append(self.edit_added_photos.pop(index))
        self.update_edit_photos_preview()

    def save_edit(self, index, name_entry, code_entry, brand_entry, cover_button):
        name = name_entry.get().strip()
        code = code_entry.get().strip()
        brand = brand_entry.get()
        cover_file = getattr(cover_button, "file_path", None)
        if not all([name, code, brand]):
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return
        item = self.items[index]
        item["name"] = name
        item["code"] = code
        item["brand"] = brand
        if cover_file:
            cover_photo = self.store_image(cover_file)
            if cover_photo:
                item["coverPhoto"] = cover_photo
                item["coverPhotoSrc"] = os.path.join(IMAGES_DIR, cover_photo)
        item["additionalPhotos"] = [p for p in item["additionalPhotos"] if p not in self.edit_removed_photos]
        item["additionalPhotos"].extend([self.store_image(f) for f in self.edit_added_photos if f not in item["additionalPhotos"] and os.path.exists(f)])
        item["additionalPhotos"] = [p for p in item["additionalPhotos"] if p]
        self.save_items()
        self.cancel_edit()
        self.load_gallery()

    def cancel_edit(self):
        self.notebook.forget(self.edit_frame)
        self.notebook.select(self.gallery_frame)
        self.load_gallery()

    def open_popup(self, index):
        item = self.items[index]
        popup = tk.Toplevel(self.root)
        popup.title(item["name"])
        ttk.Label(popup, text=item["name"]).pack(pady=5)
        ttk.Label(popup, text=f"Código: {item['code']} | Marca: {item['brand']}").pack(pady=5)
        thumbnails_frame = ttk.Frame(popup)
        thumbnails_frame.pack(side="left", padx=10)
        preview_frame = ttk.Frame(popup)
        preview_frame.pack(side="left", padx=10)
        img = Image.open(item["coverPhotoSrc"]).resize((400, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        preview_label = ttk.Label(preview_frame, image=photo)
        preview_label.image = photo
        preview_label.pack()
        ttk.Button(preview_frame, text="Ver Colores", command=lambda: self.show_colors_modal(index)).pack(side="left", padx=5)
        ttk.Button(preview_frame, text="Añadir Colores", command=lambda: self.show_colors_form(index)).pack(side="left", padx=5)
        all_photos = [item["coverPhotoSrc"]] + [os.path.join(IMAGES_DIR, p) for p in item["additionalPhotos"]]
        for i, photo in enumerate(all_photos):
            img = Image.open(photo).resize((80, 80), Image.Resampling.LANCZOS)
            thumb_photo = ImageTk.PhotoImage(img)
            thumb_label = ttk.Label(thumbnails_frame, image=thumb_photo)
            thumb_label.image = thumb_photo
            thumb_label.pack(pady=5)
            thumb_label.bind("<Button-1>", lambda e, p=photo: self.update_preview(preview_label, p))

    def update_preview(self, label, photo_path):
        img = Image.open(photo_path).resize((400, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo

    def show_colors_modal(self, index):
        item = self.items[index]
        modal = tk.Toplevel(self.root)
        modal.title("Colores Asociados")
        for code in item.get("colors", []):
            color = next((c for c in self.colors if c["code"] == code), None)
            if not color:
                continue
            frame = ttk.Frame(modal)
            frame.pack(fill="x", padx=5, pady=5)
            ttk.Label(frame, text=f"{color['code']} - {color['name']} ({color['brand']})").pack(side="left")
            status = "Tengo" if color["have"] else "Comprar"
            ttk.Label(frame, text=status).pack(side="left", padx=10)
            ttk.Button(frame, text="×", command=lambda c=code: self.remove_color(index, c)).pack(side="right")

    def remove_color(self, index, code):
        self.items[index]["colors"].remove(code)
        self.save_items()
        self.notebook.select(self.gallery_frame)
        self.load_gallery()

    def show_colors_form(self, index):
        modal = tk.Toplevel(self.root)
        modal.title("Añadir Colores")
        ttk.Label(modal, text="Códigos (uno por línea, ej: X-1, TS-3)").pack(pady=5)
        colors_input = tk.Text(modal, height=5, width=30)
        colors_input.pack(pady=5)
        ttk.Button(modal, text="Guardar", command=lambda: self.save_colors(index, colors_input.get("1.0", tk.END))).pack(side="left", padx=5)
        ttk.Button(modal, text="Cancelar", command=modal.destroy).pack(side="left", padx=5)

    def save_colors(self, index, input_text):
        codes = [self.normalize_code(c) for c in input_text.strip().split("\n")]
        valid_codes = [c for c in codes if c and c in ALL_COLORS]
        if not valid_codes:
            messagebox.showerror("Error", "No se encontraron códigos válidos.")
            return
        self.items[index]["colors"] = list(set(self.items[index].get("colors", []) + valid_codes))
        self.save_items()
        self.notebook.select(self.gallery_frame)
        self.load_gallery()

    def normalize_code(self, code):
        if not code:
            return None
        normalized = code.strip().upper().replace(".", "-")
        return normalized if re.match(r"^(X|XF|LP|TS|A-MIG|C)-?\d+$", normalized) else None

    def load_colors_tab(self):
        for widget in self.colors_list.winfo_children():
            widget.destroy()
        brand_filter = self.brand_filter.get()
        color_filter = self.color_filter.get()
        search = self.color_search.get().lower()
        filtered_colors = self.colors
        if brand_filter != "Todas":
            filtered_colors = [c for c in filtered_colors if c["brand"] == brand_filter]
        if color_filter != "Todos":
            filtered_colors = [c for c in filtered_colors if c["code"].startswith(color_filter)]
        if search:
            filtered_colors = [c for c in filtered_colors if search in c["code"].lower() or search in c["name"].lower()]
        for i, color in enumerate(filtered_colors):
            frame = ttk.Frame(self.colors_list)
            frame.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            ttk.Label(frame, text=f"{color['code']} - {color['name']} ({color['brand']})").pack(side="left")
            have_var = tk.BooleanVar(value=color["have"])
            ttk.Checkbutton(frame, text="Tengo", variable=have_var, command=lambda c=color: self.update_color(c, "have", have_var.get())).pack(side="left", padx=5)
            buy_var = tk.BooleanVar(value=color["buy"])
            ttk.Checkbutton(frame, text="Comprar", variable=buy_var, command=lambda c=color: self.update_color(c, "buy", buy_var.get())).pack(side="left", padx=5)
        print(f"Colores renderizados: {len(filtered_colors)}")

    def update_color(self, color, field, value):
        color[field] = value
        if field == "have" and value:
            color["buy"] = False
        self.save_colors(self.colors)
        self.load_colors_tab()

    def export_data(self):
        data = {
            "items": self.items,
            "colors": self.colors,
            "settings": self.settings
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            print("Datos exportados")

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            if data.get("items"):
                self.items = self.validate_items(data["items"])
                self.save_items()
            if data.get("colors"):
                self.colors = [c for c in data["colors"] if c.get("code")]
                self.save_colors(self.colors)
            if data.get("settings"):
                self.settings = data["settings"]
                self.save_settings(self.settings)
            self.load_gallery()
            self.load_colors_tab()
            messagebox.showinfo("Éxito", f"Datos importados. {len(self.items)} ítems válidos cargados.")
            print(f"Datos importados: ítems={len(self.items)}, colores={len(self.colors)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar datos: {e}")
            print(f"Error al importar: {e}")

    def show_gallery_settings(self):
        modal = tk.Toplevel(self.root)
        modal.title("Configuración de Galería")
        ttk.Label(modal, text="Alto de ítems (px)").pack(pady=5)
        item_height = ttk.Entry(modal)
        item_height.insert(0, self.settings["item_height"])
        item_height.pack(pady=5)
        ttk.Label(modal, text="Ítems por fila").pack(pady=5)
        items_per_row = ttk.Entry(modal)
        items_per_row.insert(0, self.settings["items_per_row"])
        items_per_row.pack(pady=5)
        ttk.Label(modal, text="Ítems por columna").pack(pady=5)
        items_per_column = ttk.Entry(modal)
        items_per_column.insert(0, self.settings["items_per_column"])
        items_per_column.pack(pady=5)
        ttk.Button(modal, text="Guardar", command=lambda: self.save_gallery_settings(item_height.get(), items_per_row.get(), items_per_column.get())).pack(side="left", padx=5)
        ttk.Button(modal, text="Cancelar", command=modal.destroy).pack(side="left", padx=5)

    def save_gallery_settings(self, item_height, items_per_row, items_per_column):
        try:
            self.settings = {
                "item_height": int(item_height),
                "items_per_row": int(items_per_row),
                "items_per_column": int(items_per_column)
            }
            self.save_settings(self.settings)
            self.load_gallery()
            print("Configuración de galería guardada")
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos.")

    def clear_images(self):
        if messagebox.askyesno("Confirmar", "¿Eliminar todas las imágenes?"):
            self.items = [{
                **item,
                "coverPhoto": None,
                "coverPhotoSrc": PLACEHOLDER_IMAGE,
                "additionalPhotos": []
            } for item in self.items]
            for file_name in os.listdir(IMAGES_DIR):
                if file_name != "placeholder.png":
                    os.remove(os.path.join(IMAGES_DIR, file_name))
            self.save_items()
            self.load_gallery()
            print("Imágenes limpiadas")

    def export_images(self):
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP", "*.zip")])
        if not zip_path:
            return
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_name in os.listdir(IMAGES_DIR):
                zipf.write(os.path.join(IMAGES_DIR, file_name), file_name)
        print("Imágenes exportadas como ZIP")

    def on_tab_change(self, event):
        tab = self.notebook.tab(self.notebook.select(), "text")
        if tab == "Galería":
            self.load_gallery()
        elif tab == "Colores":
            self.load_colors_tab()
        print(f"Pestaña cambiada a: {tab}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()