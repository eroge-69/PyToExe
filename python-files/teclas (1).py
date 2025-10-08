import tkinter as tk
from tkinter import messagebox

# Mapeamento das teclas
key_map = {
    'a': 'A',
    's': 'B',
    'd': 'C',
    'f': 'D',
    'e': 'E'
}

def on_key(event):
    char = event.char.lower()
    if event.keysym == "Return":  # trata Enter
        text_box.insert(tk.END, "\n")
        return "break"
    elif char in key_map:
        text_box.insert(tk.END, key_map[char] + ";")
        return "break"
    elif char.isprintable():
        text_box.insert(tk.END, char + ";")
        return "break"
    # para teclas como Shift, Ctrl etc., não faz nada
    return

def insert_letter(letter):
    text_box.insert(tk.END, letter + ";")

def copy_text():
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", tk.END))
    messagebox.showinfo("Copiado", "Texto copiado para a área de transferência!")

# Criando a janela principal
root = tk.Tk()
root.title("Teclado Personalizado")

# Campo de texto
text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)
text_box.bind("<Key>", on_key)

# Botões A, B, C, D
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

buttons = ['A', 'B', 'C', 'D']
for letter in buttons:
    b = tk.Button(button_frame, text=letter, width=5, command=lambda l=letter: insert_letter(l))
    b.pack(side=tk.LEFT, padx=5)

# Botão de copiar
copy_button = tk.Button(root, text="Copiar", command=copy_text)
copy_button.pack(pady=5)

root.mainloop()
