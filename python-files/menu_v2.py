
import tkinter as tk
from tkinter import ttk, messagebox

def cargar_datos():
    datos = []
    try:
        ruta_var = r"\\fafs01h1.automotive-wan.com\didr3395\ICT_PROGRAMS\Variantes\Variantes_Subaru_L2_T23.txt"
        with open(ruta_var, "r") as archivo:
            for linea in archivo.readlines():
                if linea.strip():
                    partes = linea.strip().split("\t")
                    if len(partes) >= 4 and partes[3].strip().lower() == "habilitado":
                        datos.append(partes)
    except FileNotFoundError:
        with open(ruta_var, "w") as archivo:
            archivo.write("Variante1\tVariante1\tVariante1\tHabilitado\n")
        messagebox.showinfo("Archivo Creado", "El archivo 'Variantes.txt' no fue encontrado, pero ha sido creado con valores predeterminados.")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {e}")
        ventana.quit()
    return datos

def centrar_ventana(ventana, ancho, alto):
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()
    x = (screen_width - ancho) // 2
    y = (screen_height - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def actualizar_columnas(event):
    seleccion = listbox.curselection()
    if seleccion:
        idx = seleccion[0]
        real_idx = indice_visible_a_real.get(idx)
        if real_idx is not None:
            variante_equipo = datos[real_idx][1]
            subensamble = datos[real_idx][2]
            label_variante.config(text=f"Variante Equipo: {variante_equipo}")
            label_subensamble.config(text=f"Subensamble: {subensamble}")

def filtrar_variantes(event):
    filtro = entry_buscar.get().strip().lower()
    listbox.delete(0, tk.END)
    global indice_visible_a_real
    indice_visible_a_real = {}
    contador = 0

    for idx, dato in enumerate(datos):
        if filtro in dato[0].lower():
            if contador % 15 == 0 and contador != 0:
                listbox.insert(tk.END, "-------------------------------")
                indice_visible_a_real[listbox.size() - 1] = None
            listbox.insert(tk.END, f"{idx + 1}.- {dato[0]}")
            indice_visible_a_real[listbox.size() - 1] = idx
            contador += 1

def guardar_informacion_produccion():
    seleccion = listbox.curselection()
    if seleccion:
        idx = seleccion[0]
        real_idx = indice_visible_a_real.get(idx)
        if real_idx is None:
            messagebox.showinfo("Error", "¡Seleccionar una variante válida!")
            return
        variante_mes = datos[real_idx][0]
        mes_estado = "H" if opcion_mes.get() == "MES Activado" else "D"
        tipo_prueba = "P" if opcion_prueba.get() == "Panel" else "U"
        informacion = f"{variante_mes} | {mes_estado} | {tipo_prueba}| {datos[real_idx][1]}"
        ruta_archivo = "C:/Agilent_ICT/boards/Subaru_T23/informacion_produccion.txt"
        with open(ruta_archivo, "w") as archivo:
            archivo.write(informacion)
        ventana.quit()
    else:
        messagebox.showinfo("Error", "¡Seleccionar variante!")

ventana = tk.Tk()
ventana.title("Seleccion Variante")
ancho_ventana = 800
alto_ventana = 700
centrar_ventana(ventana, ancho_ventana, alto_ventana)
ventana.attributes("-topmost", True)
datos = cargar_datos()
indice_visible_a_real = {i: i for i in range(len(datos))}
label_instrucciones = tk.Label(ventana, text="Seleccionar variante", font=("Arial", 16, "bold"), fg="blue")
label_instrucciones.pack(side=tk.TOP, pady=10)
frame_principal = tk.Frame(ventana)
frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
frame_listbox = tk.Frame(frame_principal)
frame_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
scrollbar = tk.Scrollbar(frame_listbox, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox = tk.Listbox(frame_listbox, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, font=("Arial", 14), width=50, height=20)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)
contador = 0
for idx, dato in enumerate(datos):
    if contador % 15 == 0 and contador != 0:
        listbox.insert(tk.END, "------------------------------------------------------------------")
        indice_visible_a_real[listbox.size() - 1] = None
    listbox.insert(tk.END, f"{idx + 1}.- {dato[0]}")
    indice_visible_a_real[listbox.size() - 1] = idx
    contador += 1
listbox.bind("<<ListboxSelect>>", actualizar_columnas)
frame_derecho = tk.Frame(frame_principal)
frame_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
label_mes = tk.Label(frame_derecho, text="Activar MES?", font=("Arial", 14, "bold"))
label_mes.pack(pady=10)
opcion_mes = tk.StringVar(value="MES Activado")
menu_mes = ttk.Combobox(frame_derecho, textvariable=opcion_mes, state="readonly", font=("Arial", 12))
menu_mes["values"] = ["MES Activado", "MES Desactivado"]
menu_mes.pack(pady=10)
label_tipo_prueba = tk.Label(frame_derecho, text="Tipo de prueba?", font=("Arial", 14, "bold"))
label_tipo_prueba.pack(pady=10)
opcion_prueba = tk.StringVar(value="Panel")
menu_prueba = ttk.Combobox(frame_derecho, textvariable=opcion_prueba, state="readonly", font=("Arial", 12))
menu_prueba["values"] = ["Panel", "Unidad Individual"]
menu_prueba.pack(pady=10)
boton_continuar = tk.Button(frame_derecho, text="CONTINUAR", font=("Arial", 16, "bold"), bg="green", fg="white", height=2, width=15, command=guardar_informacion_produccion)
boton_continuar.pack(pady=20)
label_buscar = tk.Label(frame_derecho, text="Ingresa la", font=("Arial", 10, "bold"))
label_buscar.pack(pady=1)
label_buscar = tk.Label(frame_derecho, text="variante a buscar", font=("Arial", 10, "bold"))
label_buscar.pack(pady=1)
entry_buscar = tk.Entry(frame_derecho, font=("Arial", 12))
entry_buscar.pack(pady=10)
entry_buscar.bind("<KeyRelease>", filtrar_variantes)
frame_info_ingenieria = tk.Frame(ventana)
frame_info_ingenieria.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
label_info = tk.Label(frame_info_ingenieria, text="Información material y equipo", font=("Arial", 10, "bold"))
label_info.pack(anchor="w")
label_variante = tk.Label(frame_info_ingenieria, text="Variante Equipo: N/A", font=("Arial", 10))
label_variante.pack(anchor="w")
label_subensamble = tk.Label(frame_info_ingenieria, text="Subensamble: N/A", font=("Arial", 10))
label_subensamble.pack(anchor="w")
ventana.mainloop()

#pyinstaller --onefile --windowed --icon=OIP.ico menu_v2.py
