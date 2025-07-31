import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

# Tema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Utility
def giorni_commerciali(start, end):
    sd, ed = min(start.day, 30), min(end.day, 30)
    return (end.year - start.year) * 360 + (end.month - start.month) * 30 + (ed - sd)

def aggiorna_output(entry, valore):
    entry.configure(state="normal")
    entry.delete(0, "end")
    entry.insert(0, valore)
    entry.configure(state="readonly")

def formatta_euro(val):
    return "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

# Calcolo
def calcola():
    try:
        inizio = datetime.strptime(inp_inizio.get(), "%d/%m/%Y")
        fine = datetime.strptime(inp_fine.get(), "%d/%m/%Y")
        cess = datetime.strptime(inp_cess.get(), "%d/%m/%Y")

        premio = float(inp_premio.get().replace(".", "").replace(",", "."))
        provv_inc = float(inp_provv_inc.get().replace(",", "."))
        provv_acq = float(inp_provv_acq.get().replace(",", "."))

        if not (inizio <= cess <= fine):
            messagebox.showerror("Errore", "La data di cessazione deve essere tra inizio e fine.")
            return

        durata = giorni_commerciali(inizio, fine)
        goduti = giorni_commerciali(inizio, cess)
        non_goduti = durata - goduti
        premio_goduto = premio * goduti / durata
        premio_non = premio - premio_goduto

        incasso_goduto = premio_goduto * provv_inc / 100
        incasso_rimborso = premio_non * provv_inc / 100
        acquisto_goduto = premio_goduto * provv_acq / 100
        acquisto_rimborso = premio_non * provv_acq / 100

        aggiorna_output(out_durata, f"{durata}")
        aggiorna_output(out_goduti, f"{goduti}")
        aggiorna_output(out_pg, f"€ {formatta_euro(premio_goduto)}")
        aggiorna_output(out_incasso_goduto, f"€ {formatta_euro(incasso_goduto)}")
        aggiorna_output(out_acquisto_goduto, f"€ {formatta_euro(acquisto_goduto)}")

        aggiorna_output(out_nongoduti, f"{non_goduti}")
        aggiorna_output(out_pr, f"€ {formatta_euro(premio_non)}")
        aggiorna_output(out_incasso_rimborso, f"€ {formatta_euro(incasso_rimborso)}")
        aggiorna_output(out_acquisto_rimborso, f"€ {formatta_euro(acquisto_rimborso)}")

    except Exception as e:
        messagebox.showerror("Errore", str(e))

# GUI
app = ctk.CTk()
app.iconbitmap("C:/APPFB/ICONA.ico")
app.title("Calcolo Rimborso Assicurazione")
app.geometry("1100x550")
app.configure(fg_color="#e6f2ff")

frame = ctk.CTkFrame(app, corner_radius=15, fg_color="#cce6ff")
frame.pack(padx=20, pady=20, fill="both", expand=True)

input_frame = ctk.CTkFrame(frame, corner_radius=12, fg_color="#cce6ff")
output_frame = ctk.CTkFrame(frame, corner_radius=12, fg_color="#cce6ff")

input_frame.grid(row=0, column=0, padx=30, pady=20, sticky="n")
output_frame.grid(row=0, column=1, padx=30, pady=20, sticky="n")

# Funzioni UI
def crea_input(frame, testo, riga):
    ctk.CTkLabel(frame, text=testo, text_color="#003366").grid(row=riga, column=0, sticky="w", pady=5, padx=5)
    entry = ctk.CTkEntry(frame, width=220, corner_radius=10)
    entry.grid(row=riga, column=1, pady=5, sticky="w")
    return entry

def crea_output(frame, testo, riga, colore="#000000"):
    ctk.CTkLabel(frame, text=testo, text_color="#003366").grid(row=riga, column=0, sticky="w", pady=5, padx=5)
    entry = ctk.CTkEntry(frame, width=260, state="readonly", text_color=colore, corner_radius=10)
    entry.grid(row=riga, column=1, pady=5, sticky="w")
    return entry

# Titolo input
ctk.CTkLabel(input_frame, text="📋 Dati polizza", font=("Segoe UI", 14, "bold"), text_color="#003366")\
    .grid(row=0, column=0, columnspan=2, pady=(5, 15), sticky="w")

# Campi input
inp_inizio = crea_input(input_frame, "Data inizio (gg/mm/aaaa)", 1)
inp_fine = crea_input(input_frame, "Data fine naturale (gg/mm/aaaa)", 2)
inp_cess = crea_input(input_frame, "Data cessazione (gg/mm/aaaa)", 3)
inp_premio = crea_input(input_frame, "Premio imponibile totale (€)", 4)
inp_provv_inc = crea_input(input_frame, "% Provvigione incasso", 5)
inp_provv_acq = crea_input(input_frame, "% Provvigione acquisto", 6)

ctk.CTkButton(
    input_frame,
    text="Calcola",
    command=calcola,
    fg_color="#005c99",
    hover_color="#007acc",
    corner_radius=12,
    width=150
).grid(row=7, column=0, columnspan=2, pady=15)

# Sezione Goduto
ctk.CTkLabel(output_frame, text="💚 Goduto",
             font=("Segoe UI Emoji", 14, "bold"), text_color="#006600")\
    .grid(row=0, column=0, columnspan=2, pady=(5, 10), sticky="w")


out_durata = crea_output(output_frame, "Durata polizza (giorni)", 1)
out_goduti = crea_output(output_frame, "Giorni goduti", 2)
out_pg = crea_output(output_frame, "Premio goduto", 3, colore="#006600")
out_incasso_goduto = crea_output(output_frame, "Provv. incasso goduta", 4, colore="#006600")
out_acquisto_goduto = crea_output(output_frame, "Provv. acquisto goduta", 5, colore="#006600")

# Sezione Non goduto
ctk.CTkLabel(output_frame, text="❤️ Non goduto / da revocare",
             font=("Segoe UI Emoji", 14, "bold"), text_color="#990000")\
    .grid(row=6, column=0, columnspan=2, pady=(15, 10), sticky="w")

out_nongoduti = crea_output(output_frame, "Giorni non goduti", 7)
out_pr = crea_output(output_frame, "Premio da rimborsare", 8, colore="#990000")
out_incasso_rimborso = crea_output(output_frame, "Provv. incasso da revocare", 9, colore="#990000")
out_acquisto_rimborso = crea_output(output_frame, "Provv. acquisto da revocare", 10, colore="#990000")

app.mainloop()
