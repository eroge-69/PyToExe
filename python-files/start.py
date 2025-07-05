from tkinter import messagebox
import tkinter as tk
import random
import turtle

WIDTH, HEIGHT = 1280, 720
cor_inicio = "#FFB6C1"
cor_fim = "#FF69B4"
janela = None
canvas = None
gradient_colors = {}

# ===== FUNÇÕES DE GLOBAIS =====
def criar_janela():
    global janela, canvas
    janela = tk.Tk()
    janela.geometry(f"{WIDTH}x{HEIGHT}")
    janela.resizable(False, False)
    janela.title("Desafio Especial")

    canvas = tk.Canvas(janela, width=WIDTH, height=HEIGHT)
    canvas.pack()
    criar_gradiente()
    return janela

def criar_gradiente():
    global gradient_colors
    canvas.create_rectangle(0, 0, WIDTH, (HEIGHT/2), fill=cor_inicio, width=0)
    metade = HEIGHT/2
    for i in range(int(metade), HEIGHT):
        # Cálculo da interpolação de cores
        progresso = (i - metade) / metade
        
        # Componentes RGB da cor inicial
        r_inicio = int(cor_inicio[1:3], 16)
        g_inicio = int(cor_inicio[3:5], 16)
        b_inicio = int(cor_inicio[5:7], 16)
        
        # Componentes RGB da cor final
        r_fim = int(cor_fim[1:3], 16)
        g_fim = int(cor_fim[3:5], 16)
        b_fim = int(cor_fim[5:7], 16)
        
        # Interpolação linear
        r = int((1 - progresso) * r_inicio + progresso * r_fim)
        g = int((1 - progresso) * g_inicio + progresso * g_fim)
        b = int((1 - progresso) * b_inicio + progresso * b_fim)
        
        cor = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, WIDTH, i, fill=cor)
        gradient_colors[i] = cor

def get_bg_color(y):
    """Obtém a cor de fundo na posição vertical y"""
    if y < HEIGHT/2:
        return cor_inicio
    return gradient_colors.get(int(y), cor_fim)

def limpar_tela():
    for widget in janela.winfo_children():
        if widget != canvas:
            widget.destroy()

def mover_botao(botao):
    x = random.randint(int(0.65-100), int(0.65+100))
    y = random.randint(int(0.6-100), int(0.6+100))

    botao.place(x=x, y=y)
    bg_color = get_bg_color(y + 15)  # 15 = metade da altura do botão
    botao.config(bg=bg_color)

def mostrar_coracao():
    janela.destroy()
    messagebox.showinfo("DESAFIO CONCLUÍDO", "WOOOW 20 ANOSSSSSSSSSSSSSSSSSSSS")
    
    pen = turtle.Turtle()
    def curve():
        for _ in range(200):
            pen.right(1)
            pen.forward(1)
    
    def heart():
        pen.fillcolor('red')
        pen.begin_fill()
        pen.left(140)
        pen.forward(113)
        curve()
        pen.left(120)
        curve()
        pen.forward(112)
        pen.end_fill()
    
    def txt():
        pen.up()
        pen.setpos(-68, 95)
        pen.down()
        pen.color('white')
        pen.write("senha:\nhappy20birthday1707", font=("Verdana", 8, "bold"))
    
    window = turtle.Screen()
    window.bgcolor("white")
    pen.color('red')
    pen.begin_fill()
    heart()
    pen.end_fill()
    txt()
    pen.ht()
    turtle.done()

# ===== FUNÇÕES DE PERGUNTAS =====
def pergunta_1():
    limpar_tela()
    
    bg_color = get_bg_color(HEIGHT * 0.4)
    
    rotulo = tk.Label(
        janela, 
        text="Você está pronta para o desafio!!?", 
        font=("Arial", 16, "bold"), 
        fg="white", 
        bg=bg_color,
        bd=0,
        highlightthickness=0
    )
    rotulo.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    
    btn_bg_color = get_bg_color(HEIGHT * 0.6)
    
    botao_sim = tk.Button(
        janela,
        text="Sim",
        font=("Arial", 12, "bold"),
        bg=btn_bg_color,
        fg="white",
        command=pergunta_2
    )
    botao_sim.place(relx=0.35, rely=0.6, anchor=tk.CENTER)
    
    botao_nao = tk.Button(
        janela,
        text="Não",
        font=("Arial", 12, "bold"),
        bg=btn_bg_color,
        fg="white"
    )

    botao_nao.place(relx=0.65, rely=0.6, anchor=tk.CENTER)
    botao_nao.config(command=lambda: mover_botao(botao_nao))

def pergunta_2():
    limpar_tela()
    
    bg_color = get_bg_color(HEIGHT * 0.4)
    
    rotulo = tk.Label(
        janela, 
        text="Qual o seu nome?", 
        font=("Arial", 16, "bold"), 
        fg="white", 
        bg=bg_color,
        bd=0,
        highlightthickness=0
    )
    rotulo.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    
    mensagem_erro = tk.Label(
        janela,
        text="",
        font=("Arial", 10),
        fg="yellow",
        bg=bg_color,
        bd=0,
        highlightthickness=0
    )
    mensagem_erro.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    btn_bg_color = get_bg_color(HEIGHT * 0.6)
    
    def resposta_errada(botao):
        botao.destroy()
        mensagem_erro.config(text="Música boa demais: Marvada Pinga (Zenaide) - Marco e Mario")
        janela.after(2000, lambda: mensagem_erro.config(text=""))
    
    botao_opcao1 = tk.Button(
        janela,
        text="Zenáide",
        font=("Arial", 12, "bold"),
        bg=btn_bg_color,
        fg="white"
    )
    botao_opcao1.place(relx=0.35, rely=0.6, anchor=tk.CENTER)
    botao_opcao1.config(command=lambda: resposta_errada(botao_opcao1))
    
    botao_opcao2 = tk.Button(
        janela,
        text="Amanda",
        font=("Arial", 12, "bold"),
        bg=btn_bg_color,
        fg="white",
        command=pergunta_3
    )
    botao_opcao2.place(relx=0.65, rely=0.6, anchor=tk.CENTER)

def pergunta_3():
    limpar_tela()
    
    bg_color = get_bg_color(HEIGHT * 0.3)
    
    rotulo = tk.Label(
        janela,
        text="Qual a sua banda favorita?",
        font=("Arial", 16, "bold"),
        fg="white",
        bg=bg_color,
        bd=0,
        highlightthickness=0
    )
    rotulo.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
    
    entrada_resposta = tk.Entry(
        janela,
        font=("Arial", 14),
        justify="center",
        bd=1,
        relief="flat",
        bg="white",
        highlightthickness=0
    )
    entrada_resposta.place(relx=0.5, rely=0.45, anchor=tk.CENTER, width=200, height=40)
    entrada_resposta.focus_set()
    
    msg_bg_color = get_bg_color(HEIGHT * 0.55)
    
    mensagem_erro = tk.Label(
        janela,
        text="",
        font=("Arial", 10),
        fg="yellow",
        bg=msg_bg_color,
        bd=0,
        highlightthickness=0
    )
    mensagem_erro.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
    
    def verificar_resposta():
        resposta = entrada_resposta.get().strip().lower()
        resposta_correta = "twenty one pilots"
        
        if resposta == resposta_correta:
            pergunta_4()
        else:
            mensagem_erro.config(text="Resposta incorreta! Tente novamente.")
            entrada_resposta.config(bg="#FFCCCC")
            janela.after(300, lambda: entrada_resposta.config(bg="white"))
    
    btn_bg_color = get_bg_color(HEIGHT * 0.65)
    
    botao_enviar = tk.Button(
        janela,
        text="Enviar Resposta",
        font=("Arial", 12, "bold"),
        bg=btn_bg_color,
        fg="white",
        command=verificar_resposta
    )
    botao_enviar.place(relx=0.5, rely=0.65, anchor=tk.CENTER)
    
    entrada_resposta.bind("<Return>", lambda event: verificar_resposta())

def pergunta_4():
    limpar_tela()
    
    bg_color = get_bg_color(HEIGHT * 0.15)
    
    rotulo = tk.Label(
        janela, 
        text="Quantos irmãos você tem?", 
        font=("Arial", 16, "bold"), 
        fg="white", 
        bg=bg_color,
        bd=0,
        highlightthickness=0
    )
    rotulo.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
    
    display_var = tk.StringVar()
    display_var.set("")
    
    display = tk.Label(
        janela,
        textvariable=display_var,
        font=("Arial", 24, "bold"),
        fg="black",
        bg="white",
        width=10,
        relief="flat",
        bd=1,
        highlightthickness=0
    )
    display.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
    
    keyboard_bg_color = get_bg_color(HEIGHT * 0.65)
    
    frame_teclado = tk.Frame(janela, bg=keyboard_bg_color, highlightthickness=0)
    frame_teclado.place(relx=0.5, rely=0.65, anchor=tk.CENTER)
    
    def adicionar_numero(numero):
        atual = display_var.get()
        if len(atual) < 2:  # Limitar a 2 dígitos
            novo = atual + str(numero)
            display_var.set(novo)
    
    def apagar():
        atual = display_var.get()
        display_var.set(atual[:-1])
    
    def confirmar():
        resposta = display_var.get()
        if resposta == "2" or resposta == "02":
            mostrar_coracao()
        else:
            messagebox.showerror("Erro", "Resposta incorreta! Tente novamente.")
            display_var.set("")
    
    teclas = [
        ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
        ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
        ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
        ('0', 3, 1), ('⌫', 3, 0), ('✔', 3, 2)
    ]
    
    for (texto, linha, coluna) in teclas:
        if texto == '⌫':
            comando = apagar
            cor = "#FF6347"  # Vermelho
        elif texto == '✔':
            comando = confirmar
            cor = "#32CD32"  # Verde
        else:
            comando = lambda x=texto: adicionar_numero(x)
            cor = keyboard_bg_color
        
        botao = tk.Button(
            frame_teclado,
            text=texto,
            font=("Arial", 14, "bold"),
            bg=cor,
            fg="white",
            width=4,
            height=2,
            bd=0,
            highlightthickness=0,
            activebackground=cor,
            command=comando
        )
        botao.grid(row=linha, column=coluna, padx=5, pady=5)

# ===== INICIALIZAÇÃO =====
if __name__ == "__main__":
    janela = criar_janela()
    pergunta_1()
    janela.mainloop()
