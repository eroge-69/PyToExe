import tkinter as tk
from tkinter import scrolledtext, messagebox

def pulisci_numeri():
    # Prende i numeri incollati dall'utente
    raw_text = input_box.get("1.0", tk.END)
    numeri = raw_text.splitlines()

    puliti = []
    visti = set()

    for num in numeri:
        num = num.strip()
        if num.startswith("+39"):
            num = num[3:]  # rimuove il prefisso +39
        if num and num not in visti:
            puliti.append(num)
            visti.add(num)

    # Mostra i numeri puliti
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "\n".join(puliti))
    messagebox.showinfo("Operazione completata", "Numeri puliti e duplicati rimossi!")

# --- GUI ---
root = tk.Tk()
root.title("Pulizia Numeri di Telefono")

tk.Label(root, text="Incolla qui i numeri:").pack()
input_box = scrolledtext.ScrolledText(root, width=40, height=10)
input_box.pack(padx=10, pady=5)

tk.Button(root, text="Pulisci numeri", command=pulisci_numeri).pack(pady=10)

tk.Label(root, text="Risultato:").pack()
output_box = scrolledtext.ScrolledText(root, width=40, height=10)
output_box.pack(padx=10, pady=5)

root.mainloop()
