import time
import requests
import json
import subprocess
import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import glob
from bs4 import BeautifulSoup  # Nueva dependencia para parsear HTML

COOKIES_FILE = "cookies.txt"
USERS_FILE = "users.json"
BASE_PATH = r"C:\Users\crizs\Desktop"
CHROME_HEADLESS_SHELL_PATH = r"C:\Users\crizs\Documents\tiktok_live\chrome-headless-shell-win64\chrome-headless-shell.exe"  # Nueva ruta

def get_room_id_with_headless_shell(username: str, headless_shell_path: str, log_queue) -> str:
    """
    Obtiene el room_id de un usuario en vivo usando chrome-headless-shell.
    """
    # Verificar que chrome-headless-shell existe
    if not os.path.exists(headless_shell_path):
        raise Exception(f"❌ chrome-headless-shell no encontrado en: {headless_shell_path}")

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    
    try:
        log_queue.put(f"🔍 Conectando al livestream de @{username} para obtener room_id...")
        # Comando para chrome-headless-shell
        cmd = [
            headless_shell_path,
            "--headless=new",
            "--disable-gpu",
            "--dump-dom",
            f"--user-agent={user_agent}",
            f"https://www.tiktok.com/@{username}/live"
        ]
        # Ejecutar el comando y capturar el HTML desde stdout
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10  # Aumentado a 10s para mayor estabilidad
        )
        
        # Verificar si hubo error en la ejecución
        if process.returncode != 0:
            raise Exception(f"❌ Error al ejecutar chrome-headless-shell: {process.stderr}")
        
        # Obtener el HTML desde stdout
        html_content = process.stdout
        if not html_content.strip():
            raise Exception(f"❌ No se obtuvo contenido HTML para @{username}. Posible bloqueo o página vacía.")
        
        # Parsear el HTML para encontrar SIGI_STATE
        soup = BeautifulSoup(html_content, 'html.parser')
        sigi_element = soup.find('script', id='SIGI_STATE')
        if not sigi_element:
            raise Exception(f"❌ No se encontró el elemento SIGI_STATE para @{username}. Posible cambio en la página.")
        
        # Extraer y parsear el JSON
        payload = json.loads(sigi_element.text)
        room_id = (
            payload
            .get("LiveRoom", {})
            .get("liveRoomUserInfo", {})
            .get("user", {})
            .get("roomId")
        )
        if not room_id:
            raise Exception(f"❌ @{username} no está en vivo o no se encontró roomId.")
        
        log_queue.put(f"✅ ROOM_ID para @{username}: {room_id}")
        return room_id
    
    except Exception as e:
        log_queue.put(f"🚫 Error detallado: {str(e)}")
        raise Exception(f"🚫 Error al obtener room_id para @{username}: {str(e)}")

def get_room_id_from_user(username, cookies, log_queue):
    """
    Wrapper para obtener el room_id usando chrome-headless-shell.
    Cookies se ignoran ya que no se necesitan para obtener el room_id.
    """
    try:
        return get_room_id_with_headless_shell(username, CHROME_HEADLESS_SHELL_PATH, log_queue)
    except Exception as e:
        raise e

# Resto del script permanece igual...

def validate_hls_url(hls_url, log_queue):
    """
    Valida si la URL HLS es accesible antes de iniciar la grabación.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.head(hls_url, headers=headers, timeout=10)
        if response.status_code == 200:
            log_queue.put(f"✅ URL HLS válida: {hls_url}")
            return True
        else:
            log_queue.put(f"❌ URL HLS no accesible (código {response.status_code}): {hls_url}")
            return False
    except requests.RequestException as e:
        log_queue.put(f"🚫 Error al validar URL HLS: {str(e)}")
        return False

def get_hls_url(room_id, log_queue):
    """
    Obtiene la URL del stream HLS desde la API de TikTok.
    """
    api_url = f"https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id={room_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        hls_url = data.get("data", {}).get("stream_url", {}).get("hls_pull_url")
        if not hls_url:
            raise Exception("❌ No se encontró la URL HLS.")
        if validate_hls_url(hls_url, log_queue):
            return hls_url
        else:
            raise Exception("❌ La URL HLS no es accesible.")
    except requests.RequestException as e:
        raise Exception(f"🚫 Error al obtener la URL HLS: {str(e)}")

def start_ffmpeg_recording(url, username, log_queue, notification_queue, status_queue, tiempo_inactividad=25, chequeo_cada=10):
    """
    Inicia la grabación del stream en formato .ts usando FFmpeg y monitorea la inactividad.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    user_dir = os.path.join(BASE_PATH, username)
    output_file = os.path.join(user_dir, f"{username}_{timestamp}_live.ts")
    log_queue.put(f"🎬 Iniciando grabación para {username} en: {output_file}")
    
    cmd = [
        "ffmpeg",
        "-rw_timeout", "20000000",       
        "-thread_queue_size", "1024",    
        "-analyzeduration", "5000000",  
        "-i", url,
        "-bufsize", "8000k",             
        "-sn",                           
        "-dn",                           
        "-reconnect_delay_max", "25",    
        "-reconnect_streamed",           
        "-reconnect_at_eof",             
        "-max_muxing_queue_size", "1024",
        "-correct_ts_overflow", "1",     
        "-c:v", "copy",                  
        "-c:a", "copy",                  
        "-map", "0",                      
        output_file
    ]
    
    os.makedirs(user_dir, exist_ok=True)
    
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def monitor_archivo():
        ultimo_tamano = 0
        tiempo_sin_cambios = 0
        file_created_notified = False
        
        while process.poll() is None:
            time.sleep(chequeo_cada)
            if os.path.exists(output_file) and not file_created_notified:
                log_queue.put(f"✅ Archivo {output_file} creado para {username}.")
                notification_queue.put(("info", f"Live Iniciado 📡", f"El usuario {username} ha iniciado una transmisión en vivo."))
                status_queue.put((username, "EN VIVO", time.time()))
                file_created_notified = True
            if not os.path.exists(output_file):
                continue
            tamano_actual = os.path.getsize(output_file)
            if tamano_actual == ultimo_tamano:
                tiempo_sin_cambios += chequeo_cada
                log_queue.put(f"⏸️ Sin cambios en el archivo de {username} por {tiempo_sin_cambios}s...")
                if tiempo_sin_cambios >= tiempo_inactividad:
                    log_queue.put(f"🛑 Deteniendo FFmpeg para {username} tras {tiempo_inactividad}s de inactividad.")
                    if file_created_notified:
                        notification_queue.put(("info", f"Live Terminado 📴", f"La transmisión de {username} ha terminado por inactividad."))
                        status_queue.put((username, "NO EN VIVO", None))
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    break
            else:
                tiempo_sin_cambios = 0
                ultimo_tamano = tamano_actual
    
    monitor_thread = threading.Thread(target=monitor_archivo)
    monitor_thread.start()
    
    try:
        process.wait()
        log_queue.put(f"🏁 Grabación de {username} finalizada normalmente.")
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            status_queue.put((username, "NO EN VIVO", None))
        else:
            log_queue.put(f"❌ El archivo {output_file} no se creó o está vacío.")
            status_queue.put((username, "NO EN VIVO", None))
            notification_queue.put(("error", f"Error en Grabación ⚠️", f"La grabación de {username} falló."))
    except KeyboardInterrupt:
        log_queue.put(f"🛑 Grabación de {username} detenida por el usuario.")
        if os.path.exists(output_file):
            notification_queue.put(("info", f"Live Detenido ⏹️", f"La grabación de {username} fue detenida por el usuario."))
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        status_queue.put((username, "NO EN VIVO", None))
    except Exception as e:
        log_queue.put(f"🚫 Error al grabar con FFmpeg para {username}: {e}")
        if os.path.exists(output_file):
            notification_queue.put(("error", f"Error en Grabación ⚠️", f"Error al grabar el live de {username}: {e}"))
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        status_queue.put((username, "NO EN VIVO", None))
    finally:
        log_queue.put(f"🔄 Estado de {username} actualizado a NO EN VIVO.")
        status_queue.put((username, "NO EN VIVO", None))

def grabar_live_con_reintentos(username, cookies, log_queue, stop_event, notification_queue, status_queue, espera_reintento=60, app=None):
    """
    Intenta grabar el live con reintentos cada 10 segundos.
    """
    while not stop_event.is_set():
        try:
            room_id = get_room_id_from_user(username, cookies, log_queue)
            log_queue.put(f"✅ ROOM_ID para {username}: {room_id}")
            hls_url = get_hls_url(room_id, log_queue)
            log_queue.put(f"🎥 URL del stream HLS para {username} encontrada:\n{hls_url}\n")
            start_ffmpeg_recording(hls_url, username, log_queue, notification_queue, status_queue)
            log_queue.put(f"❌ El live de {username} terminó o se detuvo. Reintentando en {espera_reintento}s...\n")
        except Exception as e:
            log_queue.put(f"🚫 Error para {username}: {e}")
            log_queue.put(f"🔁 Reintentando en {espera_reintento}s...\n")
        time.sleep(espera_reintento)
    
    if app and username in app.threads:
        del app.threads[username]
    log_queue.put(f"🛑 Monitoreo de {username} detenido completamente.")

class TikTokRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Live Recorder 📹")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Arial", 12), padding=10, background="#007bff", foreground="white")
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f2f5", foreground="#333")
        self.style.configure("TEntry", font=("Arial", 12))
        self.style.configure("TCheckbutton", font=("Arial", 12), background="#f0f2f5")
        self.style.configure("Treeview", font=("Arial", 11), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#007bff", foreground="white")

        self.log_queue = queue.Queue()
        self.notification_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.stop_events = {}
        self.threads = {}
        self.user_status = {}

        self.users = self.load_users()
        for user in self.users:
            self.user_status[user] = {"status": "NO EN VIVO", "start_time": None}

        self.setup_ui()

        self.root.after(100, self.update_log)
        self.root.after(100, self.update_notifications)
        self.root.after(5000, self.update_user_status)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(main_frame, padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_frame, text="Usuario de TikTok 📱 (sin @):", style="TLabel").pack(side=tk.LEFT, padx=5)
        self.user_entry = ttk.Entry(input_frame, width=30)
        self.user_entry.pack(side=tk.LEFT, padx=5)

        add_button = ttk.Button(input_frame, text="Agregar 📥", command=self.add_user)
        add_button.pack(side=tk.LEFT, padx=5)

        list_frame = ttk.Frame(main_frame, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(list_frame, text="Usuarios Registrados 👥", style="TLabel").pack(anchor="w", pady=5)

        self.user_tree = ttk.Treeview(list_frame, columns=("Usuario", "Estado", "Tiempo"), show="headings", height=8)
        self.user_tree.heading("Usuario", text="Usuario")
        self.user_tree.heading("Estado", text="Estado")
        self.user_tree.heading("Tiempo", text="Tiempo en Directo")
        self.user_tree.column("Usuario", width=200, anchor="w")
        self.user_tree.column("Estado", width=150, anchor="center")
        self.user_tree.column("Tiempo", width=150, anchor="center")
        self.user_tree.pack(fill=tk.BOTH, expand=True)

        delete_button = ttk.Button(list_frame, text="Eliminar 🗑️", command=self.remove_user)
        delete_button.pack(anchor="e", pady=5)

        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X, pady=10)

        start_button = ttk.Button(control_frame, text="Iniciar Grabación ▶️", command=self.start_recording)
        start_button.pack(side=tk.LEFT, padx=5)

        stop_button = ttk.Button(control_frame, text="Detener Grabación ⏹️", command=self.stop_recording)
        stop_button.pack(side=tk.LEFT, padx=5)

        log_frame = ttk.Frame(main_frame, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(log_frame, text="Registro de Eventos 📜", style="TLabel").pack(anchor="w", pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, font=("Consolas", 10), bg="white", fg="#333")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state='disabled')

        self.update_user_tree()

    def load_users(self):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_users(self):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=4)

    def add_user(self):
        username = self.user_entry.get().strip()
        if username and username not in self.users:
            self.users.append(username)
            self.user_status[username] = {"status": "NO EN VIVO", "start_time": None}
            self.save_users()
            self.update_user_tree()
            self.log_queue.put(f"✅ Usuario {username} agregado.")
        self.user_entry.delete(0, tk.END)

    def remove_user(self):
        selection = self.user_tree.selection()
        if selection:
            username = self.user_tree.item(selection[0])['values'][0]
            if username in self.users:
                self.users.remove(username)
                del self.user_status[username]
                self.save_users()
                self.update_user_tree()
                self.log_queue.put(f"❌ Usuario {username} eliminado.")
                if username in self.stop_events:
                    self.stop_events[username].set()
                    del self.stop_events[username]
                    del self.threads[username]
                    if glob.glob(os.path.join(BASE_PATH, username, "*.ts")):
                        self.notification_queue.put(("info", f"Grabación Detenida ⏹️", f"La grabación de {username} fue desactivada al eliminar el usuario."))

    def update_user_tree(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        for user in self.users:
            status_info = self.user_status.get(user, {"status": "NO EN VIVO", "start_time": None})
            status = status_info["status"]
            time_text = ""
            if status == "EN VIVO" and status_info["start_time"]:
                elapsed = int(time.time() - status_info["start_time"])
                hours, remainder = divmod(elapsed, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                status_display = "🔴 EN VIVO"
            else:
                status_display = "⚪ NO EN VIVO"
            self.user_tree.insert("", "end", values=(user, status_display, time_text))

    def start_recording(self):
        cookies = {}
        for username in self.users:
            if username not in self.threads:
                stop_event = threading.Event()
                self.stop_events[username] = stop_event
                thread = threading.Thread(
                    target=grabar_live_con_reintentos,
                    args=(username, cookies, self.log_queue, stop_event, self.notification_queue, self.status_queue, 60, self)
                )
                thread.daemon = True
                thread.start()
                self.threads[username] = thread
                self.log_queue.put(f"🚀 Iniciando grabación para {username}...")

    def stop_recording(self):
        for username, stop_event in self.stop_events.items():
            stop_event.set()
            if glob.glob(os.path.join(BASE_PATH, username, "*.ts")):
                self.notification_queue.put(("info", f"Grabación Detenida ⏹️", f"Todas las grabaciones para {username} fueron detenidas."))
            self.user_status[username] = {"status": "NO EN VIVO", "start_time": None}
        self.stop_events.clear()
        self.threads.clear()

    def update_log(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state='disabled')
        except queue.Empty:
            pass
        self.root.after(100, self.update_log)

    def update_notifications(self):
        try:
            while True:
                notification = self.notification_queue.get_nowait()
                msg_type, title, message = notification
                if msg_type == "info":
                    messagebox.showinfo(title, message)
                elif msg_type == "error":
                    messagebox.showerror(title, message)
        except queue.Empty:
            pass
        self.root.after(100, self.update_notifications)

    def update_user_status(self):
        try:
            while True:
                username, status, start_time = self.status_queue.get_nowait()
                self.user_status[username] = {"status": status, "start_time": start_time}
                self.log_queue.put(f"🔄 Actualizando estado de {username} a {status}")
        except queue.Empty:
            pass
        self.update_user_tree()
        self.root.after(5000, self.update_user_status)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokRecorderApp(root)
    app.run()