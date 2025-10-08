import tkinter as tk

def key_pressed(event):
    mapping = {'a': 'A', 's': 'B', 'd': 'C', 'f': 'D'}
    char = mapping.get(event.char.lower(), event.char)
    text.insert(tk.END, char + ';')  # Insere a letra mapeada seguida de ;
    return "break"  # Evita que a tecla original apareça

# Cria a janela principal
root = tk.Tk()
root.title("Teclado Personalizado")

# Área de texto
text = tk.Text(root, width=50, height=10)
text.pack()
text.focus_set()

# Captura todas as teclas
text.bind("<Key>", key_pressed)

root.mainloop()
