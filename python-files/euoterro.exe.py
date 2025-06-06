import tkinter as tk
from tkinter import messagebox
import os
import sys

def reiniciar_pc():
    """Função para simular o reinício do PC."""
    resposta = messagebox.askyesno("Atenção!", "Você tem certeza que quer reiniciar o PC? (Isso é uma simulação, não vai reiniciar de verdade!)")
    if resposta:
        messagebox.showinfo("Reiniciando...", "Ok, o PC seria reiniciado agora! (Simulação)")
        # A linha abaixo reiniciaria o PC de verdade. Está comentada por segurança.
        # if sys.platform == "win32":
        #     os.system("shutdown /r /t 1") # Windows
        # else:
        #     os.system("sudo reboot") # Linux/macOS (requer senha e permissões)
        sys.exit() # Sai do aplicativo Python
    else:
        messagebox.showinfo("Cancelado", "Ufa! Que bom que você pensou melhor!")

def acao_sim():
    """Função para o botão 'Sim'."""
    messagebox.showinfo("Resposta", "Que legal! Sabia que o Subs é demais!")
    root.destroy() # Fecha a janela após a resposta

def acao_nao():
    """Função para o botão 'Não'."""
    messagebox.showinfo("Ops!", "Poxa, que pena! Mas tudo bem, nem todo mundo pode ter bom gosto! 😉")
    reiniciar_pc()

# Configuração da janela principal
root = tk.Tk()
root.title("Pesquisa Subs")
root.geometry("400x200") # Tamanho da janela
root.resizable(False, False) # Impede que a janela seja redimensionada

# Estilo da interface (opcional, mas deixa mais bonito!)
root.configure(bg="#2c3e50") # Cor de fundo da janela
label_font = ("Helvetica", 18, "bold")
button_font = ("Arial", 12)

# Pergunta
label = tk.Label(root, text="Você gosta do Subs?", font=label_font, fg="#ecf0f1", bg="#2c3e50")
label.pack(pady=30)

# Botões
frame_botoes = tk.Frame(root, bg="#2c3e50")
frame_botoes.pack()

botao_sim = tk.Button(frame_botoes, text="Sim", command=acao_sim, font=button_font, bg="#27ae60", fg="white", padx=20, pady=10, relief=tk.RAISED, bd=3)
botao_sim.pack(side=tk.LEFT, padx=10)

botao_nao = tk.Button(frame_botoes, text="Não", command=acao_nao, font=button_font, bg="#e74c3c", fg="white", padx=20, pady=10, relief=tk.RAISED, bd=3)
botao_nao.pack(side=tk.RIGHT, padx=10)

# Inicia o loop principal da interface
root.mainloop()