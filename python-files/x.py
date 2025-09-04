import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import os
import shutil
from PIL import Image, ImageTk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Actas")
        self.geometry("1000x800")
        self.config(bg="#f0f0f0")

        # Conectar a la base de datos
        self.conn = sqlite3.connect("actas.db")
        self.c = self.conn.cursor()
        self.create_table()

        # Variable para el logo
        self.logo_image = None
        self.logo_path = None # Para guardar la ruta del logo si se carga desde archivo

        self.create_widgets()
        self.load_data()
        self.load_logo() # Cargar el logo al iniciar la aplicación

    def create_table(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                numero_acta TEXT,
                fecha TEXT,
                operadora TEXT,
                responsables TEXT,
                actividad TEXT,
                tipo TEXT,
                documentos BLOB
            )
        """)
        # Crear tabla para el logo si no existe
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor BLOB
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezado (cintillo para logo)
        self.header_frame = tk.Frame(main_frame, bg="gray", height=80)
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        self.logo_label = tk.Label(self.header_frame, bg="gray")
        self.logo_label.pack(pady=5)

        # Barra de menú
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menú Edición
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edición", menu=edit_menu)
        edit_menu.add_command(label="Copiar", command=lambda: self.focus_get().event_generate("<<Copy>>"))
        edit_menu.add_command(label="Pegar", command=lambda: self.focus_get().event_generate("<<Paste>>"))
        edit_menu.add_command(label="Cortar", command=lambda: self.focus_get().event_generate("<<Cut>>"))

        # Menú Configuración (para el logo)
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuración", menu=config_menu)
        config_menu.add_command(label="Cambiar Logo", command=self.change_logo)

        # Menú Estadística
        stats_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Estadística", menu=stats_menu)
        stats_menu.add_command(label="Mostrar Estadísticas", command=self.show_stats)

        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)

        # Frame para los campos y botones
        form_frame = tk.Frame(main_frame, bg="#e0e0e0", padx=10, pady=10)
        form_frame.pack(fill="x", pady=10)

        # Widgets de entrada
        self.entries = {}
        fields = [
            ("Número de Acta:", "numero_acta", "text"),
            ("Fecha:", "fecha", "date"),
            ("Operadora/Laboratorio:", "operadora", "text"),
            ("Responsables:", "responsables", "text"),
            ("Actividad:", "actividad", "option"),
            ("Tipo:", "tipo", "option"),
            ("Documentos:", "documentos", "adjunto")
        ]

        row_index = 0
        for i, (label_text, key, type) in enumerate(fields):
            tk.Label(form_frame, text=label_text, bg="#e0e0e0").grid(row=row_index, column=0, sticky="w", pady=2, padx=5)

            if type == "text" or type == "date":
                entry = tk.Entry(form_frame, width=50)
                entry.grid(row=row_index, column=1, pady=2, padx=5, columnspan=2)
                self.entries[key] = entry
            elif type == "option":
                options = []
                if key == "actividad":
                    options = ["Verificación", "Inspección", "Calibración", "Otros"]
                elif key == "tipo":
                    options = ["Fiscal", "Referencial", "Otro"]
                
                var = tk.StringVar(self)
                var.set(options[0])
                option_menu = tk.OptionMenu(form_frame, var, *options)
                option_menu.grid(row=row_index, column=1, pady=2, padx=5, sticky="ew", columnspan=2)
                self.entries[key] = var
            elif type == "adjunto":
                self.documentos = []
                docs_frame = tk.Frame(form_frame, bg="#e0e0e0")
                docs_frame.grid(row=row_index, column=1, pady=2, padx=5, sticky="ew", columnspan=2)
                
                self.docs_listbox = tk.Listbox(docs_frame, height=3, width=40)
                self.docs_listbox.pack(side="left", fill="x", expand=True)
                
                add_doc_btn = tk.Button(docs_frame, text="Adjuntar", command=self.add_document)
                add_doc_btn.pack(side="left", padx=5)

            row_index += 1

        # Botones
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(side="right", fill="y", padx=10)

        search_btn = tk.Button(button_frame, text="Buscar", width=15, command=self.search_record)
        search_btn.pack(pady=5)
        save_btn = tk.Button(button_frame, text="Guardar", width=15, command=self.save_record)
        save_btn.pack(pady=5)
        delete_btn = tk.Button(button_frame, text="Eliminar", width=15, command=self.delete_record)
        delete_btn.pack(pady=5)
        edit_btn = tk.Button(button_frame, text="Editar", width=15, command=self.edit_record)
        edit_btn.pack(pady=5)
        export_btn = tk.Button(button_frame, text="Exportar", width=15, command=self.export_records)
        export_btn.pack(pady=5)
        clear_db_btn = tk.Button(button_frame, text="Limpiar DB", width=15, command=self.vacuum_db)
        clear_db_btn.pack(pady=5)
        
        # Separador horizontal
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

        # Frame para la lista de registros
        list_frame = tk.Frame(main_frame, bg="#f0f0f0")
        list_frame.pack(fill="both", expand=True)

        # Treeview para mostrar los datos
        self.tree = ttk.Treeview(list_frame, columns=("No. Acta", "Fecha", "Operadora", "Responsables", "Actividad", "Tipo"), show="headings")
        self.tree.heading("No. Acta", text="No. Acta")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Operadora", text="Operadora/Laboratorio")
        self.tree.heading("Responsables", text="Responsables")
        self.tree.heading("Actividad", text="Actividad")
        self.tree.heading("Tipo", text="Tipo")
        
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.select_record)

    def load_logo(self):
        self.c.execute("SELECT valor FROM configuracion WHERE clave = 'logo'")
        logo_data = self.c.fetchone()
        if logo_data and logo_data[0]:
            try:
                # Guardar el BLOB en un archivo temporal para que PIL lo pueda abrir
                temp_file = "temp_logo.png" # Puedes usar otros formatos si lo deseas
                with open(temp_file, "wb") as f:
                    f.write(logo_data[0])
                
                img = Image.open(temp_file)
                img.thumbnail((self.header_frame.winfo_width(), self.header_frame.winfo_height()))
                self.logo_image = ImageTk.PhotoImage(img)
                self.logo_label.config(image=self.logo_image, text="")
                os.remove(temp_file) # Eliminar el archivo temporal
            except Exception as e:
                messagebox.showerror("Error de Logo", f"No se pudo cargar el logo: {e}")
                self.logo_label.config(text="Logo de la Empresa", font=("Helvetica", 16, "bold"), fg="white")
        else:
            self.logo_label.config(text="Logo de la Empresa", font=("Helvetica", 16, "bold"), fg="white")

    def change_logo(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de logo",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.gif"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    logo_data = f.read()
                
                self.c.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", ('logo', logo_data))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Logo actualizado exitosamente.")
                self.load_logo() # Recargar el logo para que se muestre
            except Exception as e:
                messagebox.showerror("Error al guardar logo", f"No se pudo guardar el logo: {e}")

    def add_document(self):
        file_paths = filedialog.askopenfilenames(
            title="Seleccionar documento(s)",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if file_paths:
            for path in file_paths:
                with open(path, "rb") as f:
                    file_data = f.read()
                    self.documentos.append((os.path.basename(path), file_data))
                    self.docs_listbox.insert(tk.END, os.path.basename(path))

    def save_record(self):
        numero_acta = self.entries["numero_acta"].get()
        fecha = self.entries["fecha"].get()
        operadora = self.entries["operadora"].get()
        responsables = self.entries["responsables"].get()
        actividad = self.entries["actividad"].get()
        tipo = self.entries["tipo"].get()
        
        if not all([numero_acta, fecha, operadora, responsables, actividad, tipo]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Convertir documentos a un solo BLOB
        doc_blob = b''
        if self.documentos:
            for name, data in self.documentos:
                doc_blob += name.encode('utf-8') + b'\n' + data + b'\n--DOC_SEPARATOR--\n'

        try:
            self.c.execute("INSERT INTO registros VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (numero_acta, fecha, operadora, responsables, actividad, tipo, doc_blob))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro guardado exitosamente.")
            self.clear_fields()
            self.load_data()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Error al guardar: {e}")

    def load_data(self):
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar registros desde la DB
        self.c.execute("SELECT numero_acta, fecha, operadora, responsables, actividad, tipo FROM registros")
        rows = self.c.fetchall()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

    def clear_fields(self):
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
        self.docs_listbox.delete(0, tk.END)
        self.documentos = []
    
    def select_record(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        record = self.tree.item(selected_item, "values")
        self.clear_fields()
        
        self.entries["numero_acta"].insert(0, record[0])
        self.entries["fecha"].insert(0, record[1])
        self.entries["operadora"].insert(0, record[2])
        self.entries["responsables"].insert(0, record[3])
        self.entries["actividad"].set(record[4])
        self.entries["tipo"].set(record[5])

    def search_record(self):
        search_term = self.entries["numero_acta"].get()
        self.c.execute("SELECT numero_acta, fecha, operadora, responsables, actividad, tipo FROM registros WHERE numero_acta LIKE ?", (f"%{search_term}%",))
        rows = self.c.fetchall()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for row in rows:
            self.tree.insert("", "end", values=row)
            
        if not rows:
            messagebox.showinfo("Búsqueda", "No se encontraron registros.")

    def delete_record(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un registro para eliminar.")
            return

        record = self.tree.item(selected_item, "values")
        confirm = messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el registro {record[0]}?")
        
        if confirm:
            self.c.execute("DELETE FROM registros WHERE numero_acta = ?", (record[0],))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro eliminado exitosamente.")
            self.clear_fields()
            self.load_data()
            
    def edit_record(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un registro para editar.")
            return
            
        old_record = self.tree.item(selected_item, "values")
        
        new_numero_acta = self.entries["numero_acta"].get()
        new_fecha = self.entries["fecha"].get()
        new_operadora = self.entries["operadora"].get()
        new_responsables = self.entries["responsables"].get()
        new_actividad = self.entries["actividad"].get()
        new_tipo = self.entries["tipo"].get()
        
        if not all([new_numero_acta, new_fecha, new_operadora, new_responsables, new_actividad, new_tipo]):
            messagebox.showerror("Error", "Todos los campos son obligatorios para la edición.")
            return

        try:
            self.c.execute("""
                UPDATE registros SET
                numero_acta = ?, fecha = ?, operadora = ?, responsables = ?, actividad = ?, tipo = ?
                WHERE numero_acta = ?
            """, (new_numero_acta, new_fecha, new_operadora, new_responsables, new_actividad, new_tipo, old_record[0]))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro actualizado exitosamente.")
            self.clear_fields()
            self.load_data()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"Error al actualizar: {e}")

    def export_records(self):
        save_path = filedialog.askdirectory(title="Seleccionar carpeta para exportar")
        if not save_path:
            return
            
        self.c.execute("SELECT numero_acta, documentos FROM registros WHERE documentos IS NOT NULL")
        records = self.c.fetchall()
        
        if not records:
            messagebox.showinfo("Exportar", "No hay documentos para exportar.")
            return
            
        try:
            for numero_acta, doc_blob in records:
                if doc_blob:
                    doc_blob_str = doc_blob.decode('utf-8')
                    parts = doc_blob_str.split('\n--DOC_SEPARATOR--\n')
                    
                    doc_folder = os.path.join(save_path, f"Acta_{numero_acta}")
                    os.makedirs(doc_folder, exist_ok=True)
                    
                    for part in parts:
                        if part.strip():
                            # Asegurarse de que el nombre del archivo es la primera línea antes de los datos binarios
                            name_end = part.find('\n')
                            if name_end != -1: # Si hay un salto de línea
                                file_name = part[:name_end].strip()
                                file_data_str = part[name_end+1:]
                                file_data = file_data_str.encode('utf-8')
                            else: # Si es solo el nombre del archivo sin datos (posiblemente un error o un archivo vacío)
                                file_name = part.strip()
                                file_data = b'' # No hay datos
                            
                            if file_name: # Solo guardar si hay un nombre de archivo
                                with open(os.path.join(doc_folder, file_name), "wb") as f:
                                    f.write(file_data)

            messagebox.showinfo("Exportar", "Documentos exportados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error de exportación", f"Ocurrió un error: {e}")

    def show_stats(self):
        stats_text = ""
        
        # Estadísticas de Actas por Año
        self.c.execute("SELECT substr(fecha, 7, 4) as anio, COUNT(*) as total FROM registros WHERE fecha LIKE '______/____' GROUP BY anio ORDER BY anio DESC")
        stats_text += "### Actas por Año\n"
        rows_by_year = self.c.fetchall()
        if not rows_by_year:
            stats_text += "- No hay datos de actas por año.\n"
        else:
            for row in rows_by_year:
                stats_text += f"- Año {row[0]}: {row[1]} actas\n"
        
        # Tipos de Actividad
        self.c.execute("SELECT actividad, COUNT(*) FROM registros GROUP BY actividad")
        stats_text += "\n### Tipos de Actividad\n"
        rows_by_activity = self.c.fetchall()
        if not rows_by_activity:
            stats_text += "- No hay datos de tipos de actividad.\n"
        else:
            for row in rows_by_activity:
                stats_text += f"- {row[0]}: {row[1]} registros\n"
            
        # Tipos de Fiscalización
        self.c.execute("SELECT tipo, COUNT(*) FROM registros GROUP BY tipo")
        stats_text += "\n### Tipos de Registro\n"
        rows_by_type = self.c.fetchall()
        if not rows_by_type:
            stats_text += "- No hay datos de tipos de registro.\n"
        else:
            for row in rows_by_type:
                stats_text += f"- {row[0]}: {row[1]} registros\n"
        
        messagebox.showinfo("Estadísticas", stats_text)

    def show_about(self):
        messagebox.showinfo("Acerca de", "Programa realizado por Reinaldo Andrade")

    def vacuum_db(self):
        confirm = messagebox.askyesno("Limpiar Base de Datos", "Esta acción compactará la base de datos para reducir su tamaño. ¿Desea continuar?")
        if confirm:
            try:
                self.conn.execute("VACUUM")
                self.conn.commit()
                messagebox.showinfo("Éxito", "La base de datos ha sido compactada exitosamente.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo compactar la base de datos: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()