#Create By Leandro A Ferreira 
#21/07/2025
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import re
import os
import threading
import sys

def resource_path(relative_path):
    """Retorna o caminho absoluto para recursos, compatível com PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class LoadingWindow:
    def __init__(self, master, message="Carregando..."):
        self.top = tk.Toplevel(master)
        self.top.title("Por favor, aguarde")
        self.top.geometry("300x100")
        self.top.transient(master)
        self.top.grab_set()
        self.top.resizable(False, False)

        label = tk.Label(self.top, text=message)
        label.pack(pady=10)

        self.progress = ttk.Progressbar(self.top, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=10)
        self.progress.start(10)

    def close(self):
        self.progress.stop()
        self.top.destroy()

class ComparadorPlanilhas:
    def __init__(self, master):
        self.master = master
        master.title("Comparador de Planilhas ADMS-EDP")
        master.geometry("450x600")
        master.resizable(False, False)

        self.df1 = None
        self.df2 = None
        self.nome_arquivo1 = ""
        self.nome_arquivo2 = ""

        if PIL_AVAILABLE and os.path.exists("logo5.png"):
            try:
                logo_img = Image.open(resource_path("logo5.png"))
                logo_img = logo_img.resize((200, 60))
                self.logo = ImageTk.PhotoImage(logo_img)
                self.logo_label = tk.Label(master, image=self.logo)
                self.logo_label.pack(pady=(10, 5))
            except Exception as e:
                print("Erro ao carregar a logo:", e)

        self.btn_arquivo1 = tk.Button(master, text="Selecionar Primeiro Arquivo", command=self.selecionar_arquivo1)
        self.btn_arquivo1.pack(pady=5)

        self.combo_aba1 = ttk.Combobox(master, state="readonly")
        self.combo_aba1.pack(pady=5)
        self.combo_coluna1 = ttk.Combobox(master, state="readonly")
        self.combo_coluna1.pack(pady=5)

        separator = ttk.Separator(master, orient='horizontal')
        separator.pack(fill='x', pady=10)

        self.btn_arquivo2 = tk.Button(master, text="Selecionar Segundo Arquivo", command=self.selecionar_arquivo2)
        self.btn_arquivo2.pack(pady=5)

        self.combo_aba2 = ttk.Combobox(master, state="readonly")
        self.combo_aba2.pack(pady=5)
        self.combo_coluna2 = ttk.Combobox(master, state="readonly")
        self.combo_coluna2.pack(pady=5)

        self.btn_comparar = tk.Button(master, text="Comparar", command=self.comparar)
        self.btn_comparar.pack(pady=10)

        self.frame_estatisticas = tk.Frame(master)
        self.frame_estatisticas.pack(pady=10)

    def selecionar_arquivo1(self):
        caminho = filedialog.askopenfilename(title="Selecionar primeiro arquivo", filetypes=[("Arquivos Excel", ".xlsx .xls")])
        if caminho:
            self.caminho1 = caminho
            self.nome_arquivo1 = os.path.basename(caminho)

            if hasattr(self, 'label_arquivo1'):
                self.label_arquivo1.destroy()
            self.label_arquivo1 = tk.Label(self.master, text=f"Arquivo 1: {self.nome_arquivo1}", font=("Arial", 10, "bold"))
            self.label_arquivo1.pack(before=self.combo_aba1, pady=(10, 0))

            self.xls1 = pd.ExcelFile(caminho)
            abas = ["Selecione uma aba"] + self.xls1.sheet_names
            self.combo_aba1["values"] = abas
            self.combo_aba1.current(0)
            self.combo_aba1.bind("<<ComboboxSelected>>", lambda e: self.carregar_colunas_threaded(self.xls1, self.combo_aba1.get(), self.combo_coluna1, True, caminho))

    def selecionar_arquivo2(self):
        caminho = filedialog.askopenfilename(title="Selecionar segundo arquivo", filetypes=[("Arquivos Excel", ".xlsx .xls")])
        if caminho:
            self.caminho2 = caminho
            self.nome_arquivo2 = os.path.basename(caminho)

            if hasattr(self, 'label_arquivo2'):
                self.label_arquivo2.destroy()
            self.label_arquivo2 = tk.Label(self.master, text=f"Arquivo 2: {self.nome_arquivo2}", font=("Arial", 10, "bold"))
            self.label_arquivo2.pack(before=self.combo_aba2, pady=(10, 0))

            self.xls2 = pd.ExcelFile(caminho)
            abas = ["Selecione uma aba"] + self.xls2.sheet_names
            self.combo_aba2["values"] = abas
            self.combo_aba2.current(0)
            self.combo_aba2.bind("<<ComboboxSelected>>", lambda e: self.carregar_colunas_threaded(self.xls2, self.combo_aba2.get(), self.combo_coluna2, False, caminho))

    def carregar_colunas_threaded(self, xls, aba, combo_coluna, is_first, caminho):
        loading = LoadingWindow(self.master, "Carregando colunas...")
        self.master.update()

        def task():
            print(f"Iniciando leitura da aba: {aba} do arquivo: {caminho}")
            try:
                is_tdt = caminho.endswith("_TDT.xlsx") or caminho.endswith("_TDT.xls")
                df = xls.parse(aba, skiprows=3 if is_tdt else 0)
                print(f"Colunas carregadas: {df.columns.tolist()}")
                colunas = ["Selecione uma coluna"] + df.columns.tolist()
                combo_coluna["values"] = colunas
                combo_coluna.current(0)

                if is_first:
                    self.df1 = df
                else:
                    self.df2 = df
            except Exception as e:
                print(f"Erro ao carregar colunas: {e}")
                messagebox.showerror("Erro", f"Erro ao carregar colunas:\n{e}")
            finally:
                loading.close()

        threading.Thread(target=task).start()

    def comparar(self):
        if self.df1 is None or self.df2 is None:
            messagebox.showerror("Erro", "Ambos os arquivos devem ser carregados.")
            return

        col1 = self.combo_coluna1.get()
        col2 = self.combo_coluna2.get()

        if col1 == "Selecione uma coluna" or col2 == "Selecione uma coluna":
            messagebox.showerror("Erro", "Ambas as colunas devem ser selecionadas.")
            return

        loading = LoadingWindow(self.master, "Comparando dados...")
        self.master.update()

        try:
            coluna1 = self.df1[col1].dropna().astype(str).str.strip()
            coluna2 = self.df2[col2].dropna().astype(str).str.strip()

            coluna1 = coluna1[~coluna1.str.contains(r'(?:AJM\d+|E81\d+)$', regex=True)]
            coluna2 = coluna2[~coluna2.str.contains(r'(?:AJM\d+|E81\d+)$', regex=True)]

            set1 = set(coluna1)
            set2 = set(coluna2)

            faltando_na_planilha2 = sorted(set1 - set2)
            faltando_na_planilha1 = sorted(set2 - set1)

            df_resultado = pd.DataFrame({
                f'Presentes em {self.nome_arquivo1} mas ausentes em {self.nome_arquivo2}': pd.Series(faltando_na_planilha2),
                f'Presentes em {self.nome_arquivo2} mas ausentes em {self.nome_arquivo1}': pd.Series(faltando_na_planilha1)
            })

            df_resultado.loc[len(df_resultado)] = [
                f'Total: {len(faltando_na_planilha2)}',
                f'Total: {len(faltando_na_planilha1)}'
            ]
            df_resultado.loc[len(df_resultado)] = [
                f'Total considerados {self.nome_arquivo1}: {len(set1)}',
                f'Total considerados {self.nome_arquivo2}: {len(set2)}'
            ]

            nome1 = os.path.splitext(self.nome_arquivo1)[0]
            nome2 = os.path.splitext(self.nome_arquivo2)[0]
            nome_saida = f"{nome2}_{nome1}.xlsx" if 'TDT' in nome1.upper() else f"{nome1}_{nome2}.xlsx"

            df_resultado.to_excel(nome_saida, index=False)

            self.mostrar_estatisticas(set1, set2, faltando_na_planilha2, faltando_na_planilha1)

            messagebox.showinfo("Sucesso", f"Comparação concluída!\nArquivo '{nome_saida}' criado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro durante a comparação:\n{e}")
        finally:
            loading.close()

    def mostrar_estatisticas(self, set1, set2, faltando1, faltando2):
        for widget in self.frame_estatisticas.winfo_children():
            widget.destroy()

        stats = [
            f"Total considerados {self.nome_arquivo1}: {len(set1)}",
            f"Total considerados {self.nome_arquivo2}: {len(set2)}",
            f"Presentes em {self.nome_arquivo1} mas ausentes em {self.nome_arquivo2}: {len(faltando1)}",
            f"Presentes em {self.nome_arquivo2} mas ausentes em {self.nome_arquivo1}: {len(faltando2)}",
            f"Interseção (comuns): {len(set1 & set2)}",
            f"Total único (união): {len(set1 | set2)}"
        ]

        tk.Label(self.frame_estatisticas, text="📊 Estatísticas da Comparação", font=("Arial", 10, "bold")).pack()
        for stat in stats:
            tk.Label(self.frame_estatisticas, text=stat, anchor="w").pack(fill="x", padx=10, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComparadorPlanilhas(root)
    root.mainloop()
