import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import json

class CustomNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Notepad")

        self.text = tk.Text(root, wrap="word")
        self.text.pack(expand=True, fill="both")

        self.text.tag_configure("colored")
        self.filename = None

        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Novo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Salvar", command=self.save_file)
        file_menu.add_command(label="Salvar Como", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=root.quit)
        self.menu.add_cascade(label="Arquivo", menu=file_menu)

        format_menu = tk.Menu(self.menu, tearoff=0)
        format_menu.add_command(label="Mudar Cor de Fundo", command=self.change_bg_color)
        format_menu.add_command(label="Mudar Cor do Texto", command=self.change_fg_color)
        format_menu.add_command(label="Colorir Trecho Selecionado", command=self.highlight_selection)
        self.menu.add_cascade(label="Formato", menu=format_menu)

        self.bg_color = "white"
        self.fg_color = "black"

        self.text.configure(bg=self.bg_color, fg=self.fg_color)

    def new_file(self):
        self.text.delete("1.0", tk.END)
        self.text.tag_delete("colored")
        self.filename = None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Notepad Custom Format", "*.npd")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", data["content"])
                self.text.configure(bg=data["bg_color"], fg=data["fg_color"])
                self.bg_color = data["bg_color"]
                self.fg_color = data["fg_color"]

                self.text.tag_delete("colored")
                self.text.tag_configure("colored")
                for tag in data.get("tags", []):
                    self.text.tag_add("colored", tag["start"], tag["end"])
                    self.text.tag_config("colored", foreground=tag["color"])

            self.filename = file_path

    def save_file(self):
        if not self.filename:
            self.save_file_as()
        else:
            self._save_to_file(self.filename)

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".npd", filetypes=[("Notepad Custom Format", "*.npd")])
        if file_path:
            self.filename = file_path
            self._save_to_file(file_path)

    def _save_to_file(self, path):
        content = self.text.get("1.0", tk.END)
        tag_ranges = self.text.tag_ranges("colored")
        tags = []
        for i in range(0, len(tag_ranges), 2):
            tags.append({
                "start": str(tag_ranges[i]),
                "end": str(tag_ranges[i + 1]),
                "color": self.text.tag_cget("colored", "foreground")
            })
        data = {
            "content": content,
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
            "tags": tags
        }
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def change_bg_color(self):
        color = colorchooser.askcolor(title="Escolher cor de fundo")[1]
        if color:
            self.bg_color = color
            self.text.configure(bg=self.bg_color)

    def change_fg_color(self):
        color = colorchooser.askcolor(title="Escolher cor do texto")[1]
        if color:
            self.fg_color = color
            self.text.configure(fg=self.fg_color)

    def highlight_selection(self):
        try:
            start = self.text.index(tk.SEL_FIRST)
            end = self.text.index(tk.SEL_LAST)
            color = colorchooser.askcolor(title="Escolher cor para trecho selecionado")[1]
            if color:
                self.text.tag_add("colored", start, end)
                self.text.tag_config("colored", foreground=color)
        except tk.TclError:
            messagebox.showwarning("Nenhuma seleção", "Selecione um trecho de texto antes de aplicar a cor.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomNotepad(root)
    root.mainloop()
