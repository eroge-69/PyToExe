import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from datetime import datetime
import os

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer Projetos P&D")
        self.root.geometry("300x350")

        self.file_path = None
        self.start_time = None

        # Labels
        tk.Label(root, text="Selecione o arquivo Excel:").pack(pady=5)
        tk.Button(root, text="Carregar Excel", command=self.load_excel).pack(pady=5)

        # Dropdowns
        tk.Label(root, text="Projeto:").pack()
        self.project_var = tk.StringVar()
        self.project_cb = ttk.Combobox(root, textvariable=self.project_var, state="disabled")
        self.project_cb.pack(pady=5)

        tk.Label(root, text="Analista:").pack()
        self.analyst_var = tk.StringVar()
        self.analyst_cb = ttk.Combobox(root, textvariable=self.analyst_var, state="disabled")
        self.analyst_cb.pack(pady=5)

        tk.Label(root, text="Atividade:").pack()
        self.activity_var = tk.StringVar()
        self.activity_cb = ttk.Combobox(root, textvariable=self.activity_var, state="disabled")
        self.activity_cb.pack(pady=5)

        # Botões
        self.start_btn = tk.Button(root, text="Start", command=self.start, state="disabled")
        self.start_btn.pack(pady=10)

        self.stop_btn = tk.Button(root, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(pady=10)

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        self.file_path = file_path
        try:
            df = pd.read_excel(self.file_path, sheet_name="Banco de dados")

            if not {"Projeto", "Analista", "Atividades Realizadas"}.issubset(df.columns):
                messagebox.showerror("Erro", "A aba 'Banco de dados' deve conter as colunas: Projeto, Analista e Atividades Realizadas")
                return

            # Preenche listas suspensas
            self.project_cb["values"] = sorted(df["Projeto"].dropna().unique())
            self.analyst_cb["values"] = sorted(df["Analista"].dropna().unique())
            self.activity_cb["values"] = sorted(df["Atividades Realizadas"].dropna().unique())

            self.project_cb.config(state="readonly")
            self.analyst_cb.config(state="readonly")
            self.activity_cb.config(state="readonly")
            self.start_btn.config(state="normal")

            messagebox.showinfo("Sucesso", "Planilha carregada com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a planilha:\n{e}")

    def start(self):
        if not self.project_var.get() or not self.analyst_var.get() or not self.activity_var.get():
            messagebox.showwarning("Aviso", "Selecione Projeto, Analista e Atividade antes de iniciar.")
            return
        self.start_time = datetime.now()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def stop(self):
        if not self.start_time:
            return

        end_time = datetime.now()
        duration = (end_time - self.start_time).seconds // 60  # minutos
        month = end_time.strftime("%B")

        new_data = {
            "Projeto": self.project_var.get(),
            "Atividade": self.activity_var.get(),
            "Analista": self.analyst_var.get(),
            "Início": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Fim": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Tempo Gasto (min)": duration,
            "Mês": month
        }

        # Lê aba Atividades se existir
        try:
            df = pd.read_excel(self.file_path, sheet_name="Atividades")
        except:
            df = pd.DataFrame(columns=["Projeto", "Atividade", "Analista", "Início", "Fim", "Tempo Gasto (min)", "Mês"])

        # Adiciona nova linha
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        # Grava no Excel substituindo a aba Atividades
        with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name="Atividades", index=False)

        messagebox.showinfo("Sucesso", "Atividade registrada com sucesso!")

        # Reset
        self.start_time = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
