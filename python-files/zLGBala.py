import tkinter as tk
import winsound  # para o beep no Windows

class Cronometro:
    def __init__(self, master, titulo, tempo_inicial, loop=False, com_regist=False, beep_aviso=False, beep_tipo=None):
        self.master = master
        self.titulo = titulo
        self.tempo_inicial = tempo_inicial
        self.tempo_restante = tempo_inicial
        self.loop = loop
        self.beep_aviso = beep_aviso
        self.beep_tipo = beep_tipo  # tipo de beep (None, "gelo", "bafo")
        self.ativo = False
        self.job = None

        # Frame vertical para cada cronómetro
        self.frame = tk.Frame(master, padx=10, pady=5)
        self.frame.pack(side="left", fill="y", expand=True)

        # Label de título
        self.label_titulo = tk.Label(self.frame, text=titulo, font=("Arial", 11, "bold"))
        self.label_titulo.pack(pady=(0,5))

        # Label do tempo
        self.label_tempo = tk.Label(self.frame, text=self.formatar_tempo(), font=("Arial", 14))
        self.label_tempo.pack(pady=(0,5))

        # Botões
        botoes = tk.Frame(self.frame)
        botoes.pack()
        self.botao_start = tk.Button(botoes, text="START", width=8, command=self.start)
        self.botao_start.pack(side="left", padx=2)
        self.botao_reset = tk.Button(botoes, text="REFRESH", width=8, command=self.reset)
        self.botao_reset.pack(side="left", padx=2)

        # CheckBox opcional (só para cronómetro 4)
        if com_regist:
            self.regist_var = tk.BooleanVar()
            self.check_regist = tk.Checkbutton(self.frame, text="Regist", variable=self.regist_var)
            self.check_regist.pack(pady=5)

    def formatar_tempo(self):
        horas = self.tempo_restante // 3600
        minutos = (self.tempo_restante % 3600) // 60
        segundos = self.tempo_restante % 60
        if self.tempo_inicial >= 3600:
            return f"{horas:02}:{minutos:02}:{segundos:02}"
        else:
            return f"{minutos:02}:{segundos:02}"

    def atualizar_label(self):
        self.label_tempo.config(text=self.formatar_tempo())

    def tocar_beep(self):
        if self.beep_tipo == "gelo":
            winsound.Beep(1000, 300)  # agudo e curto
        elif self.beep_tipo == "bafo":
            winsound.Beep(600, 500)   # mais grave e longo

    def tick(self):
        if self.ativo and self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.atualizar_label()

            # Beep quando chega a 1 segundo
            if self.beep_aviso and self.tempo_restante == 1:
                self.tocar_beep()

            self.job = self.master.after(1000, self.tick)

        elif self.ativo and self.tempo_restante == 0:
            if self.loop:
                self.tempo_restante = self.tempo_inicial
                self.atualizar_label()
                self.job = self.master.after(1000, self.tick)
            else:
                self.ativo = False

    def start(self):
        if not self.ativo:
            self.ativo = True
            self.tick()

    def reset(self):
        if self.job:
            self.master.after_cancel(self.job)
            self.job = None
        self.ativo = self.loop  # se for loop, já volta a contar sozinho
        self.tempo_restante = self.tempo_inicial
        self.atualizar_label()
        if self.loop:
            self.tick()


# Interface principal
root = tk.Tk()
root.title("Balathor")
root.geometry("950x180")  # janela larga

# Criar cronómetros lado a lado
cron1 = Cronometro(root, "2.ª Fase", 600, loop=False)                    
cron2 = Cronometro(root, "Gelo", 18, loop=True, beep_aviso=True, beep_tipo="gelo")  
cron3 = Cronometro(root, "Bafo", 21, loop=True, beep_aviso=True, beep_tipo="bafo")  
cron4 = Cronometro(root, "Balathor", 10800, loop=False, com_regist=True)  

root.mainloop()
