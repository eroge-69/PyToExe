import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import time
import threading
import os
import getpass

# Cores e estilos
BG_COLOR = "#f2f2f2"
PRIMARY_COLOR = "#2b5797"  # Azul corporativo
BTN_COLOR = "#1f4e79"
TEXT_COLOR = "#333333"
FONT = ("Segoe UI", 10)
HEADER_FONT = ("Segoe UI", 12, "bold")

def process_txt_to_excel(txt_file, output_path, progress_label, progress_bar):
    start_time = time.time()

    try:
        with open(txt_file, 'r', encoding='latin-1') as file:
            lines = file.readlines()

        data = []
        current_record = {}
        reference_date = ""
        reference_code = ""
        total_lines = len(lines)

        for i, line in enumerate(lines):
            line = line.strip()

            # Atualizar a barra de progresso
            progress = int((i + 1) / total_lines * 100)
            progress_bar['value'] = progress
            progress_label.config(text=f"Processando... {progress}%")
            window.update_idletasks()

            if "Central de Registo de Crédito" in line:
                if i + 1 < len(lines):
                    match_date = re.search(r'(\d{2}\.\d{2}\.\d{4})', lines[i + 1])
                    if match_date:
                        reference_date = match_date.group(1).replace(".", "-")

                if i + 2 < len(lines):
                    match_ref = re.search(r'Referência: (.+)', lines[i + 2])
                    if match_ref:
                        reference_code = match_ref.group(1).strip().replace(" / ", "_")

            match = re.match(r'^(\d{11})\s+(.+)', line)
            if match:
                if current_record:
                    data.append(current_record)
                    current_record = {}

                current_record['Nº Central'] = match.group(1)
                current_record['Nome'] = match.group(2).strip()

            match_total = re.match(r'^Total \(em (\d+)\s+Bancos\):\s+(.*)', line)
            if match_total:
                current_record['NrBancos'] = int(match_total.group(1))
                values = match_total.group(2).split()

                current_record['Tipo 1'] = values[0]
                current_record['Tipo 2'] = values[1]
                current_record['Tipo 3'] = values[2]
                current_record['Tipo 4'] = values[3]
                current_record['Tipo 5'] = values[4]
                current_record['Tipo 6'] = values[5]
                current_record['Total'] = values[6]

        if current_record:
            data.append(current_record)

        df = pd.DataFrame(data)

        dynamic_filename = f"BM CRC {reference_date} Referência_{reference_code}.xlsx"
        output_file = os.path.join(output_path, dynamic_filename)

        df.to_excel(output_file, index=False, sheet_name='Dados')

        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        progress_label.config(text=f"Concluído em {minutes}m {seconds}s")
        messagebox.showinfo("Concluído", f"Ficheiro gerado com sucesso:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))


def start_processing():
    txt_file = filedialog.askopenfilename(filetypes=[("Ficheiros TXT", "*.txt")])
    if not txt_file:
        return

    output_path = filedialog.askdirectory()
    if not output_path:
        return

    progress_label.config(text="Iniciando processamento...")
    progress_bar['value'] = 0

    thread = threading.Thread(target=process_txt_to_excel, args=(txt_file, output_path, progress_label, progress_bar))
    thread.start()


# Obter nome do utilizador
user_name = getpass.getuser()

# Interface Tkinter
window = tk.Tk()
window.title("Conversor CRBM")
window.geometry("500x320")
window.resizable(False, False)
window.configure(bg=BG_COLOR)

# Definir ícone (coloque o ficheiro logo.ico na mesma pasta ou forneça o caminho completo)
try:
    window.iconbitmap("logo.ico")
except Exception as e:
    print(f"[Aviso] Ícone não carregado: {e}")

# Frame principal
frame = tk.Frame(window, bg=BG_COLOR, padx=20, pady=20)
frame.pack(fill='both', expand=True)

# Título e utilizador
title_label = tk.Label(
    frame,
    text=f"Conversor de Ficheiro CRC (.txt) para Excel",
    font=HEADER_FONT,
    fg=PRIMARY_COLOR,
    bg=BG_COLOR
)
title_label.pack(pady=(0, 5))

user_label = tk.Label(
    frame,
    text=f"Utilizador: {user_name}",
    font=("Segoe UI", 9, "italic"),
    fg="#666666",
    bg=BG_COLOR
)
user_label.pack(pady=(0, 15))

# Botão de Seleção
btn_select = tk.Button(
    frame,
    text="Selecionar ficheiro .txt e pasta de destino",
    font=FONT,
    bg=BTN_COLOR,
    fg="white",
    relief="flat",
    padx=10,
    pady=5,
    command=start_processing
)
btn_select.pack(pady=(0, 20))

# Barra de Progresso
progress_bar = ttk.Progressbar(frame, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(pady=(0, 5))

# Texto de Progresso
progress_label = tk.Label(frame, text="Aguardando seleção...", font=FONT, bg=BG_COLOR, fg=TEXT_COLOR)
progress_label.pack()

# Estilo do ttk
style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", troughcolor='#d9d9d9', bordercolor='#f0f0f0', background=PRIMARY_COLOR, lightcolor=PRIMARY_COLOR, darkcolor=PRIMARY_COLOR)

# Iniciar janela
window.mainloop()
