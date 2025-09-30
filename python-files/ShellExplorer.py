import os
import tkinter as tk
from tkinter import filedialog, scrolledtext

class FileExplorerWithTerminal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShellExplorer")
        self.geometry("800x600")

        # Основной фрейм
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Список файлов
        self.file_listbox = tk.Listbox(self.main_frame)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Кнопка выбора директории
        self.dir_button = tk.Button(self, text="Открыть папку", command=self.load_directory)
        self.dir_button.pack(side=tk.TOP, anchor=tk.W)

        # Терминал в правом нижнем углу
        self.terminal_frame = tk.Frame(self.main_frame)
        self.terminal_frame.pack(side=tk.RIGHT, anchor=tk.SE, fill=tk.BOTH)

        self.terminal_output = scrolledtext.ScrolledText(self.terminal_frame, height=10, width=40, state='disabled')
        self.terminal_output.pack(side=tk.TOP, fill=tk.BOTH)

        self.terminal_input = tk.Entry(self.terminal_frame)
        self.terminal_input.pack(side=tk.BOTTOM, fill=tk.X)
        self.terminal_input.bind("<Return>", self.execute_command)

    def load_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.file_listbox.delete(0, tk.END)
            for file in os.listdir(folder):
                self.file_listbox.insert(tk.END, file)

    def execute_command(self, event=None):
        command = self.terminal_input.get()
        self.terminal_input.delete(0, tk.END)
        try:
            output = os.popen(command).read()
        except Exception as e:
            output = str(e)

        self.terminal_output.config(state='normal')
        self.terminal_output.insert(tk.END, f"> {command}\n{output}\n")
        self.terminal_output.config(state='disabled')
        self.terminal_output.see(tk.END)

if __name__ == "__main__":
    app = FileExplorerWithTerminal()
    app.mainloop()
