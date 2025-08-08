
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# === Interface para seleção de arquivo ===
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Selecione o arquivo HTML do cromatógrafo",
    filetypes=[("Arquivos HTML", "*.html"), ("Todos os arquivos", "*.*")]
)

if not file_path:
    messagebox.showinfo("Info", "Nenhum arquivo selecionado.")
    exit()

# === Leitura e análise do HTML ===
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "html.parser")

# Pega a primeira tabela
tables = soup.find_all("table")
if not tables:
    messagebox.showerror("Erro", "Nenhuma tabela encontrada no HTML.")
    exit()

df = pd.read_html(str(tables[0]))[0]
df.columns = [str(c).strip() for c in df.columns]

# Detecta a coluna de data/hora
datetime_col = None
for col in df.columns:
    if "date" in col.lower() or "hora" in col.lower() or "time" in col.lower():
        datetime_col = col
        break

if not datetime_col:
    messagebox.showerror("Erro", "Coluna de data/hora não encontrada.")
    exit()

df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")
df = df.dropna(subset=[datetime_col])
df["Data"] = df[datetime_col].dt.date

numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
medias_diarias = df.groupby("Data")[numeric_cols].mean().reset_index()

saida_csv = file_path.replace(".html", "_medias_diarias.csv")
medias_diarias.to_csv(saida_csv, index=False, sep=";")

messagebox.showinfo("Sucesso", f"Médias diárias salvas em:
{saida_csv}")
