import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import os
import win32com.client

def seleziona_percorso():
    cartella = filedialog.askdirectory()
    if cartella:
        entry_vals["Percorso"].delete(0, tk.END)
        entry_vals["Percorso"].insert(0, cartella)
        logbox.insert(tk.END, f"📁 Percorso selezionato: {cartella}")

def leggi_da_zwcad():
    zwcad = win32com.client.Dispatch("ZWCAD.Application")
    doc = zwcad.ActiveDocument
    ssets = doc.SelectionSets
    try:
        ssets.Item("SS1").Delete()
    except:
        pass

    sset = ssets.Add("SS1")
    logbox.insert(tk.END, "🖱️ Seleziona entità nel disegno ZWCAD...")
    sset.SelectOnScreen()

    arrayNodesLine = []
    arrayBlockList = []
    blockRawInfo = []
    countblock = 0
    c = 0

    for ent in sset:
        typename = ent.ObjectName
        logbox.insert(tk.END, f"🔍 Trovato: {typename}")
        if typename == "AcDbPolyline":
            coords = ent.Coordinates
            for i in range(0, len(coords), 2):
                x = round(coords[i], 2)
                y = round(coords[i + 1], 2)
                arrayNodesLine.append((x, y))
                c += 2
        elif typename == "AcDbCircle":
            center = ent.Center
            area = round(ent.Area, 2)
            block_str = f"{area},{round(center[0], 2)},{round(center[1], 2)}"
            arrayBlockList.append(block_str)
            blockRawInfo.append((round(center[0], 2), round(center[1], 2), area))
            countblock += 1

    return arrayNodesLine, arrayBlockList, blockRawInfo, countblock, c

def disegna_anteprima(canvas, nodes, blocks):
    canvas.delete("all")
    if not nodes and not blocks:
        return

    all_x = [x for x, y in nodes] + [cx for cx, cy, _ in blocks]
    all_y = [y for x, y in nodes] + [cy for cx, cy, _ in blocks]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    padding = 20
    canvas_w = canvas.winfo_width() - padding
    canvas_h = canvas.winfo_height() - padding
    scale_x = canvas_w / (max_x - min_x + 1)
    scale_y = canvas_h / (max_y - min_y + 1)
    scale = min(scale_x, scale_y)

    def tx(x): return int((x - min_x) * scale) + padding // 2
    def ty(y): return int((max_y - y) * scale) + padding // 2

    # Disegna polilinea
    if len(nodes) > 1:
        for i in range(len(nodes) - 1):
            x1, y1 = nodes[i]
            x2, y2 = nodes[i+1]
            canvas.create_line(tx(x1), ty(y1), tx(x2), ty(y2), fill="blue", width=2)
            x_start, y_start = nodes[0]
            x_end, y_end = nodes[-1]
            canvas.create_line(tx(x_end), ty(y_end), tx(x_start), ty(y_start), fill="blue", width=2)

    # Disegna cerchi
    for cx, cy, area in blocks:
        r = int((area ** 0.5) * scale / 2)
        canvas.create_oval(tx(cx)-r, ty(cy)-r, tx(cx)+r, ty(cy)+r, outline="red", width=2)

def genera_slu():
    try:
        path = entry_vals["Percorso"].get()
        title = entry_vals["Titolo"].get()
        ned = entry_vals["Ned"].get()
        mxed = entry_vals["Mxed"].get()
        myed = entry_vals["Myed"].get()
        steel = f'"{entry_vals["Acciaio"].get()}","Trefolo"'
        fyd = entry_vals["Fyd"].get()
        cls = f'"{entry_vals["Classe cls"].get()}"'
        fcd = entry_vals["Fcd"].get()

        os.makedirs(path, exist_ok=True)

        nodes, blocks, blockRawInfo, countblock, c = leggi_da_zwcad()

        logbox.insert(tk.END, f"✅ Coordinate lette: {len(nodes)}")
        for i, (x, y) in enumerate(nodes, start=1):
            logbox.insert(tk.END, f"  ◾ Coord {i}: {x},{y}")

        logbox.insert(tk.END, f"✅ Blocchi rilevati: {countblock}")
        for i, blk in enumerate(blocks, start=1):
            logbox.insert(tk.END, f"  ⬛ Blocco {i}: {blk}")

        disegna_anteprima(canvas_preview, nodes, blockRawInfo)

        filepath = os.path.join(path, f"{title}.slu")
        with open(filepath, "w") as f:
            f.write(f'"{title}","7.6"\n5\n{c // 2}\n')
            for x, y in nodes:
                f.write(f"{x},{y}\n")
            f.write("#FALSE#\n")
            f.write(str(countblock) + "\n")
            for line in blocks:
                f.write(line + "\n")
            f.write("0\n")
            f.write(ned + "\n")
            f.write(f"{mxed},{myed}\n")
            f.write("0\n0\n")
            f.write(steel + "\n")
            f.write(f"200000,.0675,{fyd},1500\n")
            f.write(cls + "\n")
            f.write(f".0035,{fcd},.85,.8,.002\n")
            f.write('"cm"\n')
            f.write("0,875,1250\n#FALSE#\n#FALSE#\n")
            f.write(ned + "\n")
            f.write(f"{mxed},{myed}\n")
            f.write("30,0,1080,9.75,.6,1.829,1.5,1.15\n")
            f.write("0,0\n0\n50\n1\n1.5\n0\n0\n0\n15,6\n")
            f.write("#TRUE#,#FALSE#\n#FALSE#,#TRUE#,#FALSE#\n")
            f.write("20,10,50,0\n25.0100002288818,0\n#FALSE#,0,0\n")
            f.write("0\n0,0,0\n0,0,0\n0,0,0\n0,0,0\n")
            f.write("0,0,0\n0,0,0\n0,1\n0,0,0\n0,0\n0,0\n0,#FALSE#\n")
            f.write('" "\n0,0,0\n0\n#FALSE#,#FALSE#,#FALSE#,0\n')
            f.write("#FALSE#,0,0,5.85\n0,0,0,0\n1,1\n0\n0,0\n0\n0\n0\n0\n0\n0,0\n0,0\n")
            f.write("#FALSE#,#FALSE#\n")
            f.write("0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n")
            f.write("0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n")
            f.write("0\n0\n0,0,0\n")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logbox.insert(tk.END, f"[{now}] 📝 File creato: {filepath}")
        logbox.insert(tk.END, "--------------------------------------------------")
    except Exception as e:
        messagebox.showerror("Errore", str(e))
        logbox.insert(tk.END, f"[Errore] {str(e)}")

# 🖼️ Interfaccia grafica
root = tk.Tk()
root.title("Generatore SLU con anteprima geometrica")

fields = [
    ("Percorso", ""),
    ("Titolo", ""),
    ("Ned", ""),
    ("Mxed", ""),
    ("Myed", ""),
    ("Acciaio", "FeB44k"),
    ("Fyd", "500"),
    ("Classe cls", "C30/37"),
    ("Fcd", "17"),
]

entry_vals = {}

for i, (field, default) in enumerate(fields):
    tk.Label(root, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="e")
    entry = tk.Entry(root, width=60)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entry.insert(0, default)
    entry_vals[field] = entry

# 🔘 Pulsante selezione cartella
tk.Button(root, text="Scegli cartella…", command=seleziona_percorso).grid(row=0, column=2, padx=5, pady=5)

# ▶️ Pulsante per avviare il processo
tk.Button(root, text="Seleziona in ZWCAD e genera SLU", command=genera_slu)\
    .grid(row=len(fields), column=0, columnspan=3, pady=10)

# 📐 Canvas anteprima geometrica
canvas_preview = tk.Canvas(root, width=800, height=400, bg="white", relief="sunken", bd=2)
canvas_preview.grid(row=len(fields)+1, column=0, columnspan=3, padx=10, pady=10)

# 📜 Logbox testuale sotto il canvas
logbox = tk.Listbox(root, width=100, height=10)
logbox.grid(row=len(fields)+2, column=0, columnspan=3, padx=10, pady=(0, 15))

# 🚀 Avvio dell'applicazione
root.mainloop()
