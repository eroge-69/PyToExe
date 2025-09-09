import tkinter as tk
from tkinter import messagebox
import cv2
import os
import time

# --- Funções do App ---

def tirar_foto():
    """Captura uma foto da webcam e salva na pasta fotos/."""
    try:
        # Tenta acessar a webcam
        cam = cv2.VideoCapture(0)  # 0 é o ID da webcam padrão
        if not cam.isOpened():
            messagebox.showerror("Erro", "Não foi possível acessar a webcam.")
            return

        ret, frame = cam.read()  # Lê um frame da webcam
        cam.release()  # Libera a webcam

        if ret:
            # Garante que a pasta 'fotos' exista
            if not os.path.exists("fotos"):
                os.makedirs("fotos")

            # Cria um nome de arquivo único com data e hora (incluindo milissegundos)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            milliseconds = int(time.time() * 1000) % 1000
            nome_arquivo = f"fotos/foto_{timestamp}_{milliseconds:03d}.png"

            # Salva a imagem no arquivo
            cv2.imwrite(nome_arquivo, frame)
            messagebox.showinfo("Sucesso", f"Foto salva em '{nome_arquivo}'")
        else:
            messagebox.showerror("Erro", "Falha ao capturar a imagem da webcam.")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# --- Configuração da Interface (Tkinter) ---

# Cria a janela principal
janela = tk.Tk()
janela.title("ISCZN Photo")
janela.geometry("400x400")
janela.resizable(False, False)

# Adiciona um estilo mais "limpo" (opcional)
janela.configure(bg="#2c3e50")  # Cor de fundo escura

# Título do aplicativo
titulo_label = tk.Label(janela, text="ISCZN Photo", font=("Arial", 24, "bold"), fg="#ecf0f1", bg="#2c3e50")
titulo_label.pack(pady=20)

# Frame para o botão
frame_botao = tk.Frame(janela, bg="#2c3e50")
frame_botao.pack(pady=50)

# Imagem para o botão (bolinha)
# Você pode criar uma imagem de uma bolinha e usar aqui
try:
    # A maneira mais fácil de criar uma bolinha é com um canvas ou desenhando
    # Vamos criar um canvas para desenhar um círculo, simulando a bolinha
    canvas = tk.Canvas(frame_botao, width=150, height=150, bg="#2c3e50", highlightthickness=0)
    canvas.pack()

    # Desenha o círculo
    canvas.create_oval(10, 10, 140, 140, fill="#e74c3c", outline="#c0392b", width=5)

    # Adiciona a funcionalidade de clique apenas no círculo
    def ao_clicar_no_canvas(event):
        # Verifica se o clique foi dentro do círculo
        x, y = event.x, event.y
        center_x, center_y = 75, 75  # Centro do círculo
        radius = 65  # Raio do círculo
        distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        
        if distance <= radius:
            tirar_foto()

    canvas.bind("<Button-1>", ao_clicar_no_canvas)

except Exception as e:
    messagebox.showerror("Erro", f"Não foi possível criar o botão: {e}")

# Mensagem de rodapé
rodape_label = tk.Label(janela, text="Clique na bolinha para tirar uma foto.", font=("Arial", 12), fg="#bdc3c7", bg="#2c3e50")
rodape_label.pack(side="bottom", pady=10)

# Inicia o loop principal do Tkinter
janela.mainloop()