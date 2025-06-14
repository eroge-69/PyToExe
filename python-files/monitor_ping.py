import tkinter as tk
from ping3 import ping
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import csv
import os
import webbrowser # Importa a biblioteca para abrir links no navegador

# --- Configurações ---
CSV_FILE = "./log_ping.csv"
PING_TARGET = "8.8.8.8" # Endereço IP para o ping (DNS do Google)
MAX_GRAPH_POINTS = 60 # Número máximo de pontos no gráfico
UPDATE_INTERVAL_SEC = 1 # Intervalo de atualização do ping em segundos

# --- Dados das Redes Sociais ---
WHATSAPP_NUMBER = "21979317341"
GITHUB_USERNAME = "claudio-asj"
LINKEDIN_USERNAME = "claudioasjr"

# --- Cores da Interface ---
BG_COLOR = "#2c3e50" # Azul escuro principal (dark slate blue)
PRIMARY_COLOR = "#34495e" # Azul escuro secundário (wet asphalt)
TEXT_COLOR = "#ecf0f1" # Branco acinzentado
ACCENT_COLOR = "#2ecc71" # Verde esmeralda (para o gráfico e botões)
GRAPH_LINE_COLOR = "#3498db" # Azul claro (peter river)
GRAPH_BG_COLOR = "#34495e" # Mesma cor do PRIMARY_COLOR para o fundo do plot

# Cria o arquivo CSV com cabeçalho se não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Horário", "Ping (ms)"])

# Listas para plotagem
ping_list = []
time_list = []

# --- Funções de Rede Social ---
def open_whatsapp():
    webbrowser.open_new_tab(f"https://wa.me/{WHATSAPP_NUMBER}")

def open_github():
    webbrowser.open_new_tab(f"https://github.com/{GITHUB_USERNAME}")

def open_linkedin():
    webbrowser.open_new_tab(f"https://www.linkedin.com/in/{LINKEDIN_USERNAME}")

# --- Função que mede o ping e salva ---
def medir_ping():
    while True:
        resultado = ping(PING_TARGET, unit='ms')
        ms = round(resultado, 2) if resultado else None
        hora = datetime.now().strftime("%H:%M:%S")

        if ms is not None: # Verifica se o ping foi bem-sucedido
            ping_list.append(ms)
            time_list.append(hora)

            # Salva no CSV
            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([hora, ms])

            # Atualiza o label do último ping
            last_ping_label.config(text=f"Último Ping: {ms} ms", fg=TEXT_COLOR)
        else:
            last_ping_label.config(text="Último Ping: Sem resposta", fg="#e74c3c") # Vermelho para erro

        # Limita o número de pontos no gráfico
        if len(ping_list) > MAX_GRAPH_POINTS:
            ping_list.pop(0)
            time_list.pop(0)

        atualizar_grafico()
        time.sleep(UPDATE_INTERVAL_SEC)

# --- Atualiza o gráfico ---
def atualizar_grafico():
    ax.clear()
    ax.plot(time_list, ping_list, color=GRAPH_LINE_COLOR, marker='o', markersize=4)
    ax.set_ylabel("Ping (ms)", color=TEXT_COLOR)
    ax.set_xlabel("Horário", color=TEXT_COLOR)
    ax.set_title("Ping em Tempo Real", color=TEXT_COLOR)
    
    # Ajusta os ticks do eixo X para não ficarem sobrepostos
    if len(time_list) > 10: # Só rotaciona se houver muitos pontos
        ax.set_xticks(time_list[::len(time_list)//10]) # Exibe apenas alguns rótulos para clareza
        ax.set_xticklabels(time_list[::len(time_list)//10], rotation=45, ha='right', fontsize=8)
    else:
        ax.set_xticklabels(time_list, rotation=45, ha='right', fontsize=8)

    ax.set_facecolor(GRAPH_BG_COLOR) # Fundo do plot
    fig.patch.set_facecolor(PRIMARY_COLOR) # Fundo da figura (ao redor do plot)

    # Cores dos ticks e bordas
    ax.tick_params(axis='x', colors=TEXT_COLOR)
    ax.tick_params(axis='y', colors=TEXT_COLOR)
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['top'].set_color(TEXT_COLOR)
    ax.spines['left'].set_color(TEXT_COLOR)
    ax.spines['right'].set_color(TEXT_COLOR)
    
    plt.tight_layout() # Ajusta o layout para evitar cortes
    canvas.draw()

# --- Criação da interface Tkinter ---
root = tk.Tk()
root.title("Monitor de Internet por Cláudio ASJR")
root.geometry("1000x650") # Define um tamanho inicial para a janela
root.configure(bg=BG_COLOR)

# --- Frame para o Gráfico ---
graph_frame = tk.Frame(root, bg=PRIMARY_COLOR, bd=2, relief="groove")
graph_frame.pack(pady=10, padx=10, fill="both", expand=True)

fig, ax = plt.subplots(figsize=(10, 4))
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)

# --- Label para o último Ping ---
last_ping_label = tk.Label(root, text="Aguardando ping...", fg=TEXT_COLOR, bg=BG_COLOR, font=("Arial", 14, "bold"))
last_ping_label.pack(pady=(0, 10))

# --- Frame para os botões de Rede Social ---
social_frame = tk.Frame(root, bg=BG_COLOR)
social_frame.pack(pady=10)

# Botão WhatsApp
whatsapp_btn = tk.Button(social_frame, text="WhatsApp", command=open_whatsapp,
                         bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold"), relief="raised", bd=3)
whatsapp_btn.pack(side=tk.LEFT, padx=10, pady=5)

# Botão GitHub
github_btn = tk.Button(social_frame, text="GitHub", command=open_github,
                       bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold"), relief="raised", bd=3)
github_btn.pack(side=tk.LEFT, padx=10, pady=5)

# Botão LinkedIn
linkedin_btn = tk.Button(social_frame, text="LinkedIn", command=open_linkedin,
                        bg=ACCENT_COLOR, fg=TEXT_COLOR, font=("Arial", 10, "bold"), relief="raised", bd=3)
linkedin_btn.pack(side=tk.LEFT, padx=10, pady=5)

# --- Roda a thread de medição ---
thread = threading.Thread(target=medir_ping, daemon=True)
thread.start()

# Inicia a interface
root.mainloop()