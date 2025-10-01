# busqueda_activa_app.py
import os
import sys
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ==============================
# 1. CONFIGURACIÓN INICIAL
# ==============================
if getattr(sys, 'frozen', False):
    # Si es un ejecutable (.exe)
    RUTA_BASE = os.path.dirname(sys.executable)
else:
    # Si se ejecuta como script .py
    RUTA_BASE = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_NOMBRE = "busqueda_activa.xlsx"
RUTA_ARCHIVO = os.path.join(RUTA_BASE, ARCHIVO_NOMBRE)

# Zonas y barrios de Jujuy
ZONAS_BARRIOS = {
    "San Salvador de Jujuy": [
        "Barrio 20 de Febrero", "Barrio San Pedrito", "Barrio 9 de Julio",
        "Barrio San Martín", "Barrio Alberdi", "Barrio San Francisco",
        "Barrio El Milagro", "Villa Jardín", "Villa Belgrano", "Centro",
        "Ciudad de Nieva", "Cuyaya", "Alto Comedero", "Los Perales",
        "Huaico", "Chijra", "Gorriti", "Malvinas Argentinas", "Mariano Moreno",
        "Coronel Arias", "San Cayetano", "Alto La Viña", "Bajo La Viña",
        "Castañeda", "Cerro Las Rosas", "Cuyaya", "Ejército del Norte",
        "El Chingo", "Finca Suipacha", "General Belgrano", "Gral. Manuel Arias",
        "Kennedy", "La Alborada", "La Merced", "Las Lomas", "Luján",
        "Norte", "Padre Marcelo", "Punta Diamante", "Reyes", "Rio Blanco",
        "San Isidro", "San José", "San Pablo de Reyes", "Villa San Martín"
    ],
    "Valle de Lerma": ["La Merced", "El Carmen", "Cieneguillas", "Perico", "San Antonio", "Puesto Viejo", "Monterrico", "Palpalá", "Rio Blanco (Palpalá)", "Centro (Palpalá)"],
    "Quebrada de Humahuaca": ["Humahuaca", "Tilcara", "Uquía", "Purmamarca", "Maimará", "Tumbaya", "Volcán", "Iturbe", "Tres Cruces"],
    "Puna": ["La Quiaca", "Abra Pampa", "Susques", "Cochinoca", "Casabindo", "Santa Catalina", "Yavi", "Cangrejillos", "El Aguilar", "Mina Pirquitas", "Puesto Marqués"],
    "Yungas": ["Calilegua", "Libertador General San Martín", "Palpalá", "Fraile Pintado", "Arrayanal", "Yuto", "Caimancito", "El Talar", "Santa Clara"]
}

LISTA_ZONAS = list(ZONAS_BARRIOS.keys())
LISTA_BARRIOS = sorted({barrio for barrios in ZONAS_BARRIOS.values() for barrio in barrios})

# ==============================
# 2. GESTIÓN DE ARCHIVO EXCEL
# ==============================
def inicializar_archivo():
    if not os.path.exists(RUTA_ARCHIVO):
        df_busquedas = pd.DataFrame(columns=[
            "fecha", "agente", "zona", "barrio", "tipo de propiedad", "presupuesto", "descripcion"
        ])
        df_agentes = pd.DataFrame(columns=["nombre"])
        with pd.ExcelWriter(RUTA_ARCHIVO, engine='openpyxl') as writer:
            df_busquedas.to_excel(writer, sheet_name='busquedas', index=False)
            df_agentes.to_excel(writer, sheet_name='agentes', index=False)

def cargar_datos():
    try:
        df_b = pd.read_excel(RUTA_ARCHIVO, sheet_name='busquedas', dtype=str)
        df_a = pd.read_excel(RUTA_ARCHIVO, sheet_name='agentes', dtype=str)
        agentes = df_a['nombre'].dropna().unique().tolist() if not df_a.empty else []
        return df_b, df_a, agentes
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
        return (pd.DataFrame(columns=["fecha", "agente", "zona", "barrio", "tipo de propiedad", "presupuesto", "descripcion"]),
                pd.DataFrame(columns=["nombre"]), [])

def guardar_hoja(nombre_hoja, df):
    try:
        with pd.ExcelWriter(RUTA_ARCHIVO, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudo guardar:\n{e}")

# ==============================
# 3. CLASE PRINCIPAL DE LA APLICACIÓN
# ==============================
class BusquedaActivaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Búsqueda Activa - Inmobiliaria")
        self.root.geometry("850x650")
        self.root.resizable(True, True)

        # Cargar datos
        inicializar_archivo()
        self.df_busquedas, self.df_agentes, self.lista_agentes = cargar_datos()

        # Crear pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_cargar_busqueda = ttk.Frame(self.notebook)
        self.tab_buscar = ttk.Frame(self.notebook)
        self.tab_cargar_agente = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_cargar_busqueda, text="📥 Cargar Búsqueda")
        self.notebook.add(self.tab_buscar, text="🔍 Buscar")
        self.notebook.add(self.tab_cargar_agente, text="👥 Cargar Agente")

        self.crear_pestaña_cargar_agente()
        self.crear_pestaña_cargar_busqueda()
        self.crear_pestaña_buscar()

    # ------------------------------
    def crear_pestaña_cargar_agente(self):
        frame = ttk.Frame(self.tab_cargar_agente, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Nombre del agente:", font=("Arial", 10)).pack(anchor='w', pady=(0,5))
        self.entry_agente = ttk.Entry(frame, width=40)
        self.entry_agente.pack(pady=(0,10))

        self.btn_agregar = ttk.Button(frame, text="➕ Agregar Agente", command=self.agregar_agente)
        self.btn_agregar.pack(pady=(0,10))

        self.label_status_agente = ttk.Label(frame, text="", foreground="green")
        self.label_status_agente.pack()

    def agregar_agente(self):
        nombre = self.entry_agente.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
            return
        if nombre in self.lista_agentes:
            messagebox.showwarning("Advertencia", f"Ya existe el agente '{nombre}'.")
            return

        self.df_agentes = pd.concat([self.df_agentes, pd.DataFrame([{"nombre": nombre}])], ignore_index=True)
        self.lista_agentes = self.df_agentes['nombre'].dropna().unique().tolist()
        guardar_hoja('agentes', self.df_agentes)
        self.label_status_agente.config(text=f"✅ Agente '{nombre}' agregado.")
        self.entry_agente.delete(0, 'end')
        self.actualizar_dropdowns()

    # ------------------------------
    def crear_pestaña_cargar_busqueda(self):
        frame = ttk.Frame(self.tab_cargar_busqueda, padding=15)
        frame.pack(fill='both', expand=True)

        # Configurar grid
        frame.columnconfigure(1, weight=1)

        # Fecha
        ttk.Label(frame, text="Fecha (AAAA-MM-DD):").grid(row=0, column=0, sticky='w', pady=5, padx=(0,10))
        self.fecha_var = tk.StringVar()
        self.entry_fecha = ttk.Entry(frame, textvariable=self.fecha_var, width=20)
        self.entry_fecha.grid(row=0, column=1, sticky='w', pady=5)
        self.fecha_var.set(datetime.now().strftime("%Y-%m-%d"))

        # Agente
        ttk.Label(frame, text="Agente:").grid(row=1, column=0, sticky='w', pady=5, padx=(0,10))
        self.agente_var = tk.StringVar()
        self.combo_agente = ttk.Combobox(frame, textvariable=self.agente_var, width=37, state="readonly")
        self.combo_agente.grid(row=1, column=1, sticky='w', pady=5)

        # Zona
        ttk.Label(frame, text="Zona:").grid(row=2, column=0, sticky='w', pady=5, padx=(0,10))
        self.zona_var = tk.StringVar()
        self.combo_zona = ttk.Combobox(frame, textvariable=self.zona_var, values=LISTA_ZONAS, width=37, state="readonly")
        self.combo_zona.grid(row=2, column=1, sticky='w', pady=5)
        self.combo_zona.bind("<<ComboboxSelected>>", self.actualizar_barrios)

        # Barrio
        ttk.Label(frame, text="Barrio:").grid(row=3, column=0, sticky='w', pady=5, padx=(0,10))
        self.barrio_var = tk.StringVar()
        self.combo_barrio = ttk.Combobox(frame, textvariable=self.barrio_var, width=37, state="readonly")
        self.combo_barrio.grid(row=3, column=1, sticky='w', pady=5)

        # Tipo de propiedad
        ttk.Label(frame, text="Tipo Prop.:").grid(row=4, column=0, sticky='w', pady=5, padx=(0,10))
        self.tipo_var = tk.StringVar()
        self.combo_tipo = ttk.Combobox(frame, textvariable=self.tipo_var,
                                       values=["Casa", "Departamento", "Terreno", "Local comercial", "Otro"],
                                       width=37, state="readonly")
        self.combo_tipo.grid(row=4, column=1, sticky='w', pady=5)
        self.combo_tipo.set("Casa")

        # Presupuesto
        ttk.Label(frame, text="Presupuesto ($):").grid(row=5, column=0, sticky='w', pady=5, padx=(0,10))
        self.presupuesto_var = tk.DoubleVar(value=0.0)
        self.entry_presupuesto = ttk.Entry(frame, textvariable=self.presupuesto_var, width=20)
        self.entry_presupuesto.grid(row=5, column=1, sticky='w', pady=5)

        # Descripción
        ttk.Label(frame, text="Descripción:").grid(row=6, column=0, sticky='nw', pady=5, padx=(0,10))
        self.text_descripcion = tk.Text(frame, width=40, height=4)
        self.text_descripcion.grid(row=6, column=1, sticky='w', pady=5)

        # Botón guardar
        self.btn_guardar = ttk.Button(frame, text="💾 Guardar Búsqueda", command=self.guardar_busqueda)
        self.btn_guardar.grid(row=7, column=1, sticky='w', pady=15)

        self.label_status_carga = ttk.Label(frame, text="", foreground="green")
        self.label_status_carga.grid(row=8, column=1, sticky='w')

        # Inicializar combos
        self.actualizar_dropdowns()
        if LISTA_ZONAS:
            self.zona_var.set(LISTA_ZONAS[0])
            self.actualizar_barrios()

    def actualizar_barrios(self, event=None):
        zona = self.zona_var.get()
        barrios = ZONAS_BARRIOS.get(zona, [])
        self.combo_barrio['values'] = barrios
        if barrios:
            self.barrio_var.set(barrios[0])
        else:
            self.barrio_var.set("")

    def guardar_busqueda(self):
        fecha = self.fecha_var.get().strip()
        agente = self.agente_var.get()
        zona = self.zona_var.get()
        barrio = self.barrio_var.get()
        tipo = self.tipo_var.get()
        presupuesto = self.presupuesto_var.get()
        descripcion = self.text_descripcion.get("1.0", "end-1c").strip()

        if not fecha or not agente or not zona or not barrio:
            messagebox.showwarning("Advertencia", "Complete todos los campos obligatorios.")
            return

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use AAAA-MM-DD.")
            return

        nuevo_registro = {
            "fecha": fecha,
            "agente": agente,
            "zona": zona,
            "barrio": barrio,
            "tipo de propiedad": tipo,
            "presupuesto": presupuesto,
            "descripcion": descripcion
        }

        self.df_busquedas = pd.concat([self.df_busquedas, pd.DataFrame([nuevo_registro])], ignore_index=True)
        guardar_hoja('busquedas', self.df_busquedas)

        self.label_status_carga.config(text="✅ Búsqueda guardada exitosamente.")
        # Limpiar formulario
        self.fecha_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.tipo_var.set("Casa")
        self.presupuesto_var.set(0.0)
        self.text_descripcion.delete("1.0", "end")
        if self.lista_agentes:
            self.agente_var.set(self.lista_agentes[0])

    # ------------------------------
    def crear_pestaña_buscar(self):
        frame = ttk.Frame(self.tab_buscar, padding=15)
        frame.pack(fill='both', expand=True)

        # Filtros
        filtros_frame = ttk.Frame(frame)
        filtros_frame.pack(fill='x', pady=(0,15))

        # Zona
        ttk.Label(filtros_frame, text="Zona:").grid(row=0, column=0, sticky='w', padx=(0,10))
        self.search_zona_var = tk.StringVar(value="Todas")
        zonas_opciones = ["Todas"] + LISTA_ZONAS
        self.search_zona_combo = ttk.Combobox(filtros_frame, textvariable=self.search_zona_var, values=zonas_opciones, width=20, state="readonly")
        self.search_zona_combo.grid(row=0, column=1, sticky='w', padx=(0,20))
        self.search_zona_combo.bind("<<ComboboxSelected>>", self.actualizar_barrios_busqueda)

        # Barrio
        ttk.Label(filtros_frame, text="Barrio:").grid(row=0, column=2, sticky='w', padx=(0,10))
        self.search_barrio_var = tk.StringVar(value="Todos")
        self.search_barrio_combo = ttk.Combobox(filtros_frame, textvariable=self.search_barrio_var, width=20, state="readonly")
        self.search_barrio_combo.grid(row=0, column=3, sticky='w', padx=(0,20))

        # Agente
        ttk.Label(filtros_frame, text="Agente:").grid(row=1, column=0, sticky='w', pady=(10,0), padx=(0,10))
        self.search_agente_var = tk.StringVar(value="Todos")
        agentes_opciones = ["Todos"] + self.lista_agentes
        self.search_agente_combo = ttk.Combobox(filtros_frame, textvariable=self.search_agente_var, values=agentes_opciones, width=20, state="readonly")
        self.search_agente_combo.grid(row=1, column=1, sticky='w', pady=(10,0), padx=(0,20))

        # Tipo
        ttk.Label(filtros_frame, text="Tipo Prop.:").grid(row=1, column=2, sticky='w', pady=(10,0), padx=(0,10))
        self.search_tipo_var = tk.StringVar(value="Todos")
        tipo_opciones = ["Todos", "Casa", "Departamento", "Terreno", "Local comercial", "Otro"]
        self.search_tipo_combo = ttk.Combobox(filtros_frame, textvariable=self.search_tipo_var, values=tipo_opciones, width=20, state="readonly")
        self.search_tipo_combo.grid(row=1, column=3, sticky='w', pady=(10,0), padx=(0,20))

        # Botones
        botones_frame = ttk.Frame(frame)
        botones_frame.pack(pady=10)
        ttk.Button(botones_frame, text="🔍 Buscar", command=self.realizar_busqueda).pack(side='left', padx=5)
        ttk.Button(botones_frame, text="📥 Descargar Resultados", command=self.descargar_resultados).pack(side='left', padx=5)

        # Resultados
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, pady=(10,0))

        self.tree = ttk.Treeview(tree_frame, columns=("fecha", "agente", "zona", "barrio", "tipo", "presupuesto", "descripcion"), show='headings')
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configurar columnas
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("agente", text="Agente")
        self.tree.heading("zona", text="Zona")
        self.tree.heading("barrio", text="Barrio")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("presupuesto", text="Presupuesto")
        self.tree.heading("descripcion", text="Descripción")

        self.tree.column("fecha", width=100, anchor='center')
        self.tree.column("agente", width=100, anchor='center')
        self.tree.column("zona", width=120, anchor='center')
        self.tree.column("barrio", width=120, anchor='center')
        self.tree.column("tipo", width=100, anchor='center')
        self.tree.column("presupuesto", width=100, anchor='e')
        self.tree.column("descripcion", width=250, anchor='w')

        self.resultados_df = pd.DataFrame()
        self.actualizar_barrios_busqueda()

    def actualizar_barrios_busqueda(self, event=None):
        zona = self.search_zona_var.get()
        if zona == "Todas":
            barrios = ["Todos"] + LISTA_BARRIOS
        else:
            barrios = ["Todos"] + ZONAS_BARRIOS.get(zona, [])
        self.search_barrio_combo['values'] = barrios
        self.search_barrio_var.set("Todos")

    def realizar_busqueda(self):
        # Limpiar resultados anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro = self.df_busquedas.copy()
        if filtro.empty:
            messagebox.showinfo("Sin datos", "No hay búsquedas registradas.")
            return

        if self.search_zona_var.get() != "Todas":
            filtro = filtro[filtro["zona"] == self.search_zona_var.get()]
        if self.search_barrio_var.get() != "Todos":
            filtro = filtro[filtro["barrio"] == self.search_barrio_var.get()]
        if self.search_agente_var.get() != "Todos":
            filtro = filtro[filtro["agente"] == self.search_agente_var.get()]
        if self.search_tipo_var.get() != "Todos":
            filtro = filtro[filtro["tipo de propiedad"] == self.search_tipo_var.get()]

        if filtro.empty:
            messagebox.showinfo("Sin resultados", "No se encontraron coincidencias.")
            self.resultados_df = pd.DataFrame()
        else:
            self.resultados_df = filtro.copy()
            for _, row in filtro.iterrows():
                self.tree.insert("", "end", values=(
                    row["fecha"],
                    row["agente"],
                    row["zona"],
                    row["barrio"],
                    row["tipo de propiedad"],
                    f"${float(row['presupuesto']):,.2f}" if pd.notna(row['presupuesto']) else "$0.00",
                    row["descripcion"]
                ))

    def descargar_resultados(self):
        if self.resultados_df.empty:
            messagebox.showwarning("Advertencia", "No hay resultados para descargar.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            title="Guardar resultados"
        )
        if filepath:
            try:
                self.resultados_df.to_excel(filepath, index=False)
                messagebox.showinfo("Éxito", f"Resultados guardados en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    # ------------------------------
    def actualizar_dropdowns(self):
        # Actualizar combos de agentes en todas las pestañas
        self.combo_agente['values'] = self.lista_agentes
        if self.lista_agentes:
            self.combo_agente.set(self.lista_agentes[0])
        else:
            self.combo_agente.set("")

        # Actualizar combo de búsqueda
        agentes_opciones = ["Todos"] + self.lista_agentes
        self.search_agente_combo['values'] = agentes_opciones
        self.search_agente_var.set("Todos")

# ==============================
# 4. EJECUCIÓN PRINCIPAL
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = BusquedaActivaApp(root)
    root.mainloop()