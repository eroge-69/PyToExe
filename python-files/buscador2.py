
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
# Usar sqlcipher3 en lugar de sqlite3
import sqlcipher3 as sqlite3
import pandas as pd

class ScrolledFrame(ttk.Frame):
    """Un frame con una barra de scroll vertical que aparece solo si es necesario."""
    def __init__(self, parent, bg_color, *args, **kw):
        super().__init__(parent, *args, **kw)

        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, background=bg_color)
        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set, takefocus=0)

        v_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = ttk.Frame(canvas, style="TFrame")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        def _on_mousewheel(event):
            scroll_delta = 0
            if event.num == 5 or event.delta < 0:
                scroll_delta = 1
            elif event.num == 4 or event.delta > 0:
                scroll_delta = -1
            canvas.yview_scroll(scroll_delta, "units")

        self.bind_all("<MouseWheel>", _on_mousewheel, "+")
        self.bind_all("<Button-4>", _on_mousewheel, "+")
        self.bind_all("<Button-5>", _on_mousewheel, "+")


class BuscadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DataSearchX DVC - (Modo Seguro)")
        self.root.geometry("1366x768")
        self.root.minsize(1024, 700)
        self.root.resizable(True, True)

        self.last_search_sql = None
        self.last_search_params = None

        self.BG_COLOR = "#2E2E2E"
        self.FG_COLOR = "#F0F0F0"
        self.FIELD_BG_COLOR = "#3C3C3C"
        self.ACCENT_COLOR = "#00BFFF" 
        self.BORDER_COLOR = "#555555"
        self.BUTTON_BG = "#4A4A4A"
        
        self.detail_nombre = tk.StringVar(value="...")
        self.detail_dni = tk.StringVar(value="...")
        self.detail_fec_nac = tk.StringVar(value="...")
        self.detail_direccion = tk.StringVar(value="...")
        self.detail_ubigeo_dir = tk.StringVar(value="...")

        # --- BLOQUE DE CONEXIÓN CORREGIDO ---
        try:
            # Conectar al archivo de base de datos encriptado
            # NOTA: Asegúrate de que la ruta sea correcta. Si el script está en la raíz
            # y la DB en una carpeta 'data', la ruta sería 'data/personas_encrypted.db'
            self.conn = sqlite3.connect("personas_encrypted.db")
            self.cursor = self.conn.cursor()

            password = "penelopecruz18"
            
            # 1. Aplicar la MISMA configuración que se usó para crear la DB
            #    Estos PRAGMAs deben ir ANTES de la clave.
            self.cursor.execute("PRAGMA kdf_iter = 64000")
            self.cursor.execute("PRAGMA cipher_page_size = 4096")

            # 2. Ahora, proporcionar la contraseña para desencriptar
            self.cursor.execute(f"PRAGMA key = '{password}'")

            # 3. Realizar una consulta de prueba para verificar que todo es correcto
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")

        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo conectar o descifrar 'personas_encrypted.db'.\n"
                f"Verifique la ruta, la contraseña y la configuración de encriptación.\n\nError: {e}"
            )
            self.root.destroy()
            return
            
        self.setup_styles()
        self.create_widgets()

        self.root.bind("<Return>", lambda e: self.buscar())
        self.root.bind("<Escape>", lambda e: self.clear_form())

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        self.root.configure(background=self.BG_COLOR)
        
        style.configure(".", background=self.BG_COLOR, foreground=self.FG_COLOR, fieldbackground=self.FIELD_BG_COLOR, bordercolor=self.BORDER_COLOR, lightcolor=self.BG_COLOR, darkcolor=self.BG_COLOR)
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("TLabel", background=self.BG_COLOR, foreground=self.FG_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), foreground=self.ACCENT_COLOR, background=self.BG_COLOR)
        style.configure("Data.TLabel", font=("Segoe UI", 10), wraplength=350, background=self.BG_COLOR)
        style.configure("TLabelframe", background=self.BG_COLOR, bordercolor=self.BORDER_COLOR, relief="groove")
        style.configure("TLabelframe.Label", background=self.BG_COLOR, foreground=self.ACCENT_COLOR, font=("Segoe UI Semibold", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6, background=self.BUTTON_BG, foreground=self.FG_COLOR, borderwidth=1, relief="raised")
        style.map("TButton", background=[('active', self.ACCENT_COLOR)], foreground=[('active', 'black')])
        style.configure("TEntry", padding=5, insertcolor=self.FG_COLOR, fieldbackground=self.FIELD_BG_COLOR, foreground=self.FG_COLOR)
        style.map("TCombobox", fieldbackground=[('readonly', self.FIELD_BG_COLOR)], foreground=[('readonly', self.FG_COLOR)], selectbackground=[('readonly', self.FIELD_BG_COLOR)], selectforeground=[('readonly', self.FG_COLOR)])
        style.configure("Treeview", font=("Consolas", 10), rowheight=28, background=self.FIELD_BG_COLOR, foreground=self.FG_COLOR)
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 11), padding=8, background="#3C3C3C", relief="raised")
        style.map("Treeview", background=[('selected', self.ACCENT_COLOR)], foreground=[('selected', 'black')])
        style.configure("OddRow", background=self.FIELD_BG_COLOR)
        style.configure("EvenRow", background="#353535")
        style.configure("Vertical.TScrollbar", background=self.BUTTON_BG, troughcolor=self.BG_COLOR, bordercolor=self.BORDER_COLOR, arrowcolor=self.FG_COLOR)
        style.map("Vertical.TScrollbar", background=[('active', self.ACCENT_COLOR)])
        style.configure("Horizontal.TScrollbar", background=self.BUTTON_BG, troughcolor=self.BG_COLOR, bordercolor=self.BORDER_COLOR, arrowcolor=self.FG_COLOR)
        style.map("Horizontal.TScrollbar", background=[('active', self.ACCENT_COLOR)])
        style.configure("TPanedwindow", background=self.BG_COLOR)

    def create_widgets(self):
        paned_window = ttk.PanedWindow(self.root, orient='vertical', style="TPanedwindow")
        paned_window.pack(fill='both', expand=True, padx=10, pady=(5,0))

        filter_container = ScrolledFrame(paned_window, self.BG_COLOR, style="TFrame")
        paned_window.add(filter_container, weight=0)

        top_frame = filter_container.scrollable_frame
        top_frame.columnconfigure(0, weight=3)
        top_frame.columnconfigure(1, weight=2)

        filter_panels_frame = ttk.Frame(top_frame)
        filter_panels_frame.grid(row=0, column=0, sticky="nsew")

        personal_frame = ttk.LabelFrame(filter_panels_frame, text="Filtros Personales", padding=(15, 10))
        personal_frame.pack(fill='x', expand=True, padx=10, pady=8)
        campos = [("DNI", "DNI"), ("Ap. Paterno", "AP_PAT"), ("Ap. Materno", "AP_MAT"), ("Nombres", "NOMBRES"), 
                  ("Dirección", "DIRECCION"), ("Nombre Madre", "MADRE"), ("Nombre Padre", "PADRE")]
        self.entries = {}
        for i, (label_text, db_field) in enumerate(campos):
            row, col = divmod(i, 2)
            ttk.Label(personal_frame, text=f"{label_text}:").grid(row=row, column=col*2, sticky="w", pady=4, padx=5)
            entry = ttk.Entry(personal_frame)
            entry.grid(row=row, column=col*2 + 1, sticky="ew", pady=4, padx=5)
            self.entries[db_field] = entry
        
        row_offset = (len(campos) + 1) // 2
        ttk.Label(personal_frame, text="Estado Civil:").grid(row=row_offset, column=0, sticky="w", pady=4, padx=5)
        self.est_civil_combo = ttk.Combobox(personal_frame, values=["", "SOLTERO", "CASADO", "DIVORCIADO", "VIUDO", "CONVIVIENTE"], state="readonly")
        self.est_civil_combo.grid(row=row_offset, column=1, sticky="ew", pady=4, padx=5)
        ttk.Label(personal_frame, text="Sexo:").grid(row=row_offset, column=2, sticky="w", pady=4, padx=5)
        self.sexo_combo = ttk.Combobox(personal_frame, values=["", "Masculino", "Femenino"], state="readonly")
        self.sexo_combo.grid(row=row_offset, column=3, sticky="ew", pady=4, padx=5)
        self.sexo_map = {"Masculino": "1", "Femenino": "2", "": ""}
        for i in [1, 3]: personal_frame.columnconfigure(i, weight=1)

        ubigeo_frame = ttk.LabelFrame(filter_panels_frame, text="Filtros Geográficos", padding=(15, 10))
        ubigeo_frame.pack(fill='x', expand=True, padx=10, pady=8)
        for i in [1, 3]: ubigeo_frame.columnconfigure(i, weight=1)
        
        self.cursor.execute("SELECT DISTINCT Departamento FROM ubigeo ORDER BY Departamento")
        departamentos = [""] + [row[0] for row in self.cursor.fetchall()]
        
        ttk.Label(ubigeo_frame, text="Dpto. Nac:").grid(row=0, column=0, sticky="w", pady=3, padx=5)
        self.dep_nac = ttk.Combobox(ubigeo_frame, values=departamentos, state="readonly")
        self.dep_nac.grid(row=0, column=1, sticky="ew", pady=3, padx=5)
        self.dep_nac.bind("<<ComboboxSelected>>", self.update_provincias_nac)
        ttk.Label(ubigeo_frame, text="Prov. Nac:").grid(row=0, column=2, sticky="w", pady=3, padx=5)
        self.prov_nac = ttk.Combobox(ubigeo_frame, values=[""], state="disabled")
        self.prov_nac.grid(row=0, column=3, sticky="ew", pady=3, padx=5)
        self.prov_nac.bind("<<ComboboxSelected>>", self.update_distritos_nac)
        ttk.Label(ubigeo_frame, text="Dist. Nac:").grid(row=1, column=0, sticky="w", pady=3, padx=5)
        self.dist_nac = ttk.Combobox(ubigeo_frame, values=[""], state="disabled")
        self.dist_nac.grid(row=1, column=1, sticky="ew", pady=3, padx=5)
        
        ttk.Label(ubigeo_frame, text="Dpto. Res:").grid(row=1, column=2, sticky="w", pady=3, padx=5)
        self.dep_dir = ttk.Combobox(ubigeo_frame, values=departamentos, state="readonly")
        self.dep_dir.grid(row=1, column=3, sticky="ew", pady=3, padx=5)
        self.dep_dir.bind("<<ComboboxSelected>>", self.update_provincias_dir)
        ttk.Label(ubigeo_frame, text="Prov. Res:").grid(row=2, column=0, sticky="w", pady=3, padx=5)
        self.prov_dir = ttk.Combobox(ubigeo_frame, values=[""], state="disabled")
        self.prov_dir.grid(row=2, column=1, sticky="ew", pady=3, padx=5)
        self.prov_dir.bind("<<ComboboxSelected>>", self.update_distritos_dir)
        ttk.Label(ubigeo_frame, text="Dist. Res:").grid(row=2, column=2, sticky="w", pady=3, padx=5)
        self.dist_dir = ttk.Combobox(ubigeo_frame, values=[""], state="disabled")
        self.dist_dir.grid(row=2, column=3, sticky="ew", pady=3, padx=5)

        otras_frame = ttk.LabelFrame(filter_panels_frame, text="Rango de Edad", padding=(15, 10))
        otras_frame.pack(fill='x', expand=True, padx=10, pady=8)
        
        ttk.Label(otras_frame, text="Mínima:").grid(row=0, column=0, sticky="w", pady=4, padx=5)
        self.edad_min = tk.IntVar(value=0)
        self.scale_min = ttk.Scale(otras_frame, from_=0, to=120, orient="horizontal", variable=self.edad_min, command=lambda e: self.min_label.config(text=self.edad_min.get()))
        self.scale_min.grid(row=0, column=1, sticky="ew", pady=4, padx=(0, 10))
        self.min_label = ttk.Label(otras_frame, text="0", width=3)
        self.min_label.grid(row=0, column=2, sticky="w")
        
        ttk.Label(otras_frame, text="Máxima:").grid(row=0, column=3, sticky="w", pady=4, padx=5)
        self.edad_max = tk.IntVar(value=120)
        self.scale_max = ttk.Scale(otras_frame, from_=0, to=120, orient="horizontal", variable=self.edad_max, command=lambda e: self.max_label.config(text=self.edad_max.get()))
        self.scale_max.grid(row=0, column=4, sticky="ew", pady=4, padx=(0, 10))
        self.max_label = ttk.Label(otras_frame, text="120", width=3)
        self.max_label.grid(row=0, column=5, sticky="w")
        otras_frame.columnconfigure(1, weight=1)
        otras_frame.columnconfigure(4, weight=1)
        
        btn_frame = ttk.Frame(filter_panels_frame)
        btn_frame.pack(pady=10)
        acciones = [("Buscar 🔎", self.buscar), ("Limpiar 🧹", self.clear_form), 
                    ("Copiar 📋", self.copy_to_clipboard), 
                    ("Ver Detalle Completo ℹ️", self.ver_detalle), 
                    ("Exportar a Excel 📊", self.exportar_a_excel)]
        for texto, comando in acciones:
            ttk.Button(btn_frame, text=texto, command=comando).pack(side="left", padx=7, ipadx=5)
        
        detail_frame = ttk.LabelFrame(top_frame, text="Detalle de Selección", padding=(15, 10))
        detail_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=8)
        
        ttk.Label(detail_frame, text="Nombre:", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=(0,2))
        ttk.Label(detail_frame, textvariable=self.detail_nombre, style="Data.TLabel").grid(row=1, column=0, sticky="w", pady=(0,10), padx=5)
        ttk.Label(detail_frame, text="DNI:", style="Header.TLabel").grid(row=2, column=0, sticky="w", pady=(0,2))
        ttk.Label(detail_frame, textvariable=self.detail_dni, style="Data.TLabel").grid(row=3, column=0, sticky="w", pady=(0,10), padx=5)
        ttk.Label(detail_frame, text="Fecha Nacimiento:", style="Header.TLabel").grid(row=4, column=0, sticky="w", pady=(0,2))
        ttk.Label(detail_frame, textvariable=self.detail_fec_nac, style="Data.TLabel").grid(row=5, column=0, sticky="w", pady=(0,10), padx=5)
        ttk.Label(detail_frame, text="Dirección:", style="Header.TLabel").grid(row=6, column=0, sticky="w", pady=(0,2))
        ttk.Label(detail_frame, textvariable=self.detail_direccion, style="Data.TLabel").grid(row=7, column=0, sticky="w", pady=(0,10), padx=5)
        ttk.Label(detail_frame, text="Ubigeo Residencia:", style="Header.TLabel").grid(row=8, column=0, sticky="w", pady=(0,2))
        ttk.Label(detail_frame, textvariable=self.detail_ubigeo_dir, style="Data.TLabel").grid(row=9, column=0, sticky="w", pady=(0,10), padx=5)

        tree_frame = ttk.Frame(paned_window, style="TFrame")
        paned_window.add(tree_frame, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.columns = ("DNI", "Ap. Paterno", "Ap. Materno", "Nombres", "Edad", "Fec. Nacimiento", "Sexo", "Estado Civil", "Dirección Completa", "Lugar Nacimiento", "Lugar Residencia")
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings", selectmode='browse')
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_by(_col, False))
            self.tree.column(col, width=150, anchor="w")
        self.tree.column("DNI", width=80, anchor="w")
        self.tree.column("Edad", width=50, anchor="center")
        self.tree.column("Sexo", width=90, anchor="w")
        
        self.tree.bind("<Double-1>", self.ver_detalle)
        self.tree.bind('<<TreeviewSelect>>', self._on_treeview_select)
        
        self.tree.tag_configure('oddrow', background=self.FIELD_BG_COLOR)
        self.tree.tag_configure('evenrow', background="#353535")
        
        self.status_label = ttk.Label(self.root, text="Listo para buscar", anchor='w')
        self.status_label.pack(side='bottom', fill='x', padx=15, pady=(0, 5))

    def _on_treeview_select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        values = self.tree.item(item_id, 'values')
        
        try:
            nombre_completo = f"{values[3]} {values[1]} {values[2]}"
            self.detail_nombre.set(nombre_completo)
            self.detail_dni.set(values[0])
            self.detail_fec_nac.set(values[5])
            self.detail_direccion.set(values[8])
            self.detail_ubigeo_dir.set(values[10])
        except IndexError:
            self._clear_details_panel()

    def _clear_details_panel(self):
        self.detail_nombre.set("...")
        self.detail_dni.set("...")
        self.detail_fec_nac.set("...")
        self.detail_direccion.set("...")
        self.detail_ubigeo_dir.set("...")

    def update_provincias(self, dep_combo, prov_combo, dist_combo):
        dep = dep_combo.get()
        query = "SELECT DISTINCT Provincia FROM ubigeo WHERE Departamento = ? ORDER BY Provincia"
        self.cursor.execute(query, (dep,))
        items = [""] + [row[0] for row in self.cursor.fetchall()]
        prov_combo.config(values=items, state="readonly" if dep else "disabled")
        prov_combo.set('')
        dist_combo.set('')
        dist_combo.config(values=[""], state="disabled")

    def update_distritos(self, dep_combo, prov_combo, dist_combo):
        dep, prov = dep_combo.get(), prov_combo.get()
        if not prov:
            dist_combo.set('')
            dist_combo.config(values=[""], state="disabled")
            return
        query = "SELECT DISTINCT Distrito FROM ubigeo WHERE Departamento = ? AND Provincia = ? ORDER BY Distrito"
        self.cursor.execute(query, (dep, prov))
        items = [""] + [row[0] for row in self.cursor.fetchall()]
        dist_combo.config(values=items, state="readonly")
        dist_combo.set('')

    def update_provincias_nac(self, event): self.update_provincias(self.dep_nac, self.prov_nac, self.dist_nac)
    def update_distritos_nac(self, event): self.update_distritos(self.dep_nac, self.prov_nac, self.dist_nac)
    def update_provincias_dir(self, event): self.update_provincias(self.dep_dir, self.prov_dir, self.dist_dir)
    def update_distritos_dir(self, event): self.update_distritos(self.dep_dir, self.prov_dir, self.dist_dir)

    def clear_form(self):
        for entry in self.entries.values(): entry.delete(0, tk.END)
        for combo in [self.est_civil_combo, self.sexo_combo, self.dep_nac, self.prov_nac, self.dist_nac, self.dep_dir, self.prov_dir, self.dist_dir]: combo.set('')
        for combo in [self.prov_nac, self.dist_nac, self.prov_dir, self.dist_dir]: combo.config(values=[""], state="disabled")
        self.edad_min.set(0); self.min_label.config(text="0")
        self.edad_max.set(120); self.max_label.config(text="120")
        self.tree.delete(*self.tree.get_children())
        self._clear_details_panel()
        self.status_label.config(text="Formulario limpiado. Listo para buscar.", foreground="#00FF00")
        
    def buscar(self):
        if self.edad_min.get() > self.edad_max.get():
            messagebox.showwarning("Rango de edad inválido", "La edad mínima no puede ser mayor que la máxima.")
            return

        self.status_label.config(text="Construyendo consulta...", foreground=self.FG_COLOR)
        self.root.update_idletasks()

        base_sql = "FROM personas p LEFT JOIN ubigeo u_nac ON p.UBIGEO_NAC = u_nac.Ubigeo"
        where_clauses = []
        params = []
        
        for field, entry in self.entries.items():
            if entry.get(): where_clauses.append(f"UPPER(p.{field}) LIKE ?"); params.append(f"%{entry.get().strip().upper()}%")
        if self.est_civil_combo.get(): where_clauses.append("p.EST_CIVIL = ?"); params.append(self.est_civil_combo.get())
        if self.sexo_combo.get(): where_clauses.append("p.SEXO = ?"); params.append(self.sexo_map[self.sexo_combo.get()])
        if self.dep_nac.get(): where_clauses.append("u_nac.Departamento = ?"); params.append(self.dep_nac.get())
        if self.prov_nac.get(): where_clauses.append("u_nac.Provincia = ?"); params.append(self.prov_nac.get())
        if self.dist_nac.get(): where_clauses.append("u_nac.Distrito = ?"); params.append(self.dist_nac.get())
        
        dir_parts = [self.dep_dir.get(), self.prov_dir.get(), self.dist_dir.get()]
        if any(dir_parts):
            where_clauses.append("p.UBIGEO_DIR LIKE ?")
            params.append(f'{" - ".join(filter(None, dir_parts))}%')

        age_clause = "(CAST(strftime('%Y', 'now') AS INTEGER) - CAST(substr(p.FECHA_NAC, 7, 4) AS INTEGER)) BETWEEN ? AND ?"
        where_clauses.append(age_clause)
        params.extend([self.edad_min.get(), self.edad_max.get()])
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        try:
            self.status_label.config(text="Contando resultados...", foreground=self.FG_COLOR)
            self.root.update_idletasks()
            
            count_sql = f"SELECT COUNT(*) {base_sql} {where_sql}"
            self.cursor.execute(count_sql, params)
            num_results = self.cursor.fetchone()[0]

            select_cols = """
                p.DNI, p.AP_PAT, p.AP_MAT, p.NOMBRES,
                (strftime('%Y', 'now') - substr(p.FECHA_NAC, 7, 4)) - (strftime('%m-%d', 'now') < substr(p.FECHA_NAC, 4, 2) || '-' || substr(p.FECHA_NAC, 1, 2)),
                p.FECHA_NAC, CASE p.SEXO WHEN '1' THEN 'Masculino' WHEN '2' THEN 'Femenino' ELSE p.SEXO END,
                p.EST_CIVIL, p.DIRECCION,
                CASE WHEN u_nac.Departamento IS NOT NULL THEN u_nac.Departamento || ' - ' || u_nac.Provincia || ' - ' || u_nac.Distrito ELSE p.UBIGEO_NAC END,
                p.UBIGEO_DIR
            """
            self.last_search_sql = f"SELECT {select_cols} {base_sql} {where_sql}"
            self.last_search_params = params

            if num_results > 500:
                msg = f"La búsqueda generó {num_results} resultados. ¿Deseas mostrarlos en la tabla? (Puede hacer lenta la aplicación)"
                if not messagebox.askyesno("Advertencia: Resultados Masivos", msg):
                    self.status_label.config(text=f"Búsqueda cancelada por el usuario. {num_results} resultados encontrados.", foreground="#FFA500")
                    return

            self.status_label.config(text=f"Obteniendo {num_results} resultados...", foreground=self.FG_COLOR)
            self.root.update_idletasks()
            
            self.cursor.execute(self.last_search_sql, self.last_search_params)
            resultados = self.cursor.fetchall()
            
            self.tree.delete(*self.tree.get_children())
            for i, row in enumerate(resultados):
                self.tree.insert("", "end", values=row, tags=('evenrow' if i % 2 == 0 else 'oddrow'))
            
            self.status_label.config(text=f"Se encontraron {len(resultados)} coincidencias.", foreground="#00FF00" if resultados else "#FF6347")

        except sqlite3.Error as e:
            messagebox.showerror("Error en Consulta SQL", f"Ha ocurrido un error: {e}")
            self.status_label.config(text="Error en la consulta", foreground="#FF6347")
            
    def exportar_a_excel(self):
        if not self.last_search_sql:
            messagebox.showwarning("Nada que exportar", "Por favor, realiza una búsqueda primero.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")], title="Guardar resultados como...")
        if not file_path: return

        self.status_label.config(text="Exportando a Excel...", foreground=self.FG_COLOR)
        self.root.update_idletasks()
        try:
            df = pd.read_sql_query(self.last_search_sql, self.conn, params=self.last_search_params)
            df.columns = ["DNI", "AP_PAT", "AP_MAT", "NOMBRES", "EDAD", "FECHA_NAC", "SEXO", "EST_CIVIL", "DIRECCION", "LUGAR_NACIMIENTO", "LUGAR_RESIDENCIA"]
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Éxito", f"Los datos han sido exportados exitosamente a:\n{file_path}")
            self.status_label.config(text="Exportación completada.", foreground="#00FF00")
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"No se pudo exportar a Excel: {e}")
            self.status_label.config(text="Error durante la exportación.", foreground="#FF6347")
            
    def ver_detalle(self, event=None):
        if not self.tree.selection():
            if event: messagebox.showwarning("Sin selección", "Haz clic en una fila para seleccionarla antes de ver el detalle.")
            return
        
        item_id = self.tree.selection()[0]
        dni = self.tree.item(item_id, 'values')[0]
        self.cursor.execute("SELECT * FROM personas WHERE DNI = ?", (dni,))
        full_data = self.cursor.fetchone()
        
        if not full_data: return
        
        column_names = [desc[0] for desc in self.cursor.description]
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalle Completo de {full_data[3]} {full_data[1]}")
        detail_window.geometry("550x600")
        detail_window.configure(background=self.BG_COLOR)
        
        text_widget = tk.Text(detail_window, font=("Consolas", 11), wrap='word', borderwidth=0, highlightthickness=0, background=self.FIELD_BG_COLOR, foreground=self.FG_COLOR, insertbackground=self.FG_COLOR)
        text_widget.pack(padx=15, pady=15, fill='both', expand=True)
        
        for name, value in zip(column_names, full_data):
            text_widget.insert(tk.END, f"{name.replace('_', ' ').upper():<20}: ", ("bold",))
            text_widget.insert(tk.END, f"{value}\n")
        
        text_widget.tag_configure("bold", font=("Segoe UI Semibold", 11), foreground=self.ACCENT_COLOR)
        text_widget.config(state='disabled')

    def sort_by(self, col, descending):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: int(str(t[0]).strip()), reverse=descending)
        except (ValueError, TypeError):
            data.sort(key=lambda t: str(t[0]).lower(), reverse=descending)
        
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
            self.tree.item(child, tags=('evenrow' if index % 2 == 0 else 'oddrow'))
        self.tree.heading(col, command=lambda _col=col: self.sort_by(_col, not descending))

    def copy_to_clipboard(self):
        items_to_copy = self.tree.selection()
        if not items_to_copy:
            items_to_copy = self.tree.get_children()
            if not items_to_copy:
                messagebox.showinfo("Nada que copiar", "La tabla está vacía.")
                return

        header = "\t".join(self.columns)
        lines = [header] + ["\t".join(map(str, self.tree.item(item, 'values'))) for item in items_to_copy]
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines))
        messagebox.showinfo("Copiado", f"{len(items_to_copy)} fila(s) copiada(s) al portapapeles.")

    def on_closing(self):
        if self.conn: self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BuscadorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

