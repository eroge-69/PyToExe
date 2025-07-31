
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import requests

# Costanti
PASSWORD = "evade42"
AI_ENDPOINT = "https://api.luci.ai/free"  # Placeholder endpoint, simulato

def chiedi_password():
    tentativi = 3
    while tentativi > 0:
        pw = simpledialog.askstring("Accesso Protetto", "Inserisci la password:", show="*")
        if pw == PASSWORD:
            return True
        else:
            tentativi -= 1
            messagebox.showerror("Errore", f"Password errata. Tentativi rimasti: {tentativi}")
    return False

def invia_ai(prompt):
    try:
        headers = {"Content-Type": "application/json"}
        json_data = {"prompt": prompt}
        # Simulazione chiamata (sostituibile con qualsiasi endpoint AI gratuito)
        response = requests.post("https://api.danbooru.donmai.us/simulated", json=json_data, timeout=10)
        if response.status_code == 200:
            return response.json().get("reply", "Risposta non trovata.")
        return "Errore nella richiesta AI."
    except:
        return "Connessione fallita. Verifica internet."

def invia_prompt():
    testo = input_box.get("1.0", tk.END).strip()
    if not testo:
        messagebox.showinfo("Attenzione", "Inserisci una domanda o frase.")
        return
    risposta = invia_ai(testo)
    output_box.config(state="normal")
    output_box.insert(tk.END, f"> {testo}
{risposta}

")
    output_box.config(state="disabled")
    input_box.delete("1.0", tk.END)

# GUI
root = tk.Tk()
root.title("EVADE V2 – AI Gratuita")
root.geometry("600x400")
root.configure(bg="#1e1e1e")

if not chiedi_password():
    root.destroy()
    exit()

input_box = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD, bg="#2d2d2d", fg="white", insertbackground="white")
input_box.pack(padx=10, pady=10, fill=tk.X)

send_button = tk.Button(root, text="Invia", command=invia_prompt, bg="#007acc", fg="white")
send_button.pack(pady=(0, 10))

output_box = scrolledtext.ScrolledText(root, height=15, wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4", state="disabled")
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
