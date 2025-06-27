import tkinter as tk
from tkinter import messagebox
import win32print
import win32api

def imprimir():
    try:
        hilo = entries["hilo"].get()
        prod = entries["prod"].get()
        denier = entries["denier"].get()
        color = entries["color"].get()
        epr = entries["epr"].get()
        fecha = entries["fecha"].get()
        turno = entries["turno"].get()
        linea = entries["linea"].get()
        parada = entries["parada"].get()
        ordpro = entries["ordpro"].get()
        lote = entries["lote"].get()
        op = entries["op"].get()
        cantidad = entries["cantidad"].get()


        if not hilo or not prod or not denier or not color:
            messagebox.showerror("Error", "Por favor completa los campos principales")
            return

        if not cantidad.isdigit() or int(cantidad) < 1:
            messagebox.showerror("Error", "Cantidad inválida")
            return

        cantidad_int = int(cantidad)

        zpl_single = f"""
^XA
^PW404
^LL144
^LH0,0

^FO-10,48^GB170,112,2^FS
^FO-179,48^GB180,112,2^FS

^FO12,20^A0N,26,26^FB384,1,0,C,0^FDETIQUETA EXTRUSION^FS

^FO-25,55^A0N,25,20^FDHILO:^FS
^FO-25,80^A0N,25,20^FDPROD:^FS
^FO-25,100^A0N,25,20^FDDENIER.:^FS
^FO-25,120^A0N,25,20^FDCOLOR:^FS
^FO-25,140^A0N,25,20^FDCOD. ERP:^FS
^FO-25,165^A0N,25,20^FDLOTE:^FS
^FO115,55^A0N,25,20^FD{hilo}^FS
^FO115,80^A0N,25,20^FD{prod}^FS
^FO115,100^A0N,25,20^FD{denier}^FS
^FO115,120^A0N,25,20^FD{color}^FS
^FO115,140^A0N,25,20^FD{epr}^FS
^FO115,165^A0N,25,20^FD{lote}^FS

^FO185,55^A0N,25,20^FDFECHA:^FS
^FO185,80^A0N,25,20^FDTURNO:^FS
^FO185,100^A0N,25,20^FDLINEA:^FS
^FO185,120^A0N,25,20^FDPARADA:^FS
^FO185,140^A0N,25,20^FDORD.PRO:^FS
^FO185,165^A0N,25,20^FDOP:^FS

^FO265,55^A0N,25,20^FD{fecha}^FS
^FO265,80^A0N,25,20^FD{turno}^FS
^FO265,100^A0N,25,20^FD{linea}^FS
^FO265,120^A0N,25,20^FD{parada}^FS
^FO265,140^A0N,25,20^FD{ordpro}^FS
^FO265,165^A0N,25,20^FD{op}^FS

^XZ
"""

        zpl = zpl_single * cantidad_int

        printer_name = "ZDesigner ZD421-203dpi ZPL"  # Cambia al nombre de tu impresora

        # Enviar a la impresora (modo RAW)
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Etiqueta Extrusion", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, zpl.encode("utf-8"))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

        messagebox.showinfo("Éxito", f"Se enviaron {cantidad} etiqueta(s) a impresión.")

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("ETIQUETA EXTRUSION")
root.geometry("450x600")

fields = [
    ("HILO:", "hilo"),
    ("PROD.:", "prod"),
    ("DENIER:", "denier"),
    ("COLOR:", "color"),
    ("COD.EPR:", "epr"),
    ("FECHA:", "fecha"),
    ("TURNO:", "turno"),
    ("LINEA:", "linea"),
    ("PARADA:", "parada"),
    ("ORD.PRO:", "ordpro"),
    ("LOTE:", "lote"),
    ("OP:", "op"),
    ("CANTIDAD:", "cantidad"),
]

entries = {}

y = 20
for label_text, var_name in fields:
    label = tk.Label(root, text=label_text)
    label.place(x=10, y=y)
    entry = tk.Entry(root)
    entry.place(x=120, y=y, width=300)
    entries[var_name] = entry
    y += 35

button = tk.Button(root, text="Imprimir", command=imprimir)
button.place(x=170, y=y + 10, width=100, height=30)

root.mainloop()
