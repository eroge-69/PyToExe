import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class ReemplazadorYMLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reemplazador YML")
        self.geometry("720x520")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Colores personalizados
        self.style.configure('TFrame', background='#f0f4f8')
        self.style.configure('TLabel', background='#f0f4f8', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.configure('TEntry', padding=5)
        self.style.configure('Treeview', font=('Segoe UI', 10), rowheight=24)
        self.style.map('TButton',
                       foreground=[('pressed', '#004080'), ('active', '#0066cc')],
                       background=[('pressed', '#cce6ff'), ('active', '#99ccff')])

        self.perfiles = {}
        self.current_profile = None

        self.create_widgets()
        self.load_profiles()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Pestaña Perfil
        self.frame_perfil = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_perfil, text='Perfiles')

        ttk.Label(self.frame_perfil, text="Perfiles:").grid(row=0, column=0, sticky='w', padx=5, pady=10)
        self.combo_perfiles = ttk.Combobox(self.frame_perfil, state="readonly", width=30)
        self.combo_perfiles.grid(row=0, column=1, sticky='w', padx=5)
        self.combo_perfiles.bind("<<ComboboxSelected>>", self.on_profile_selected)

        btn_nuevo = ttk.Button(self.frame_perfil, text="Nuevo Perfil", command=self.new_profile)
        btn_nuevo.grid(row=0, column=2, padx=10)
        btn_eliminar = ttk.Button(self.frame_perfil, text="Eliminar Perfil", command=self.delete_profile)
        btn_eliminar.grid(row=0, column=3, padx=10)

        ttk.Label(self.frame_perfil, text="Carpeta destino:").grid(row=1, column=0, sticky='w', padx=5, pady=10)
        self.entry_carpeta = ttk.Entry(self.frame_perfil, width=45)
        self.entry_carpeta.grid(row=1, column=1, columnspan=2, sticky='w', padx=5)
        btn_seleccionar = ttk.Button(self.frame_perfil, text="Seleccionar carpeta", command=self.select_folder)
        btn_seleccionar.grid(row=1, column=3, padx=10)

        # Pestaña Archivos/Reemplazos
        self.frame_reemplazos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_reemplazos, text='Archivos y Reemplazos')

        # Treeview con 3 columnas: archivo, buscar, reemplazar
        columns = ("archivo", "buscar", "reemplazar")
        self.tree = ttk.Treeview(self.frame_reemplazos, columns=columns, show="headings", selectmode='extended', height=15)
        self.tree.heading("archivo", text="Archivo (.yml)")
        self.tree.heading("buscar", text="Texto a buscar")
        self.tree.heading("reemplazar", text="Texto reemplazo")
        self.tree.column("archivo", width=180, anchor='w')
        self.tree.column("buscar", width=150, anchor='w')
        self.tree.column("reemplazar", width=180, anchor='w')
        self.tree.grid(row=0, column=0, sticky='nsew', padx=(10,0), pady=10)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.frame_reemplazos, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns', pady=10)

        # Panel de controles para agregar/editar reemplazos
        panel_controls = ttk.Frame(self.frame_reemplazos)
        panel_controls.grid(row=0, column=2, sticky='n', padx=10, pady=10)

        ttk.Label(panel_controls, text="Archivo (.yml):").grid(row=0, column=0, sticky='w')
        self.entry_archivo = ttk.Entry(panel_controls, width=30)
        self.entry_archivo.grid(row=1, column=0, pady=4)

        ttk.Label(panel_controls, text="Texto a buscar:").grid(row=2, column=0, sticky='w')
        self.entry_buscar = ttk.Entry(panel_controls, width=30)
        self.entry_buscar.grid(row=3, column=0, pady=4)

        ttk.Label(panel_controls, text="Texto reemplazo:").grid(row=4, column=0, sticky='w')
        self.entry_reemplazar = ttk.Entry(panel_controls, width=30)
        self.entry_reemplazar.grid(row=5, column=0, pady=4)

        btn_add = ttk.Button(panel_controls, text="Añadir reemplazo", command=self.add_replacement)
        btn_add.grid(row=6, column=0, pady=(10,4), sticky='ew')

        btn_del = ttk.Button(panel_controls, text="Eliminar selección", command=self.delete_selection)
        btn_del.grid(row=7, column=0, pady=4, sticky='ew')

        # Pestaña Aplicar Cambios
        self.frame_aplicar = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_aplicar, text='Aplicar Cambios')

        ttk.Label(self.frame_aplicar, text="Carpeta destino:").pack(padx=10, pady=(20,5), anchor='w')
        self.entry_carpeta_apply = ttk.Entry(self.frame_aplicar, width=60)
        self.entry_carpeta_apply.pack(padx=10, pady=5, anchor='w')

        btn_select_apply = ttk.Button(self.frame_aplicar, text="Seleccionar carpeta", command=self.select_folder_apply)
        btn_select_apply.pack(padx=10, pady=5, anchor='w')

        btn_apply = ttk.Button(self.frame_aplicar, text="Aplicar todos los cambios", command=self.apply_changes)
        btn_apply.pack(pady=30)

        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')

    def load_profiles(self):
        if not os.path.exists("perfiles.json"):
            with open("perfiles.json", "w", encoding='utf-8') as f:
                json.dump({}, f)
        with open("perfiles.json", "r", encoding='utf-8') as f:
            self.perfiles = json.load(f)
        self.combo_perfiles["values"] = list(self.perfiles.keys())
        if self.perfiles:
            self.combo_perfiles.current(0)
            self.load_profile(list(self.perfiles.keys())[0])

    def save_profiles(self):
        with open("perfiles.json", "w", encoding='utf-8') as f:
            json.dump(self.perfiles, f, indent=4, ensure_ascii=False)

    def on_profile_selected(self, event):
        perfil = self.combo_perfiles.get()
        self.load_profile(perfil)

    def load_profile(self, perfil):
        self.current_profile = perfil
        data = self.perfiles.get(perfil, {})
        carpeta = data.get("carpeta_destino", "")
        self.entry_carpeta.delete(0, tk.END)
        self.entry_carpeta.insert(0, carpeta)
        self.entry_carpeta_apply.delete(0, tk.END)
        self.entry_carpeta_apply.insert(0, carpeta)

        self.tree.delete(*self.tree.get_children())
        archivos = data.get("archivos", {})
        for archivo, reemplazos in archivos.items():
            for buscar, reemplazar in reemplazos.items():
                self.tree.insert("", tk.END, values=(archivo, buscar, reemplazar))

    def new_profile(self):
        nuevo_nombre = simpledialog.askstring("Nuevo perfil", "Nombre del nuevo perfil:")
        if nuevo_nombre:
            if nuevo_nombre in self.perfiles:
                messagebox.showerror("Error", "El perfil ya existe.")
                return
            self.perfiles[nuevo_nombre] = {"carpeta_destino": "", "archivos": {}}
            self.save_profiles()
            self.combo_perfiles["values"] = list(self.perfiles.keys())
            self.combo_perfiles.set(nuevo_nombre)
            self.load_profile(nuevo_nombre)

    def delete_profile(self):
        perfil = self.combo_perfiles.get()
        if not perfil:
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar el perfil '{perfil}'?"):
            self.perfiles.pop(perfil, None)
            self.save_profiles()
            self.combo_perfiles["values"] = list(self.perfiles.keys())
            if self.perfiles:
                self.combo_perfiles.current(0)
                self.load_profile(list(self.perfiles.keys())[0])
            else:
                self.current_profile = None
                self.entry_carpeta.delete(0, tk.END)
                self.entry_carpeta_apply.delete(0, tk.END)
                self.tree.delete(*self.tree.get_children())

    def select_folder(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.entry_carpeta.delete(0, tk.END)
            self.entry_carpeta.insert(0, carpeta)
            if self.current_profile:
                self.perfiles[self.current_profile]["carpeta_destino"] = carpeta
                self.save_profiles()
                self.status_var.set(f"Carpeta destino cambiada a: {carpeta}")

    def select_folder_apply(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.entry_carpeta_apply.delete(0, tk.END)
            self.entry_carpeta_apply.insert(0, carpeta)

    def add_replacement(self):
        archivo = self.entry_archivo.get().strip()
        buscar = self.entry_buscar.get().strip()
        reemplazar = self.entry_reemplazar.get().strip()
        if not archivo or not buscar:
            messagebox.showwarning("Atención", "Archivo y texto a buscar son obligatorios.")
            return
        if not self.current_profile:
            messagebox.showwarning("Atención", "Selecciona o crea un perfil primero.")
            return

        archivos = self.perfiles[self.current_profile].setdefault("archivos", {})
        reemplazos = archivos.setdefault(archivo, {})
        reemplazos[buscar] = reemplazar
        self.save_profiles()

        self.tree.insert("", tk.END, values=(archivo, buscar, reemplazar))
        self.entry_archivo.delete(0, tk.END)
        self.entry_buscar.delete(0, tk.END)
        self.entry_reemplazar.delete(0, tk.END)
        self.status_var.set(f"Reemplazo añadido: {archivo} - '{buscar}' → '{reemplazar}'")

    def delete_selection(self):
        selected = self.tree.selection()
        if not selected:
            return
        if not self.current_profile:
            messagebox.showwarning("Atención", "Selecciona o crea un perfil primero.")
            return
        for item in selected:
            vals = self.tree.item(item, "values")
            archivo, buscar = vals[0], vals[1]
            try:
                del self.perfiles[self.current_profile]["archivos"][archivo][buscar]
                if not self.perfiles[self.current_profile]["archivos"][archivo]:
                    del self.perfiles[self.current_profile]["archivos"][archivo]
            except KeyError:
                pass
            self.tree.delete(item)
        self.save_profiles()
        self.status_var.set(f"Reemplazos eliminados.")

    def apply_changes(self):
        carpeta = self.entry_carpeta_apply.get().strip()
        if not carpeta or not os.path.isdir(carpeta):
            messagebox.showerror("Error", "Selecciona una carpeta válida para aplicar los cambios.")
            return
        if not self.current_profile:
            messagebox.showwarning("Atención", "Selecciona o crea un perfil primero.")
            return

        archivos = self.perfiles[self.current_profile].get("archivos", {})
        if not archivos:
            messagebox.showwarning("Atención", "No hay archivos ni reemplazos configurados.")
            return

        total_files = 0
        total_replacements = 0

        for archivo, reemplazos in archivos.items():
            ruta_archivo = os.path.join(carpeta, archivo)
            if not os.path.isfile(ruta_archivo):
                self.status_var.set(f"Archivo no encontrado: {ruta_archivo}")
                continue

            try:
                with open(ruta_archivo, "r", encoding='utf-8') as f:
                    contenido = f.read()

                for buscar, reemplazar in reemplazos.items():
                    contenido = contenido.replace(buscar, reemplazar)
                    total_replacements += 1

                with open(ruta_archivo, "w", encoding='utf-8') as f:
                    f.write(contenido)
                total_files += 1
            except Exception as e:
                messagebox.showerror("Error", f"Error procesando {archivo}:\n{e}")

        self.status_var.set(f"Cambios aplicados a {total_files} archivos, {total_replacements} reemplazos.")

if __name__ == "__main__":
    app = ReemplazadorYMLApp()
    app.mainloop()
