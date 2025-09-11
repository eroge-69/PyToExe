import tkinter as tk
from tkinter import messagebox

def transforma():
    text_input = text_area.get("1.0", tk.END).strip()
    if not text_input:
        messagebox.showwarning("Atenție", "Introdu niște coduri mai întâi!")
        return
    
    coduri = text_input.splitlines()
    rezultat = ",".join(f"_{c.strip()}" for c in coduri if c.strip())
    
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, rezultat)

# Fereastra principală
root = tk.Tk()
root.title("Transformator Coduri")
root.geometry("500x400")

# Instrucțiuni
label = tk.Label(root, text="Lipește codurile (unul pe linie):")
label.pack(pady=5)

# Zonă input
text_area = tk.Text(root, height=10, width=50)
text_area.pack(pady=5)

# Buton de transformare
btn = tk.Button(root, text="Transformă", command=transforma)
btn.pack(pady=10)

# Zonă output
label_out = tk.Label(root, text="Rezultat:")
label_out.pack(pady=5)
output_area = tk.Text(root, height=5, width=50)
output_area.pack(pady=5)

root.mainloop()