import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser, font
import time, json

class CustomNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Bloco de Notas Personalizado")
        self.root.geometry("800x600")

        self.filename = None
        self.text_changed = False

        self.text_area = tk.Text(self.root, undo=True, wrap="none")
        self.text_area.pack(fill=tk.BOTH, expand=1)

        self.status_bar = tk.Label(self.root, text="Lin: 1 | Col: 1", anchor='e')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_menu()
        self.bind_shortcuts()
        self.text_area.bind('<KeyRelease>', self.update_status_bar)
        self.update_status_bar()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Salvar", command=self.save_file)
        file_menu.add_command(label="Salvar como...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", command=lambda: self.text_area.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Refazer", command=lambda: self.text_area.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_command(label="Selecionar tudo", command=lambda: self.text_area.event_generate("<<SelectAll>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Localizar", command=self.find_text)
        edit_menu.add_command(label="Substituir", command=self.replace_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Inserir Data/Hora", command=self.insert_datetime)

        format_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Formatar", menu=format_menu)
        format_menu.add_command(label="Quebra automática de linha", command=self.toggle_wrap)
        format_menu.add_command(label="Fonte", command=self.choose_font)
        format_menu.add_command(label="Cor do fundo", command=self.choose_bg_color)
        format_menu.add_command(label="Cor do texto", command=self.choose_fg_color)
        format_menu.add_command(label="Cor do trecho selecionado", command=self.choose_selection_color)

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.clear_tags()
        self.filename = None
        self.root.title("Bloco de Notas Personalizado")

    def open_file(self):
        file = filedialog.askopenfilename(defaultextension=".notepadjson", filetypes=[("NotepadJSON", "*.notepadjson")])
        if file:
            self.filename = file
            self.root.title(f"{file} - Bloco de Notas Personalizado")
            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content['text'])
                self.clear_tags()
                for tag in content.get('tags', []):
                    self.text_area.tag_add(tag['name'], tag['start'], tag['end'])
                    self.text_area.tag_config(tag['name'], foreground=tag['color'])

    def save_file(self):
        if not self.filename:
            self.save_as_file()
        else:
            self._write_custom_format()

    def save_as_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".notepadjson", filetypes=[("NotepadJSON", "*.notepadjson")])
        if file:
            self.filename = file
            self.save_file()

    def _write_custom_format(self):
        text_content = self.text_area.get(1.0, tk.END)
        tag_data = []
        for tag in self.text_area.tag_names():
            if tag.startswith("custom_"):
                ranges = self.text_area.tag_ranges(tag)
                if len(ranges) == 2:
                    start, end = ranges
                    color = self.text_area.tag_cget(tag, "foreground")
                    tag_data.append({"name": tag, "start": str(start), "end": str(end), "color": color})
        content = {"text": text_content, "tags": tag_data}
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4)

    def find_text(self):
        search_term = simpledialog.askstring("Localizar", "Texto a localizar:")
        self.text_area.tag_remove("highlight", 1.0, tk.END)
        if search_term:
            idx = "1.0"
            while True:
                idx = self.text_area.search(search_term, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                end = f"{idx}+{len(search_term)}c"
                self.text_area.tag_add("highlight", idx, end)
                self.text_area.tag_config("highlight", background="yellow")
                idx = end

    def replace_text(self):
        find = simpledialog.askstring("Substituir", "Texto a substituir:")
        replace = simpledialog.askstring("Substituir por", "Substituir por:")
        content = self.text_area.get(1.0, tk.END)
        new_content = content.replace(find, replace)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, new_content)

    def insert_datetime(self):
        self.text_area.insert(tk.INSERT, time.strftime("%d/%m/%Y %H:%M:%S"))

    def toggle_wrap(self):
        current = self.text_area.cget("wrap")
        self.text_area.config(wrap="char" if current == "none" else "none")

    def choose_font(self):
        f = font.askfont(self.root)
        if f:
            font_name = f['family']
            font_size = f['size']
            self.text_area.config(font=(font_name, font_size))

    def choose_bg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text_area.config(bg=color)

    def choose_fg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text_area.config(fg=color)

    def choose_selection_color(self):
        try:
            start = self.text_area.index(tk.SEL_FIRST)
            end = self.text_area.index(tk.SEL_LAST)
            color = colorchooser.askcolor()[1]
            if color:
                tag_name = f"custom_{start.replace('.', '_')}_{end.replace('.', '_')}"
                self.text_area.tag_add(tag_name, start, end)
                self.text_area.tag_config(tag_name, foreground=color)
        except tk.TclError:
            messagebox.showinfo("Aviso", "Selecione um trecho de texto primeiro.")

    def clear_tags(self):
        for tag in self.text_area.tag_names():
            if tag.startswith("custom_"):
                self.text_area.tag_delete(tag)

    def update_status_bar(self, event=None):
        row, col = self.text_area.index(tk.INSERT).split(".")
        self.status_bar.config(text=f"Lin: {int(row)} | Col: {int(col) + 1}")

    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        self.root.bind('<Control-g>', lambda e: self.insert_datetime())

if __name__ == '__main__':
    root = tk.Tk()
    app = CustomNotepad(root)
    root.mainloop()
