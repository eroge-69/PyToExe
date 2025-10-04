import tkinter as tk
import pyperclip

def on_key_release(event=None):
    content = text.get("1.0", tk.END)
    pyperclip.copy(content.strip())

root = tk.Tk()
root.title("Clipboard Notepad")
root.geometry("600x400")

text = tk.Text(root, wrap="word", font=("Arial", 14))
text.pack(expand=True, fill="both")

text.bind("<KeyRelease>", on_key_release)

root.mainloop()

how