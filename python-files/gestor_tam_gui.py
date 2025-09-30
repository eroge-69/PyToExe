import PySimpleGUI as sg
import pandas as pd
import datetime
import os

# Carpeta base para guardar el historial
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORIAL_FILE = os.path.join(BASE_DIR, "historial_intentos.csv")

# Cargar historial existente o crear uno nuevo
if os.path.exists(HISTORIAL_FILE):
    historial = pd.read_csv(HISTORIAL_FILE)
else:
    historial = pd.DataFrame(columns=["Case ID", "FechaHora", "Detalle"])

# Layout actualizado con filtro de equipo
layout = [
    [sg.Frame("📂 Sube la planilla semanal (Excel)", [
        [sg.FileBrowse("Seleccionar archivo", key="-FILE-", file_types=(("Excel Files", "*.xls;*.xlsx"),)), 
         sg.Button("Cargar Excel", key="-LOAD-")]
    ], expand_x=True)],

    [sg.Frame("📋 Casos cargados", [
        [sg.Text("Filtrar por Equipo:"), sg.Combo([], key="-EQUIPO-", enable_events=True, readonly=True, expand_x=True)],
        [sg.Listbox(values=[], size=(60, 10), key="-LIST-", expand_x=True, expand_y=True)]
    ], expand_x=True, expand_y=True)],

    [sg.Frame("📝 Registrar intento", [
        [sg.Text("Selecciona Case ID:"), sg.Combo([], key="-CASE-", size=(20,1), readonly=True, expand_x=True)],
        [sg.Text("Resultado del intento:")],
        [sg.Combo(["TAM aplicado", "Sin respuesta", "Teléfono fuera de servicio", "Número no existe", "Otro"], key="-RESULT-", size=(30,1))],
        [sg.Text("Detalle (solo si seleccionas Otro):"), sg.Input(key="-DETAIL-", size=(40,1))],
        [sg.Button("➕ Agregar intento"), sg.Button("Salir")]
    ], expand_x=True)],

    [sg.Frame("📊 Historial de intentos", [
        [sg.Listbox(values=[], size=(60, 10), key="-HIST-", expand_x=True, expand_y=True)]
    ], expand_x=True, expand_y=True)]
]

# Crear ventana
window = sg.Window("📞 Gestión de Intentos TAM", layout, resizable=True, finalize=True)

df_excel = None
df_filtrado = None

# Bucle de eventos
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Salir":
        break

    # Cargar Excel
    if event == "-LOAD-":
        file_path = values["-FILE-"]
        if file_path:
            try:
                df_excel = pd.read_excel(file_path)

                # Validaciones de columnas requeridas
                columnas_requeridas = ["Case ID", "End Collection", "Equipo"]
                for col in columnas_requeridas:
                    if col not in df_excel.columns:
                        sg.popup_error(f'El archivo Excel debe contener la columna "{col}"')
                        df_excel = None
                        continue

                # Convertir fechas y ordenar
                df_excel["End Collection"] = pd.to_datetime(df_excel["End Collection"], errors="coerce")
                df_excel = df_excel.sort_values(by="End Collection", ascending=True)

                # Poblar combo de equipos
                equipos = df_excel["Equipo"].dropna().unique().tolist()
                window["-EQUIPO-"].update(values=equipos, value=None)

                # Limpiar listas
                window["-LIST-"].update([])
                window["-CASE-"].update(values=[], value=None)

                sg.popup("✅ Excel cargado correctamente. Selecciona un equipo para ver los casos.")
            except Exception as e:
                sg.popup_error(f"Error al cargar Excel:\n{e}")

    # Filtrar por equipo seleccionado
    if event == "-EQUIPO-" and df_excel is not None:
        equipo_sel = values["-EQUIPO-"]
        if equipo_sel:
            df_filtrado = df_excel[df_excel["Equipo"] == equipo_sel]

            # Lista ordenada por End Collection
            case_list = df_filtrado["Case ID"].dropna().tolist()
            window["-LIST-"].update(case_list)
            window["-CASE-"].update(values=case_list, value=None)

    # Agregar intento
    if event == "➕ Agregar intento":
        case_id = values["-CASE-"]
        result = values["-RESULT-"]
        detail = values["-DETAIL-"].strip()

        if not case_id:
            sg.popup_error("Selecciona un Case ID antes de agregar un intento")
            continue
        if not result:
            sg.popup_error("Selecciona un resultado del intento")
            continue
        if result == "Otro" and not detail:
            sg.popup_error('Debes especificar un detalle para "Otro"')
            continue

        # Determinar detalle final
        final_detail = detail if result == "Otro" else result

        nuevo_intento = {
            "Case ID": case_id,
            "FechaHora": datetime.datetime.now().strftime("%d/%m %H:%M"),
            "Detalle": final_detail
        }

        historial = pd.concat([historial, pd.DataFrame([nuevo_intento])], ignore_index=True)
        historial.to_csv(HISTORIAL_FILE, index=False)

        # Actualizar historial en ventana
        historial_str = [f"{r['FechaHora']} | {r['Case ID']} | {r['Detalle']}" for idx, r in historial.iterrows()]
        window["-HIST-"].update(historial_str)

        # Limpiar selección
        window["-CASE-"].update(value=None)
        window["-RESULT-"].update(value=None)
        window["-DETAIL-"].update(value="")
        sg.popup("✅ Intento agregado correctamente")

window.close()
