import tkinter as tk
from tkinter import filedialog, messagebox
import os

def open_folder():
    folder_path = filedialog.askdirectory(title="Select Folder with .pza Files")
    if folder_path:
        orders = []
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower().endswith(".pza"):
                try:
                    with open(os.path.join(folder_path, fname), "r", encoding="utf-8") as f:
                        content = f.read()
                    orders.append(f"--- {fname} ---\n{content}\n")
                except Exception as e:
                    orders.append(f"--- {fname} ---\n[Error reading file: {e}]\n")
        if orders:
            text.delete("1.0", tk.END)
            text.insert(tk.END, "\n".join(orders))
            root.title(f"Viewing all .pza orders in: {folder_path}")
        else:
            messagebox.showinfo("No Orders", "No .pza files found in this folder.")

def open_pza_file():
    file_path = filedialog.askopenfilename(
        title="Open .pza File",
        filetypes=[("Pizza Order Files", "*.pza"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            text.delete("1.0", tk.END)
            text.insert(tk.END, content)
            root.title(f"Viewing: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

root = tk.Tk()
root.title("Pizza Order Viewer")
root.geometry("600x400")

menu = tk.Menu(root)
root.config(menu=menu)
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open .pza...", command=open_pza_file)
file_menu.add_command(label="Open Folder...", command=open_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

text = tk.Text(root, wrap="word", font=("Consolas", 12))
text.pack(fill="both", expand=True, padx=8, pady=8)

root.mainloop()