import tkinter as tk

# Mapeamento: tecla pressionada -> caractere inserido
MAPPING = {
    'a': 'A',
    's': 'B',
    'd': 'C',
    'f': 'D',
}

def on_key(event):
    """
    Substitui A/S/D/F por A/B/C/D + ';'.
    Todas as outras teclas continuam funcionando normalmente (backspace, setas, Ctrl+C/V, etc.)
    """
    ch = event.char.lower()
    # Substitui apenas se a tecla for A/S/D/F
    if ch in MAPPING:
        text.insert('insert', MAPPING[ch] + ';')
        return "break"  # impede que a tecla original seja inserida
    # Para todas as outras teclas, inclusive backspace, delete, setas, Ctrl combos, deixa o comportamento normal

# Configuração da interface
root = tk.Tk()
root.title("Teclado Personalizado - A S D F → A B C D ;")

text = tk.Text(root, width=60, height=20)
text.pack(padx=10, pady=10)
text.focus_set()

# Liga o evento de tecla ao handler
text.bind("<Key>", on_key)

# Instruções opcionais
help_label = tk.Label(root, text="A S D F → A B C D + ';'. Outras teclas funcionam normalmente.")
help_label.pack(pady=(0,8))

root.mainloop()
