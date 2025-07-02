import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import tempfile

def create_gradient(canvas, width, height, color1, color2):
    limit = width
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r_ratio = float(r2 - r1) / limit
    g_ratio = float(g2 - g1) / limit
    b_ratio = float(b2 - b1) / limit
    for i in range(limit):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = f'#{nr//256:02x}{ng//256:02x}{nb//256:02x}'
        canvas.create_line(i, 0, i, height, fill=color)

def update_line_numbers(event=None):
    line_numbers = "\n".join(str(i) for i in range(1, int(text_editor.index('end-1c').split('.')[0]) + 1))
    line_number_bar.config(state='normal')
    line_number_bar.delete('1.0', tk.END)
    line_number_bar.insert('1.0', line_numbers)
    line_number_bar.config(state='disabled')

def on_text_scroll(*args):
    text_editor.yview(*args)
    line_number_bar.yview(*args)

def open_file():
    filepath = filedialog.askopenfilename(
        filetypes=[
            ("Wszystkie pliki", "*.*"),
            ("Python", "*.py"),
            ("HTML", "*.html"),
            ("CSS", "*.css"),
            ("Batch", "*.bat"),
            ("VBScript", "*.vbs"),
            ("JSON", "*.json"),
            ("Java Archive", "*.jar"),
            ("JavaScript", "*.js"),
            ("PowerShell", "*.ps1")
        ]
    )
    if not filepath:
        return
    text_editor.delete(1.0, tk.END)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as input_file:
        text = input_file.read()
        text_editor.insert(tk.END, text)
    root.title(f"Edytor skryptów - {filepath}")
    update_line_numbers()

def save_file():
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[
            ("HTML", "*.html"),
            ("CSS", "*.css"),
            ("Batch", "*.bat"),
            ("VBScript", "*.vbs"),
            ("JSON", "*.json"),
            ("Java Archive", "*.jar"),
            ("JavaScript", "*.js"),
            ("PowerShell", "*.ps1"),
            ("Python", "*.py"),
            ("Wszystkie pliki", "*.*"),
        ],
    )
    if not filepath:
        return
    with open(filepath, "w", encoding="utf-8") as output_file:
        text = text_editor.get(1.0, tk.END)
        output_file.write(text)
    root.title(f"Edytor skryptów - {filepath}")
    messagebox.showinfo("Zapisano", "Plik został zapisany!")

def build_exe():
    code = text_editor.get(1.0, tk.END)
    with tempfile.TemporaryDirectory() as tempdir:
        temp_py_path = os.path.join(tempdir, "temp_script.py")
        with open(temp_py_path, "w", encoding="utf-8") as f:
            f.write(code)
        output_path = filedialog.asksaveasfilename(defaultextension=".exe",
                                                   filetypes=[("Plik wykonywalny", "*.exe")])
        if not output_path:
            return
        try:
            cmd = [
                "pyinstaller",
                "--onefile",
                "--noconsole",
                f"--distpath={os.path.dirname(output_path)}",
                f"--name={os.path.splitext(os.path.basename(output_path))[0]}",
                temp_py_path
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                messagebox.showerror("Błąd", f"Budowanie nie powiodło się:\n{proc.stderr}")
                return
            messagebox.showinfo("Sukces", f"Plik .exe został zbudowany:\n{output_path}")
            os.startfile(output_path)
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd:\n{e}")

root = tk.Tk()
root.title("Edytor skryptów")
width, height = 800, 600
root.geometry(f"{width}x{height}")

canvas = tk.Canvas(root, width=width, height=height)
canvas.pack(fill=tk.BOTH, expand=True)
create_gradient(canvas, width, height, "#764ba2", "#667eea")

line_number_bar = tk.Text(root, width=4, padx=4, takefocus=0, border=0,
                          background="#e0e0e0", state='disabled', font=("Consolas", 12))
line_number_bar.place(x=10, y=10, height=height-70)

text_editor = tk.Text(root, wrap=tk.NONE, font=("Consolas", 12), bg="#f0f0f0")
text_editor.place(x=60, y=10, width=width-70, height=height-70)

scrollbar = tk.Scrollbar(root, command=on_text_scroll)
scrollbar.place(x=width-10, y=10, height=height-70)
text_editor.config(yscrollcommand=scrollbar.set)
line_number_bar.config(yscrollcommand=scrollbar.set)

text_editor.bind('<KeyRelease>', update_line_numbers)
text_editor.bind('<MouseWheel>', update_line_numbers)
text_editor.bind('<Button-1>', update_line_numbers)
text_editor.bind('<Return>', update_line_numbers)

def draw_corners():
    canvas.delete("corner_text")
    canvas.create_text(10, 10, anchor="nw", text="AUTOR KAMIL BYRTUS", fill="white", font=("Arial", 10, "bold"), tags="corner_text")
    canvas.create_text(width - 10, 10, anchor="ne", text="AUTOR KAMIL BYRTUS", fill="white", font=("Arial", 10, "bold"), tags="corner_text")
    canvas.create_text(10, height - 60, anchor="sw", text="AUTOR KAMIL BYRTUS", fill="white", font=("Arial", 10, "bold"), tags="corner_text")
    canvas.create_text(width - 10, height - 60, anchor="se", text="AUTOR KAMIL BYRTUS", fill="white", font=("Arial", 10, "bold"), tags="corner_text")

draw_corners()
root.bind('<Configure>', lambda e: draw_corners())

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Otwórz", command=open_file)
file_menu.add_command(label="Zapisz", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Wyjście", command=root.quit)
menu_bar.add_cascade(label="Plik", menu=file_menu)
root.config(menu=menu_bar)

build_button = tk.Button(root, text="ZBUDUJ", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", command=build_exe)
build_button.place(x=width//2 - 50, y=height - 50, width=100, height=35)

update_line_numbers()
root.mainloop()
