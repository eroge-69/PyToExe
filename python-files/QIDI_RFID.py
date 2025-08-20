import tkinter as tk
from tkinter import messagebox
from smartcard.System import readers

# ================================
# CONFIG DATI
# ================================
MATERIALI = {
    "PLA": 1, "PLA Matte": 2, "PLA Metal": 3, "PLA Silk": 4, "PLA-CF": 5, "PLA-Wood": 6,
    "ABS": 11, "ABS-GF": 12, "ABS-Metal": 13, "ASA": 18, "ASA-AERO": 19,
    "PA": 24, "PA-CF": 25, "PAHT-CF": 30, "PAHT-GF": 31, "PC/ABS-FR": 34,
    "PET-CF": 37, "PET-GF": 38, "PETG": 41, "PPS-CF": 44, "PVA": 47, "TPU": 50
}

MATERIALI_REV = {v: k for k, v in MATERIALI.items()}

COLORI = {
    "#FAFAFA": 1, "#060606": 2, "#D9E3ED": 3, "#5CF30F": 4, "#63E492": 5, "#2850FF": 6,
    "#FE98FE": 7, "#DFD628": 8, "#228332": 9, "#99DEFF": 10, "#1714B0": 11, "#CEC0FE": 12,
    "#CADE4B": 13, "#1353AB": 14, "#5EA9FD": 15, "#A878FF": 16, "#FE717A": 17, "#FF362D": 18,
    "#E2DFCD": 19, "#898F9B": 20, "#6E3812": 21, "#CAC59F": 22, "#F28636": 23, "#B87F2B": 24
}

COLORI_REV = {v: k for k, v in COLORI.items()}

BLOCCO_SETT1 = 4
KEYS_TO_TRY = [
    [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7],
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
]

# ================================
# FUNZIONI RFID
# ================================
def connect_reader():
    r = readers()
    if not r:
        raise Exception("Nessun lettore trovato!")
    conn = r[0].createConnection()
    conn.connect()
    return conn

def load_key(conn, key):
    LOAD_KEY = [0xFF, 0x82, 0x00, 0x00, 0x06] + key
    _, sw1, sw2 = conn.transmit(LOAD_KEY)
    return (sw1 == 0x90 and sw2 == 0x00)

def authenticate_block(conn, block, key_type=0x60):
    AUTH_BLOCK = [0xFF, 0x86, 0x00, 0x00, 0x05,
                  0x01, 0x00, block, key_type, 0x00]
    _, sw1, sw2 = conn.transmit(AUTH_BLOCK)
    return (sw1 == 0x90 and sw2 == 0x00)

def find_working_key(conn, block):
    for key in KEYS_TO_TRY:
        if load_key(conn, key) and authenticate_block(conn, block):
            return key
    raise Exception("Nessuna chiave valida trovata per il blocco")

def write_block(conn, block, materiale_num, colore_num, valore_num, key):
    if not load_key(conn, key):
        raise Exception("Errore caricamento chiave")
    if not authenticate_block(conn, block):
        raise Exception(f"Autenticazione fallita per blocco {block}")
    data_bytes = [materiale_num, colore_num, valore_num] + [0x00]*13
    WRITE_BLOCK = [0xFF, 0xD6, 0x00, block, 0x10] + data_bytes
    _, sw1, sw2 = conn.transmit(WRITE_BLOCK)
    if sw1 != 0x90 or sw2 != 0x00:
        raise Exception(f"Scrittura fallita per blocco {block}")

def write_trailer_block(conn, sector, old_key):
    trailer_block = sector * 4 + 3
    key_a_new = [0xFF]*6
    key_b_new = [0xFF]*6
    access_bits = [0xFF, 0x07, 0x80, 0x69]
    data_bytes = key_a_new + access_bits + key_b_new

    if not load_key(conn, old_key):
        raise Exception(f"Errore caricamento chiave per settore {sector}")
    if not authenticate_block(conn, trailer_block):
        raise Exception(f"Autenticazione fallita per blocco trailer settore {sector}")

    WRITE_BLOCK = [0xFF, 0xD6, 0x00, trailer_block, 0x10] + data_bytes
    _, sw1, sw2 = conn.transmit(WRITE_BLOCK)
    if sw1 != 0x90 or sw2 != 0x00:
        raise Exception(f"Scrittura blocco trailer settore {sector} fallita")

def scrivi_tag(materiale_num, colore_num, valore_num=1):
    conn = connect_reader()
    working_key = find_working_key(conn, BLOCCO_SETT1)
    write_block(conn, BLOCCO_SETT1, materiale_num, colore_num, valore_num, working_key)
    for sector in range(16):
        write_trailer_block(conn, sector, working_key)
    conn.disconnect()
    messagebox.showinfo("Completato", "Scrittura completata con successo!")

def leggi_tag():
    try:
        conn = connect_reader()
        working_key = find_working_key(conn, BLOCCO_SETT1)

        if not load_key(conn, working_key) or not authenticate_block(conn, BLOCCO_SETT1):
            raise Exception("Autenticazione fallita per lettura")

        READ_BLOCK = [0xFF, 0xB0, 0x00, BLOCCO_SETT1, 0x10]
        data, sw1, sw2 = conn.transmit(READ_BLOCK)
        if sw1 != 0x90 or sw2 != 0x00:
            raise Exception("Lettura blocco fallita")

        materiale_val = data[0]
        colore_val = data[1]

        materiale_nome = MATERIALI_REV.get(materiale_val, f"Unknown ({materiale_val})")
        colore_hex = COLORI_REV.get(colore_val, "#FFFFFF")

        # Mostra info
        top = tk.Toplevel()
        top.title("Dati Tag")
        tk.Label(top, text=f"Materiale: {materiale_nome}", font=("Arial", 14)).pack(pady=5)
        colore_frame = tk.Frame(top, bg=colore_hex, width=100, height=50, relief="ridge", borderwidth=2)
        colore_frame.pack(pady=5)
        tk.Label(top, text=f"Colore: {colore_hex}", font=("Arial", 12)).pack(pady=5)

        conn.disconnect()

    except Exception as e:
        messagebox.showerror("Errore", str(e))

# ================================
# INTERFACCIA GRAFICA
# ================================
root = tk.Tk()
root.title("QIDI RFID TAG WRITER/READER")
root.geometry("400x450")

tk.Label(root, text="Tipo di materiale").pack(pady=5)
materiale_var = tk.StringVar()
materiale_combo = tk.OptionMenu(root, materiale_var, *MATERIALI.keys())
materiale_combo.pack()

tk.Label(root, text="Seleziona Colore").pack(pady=5)
canvas = tk.Canvas(root, width=300, height=150)
canvas.pack()

square_size = 30
cols_per_row = 6
color_positions = {}
colore_var = tk.StringVar()
colore_preview = tk.Label(root, text="Selezionato", bg="#FFFFFF", width=20, height=2, relief="ridge")
colore_preview.pack(pady=5)

for idx, (col_hex, val) in enumerate(COLORI.items()):
    row = idx // cols_per_row
    col = idx % cols_per_row
    x0 = col * square_size
    y0 = row * square_size
    x1 = x0 + square_size
    y1 = y0 + square_size
    rect = canvas.create_rectangle(x0, y0, x1, y1, fill=col_hex, outline="black")
    color_positions[rect] = (col_hex, val)

def on_canvas_click(event):
    clicked_items = canvas.find_closest(event.x, event.y)
    if clicked_items:
        col_hex, val = color_positions[clicked_items[0]]
        colore_var.set(col_hex)
        colore_preview.config(bg=col_hex)

canvas.bind("<Button-1>", on_canvas_click)

def on_write():
    try:
        mat = materiale_var.get()
        col_hex = colore_var.get()
        if mat not in MATERIALI or col_hex not in COLORI:
            messagebox.showerror("Errore", "Seleziona materiale e colore validi")
            return
        scrivi_tag(MATERIALI[mat], COLORI[col_hex], 1)
    except Exception as e:
        messagebox.showerror("Errore", str(e))

tk.Button(root, text="Scrivi su tag", command=on_write).pack(pady=10)
tk.Button(root, text="Leggi tag", command=leggi_tag).pack(pady=10)

root.mainloop()
