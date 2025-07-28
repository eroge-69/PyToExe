import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, Toplevel, Label, Scale, HORIZONTAL
from tkinter.ttk import Progressbar
import requests
import json
import os
import re
import csv
from openpyxl import Workbook
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import platform

# ---------------------------
# CONFIGURACIÓN GLOBAL (Constantes)
# ---------------------------
# Rutas de archivos
ARCHIVOS_SALIDA = {
    "TXT": "cookies_validas.txt",
    "JSON": "cookies_validas.json",
    "CSV": "cookies_validas.csv",
    "XLSX": "cookies_validas.xlsx",
    "PROXIES_CAIDAS": "proxies_caidas.txt",
    "COOKIES_INVALIDAS": "cookies_invalidas.txt",
    "USER_AGENTS": "user_agents.txt",
    "CONFIG": "config.json"
}

# URLs de API de Roblox
ROBLOX_AUTHENTICATED_USER_API = "https://users.roblox.com/v1/users/authenticated"
ROBLOX_CURRENCY_API = "https://economy.roblox.com/v1/user/currency"
ROBLOX_FRIENDS_API = "https://friends.roblox.com/v1/users/{}/friends"
ROBLOX_PROXY_TEST_API = "https://www.roblox.com/login"

# User Agents por defecto
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
]
DEFAULT_USER_AGENTS_URL = "https://raw.githubusercontent.com/monosans/proxy-list/main/user-agents/browsers.txt"

# Configuración de reintentos y fallos
MAX_PROXY_FAILS = 3
REQUEST_TIMEOUT = 10
RETRY_DELAY_BASE = 1

class ConfigManager:
    def __init__(self, config_file=ARCHIVOS_SALIDA["CONFIG"]):
        self.config_file = config_file
        self.config = self._load_default_config()
        self.load_config()

    def _load_default_config(self):
        return {
            "discord_webhook_url": "",
            "retry_delay_base": RETRY_DELAY_BASE,
            "max_threads": 20,
            "theme_mode": "Dark"
        }

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error al cargar configuración: {e}. Usando valores por defecto.")
        return self.config

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

    def get_setting(self, key, default=None):
        return self.config.get(key, default)

    def set_setting(self, key, value):
        self.config[key] = value

class RobloxAPIClient:
    def __init__(self, session, user_agents, log_callback=None):
        self.session = session
        self.user_agents = user_agents
        self._log = log_callback if log_callback else self._default_log

    def _default_log(self, message, color="white"):
        # Fallback log si no se proporciona un callback
        print(f"[{color}] {message}")

    def _make_request(self, method, url, headers=None, proxies=None, timeout=REQUEST_TIMEOUT):
        try:
            response = self.session.request(method, url, headers=headers, proxies=proxies, timeout=timeout)
            response.raise_for_status() # Lanza HTTPError para 4xx/5xx
            return response
        except requests.exceptions.Timeout:
            raise APIError("Timeout", "Timeout de la solicitud.")
        except requests.exceptions.ConnectionError:
            raise APIError("ConnectionError", "Error de conexión.")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 403:
                raise APIError("Forbidden", f"Solicitud prohibida (403).")
            elif status_code == 429:
                raise APIError("RateLimited", f"Límite de tasa alcanzado (429).")
            else:
                raise APIError("HTTPError", f"Error HTTP {status_code}: {e.response.text[:100]}")
        except requests.exceptions.RequestException as e:
            raise APIError("RequestError", f"Error general de solicitud: {e}")
        except Exception as e:
            raise APIError("UnexpectedError", f"Error inesperado: {e}")

    def test_proxy_connectivity(self, proxy_obj):
        ua = random.choice(self.user_agents)
        headers = {"User-Agent": ua}
        start_time_proxy = time.time()
        try:
            response = self._make_request("GET", ROBLOX_PROXY_TEST_API, headers=headers, proxies=proxy_obj)
            latency = (time.time() - start_time_proxy) * 1000
            if "login-form" in response.text.lower() or "roblox.com" in response.url:
                return True, latency
            else:
                self._log(f"❌ Proxy caída/bloqueada (contenido inesperado): {proxy_obj['http']}", "red")
                return False, latency
        except APIError as e:
            self._log(f"❌ Proxy caída ({e.error_type}): {proxy_obj['http']}", "red")
            return False, None
        except Exception as e:
            self._log(f"❌ Proxy caída (error inesperado): {proxy_obj['http']} ({e})", "red")
            return False, None

    def get_user_info(self, cookie, proxy_obj):
        ua = random.choice(self.user_agents)
        headers = {"Cookie": f".ROBLOSECURITY={cookie}", "User-Agent": ua}
        try:
            response = self._make_request("GET", ROBLOX_USERINFO_API, headers=headers, proxies=proxy_obj)
            data = response.json()
            if "errors" in data or "error" in data or "captcha" in response.text.lower():
                raise APIError("CaptchaOrError", "Respuesta de API indica captcha o error de Roblox.")
            return data
        except json.JSONDecodeError:
            raise APIError("JSONError", "Respuesta de API no es JSON válido.")
        except APIError as e:
            raise e # Re-lanzar errores específicos de API
        except Exception as e:
            raise APIError("UnexpectedError", f"Error inesperado al obtener info de usuario: {e}")

    def get_robux(self, headers, proxy_obj):
        try:
            response = self._make_request("GET", ROBLOX_CURRENCY_API, headers=headers, proxies=proxy_obj)
            return response.json().get("robux", "?")
        except (APIError, json.JSONDecodeError, Exception):
            return "?"

    def get_friends(self, user_id, headers, proxy_obj):
        try:
            response = self._make_request("GET", ROBLOX_AUTHENTICATED_USER_API, headers=headers, proxies=proxy_obj)
            return [f.get("name", "?") for f in response.json().get("data", [])[:10]]
        except (APIError, json.JSONDecodeError, Exception):
            return []

class APIError(Exception):
    """Excepción personalizada para errores de API."""
    def __init__(self, error_type, message):
        self.error_type = error_type
        self.message = message
        super().__init__(f"{error_type}: {message}")

class RobloxCheckerCore:
    def __init__(self):
        # Callbacks para comunicarse con la UI
        self._log_callback = None
        self._update_stats_callback = None
        self._send_discord_notification_callback = None
        self._update_proxies_ui_callback = None

        # Variables de estado
        self.cookies_validas = []
        self.cookies_procesadas_set = set()
        self.archivo_cookies = None
        self.proxies_list = []
        self.proxies_cargadas_set = set()
        self.proxy_failures = {}
        self.proxy_index = 0
        self.user_agents = list(DEFAULT_USER_AGENTS) # Se actualizará desde APIClient
        
        self.total_cookies = 0
        self.cookies_checked = 0
        self.cookies_invalidas = 0
        self.errores_proxy = 0
        self.duplicados_omitidos = 0
        self.lock = threading.Lock()
        self.pause_flag = False
        self.stop_flag = False
        self.start_time = 0
        self.executor = None

        # Configuración (se establecerá desde ConfigManager a través de la UI)
        self.max_threads = 20
        self.retry_delay_base = RETRY_DELAY_BASE
        self.discord_webhook_url = ""

        self.session = requests.Session()
        self.api_client = RobloxAPIClient(self.session, self.user_agents, self._log) # Pasar user_agents y log_callback

    # ---------------------------
    # Métodos para registrar Callbacks
    # ---------------------------
    def register_log_callback(self, func):
        self._log_callback = func
        self.api_client._log = func # Asegurar que el APIClient también use el log de la UI

    def register_update_stats_callback(self, func):
        self._update_stats_callback = func

    def register_discord_notification_callback(self, func):
        self._send_discord_notification_callback = func

    def register_update_proxies_ui_callback(self, func):
        self._update_proxies_ui_callback = func

    # ---------------------------
    # Métodos internos que usan Callbacks
    # ---------------------------
    def _log(self, message, color="white"):
        if self._log_callback:
            self._log_callback(message, color)

    def _update_ui_stats(self, threads_active=None):
        if self._update_stats_callback:
            self._update_stats_callback(threads_active=threads_active)

    def _send_discord_notification(self, message, color="blue"):
        if self._send_discord_notification_callback:
            self._send_discord_notification_callback(message, color)

    def _update_proxies_ui(self, num_proxies, message_override=None):
        if self._update_proxies_ui_callback:
            self._update_proxies_ui_callback(num_proxies, message_override)

    # ---------------------------
    # FUNCIONES DE PROXIES
    # ---------------------------
    def cargar_proxies(self, archivo):
        if archivo:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    nuevos_proxies = []
                    for line in f:
                        proxy = line.strip()
                        if proxy and proxy not in self.proxies_cargadas_set:
                            nuevos_proxies.append(proxy)
                            self.proxies_cargadas_set.add(proxy)
                    self.proxies_list.extend(nuevos_proxies)
                self.proxy_index = 0
                self.proxy_failures.clear()
                self._log(f"🌐 Proxies cargadas: {len(nuevos_proxies)} nuevas, Total: {len(self.proxies_list)}", "blue")
                self._update_proxies_ui(len(self.proxies_list))
            except Exception as e:
                messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo de proxies: {e}")
                self._log(f"❌ Error al cargar proxies: {e}", "red")
        else:
            self._update_proxies_ui(0, "⚠️ Ningún archivo de proxies seleccionado")

    def get_next_proxy(self):
        with self.lock:
            if not self.proxies_list:
                return None, None
            proxy = self.proxies_list[self.proxy_index % len(self.proxies_list)]
            self.proxy_index += 1
            return {"http": proxy, "https": proxy}, proxy

    def report_proxy_failure(self, proxy):
        with self.lock:
            self.errores_proxy += 1
            self._update_ui_stats()
            if not proxy:
                return
            self.proxy_failures[proxy] = self.proxy_failures.get(proxy, 0) + 1
            if self.proxy_failures[proxy] >= MAX_PROXY_FAILS:
                self._log(f"⚠️ Proxy eliminada por fallos: {proxy}", "red")
                if proxy in self.proxies_list:
                    self.proxies_list.remove(proxy)
                    self.proxies_cargadas_set.discard(proxy)
                    self._update_proxies_ui(len(self.proxies_list))
                with open(ARCHIVOS_SALIDA["PROXIES_CAIDAS"], "a", encoding="utf-8") as f:
                    f.write(proxy + "\n")

    def chequear_proxies(self):
        if not self.proxies_list:
            messagebox.showwarning("Advertencia", "No hay proxies cargadas.")
            return
        self._log("🔍 Iniciando verificación de proxies...", "blue")
        
        def check_single_proxy_task(proxy):
            proxy_obj = {"http": proxy, "https": proxy}
            is_ok, latency = self.api_client.test_proxy_connectivity(proxy_obj)
            if is_ok:
                self._log(f"✅ Proxy OK: {proxy} (Latencia: {latency:.2f}ms)", "green")
                return proxy
            else:
                # El log ya se hizo dentro de test_proxy_connectivity
                return None

        proxies_ok = []
        with ThreadPoolExecutor(max_workers=10) as executor_check:
            futures = [executor_check.submit(check_single_proxy_task, proxy) for proxy in self.proxies_list]
            for future in futures:
                result = future.result()
                if result:
                    proxies_ok.append(result)
        
        self.proxies_list = proxies_ok
        self.proxies_cargadas_set = set(proxies_ok)
        self._log(f"✔ Proxies válidas: {len(self.proxies_list)}", "blue")
        self._update_proxies_ui(len(self.proxies_list))

    # ---------------------------
    # VALIDACIÓN DE COOKIES
    # ---------------------------
    def validar_cookie(self, cookie):
    if not self.validar_formato_cookie(cookie):
        self._log(f"❌ Formato de cookie inválido: {cookie[:20]}...", "red")
        return None

    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    proxy_obj = self._get_next_proxy()

    for attempt in range(3):
        if self.stop_flag:
            return None

        try:
            # 1. Obtener datos básicos del usuario (API moderna)
            response = requests.get(
                ROBLOX_AUTHENTICATED_USER_API,
                headers=headers,
                proxies=proxy_obj,
                timeout=15
            )
            if response.status_code != 200:
                raise APIError("InvalidResponse", f"Código de estado: {response.status_code}")

            user_data = response.json()
            if "id" not in user_data:
                raise APIError("InvalidResponse", "Faltan datos del usuario")

            # 2. Obtener Robux
            robux_response = requests.get(
                ROBLOX_CURRENCY_API,
                headers=headers,
                proxies=proxy_obj,
                timeout=15
            )
            robux = robux_response.json().get("robux", 0)

            # 3. Obtener amigos (limitado a 10)
            friends_response = requests.get(
                ROBLOX_FRIENDS_API.format(user_data["id"]),
                headers=headers,
                proxies=proxy_obj,
                timeout=15
            )
            friends = [f["name"] for f in friends_response.json().get("data", [])[:10]]

            result = {
                "cookie": cookie,
                "UserName": user_data.get("displayName", user_data.get("name", "?")),
                "UserID": user_data["id"],
                "Robux": robux,
                "Friends": friends,
                "IsPremium": user_data.get("isPremium", False),  # Nuevo campo
                "Proxy": proxy_obj
            }

            self._log(
                f"✅ {result['UserName']} | Robux: {result['Robux']} | "
                f"{'Premium' if result['IsPremium'] else 'No Premium'}",
                "green"
            )
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de red (intento {attempt + 1}/3): {str(e)}"
            self._log(f"⚠️ {error_msg}", "yellow")
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            error_msg = f"Error inesperado (intento {attempt + 1}/3): {str(e)}"
            self._log(f"⚠️ {error_msg}", "yellow")
            time.sleep(3 * (attempt + 1))

    return None


    # ---------------------------
    # PROCESAMIENTO
    # ---------------------------
    def procesar_cookies_thread(self, archivo_cookies):
        self.archivo_cookies = archivo_cookies
        if not self.archivo_cookies:
            messagebox.showwarning("Advertencia", "Debes seleccionar un archivo de cookies.")
            return

        if os.path.exists(ARCHIVOS_SALIDA["COOKIES_INVALIDAS"]):
            try:
                os.remove(ARCHIVOS_SALIDA["COOKIES_INVALIDAS"])
                self._log(f"🗑️ Archivo de cookies inválidas anterior borrado: {ARCHIVOS_SALIDA['COOKIES_INVALIDAS']}", "blue")
            except Exception as e:
                self._log(f"❌ Error al borrar archivo de cookies inválidas: {e}", "red")

        try:
            with open(self.archivo_cookies, "r", encoding="utf-8") as f:
                raw_cookies = [line.strip() for line in f if line.strip()]
                cookies_a_procesar = []
                self.cookies_procesadas_set.clear()
                self.duplicados_omitidos = 0
                for cookie in raw_cookies:
                    if self.validar_formato_cookie(cookie) and cookie not in self.cookies_procesadas_set:
                        cookies_a_procesar.append(cookie)
                        self.cookies_procesadas_set.add(cookie)
                    elif cookie in self.cookies_procesadas_set:
                        self.duplicados_omitidos += 1
                        self._log(f"⚠️ Cookie duplicada detectada y omitida: {cookie[:10]}...", "white")
                    else:
                        self._log(f"❌ Formato de cookie inválido detectado y omitido: {cookie[:10]}...", "red")

        except Exception as e:
            messagebox.showerror("Error de Lectura", f"No se pudo leer el archivo de cookies: {e}")
            self._log(f"❌ Error al leer archivo de cookies: {e}", "red")
            return

        if not cookies_a_procesar:
            self._log("❌ No hay cookies válidas y no duplicadas en el archivo para procesar.", "red")
            return

        self.total_cookies = len(cookies_a_procesar)
        self.cookies_checked = 0
        self.cookies_invalidas = 0
        self.pause_flag = False
        self.stop_flag = False
        self.start_time = time.time()

        self._update_ui_stats() # Actualizar UI al inicio del procesamiento
        self._log(f"🔍 Validando {self.total_cookies} cookies...", "blue")
        
        self.executor = ThreadPoolExecutor(max_workers=self.max_threads)
        futures = [self.executor.submit(self.worker, c) for c in cookies_a_procesar]

        threading.Thread(target=self._monitor_threads, daemon=True).start()

        for future in futures:
            if self.stop_flag:
                self.executor.shutdown(wait=False, cancel_futures=True)
                self._log("Proceso detenido por el usuario.", "red")
                break
            
            while self.pause_flag and not self.stop_flag:
                time.sleep(0.5)
            
            try:
                future.result(timeout=REQUEST_TIMEOUT * 2)
            except Exception as e:
                self._log(f"Error en la tarea de validación de cookie: {e}", "red")
                with self.lock:
                    self.cookies_checked += 1
                    self.cookies_invalidas += 1
                    self._update_ui_stats()

        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None

        if not self.stop_flag:
            self._log("✔ Proceso de validación de cookies finalizado.", "blue")
            self._send_discord_notification("Proceso de validación finalizado.", "green")
            self._update_ui_stats(final_update=True) # Indicar a la UI que es la actualización final

    def worker(self, cookie):
        while self.pause_flag and not self.stop_flag:
            time.sleep(0.5)
        
        if self.stop_flag:
            return

        resultado = self.validar_cookie(cookie)
        with self.lock:
            if resultado:
                self.cookies_validas.append(resultado)
                self._log(f"✅ {resultado['UserName']} | Robux: {resultado['Robux']}", "green")
            else:
                self.cookies_invalidas += 1
                self._log(f"❌ Cookie inválida o error de conexión: {cookie[:10]}...", "red")
                with open(ARCHIVOS_SALIDA["COOKIES_INVALIDAS"], "a", encoding="utf-8") as f:
                    f.write(cookie + "\n")
            self.cookies_checked += 1
            self._update_ui_stats()

    def iniciar_procesamiento(self, archivo_cookies):
        threading.Thread(target=self.procesar_cookies_thread, args=(archivo_cookies,), daemon=True).start()
        self._send_discord_notification("Proceso de validación iniciado.", "blue")

    def pausar_proceso(self):
        self.pause_flag = True
        self._log("⏸ Proceso en pausa.", "blue")
        self._send_discord_notification("Proceso pausado.", "yellow")

    def reanudar_proceso(self):
        self.pause_flag = False
        self._log("▶ Proceso reanudado.", "blue")
        self._send_discord_notification("Proceso reanudado.", "blue")

    def detener_proceso(self):
        if messagebox.askyesno("Confirmar Detención", "¿Estás seguro de que quieres detener el proceso?"):
            self.stop_flag = True
            self.pause_flag = False
            if self.executor:
                self.executor.shutdown(wait=False, cancel_futures=True)
                self.executor = None
            self._log("🛑 Solicitud de detención del proceso.", "red")
            messagebox.showinfo("Proceso Detenido", "El proceso ha sido detenido.")
            self._send_discord_notification("Proceso detenido por el usuario.", "red")

    # ---------------------------
    # ESTADÍSTICAS Y MONITOREO (Delegadas a la UI)
    # ---------------------------
    def _monitor_threads(self):
        while not self.stop_flag and (self.executor and self.executor._work_queue.qsize() > 0 or threading.active_count() > 1):
            with self.lock:
                if self.executor:
                    active_workers = self.executor._max_workers - self.executor._work_queue.qsize()
                    self._update_ui_stats(threads_active=max(0, active_workers))
                else:
                    self._update_ui_stats(threads_active=0)
            time.sleep(1)
        self._update_ui_stats(threads_active=0)

    # ---------------------------
    # INTEGRACIÓN Y UTILIDADES
    # ---------------------------
    def actualizar_user_agents(self):
        self._log("🌐 Intentando actualizar User Agents...", "blue")
        try:
            response = self.session.get(DEFAULT_USER_AGENTS_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            new_user_agents = [line.strip() for line in response.text.splitlines() if line.strip()]
            if new_user_agents:
                self.user_agents = new_user_agents
                self.api_client.user_agents = new_user_agents # Actualizar en APIClient
                with open(ARCHIVOS_SALIDA["USER_AGENTS"], "w", encoding="utf-8") as f:
                    for ua in new_user_agents:
                        f.write(ua + "\n")
                self._log(f"✅ User Agents actualizados desde la web. Total: {len(self.user_agents)}", "green")
                messagebox.showinfo("Actualización", f"User Agents actualizados exitosamente. Total: {len(self.user_agents)}")
            else:
                self._log("⚠️ No se encontraron User Agents válidos en la URL.", "red")
                messagebox.showwarning("Actualización", "No se encontraron User Agents válidos en la URL.")
        except requests.exceptions.RequestException as e:
            self._log(f"❌ Error de red al actualizar User Agents: {e}", "red")
            messagebox.showerror("Error de Actualización", f"Error de red al actualizar User Agents: {e}")
        except Exception as e:
            self._log(f"❌ Error inesperado al actualizar User Agents: {e}", "red")
            messagebox.showerror("Error de Actualización", f"Error inesperado al actualizar User Agents: {e}")

    def _cargar_user_agents_locales(self):
        if os.path.exists(ARCHIVOS_SALIDA["USER_AGENTS"]):
            try:
                with open(ARCHIVOS_SALIDA["USER_AGENTS"], "r", encoding="utf-8") as f:
                    loaded_uas = [line.strip() for line in f if line.strip()]
                    if loaded_uas:
                        self.user_agents = loaded_uas
                        self.api_client.user_agents = loaded_uas # Actualizar en APIClient
                        self._log(f"✅ User Agents cargados desde archivo local: {len(self.user_agents)}", "blue")
                    else:
                        self._log("⚠️ Archivo local de User Agents vacío.", "white")
            except Exception as e:
                self._log(f"❌ Error al cargar User Agents locales: {e}", "red")
        else:
            self._log("ℹ️ No se encontró archivo local de User Agents. Usando valores por defecto.", "white")


class RobloxCookieCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Cookie Checker Avanzado con Estadísticas")
        self.geometry("900x950")

        # Instancia del gestor de configuración
        self.config_manager = ConfigManager()
        
        # Instancia de la lógica de negocio
        self.core = RobloxCheckerCore()
        # Registrar callbacks de la UI en la lógica de negocio
        self.core.register_log_callback(self.log)
        self.core.register_update_stats_callback(self.actualizar_progreso)
        self.core.register_discord_notification_callback(self.send_discord_notification)
        self.core.register_update_proxies_ui_callback(self.actualizar_proxies_ui)

        # ---------------------------
        # StringVars para UI
        # ---------------------------
        self.total_cookies_var = StringVar(value="0")
        self.cookies_checked_var = StringVar(value="0")
        self.cookies_validas_var = StringVar(value="0")
        self.cookies_invalidas_var = StringVar(value="0")
        self.errores_proxy_var = StringVar(value="0")
        self.cps_var = StringVar(value="0.00")
        self.lbl_cookies_text = StringVar(value="⚠️ No se ha seleccionado archivo de cookies")
        self.lbl_proxies_text = StringVar(value="⚠️ Ningún archivo de proxies seleccionado")
        self.threads_active_var = StringVar(value="0")
        self.duplicados_omitidos_var = StringVar(value="0")
        self.system_info_var = StringVar(value="Cargando...")
        self.discord_webhook_url = StringVar(value="")
        self.retry_delay_var = StringVar(value=str(RETRY_DELAY_BASE))
        self.theme_mode_var = StringVar(value=ctk.get_appearance_mode())

        # ---------------------------
        # Configuración de la UI
        # ---------------------------
        self._create_widgets()
        self._load_initial_config_and_ui()
        self._start_system_info_monitor()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        # Frame de cookies
        frame_cookies = ctk.CTkFrame(self)
        frame_cookies.pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame_cookies, text="Seleccionar Cookies", command=self.seleccionar_cookies).pack(side="left", padx=10)
        ctk.CTkButton(frame_cookies, text="Validar Cookies", command=self.iniciar_procesamiento).pack(side="left", padx=10)
        ctk.CTkButton(frame_cookies, text="Exportar Resultados", command=self.exportar_resultados).pack(side="left", padx=10)
        ctk.CTkButton(frame_cookies, text="Abrir Carpeta Resultados", command=self.abrir_carpeta_resultados).pack(side="left", padx=10)
        self.lbl_cookies = ctk.CTkLabel(frame_cookies, textvariable=self.lbl_cookies_text)
        self.lbl_cookies.pack(side="left", padx=10)

        # Frame de control
        frame_control = ctk.CTkFrame(self)
        frame_control.pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame_control, text="⏸ Pausar", command=self.core.pausar_proceso).pack(side="left", padx=10)
        ctk.CTkButton(frame_control, text="▶ Reanudar", command=self.core.reanudar_proceso).pack(side="left", padx=10)
        ctk.CTkButton(frame_control, text="🛑 Detener", command=self.core.detener_proceso).pack(side="left", padx=10)
        ctk.CTkButton(frame_control, text="📊 Gráfico Resumen", command=self.generar_grafico_resumen).pack(side="left", padx=10)

        # Frame de proxies
        frame_proxy = ctk.CTkFrame(self)
        frame_proxy.pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame_proxy, text="Cargar Proxies", command=self.cargar_proxies_ui).pack(side="left", padx=10)
        ctk.CTkButton(frame_proxy, text="Chequear Proxies", command=self.core.chequear_proxies).pack(side="left", padx=10)
        self.lbl_proxies = ctk.CTkLabel(frame_proxy, textvariable=self.lbl_proxies_text)
        self.lbl_proxies.pack(side="left", padx=10)

        # Frame para validar una sola cookie
        frame_single_cookie = ctk.CTkFrame(self)
        frame_single_cookie.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(frame_single_cookie, text="Validar Cookie Individual:").pack(side="left", padx=5)
        self.entry_single_cookie = ctk.CTkEntry(frame_single_cookie, width=300)
        self.entry_single_cookie.pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(frame_single_cookie, text="Validar", command=self.validar_cookie_individual_ui).pack(side="left", padx=5)

        # Frame de configuración avanzada (Hilos, User Agents, Discord, Retrasos, Tema)
        frame_advanced_config = ctk.CTkFrame(self)
        frame_advanced_config.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(frame_advanced_config, text="Configuración Avanzada", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        # Hilos
        frame_threads = ctk.CTkFrame(frame_advanced_config)
        frame_threads.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_threads, text="Hilos de Validación:").pack(side="left", padx=5)
        self.slider_threads = ctk.CTkSlider(frame_threads, from_=1, to_=os.cpu_count() * 4 if os.cpu_count() else 40, command=self._update_max_threads_ui)
        self.slider_threads.set(self.core.max_threads)
        self.slider_threads.pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(frame_threads, text="Auto Hilos", command=self.auto_threads_config).pack(side="left", padx=5)

        # User Agents
        frame_ua = ctk.CTkFrame(frame_advanced_config)
        frame_ua.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_ua, text="User Agents:").pack(side="left", padx=5)
        ctk.CTkButton(frame_ua, text="Actualizar desde Web", command=self.core.actualizar_user_agents).pack(side="left", padx=5)

        # Discord Webhook
        frame_discord = ctk.CTkFrame(frame_advanced_config)
        frame_discord.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_discord, text="Discord Webhook URL:").pack(side="left", padx=5)
        self.entry_discord_webhook = ctk.CTkEntry(frame_discord, textvariable=self.discord_webhook_url, width=400)
        self.entry_discord_webhook.pack(side="left", padx=5, expand=True, fill="x")
        self.discord_webhook_url.trace_add("write", self._update_core_discord_url)

        # Configuración de Retrasos
        frame_delays = ctk.CTkFrame(frame_advanced_config)
        frame_delays.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_delays, text="Retraso Base (seg):").pack(side="left", padx=5)
        self.entry_retry_delay = ctk.CTkEntry(frame_delays, textvariable=self.retry_delay_var, width=50)
        self.entry_retry_delay.pack(side="left", padx=5)
        self.retry_delay_var.trace_add("write", self._validate_retry_delay_ui)

        # Selector de Tema
        frame_theme = ctk.CTkFrame(frame_advanced_config)
        frame_theme.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_theme, text="Tema:").pack(side="left", padx=5)
        self.theme_optionmenu = ctk.CTkOptionMenu(frame_theme, values=["Dark", "Light", "System"],
                                                  command=self._change_appearance_mode_event,
                                                  variable=self.theme_mode_var)
        self.theme_optionmenu.pack(side="left", padx=5)

        # Información del sistema
        frame_system_info = ctk.CTkFrame(self)
        frame_system_info.pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame_system_info, text="Mostrar Info Sistema", command=self.mostrar_info_sistema).pack(side="left", padx=10)
        self.lbl_system_info = ctk.CTkLabel(frame_system_info, textvariable=self.system_info_var, wraplength=700, justify="left")
        self.lbl_system_info.pack(side="left", padx=10, expand=True, fill="x")

        # Barra de progreso
        self.progress_bar = Progressbar(self, orient="horizontal", mode="determinate", length=800)
        self.progress_bar.pack(pady=10)
        self.lbl_stats = ctk.CTkLabel(self, 
            text=f"Procesadas: {self.cookies_checked_var.get()}/{self.total_cookies_var.get()} | Válidas: {self.cookies_validas_var.get()} | Inválidas: {self.cookies_invalidas_var.get()} | Duplicados: {self.duplicados_omitidos_var.get()} | Errores Proxy: {self.errores_proxy_var.get()} | CPS: {self.cps_var.get()} | Hilos Activos: {self.threads_active_var.get()}"
        )
        self.lbl_stats.pack(pady=5)

        # Log
        self.text_output = ctk.CTkTextbox(self, width=850, height=300)
        self.text_output.pack(pady=10)
        self.text_output.configure(state="disabled")

        # Botón para limpiar log
        ctk.CTkButton(self, text="Limpiar Log", command=self.limpiar_log).pack(pady=5)

    def _load_initial_config_and_ui(self):
        config = self.config_manager.config # Acceder directamente al diccionario de configuración
        
        self.discord_webhook_url.set(config.get("discord_webhook_url", ""))
        self.retry_delay_var.set(str(config.get("retry_delay_base", RETRY_DELAY_BASE)))
        self.core.max_threads = config.get("max_threads", 20)
        self.slider_threads.set(self.core.max_threads)
        
        theme_mode = config.get("theme_mode", "Dark")
        self.theme_mode_var.set(theme_mode)
        ctk.set_appearance_mode(theme_mode)
        self.log("✅ Configuración cargada.", "blue")

        # Asegurarse de que la lógica de negocio también tenga la configuración inicial
        self.core.discord_webhook_url = self.discord_webhook_url.get()
        self.core.retry_delay_base = float(self.retry_delay_var.get())

    def _on_closing(self):
        # Guardar la configuración actual de la UI en el ConfigManager
        self.config_manager.set_setting("discord_webhook_url", self.discord_webhook_url.get())
        self.config_manager.set_setting("retry_delay_base", float(self.retry_delay_var.get()))
        self.config_manager.set_setting("max_threads", self.core.max_threads)
        self.config_manager.set_setting("theme_mode", self.theme_mode_var.get())
        self.config_manager.save_config()

        self.core.stop_flag = True
        if self.core.executor:
            self.core.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()

    def _start_system_info_monitor(self):
        threading.Thread(target=self._update_system_info_periodically, daemon=True).start()

    def _update_max_threads_ui(self, val):
        self.core.max_threads = int(float(val))

    def _update_core_discord_url(self, *args):
        self.core.discord_webhook_url = self.discord_webhook_url.get()

    def _validate_retry_delay_ui(self, *args):
        try:
            value = float(self.retry_delay_var.get())
            if value < 0:
                raise ValueError
            self.core.retry_delay_base = value
        except ValueError:
            self.retry_delay_var.set(str(RETRY_DELAY_BASE))
            self.log("⚠️ Retraso base inválido. Usando valor por defecto.", "yellow")
            self.core.retry_delay_base = RETRY_DELAY_BASE

    def _change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        self.theme_mode_var.set(new_appearance_mode)

    # ---------------------------
    # Métodos de UI que interactúan con Core y actualizan UI
    # ---------------------------
    def seleccionar_cookies(self):
        archivo = filedialog.askopenfilename(title="Selecciona archivo de cookies", filetypes=[("Text files", "*.txt")])
        if archivo:
            self.lbl_cookies_text.set(f"Archivo de cookies: {os.path.basename(archivo)} ✅")
            self.log(f"📂 Archivo de cookies seleccionado: {archivo}", "blue")
            self.core.iniciar_procesamiento(archivo) # Iniciar procesamiento directamente
        else:
            self.lbl_cookies_text.set("⚠️ No se ha seleccionado archivo de cookies")

    def iniciar_procesamiento(self):
        # Este método ahora solo se usa si el usuario hace clic en "Validar Cookies" sin haber seleccionado un archivo
        # La selección de archivo ya inicia el procesamiento
        if not self.core.archivo_cookies:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo de cookies primero.")
            return
        self.core.iniciar_procesamiento(self.core.archivo_cookies)

    def cargar_proxies_ui(self):
        archivo = filedialog.askopenfilename(title="Selecciona archivo de proxies", filetypes=[("Text files", "*.txt")])
        self.core.cargar_proxies(archivo)

    def actualizar_proxies_ui(self, num_proxies, message_override=None):
        if message_override:
            self.lbl_proxies_text.set(message_override)
        else:
            self.lbl_proxies_text.set(f"Proxies cargadas: {num_proxies} {'✅' if num_proxies > 0 else '⚠️'}")

    def validar_cookie_individual_ui(self):
        cookie = self.entry_single_cookie.get().strip()
        if not cookie:
            messagebox.showwarning("Advertencia", "Por favor, introduce una cookie.")
            return
        if not self.core.validar_formato_cookie(cookie):
            messagebox.showwarning("Advertencia", "Formato de cookie inválido.")
            return
        
        self.log(f"🔍 Validando cookie individual: {cookie[:10]}...", "blue")
        threading.Thread(target=lambda: self._validar_cookie_individual_thread(cookie), daemon=True).start()

    def _validar_cookie_individual_thread(self, cookie):
        resultado = self.core.validar_cookie(cookie)
        if resultado:
            self.log(f"✅ Cookie individual VÁLIDA: {resultado['UserName']} | Robux: {resultado['Robux']}", "green")
            messagebox.showinfo("Resultado", f"Cookie Válida:\nUsuario: {resultado['UserName']}\nRobux: {resultado['Robux']}\nAmigos: {', '.join(resultado['Friends'])}")
        else:
            self.log(f"❌ Cookie individual INVÁLIDA o error de conexión.", "red")
            messagebox.showerror("Resultado", "Cookie Inválida o error de conexión.")

    def exportar_resultados(self):
        if not self.core.cookies_validas:
            messagebox.showwarning("Advertencia", "No hay cookies válidas para exportar.")
            return

        try:
            with open(ARCHIVOS_SALIDA["TXT"], "w", encoding="utf-8") as f:
                for v in self.core.cookies_validas:
                    amigos = ", ".join(v.get("Friends", [])) or "Sin amigos"
                    f.write(f"{v['UserName']} | {v['Robux']} Robux | Amigos: {amigos}\n")

            with open(ARCHIVOS_SALIDA["JSON"], "w", encoding="utf-8") as f:
                json.dump(self.core.cookies_validas, f, indent=4, ensure_ascii=False)

            with open(ARCHIVOS_SALIDA["CSV"], "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Usuario", "UserID", "Robux", "Amigos", "Premium", "Cookie"])
                for v in self.core.cookies_validas:
                   writer.writerow([v["UserName"], v["UserID"], v["Robux"], ", ".join(v["Friends"]), v.get("IsPremium", False), v["cookie"]])

            wb = Workbook()
            ws = wb.active
            ws.append(["Usuario", "UserID", "Robux", "Amigos", "Premium", "Cookie"])
            for v in self.core.cookies_validas:
                ws.append([v["UserName"], v["UserID"], v["Robux"], ", ".join(v["Friends"]), v.get("IsPremium", False), v["cookie"]])
            wb.save(ARCHIVOS_SALIDA["XLSX"])

            self.log("✅ Exportación completa en TXT, JSON, CSV y XLSX.", "blue")
            messagebox.showinfo("Exportación", "Resultados exportados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"No se pudieron exportar los resultados: {e}")
            self.log(f"❌ Error al exportar resultados: {e}", "red")

    def abrir_carpeta_resultados(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            os.startfile(script_dir)
        except AttributeError:
            import subprocess
            subprocess.Popen(['xdg-open', script_dir])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta de resultados: {e}")
            self.log(f"❌ Error al abrir carpeta de resultados: {e}", "red")

    def generar_grafico_resumen(self):
        if not self.core.cookies_checked:
            messagebox.showwarning("Advertencia", "No hay datos para generar el gráfico.")
            return

        labels = ['Válidas', 'Inválidas', 'Duplicadas Omitidas', 'Errores Proxy']
        sizes = [len(self.core.cookies_validas), self.core.cookies_invalidas, self.core.duplicados_omitidos, self.core.errores_proxy]
        colors = ['#4CAF50', '#FF5722', '#FFC107', '#9E9E9E']
        explode = (0.1, 0, 0, 0)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')
        ax1.set_title('Resumen de Validación de Cookies')

        graph_window = Toplevel(self)
        graph_window.title("Gráfico de Resumen")
        
        canvas = FigureCanvasTkAgg(fig1, master=graph_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=ctk.TOP, fill=ctk.BOTH, expand=1)
        canvas.draw()

        try:
            plt.savefig("resumen_validacion.png")
            self.log("📊 Gráfico de resumen guardado como resumen_validacion.png", "blue")
        except Exception as e:
            self.log(f"❌ Error al guardar el gráfico: {e}", "red")

    def send_discord_notification(self, message, color="blue"):
        webhook_url = self.discord_webhook_url.get()
        if not webhook_url or not self._is_valid_url(webhook_url):
            self.log("⚠️ URL de Discord Webhook inválida o vacía. Notificación no enviada.", "yellow")
            return

        colors_map = {
            "blue": 3447003,
            "green": 3066993,
            "red": 15158332,
            "yellow": 16776960
        }
        embed_color = colors_map.get(color, 3447003)

        data = {
            "embeds": [
                {
                    "title": "Roblox Cookie Checker Notificación",
                    "description": message,
                    "color": embed_color,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                }
            ]
        }
        try:
            self.core.session.post(webhook_url, json=data, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            self.log(f"❌ Error al enviar notificación a Discord: {e}", "red")

    def _is_valid_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def _update_system_info_periodically(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            ram_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            os_name = platform.system()
            os_release = platform.release()
            
            info = (
                f"Sistema Operativo: {os_name} {os_release}\n"
                f"Uso de CPU: {cpu_percent}% | Uso de RAM: {ram_percent}% | Uso de Disco: {disk_usage}%\n"
                f"Núcleos de CPU: {os.cpu_count()}"
            )
            self.system_info_var.set(info)
            time.sleep(5)

    def mostrar_info_sistema(self):
        messagebox.showinfo("Información del Sistema", self.system_info_var.get())

    def auto_threads_config(self):
        num_cores = os.cpu_count()
        if num_cores:
            suggested_threads = num_cores * 2
            if suggested_threads > 50: suggested_threads = 50
            
            def set_threads_from_slider(val):
                self.core.max_threads = int(float(val))
                self.slider_threads.set(self.core.max_threads)
                lbl_thread_value.configure(text=f"Hilos: {self.core.max_threads}")

            top = Toplevel(self)
            top.title("Configuración de Hilos Automáticos")
            top.geometry("300x150")
            
            Label(top, text="Ajusta el número máximo de hilos:").pack(pady=10)
            
            slider = Scale(top, from_=1, to_=os.cpu_count() * 4, orient=HORIZONTAL, command=set_threads_from_slider)
            slider.set(suggested_threads)
            slider.pack(pady=5)

            lbl_thread_value = Label(top, text=f"Hilos: {self.core.max_threads}")
            lbl_thread_value.pack()

            ctk.CTkButton(top, text="Cerrar", command=top.destroy).pack(pady=10)
        else:
            messagebox.showwarning("Advertencia", "No se pudo detectar el número de núcleos de CPU.")

    def limpiar_log(self):
        if messagebox.askyesno("Confirmar Limpieza", "¿Estás seguro de que quieres limpiar el log?"):
            self.text_output.configure(state="normal")
            self.text_output.delete("1.0", "end")
            self.text_output.configure(state="disabled")
            self.log("Log limpiado.", "blue")

# ---------------------------
# Ejecución de la Aplicación
# ---------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = RobloxCookieCheckerApp()
    app.mainloop()
