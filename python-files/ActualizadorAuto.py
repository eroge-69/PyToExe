from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys
import os
import ftplib
import threading
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
from io import StringIO

# Redirigir stderr para ocultar logs de Chrome
sys.stderr = open(os.devnull, "w")

HEADLESS = 1  # 0 = visible, 1 = invisible

# Configuración FTP
FTP_SERVER = "198.91.81.15"
FTP_PORT = 21
FTP_USER = "psgewxys"
FTP_PASSWORD = "+Yoni1808"
FTP_DIRECTORY = "/domains/gabarri.com/public_html/TV"

# Archivos a subir
FILES_TO_UPLOAD = ["lista_iptv.m3u", "index.html"]

chrome_options = Options()
if HEADLESS:
    chrome_options.add_argument("--headless=new")

chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--no-default-browser-check")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")  # Reduce logs internos

class App:
    def __init__(self):
        self.window = ctk.CTk()
        self.setup_window()
        self.setup_tray()
        self.running = True
        
    def setup_window(self):
        self.window.title("Actualizador Automático")
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Interceptar eventos de cerrar y minimizar
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.window.bind("<Unmap>", self.on_minimize)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(main_frame, text="Estado del Proceso", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(20, 10))
        
        # Área de texto para mostrar el proceso
        self.text_area = ctk.CTkTextbox(main_frame, height=300, width=550)
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Estado inicial
        self.add_message("🚀 Iniciando aplicación...")
        
    def setup_tray(self):
        # Crear icono para el system tray
        def create_icon():
            # Crear una imagen simple para el icono
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='blue')
            dc = ImageDraw.Draw(image)
            dc.rectangle((16, 16, width-16, height-16), fill='white')
            dc.text((20, 24), "AT", fill='blue')
            return image
        
        # Menú del system tray
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self.show_window),
            pystray.MenuItem("Salir", self.quit_app)
        )
        
        # Crear el icono del system tray
        self.tray_icon = pystray.Icon("AutoUpdater", create_icon(), "Actualizador Automático", menu)
        
    def hide_window(self):
        """Oculta la ventana en el system tray"""
        self.window.withdraw()
        if not hasattr(self, 'tray_thread') or not self.tray_thread.is_alive():
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        
    def on_minimize(self, event):
        """Se ejecuta cuando se minimiza la ventana"""
        if event.widget == self.window:
            self.window.after(10, self.hide_window)
    
    def show_window(self, icon=None, item=None):
        """Muestra la ventana desde el system tray"""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
    
    def quit_app(self, icon=None, item=None):
        """Cierra completamente la aplicación"""
        self.running = False
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.window.quit()
        os._exit(0)
    
    def add_message(self, message):
        """Añade un mensaje al área de texto"""
        current_time = time.strftime("%H:%M:%S")
        formatted_message = f"[{current_time}] {message}\n"
        
        self.window.after(0, lambda: self._update_text(formatted_message))
        
    def _update_text(self, message):
        """Actualiza el texto en el hilo principal"""
        self.text_area.insert("end", message)
        self.text_area.see("end")
    
    def upload_files_ftp(self):
        """Sube los archivos al servidor FTP"""
        try:
            self.add_message("📡 Conectando al servidor FTP...")
            ftp = ftplib.FTP()
            ftp.connect(FTP_SERVER, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASSWORD)
            
            # Cambiar al directorio de destino
            ftp.cwd(FTP_DIRECTORY)
            self.add_message(f"📁 Cambiado al directorio: {FTP_DIRECTORY}")
            
            # Obtener la carpeta donde está el ejecutable (.exe) o el script (.py)
            if getattr(sys, 'frozen', False):
                # Si está ejecutándose como .exe
                script_dir = os.path.dirname(sys.executable)
            else:
                # Si está ejecutándose como .py
                script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Subir cada archivo
            for filename in FILES_TO_UPLOAD:
                full_path = os.path.join(script_dir, filename)
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as file:
                        ftp.storbinary(f'STOR {filename}', file)
                        self.add_message(f"✅ Archivo {filename} subido correctamente")
                else:
                    self.add_message(f"❌ Archivo {filename} no encontrado en: {full_path}")
            
            ftp.quit()
            self.add_message("🔌 Desconectado del servidor FTP")
            
        except ftplib.all_errors as e:
            self.add_message(f"❌ Error FTP: {e}")
        except Exception as e:
            self.add_message(f"❌ Error general: {e}")
    
    def clear_log(self):
        """Limpia el área de texto"""
        self.window.after(0, lambda: self.text_area.delete("1.0", "end"))
    
    def run_automation(self):
        """Ejecuta el ciclo de automatización"""
        cycle_count = 0
        while self.running:
            try:
                # Limpiar log al inicio de cada ciclo (excepto el primero)
                if cycle_count > 0:
                    self.clear_log()
                
                cycle_count += 1
                
                # Abrir página web
                self.add_message("🌐 Abriendo página web...")
                driver = webdriver.Chrome(options=chrome_options)
                driver.get("http://127.0.0.1:43110/1JKe3VPvFe35bm1aiHdD4p1xcGCkZKhH3Q/")
                
                self.add_message("⏰ Página abierta, esperando 10 segundos...")
                time.sleep(10)
                
                driver.quit()
                self.add_message("🚪 Navegador cerrado")
                
                # Subir archivos por FTP
                self.upload_files_ftp()
                
                self.add_message("⏳ Esperando 1 hora antes del próximo ciclo...")
                
                # Esperar 1 hora (3600 segundos) pero chequeando si debemos parar
                for i in range(3600):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.add_message(f"❌ Error en el ciclo: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def start(self):
        """Inicia la aplicación"""
        # Iniciar el hilo de automatización
        automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        automation_thread.start()
        
        # Iniciar directamente minimizado en el system tray
        self.window.after(100, self.hide_window)  # Se oculta después de 100ms
        
        # Iniciar la GUI
        self.window.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()