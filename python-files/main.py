from tkinter import Tk, Text, Button, END, INSERT
from tkinter import filedialog


root = Tk()
root.geometry("600x600")
root.title("File Dialog Example")
root.config(bg="lightblue")
root.resizable(False, False)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if not file_path:
        return
    text = entry.get("1.0", END)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text)

def open_file():
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        entry.delete("1.0", END)  # Clear existing content
        entry.insert(INSERT, content)

Button(root, width=20, height=2, bg="#fff", text='Save File', command=save_file).place(x=100, y=5)
Button(root, width=20, height=2, bg="#fff", text='Open File', command=open_file).place(x=300, y=5)

entry = Text(root, width=72, height=33, wrap='word')
entry.place(x=10, y=60)

root.mainloop()
