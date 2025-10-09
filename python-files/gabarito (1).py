import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Mapeamento: tecla física -> letra que será inserida (maiúscula)
KEY_MAP = {
    'a': 'A',
    's': 'B',
    'd': 'C',
    'f': 'D'
}

class LetterApp:
    def __init__(self, root):
        self.root = root
        root.title("Gabarito")
        root.geometry("760x480")
        root.minsize(700, 420)

        # contador de letras inseridas (para o auto-enter)
        self.letter_count = 0

        # Frame superior com botões A B C D e controles
        top = ttk.Frame(root, padding=(8,8))
        top.pack(side=tk.TOP, fill=tk.X)

        # Botões A B C D (lado a lado)
        btn_frame = ttk.Frame(top)
        btn_frame.pack(side=tk.LEFT, padx=(0,12))
        for ch in ("A","B","C","D"):
            b = ttk.Button(btn_frame, text=ch, width=6, command=lambda c=ch: self.insert_letter_from_button(c))
            b.pack(side=tk.LEFT, padx=4)

        # Spinbox (Choice) 0-100 para auto-enter
        choice_frame = ttk.Frame(top)
        choice_frame.pack(side=tk.LEFT, padx=(10,12))
        ttk.Label(choice_frame, text="Auto-Enter a cada:").pack(anchor=tk.W)
        self.spin_var = tk.IntVar(value=0)
        self.spin = ttk.Spinbox(choice_frame, from_=0, to=100, width=5, textvariable=self.spin_var)
        self.spin.pack()

        ttk.Label(choice_frame, text="(0 = desativado)").pack(anchor=tk.W)

        # Botões copiar / salvar / carregar
        action_frame = ttk.Frame(top)
        action_frame.pack(side=tk.RIGHT, padx=8)
        ttk.Button(action_frame, text="Copiar tudo", command=self.copy_all).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="Salvar (.dat)", command=self.save_dat).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_frame, text="Carregar (.dat)", command=self.load_dat).pack(side=tk.LEFT, padx=6)

        # Texto principal com scrollbar
        text_frame = ttk.Frame(root, padding=(8,4))
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(text_frame, wrap=tk.WORD, undo=True)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(text_frame, command=self.text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scroll.set)

        # Bind de teclas: intercepta teclas imprimíveis
        # Use bind on the Text widget to control insertion and still allow normal behavior for control keys.
        self.text.bind("<Key>", self.on_keypress)

        # Ajuda rápida na parte inferior
        footer = ttk.Frame(root, padding=(8,6))
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        help_text = ("Digite letras normalmente — cada letra imprimível será inserida seguida de ';'.\n"
                     "Teclas A S D F são mapeadas para A B C D (maiúsculas). Espaço insere ' ' + ';'.\n"
                     "Escolha um número (0-100) para auto-enter após N letras. Use Salvar/Carregar para .dat.")
        ttk.Label(footer, text=help_text, wraplength=720, justify=tk.LEFT).pack()

    def insert_letter_from_button(self, ch):
        """Inserção via botão (A/B/C/D)."""
        # Insere letra seguida de ; na posição atual do cursor
        self._insert_with_semicolon(ch)
        # foca novamente no text widget
        self.text.focus_set()

    def on_keypress(self, event):
        """
        Trata todas as teclas pressionadas na Text widget.
        Se for caractere imprimível (event.char não vazio e não controle), insere <CARACT> + ';'
        - Mapeia a/s/d/f conforme KEY_MAP.
        - Para espaço, insere ' ' + ';'
        - Para teclas de controle (Backspace, Return, Tab, setas, etc.) deixa o comportamento padrão.
        """
        # event.char é string vazia para teclas como Shift, Ctrl, etc.
        ch = event.char
        keysym = event.keysym

        # Permitimos que Ctrl+C, Ctrl+V e outros combos funcionem naturalmente:
        if (event.state & 0x4) != 0:  # se Ctrl estiver pressionado (state bit mask)
            # deixa o comportamento natural para combos com Ctrl
            return

        # Se não há char imprimível, permitir comportamento padrão (ex.: BackSpace, Return)
        if not ch:
            return

        # Se a tecla for Enter (Return) ou BackSpace ou Tab -> permitir comportamento normal (não alteramos)
        if keysym in ("Return", "BackSpace", "Tab", "Left", "Right", "Up", "Down", "Home", "End", "Delete"):
            return

        # Agora tratamos caracteres imprimíveis: letras, números, espaços, pontuação etc.
        # Convertemos para mapeamento se necessário
        lower = ch.lower()
        if lower in KEY_MAP:
            insert_char = KEY_MAP[lower]
        else:
            # preserva a forma original do caractere, mas converte letras para maiúsculas (conforme solicitou letras maiúsculas)
            if ch.isalpha():
                insert_char = ch.upper()
            else:
                insert_char = ch  # números e pontuações ficam iguais

        # Se for espaço, queremos inserir ' ' + ';'
        if ch == ' ':
            to_insert = ' ' + ';'
        else:
            to_insert = insert_char + ';'

        # Inserir no widget texto na posição atual
        self.text.insert(tk.INSERT, to_insert)

        # Atualiza contador e possivelmente adiciona newline
        self._increment_and_maybe_newline()

        # Impede a inserção padrão (evita duplicar o caractere)
        return "break"

    def _insert_with_semicolon(self, ch):
        """Insere ch + ';' e atualiza contador. ch é esperado já em forma final (A,B,C,D ou outros)."""
        to_insert = (ch + ';') if ch != ' ' else (' ' + ';')
        self.text.insert(tk.INSERT, to_insert)
        self._increment_and_maybe_newline()

    def _increment_and_maybe_newline(self):
        """Incrementa contador de letras e insere \n se alcançou o valor do spinbox (se >0)."""
        # incrementa quando inserimos um "item" (letra ou espaço)
        self.letter_count += 1
        target = self.spin_var.get()
        try:
            target = int(target)
        except Exception:
            target = 0
            self.spin_var.set(0)

        if target > 0 and self.letter_count >= target:
            # insere nova linha
            self.text.insert(tk.INSERT, '\n')
            self.letter_count = 0

    def copy_all(self):
        """Copia todo o conteúdo do Text para a área de transferência."""
        content = self.text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Copiado", "Todo o conteúdo foi copiado para a área de transferência.")

    def save_dat(self):
        """Salva o conteúdo em arquivo .dat (UTF-8)."""
        content = self.text.get("1.0", tk.END)
        fn = filedialog.asksaveasfilename(defaultextension=".dat",
                                          filetypes=[("DAT files", "*.dat"), ("All files", "*.*")],
                                          title="Salvar como...")
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Salvo", f"Arquivo salvo: {fn}")
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def load_dat(self):
        """Carrega conteúdo de um arquivo .dat e substitui o texto corrente."""
        fn = filedialog.askopenfilename(defaultextension=".dat",
                                        filetypes=[("DAT files", "*.dat"), ("All files", "*.*")],
                                        title="Abrir arquivo...")
        if not fn:
            return
        try:
            with open(fn, "r", encoding="utf-8") as f:
                data = f.read()
            # substitui conteúdo e zera contador
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", data)
            self.letter_count = 0
            messagebox.showinfo("Carregado", f"Arquivo carregado: {fn}")
        except Exception as e:
            messagebox.showerror("Erro ao carregar", f"Não foi possível abrir o arquivo:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LetterApp(root)
    root.mainloop()
