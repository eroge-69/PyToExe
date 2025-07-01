import os
import sys
import ctypes
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, font, messagebox
from threading import Thread
import base64

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
DOMAIN_TO_BLOCK = "activate.api.stardock.net"
HOSTS_FILE_PATH = r"C:\Windows\System32\drivers\etc\hosts"
FENCES_CACHE_FILE = os.path.expandvars(r"%ProgramData%\Stardock\Fences6\Cache.dat")
BACKUP_FOLDER = os.path.expandvars(r"%USERPROFILE%\Documents\FencesBackup")
BACKUP_FILE_PATH = os.path.join(BACKUP_FOLDER, "Cache.dat.bak")

# ==============================================================================
# LÓGICA DE BACKEND (Las funciones que ya hemos creado)
# ==============================================================================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def stop_fences_processes(log_func):
    log_func("[*] Deteniendo procesos de Fences...")
    for process in ["Fences.exe", "FencesSrv.exe"]:
        result = os.system(f"taskkill /f /im {process} >nul 2>&1")
    log_func("    - Procesos detenidos.")

def save_trial_state(log_func):
    log_func("\n--- GUARDANDO ESTADO DEL TRIAL ---")
    if not os.path.exists(FENCES_CACHE_FILE):
        log_func("[!] ERROR: No se encontró 'Cache.dat'. Asegúrate de que Fences tenga un trial activo.")
        return
    try:
        os.makedirs(BACKUP_FOLDER, exist_ok=True)
        shutil.copy2(FENCES_CACHE_FILE, BACKUP_FILE_PATH)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_func(f"✅ ¡Éxito! Estado guardado en:\n   {BACKUP_FILE_PATH}")
        log_func(f"   Fecha del respaldo: {timestamp}")
    except Exception as e:
        log_func(f"[!] ERROR al guardar: {e}")

def restore_trial_state(log_func):
    log_func("\n--- RESTAURANDO ESTADO DEL TRIAL ---")
    if not os.path.exists(BACKUP_FILE_PATH):
        log_func("[!] ERROR: No se encontró un estado guardado ('Cache.dat.bak').")
        return
    stop_fences_processes(log_func)
    try:
        if os.path.exists(FENCES_CACHE_FILE):
            os.remove(FENCES_CACHE_FILE)
        shutil.copy2(BACKUP_FILE_PATH, FENCES_CACHE_FILE)
        log_func(f"✅ ¡Éxito! Estado restaurado desde:\n   {BACKUP_FILE_PATH}")
    except Exception as e:
        log_func(f"[!] ERROR al restaurar: {e}")

def modify_hosts_file(action, log_func):
    log_func(f"\n--- MODIFICANDO ARCHIVO HOSTS ({action.upper()}) ---")
    block_line = f"127.0.0.1    {DOMAIN_TO_BLOCK}"
    try:
        with open(HOSTS_FILE_PATH, 'r') as f:
            lines = f.readlines()
        
        filtered_lines = [l for l in lines if DOMAIN_TO_BLOCK not in l.lower() and "# bloqueo para stardock" not in l.lower()]
        
        if action == "block":
            log_func(f"[*] Bloqueando '{DOMAIN_TO_BLOCK}'...")
            filtered_lines.append(f"\n# Bloqueo para Stardock Fences (Toolkit)\n{block_line}\n")
            log_func("    - ¡Bloqueo aplicado!")
        else: # unblock
            log_func(f"[*] Desbloqueando '{DOMAIN_TO_BLOCK}'...")
            log_func("    - ¡Desbloqueo realizado!")
            
        with open(HOSTS_FILE_PATH, 'w') as f:
            f.writelines(filtered_lines)
    except Exception as e:
        log_func(f"[!] ERROR modificando hosts: {e}")

def check_block_status():
    try:
        with open(HOSTS_FILE_PATH, 'r') as f:
            return any(DOMAIN_TO_BLOCK in line and not line.strip().startswith('#') for line in f)
    except:
        return False

# ==============================================================================
# CLASE DE LA APLICACIÓN GRÁFICA (GUI)
# ==============================================================================

class FencesToolkitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fences Toolkit")
        self.geometry("500x550")
        self.resizable(False, False)
        self.configure(bg="#2E2E2E")

        # --- Estilos ---
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2E2E2E")
        self.style.configure("TLabel", background="#2E2E2E", foreground="#FFFFFF", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("TButton", background="#4A4A4A", foreground="#FFFFFF", borderwidth=0, focusthickness=0, padding=10)
        self.style.map("TButton", background=[("active", "#5A5A5A")])

        # --- Iconos (Base64) ---
        self.save_icon_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADKSURBVEhL7dOxCsJAFEXRk2gVLPwHW8E3sLDTy8baxtdQlO08goU3sLKy8A8sLMRSEIkkFC9CgqA4cMDBg38iB+49zCUoikmJicn/IZyRk7gR2Yk9kZ3Yk1gR2Yl9iRVRnYhP1EXqInURu4g9xF5iL7EXmYvMRWYj85G5yHxEHhIfkYfEQ+Ih8hB5iDxEHiIPkYfEY+Ix8Rh5jDxGHiMPEYeIw8Rh4jDxGHiMPEYeI48xx5gE5yJzEXlEHiIPkYfEY+IxcZn5iHwKZg9x/gN5lQAAAABJRU5ErkJggg==")
        self.restore_icon_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADsSURBVEhL7dOxCsJgEAXQk2gVLPwHW8E3sLDTy8baxtdQlO08goU3sLKy8A8sLMRSEIkkFC9CgqA4cMDBg38iB+49zCUoikmJicn/IZyRk7gR2Yk9kZ3Yk1gR2Yl9iRVRnYhP1EXqInURu4g9xF5iL7EXmYvMRWYj85G5yHxEHhIfkYfEQ+Ih8hB5iDxEHiIPkYfEY+Ix8Rh5jDxGHiMPEYeIw8Rh4jDxGHiMPEYeI48xx5gE5yJzEXlEHiIPkYfEY+IxcZn5iHwKZg9x/gM1QAAAABJRU5ErkJggg==")
        self.block_icon_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEASURBVEhL7dOxCsJgEAXQk2gVLPwHW8E3sLDTy8baxtdQlO08goU3sLKy8A8sLMRSEIkkFC9CgqA4cMDBg38iB+49zCUoikmJicn/IZyRk7gR2Yk9kZ3Yk1gR2Yl9iRVRnYhP1EXqInURu4g9xF5iL7EXmYvMRWYj85G5yHxEHhIfkYfEQ+Ih8hB5iDxEHiIPkYfEY+Ix8Rh5jDxGHiMPEYeIw8Rh4jDxGHiMPEYeI48xx5gE5yJzEXlEHiIPkYfEY+IxcZn5iHwKZg9x/gM1QAAAABJRU5ErkJggg==")
        self.unblock_icon_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADsSURBVEhL7dOxCsJgEAXQk2gVLPwHW8E3sLDTy8baxtdQlO08goU3sLKy8A8sLMRSEIkkFC9CgqA4cMDBg38iB+49zCUoikmJicn/IZyRk7gR2Yk9kZ3Yk1gR2Yl9iRVRnYhP1EXqInURu4g9xF5iL7EXmYvMRWYj85G5yHxEHhIfkYfEQ+Ih8hB5iDxEHiIPkYfEY+Ix8Rh5jDxGHiMPEYeIw8Rh4jDxGHiMPEYeI48xx5gE5yJzEXlEHiIPkYfEY+IxcZn5iHwKZg9x/gM1QAAAABJRU5ErkJggg==")

        self.save_icon = tk.PhotoImage(data=self.save_icon_data)
        self.restore_icon = tk.PhotoImage(data=self.restore_icon_data)
        self.block_icon = tk.PhotoImage(data=self.block_icon_data)
        self.unblock_icon = tk.PhotoImage(data=self.unblock_icon_data)

        self.create_widgets()
        self.update_status_display()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)

        # --- Título ---
        ttk.Label(main_frame, text="Fences Toolkit", style="Title.TLabel").pack(pady=(0, 20))

        # --- Sección de Estado del Trial ---
        trial_frame = ttk.Frame(main_frame, padding=10)
        trial_frame.pack(fill="x", pady=10)
        ttk.Label(trial_frame, text="Gestión del Estado del Trial", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        save_button = ttk.Button(trial_frame, text=" Guardar Estado", image=self.save_icon, compound="left", command=lambda: self.run_in_thread(save_trial_state))
        save_button.pack(fill="x", pady=5)
        
        restore_button = ttk.Button(trial_frame, text=" Restaurar Estado", image=self.restore_icon, compound="left", command=lambda: self.run_in_thread(restore_trial_state))
        restore_button.pack(fill="x", pady=5)

        # --- Sección de Red ---
        network_frame = ttk.Frame(main_frame, padding=10)
        network_frame.pack(fill="x", pady=10)
        ttk.Label(network_frame, text="Control de Red", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        block_button = ttk.Button(network_frame, text=" Bloquear Servidor", image=self.block_icon, compound="left", command=lambda: self.run_in_thread(modify_hosts_file, "block"))
        block_button.pack(fill="x", pady=5)

        unblock_button = ttk.Button(network_frame, text=" Desbloquear Servidor", image=self.unblock_icon, compound="left", command=lambda: self.run_in_thread(modify_hosts_file, "unblock"))
        unblock_button.pack(fill="x", pady=5)
        
        # --- Log de Actividad ---
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=(20, 0))
        ttk.Label(log_frame, text="Registro de Actividad:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.log_text = tk.Text(log_frame, height=8, bg="#1E1E1E", fg="#D4D4D4", relief="flat", font=("Consolas", 9), wrap="word")
        self.log_text.pack(fill="both", expand=True, pady=(5,0))
        self.log_text.configure(state="disabled")

    def log_to_status(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll
        self.log_text.configure(state="disabled")

    def run_in_thread(self, target_func, *args):
        # Ejecuta la lógica en un hilo separado para no congelar la GUI
        thread = Thread(target=target_func, args=(self.log_to_status, *args))
        thread.daemon = True
        thread.start()

    def update_status_display(self):
        self.log_to_status("--- ESTADO INICIAL ---")
        if check_block_status():
            self.log_to_status("[i] El servidor de Stardock está BLOQUEADO.")
        else:
            self.log_to_status("[i] El servidor de Stardock está DESBLOQUEADO.")
        
        if os.path.exists(BACKUP_FILE_PATH):
            mtime = os.path.getmtime(BACKUP_FILE_PATH)
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            self.log_to_status(f"[i] Se encontró un estado guardado del {date_str}.")
        else:
            self.log_to_status("[i] No se ha encontrado un estado guardado.")

# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
if __name__ == "__main__":
    if not is_admin():
        messagebox.showinfo("Permisos Requeridos", "Este programa necesita privilegios de Administrador para funcionar. Se reiniciará para solicitarlos.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = FencesToolkitApp()
        app.mainloop()
