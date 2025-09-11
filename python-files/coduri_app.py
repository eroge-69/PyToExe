import tkinter as tk
from tkinter import messagebox, filedialog

def transforma():
    text_input = text_area.get("1.0", tk.END).strip()
    if not text_input:
        messagebox.showwarning("Atenție", "Introdu niște coduri mai întâi!")
        return
    
    coduri = text_input.splitlines()
    rezultat = ",".join(f"_{c.strip()}" for c in coduri if c.strip())
    
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, rezultat)

def salveaza():
    rezultat = output_area.get("1.0", tk.END).strip()
    if not rezultat:
        messagebox.showwarning("Atenție", "Nu există nimic de salvat!")
        return
    
    fisier = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Fișiere text", "*.txt")])
    if fisier:
        with open(fisier, "w", encoding="utf-8") as f:
            f.write(rezultat)
        messagebox.showinfo("Succes", f"Rezultatul a fost salvat în:\n{fisier}")

# Fereastra principală
root = tk.Tk()
root.title("Transformator Coduri")
root.geometry("600x450")

# Instrucțiuni
label = tk.Label(root, text="Lipește codurile (unul pe linie):")
label.pack(pady=5)

# Zonă input
text_area = tk.Text(root, height=10, width=70)
text_area.pack(pady=5)

# Butoane
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

btn_transforma = tk.Button(btn_frame, text="Transformă", command=transforma, width=15)
btn_transforma.pack(side=tk.LEFT, padx=5)

btn_salveaza = tk.Button(btn_frame, text="Salvează rezultat", command=salveaza, width=15)
btn_salveaza.pack(side=tk.LEFT, padx=5)

# Zonă output
label_out = tk.Label(root, text="Rezultat:")
label_out.pack(pady=5)
output_area = tk.Text(root, height=5, width=70)
output_area.pack(pady=5)

root.mainloop()
