import tkinter as tk
from tkinter import ttk
import math

# ----------------- Helpers -----------------
def safe_float(s, default=0.0):
    try:
        return float(s)
    except (ValueError, TypeError):
        return default

def safe_int(s, default=0):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

# Lista de tipos para los menús desplegables
lista_tipos = [
    "Acero", "Agua", "Bicho", "Dragón", "Eléctrico", "Fantasma",
    "Fuego", "Hada", "Hielo", "Lucha", "Normal", "Planta",
    "Psíquico", "Roca", "Siniestro", "Tierra", "Veneno", "Volador"
]

# ----------------- Ventana -----------------
root = tk.Tk()
root.title("Calculadora de Daño - RPG")

# ----------------- Frame superior: datos del personaje -----------------
frame_superior = ttk.LabelFrame(root, text="Datos del Personaje", padding=8)
frame_superior.pack(fill="x", padx=10, pady=6)

# Tipos del personaje ahora con listas desplegables
ttk.Label(frame_superior, text="Tipo 1:").grid(row=0, column=0, sticky="w")
tipo1_combobox = ttk.Combobox(frame_superior, values=lista_tipos, width=10)
tipo1_combobox.grid(row=0, column=1, padx=4)
tipo1_combobox.set("") # Valor inicial vacío

ttk.Label(frame_superior, text="Tipo 2:").grid(row=0, column=2, sticky="w")
tipo2_combobox = ttk.Combobox(frame_superior, values=lista_tipos, width=10)
tipo2_combobox.grid(row=0, column=3, padx=4)
tipo2_combobox.set("") # Valor inicial vacío

# Stats y buffs
ttk.Label(frame_superior, text="Ataque:").grid(row=1, column=0, sticky="w")
ataque_var = tk.StringVar(value="0")
ttk.Entry(frame_superior, textvariable=ataque_var, width=10).grid(row=1, column=1, padx=4)

ttk.Label(frame_superior, text="Buff/Debuff (valor):").grid(row=1, column=2, sticky="w")
buff_atq_var = tk.StringVar(value="0")
ttk.Entry(frame_superior, textvariable=buff_atq_var, width=10).grid(row=1, column=3, padx=4)

ttk.Label(frame_superior, text="Ataque Especial:").grid(row=2, column=0, sticky="w")
ataque_esp_var = tk.StringVar(value="0")
ttk.Entry(frame_superior, textvariable=ataque_esp_var, width=10).grid(row=2, column=1, padx=4)

ttk.Label(frame_superior, text="Buff Esp (valor):").grid(row=2, column=2, sticky="w")
buff_esp_var = tk.StringVar(value="0")
ttk.Entry(frame_superior, textvariable=buff_esp_var, width=10).grid(row=2, column=3, padx=4)

# STAB (en personaje)
ttk.Label(frame_superior, text="STAB (valor):").grid(row=3, column=0, sticky="w")
stab_var = tk.StringVar(value="0")
ttk.Entry(frame_superior, textvariable=stab_var, width=10).grid(row=3, column=1, padx=4)

# ----------------- Frame central: ataques -----------------
frame_ataques = ttk.LabelFrame(root, text="Ataques", padding=8)
frame_ataques.pack(fill="both", padx=10, pady=6)

ataques = []

# ----------------- Función para mostrar el resultado en una ventana emergente -----------------
def mostrar_resultado_popup(nombre_ataque, logs):
    popup = tk.Toplevel(root)
    popup.title(f"Resultado de '{nombre_ataque}'")
    
    text_output = tk.Text(popup, height=15, width=60, wrap="word", padx=10, pady=10)
    text_output.pack(expand=True, fill="both")

    for l in logs:
        text_output.insert(tk.END, l + "\n")
    text_output.see(tk.END)

# ----------------- Función usar_ataque corregida -----------------
def usar_ataque(i):
    datos = ataques[i]

    # Leer PP
    pp = safe_int(datos["pp_var"].get(), 0)
    if pp <= 0:
        mostrar_resultado_popup(datos["nombre"].get() or 'Ataque', ["❗ **ERROR:** No quedan PP para este ataque."])
        return

    # Disminuir PP
    datos["pp_var"].set(str(pp - 1))

    # Leer valores de ataque
    nombre = datos["nombre"].get() or f"Ataque {i+1}"
    tipo_atk = (datos["tipo"].get() or "").strip().lower()
    dmg_base = safe_float(datos["dmg"].get(), 0.0)

    categoria = datos["categoria"].get() or "Físico"
    attacking_stat = safe_float(ataque_var.get(),0.0) if categoria=="Físico" else safe_float(ataque_esp_var.get(),0.0)
    buff_stat_val = safe_float(buff_atq_var.get(),0.0) if categoria=="Físico" else safe_float(buff_esp_var.get(),0.0)
    
    # Obtener valores de item, clima y campo
    item_bonus_val = safe_float(datos["item_var"].get(),0.0)
    stab_val = safe_float(stab_var.get(), 0.0)
    clima_choice = datos["clima_var"].get()
    campo_active = datos["campo_var"].get()

    # ----------------- START cálculo paso a paso (Lógica modificada) -----------------
    logs = []

    # 1. Daño Base (+)
    damage_pre_multipliers = dmg_base
    logs.append(f"1. Daño base: {dmg_base:.2f}")

    # 2. Estadística de Ataque (+)
    damage_pre_multipliers += attacking_stat
    logs.append(f"2. + Estadística de Ataque ({categoria}): {attacking_stat:.2f} -> Total: {damage_pre_multipliers:.2f}")

    # 3. Buffs/Debuffs (+)
    damage_pre_multipliers += buff_stat_val
    logs.append(f"3. + Buff/Debuff: {buff_stat_val:.2f} -> Total: {damage_pre_multipliers:.2f}")
    
    # 4. STAB (+)
    pj_t1 = tipo1_combobox.get().strip().lower()
    pj_t2 = tipo2_combobox.get().strip().lower()
    if tipo_atk and (tipo_atk == pj_t1 or tipo_atk == pj_t2):
        damage_pre_multipliers += stab_val
        logs.append(f"4. + STAB aplicado: {stab_val:.2f} -> Total: {damage_pre_multipliers:.2f}")
    else:
        logs.append("4. STAB no aplicado: 0.0")

    # 5. Item bonuses (+)
    damage_pre_multipliers += item_bonus_val
    logs.append(f"5. + Bonificación de Objeto: {item_bonus_val:.2f} -> Total: {damage_pre_multipliers:.2f}")
    
    # Iniciar con el valor calculado antes de las multiplicaciones
    final_damage = damage_pre_multipliers

    # 6. Type effectiveness (*)
    eff_mult = 1.0
    if datos["super_efectivo"].get():
        eff_mult = 2.0
    elif datos["muy_efectivo"].get():
        eff_mult = 1.5
    elif datos["poco_efectivo"].get():
        eff_mult = 0.5
    elif datos["super_poco_efectivo"].get():
        eff_mult = 0.25
    logs.append(f"6. * Efectividad de Tipo: x{eff_mult:.2f}")
    final_damage *= eff_mult

    # 7. Critical hit (*)
    if datos["critico"].get():
        logs.append("7. * Golpe Crítico: x1.5")
        final_damage *= 1.5
    else:
        logs.append("7. Golpe normal: x1.0")

    # 8. Weather (*)
    clima_mult = 1.0
    if clima_choice == "Positivo":
        clima_mult = 1.5
    elif clima_choice == "Negativo":
        clima_mult = 0.5
    logs.append(f"8. * Clima: x{clima_mult:.2f}")
    final_damage *= clima_mult

    # 9. Terrain (*)
    campo_mult = 1.0
    if campo_active:
        campo_mult = 1.5
    logs.append(f"9. * Terreno: x{campo_mult:.2f}")
    final_damage *= campo_mult

    # Redondear el resultado final hacia arriba
    final_damage_rounded = math.ceil(final_damage)
    logs.append(f"\nDAÑO FINAL (sin redondear): {final_damage:.2f}")
    logs.append(f"--- **DAÑO FINAL** (redondeado hacia arriba): {final_damage_rounded} ---")

    # Mostrar el resultado en una ventana emergente
    mostrar_resultado_popup(nombre, logs)

# Crear 4 ataques y posicionarlos en una grilla de 2x2
for i in range(4):
    f = ttk.LabelFrame(frame_ataques, text=f"Ataque {i+1}", padding=6)
    fila = i // 2
    columna = i % 2
    f.grid(row=fila, column=columna, padx=6, pady=4, sticky="nsew")

    # Variables por ataque
    nombre_var = tk.StringVar()
    tipo_var = tk.StringVar()
    pp_var = tk.StringVar(value="5")
    dmg_var = tk.StringVar(value="0")
    item_var = tk.StringVar(value="0")
    categoria_var = tk.StringVar(value="Físico")
    clima_var_atk = tk.StringVar(value="Normal")
    campo_var_atk = tk.BooleanVar(value=False)

    datos = {
        "nombre": nombre_var,
        "tipo": tipo_var,
        "pp_var": pp_var,
        "dmg": dmg_var,
        "item_var": item_var,
        "categoria": categoria_var,
        "clima_var": clima_var_atk,
        "campo_var": campo_var_atk,
        "muy_efectivo": tk.BooleanVar(),
        "super_efectivo": tk.BooleanVar(),
        "poco_efectivo": tk.BooleanVar(),
        "super_poco_efectivo": tk.BooleanVar(),
        "critico": tk.BooleanVar(),
    }
    ataques.append(datos)

    # Layout del ataque
    ttk.Label(f, text="Nombre:").grid(row=0, column=0, sticky="w")
    ttk.Entry(f, textvariable=nombre_var, width=18).grid(row=0, column=1, padx=4)

    ttk.Label(f, text="Tipo:").grid(row=0, column=2, sticky="w")
    # Combobox para el tipo del ataque
    tipo_combobox = ttk.Combobox(f, values=lista_tipos, textvariable=tipo_var, width=8)
    tipo_combobox.grid(row=0, column=3, padx=4)
    tipo_combobox.set("")

    ttk.Label(f, text="PP:").grid(row=1, column=0, sticky="w")
    ttk.Entry(f, textvariable=pp_var, width=6).grid(row=1, column=1, padx=4)

    ttk.Label(f, text="DMG base:").grid(row=1, column=2, sticky="w")
    ttk.Entry(f, textvariable=dmg_var, width=8).grid(row=1, column=3, padx=4)

    ttk.Label(f, text="Item Bonus:").grid(row=0, column=4, sticky="w")
    ttk.Entry(f, textvariable=item_var, width=8).grid(row=0, column=5, padx=4)

    # Categoria Físico / Especial
    ttk.Radiobutton(f, text="Físico", variable=categoria_var, value="Físico").grid(row=2, column=0, columnspan=2)
    ttk.Radiobutton(f, text="Especial", variable=categoria_var, value="Especial").grid(row=2, column=2, columnspan=2)

    # Clima (por ataque)
    ttk.Label(f, text="Clima:").grid(row=3, column=0, sticky="w")
    ttk.Radiobutton(f, text="Positivo", variable=clima_var_atk, value="Positivo").grid(row=3, column=1)
    ttk.Radiobutton(f, text="Negativo", variable=clima_var_atk, value="Negativo").grid(row=3, column=2)
    ttk.Radiobutton(f, text="Normal", variable=clima_var_atk, value="Normal").grid(row=3, column=3)

    # Campo (terrain)
    ttk.Checkbutton(f, text="Campo Positivo", variable=campo_var_atk).grid(row=4, column=0, columnspan=2, sticky="w")

    # Efectividades y Critico
    ttk.Checkbutton(f, text="Muy Efectivo", variable=datos["muy_efectivo"]).grid(row=5, column=0, sticky="w")
    ttk.Checkbutton(f, text="Súper Efectivo", variable=datos["super_efectivo"]).grid(row=5, column=1, sticky="w")
    ttk.Checkbutton(f, text="Poco Efectivo", variable=datos["poco_efectivo"]).grid(row=5, column=2, sticky="w")
    ttk.Checkbutton(f, text="Súper Poco Efectivo", variable=datos["super_poco_efectivo"]).grid(row=5, column=3, sticky="w")
    ttk.Checkbutton(f, text="Crítico", variable=datos["critico"]).grid(row=5, column=4, sticky="w")

    # Botón atacar
    ttk.Button(f, text="Atacar", command=lambda i=i: usar_ataque(i)).grid(row=6, column=0, columnspan=6, pady=6)

# Run
root.mainloop()
