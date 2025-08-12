import os
from pathlib import Path
import tempfile
import shutil
import atexit
import logging

APP_DIR = Path(__file__).resolve().parent
APP_TEMP = APP_DIR / ".app_tmp"
APP_TEMP.mkdir(exist_ok=True)

try:
    APP_TEMP.chmod(0o700)
except Exception:
    pass

tempfile.tempdir = str(APP_TEMP)
os.environ["TEMP"] = str(APP_TEMP)
os.environ["TMP"] = str(APP_TEMP)

logging.getLogger().handlers.clear()
logging.getLogger().setLevel(logging.CRITICAL)

def _cleanup_temp():
    try:
        if APP_TEMP.exists() and APP_TEMP.is_dir():
            shutil.rmtree(APP_TEMP, ignore_errors=True)
    except Exception:
        pass

atexit.register(_cleanup_temp)
def _wipe_variable(name: str, namespace: dict):
    try:
        if name in namespace:
            namespace[name] = None
            del namespace[name]
    except Exception:
        pass

import customtkinter as ctk
import mysql.connector
import bcrypt
import threading
import time
import random
from pynput.mouse import Controller, Button
import keyboard
import sys
from datetime import datetime, date

DB_CONFIG = {
    "host": "141.11.34.87",
    "port": 3306,
    "user": "u1528_sHBQi5IXfd",
    "password": "rF67E.GJG9yBPirqnB@kxWpB",
    "database": "s1528_auto"
}

def conectar():
    return mysql.connector.connect(**DB_CONFIG)

def verificar_credenciales(usuario, password):
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT contraseña, rol, fecha_expiracion FROM usuarios WHERE nombre = %s",
            (usuario,))
        datos = cursor.fetchone()
        if not datos:
            return False, "Usuario no encontrado.", None

        stored_pass = datos.get("contraseña")
        rol = datos.get("rol", "user")
        fecha_exp = datos.get("fecha_expiracion")

        if fecha_exp:
            try:
                if isinstance(fecha_exp, str):
                    fecha_obj = datetime.strptime(fecha_exp.split(" ")[0], "%Y-%m-%d").date()
                else:
                    fecha_obj = fecha_exp
                if fecha_obj < date.today():
                    return False, "Cuenta expirada.", None
            except Exception:
                pass

        try:
            if isinstance(stored_pass, str):
                stored_bytes = stored_pass.encode("utf-8")
            else:
                stored_bytes = stored_pass
            password_bytes = password.encode("utf-8")
            if bcrypt.checkpw(password_bytes, stored_bytes):
                return True, "", rol
            else:
                return False, "Contraseña incorrecta.", None
        except Exception:
            if stored_pass == password:
                try:
                    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    cursor.execute("UPDATE usuarios SET contraseña = %s WHERE nombre = %s", (hashed, usuario))
                    conn.commit()
                    return True, "", rol
                except Exception:
                    return True, "", rol
            return False, "Contraseña incorrecta.", None
    except mysql.connector.Error as e:
        return False, f"Error MySQL: {e}", None
    except Exception as e:
        return False, f"Error: {e}", None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def crear_usuario(nombre, email, password, fecha_expiracion=None, rol="user"):
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, contraseña, rol, fecha_expiracion) VALUES (%s, %s, %s, %s, %s)",
            (nombre, email, hashed, rol, fecha_expiracion)
        )
        conn.commit()
        return True, "✅ Usuario creado correctamente."
    except mysql.connector.IntegrityError as e:
        return False, f"Error MySQL (integrity): {e}"
    except mysql.connector.Error as e:
        return False, f"Error MySQL: {e}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def abrir_admin():
    login_frame.pack_forget()
    admin_frame = ctk.CTkFrame(root)
    admin_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(admin_frame, text="Panel de Administración", font=("Arial", 18, "bold")).pack(pady=10)

    ctk.CTkLabel(admin_frame, text="Nuevo Usuario:").pack()
    entry_new_user = ctk.CTkEntry(admin_frame)
    entry_new_user.pack()

    ctk.CTkLabel(admin_frame, text="Email:").pack()
    entry_new_email = ctk.CTkEntry(admin_frame)
    entry_new_email.pack()

    ctk.CTkLabel(admin_frame, text="Contraseña:").pack()
    entry_new_pass = ctk.CTkEntry(admin_frame, show="*")
    entry_new_pass.pack()

    ctk.CTkLabel(admin_frame, text="Fecha Expiración (YYYY-MM-DD) opcional:").pack()
    entry_fecha = ctk.CTkEntry(admin_frame)
    entry_fecha.pack()

    ctk.CTkLabel(admin_frame, text="Rol:").pack()
    rol_var = ctk.StringVar(value="user")
    ctk.CTkOptionMenu(admin_frame, values=["user", "admin"], variable=rol_var).pack()

    lbl_admin_msg = ctk.CTkLabel(admin_frame, text="")
    lbl_admin_msg.pack(pady=5)

    def crear():
        u = entry_new_user.get().strip()
        e = entry_new_email.get().strip()
        p = entry_new_pass.get().strip()
        f = entry_fecha.get().strip()
        r = rol_var.get()

        if not u or not e or not p:
            lbl_admin_msg.configure(text="❌ Campos incompletos", text_color="red")
            return

        fecha_val = None
        if f:
            try:
                fecha_obj = datetime.strptime(f, "%Y-%m-%d").date()
                fecha_val = fecha_obj
            except Exception:
                lbl_admin_msg.configure(text="❌ Formato de fecha inválido", text_color="red")
                return

        ok, msg = crear_usuario(u, e, p, fecha_val, r)
        lbl_admin_msg.configure(text=msg, text_color="green" if ok else "red")

    ctk.CTkButton(admin_frame, text="Crear Usuario", command=crear).pack(pady=10)
    def volver():
        admin_frame.pack_forget()
        login_frame.pack(expand=True)
    ctk.CTkButton(admin_frame, text="Volver", command=volver).pack(pady=5)

def login():
    usuario = entry_user.get().strip()
    password = entry_pass.get().strip()

    if not usuario or not password:
        lbl_msg.configure(text="❌ Completa usuario y contraseña", text_color="red")
        return

    lbl_msg.configure(text="⏳ Verificando...", text_color="gray")

    def do_check():
        ok, mensaje, rol = verificar_credenciales(usuario, password)
        if ok:
            if rol == "admin":
                root.after(0, abrir_admin)
            else:
                root.after(0, abrir_autoclicker_safe)
        else:
            root.after(0, lambda: lbl_msg.configure(text=f"❌ {mensaje}", text_color="red"))

    threading.Thread(target=do_check, daemon=True).start()

def abrir_autoclicker_safe():
    login_frame.pack_forget()
    abrir_autoclicker()

def abrir_autoclicker():
    global toggle_key, running, mouse, cps_min_slider, cps_max_slider, cps_min_label, cps_max_label, key_label, key_entry, enabled, hotkey_handle, mode_var

    toggle_key = "x"
    enabled = False
    mouse = Controller()
    hotkey_handle = None
    mode_var = ctk.StringVar(value="Toggle")

    def click_loop():
        while True:
            try:
                cps_min_val = cps_min_slider.get()
                cps_max_val = cps_max_slider.get()
                if cps_min_val > cps_max_val:
                    cps_min_val, cps_max_val = cps_max_val, cps_min_val
                delay = 1 / random.uniform(max(1, cps_min_val), max(1, cps_max_val))

                if mode_var.get() == "Toggle":
                    if enabled:
                        mouse.click(Button.left)
                        time.sleep(delay)
                    else:
                        time.sleep(0.01)
                elif mode_var.get() == "Press":
                    if keyboard.is_pressed(toggle_key):
                        mouse.click(Button.left)
                        time.sleep(delay)
                    else:
                        time.sleep(0.01)
            except Exception:
                time.sleep(0.1)

    def toggle():
        global enabled
        enabled = not enabled
        root.after(0, lambda: key_label.configure(
            text=f"{toggle_key.upper()} (ACTIVO)" if enabled else f"{toggle_key.upper()} (INACTIVO)"
        ))

    def register_hotkey(key):
        global hotkey_handle
        try:
            if hotkey_handle is not None:
                try:
                    keyboard.remove_hotkey(hotkey_handle)
                except Exception:
                    keyboard.clear_all_hotkeys()
                    hotkey_handle = None
            if mode_var.get() == "Toggle":
                hotkey_handle = keyboard.add_hotkey(key, toggle)
        except Exception:
            pass

    def update_toggle_key():
        global toggle_key
        new_key = key_entry.get().strip().lower()
        key_entry.delete(0, "end")
        if not new_key:
            return
        toggle_key = new_key
        register_hotkey(toggle_key)
        key_label.configure(text=toggle_key.upper())

    def update_cps_labels(_=None):
        cps_min_label.configure(text=f"CPS Mínimo: {int(cps_min_slider.get())}")
        cps_max_label.configure(text=f"CPS Máximo: {int(cps_max_slider.get())}")

    frame_main = ctk.CTkFrame(root)
    frame_main.pack(fill="both", expand=True)

    ctk.CTkLabel(frame_main, text="PokkerClicker", font=("Arial", 18, "bold")).pack(pady=10)

    frame_toggle = ctk.CTkFrame(frame_main)
    frame_toggle.pack(pady=5)
    ctk.CTkLabel(frame_toggle, text="Tecla:").grid(row=0, column=0, padx=5)
    key_entry = ctk.CTkEntry(frame_toggle, width=50)
    key_entry.grid(row=0, column=1, padx=5)
    ctk.CTkButton(frame_toggle, text="Cambiar", command=update_toggle_key).grid(row=0, column=2, padx=5)

    # Nuevo: selector de modo
    ctk.CTkLabel(frame_toggle, text="Modo:").grid(row=1, column=0, padx=5, pady=5)
    ctk.CTkOptionMenu(frame_toggle, values=["Toggle", "Press"], variable=mode_var,
                      command=lambda _: register_hotkey(toggle_key)).grid(row=1, column=1, padx=5, pady=5)

    frame = ctk.CTkFrame(frame_main)
    frame.pack(pady=10)

    cps_min_slider = ctk.CTkSlider(frame, from_=1, to=30, number_of_steps=29, width=200, command=update_cps_labels)
    cps_min_slider.set(10)
    cps_min_slider.grid(row=0, column=0, padx=10, pady=5)
    cps_max_slider = ctk.CTkSlider(frame, from_=1, to=30, number_of_steps=29, width=200, command=update_cps_labels)
    cps_max_slider.set(15)
    cps_max_slider.grid(row=1, column=0, padx=10, pady=5)

    cps_min_label = ctk.CTkLabel(frame, text="CPS Mínimo: 10")
    cps_min_label.grid(row=0, column=1)
    cps_max_label = ctk.CTkLabel(frame, text="CPS Máximo: 15")
    cps_max_label.grid(row=1, column=1)

    frame_info = ctk.CTkFrame(frame_main)
    frame_info.pack(pady=5)
    ctk.CTkLabel(frame_info, text="Presiona ", font=("Arial", 12)).pack(side="left")
    key_label = ctk.CTkLabel(frame_info, text=f"{toggle_key.upper()}  (INACTIVO)", font=("Arial", 12, "bold"))
    key_label.pack(side="left")
    ctk.CTkLabel(frame_info, text=" para activar autoclick", font=("Arial", 12)).pack(side="left")

    update_cps_labels()
    register_hotkey(toggle_key)
    threading.Thread(target=click_loop, daemon=True).start()

localization_path = os.path.join(os.path.dirname(__file__), "localization")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS 
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# UI inicial
root = ctk.CTk()
root.title("PokkerClicker")
root.geometry("350x420")
root.iconbitmap(resource_path("icono.ico"))
root.resizable(False, False)

login_frame = ctk.CTkFrame(root)
login_frame.pack(expand=True)

ctk.CTkLabel(login_frame, text="Usuario:").pack(pady=5)
entry_user = ctk.CTkEntry(login_frame)
entry_user.pack()

ctk.CTkLabel(login_frame, text="Contraseña:").pack(pady=5)
entry_pass = ctk.CTkEntry(login_frame, show="*")
entry_pass.pack()

lbl_msg = ctk.CTkLabel(login_frame, text="")
lbl_msg.pack(pady=5)

ctk.CTkButton(login_frame, text="Iniciar sesión", command=login).pack(pady=10)

# ---------------------------------------------------------
# LIMPIEZAS FINALES (antes de salir definitivamente)
# ---------------------------------------------------------
def _on_exit_cleanup():
    try:
        _wipe_variable("DB_CONFIG", globals())
        _wipe_variable("entry_pass", globals())
        _wipe_variable("entry_user", globals())
    except Exception:
        pass
atexit.register(_on_exit_cleanup)

try:
    root.mainloop()
finally:
    _on_exit_cleanup()