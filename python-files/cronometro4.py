import tkinter as tk
from tkinter import messagebox, ttk
import time

# Serviços e valores por hora
servicos = {
    "Serviços Gráficos e Personal Tec (R$ 50,00/h)": 50.00,
    "Configuração simples de celular (vírus) (R$ 30,00/h)": 30.00,
    "Atendente Júnior (R$ 30,00/h)": 30.00
}

# Variáveis de controle
tempo_inicial = 0
tempo_total = 0
rodando = False
valor_por_segundo = 0.0
servico_atual = None

def selecionar_servico(event=None):
    global valor_por_segundo, servico_atual
    servico_atual = combo_servicos.get()
    valor_hora = servicos[servico_atual]
    valor_por_segundo = valor_hora / 3600
    label_valor_info.config(text=f"Serviço selecionado: {servico_atual}")

def iniciar():
    global tempo_inicial, rodando
    if servico_atual is None:
        messagebox.showwarning("Aviso", "Selecione um serviço antes de iniciar!")
        return
    if not rodando:
        tempo_inicial = time.time() - tempo_total
        rodando = True
        atualizar_tempo()

def pausar():
    global tempo_total, rodando
    if rodando:
        tempo_total = time.time() - tempo_inicial
        rodando = False

def zerar():
    global tempo_inicial, tempo_total, rodando
    tempo_inicial = 0
    tempo_total = 0
    rodando = False
    label_tempo.config(text="0.00 s")
    label_valor.config(text="R$ 0.00")

def salvar():
    if servico_atual is None:
        messagebox.showwarning("Aviso", "Selecione um serviço antes de salvar!")
        return
    valor = tempo_total * valor_por_segundo
    with open("registro_servicos.txt", "a", encoding="utf-8") as f:
        f.write(f"Serviço: {servico_atual} | Tempo: {tempo_total:.2f} s | Valor: R$ {valor:.2f}\n")
    messagebox.showinfo("Salvo", "Registro salvo em 'registro_servicos.txt'.")

def atualizar_tempo():
    global tempo_total
    if rodando:
        tempo_total = time.time() - tempo_inicial
        label_tempo.config(text=f"{tempo_total:.2f} s")
        valor = tempo_total * valor_por_segundo
        label_valor.config(text=f"R$ {valor:.2f}")
        janela.after(100, atualizar_tempo)

# Janela principal
janela = tk.Tk()
janela.title("Cronômetro de Serviços")
janela.geometry("400x300")

# Usar tema ttk para estilo Windows azul
style = ttk.Style(janela)
style.theme_use('vista')  # Tenta aplicar o tema Windows Vista/7

# Seleção de serviço
ttk.Label(janela, text="Selecione o serviço:").pack(pady=5)
combo_servicos = ttk.Combobox(janela, values=list(servicos.keys()), state="readonly")
combo_servicos.pack()
combo_servicos.bind("<<ComboboxSelected>>", selecionar_servico)

label_valor_info = ttk.Label(janela, text="Nenhum serviço selecionado")
label_valor_info.pack(pady=5)

# Labels
label_tempo = ttk.Label(janela, text="0.00 s", font=("Arial", 20))
label_tempo.pack(pady=5)

label_valor = ttk.Label(janela, text="R$ 0.00", font=("Arial", 16))
label_valor.pack(pady=5)

# Botões de controle
frame_botoes = ttk.Frame(janela)
frame_botoes.pack(pady=10)

btn_play = ttk.Button(frame_botoes, text="▶ Play", command=iniciar)
btn_play.grid(row=0, column=0, padx=5)

btn_pause = ttk.Button(frame_botoes, text="⏸ Pausar", command=pausar)
btn_pause.grid(row=0, column=1, padx=5)

btn_reset = ttk.Button(frame_botoes, text="⏹ Zerar", command=zerar)
btn_reset.grid(row=0, column=2, padx=5)

btn_salvar = ttk.Button(janela, text="💾 Salvar registro", command=salvar)
btn_salvar.pack(pady=5)

janela.mainloop()
