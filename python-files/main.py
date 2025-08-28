import os
import json
import uuid
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Marketplace Assistant (Prototype)"
DATA_FILE = "posts.json"
SETTINGS_FILE = "settings.json"

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("980x640")
        self.minsize(920, 560)
        self.configure(bg="#f7f7fb")
        self.posts = load_json(DATA_FILE, [])
        self.settings = load_json(SETTINGS_FILE, {
            "weak_clicks_threshold": 5,
            "weak_messages_threshold": 1,
            "auto_renew_hours": 48
        })

        self._build_layout()

    # -------- Layout ----------
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = tk.Frame(self, bg="#ffffff", bd=0, highlightthickness=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.configure(width=220)
        for i in range(8):
            sidebar.grid_rowconfigure(i, weight=0)
        sidebar.grid_rowconfigure(9, weight=1)

        title = tk.Label(sidebar, text="Marketplace Bot", bg="#ffffff", fg="#111827",
                         font=("Segoe UI Semibold", 16))
        title.grid(padx=16, pady=(16, 8), sticky="w")

        self.menu_buttons = {}
        for i, (key, label) in enumerate([
            ("publish", "📤 Publicar"),
            ("renew", "♻️ Renovar"),
            ("delete", "❌ Eliminar"),
            ("analytics", "📊 Analítica"),
            ("settings", "⚙️ Ajustes"),
        ]):
            btn = tk.Button(sidebar, text=label, anchor="w",
                            font=("Segoe UI", 11), relief="flat", bd=0,
                            bg="#ffffff", fg="#111827",
                            activebackground="#eef2ff", activeforeground="#111827",
                            command=lambda k=key: self.show_panel(k))
            btn.grid(row=i+1, column=0, sticky="ew", padx=12, pady=4, ipadx=8, ipady=8)
            self.menu_buttons[key] = btn

        # Footer
        footer = tk.Label(sidebar, text="Prototipo • No publica aún",
                          bg="#ffffff", fg="#6b7280", font=("Segoe UI", 9))
        footer.grid(row=9, column=0, padx=16, pady=16, sticky="sw")

        # Main content container
        self.container = tk.Frame(self, bg="#f7f7fb")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Panels
        self.panels = {
            "publish": self._build_publish_panel(),
            "renew": self._build_renew_panel(),
            "delete": self._build_delete_panel(),
            "analytics": self._build_analytics_panel(),
            "settings": self._build_settings_panel(),
        }
        self.show_panel("publish")

    def _panel_wrapper(self, title_text):
        panel = tk.Frame(self.container, bg="#f7f7fb")
        header = tk.Frame(panel, bg="#f7f7fb")
        header.pack(fill="x", padx=20, pady=(20, 10))
        title = tk.Label(header, text=title_text, bg="#f7f7fb", fg="#111827",
                         font=("Segoe UI Semibold", 18))
        title.pack(side="left")
        body = tk.Frame(panel, bg="#ffffff")
        body.pack(fill="both", expand=True, padx=20, pady=10)
        body.grid_columnconfigure(0, weight=1)
        return panel, body

    # -------- Publish Panel --------
    def _build_publish_panel(self):
        panel, body = self._panel_wrapper("📤 Publicar en Marketplace")

        form = tk.Frame(body, bg="#ffffff")
        form.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        body.grid_rowconfigure(0, weight=1)

        # Title
        tk.Label(form, text="Título", bg="#ffffff", fg="#374151", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        tk.Entry(form, textvariable=self.title_var, font=("Segoe UI", 11), bd=1, relief="solid").grid(row=1, column=0, sticky="ew", pady=(0,10))
        # Price
        tk.Label(form, text="Precio (USD)", bg="#ffffff", fg="#374151", font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", padx=(12,0))
        self.price_var = tk.StringVar()
        tk.Entry(form, textvariable=self.price_var, font=("Segoe UI", 11), bd=1, relief="solid").grid(row=1, column=1, sticky="ew", padx=(12,0), pady=(0,10))

        # Category
        tk.Label(form, text="Categoría", bg="#ffffff", fg="#374151", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w")
        self.category_var = tk.StringVar()
        categories = ["Servicios", "Electrónica", "Hogar", "Vehículos", "Empleos", "Otros"]
        self.category_cb = ttk.Combobox(form, values=categories, textvariable=self.category_var, state="readonly")
        self.category_cb.grid(row=3, column=0, sticky="ew", pady=(0,10))

        # Description
        tk.Label(form, text="Descripción", bg="#ffffff", fg="#374151", font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", padx=(12,0))
        self.desc_txt = tk.Text(form, height=8, bd=1, relief="solid", font=("Segoe UI", 10))
        self.desc_txt.grid(row=3, column=1, sticky="nsew", padx=(12,0), pady=(0,10))

        # Images
        img_frame = tk.Frame(form, bg="#f9fafb", bd=1, relief="solid")
        img_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0,10))
        img_frame.grid_columnconfigure(0, weight=1)
        tk.Label(img_frame, text="Fotos seleccionadas:", bg="#f9fafb", fg="#374151", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.images_list = tk.Listbox(img_frame, height=4, bd=0)
        self.images_list.grid(row=1, column=0, sticky="ew", padx=8, pady=(0,8))
        btns = tk.Frame(img_frame, bg="#f9fafb")
        btns.grid(row=0, column=1, rowspan=2, sticky="ns", padx=8)
        tk.Button(btns, text="➕ Agregar", command=self.add_images).pack(fill="x", pady=(8,4))
        tk.Button(btns, text="🗑️ Quitar", command=self.remove_selected_images).pack(fill="x")

        # Publish button
        publish_btn = tk.Button(form, text="PUBLICAR (MODO DEMO)", font=("Segoe UI Semibold", 12),
                                bg="#4f46e5", fg="white", activebackground="#4338ca", activeforeground="white",
                                command=self.mock_publish)
        publish_btn.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6,0))

        # column weighting
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)
        form.grid_rowconfigure(3, weight=1)

        return panel

    def add_images(self):
        files = filedialog.askopenfilenames(title="Selecciona imágenes",
                                            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp")])
        for f in files:
            self.images_list.insert("end", f)

    def remove_selected_images(self):
        for i in reversed(self.images_list.curselection()):
            self.images_list.delete(i)

    def mock_publish(self):
        title = self.title_var.get().strip()
        price = self.price_var.get().strip()
        category = self.category_var.get().strip() or "Otros"
        desc = self.desc_txt.get("1.0", "end").strip()
        images = list(self.images_list.get(0, "end"))

        if not title:
            messagebox.showwarning("Falta título", "Por favor, ingresa un título.")
            return
        if not price or not price.replace(".", "", 1).isdigit():
            messagebox.showwarning("Precio inválido", "Ingresa un precio numérico válido (ej. 19.99).")
            return

        post = {
            "id": str(uuid.uuid4()),
            "title": title,
            "price": float(price),
            "category": category,
            "description": desc,
            "images": images,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "clicks": 0,
            "messages": 0,
            "status": "active"
        }
        self.posts.append(post)
        save_json(DATA_FILE, self.posts)
        self.refresh_tables()
        messagebox.showinfo("Publicado (DEMO)", "Se creó la publicación en modo DEMO.\n(La automatización real se agregará en la siguiente versión).")

        # reset form
        self.title_var.set("")
        self.price_var.set("")
        self.category_var.set("")
        self.desc_txt.delete("1.0", "end")
        self.images_list.delete(0, "end")

    # -------- Renew Panel --------
    def _build_renew_panel(self):
        panel, body = self._panel_wrapper("♻️ Renovar publicaciones")

        self.renew_table = self._make_table(body, ["Título", "Precio", "Clicks", "Mensajes", "Actualizado"], stretch_cols=[0])
        self.renew_table.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        btns = tk.Frame(body, bg="#ffffff")
        btns.pack(fill="x", padx=16, pady=12)
        tk.Button(btns, text="Renovar seleccionadas (DEMO)", command=self.mock_renew_selected).pack(side="left")
        tk.Button(btns, text="Renovar todas (DEMO)", command=self.mock_renew_all).pack(side="left", padx=8)

        return panel

    def mock_renew_selected(self):
        selected = self.renew_table.selection()
        if not selected:
            messagebox.showinfo("Nada seleccionado", "Selecciona al menos una publicación.")
            return
        ids = [self.renew_table.set(i, "id") for i in selected]
        count = 0
        for p in self.posts:
            if p["id"] in ids and p["status"] == "active":
                p["updated_at"] = datetime.datetime.now().isoformat()
                count += 1
        save_json(DATA_FILE, self.posts)
        self.refresh_tables()
        messagebox.showinfo("Renovadas", f"Se renovaron {count} publicaciones (DEMO).")

    def mock_renew_all(self):
        count = 0
        for p in self.posts:
            if p["status"] == "active":
                p["updated_at"] = datetime.datetime.now().isoformat()
                count += 1
        save_json(DATA_FILE, self.posts)
        self.refresh_tables()
        messagebox.showinfo("Renovadas", f"Se renovaron {count} publicaciones (DEMO).")

    # -------- Delete Panel --------
    def _build_delete_panel(self):
        panel, body = self._panel_wrapper("❌ Eliminar publicaciones")

        self.delete_table = self._make_table(body, ["Título", "Precio", "Clicks", "Mensajes", "Estado"], stretch_cols=[0])
        self.delete_table.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        btns = tk.Frame(body, bg="#ffffff")
        btns.pack(fill="x", padx=16, pady=12)
        tk.Button(btns, text="Eliminar seleccionadas", command=self.delete_selected).pack(side="left")
        tk.Button(btns, text="Eliminar todas", command=self.delete_all).pack(side="left", padx=8)

        return panel

    def delete_selected(self):
        selected = self.delete_table.selection()
        if not selected:
            messagebox.showinfo("Nada seleccionado", "Selecciona al menos una publicación.")
            return
        ids = [self.delete_table.set(i, "id") for i in selected]
        before = len(self.posts)
        self.posts = [p for p in self.posts if p["id"] not in ids]
        save_json(DATA_FILE, self.posts)
        self.refresh_tables()
        messagebox.showinfo("Eliminadas", f"Se eliminaron {before - len(self.posts)} publicaciones.")

    def delete_all(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar TODAS las publicaciones?"):
            self.posts = []
            save_json(DATA_FILE, self.posts)
            self.refresh_tables()
            messagebox.showinfo("Eliminadas", "Se eliminaron todas las publicaciones.")

    # -------- Analytics Panel --------
    def _build_analytics_panel(self):
        panel, body = self._panel_wrapper("📊 Analítica y optimización")

        self.analytics_table = self._make_table(body, ["Título", "Clicks", "Mensajes", "Fuerza"], stretch_cols=[0])
        self.analytics_table.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        btns = tk.Frame(body, bg="#ffffff")
        btns.pack(fill="x", padx=16, pady=12)
        tk.Button(btns, text="Simular tráfico (añadir clicks/mensajes)", command=self.simulate_traffic).pack(side="left")
        tk.Button(btns, text="Optimizar automáticamente", command=self.optimize_auto).pack(side="left", padx=8)

        return panel

    def simulate_traffic(self):
        # Simple simulation: increment random-ish small amounts
        changed = 0
        for p in self.posts:
            if p["status"] == "active":
                p["clicks"] += 1
                if p["clicks"] % 3 == 0:
                    p["messages"] += 1
                changed += 1
        if changed:
            save_json(DATA_FILE, self.posts)
            self.refresh_tables()
            messagebox.showinfo("Simulado", f"Se actualizaron métricas de {changed} publicaciones.")
        else:
            messagebox.showinfo("Sin publicaciones", "No hay publicaciones activas para simular.")

    def optimize_auto(self):
        weak_c = self.settings.get("weak_clicks_threshold", 5)
        weak_m = self.settings.get("weak_messages_threshold", 1)

        kept, removed, re_posted = 0, 0, 0
        new_posts = []
        for p in self.posts:
            strong = (p["clicks"] >= weak_c) or (p["messages"] >= weak_m)
            if strong:
                kept += 1
                new_posts.append(p)
            else:
                removed += 1
                # "Re-create" with a refreshed timestamp and reset metrics (demo of re-posting)
                new_p = p.copy()
                new_p["id"] = str(uuid.uuid4())
                new_p["created_at"] = datetime.datetime.now().isoformat()
                new_p["updated_at"] = datetime.datetime.now().isoformat()
                new_p["clicks"] = 0
                new_p["messages"] = 0
                new_posts.append(new_p)
                re_posted += 1

        self.posts = new_posts
        save_json(DATA_FILE, self.posts)
        self.refresh_tables()
        messagebox.showinfo("Optimización completada",
                            f"Fuertes conservadas: {kept}\nEliminadas (débiles): {removed}\nRe-publicadas: {re_posted}\n\n*Modo DEMO: no publica en Facebook aún.*")

    # -------- Settings Panel --------
    def _build_settings_panel(self):
        panel, body = self._panel_wrapper("⚙️ Ajustes")

        form = tk.Frame(body, bg="#ffffff")
        form.pack(fill="x", padx=16, pady=16)

        tk.Label(form, text="Umbral de 'clics' para considerar FUERTE", bg="#ffffff").grid(row=0, column=0, sticky="w", pady=6)
        self.weak_clicks_var = tk.IntVar(value=self.settings.get("weak_clicks_threshold", 5))
        tk.Entry(form, textvariable=self.weak_clicks_var).grid(row=0, column=1, sticky="w")

        tk.Label(form, text="Umbral de 'mensajes' para considerar FUERTE", bg="#ffffff").grid(row=1, column=0, sticky="w", pady=6)
        self.weak_msg_var = tk.IntVar(value=self.settings.get("weak_messages_threshold", 1))
        tk.Entry(form, textvariable=self.weak_msg_var).grid(row=1, column=1, sticky="w")

        tk.Label(form, text="Renovar automáticamente cada (horas)", bg="#ffffff").grid(row=2, column=0, sticky="w", pady=6)
        self.renew_hours_var = tk.IntVar(value=self.settings.get("auto_renew_hours", 48))
        tk.Entry(form, textvariable=self.renew_hours_var).grid(row=2, column=1, sticky="w")

        tk.Button(form, text="Guardar ajustes", command=self.save_settings).grid(row=3, column=0, columnspan=2, pady=(10,0), sticky="w")

        info = tk.Label(body, text=("Nota: Este prototipo es de interfaz. "
                                    "La publicación/renovación/eliminación reales en Facebook se integrarán en la siguiente fase "
                                    "usando automatización de navegador."),
                        bg="#ffffff", fg="#6b7280", justify="left", wraplength=820)
        info.pack(fill="x", padx=16, pady=(0,16))

        return panel

    def save_settings(self):
        self.settings["weak_clicks_threshold"] = int(self.weak_clicks_var.get())
        self.settings["weak_messages_threshold"] = int(self.weak_msg_var.get())
        self.settings["auto_renew_hours"] = int(self.renew_hours_var.get())
        save_json(SETTINGS_FILE, self.settings)
        messagebox.showinfo("Guardado", "Ajustes guardados correctamente.")

    # -------- Helpers --------
    def _make_table(self, parent, headers, stretch_cols=None):
        frame = tk.Frame(parent, bg="#ffffff")
        frame.pack(fill="both", expand=True)

        columns = ["id"] + headers
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        tree.pack(fill="both", expand=True, side="left", padx=(8,0), pady=8)

        tree.heading("id", text="ID")
        tree.column("id", width=0, stretch=False)

        for h in headers:
            tree.heading(h, text=h)
            width = 200 if h == "Título" else 100
            tree.column(h, width=width, anchor="w")
        if stretch_cols:
            for idx in stretch_cols:
                tree.column(headers[idx], width=300, stretch=True)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=8)

        return tree

    def show_panel(self, key):
        for k, p in self.panels.items():
            p.pack_forget()
            self.menu_buttons[k].configure(bg="#ffffff")
        self.panels[key].pack(fill="both", expand=True)
        self.menu_buttons[key].configure(bg="#eef2ff")
        self.refresh_tables()

    def refresh_tables(self):
        def clear(tree):
            for i in tree.get_children():
                tree.delete(i)

        # Renew table
        if hasattr(self, "renew_table"):
            clear(self.renew_table)
            for p in self.posts:
                if p["status"] == "active":
                    self.renew_table.insert("", "end", values=(
                        p["id"], p["title"], f"${p['price']:.2f}", p["clicks"], p["messages"],
                        p["updated_at"].split("T")[0]
                    ))

        # Delete table
        if hasattr(self, "delete_table"):
            clear(self.delete_table)
            for p in self.posts:
                self.delete_table.insert("", "end", values=(
                    p["id"], p["title"], f"${p['price']:.2f}", p["clicks"], p["messages"], p["status"]
                ))

        # Analytics table
        if hasattr(self, "analytics_table"):
            clear(self.analytics_table)
            weak_c = self.settings.get("weak_clicks_threshold", 5)
            weak_m = self.settings.get("weak_messages_threshold", 1)
            for p in self.posts:
                strength = "Fuerte" if (p["clicks"] >= weak_c or p["messages"] >= weak_m) else "Débil"
                self.analytics_table.insert("", "end", values=(
                    p["id"], p["title"], p["clicks"], p["messages"], strength
                ))

if __name__ == "__main__":
    app = App()
    app.mainloop()
