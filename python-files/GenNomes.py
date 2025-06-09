import tkinter as tk
from tkinter import ttk, messagebox

def centrar_janela(root):
    root.update_idletasks()
    largura = root.winfo_width()
    altura = root.winfo_height()
    largura_ecra = root.winfo_screenwidth()
    altura_ecra = root.winfo_screenheight()
    x = (largura_ecra // 2) - (largura // 2)
    y = (altura_ecra // 2) - (altura // 2)
    root.geometry(f"+{x}+{y}")

def copiar_texto(texto):
    root.clipboard_clear()
    root.clipboard_append(texto)
    root.update()
    messagebox.showinfo("Copiado", f"\"{texto}\" copiado para a área de transferência.")

def atualizar_campos(*args):
    zona = combo_zona.get()
    for frame in (frame_rip, frame_dose, frame_indefinido):
        frame.grid_remove()
    for frame in (frame_resultados_rip, frame_resultados_dose):
        frame.grid_remove()

    if zona == "RIP":
        frame_rip.grid(row=1, column=0, sticky="nw")
        frame_resultados_rip.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,10))
    elif zona == "DOSE":
        frame_dose.grid(row=1, column=0, sticky="nw")
        frame_resultados_dose.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,10))
    else:
        frame_indefinido.grid(row=1, column=0, sticky="nw")

def gerar_nomes():
    zona = combo_zona.get()

    if not zona:
        for tipo in resultados:
            resultados[tipo].set("Escolha uma zona primeiro.")
        return

    if zona == "RIP":
        departement = entry_departement.get()
        tri = entry_tri.get()
        commune = entry_commune_rip.get()
        pmz = entry_pmz_rip.get()
        pa = entry_pa_rip.get()
        imb = entry_imb_rip.get().replace("/", "")

        resultados["RIP_CAPFT"].set(f"{departement}{tri}_CST_ET_CAPFT_{commune}_PMZ{pmz}_PA{pa}_{imb}")
        resultados["RIP_COMAC"].set(f"{departement}{tri}_CST_ET_COMAC_{commune}_PMZ{pmz}_PA{pa}_{imb}")
        resultados["RIP_IMPL"].set(f"{departement}{tri}_CST_ET_IMPL_{commune}_PMZ{pmz}_PA{pa}_{imb}")

    elif zona == "DOSE":
        commune = entry_commune_dose.get()
        pmz = entry_pmz_dose.get()
        pa = entry_pa_dose.get()
        imb = entry_imb_dose.get().replace("/", "_")
        rue = entry_rue_dose.get().upper()

        resultados["DOSE_CAPFT"].set(f"CST_CAPFT_{commune}_{rue}_PMZ{pmz}_PA{pa}_D2")
        resultados["DOSE_COMAC"].set(f"ET_NBS_FTTH_UCIPRM_{commune}_{imb}")
        resultados["DOSE_IMPL_Comac"].set(f"ET_NBS_IMPL_UCIPRM_{commune}_{imb}")
        resultados["DOSE_IMPL_Capft"].set(f"CST_IMPL_{commune}_{rue}_PMZ{pmz}_PA{pa}_D2")

    elif zona == "DOCE":
        for tipo in resultados:
            resultados[tipo].set("Zona ainda não implementada.")

    elif zona == "DOC":
        for tipo in resultados:
            resultados[tipo].set("Zona ainda não implementada.")

root = tk.Tk()
root.title("Générateur de noms d'études")

root.geometry("610x350")
root.resizable(False, False)
centrar_janela(root)

frame_top = ttk.Frame(root)
frame_top.grid(row=0, column=0, sticky="w", padx=10, pady=(10,5))

ttk.Label(frame_top, text="Zone:").grid(row=0, column=0, sticky="w")
combo_zona = ttk.Combobox(frame_top, values=["RIP", "DOSE", "DOC", "DOCE"], state="readonly", width=8)
combo_zona.grid(row=0, column=1, sticky="w", padx=(5,0))
combo_zona.set("")
combo_zona.bind("<<ComboboxSelected>>", atualizar_campos)


frame_inputs = ttk.Frame(root)
frame_inputs.grid(row=1, column=0, sticky="nw", padx=10, pady=5)

frame_rip = ttk.LabelFrame(frame_inputs, text="Zone RIP")
frame_rip.grid_columnconfigure(2, weight=1)
ttk.Label(frame_rip, text="Département:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
entry_departement = ttk.Entry(frame_rip, width=50)
entry_departement.grid(row=0, column=2, padx=5, sticky="w")
ttk.Label(frame_rip, text="Commune Code:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
entry_commune_rip = ttk.Entry(frame_rip, width=50)
entry_commune_rip.grid(row=1, column=2, padx=5, sticky="w")
ttk.Label(frame_rip, text="TRI:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
entry_tri = ttk.Entry(frame_rip, width=50)
entry_tri.grid(row=2, column=2, padx=5, sticky="w")
ttk.Label(frame_rip, text="PMZ:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
entry_pmz_rip = ttk.Entry(frame_rip, width=50)
entry_pmz_rip.grid(row=3, column=2, padx=5, sticky="w")
ttk.Label(frame_rip, text="PA:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
entry_pa_rip = ttk.Entry(frame_rip, width=50)
entry_pa_rip.grid(row=4, column=2, padx=5, sticky="w")
ttk.Label(frame_rip, text="IMB:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
entry_imb_rip = ttk.Entry(frame_rip, width=50)
entry_imb_rip.grid(row=5, column=2, padx=5, sticky="w")

frame_dose = ttk.LabelFrame(frame_inputs, text="Zone DOSE")
frame_dose.grid_columnconfigure(2, weight=1)
ttk.Label(frame_dose, text="Commune Code:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
entry_commune_dose = ttk.Entry(frame_dose, width=50)
entry_commune_dose.grid(row=0, column=2, padx=5, sticky="w")
ttk.Label(frame_dose, text="PMZ:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
entry_pmz_dose = ttk.Entry(frame_dose, width=50)
entry_pmz_dose.grid(row=1, column=2, padx=5, sticky="w")
ttk.Label(frame_dose, text="PA:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
entry_pa_dose = ttk.Entry(frame_dose, width=50)
entry_pa_dose.grid(row=2, column=2, padx=5, sticky="w")
ttk.Label(frame_dose, text="IMB:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
entry_imb_dose = ttk.Entry(frame_dose, width=50)
entry_imb_dose.grid(row=3, column=2, padx=5, sticky="w")
ttk.Label(frame_dose, text="Rue:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
entry_rue_dose = ttk.Entry(frame_dose, width=50)
entry_rue_dose.grid(row=4, column=2, padx=5, sticky="w")

frame_indefinido = ttk.LabelFrame(frame_inputs, text="Zona em desenvolvimento")
ttk.Label(frame_indefinido, text="Funcionalidade ainda não disponível para esta zona.").pack(padx=10, pady=10)

frame_botao = ttk.Frame(root)
frame_botao.grid(row=1, column=1, sticky="ns", padx=10, pady=5)
frame_botao.rowconfigure(0, weight=1)
btn_gerar = ttk.Button(frame_botao, text="Gerar Nomes", width=20, command=gerar_nomes)
btn_gerar.grid(row=0, column=0, sticky="n")

# Frames resultados separados para RIP e DOSE
frame_resultados_rip = ttk.Frame(root)
frame_resultados_rip.columnconfigure(1, weight=1)

resultados = {}

linha_rip = 0
for tipo in ["CAPFT", "COMAC", "IMPL"]:
    chave = f"RIP_{tipo}"
    resultados[chave] = tk.StringVar()
    ttk.Label(frame_resultados_rip, text=tipo + ":").grid(row=linha_rip, column=0, padx=5, pady=2, sticky="e")
    ttk.Entry(frame_resultados_rip, textvariable=resultados[chave], width=65).grid(row=linha_rip, column=1, padx=5, pady=2, sticky="we")
    ttk.Button(frame_resultados_rip, text="Copiar", width=10, command=lambda c=chave: copiar_texto(resultados[c].get())).grid(row=linha_rip, column=2, padx=5, pady=2)
    linha_rip += 1

frame_resultados_dose = ttk.Frame(root)
frame_resultados_dose.columnconfigure(1, weight=1)

resultados["DOSE_CAPFT"] = tk.StringVar()
resultados["DOSE_COMAC"] = tk.StringVar()
resultados["DOSE_IMPL_Comac"] = tk.StringVar()
resultados["DOSE_IMPL_Capft"] = tk.StringVar()

linhas_dose = [
    ("CAPFT", "DOSE_CAPFT"),
    ("COMAC", "DOSE_COMAC"),
    ("IMPL COMAC", "DOSE_IMPL_Comac"),
    ("IMPL CAPFT", "DOSE_IMPL_Capft"),
]

for i, (label, chave) in enumerate(linhas_dose):
    ttk.Label(frame_resultados_dose, text=label + ":").grid(row=i, column=0, padx=5, pady=2, sticky="e")
    ttk.Entry(frame_resultados_dose, textvariable=resultados[chave], width=65).grid(row=i, column=1, padx=5, pady=2, sticky="we")
    ttk.Button(frame_resultados_dose, text="Copiar", width=10, command=lambda c=chave: copiar_texto(resultados[c].get())).grid(row=i, column=2, padx=5, pady=2)

atualizar_campos()

root.mainloop()
