import tkinter as tk
from tkinter import filedialog
import hashlib

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def import_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def compare_sha256():
    file_path = file_entry.get()
    user_sha256 = sha_entry.get()

    if not file_path or not user_sha256:
        result_label.config(text="Veuillez importer un fichier et entrer un SHA-256.", fg="black")
        return

    calculated_sha256 = calculate_sha256(file_path)

    if calculated_sha256 == user_sha256:
        result_label.config(text="Les sommes de contrôle SHA-256 correspondent!", fg="green")
    else:
        result_label.config(text="Les sommes de contrôle SHA-256 ne correspondent pas.", fg="red")

# Create the main window
root = tk.Tk()
root.title("Comparateur SHA-256")

# File selection
file_label = tk.Label(root, text="Fichier:")
file_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=5)
import_button = tk.Button(root, text="Importer", command=import_file)
import_button.grid(row=0, column=2, padx=10, pady=5)

# SHA-256 input
sha_label = tk.Label(root, text="SHA-256 connu:")
sha_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
sha_entry = tk.Entry(root, width=50)
sha_entry.grid(row=1, column=1, padx=10, pady=5)

# Compare button
compare_button = tk.Button(root, text="Comparer", command=compare_sha256)
compare_button.grid(row=2, column=1, pady=20)

# Result label
result_label = tk.Label(root, text="", fg="black")
result_label.grid(row=3, column=1, pady=5)

# Run the application
root.mainloop()
