#!/usr/bin/env python3
import sys
import os
import signal
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import BooleanVar, Checkbutton, ttk
import datetime

# ---------------------------------------------------------------------------
# Borrar archivo oculto al inicio
# ---------------------------------------------------------------------------
CACHE_FILE = os.path.join(os.path.dirname(__file__), ".cache_rutas.json")
if os.path.exists(CACHE_FILE):
    try:
        os.remove(CACHE_FILE)
        print(f"Archivo {CACHE_FILE} eliminado")
    except Exception as e:
        print(f"No se pudo eliminar {CACHE_FILE}: {e}")

# ---------------------------------------------------------------------------
# Importar utils_rutas plug-and-play
# ---------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils_rutas

# ---------------------------------------------------------------------------
# Importación de módulos principales
# ---------------------------------------------------------------------------
from config_proxy import cfg
from modificar_config import actualizar_configuracion
import lib_diana_tiro as libd
from system_utils import CaffeinateManager
from window_utils import WindowManager

# ---------------------------------------------------------------------------
# Variables globales
# ---------------------------------------------------------------------------
ruta_base_proyecto = utils_rutas.encontrar_directorio_base()
CONFIG_PATH = utils_rutas.buscar_path_fichero("conf_menu.json")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_APP_SH = utils_rutas.buscar_path_fichero("run_app.sh")
proc_map = {}  # guarda todos los procesos lanzados

# ---------------------------------------------------------------------------
# Caffeinate manager
# ---------------------------------------------------------------------------
caff_mgr = CaffeinateManager()
caff_mgr.start()  # inicia caffeinate

# ---------------------------------------------------------------------------
# Window manager
# ---------------------------------------------------------------------------
win_mgr = WindowManager(config_file=CONFIG_PATH, bloqueo=cfg.bloqueo_ventana)

# ---------------------------------------------------------------------------
# Inicializar ruta_logger con fallback
# ---------------------------------------------------------------------------
ruta_logger = utils_rutas.buscar_path_carpeta(cfg.carpeta_logger, create_if_missing=True)
if not ruta_logger:
    ruta_logger = os.path.join(SCRIPT_DIR, cfg.carpeta_logger)
    os.makedirs(ruta_logger, exist_ok=True)

# Borrar todos los logs antiguos al inicio
if os.path.isdir(ruta_logger):
    for fname in os.listdir(ruta_logger):
        if fname.endswith(".log"):
            try:
                os.remove(os.path.join(ruta_logger, fname))
            except Exception as e:
                print(f"No se pudo borrar {fname}: {e}")

# ---------------------------------------------------------------------------
# Función launch_app
# ---------------------------------------------------------------------------
def launch_app(py_script_path, key):
    if key in proc_map and proc_map[key].poll() is None:
        print(f"{key} ya está en ejecución")
        return

    log_file_path = None
    if getattr(cfg, "logger_prg", False):
        for fname in os.listdir(ruta_logger):
            if fname.startswith(f"{key}_") and fname.endswith(".log"):
                try:
                    os.remove(os.path.join(ruta_logger, fname))
                except Exception as e:
                    print(f"No se pudo borrar {fname}: {e}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(ruta_logger, f"{key}_{timestamp}.log")

    try:
        proc = subprocess.Popen(
            ["/bin/bash", RUN_APP_SH, py_script_path],
            cwd=SCRIPT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            preexec_fn=os.setsid
        )
        proc_map[key] = proc
        print(f"Lanzado {key} ({py_script_path})" + (f", log en {log_file_path}" if log_file_path else ""))

        q = queue.Queue()

        def enqueue_output(pipe):
            for line in iter(pipe.readline, ''):
                q.put(line)
            pipe.close()

        threading.Thread(target=enqueue_output, args=(proc.stdout,), daemon=True).start()

        def process_queue():
            if log_file_path:
                with open(log_file_path, 'a') as f:
                    while proc.poll() is None or not q.empty():
                        try:
                            line = q.get(timeout=0.1).rstrip()
                            f.write(line + "\n")
                            f.flush()
                        except queue.Empty:
                            continue
            else:
                while proc.poll() is None or not q.empty():
                    try:
                        line = q.get(timeout=0.1).rstrip()
                        print(f"[{key}] {line}")
                    except queue.Empty:
                        continue

        threading.Thread(target=process_queue, daemon=True).start()

    except Exception as e:
        print(f"Error lanzando {key}: {e}")

# ---------------------------------------------------------------------------
# Inicialización de ventana
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("Menu Tiro Laser")
win_mgr.load_window_config(root)
root.update_idletasks()
win_mgr.keep_window_in_screen(root)
root.resizable(True, True)
root.configure(bg="#2b2b2b")

# ---------------------------------------------------------------------------
# Creación de botones dinámicos usando programas_menu
# ---------------------------------------------------------------------------
BUTTON_GAP = 2
IPADY = 3
IPADX = 12
MAX_PER_ROW = 3

btn_bg, active_bg, fg_color = "#444444", "#666666", "white"

common_kwargs = dict(
    bg=btn_bg, fg=fg_color, font=("Arial", 12),
    cursor="hand2", bd=2, relief="raised",
    highlightthickness=0, highlightbackground=btn_bg, highlightcolor=active_bg,
    anchor="center"
)

button_frame = tk.Frame(root, bg="#2b2b2b")
button_frame.pack(pady=4, padx=(4, 0), anchor="w")

def make_launch_func(script_file, key):
    path = utils_rutas.buscar_path_fichero(script_file)
    def _launcher(event=None):
        if path:
            launch_app(path, key)
        else:
            print(f"No se encuentra el script {script_file}")
    return _launcher

# ---------------------------------------------------------------------------
# Separar programas normales de ocultos
# ---------------------------------------------------------------------------
normal_programs = []
hidden_programs = []

for btn_name, script_file in cfg.programas_menu.items():
    if btn_name.startswith("·"):
        hidden_programs.append((btn_name[1:], script_file))  # quitamos el "·"
    else:
        normal_programs.append((btn_name, script_file))

# Labels para programas normales
for i, (btn_name, script_file) in enumerate(normal_programs):
    key = btn_name.upper()
    lbl = tk.Label(button_frame, text=btn_name, **common_kwargs)
    lbl.grid(row=i // MAX_PER_ROW, column=i % MAX_PER_ROW,
             padx=BUTTON_GAP, pady=BUTTON_GAP, ipadx=IPADX, ipady=IPADY)

    lbl.bind("<Button-1>", make_launch_func(script_file, key))
    lbl.bind("<Enter>", lambda e, w=lbl: w.config(bg=active_bg))
    lbl.bind("<Leave>", lambda e, w=lbl: w.config(bg=btn_bg))

# ---------------------------------------------------------------------------
# Combo + botón alineados a la izquierda para programas ocultos
# ---------------------------------------------------------------------------
if hidden_programs:
    combo_frame = tk.Frame(button_frame, bg="#2b2b2b")
    last_row = (len(normal_programs) - 1) // MAX_PER_ROW + 1
    combo_frame.grid(row=last_row, column=0, columnspan=MAX_PER_ROW, pady=6, sticky="w")

    width_combo = 19
    width_btn = 2

    combo_values = [name for name, _ in hidden_programs]

    style = ttk.Style()
    style.theme_use('clam')  # Permite personalizar colores
    style.configure("Dark.TCombobox",
                    fieldbackground="#2b2b2b",
                    background="#2b2b2b",
                    foreground="white",
                    arrowcolor="white",
                    selectbackground="#2b2b2b",
                    selectforeground="#34E431",
                    bordercolor="#2b2b2b",
                    relief="flat")
    style.map("Dark.TCombobox",
              fieldbackground=[("readonly", "#2b2b2b")],
              background=[("readonly", "#2b2b2b")],
              foreground=[("readonly", "white")],
              selectbackground=[("readonly", "#2b2b2b")],
              selectforeground=[("readonly", "#34E431")])

    combo = ttk.Combobox(combo_frame,
                         values=combo_values,
                         state="readonly",
                         width=width_combo,
                         font=("Arial", 14),
                         style="Dark.TCombobox",
                         takefocus=0)
    combo.grid(row=0, column=0, padx=(0,1), pady=0)

    root.update()  # fuerza que el combo se vea al arrancar

    def launch_selected():
        sel = combo.get()
        if not sel:
            print("No hay programa seleccionado")
            return
        for name, script in hidden_programs:
            if name == sel:
                launch_app(utils_rutas.buscar_path_fichero(script), name.upper())
                break

    btn = tk.Label(combo_frame, text=">", width=width_btn,
                   bg=btn_bg, fg=fg_color, font=("Arial", 13),
                   relief="raised", bd=2, cursor="hand2")
    btn.grid(row=0, column=1, padx=(1,0))
    btn.bind("<Button-1>", lambda e: launch_selected())
    btn.bind("<Enter>", lambda e: btn.config(bg=active_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=btn_bg))

# ---------------------------------------------------------------------------
# Checkbuttons dinámicos
# ---------------------------------------------------------------------------
chek_user, var_chek_user, user_botones_objetos = [], [], []
prev_mapping, prev_values = {}, {}
FONDO_chek_user, CHECK_FONT = "#2b2b2b", ("Arial", 12)
COLOR_TEXT_CHECK, COLOR_TRUE, COLOR_FALSE = True, "#34E431", "#8F8F96"

user_button_frame = tk.Frame(root, bg="#2b2b2b")
user_button_frame.pack(side="left", padx=10, pady=5, anchor="nw")

def toggle_chek(i):
    var_name = var_chek_user[i]
    nuevo_estado = user_botones_objetos[i].var.get()
    setattr(cfg, var_name, nuevo_estado)
    actualizar_configuracion(var_name, nuevo_estado)
    prev_values[var_name] = nuevo_estado
    if COLOR_TEXT_CHECK:
        user_botones_objetos[i].config(fg=(COLOR_TRUE if nuevo_estado else COLOR_FALSE))

def recargar_chek_usuario():
    global chek_user, var_chek_user, user_botones_objetos
    for cb in user_botones_objetos:
        cb.destroy()
    user_botones_objetos.clear()
    chek_user = list(getattr(cfg, "chek_user", {}).keys())
    var_chek_user = list(getattr(cfg, "chek_user", {}).values())
    for i, texto in enumerate(chek_user):
        estado = getattr(cfg, var_chek_user[i], False)
        var_bool = BooleanVar(value=estado)
        fg_color = (COLOR_TRUE if estado else COLOR_FALSE) if COLOR_TEXT_CHECK else "white"
        cb = Checkbutton(
            user_button_frame, text=texto, variable=var_bool,
            onvalue=True, offvalue=False, bg=FONDO_chek_user,
            fg=fg_color, font=CHECK_FONT, anchor="w",
            selectcolor=FONDO_chek_user, activebackground="#666666",
            activeforeground="white", cursor="hand2"
        )
        cb.var = var_bool
        cb.config(command=lambda i=i: toggle_chek(i))
        cb.pack(pady=1, anchor="w", fill="x")
        user_botones_objetos.append(cb)
    snapshot_cfg()

def snapshot_cfg():
    global prev_mapping, prev_values
    prev_mapping = dict(getattr(cfg, "chek_user", {}))
    prev_values = {vn: getattr(cfg, vn, False) for vn in prev_mapping.values()}

REFRESH_MS = 1000
def vigilar_cambios():
    if hasattr(cfg, "chek_user"):
        new_mapping = dict(getattr(cfg, "chek_user", {}))
        if new_mapping != prev_mapping:
            recargar_chek_usuario()
        else:
            for i, var_name in enumerate(var_chek_user):
                nuevo_estado = getattr(cfg, var_name, False)
                if prev_values.get(var_name) != nuevo_estado:
                    user_botones_objetos[i].var.set(nuevo_estado)
                    if COLOR_TEXT_CHECK:
                        user_botones_objetos[i].config(fg=(COLOR_TRUE if nuevo_estado else COLOR_FALSE))
                    prev_values[var_name] = nuevo_estado
    root.after(REFRESH_MS, vigilar_cambios)

# ---------------------------------------------------------------------------
# Cierre limpio actualizado
# ---------------------------------------------------------------------------
def cerrar_gracefully(sig=None, frame=None):
    win_mgr.save_window_config(root)
    try:
        caff_mgr.stop()
    except Exception:
        pass

    for key, proc in proc_map.items():
        try:
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception as e:
            print(f"No se pudo cerrar {key}: {e}")

    root.destroy()
    sys.exit(0)

signal.signal(signal.SIGTERM, cerrar_gracefully)
signal.signal(signal.SIGINT, cerrar_gracefully)

# ---------------------------------------------------------------------------
# Inicialización final
# ---------------------------------------------------------------------------
recargar_chek_usuario()
snapshot_cfg()
vigilar_cambios()
root.after(100, lambda: win_mgr.keep_window_in_screen(root))
root.protocol("WM_DELETE_WINDOW", cerrar_gracefully)
root.mainloop()

