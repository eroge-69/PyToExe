import tkinter as tk
import random
from tkinter import messagebox

class SunsetPostIt:
    def __init__(self, root):
        self.root = root
        self.root.title("Post-it com Tons de Pôr do Sol")
        self.root.geometry("300x150+100+100")
        self.root.configure(bg="#2c3e50")
        self.root.attributes("-alpha", 0.95)  # Transparência suave
        
        # Paleta de cores de pôr do sol
        self.sunset_colors = [
            "#FF6B6B", "#FF8E53", "#FFD166", "#06D6A0", "#118AB2", 
            "#EF476F", "#FFD166", "#073B4C", "#FF9E6D", "#FFAFCC"
        ]
        
        # Criar o primeiro post-it
        self.create_postit()
        
        # Botão para adicionar mais post-its
        self.add_btn = tk.Button(root, text="+ Novo Post-it", command=self.create_postit, 
                                bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                                relief="flat", cursor="hand2")
        self.add_btn.place(relx=0.5, rely=0.95, anchor="s")
        
        # Configurar para fechar todos os post-its quando a janela principal fechar
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def create_postit(self, text="", x=None, y=None):
        """Cria um novo post-it na tela"""
        # Posição aleatória se não for especificada
        if x is None:
            x = random.randint(50, tk.Tk().winfo_screenwidth() - 300)
        if y is None:
            y = random.randint(50, tk.Tk().winfo_screenheight() - 250)
        
        # Criar uma nova janela para o post-it
        postit = tk.Toplevel(self.root)
        postit.title("Post-it")
        postit.geometry(f"250x200+{x}+{y}")
        postit.overrideredirect(True)  # Remove a barra de título
        postit.attributes("-topmost", True)  # Sempre visível
        postit.attributes("-alpha", 0.95)  # Transparência suave
        
        # Escolher uma cor aleatória da paleta
        bg_color = random.choice(self.sunset_colors)
        postit.configure(bg=bg_color)
        
        # Botão de fechar
        close_btn = tk.Button(postit, text="✕", command=postit.destroy,
                             bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                             relief="flat", width=2, cursor="hand2")
        close_btn.place(x=220, y=5)
        
        # Botão para mudar cor
        color_btn = tk.Button(postit, text="☀️", command=lambda: self.change_color(postit),
                            bg="#f39c12", fg="white", font=("Arial", 10),
                            relief="flat", width=2, cursor="hand2")
        color_btn.place(x=5, y=5)
        
        # Área de texto
        text_area = tk.Text(postit, bg=bg_color, fg="#2c3e50", font=("Arial", 11),
                           relief="flat", padx=10, pady=10, wrap="word",
                           highlightthickness=0, selectbackground="#3498db")
        text_area.pack(fill="both", expand=True, padx=5, pady=25)
        text_area.insert("1.0", text)
        
        # Configurar arrastar com o mouse
        def start_drag(event):
            postit.x = event.x
            postit.y = event.y
        
        def do_drag(event):
            deltax = event.x - postit.x
            deltay = event.y - postit.y
            x = postit.winfo_x() + deltax
            y = postit.winfo_y() + deltay
            postit.geometry(f"+{x}+{y}")
        
        # Permitir arrastar clicando em qualquer lugar do post-it
        postit.bind("<ButtonPress-1>", start_drag)
        postit.bind("<B1-Motion>", do_drag)
        
        return postit
    
    def change_color(self, postit):
        """Muda a cor de fundo do post-it"""
        new_color = random.choice(self.sunset_colors)
        postit.configure(bg=new_color)
        # Atualiza a cor de fundo da área de texto
        for widget in postit.winfo_children():
            if isinstance(widget, tk.Text):
                widget.configure(bg=new_color)
    
    def confirm_exit(self):
        """Confirma se o usuário quer sair"""
        if messagebox.askyesno("Sair", "Deseja fechar todos os post-its?"):
            self.root.destroy()

# Criar a janela principal
if __name__ == "__main__":
    root = tk.Tk()
    app = SunsetPostIt(root)
    root.mainloop()