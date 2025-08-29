import pandas as pd
from tkinter import Tk, StringVar, Button, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Combobox
import sys

Tk().withdraw()

dirreadfile = askopenfilename(
    title="Selecciona un padron",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)

dirsavefile = asksaveasfilename(
    title="Guardar archivo como...",
    defaultextension=".xlsx",
    filetypes=[("Archivos Excel", "*.xlsx")]
)

# ---------- INTERFAZ PARA ELEGIR POBLACIÓN ----------
# Definir tus grupos de subsectores
sectoresCAS = {
    "CASTELL - ROMERAL RD": [
        "MOT_ROMERAL - 1 ROMERAL",
        "MOT_ROMERAL - 1.1 SUBSECTOR EL ROMERAL",
        "MOT_ROMERAL - 1.1.1 SUBSUBSECTOR NUEVO ROMERAL",
        "MOT_ROMERAL - 1.2 ROMERAL VIEJO",
        "MOT_ROMERAL - 1.4 PASTORES"
    ],
    "CASTELL - GUALCHOS": [
        "CVS_GUALCHOS - GUALCHOS"
    ],
    "CASTELL - HILEROS": [
        "MOT_ROMERAL - 1.3 RAMBLA HILEROS-CASTELL"
    ]
}

sectoresTOR = {
    "MOT_TORRENUEVA - ACERA DEL MAR": [
        "MOT_TORRENUEVA - 1.5 ACERA DEL MAR",
        "MOT_TORRENUEVA - 1.5.1 ALCOTAN"
    ],
    "MOT_TORRENUEVA - RD": [
        "MOT_TORRENUEVA - 1 BALANDROS",
        "MOT_TORRENUEVA - 1.4 JARDINES",
        "MOT_TORRENUEVA - 1.1 TORREDOBLADA",
        "MOT_TORRENUEVA - 1.2 MERCADO"
    ]
}

ventana = Tk()
ventana.title("Seleccionar población")

combo = Combobox(ventana, state="readonly")
combo['values'] = ("TORRENUEVA", "CASTELL")
combo.current(0)
combo.pack(padx=60, pady=60)

def seleccionar():
    poblacion = combo.get().strip()
    if poblacion == "":
        messagebox.showwarning("Aviso", "Debes seleccionar una población")
    else:
        ventana.quit()

boton = Button(ventana, text="Aceptar", command=seleccionar)
boton.pack(pady=10)

ventana.bind("<Return>", lambda event: seleccionar())

def cerrar_ventana():
    if messagebox.askyesno("Salir", "No seleccionaste ninguna población. ¿Quieres salir?"):
        ventana.destroy()
        sys.exit()  # Termina el programa de forma limpia

ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)

ventana.mainloop()

# Recuperar la selección después de cerrar
poblacion = combo.get().strip()
ventana.destroy()

# Validación final
if poblacion == "CASTELL":
    poblSelect = sectoresCAS
elif poblacion == "TORRENUEVA":
    poblSelect = sectoresTOR
else:
    messagebox.showerror("Error", f"Población no válida: {poblacion!r}")
    sys.exit()



df = pd.read_excel(dirreadfile)
df = df[df["plantilla"].str.strip() != "EXENTA"]

# Convertir fechas a días desde 1970-01-01
df["fec_lec_ant_1"] = pd.to_datetime(df["fec_lec_ant_1"], errors="coerce")
df["fec_num_ant_1"] = (df["fec_lec_ant_1"] - pd.Timestamp("1970-01-01")).dt.days
df["fm_lec_ant"] = df["fec_num_ant_1"] * df["dif_lec_1"]

df["fec_lec_act_1"] = pd.to_datetime(df["fec_lec_act_1"], errors="coerce")
df["fec_num_act_1"] = (df["fec_lec_act_1"] - pd.Timestamp("1970-01-01")).dt.days
df["fm_lec_act"] = df["fec_num_act_1"] * df["dif_lec_1"]

# Función para calcular fecha media ponderada y sumas por subsector
def fecha_media_ponderada(subdf):
    fm_lec_ant_acum = subdf["fm_lec_ant"].sum()
    fm_lec_act_acum = subdf["fm_lec_act"].sum()
    dif_lec_1_acum = subdf["dif_lec_1"].sum()
    m3_fact_acum = subdf["m3_fact"].sum()
    clientes = subdf["cliente"].count()

    media_ant_dias = fm_lec_ant_acum / dif_lec_1_acum
    media_act_dias = fm_lec_act_acum / dif_lec_1_acum
    
    fecha_media_ant = pd.Timestamp("1970-01-01") + pd.to_timedelta(media_ant_dias, unit="D")
    fecha_media_act = pd.Timestamp("1970-01-01") + pd.to_timedelta(media_act_dias, unit="D")
    
    return pd.Series({
        "lec_ant": fecha_media_ant.date(),
        "lec_act": fecha_media_act.date(),
        "dif_lec": dif_lec_1_acum,
        "m3_fact": m3_fact_acum,
        "contratos": clientes
    })

def fecha_media_ponderada_resumen(subdf):
    fm_lec_ant = ((pd.to_datetime(subdf["lec_ant"]) - pd.Timestamp("1970-01-01")).dt.days * subdf["dif_lec"]).sum()
    fm_lec_act = ((pd.to_datetime(subdf["lec_act"]) - pd.Timestamp("1970-01-01")).dt.days * subdf["dif_lec"]).sum()
    
    dif_lec_sum = subdf["dif_lec"].sum()
    m3_fact_sum = subdf["m3_fact"].sum()
    contratos_sum = subdf["contratos"].sum()
    
    fecha_ant = pd.Timestamp("1970-01-01") + pd.to_timedelta(fm_lec_ant / dif_lec_sum, unit="D")
    fecha_act = pd.Timestamp("1970-01-01") + pd.to_timedelta(fm_lec_act / dif_lec_sum, unit="D")
    
    return pd.Series({
        "lec_ant": fecha_ant.date(),
        "lec_act": fecha_act.date(),
        "dif_lec": dif_lec_sum,
        "m3_fact": m3_fact_sum,
        "contratos": contratos_sum
    })

# Calcular por subsector
resumen_df = df.groupby("subsector", dropna=False).apply(fecha_media_ponderada)
print(resumen_df)

df_agrupado = pd.DataFrame(columns=["lec_ant", "lec_act", "dif_lec", "m3_fact", "contratos"])

for nombre_grupo, lista_subsectores in poblSelect.items():
    subdf = resumen_df[resumen_df.index.isin(lista_subsectores)]
    df_agrupado.loc[nombre_grupo] = fecha_media_ponderada_resumen(subdf)

# Mostrar resultado
print(df_agrupado)

with pd.ExcelWriter(dirsavefile, engine="openpyxl") as writer:
    resumen_df.to_excel(writer, sheet_name="Resumen")
    df_agrupado.to_excel(writer, sheet_name="Agrupado")
    df.to_excel(writer, sheet_name="Padron")

print(f"Archivo guardado con éxito en: {dirsavefile}")
