import tkinter as tk

def fechar(event=None):
    root.destroy()

root = tk.Tk()
root.title("Aviso")
root.attributes("-fullscreen", True)   # tela cheia
root.configure(bg="black")
root.overrideredirect(True)            # remove bordas e barra de título

# Cadeado e textos
tk.Label(root, text="🔒", font=("Segoe UI Emoji", 200), bg="black", fg="white").pack(pady=(80,10))
tk.Label(root, text="NÃO MEXA NO PC", font=("Arial", 36, "bold"), bg="black", fg="white").pack(pady=(0,5))
tk.Label(root, text="Caso mexa, a situação pode piorar.", font=("Arial", 20), bg="black", fg="white").pack(pady=(0,40))

# Fechar seguro (Esc ou duplo-clique)
root.bind("<Escape>", fechar)
root.bind("<Double-Button-1>", fechar)

root.mainloop()
