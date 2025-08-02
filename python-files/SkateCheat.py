import tkinter as tk
from tkinter import ttk

class SkateCheatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skate Cheat")
        self.root.configure(bg="black")
        self.root.geometry("1000x600")  # Tamanho inicial
        self.root.minsize(400, 300)     # Tamanho mínimo

        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", foreground='lime', background='black')
        style.configure("TScale", background='black')

        # Layout principal com padding
        self.main_frame = tk.Frame(root, bg="black", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # Título
        self.title_label = tk.Label(self.main_frame, text="== Skate Cheat ==", font=("Courier", 22), fg="lime", bg="black")

        self.title_label.pack(pady=20)

        # Equilíbrio
        self.balance_var = tk.DoubleVar()
        balance_label = tk.Label(self.main_frame, text="Equilíbrio", font=("Courier", 14), fg="white", bg="black")
        balance_label.pack()

        self.balance_scale = ttk.Scale(self.main_frame, from_=-100, to=100, orient='horizontal', variable=self.balance_var)
        self.balance_scale.pack(fill="x", padx=10, pady=10)

        # Área dos truques
        self.tricks_frame = tk.Frame(self.main_frame, bg="black")
        self.tricks_frame.pack(fill="both", expand=True)

        # Lista de truques
        self.tricks = {
            "Ollie": False,
            "Manual": False,
            "360": False,
            "Várias Body": False
        }

        for trick in self.tricks:
            self.add_trick_button(trick)

    def add_trick_button(self, trick_name):
        frame = tk.Frame(self.tricks_frame, bg="black")
        frame.pack(fill="x", padx=5, pady=5)

        label = tk.Label(frame, text=trick_name, font=("Courier", 12), fg="white", bg="black")
        label.pack(side="left", expand=True, anchor="w")

        btn = ttk.Button(frame, text="Ativar", command=lambda: self.toggle_trick(trick_name))
        btn.pack(side="right")

    def toggle_trick(self, trick_name):
        self.tricks[trick_name] = not self.tricks[trick_name]
        state = "ATIVADO" if self.tricks[trick_name] else "DESATIVADO"
        print(f"{trick_name}: {state}")

# Execução
if __name__ == "__main__":
    root = tk.Tk()
    app = SkateCheatApp(root)
    root.mainloop()
