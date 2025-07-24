
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def launch_game():
    exe_path = exe_path_var.get()
    server_ip = server_ip_var.get()

    if not exe_path or not os.path.isfile(exe_path):
        messagebox.showerror("Erro", "Por favor selecione o executável do jogo.")
        return

    if not server_ip:
        messagebox.showerror("Erro", "Por favor insira o IP do servidor.")
        return

    # Define o App ID do Spacewar
    os.environ["SteamAppId"] = "480"

    # Executa o jogo com o IP como argumento
    try:
        subprocess.Popen([exe_path, server_ip])
        root.quit()
    except Exception as e:
        messagebox.showerror("Erro ao iniciar o jogo", str(e))

def browse_exe():
    file_path = filedialog.askopenfilename(filetypes=[("Executável", "*.exe")])
    exe_path_var.set(file_path)

# Interface gráfica
root = tk.Tk()
root.title("Launcher Zombie Army VR (LAN)")

tk.Label(root, text="Caminho do executável do jogo:").pack(pady=5)
exe_path_var = tk.StringVar()
tk.Entry(root, textvariable=exe_path_var, width=50).pack()
tk.Button(root, text="Procurar", command=browse_exe).pack(pady=5)

tk.Label(root, text="IP do servidor local (ex: 127.0.0.1):").pack(pady=5)
server_ip_var = tk.StringVar()
tk.Entry(root, textvariable=server_ip_var, width=30).pack()

tk.Button(root, text="Iniciar Jogo", command=launch_game).pack(pady=10)

root.mainloop()
