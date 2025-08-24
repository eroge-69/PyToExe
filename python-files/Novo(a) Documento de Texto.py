import subprocess
import tkinter as tk
from tkinter import messagebox

def listar_teclados():
    output = subprocess.check_output("wmic path Win32_Keyboard get Name,DeviceID", shell=True, text=True)
    linhas = output.strip().split("\n")[1:]
    dispositivos = [linha.strip() for linha in linhas if linha.strip()]
    return dispositivos

def desativar_teclado(device_id):
    try:
        comando = f'devcon disable "{device_id}"'
        subprocess.run(comando, shell=True, check=True)
        messagebox.showinfo("Sucesso", f"Teclado '{device_id}' desativado com sucesso.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Erro", f"Falha ao desativar '{device_id}'. Você pode precisar de permissões administrativas.")

def on_selecionar():
    selecao = lista.curselection()
    if selecao:
        item = lista.get(selecao)
        device_id = item.split()[0]
        desativar_teclado(device_id)

# Interface gráfica
janela = tk.Tk()
janela.title("Desativar Teclado")

lista = tk.Listbox(janela, width=80)
lista.pack(padx=10, pady=10)

teclados = listar_teclados()
for t in teclados:
    lista.insert(tk.END, t)

botao = tk.Button(janela, text="Desativar Selecionado", command=on_selecionar)
botao.pack(pad
