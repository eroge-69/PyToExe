import tkinter as tk
import time
import threading
import sys

# Função para formatar tempo em hh:mm:ss
def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

class Timer:
    def __init__(self, root, name, duration, loop=False, with_checkbox=False, bg_color=None):
        self.name = name
        self.duration = duration
        self.loop = loop
        self.remaining = duration
        self.running = False

        # Criar frame para organizar (grid para alinhar tudo)
        frame = tk.Frame(root, bd=1, relief="solid", bg=bg_color)
        frame.pack(anchor="w", padx=5, pady=1, fill="x")

        self.label = tk.Label(frame, text=f"{self.name}: {format_time(self.remaining)}", font=("Arial", 12), width=20, anchor="w", bg=bg_color)
        self.label.grid(row=0, column=0, padx=5, pady=2)

        self.start_btn = tk.Button(frame, text="▶", command=self.start, width=3)
        self.start_btn.grid(row=0, column=1, padx=2)

        self.pause_btn = tk.Button(frame, text="⏸", command=self.pause, width=3)
        self.pause_btn.grid(row=0, column=2, padx=2)

        self.reset_btn = tk.Button(frame, text="⟳", command=self.reset, width=3)
        self.reset_btn.grid(row=0, column=3, padx=2)

        if with_checkbox:
            self.var = tk.BooleanVar()
            self.checkbox = tk.Checkbutton(frame, variable=self.var, bg=bg_color)
            self.checkbox.grid(row=0, column=4, padx=5)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run, daemon=True).start()

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False
        self.remaining = self.duration
        self.label.config(text=f"{self.name}: {format_time(self.remaining)}")

    def run(self):
        while self.running:
            if self.remaining >= 0:
                self.label.config(text=f"{self.name}: {format_time(self.remaining)}")
                time.sleep(1)
                self.remaining -= 1
            else:
                if self.loop:
                    # Se for o temporizador "Ice" de 17s, faz beep
                    if self.name == "Ice":
                        sys.stdout.write('\a')  # beep do sistema
                        sys.stdout.flush()
                    self.remaining = self.duration
                else:
                    self.running = False

# Criar janela principal
root = tk.Tk()
root.title("xL0g1c")

# Definir cores para grupos
group_colors = {
    "Bosses": "#ffcccc",  # vermelho claro
    "Hidras": "#cce5ff",  # azul claro
    "Loop": "#ccffcc",    # verde claro
}

# Agrupamentos para criar divisores visuais
groups = {
    "Bosses": [
        ("Balathor", 3*3600, False, True),
        ("Meley W", 3*3600, False, True),
        ("Meley Z", 3*3600, False, True),
        ("Meley V", 3*3600, False, True),
        ("Meley Y", 3*3600, False, True),
    ],
    "Hidras": [
        ("Hidra 1", 20*60, False, False),
        ("Hidra 2", 20*60, False, False),
    ],
    "Loop": [
        ("Simples", 3600, True, False),
        ("Dupla", 7200, True, False),
        ("Ice", 17, True, False),
    ]
}

# Criar instâncias dos temporizadores organizados em grupos
for group_name, timers_config in groups.items():
    tk.Label(root, text=group_name, font=("Arial", 13, "bold"), anchor="w", bg=group_colors[group_name]).pack(fill="x", padx=5, pady=(8, 2))
    for name, duration, loop, checkbox in timers_config:
        Timer(root, name, duration, loop, checkbox, bg_color=group_colors[group_name])

# Loop da interface gráfica
root.mainloop()
