import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog

BYTE_POS = 124  # Byte 124 (0-basiert)

# Zweites Nibble je Stufe
STUFEN_NIBBLE = {
    "MKA": "7",
    "MK":  "1",
    "EK":  "0",
}

def markiere_byte(text_widget, byte_pos, tag_name):
    start_index = f"1.0 + {byte_pos*2} chars"
    end_index = f"1.0 + {byte_pos*2 + 2} chars"
    text_widget.tag_remove(tag_name, "1.0", tk.END)
    text_widget.tag_add(tag_name, start_index, end_index)

def copy_checksum(event=None):
    checksum = label_checksum.cget("text")
    root.clipboard_clear()
    root.clipboard_append(checksum)
    messagebox.showinfo("Kopiert", f"Checksumme {checksum} wurde in die Zwischenablage kopiert.")

def lade_datei():
    filepath = filedialog.askopenfilename(
        title="EEPROM Datei laden",
        filetypes=[("HEX Dateien", "*.hex"), ("Alle Dateien", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, "rb") as f:
                daten = f.read()
            hex_daten = daten.hex().upper()
            text_hex.delete("1.0", tk.END)
            text_hex.insert("1.0", hex_daten)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden:\n{str(e)}")

def speichere_datei():
    neuer_inhalt = result_text.get("1.0", tk.END).strip()
    if not neuer_inhalt:
        messagebox.showwarning("Achtung", "Keine Daten zum Speichern vorhanden.")
        return
    if len(neuer_inhalt) % 2 != 0:
        messagebox.showerror("Fehler", "HEX-Daten haben ungerade Länge – ungültig!")
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".hex",
        filetypes=[("HEX Dateien", "*.hex"), ("Alle Dateien", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, "wb") as f:
                f.write(bytes.fromhex(neuer_inhalt))
            messagebox.showinfo("Gespeichert", f"Datei gespeichert:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))

def berechne_checksumme_und_update():
    try:
        hex_string = text_hex.get("1.0", tk.END).strip().replace(" ", "").replace("\n", "")
        if len(hex_string) % 2 != 0:
            messagebox.showerror("Fehler", "HEX Daten EEPROM müssen eine gerade Anzahl an Zeichen haben.")
            return

        if BYTE_POS*2+1 >= len(hex_string):
            messagebox.showerror("Fehler", f"HEX Daten EEPROM zu kurz für Byte-Position {BYTE_POS}.")
            return
        
        if len(hex_string) < (126 + 1)*2:
            messagebox.showerror("Fehler", "Mindestens 127 Bytes (254 Zeichen) notwendig.")
            return

        stufe = combo_stufe.get()
        if stufe not in STUFEN_NIBBLE:
            messagebox.showerror("Fehler", "Bitte eine gültige Stufe auswählen.")
            return
        
        neuer_nibble = STUFEN_NIBBLE[stufe]
        
        byte_start = BYTE_POS * 2
        altes_byte = hex_string[byte_start:byte_start+2]
        altes_high_nibble = altes_byte[0]
        neues_byte = altes_high_nibble + neuer_nibble
        
        alte_checksumme = int(hex_string[126*2:126*2+2], 16)
        alter_wert = int(altes_byte, 16)
        neuer_wert = int(neues_byte, 16)
        
        neue_checksumme = (alte_checksumme + alter_wert - neuer_wert) % 256
        
        neuer_hex_string = (
            hex_string[:byte_start] +
            neues_byte +
            hex_string[byte_start+2:126*2] +
            f"{neue_checksumme:02X}" +
            hex_string[126*2+2:]
        )
        
        result_text.config(state="normal")
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, neuer_hex_string)
        markiere_byte(result_text, BYTE_POS, "highlight")
        markiere_byte(result_text, 126, "checksum_highlight")
        result_text.config(state="disabled")

        label_checksum.config(text=f"{neue_checksumme:02X}")
        text_hex.tag_remove("highlight", "1.0", tk.END)
        text_hex.tag_remove("checksum_highlight", "1.0", tk.END)
        markiere_byte(text_hex, BYTE_POS, "highlight")
        markiere_byte(text_hex, 126, "checksum_highlight")
        
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gültige HEX Daten EEPROM eingeben.")

# GUI Setup
root = tk.Tk()
root.title("Checksummenrechner Swissphone RE329")
root.geometry("900x720")
root.resizable(False, False)

font_mono = ("Consolas", 11)
font_bold = ("Consolas", 11, "bold")

# Eingabe
frame_input = tk.LabelFrame(root, text="HEX Daten EEPROM Eingabe", padx=10, pady=10)
frame_input.pack(fill="both", padx=15, pady=(15, 5))

text_hex = scrolledtext.ScrolledText(frame_input, width=100, height=10, font=font_mono)
text_hex.pack(fill="both")
text_hex.tag_configure("highlight", foreground="red", font=font_bold)
text_hex.tag_configure("checksum_highlight", foreground="blue", font=font_bold)

# Stufe + Berechnen
frame_controls = tk.Frame(root)
frame_controls.pack(fill="x", padx=15, pady=10)

label_stufe = tk.Label(frame_controls, text="Stufe wählen (Byte 124 – 2. Stelle):", font=font_mono)
label_stufe.pack(side="left")

combo_stufe = ttk.Combobox(frame_controls, values=list(STUFEN_NIBBLE.keys()), state="readonly", font=font_mono, width=6)
combo_stufe.pack(side="left", padx=8)
combo_stufe.current(0)

btn_berechnen = tk.Button(frame_controls, text="Berechne & Update", font=font_bold, command=berechne_checksumme_und_update, bg="#007acc", fg="white", padx=10, pady=5)
btn_berechnen.pack(side="left", padx=15)

# Datei laden/speichern
frame_io = tk.Frame(root)
frame_io.pack(fill="x", padx=15, pady=(0, 10))

btn_laden = tk.Button(frame_io, text="Datei laden", command=lade_datei, width=20)
btn_laden.pack(side="left", padx=5)

btn_speichern = tk.Button(frame_io, text="Geänderte Datei speichern", command=speichere_datei, width=25)
btn_speichern.pack(side="left", padx=5)

# Checksumme
label_checksum_frame = tk.LabelFrame(root, text="Neue Checksumme (Byte 126)", padx=10, pady=10)
label_checksum_frame.pack(fill="x", padx=15, pady=(0, 10))

label_checksum = tk.Label(label_checksum_frame, text="--", font=("Consolas", 24, "bold"),
                         fg="darkgreen", bg="#d4f0d4", relief="solid", bd=2, padx=10, pady=5, cursor="hand2")
label_checksum.pack(pady=5)
label_checksum.bind("<Button-1>", copy_checksum)

# Ausgabe
frame_output = tk.LabelFrame(root, text="Aktualisierte HEX Daten EEPROM Ausgabe", padx=10, pady=10)
frame_output.pack(fill="both", padx=15, pady=(0, 15), expand=True)

result_text = scrolledtext.ScrolledText(frame_output, width=100, height=10, font=font_mono, state="disabled")
result_text.pack(fill="both")
result_text.tag_configure("highlight", foreground="red", font=font_bold)
result_text.tag_configure("checksum_highlight", foreground="blue", font=font_bold)

root.mainloop()
