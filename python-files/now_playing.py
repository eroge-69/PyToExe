import tkinter as tk

def guardar_nome(event=None):
    nome_musica = entrada.get()
    with open("now_playing.txt", "w", encoding="utf-8") as ficheiro:
        ficheiro.write(nome_musica)
    entrada.delete(0, tk.END)  # Limpa o campo após guardar

# Criar a janela principal
janela = tk.Tk()
janela.title("Now Playing")
janela.geometry("400x120")  # Tamanho fixo da janela
janela.resizable(False, False)

# Campo de entrada
entrada = tk.Entry(janela, width=40, font=("Arial", 14))
entrada.pack(pady=10)
entrada.focus()  # Coloca o cursor diretamente no campo ao iniciar

# Botão para guardar
botao = tk.Button(janela, text="Guardar", command=guardar_nome, font=("Arial", 12))
botao.pack(pady=5)

# Associar tecla Enter ao botão
janela.bind("<Return>", guardar_nome)

# Iniciar aplicação
janela.mainloop()
