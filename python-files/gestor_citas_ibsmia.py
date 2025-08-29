
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

citas_df = pd.DataFrame({})

class CitasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Citas IBSMIA")
        self.tree = ttk.Treeview(root, columns=list(citas_df.columns), show='headings')
        for col in citas_df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(expand=True, fill='both')
        self.load_data()

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill='x')
        tk.Button(btn_frame, text="Editar", command=self.edit_entry).pack(side='left')
        tk.Button(btn_frame, text="Eliminar", command=self.delete_entry).pack(side='left')
        tk.Button(btn_frame, text="Enviar SMS", command=self.send_sms).pack(side='left')

    def load_data(self):
        for _, row in citas_df.iterrows():
            self.tree.insert('', 'end', values=list(row))

    def edit_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una cita para editar.")
            return
        item = self.tree.item(selected[0])
        values = item['values']
        messagebox.showinfo("Editar", f"Editar cita de {values[4]} (simulado)")

    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una cita para eliminar.")
            return
        self.tree.delete(selected[0])
        messagebox.showinfo("Eliminar", "Cita eliminada correctamente.")

    def send_sms(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una cita para enviar SMS.")
            return
        item = self.tree.item(selected[0])
        values = item['values']
        messagebox.showinfo("SMS", f"SMS enviado a {values[6]} (simulado)")

if __name__ == '__main__':
    citas_df = pd.DataFrame({})
    root = tk.Tk()
    app = CitasApp(root)
    root.mainloop()
