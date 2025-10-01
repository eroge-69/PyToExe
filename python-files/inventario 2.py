import pandas as pd
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os  # 👈 Necesario para verificar si el archivo existe

COLUMNAS = ["Producto", "Cantidad", "Restante", "Fecha de ingreso", "Último uso"]
ARCHIVO_CSV = "inventario_guardado.csv"  # 👈 Archivo donde se guardará el inventario

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 Inventario Interno")
        self.root.geometry("1300x750")

        style = ttk.Style("cosmo")
        style.configure("BotonNegro.TButton", font=("Arial", 12))

        # Cargar inventario desde CSV si existe
        if os.path.exists(ARCHIVO_CSV):
            self.df = pd.read_csv(ARCHIVO_CSV)
        else:
            self.df = pd.DataFrame(columns=COLUMNAS)

        # Buscador
        self.search_var = tk.StringVar()
        buscador_frame = ttk.Frame(self.root)
        buscador_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(buscador_frame, text="🔍 Buscar producto:", font=("Arial",12)).pack(side="left", padx=5)
        tk.Entry(buscador_frame, textvariable=self.search_var, font=("Arial",12)).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(buscador_frame, text="🔄 Buscar", command=self.buscar_producto,
                  font=("Arial", 12), fg="black", bd=2).pack(side="left", padx=5)
        tk.Button(buscador_frame, text="❌ Limpiar", command=self.limpiar_busqueda,
                  font=("Arial", 12), fg="black", bd=2).pack(side="left", padx=5)

        # Tabla
        self.tree = ttk.Treeview(self.root, columns=COLUMNAS, show="headings", bootstyle=INFO)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in COLUMNAS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center", minwidth=100, stretch=True)

        estilo_tabla = ttk.Style()
        estilo_tabla.configure("Treeview", font=("Arial", 12), rowheight=30,
                               bordercolor="black", relief="solid")
        estilo_tabla.configure("Treeview.Heading", font=("Arial", 14, "bold"),
                               relief="solid", bordercolor="black")
        estilo_tabla.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        self.tree.tag_configure("par", background="#f2f2f2")
        self.tree.tag_configure("impar", background="white")

        self.tree.bind("<Double-1>", self.editar_celda)

        # Botones
        botones_frame = ttk.Frame(self.root)
        botones_frame.pack(fill="x", padx=10, pady=10)
        botones = [
            ("➕ Agregar producto", self.agregar_producto),
            ("🗑 Eliminar producto", self.eliminar_producto),
            ("📦 Registrar uso", self.registrar_uso),
            ("📄 Exportar PDF", self.exportar_pdf),
            ("💾 Exportar Excel", self.exportar_excel),
            ("🔄 Actualizar tabla", self.actualizar_tabla),
            ("❌ Salir", self.root.quit)
        ]
        for i, (texto, comando) in enumerate(botones):
            btn = ttk.Button(botones_frame, text=texto, command=comando,
                             bootstyle=("outline-dark", "toolbutton"),
                             style="BotonNegro.TButton", width=20)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            botones_frame.grid_columnconfigure(i, weight=1)

        self.actualizar_tabla()

    def actualizar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, (_, row) in enumerate(self.df.iterrows()):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=list(row), tags=(tag,))

    def editar_celda(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        item = seleccion[0]
        col = self.tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1
        valores = list(self.tree.item(item, "values"))
        valor_actual = valores[col_index]

        if col_index in [1,2]:
            nuevo_valor = simpledialog.askfloat("Editar valor", f"Valor actual: {valor_actual}",
                                                initialvalue=float(valor_actual) if valor_actual else 0)
        else:
            nuevo_valor = simpledialog.askstring("Editar valor", f"Valor actual: {valor_actual}", initialvalue=valor_actual)

        if nuevo_valor is None:
            return

        valores[col_index] = nuevo_valor
        try:
            cantidad = float(valores[1])
            valores[2] = cantidad
        except:
            valores[2] = 0

        while len(valores) < len(COLUMNAS):
            valores.append("")

        self.tree.item(item, values=valores)
        self.df.loc[self.df["Producto"] == valores[0], :] = valores

    def agregar_producto(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar producto")
        ventana.geometry("350x200")
        ventana.grab_set()

        tk.Label(ventana, text="Nombre del producto:", font=("Arial",12)).pack(pady=5)
        entry_producto = tk.Entry(ventana, font=("Arial",12))
        entry_producto.pack(pady=5)
        entry_producto.focus()

        tk.Label(ventana, text="Cantidad inicial:", font=("Arial",12)).pack(pady=5)
        entry_cantidad = tk.Entry(ventana, font=("Arial",12))
        entry_cantidad.pack(pady=5)

        def guardar_nuevo():
            producto = entry_producto.get().strip()
            if not producto:
                messagebox.showwarning("Atención", "Debe ingresar un nombre de producto.")
                return
            try:
                cantidad = float(entry_cantidad.get())
            except:
                messagebox.showwarning("Atención", "Cantidad inválida")
                return

            fecha_ingreso = datetime.now().strftime("%d/%m/%Y")

            if producto in self.df["Producto"].values:
                idx = self.df.index[self.df["Producto"] == producto][0]
                nueva_cantidad = self.df.at[idx, "Restante"] + cantidad
                self.df.at[idx, "Cantidad"] = nueva_cantidad
                self.df.at[idx, "Restante"] = nueva_cantidad
                self.df.at[idx, "Fecha de ingreso"] = fecha_ingreso
            else:
                nuevo = pd.DataFrame([[producto, cantidad, cantidad, fecha_ingreso, ""]], columns=COLUMNAS)
                self.df = pd.concat([self.df, nuevo], ignore_index=True)

            self.actualizar_tabla()
            ventana.destroy()

        def enter_pressed(event):
            if ventana.focus_get() == entry_producto:
                entry_cantidad.focus()
            elif ventana.focus_get() == entry_cantidad:
                guardar_nuevo()

        ventana.bind("<Return>", enter_pressed)

        botones_frame = tk.Frame(ventana)
        botones_frame.pack(pady=10)
        tk.Button(botones_frame, text="Aceptar", command=guardar_nuevo, width=12, fg="black").pack(side="left", padx=10)
        tk.Button(botones_frame, text="Cancelar", command=ventana.destroy, width=12, fg="black").pack(side="right", padx=10)

    def eliminar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para eliminar.")
            return
        valores = self.tree.item(seleccion[0], "values")
        producto = valores[0]
        if messagebox.askyesno("Confirmar", f"¿Seguro que desea eliminar '{producto}'?"):
            self.df = self.df[self.df["Producto"] != producto]
            self.actualizar_tabla()

    def registrar_uso(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para registrar uso.")
            return
        item = seleccion[0]
        valores = list(self.tree.item(item, "values"))
        producto = valores[0]
        try:
            restante_actual = float(valores[2])
        except:
            restante_actual = 0
        cantidad_usada = simpledialog.askfloat("Registrar uso", f"Cantidad a usar de '{producto}':",
                                               minvalue=0, maxvalue=restante_actual)
        if cantidad_usada is None:
            return
        valores[2] = restante_actual - cantidad_usada
        valores[4] = datetime.now().strftime("%d/%m/%Y")
        self.tree.item(item, values=valores)
        self.df.loc[self.df["Producto"] == producto, :] = valores

    def buscar_producto(self):
        texto = self.search_var.get().lower()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, (_, row) in enumerate(self.df.iterrows()):
            if texto in str(row["Producto"]).lower():
                tag = "par" if i % 2 == 0 else "impar"
                self.tree.insert("", "end", values=list(row), tags=(tag,))

    def limpiar_busqueda(self):
        self.search_var.set("")
        self.actualizar_tabla()

    def exportar_excel(self):
        if self.df.empty:
            messagebox.showwarning("Atención", "No hay datos para exportar.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Archivos Excel", "*.xlsx")])
        if ruta:
            self.df.to_excel(ruta, index=False)
            messagebox.showinfo("Éxito", f"Inventario exportado a Excel:\n{ruta}")

    def exportar_pdf(self):
        if self.df.empty:
            messagebox.showwarning("Atención", "No hay datos para exportar.")
            return

        ruta_pdf = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("Archivo PDF", "*.pdf")])
        if not ruta_pdf:
            return

        doc = SimpleDocTemplate(ruta_pdf, pagesize=A4)
        elementos = []
        estilos = getSampleStyleSheet()
        titulo = Paragraph("📦 Informe de Inventario", estilos["Title"])
        elementos.append(titulo)
        elementos.append(Spacer(1, 20))

        data = [list(self.df.columns)] + self.df.values.tolist()
        data = [[str(c) for c in fila] for fila in data]

        colWidths = [max(100, min(max(len(str(row[i]))*7, 50), 300)) for i in range(len(data[0]))]

        tabla = Table(data, colWidths=colWidths, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4CAF50")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 12),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("FONTSIZE", (0,1), (-1,-1), 10)
        ]))
        elementos.append(tabla)
        doc.build(elementos)

        messagebox.showinfo("Éxito", f"Informe exportado a PDF:\n{ruta_pdf}")

# ==============================
# Inicio del programa
# ==============================
if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")
    app = InventarioApp(root)

    # Guardar datos al cerrar la ventana
    def guardar_al_salir():
        app.df.to_csv(ARCHIVO_CSV, index=False)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", guardar_al_salir)
    root.mainloop()
