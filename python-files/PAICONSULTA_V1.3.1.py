import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import requests
import json
import os
import csv
import pandas as pd
import threading
import queue
from datetime import datetime
import concurrent.futures
from threading import Lock
import re  # Importamos el módulo re para sanitizar los nombres de archivos

#Compilar código generar .exe
#python -m PyInstaller --onefile --noconsole PAICONSULTA_V1.3.1.py

# Deshabilitar advertencias de solicitudes inseguras (opcional)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Función para sanitizar nombres de archivos
def sanitize_filename(filename):
    # Reemplazar caracteres inválidos en nombres de archivos por guiones bajos
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Variables globales para los nombres de los archivos CSV
csv_filename = None
csv_filename2 = None
indice_progreso_filename = None

# Variable global para el temporizador
timer_id = None

# Crear una cola para comunicación entre hilos
message_queue = queue.Queue()

# Evento para detener el proceso
stop_event = threading.Event()

# Variable para almacenar el nombre del archivo Excel
excel_filename = None

# Lock para proteger la escritura en archivos
lock = Lock()

# Mapeo de opciones a vacunas y dosis
# Mapeo de opciones a vacunas y dosis con el nuevo formato
opciones_vacunas = {
    '1 -- BCG (Única)': {'biologico': 'BCG', 'dosis': 'Única'},
    '2 -- DPT Segundo (Refuerzo)': {'biologico': 'DPT', 'dosis': 'Segundo Refuerzo'},
    '3 -- Fiebre Amarilla (Única)': {'biologico': 'Fiebre Amarilla', 'dosis': 'Única'},
    '4 -- Pentavalente PAI (Primera)': {'biologico': 'Pentavalente PAI', 'dosis': 'Primera'},
    '5 -- Pentavalente PAI (Segunda)': {'biologico': 'Pentavalente PAI', 'dosis': 'Segunda'},
    '6 -- Pentavalente PAI (Tercera)': {'biologico': 'Pentavalente PAI', 'dosis': 'Tercera'},
    '7 -- Pentavalente PAI (Primer Refuerzo)': {'biologico': 'Pentavalente PAI', 'dosis': 'Primer Refuerzo'},
    '8 -- Rotavirus (Primera)': {'biologico': 'Rotavirus', 'dosis': 'Primera'},
    '9 -- Rotavirus (Segunda)': {'biologico': 'Rotavirus', 'dosis': 'Segunda'},
    '10 - Sarampión - Rubéola (Adicional)': {'biologico': 'Sarampión - Rubéola', 'dosis': 'Adicional'},
    '11 - Triple Viral (Primera)': {'biologico': 'Triple Viral', 'dosis': 'Primera'},
    '12 - Triple Viral (Refuerzo)': {'biologico': 'Triple Viral', 'dosis': 'Refuerzo'},
    '13 - VPH (Única)': {'biologico': 'VPH', 'dosis': 'Única'},
    '14 - VPH (Primera)': {'biologico': 'VPH', 'dosis': 'Primera'},    
    '15 - TdaP Acelular Gestante (Anual)': {'biologico': 'TdaP Acelular Gestante', 'dosis': 'Anual'},    
    '16 - COVID PFIZER JN1 (Adicional)': {'biologico': 'COVID PFIZER JN1', 'dosis': 'Adicional'},    
    '17 - INFLUENZA TRIVALENTE ADULTOS (Anual)': {'biologico': 'INFLUENZA TRIVALENTE ADULTOS', 'dosis': 'Anual'},
    '18 - Fiebre amarilla particular (Única)': {'biologico': 'Fiebre amarilla particular', 'dosis': 'Única'}
}


def parse_fecha(fecha_str):
    formatos = ['%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Fecha '{fecha_str}' no tiene un formato reconocido")

def obtener_token(programmatic=False):
    usuario = entry_usuario.get().strip()
    contrasena = entry_contrasena.get().strip()

    if not usuario or not contrasena:
        if not programmatic:
            text_resultado.delete('1.0', tk.END)
            text_resultado.insert(tk.END, "Por favor, ingresa el usuario y la contraseña.\n")
        return

    url_auth = 'https://paiwebservices.paiweb.gov.co:8081/api/Login'

    payload = {
        "tipoIdentificacion": "CC",
        "Identificacion": usuario,
        "Password": contrasena,
        "TokenReCaptcha": None,
        "Codigo": None
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(url_auth, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            resultado = response.json()
            bearer_token = resultado.get('token')
            if bearer_token:
                entry_token.delete(0, tk.END)
                entry_token.insert(0, bearer_token)
                if not programmatic:
                    text_resultado.delete('1.0', tk.END)
                    text_resultado.insert(tk.END, "Autenticación exitosa. Token obtenido.\n")
                if not programmatic:
                    programar_actualizacion_token()
                actualizar_tiempo_restante(TIEMPO_TOKEN)
            else:
                if not programmatic:
                    text_resultado.delete('1.0', tk.END)
                    text_resultado.insert(tk.END, "No se pudo obtener el token de autenticación.\n")
        else:
            if not programmatic:
                text_resultado.delete('1.0', tk.END)
                text_resultado.insert(tk.END, f"Error en la autenticación: Código {response.status_code}\n")
                text_resultado.insert(tk.END, response.text + "\n")
    except requests.exceptions.RequestException as e:
        if not programmatic:
            text_resultado.delete('1.0', tk.END)
            text_resultado.insert(tk.END, f"Excepción al realizar la autenticación: {e}\n")

def programar_actualizacion_token():
    obtener_token(programmatic=True)
    root.after(REFRESCO_TOKEN_MS, programar_actualizacion_token)

def actualizar_tiempo_restante(segundos):
    global timer_id
    if timer_id is not None:
        root.after_cancel(timer_id)
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    label_tiempo_restante.config(text=f"Tiempo hasta que el token caduque: {minutos:02d}:{segundos_restantes:02d}")
    if segundos > 0:
        timer_id = root.after(1000, actualizar_tiempo_restante, segundos - 1)
    else:
        obtener_token(programmatic=True)
        actualizar_tiempo_restante(TIEMPO_TOKEN)

def consulta_por_identificacion(numero_identificacion, bearer_token, fecha_nacimiento):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    url = 'https://paiwebservices.paiweb.gov.co:8081/api/v2/Paciente/GetList'

    payload = {
        "size": 10,
        "totalElements": 0,
        "totalPages": 0,
        "pageNumber": 0,
        "data": {
            "numeroIdentificacion": numero_identificacion,
            "tipoDocumento": {},
            "numeroIdentificacionCuidador": "",
            "type": "basic"
        }
    }

    data = json.dumps(payload)

    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        if response.status_code == 200:
            resultado = response.json()
            total_elements = resultado.get('totalElements', 0)

            if total_elements == 1:
                paciente_data = resultado.get('data', [])
                if paciente_data and isinstance(paciente_data, list):
                    paciente = paciente_data[0]
                    paciente_id = paciente.get('pacienteId')
                    if paciente_id:
                        return procesar_paciente(numero_identificacion, paciente_id, headers)
                    else:
                        return {'error': "No se pudo obtener el pacienteId de la respuesta.", 'numero_identificacion': numero_identificacion}
                else:
                    return {'error': "La estructura de los datos no es la esperada.", 'numero_identificacion': numero_identificacion}
            elif total_elements >= 2:
                paciente_data = resultado.get('data', [])
                if paciente_data and isinstance(paciente_data, list):
                    # Convertir fecha_nacimiento de Excel a datetime
                    try:
                        fecha_nacimiento_excel_dt = parse_fecha(fecha_nacimiento)
                    except ValueError as ve:
                        return {'error': str(ve), 'numero_identificacion': numero_identificacion}

                    # Buscar el paciente que coincida con la fecha de nacimiento
                    paciente_encontrado = None
                    for paciente in paciente_data:
                        fecha_nacimiento_api = paciente.get('fechaNacimiento', '')
                        if fecha_nacimiento_api:
                            try:
                                fecha_nacimiento_api_dt = parse_fecha(fecha_nacimiento_api)
                            except ValueError:
                                continue  # Si el formato es incorrecto, continuar con el siguiente

                            if fecha_nacimiento_excel_dt.date() == fecha_nacimiento_api_dt.date():
                                paciente_encontrado = paciente
                                break  # Salir del bucle al encontrar coincidencia

                    if paciente_encontrado:
                        paciente_id = paciente_encontrado.get('pacienteId')
                        if paciente_id:
                            return procesar_paciente(numero_identificacion, paciente_id, headers)
                        else:
                            return {'error': "No se pudo obtener el pacienteId de la respuesta.", 'numero_identificacion': numero_identificacion}
                    else:
                        # No se encontró coincidencia en fecha de nacimiento
                        with lock:
                            with open(csv_filename2, mode='a', newline='', encoding='utf-8-sig') as file:
                                writer = csv.writer(file)
                                writer.writerow([numero_identificacion, 'No se encontró coincidencia en fecha de nacimiento'])
                        return {'error': f"No se encontró coincidencia en fecha de nacimiento para el usuario con documento {numero_identificacion}. Registrado en {csv_filename2}.", 'numero_identificacion': numero_identificacion}
                else:
                    return {'error': "La estructura de los datos no es la esperada.", 'numero_identificacion': numero_identificacion}
            else:
                return {'error': "No se encontraron registros para este número de identificación.", 'numero_identificacion': numero_identificacion}
        elif response.status_code == 401:
            try:
                error_response = response.json()
                if error_response.get('status') == 'Error' and error_response.get('message') == 'No Auth':
                    return {'error': "El token ha vencido. Por favor, ingresa un nuevo token.", 'numero_identificacion': numero_identificacion}
                else:
                    return {'error': "Error de autenticación: Token inválido o vencido.", 'numero_identificacion': numero_identificacion}
            except json.JSONDecodeError:
                return {'error': "Error de autenticación: Token inválido o vencido.", 'numero_identificacion': numero_identificacion}
        else:
            return {'error': f"Error en la solicitud: Código {response.status_code}", 'numero_identificacion': numero_identificacion}
    except requests.exceptions.RequestException as e:
        return {'error': f"Excepción al realizar la solicitud: {e}", 'numero_identificacion': numero_identificacion}

def procesar_paciente(numero_identificacion, paciente_id, headers):
    seleccion = combo_opciones.get()
    vacuna_dosis = opciones_vacunas.get(seleccion, {})
    biologico_objetivo = vacuna_dosis.get('biologico', '')
    dosis_objetivo = vacuna_dosis.get('dosis', '')

    url_encabezado = f'https://paiwebservices.paiweb.gov.co:8081/api/resumen/paciente/{paciente_id}/aplicaciones'
    response_encabezado = requests.get(url_encabezado, headers=headers, verify=False)
    if response_encabezado.status_code == 200:
        resultado_encabezado = response_encabezado.json()

        fecha_aplicacion_vacuna = 'no se encontró'
        ips_vacunadora = 'no se encontró'

        if isinstance(resultado_encabezado, list):
            for aplicacion in resultado_encabezado:
                nombre_vacuna = aplicacion.get('biologico', '')
                dosis = aplicacion.get('dosis', '')
                fecha_aplicacion = aplicacion.get('fechaAplicacion', '')
                ips = aplicacion.get('institucionVacunadora', '')

                # Modificar fechaAplicacion para eliminar la hora
                if fecha_aplicacion:
                    fecha_aplicacion = fecha_aplicacion.split('T')[0]

                if nombre_vacuna == biologico_objetivo and dosis == dosis_objetivo:
                    fecha_aplicacion_vacuna = fecha_aplicacion
                    ips_vacunadora = ips
                    break  # Encontramos la vacuna deseada, salimos del bucle
        else:
            message_queue.put("La estructura de resultado_encabezado no es una lista.\n")

        return {
            'numero_identificacion': numero_identificacion,
            'consulta': seleccion,
            'resultado': 'Usuario encontrado en PAIWEB',
            'fecha_aplicacion': fecha_aplicacion_vacuna,
            'ips_vacunadora': ips_vacunadora
        }
    else:
        return {'error': f"Error en la segunda solicitud: Código {response_encabezado.status_code}", 'numero_identificacion': numero_identificacion}

def realizar_consulta():
    bearer_token = entry_token.get().strip()
    numero_identificacion = entry_identificacion.get().strip()
    fecha_nacimiento = entry_fecha_nacimiento.get().strip()

    if not bearer_token or not numero_identificacion or not fecha_nacimiento:
        text_resultado.delete('1.0', tk.END)
        text_resultado.insert(tk.END, "Por favor, ingresa el Bearer Token, el número de identificación y la fecha de nacimiento.\n")
        return

    # Actualizar los nombres de archivo antes de la consulta individual
    update_filenames()

    result = consulta_por_identificacion(numero_identificacion, bearer_token, fecha_nacimiento)

    text_resultado.delete('1.0', tk.END)

    if 'error' in result:
        text_resultado.insert(tk.END, result['error'] + "\n")
    else:
        text_resultado.insert(tk.END, f"Datos para el número de identificación {numero_identificacion}:\n")
        text_resultado.insert(tk.END, json.dumps(result, indent=4, ensure_ascii=False) + "\n")

        with lock:
            with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([
                    numero_identificacion,
                    result['consulta'],
                    result['resultado'],
                    result['fecha_aplicacion'],
                    result['ips_vacunadora']
                ])

def cargar_excel():
    global excel_filename
    excel_filename = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=(("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*"))
    )
    if excel_filename:
        message_queue.put(f"Archivo Excel seleccionado: {excel_filename}\n")
    else:
        message_queue.put("No se seleccionó ningún archivo.\n")

def procesar_numero_identificacion(index, numero_identificacion, bearer_token, total_rows, fecha_nacimiento):
    if stop_event.is_set():
        return

    message_queue.put(f"Procesando número de identificación {numero_identificacion} ({index + 1}/{total_rows})\n")

    result = consulta_por_identificacion(numero_identificacion, bearer_token, fecha_nacimiento)

    if 'error' in result:
        message_queue.put(f"Error: {result['error']}\n")
        with lock:
            with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([
                    numero_identificacion,
                    '',
                    result['error'],
                    '',
                    ''
                ])
    else:
        with lock:
            with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([
                    numero_identificacion,
                    result['consulta'],
                    result['resultado'],
                    result['fecha_aplicacion'],
                    result['ips_vacunadora']
                ])

    # Guardar el índice de progreso
    with lock:
        with open(indice_progreso_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow([index + 1])

def procesar_excel():
    bearer_token = entry_token.get().strip()

    if not bearer_token:
        text_resultado.insert(tk.END, "Por favor, ingresa el Bearer Token.\n")
        return

    if not excel_filename:
        text_resultado.insert(tk.END, "Por favor, carga un archivo Excel antes de iniciar el proceso.\n")
        return

    # Actualizar los nombres de los archivos según la selección actual
    update_filenames()

    # Crear los archivos CSV si no existen
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['Numero de Documento', 'Consulta', 'Resultado', 'Fecha Aplicación', 'IPS Vacunadora'])

    if not os.path.exists(csv_filename2):
        with open(csv_filename2, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['Numero de Documento', 'Descripción'])

    stop_event.clear()
    boton_iniciar_proceso.config(state=tk.DISABLED)
    # Deshabilitar el combobox
    combo_opciones.config(state='disabled')
    threading.Thread(target=procesar_excel_thread, args=(bearer_token,)).start()

def procesar_excel_thread(bearer_token):
    global excel_filename
    if not excel_filename:
        message_queue.put("No se seleccionó ningún archivo.\n")
        root.after(0, boton_iniciar_proceso.config, {'state': tk.NORMAL})
        root.after(0, combo_opciones.config, {'state': 'normal'})
        return

    try:
        df = pd.read_excel(excel_filename)
    except Exception as e:
        message_queue.put(f"Error al leer el archivo Excel: {e}\n")
        root.after(0, boton_iniciar_proceso.config, {'state': tk.NORMAL})
        root.after(0, combo_opciones.config, {'state': 'normal'})
        return

    if 'numero_documento' not in df.columns or 'fecha_nacimiento' not in df.columns:
        message_queue.put("El archivo Excel debe contener las columnas 'numero_documento' y 'fecha_nacimiento'\n")
        root.after(0, boton_iniciar_proceso.config, {'state': tk.NORMAL})
        root.after(0, combo_opciones.config, {'state': 'normal'})
        return

    # Convertir la columna 'fecha_nacimiento' a string
    df['fecha_nacimiento'] = df['fecha_nacimiento'].astype(str)

    # Leer el índice de progreso si existe
    inicio = 0
    if os.path.exists(indice_progreso_filename):
        with open(indice_progreso_filename, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    inicio = int(row[0])
                    message_queue.put(f"Reanudando desde el índice {inicio}\n")
                    break

    total_rows = len(df)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for index, row in df.iloc[inicio:].iterrows():
            if stop_event.is_set():
                message_queue.put("El proceso ha sido detenido.\n")
                break

            numero_identificacion = str(row['numero_documento']).strip()
            fecha_nacimiento = str(row['fecha_nacimiento']).strip()
            future = executor.submit(procesar_numero_identificacion, index, numero_identificacion, bearer_token, total_rows, fecha_nacimiento)
            futures.append(future)

        # Esperar a que todos los futuros se completen
        concurrent.futures.wait(futures)

    message_queue.put(f"Proceso completado. Los resultados se han guardado en '{csv_filename}'.\n")
    root.after(0, boton_iniciar_proceso.config, {'state': tk.NORMAL})
    # Rehabilitar el combobox
    root.after(0, combo_opciones.config, {'state': 'normal'})

def detener_proceso():
    stop_event.set()
    message_queue.put("Proceso detenido por el usuario.\n")
    # Rehabilitar el combobox
    combo_opciones.config(state='normal')
    boton_iniciar_proceso.config(state=tk.NORMAL)

def borrar_token():
    global timer_id
    entry_token.delete(0, tk.END)
    if timer_id is not None:
        root.after_cancel(timer_id)
        timer_id = None
    label_tiempo_restante.config(text="Tiempo hasta que el token caduque: --:--")

def procesar_cola_mensajes():
    try:
        while True:
            message = message_queue.get_nowait()
            text_resultado.insert(tk.END, message)
            text_resultado.see(tk.END)
    except queue.Empty:
        pass
    root.after(100, procesar_cola_mensajes)

def update_filenames():
    global csv_filename, csv_filename2, indice_progreso_filename
    seleccion = combo_opciones.get()
    sanitized_seleccion = sanitize_filename(seleccion)
    csv_filename = f'resultados_{sanitized_seleccion}.csv'
    csv_filename2 = f'documentos_mas_de_dos_veces_{sanitized_seleccion}.csv'
    indice_progreso_filename = f'indice_progreso_{sanitized_seleccion}.csv'

# Constantes para el tiempo de vida del token
TIEMPO_TOKEN = 59 * 60
REFRESCO_TOKEN_MS = TIEMPO_TOKEN * 1000

# Configuración de la ventana principal
root = tk.Tk()
root.title("PAICONSULTA V1.3.1")
root.geometry("550x650")  # Ajustar altura para acomodar nuevos widgets

# Frame para los campos de entrada
frame_entrada = ttk.Frame(root, padding="10")
frame_entrada.pack(fill=tk.X)

# Etiqueta y campo para el Usuario
label_usuario = ttk.Label(frame_entrada, text="Usuario:")
label_usuario.grid(row=0, column=0, sticky='w')
entry_usuario = ttk.Entry(frame_entrada, width=80)
entry_usuario.grid(row=1, column=0, columnspan=2, pady=5)

# Etiqueta y campo para la Contraseña
label_contrasena = ttk.Label(frame_entrada, text="Contraseña:")
label_contrasena.grid(row=2, column=0, sticky='w')
entry_contrasena = ttk.Entry(frame_entrada, width=80, show="*")
entry_contrasena.grid(row=3, column=0, columnspan=2, pady=5)

# Botones para obtener y borrar el token en dos columnas
boton_obtener_token = ttk.Button(frame_entrada, text="Obtener Token", command=obtener_token)
boton_obtener_token.grid(row=4, column=0, pady=5)
boton_borrar_token = ttk.Button(frame_entrada, text="Borrar Token", command=borrar_token)
boton_borrar_token.grid(row=4, column=1, pady=5)

# Etiqueta y campo para el Bearer Token
label_token = ttk.Label(frame_entrada, text="Bearer Token:")
label_token.grid(row=5, column=0, sticky='w')
entry_token = ttk.Entry(frame_entrada, width=80)
entry_token.grid(row=6, column=0, columnspan=2, pady=5)

""" # Etiqueta y campo para el Número de Identificación
label_identificacion = ttk.Label(frame_entrada, text="Número de Identificación:")
label_identificacion.grid(row=7, column=0, sticky='w')
entry_identificacion = ttk.Entry(frame_entrada, width=30)
entry_identificacion.grid(row=8, column=0, columnspan=2, pady=5)

# Etiqueta y campo para la Fecha de Nacimiento
label_fecha_nacimiento = ttk.Label(frame_entrada, text="Fecha de Nacimiento (dd/mm/yyyy):")
label_fecha_nacimiento.grid(row=9, column=0, sticky='w')
entry_fecha_nacimiento = ttk.Entry(frame_entrada, width=30)
entry_fecha_nacimiento.grid(row=10, column=0, columnspan=2, pady=5) """

# Etiqueta y ComboBox para seleccionar la consulta
label_opciones = ttk.Label(frame_entrada, text="Seleccione la consulta:")
label_opciones.grid(row=11, column=0, sticky='w')
combo_opciones = ttk.Combobox(frame_entrada, values=list(opciones_vacunas.keys()), state="readonly", width=80)
combo_opciones.grid(row=12, column=0, columnspan=2, pady=5)
combo_opciones.current(0)  # Seleccionar la primera opción por defecto

# Frame para los botones organizados en dos columnas
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=5)

# Botones organizados en dos columnas
boton_cargar_excel = ttk.Button(frame_botones, text="Cargar Excel", command=cargar_excel)
boton_cargar_excel.grid(row=0, column=0, padx=5, pady=5)

boton_iniciar_proceso = ttk.Button(frame_botones, text="Iniciar Proceso", command=procesar_excel)
boton_iniciar_proceso.grid(row=0, column=1, padx=5, pady=5)

boton_detener_proceso = ttk.Button(frame_botones, text="Detener Proceso", command=detener_proceso)
boton_detener_proceso.grid(row=1, column=0, padx=5, pady=5)

boton_consultar = ttk.Button(frame_botones, text="Consultar Individual", command=realizar_consulta)
boton_consultar.grid(row=1, column=1, padx=5, pady=5)
boton_consultar.config(state=tk.DISABLED)

# Etiqueta para el temporizador
label_tiempo_restante = ttk.Label(root, text="Tiempo hasta que el token caduque: --:--", font=("Helvetica", 12))
label_tiempo_restante.pack(pady=5)

# Campo de texto para mostrar los resultados
label_resultado = ttk.Label(root, text="Resultado de la API:")
label_resultado.pack(anchor='w', padx=10)

text_resultado = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
text_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Iniciar la verificación de la cola de mensajes
procesar_cola_mensajes()

root.mainloop()
