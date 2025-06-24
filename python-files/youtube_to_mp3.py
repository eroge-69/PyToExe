#!/usr/bin/env python3
"""
Descargador de Audio de YouTube - Versión Portable Mejorada
Interfaz moderna y elegante para descargar audio de YouTube

IMPORTANTE: 
- Solo usa este programa con contenido del que tengas derechos
- Respeta los términos de servicio de YouTube
- Esta versión descarga en formato M4A (audio de alta calidad)

Dependencias necesarias:
pip install yt-dlp pillow requests
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import yt_dlp
import threading
import os
import re
from pathlib import Path
import sys
import time
from urllib.parse import urlparse, parse_qs

# Importaciones opcionales
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class YouTubeDownloaderPortable:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎵 Descargador de YouTube - Versión Portable")
        self.root.geometry("800x900")  # Ventana más grande
        self.root.minsize(750, 800)  # Tamaño mínimo
        self.root.resizable(True, True)
        
        # Variables
        self.download_folder = tk.StringVar(value=str(Path.home() / "Downloads" / "YouTube_Audio"))
        self.url_var = tk.StringVar()
        self.filename_var = tk.StringVar()
        self.is_downloading = False
        self.is_validating = False
        self.video_info = None
        self.validation_timer = None
        self.validation_thread = None
        
        # Crear directorio de descarga
        Path(self.download_folder.get()).mkdir(parents=True, exist_ok=True)
        
        # Configurar estilo moderno
        self.setup_modern_style()
        
        # Crear interfaz mejorada
        self.create_modern_widgets()
        
        # Centrar ventana
        self.center_window()
    
    def setup_modern_style(self):
        """Configura un estilo moderno y elegante"""
        style = ttk.Style()
        
        # Configurar tema moderno
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Configurar colores y estilos personalizados
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'), 
                       foreground='#2C3E50')
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 12), 
                       foreground='#27AE60')
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 13, 'bold'), 
                       foreground='#34495E')
        
        style.configure('Info.TLabel', 
                       font=('Segoe UI', 11), 
                       foreground='#2C3E50')
        
        style.configure('Success.TLabel', 
                       foreground='#27AE60', 
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Error.TLabel', 
                       foreground='#E74C3C', 
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Status.TLabel', 
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Download.TButton', 
                       font=('Segoe UI', 13, 'bold'),  # Ligeramente más pequeño
                       focuscolor='none',
                       relief='raised',
                       borderwidth=2)
        
        # Estilo especial para botón habilitado
        style.map('Download.TButton',
                 background=[('active', '#27AE60'),
                            ('pressed', '#1E8449')],
                 foreground=[('active', 'white'),
                            ('pressed', 'white')])
        
        style.configure('Action.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       focuscolor='none')
        
        # Configurar el frame principal con un color de fondo suave
        self.root.configure(bg='#F8F9FA')
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_modern_widgets(self):
        """Crea una interfaz moderna y elegante"""
        # Frame principal con padding generoso
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid para expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Encabezado elegante
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        header_frame.columnconfigure(0, weight=1)
        
        # Título principal
        title_label = ttk.Label(header_frame, 
                               text="🎵 Descargador de YouTube", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Subtítulo
        subtitle_label = ttk.Label(header_frame, 
                                  text="✨ Versión Portable - No requiere FFmpeg - Funciona inmediatamente", 
                                  style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(0, 10))
        
        # Separador visual
        separator1 = ttk.Separator(header_frame, orient='horizontal')
        separator1.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # === SECCIÓN URL ===
        url_section = ttk.LabelFrame(main_frame, text="🔗 Enlace del Video", padding="20")
        url_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        url_section.columnconfigure(0, weight=1)
        
        # Campo URL más grande
        self.url_entry = ttk.Entry(url_section, textvariable=self.url_var, 
                                  font=('Segoe UI', 12), width=60)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        self.url_entry.bind('<Return>', lambda e: self.validate_url())  # Enter para validar
        
        # Campo URL con botones
        url_controls = ttk.Frame(url_section)
        url_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        url_controls.columnconfigure(0, weight=1)
        
        # Botones de control
        buttons_frame = ttk.Frame(url_controls)
        buttons_frame.grid(row=0, column=0)
        
        self.validate_btn = ttk.Button(buttons_frame, text="✓ Validar URL", 
                                      command=self.validate_url, style='Action.TButton')
        self.validate_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Botón para limpiar URL
        self.clean_btn = ttk.Button(buttons_frame, text="🧹 Limpiar URL", 
                                   command=self.clean_url_manual, style='Action.TButton')
        self.clean_btn.grid(row=0, column=1)
        
        # Estado de validación
        self.validation_label = ttk.Label(url_section, text="💡 Pega el enlace de YouTube. Si tiene caracteres raros, usa '🧹 Limpiar URL' primero")
        self.validation_label.grid(row=2, column=0, sticky=tk.W)
        
        # === SECCIÓN INFORMACIÓN DEL VIDEO ===
        self.info_section = ttk.LabelFrame(main_frame, text="📹 Información del Video", padding="20")
        self.info_section.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.info_section.columnconfigure(1, weight=1)
        self.info_section.grid_remove()  # Ocultar inicialmente
        
        # Miniatura más grande
        self.thumbnail_label = ttk.Label(self.info_section, text="🖼️\nCargando...", 
                                        font=('Segoe UI', 10), anchor='center')
        self.thumbnail_label.grid(row=0, column=0, rowspan=4, padx=(0, 25), pady=(0, 10))
        
        # Información del video con mejor formato
        self.title_info = ttk.Label(self.info_section, text="", 
                                   wraplength=450, justify=tk.LEFT, style='Info.TLabel')
        self.title_info.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 8))
        
        self.duration_info = ttk.Label(self.info_section, text="", style='Info.TLabel')
        self.duration_info.grid(row=1, column=1, sticky=tk.W, pady=(0, 8))
        
        self.channel_info = ttk.Label(self.info_section, text="", style='Info.TLabel')
        self.channel_info.grid(row=2, column=1, sticky=tk.W, pady=(0, 8))
        
        self.views_info = ttk.Label(self.info_section, text="", style='Info.TLabel')
        self.views_info.grid(row=3, column=1, sticky=tk.W)
        
        # === BOTÓN DE DESCARGA - JUSTO DESPUÉS DEL VIDEO ===
        download_section = ttk.Frame(main_frame)
        download_section.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        download_section.columnconfigure(0, weight=1)
        
        # BOTÓN DE DESCARGA COMPACTO PERO VISIBLE
        self.download_btn = ttk.Button(download_section, 
                                      text="⬇️ DESCARGAR AUDIO EN M4A", 
                                      command=self.download_audio, 
                                      style='Download.TButton', 
                                      state='disabled')
        self.download_btn.grid(row=0, column=0, pady=(10, 10), ipadx=50, ipady=15)
        
        # Estado del botón compacto
        self.download_status = ttk.Label(download_section, 
                                        text="❌ Primero valida una URL de YouTube", 
                                        style='Status.TLabel',
                                        foreground='#E74C3C')
        self.download_status.grid(row=1, column=0, pady=(0, 10))
        
        # === SECCIÓN CONFIGURACIÓN Y DESCARGA ===
        config_section = ttk.LabelFrame(main_frame, text="⚙️ Configuración", padding="20")
        config_section.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        config_section.columnconfigure(0, weight=1)
        
        # Nombre del archivo
        ttk.Label(config_section, text="📝 Nombre del archivo (opcional):", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.filename_entry = ttk.Entry(config_section, textvariable=self.filename_var, 
                                       font=('Segoe UI', 11), width=60)
        self.filename_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Carpeta de descarga
        ttk.Label(config_section, text="📁 Carpeta de descarga:", 
                 style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        
        folder_frame = ttk.Frame(config_section)
        folder_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.download_folder, 
                                     font=('Segoe UI', 10), state='readonly')
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        ttk.Button(folder_frame, text="📂 Cambiar", command=self.select_folder,
                  style='Action.TButton').grid(row=0, column=1)
        
        # === SECCIÓN DESCARGA ===
        download_section = ttk.LabelFrame(main_frame, text="🎯 ¡DESCARGAR AQUÍ!", padding="25")
        download_section.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        download_section.columnconfigure(0, weight=1)
        
        # BOTÓN DE DESCARGA EXTRA GRANDE Y PROMINENTE
        self.download_btn = ttk.Button(download_section, 
                                      text="⬇️ DESCARGAR AUDIO EN M4A", 
                                      command=self.download_audio, 
                                      style='Download.TButton', 
                                      state='disabled')
        self.download_btn.grid(row=0, column=0, pady=(10, 15), ipadx=100, ipady=30)
        
        # Estado del botón más grande
        self.download_status = ttk.Label(download_section, 
                                        text="❌ Primero valida una URL de YouTube", 
                                        style='Status.TLabel',
                                        foreground='#E74C3C')
        self.download_status.grid(row=1, column=0, pady=(0, 10))
        
        # === SECCIÓN PROGRESO ===
        progress_section = ttk.Frame(main_frame)
        progress_section.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_section.columnconfigure(0, weight=1)
        
        # Barra de progreso (oculta inicialmente)
        self.progress_frame = ttk.Frame(progress_section)
        self.progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.progress_frame.columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate', 
                                           style='TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(self.progress_frame, text="", style='Info.TLabel')
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # === SECCIÓN LOG ===
        log_section = ttk.LabelFrame(main_frame, text="📋 Registro de Actividad", padding="15")
        log_section.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        log_section.columnconfigure(0, weight=1)
        log_section.rowconfigure(0, weight=1)
        
        # Log con mejor formato pero más compacto
        self.log_text = scrolledtext.ScrolledText(log_section, 
                                                 height=6,  # Más pequeño
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD,
                                                 relief='flat',
                                                 borderwidth=1)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión de filas
        main_frame.rowconfigure(6, weight=1)
        
        # Mensaje de bienvenida mejorado
        self.log("🎵 ¡Bienvenido al Descargador de YouTube Portable!")
        self.log("=" * 55)
        self.log("✨ Esta versión NO requiere FFmpeg instalado")
        self.log("📀 Descarga automáticamente en formato M4A de alta calidad")
        self.log("🚀 Funcionamiento instantáneo")
        self.log("🧹 Limpieza automática de URLs problemáticas")
        self.log("⏱️ Timeout automático de 8 segundos en verificación")
        self.log("🔄 Interfaz se resetea automáticamente tras descarga")
        self.log("=" * 55)
        self.log("💡 INSTRUCCIONES:")
        self.log("   1️⃣ Pega el enlace de YouTube arriba")
        self.log("   2️⃣ Si tiene caracteres raros, usa '🧹 Limpiar URL'")
        self.log("   3️⃣ Presiona Enter o 'Validar URL'")
        self.log("   4️⃣ Revisa la información del video")
        self.log("   5️⃣ ¡El botón aparece justo después del video!")
        self.log("   6️⃣ La interfaz se resetea sola al terminar")
        self.log("=" * 55)
        self.log("⚠️  IMPORTANTE: Solo descarga contenido del que tengas derechos")
        self.log("")
        self.log("🆘 Si tienes problemas con URLs:")
        self.log("   • Usa el botón '🧹 Limpiar URL' primero")
        self.log("   • Verifica que sea una URL de YouTube válida")
        self.log("   • Prueba con URLs más simples si es necesario")
    
    def log(self, message):
        """Agrega un mensaje al log con mejor formato"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
        # Colorear ciertos tipos de mensajes
        if "✅" in message or "completada" in message.lower():
            # Mensajes de éxito en verde
            start_line = self.log_text.index(tk.END + "-2l")
            end_line = self.log_text.index(tk.END + "-1l")
            self.log_text.tag_add("success", start_line, end_line)
            self.log_text.tag_config("success", foreground="#27AE60")
        elif "❌" in message or "error" in message.lower():
            # Mensajes de error en rojo
            start_line = self.log_text.index(tk.END + "-2l")
            end_line = self.log_text.index(tk.END + "-1l")
            self.log_text.tag_add("error", start_line, end_line)
            self.log_text.tag_config("error", foreground="#E74C3C")
        
        self.root.update_idletasks()
    
    def on_url_change(self, event=None):
        """Se ejecuta cuando cambia la URL"""
        # Cancelar validación si está en curso
        if self.is_validating:
            self.cancel_validation()
        
        # Limpiar URL automáticamente cuando el usuario la pega
        current_url = self.url_var.get().strip()
        if current_url and len(current_url) > 20:  # Solo si parece una URL completa
            # Limpiar caracteres raros automáticamente
            clean_url = ''.join(char for char in current_url if ord(char) < 128)
            if clean_url != current_url:
                self.url_var.set(clean_url)
                self.log("🧹 URL limpiada automáticamente (se removieron caracteres especiales)")
        
        self.info_section.grid_remove()
        self.download_btn.config(state='disabled')
        self.download_status.config(text="❌ Primero valida una URL de YouTube", foreground='#E74C3C')
        self.validation_label.config(text="💡 Presiona '🧹 Limpiar URL' si es necesario, luego 'Validar URL'")
        self.video_info = None
    
    def extract_video_id(self, url):
        """Extrae el ID del video de diferentes formatos de URL de YouTube de forma más robusta"""
        # Limpiar la URL de caracteres raros
        url = url.strip()
        # Remover caracteres no ASCII que pueden causar problemas
        url = ''.join(char for char in url if ord(char) < 128)
        
        # Patrones para diferentes formatos de URL de YouTube
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11})',  # Patrón más simple y flexible
            r'youtu\.be/([0-9A-Za-z_-]{11})',
            r'youtube\.com/watch\?v=([0-9A-Za-z_-]{11})',
            r'youtube\.com/embed/([0-9A-Za-z_-]{11})',
            r'youtube\.com/v/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def is_valid_youtube_url(self, url):
        """Verifica si la URL es válida de YouTube con validación mejorada"""
        # Limpiar la URL de espacios y caracteres raros
        url = url.strip()
        # Remover caracteres no ASCII
        url = ''.join(char for char in url if ord(char) < 128)
        
        # Si podemos extraer un video ID válido, la URL es válida
        video_id = self.extract_video_id(url)
        if video_id and len(video_id) == 11:
            return True
        
        # Patrones de respaldo más flexibles
        youtube_patterns = [
            r'youtube\.com.*[?&]v=([0-9A-Za-z_-]{11})',
            r'youtu\.be/([0-9A-Za-z_-]{11})',
            r'youtube\.com/embed/([0-9A-Za-z_-]{11})',
            r'youtube\.com/v/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in youtube_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def validate_url(self):
        """Valida la URL y obtiene información del video con timeout mejorado"""
        if self.is_validating:
            # Si ya está validando, cancelar y reiniciar
            self.cancel_validation()
            return
            
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("URL vacía", "Por favor ingresa una URL de YouTube")
            return
        
        # Mostrar URL original para debugging
        self.log(f"🔗 URL original: {url}")
        
        # Limpiar URL primero
        clean_url = self.clean_youtube_url(url)
        
        if not self.is_valid_youtube_url(clean_url):
            self.validation_label.config(text="❌ URL de YouTube no válida", 
                                       style='Error.TLabel')
            self.log("❌ URL no válida - Verifica que sea un enlace de YouTube")
            self.log(f"💡 URL procesada: {clean_url}")
            self.log("💡 Formatos válidos:")
            self.log("   • https://www.youtube.com/watch?v=VIDEO_ID")
            self.log("   • https://youtu.be/VIDEO_ID")
            return
        
        # Iniciar validación
        self.is_validating = True
        self.validation_label.config(text="🔍 Verificando enlace...", 
                                   style='Subtitle.TLabel')
        self.validate_btn.config(state='normal', text="❌ Cancelar")
        self.root.update_idletasks()
        
        # Configurar timeout de 8 segundos (más tiempo para URLs complejas)
        self.validation_timer = self.root.after(8000, self.validation_timeout)
        
        # Ejecutar validación en hilo separado
        self.validation_thread = threading.Thread(target=self._validate_url_thread, args=(clean_url,), daemon=True)
        self.validation_thread.start()
    
    def clean_url_manual(self):
        """Limpia la URL manualmente cuando el usuario presiona el botón"""
        current_url = self.url_var.get().strip()
        if not current_url:
            messagebox.showinfo("URL vacía", "Primero pega una URL de YouTube")
            return
        
        original_url = current_url
        
        # Limpiar la URL
        cleaned_url = self.clean_youtube_url(current_url)
        
        # Actualizar el campo
        self.url_var.set(cleaned_url)
        
        if cleaned_url != original_url:
            self.log(f"🧹 URL limpiada manualmente")
            self.log(f"   Original: {original_url}")
            self.log(f"   Limpia: {cleaned_url}")
            self.validation_label.config(text="✅ URL limpiada - Ahora presiona 'Validar URL'", 
                                       style='Success.TLabel')
        else:
            self.log("ℹ️ La URL ya estaba limpia")
            self.validation_label.config(text="ℹ️ La URL ya estaba limpia - Presiona 'Validar URL'")
    
    def clean_youtube_url(self, url):
        """Limpia la URL de YouTube eliminando caracteres problemáticos y parámetros innecesarios"""
        try:
            # Limpiar caracteres no ASCII y espacios
            url = url.strip()
            url = ''.join(char for char in url if ord(char) < 128)
            
            # Extraer el video ID de forma robusta
            video_id = self.extract_video_id(url)
            if video_id and len(video_id) == 11:
                # Crear URL limpia y simple
                clean_url = f"https://www.youtube.com/watch?v={video_id}"
                self.log(f"🧹 URL limpiada: {clean_url}")
                return clean_url
            
            # Si no se puede limpiar, devolver la original sin caracteres raros
            return url
        except Exception as e:
            self.log(f"⚠️ Error al limpiar URL: {e}")
            return url
    
    def cancel_validation(self):
        """Cancela la validación en curso"""
        if self.validation_timer:
            self.root.after_cancel(self.validation_timer)
            self.validation_timer = None
        
        self.is_validating = False
        self.validate_btn.config(state='normal', text="✓ Validar URL")
        self.validation_label.config(text="❌ Verificación cancelada")
        self.log("❌ Verificación cancelada por el usuario")
    
    def validation_timeout(self):
        """Se ejecuta cuando la validación tarda más de 8 segundos"""
        if self.is_validating:
            self.is_validating = False
            self.validate_btn.config(state='normal', text="✓ Validar URL")
            self.validation_label.config(text="⏱️ Timeout - Intenta de nuevo", 
                                       style='Error.TLabel')
            self.log("⏱️ La verificación tardó demasiado (>8s) - Reintenta")
            self.log("💡 Consejos para solucionar:")
            self.log("   • Verifica tu conexión a internet")
            self.log("   • Usa el botón '🧹 Limpiar URL' primero")
            self.log("   • Prueba con URL más simple: youtube.com/watch?v=VIDEO_ID")
            self.log("   • Algunos videos pueden estar restringidos geográficamente")
    
    def _validate_url_thread(self, url):
        """Validación de URL en hilo separado con timeout"""
        if not self.is_validating:
            return
            
        try:
            self.root.after(0, lambda: self.log("🔍 Conectando con YouTube..."))
            self.root.after(0, lambda: self.log(f"🔗 URL limpia: {url}"))
            
            # Configuración optimizada para yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 10,
                'retries': 2,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Verificar si aún estamos validando
                if not self.is_validating:
                    return
                
                self.video_info = {
                    'title': info.get('title', 'Título no disponible'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Desconocido'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'upload_date': info.get('upload_date', 'Desconocida')
                }
                
                self.root.after(0, self._update_video_info)
                
        except Exception as e:
            if not self.is_validating:
                return
                
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self._validation_error(error_msg))
    
    def _validation_error(self, error_msg):
        """Maneja errores de validación"""
        if self.validation_timer:
            self.root.after_cancel(self.validation_timer)
            self.validation_timer = None
        
        self.is_validating = False
        self.validation_label.config(text="❌ Error al verificar enlace", style='Error.TLabel')
        self.validate_btn.config(state='normal', text="✓ Validar URL")
        self.log(f"❌ Error de verificación: {error_msg}")
        self.log("💡 Consejos para solucionar:")
        self.log("   • Verifica tu conexión a internet")
        self.log("   • Prueba con una URL más simple")
        self.log("   • El video podría estar restringido")
    
    def _update_video_info(self):
        """Actualiza la información del video en la UI"""
        if not self.video_info or not self.is_validating:
            return
        
        # Cancelar timer y resetear estado
        if self.validation_timer:
            self.root.after_cancel(self.validation_timer)
            self.validation_timer = None
        
        self.is_validating = False
        self.validation_label.config(text="✅ ¡Enlace válido! Video encontrado", 
                                   style='Success.TLabel')
        self.validate_btn.config(state='normal', text="✓ Validar URL")
        
        # Actualizar información del video con mejor formato
        self.title_info.config(text=f"📹 {self.video_info['title']}")
        
        duration = self.format_duration(self.video_info['duration'])
        self.duration_info.config(text=f"⏱️  Duración: {duration}")
        
        self.channel_info.config(text=f"👤 Canal: {self.video_info['uploader']}")
        
        views = f"{self.video_info['view_count']:,}" if self.video_info['view_count'] else "N/A"
        self.views_info.config(text=f"👀 Vistas: {views}")
        
        # Cargar miniatura
        self.load_thumbnail()
        
        # Mostrar sección de información
        self.info_section.grid()
        
        # Habilitar botón de descarga - MUY IMPORTANTE
        self.download_btn.config(state='normal')
        self.download_status.config(text="✅ ¡Listo para descargar! Botón habilitado arriba",
                                   foreground='#27AE60')
        
        # Hacer el botón más visible
        self.root.after(100, lambda: self.download_btn.focus())
        
        # Scroll hacia el botón para asegurar que sea visible
        self.log("🎯 ¡Botón de descarga habilitado!")
        self.log("⬆️ ¡BOTÓN HABILITADO! Está justo después de la información del video")
        self.log("📀 Se descargará automáticamente en formato M4A")
        
        # Sugerir nombre de archivo
        if not self.filename_var.get():
            safe_title = re.sub(r'[<>:"/\\|?*]', '', self.video_info['title'])
            self.filename_var.set(safe_title[:50])
        
        self.log(f"✅ Video verificado exitosamente")
        self.log(f"📹 Título: {self.video_info['title']}")
        self.log(f"👤 Canal: {self.video_info['uploader']}")
        self.log(f"⏱️  Duración: {duration}")
    
    def load_thumbnail(self):
        """Carga la miniatura del video"""
        if not self.video_info or not self.video_info['thumbnail']:
            self.thumbnail_label.config(text="🖼️\nSin miniatura")
            return
            
        if not (PIL_AVAILABLE and REQUESTS_AVAILABLE):
            self.thumbnail_label.config(text="🖼️\nMiniatura\nno disponible")
            return

        try:
            threading.Thread(target=self._load_thumbnail_thread, daemon=True).start()
        except Exception as e:
            self.log(f"⚠️ No se pudo cargar la miniatura: {e}")
            self.thumbnail_label.config(text="🖼️\nError al\ncargar imagen")
    
    def _load_thumbnail_thread(self):
        """Carga la miniatura en hilo separado"""
        if not (PIL_AVAILABLE and REQUESTS_AVAILABLE):
            return
            
        try:
            import io
            response = requests.get(self.video_info['thumbnail'], timeout=10)
            img = Image.open(io.BytesIO(response.content))
            
            # Miniatura más grande
            img.thumbnail((160, 120), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.root.after(0, lambda: self.thumbnail_label.config(image=photo, text=""))
            self.root.after(0, lambda: setattr(self.thumbnail_label, 'image', photo))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"⚠️ No se pudo cargar miniatura: {e}"))
            self.root.after(0, lambda: self.thumbnail_label.config(text="🖼️\nError al\ncargar imagen"))
    
    def format_duration(self, seconds):
        """Convierte segundos a formato mm:ss"""
        if not seconds:
            return "Desconocida"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def select_folder(self):
        """Selecciona la carpeta de descarga"""
        folder = filedialog.askdirectory(initialdir=self.download_folder.get())
        if folder:
            self.download_folder.set(folder)
            self.log(f"📁 Carpeta de descarga actualizada: {folder}")
    
    def reset_to_default(self):
        """Resetea toda la interfaz al estado predefinido"""
        # Limpiar campos
        self.url_var.set("")
        self.filename_var.set("")
        
        # Resetear estados
        self.is_downloading = False
        self.is_validating = False
        self.video_info = None
        
        # Cancelar timers si existen
        if self.validation_timer:
            self.root.after_cancel(self.validation_timer)
            self.validation_timer = None
        
        # Ocultar secciones
        self.info_section.grid_remove()
        self.progress_frame.grid_remove()
        
        # Resetear labels y botones
        self.validation_label.config(text="💡 Pega el enlace de YouTube. Si tiene caracteres raros, usa '🧹 Limpiar URL' primero")
        self.validate_btn.config(state='normal', text="✓ Validar URL")
        self.download_btn.config(state='disabled', text="⬇️ DESCARGAR AUDIO EN M4A")
        self.download_status.config(text="❌ Primero valida una URL de YouTube", foreground='#E74C3C')
        
        # Resetear miniatura
        self.thumbnail_label.config(text="🖼️\nCargando...", image="")
        
        # Limpiar información del video
        self.title_info.config(text="")
        self.duration_info.config(text="")
        self.channel_info.config(text="")
        self.views_info.config(text="")
        
        # Parar barra de progreso
        self.progress_bar.stop()
        
        self.log("🔄 Interfaz restablecida - Lista para nueva descarga")
        self.log("💡 Pega un nuevo enlace de YouTube para continuar")
    
    def download_audio(self):
        """Inicia la descarga del audio"""
        if self.is_downloading:
            return
        
        if not self.video_info:
            messagebox.showwarning("Sin video", "Primero valida una URL de YouTube")
            return
        
        # Confirmar descarga con ventana más elegante
        response = messagebox.askyesno(
            "🎵 Confirmar Descarga",
            f"¿Descargar este video?\n\n"
            f"📹 {self.video_info['title']}\n"
            f"📀 Formato: M4A (Alta Calidad)\n"
            f"📁 Destino: {self.download_folder.get()}"
        )
        
        if not response:
            return
        
        # Iniciar descarga
        self.is_downloading = True
        self.download_btn.config(state='disabled', text="🔄 Descargando...")
        self.download_status.config(text="🔄 Descargando audio...", foreground='#3498DB')
        self.progress_frame.grid()
        self.progress_bar.start()
        self.progress_label.config(text="🚀 Preparando descarga...")
        
        self.log("🎵 Iniciando descarga de audio...")
        self.log(f"📀 Formato: M4A (Alta Calidad)")
        
        threading.Thread(target=self._download_thread, daemon=True).start()
    
    def _download_thread(self):
        """Descarga el audio en hilo separado"""
        try:
            url = self.clean_youtube_url(self.url_var.get().strip())
            custom_filename = self.filename_var.get().strip()
            
            # Preparar nombre del archivo
            if custom_filename:
                safe_filename = re.sub(r'[<>:"/\\|?*]', '', custom_filename)
                output_template = str(Path(self.download_folder.get()) / f'{safe_filename}.%(ext)s')
            else:
                output_template = str(Path(self.download_folder.get()) / '%(title)s.%(ext)s')
            
            # Configuración optimizada para M4A
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': output_template,
                'restrictfilenames': True,
                'noplaylist': True,
                'socket_timeout': 30,
                'retries': 3,
                'progress_hooks': [self._progress_hook],
            }
            
            self.root.after(0, lambda: self.progress_label.config(text="📥 Descargando audio..."))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, self._download_completed)
            
        except Exception as e:
            error_msg = f"❌ Error durante la descarga: {str(e)}"
            self.root.after(0, lambda: self._download_error(error_msg))
    
    def _progress_hook(self, d):
        """Hook para mostrar progreso de descarga"""
        if d['status'] == 'downloading':
            self.root.after(0, lambda: self.progress_label.config(text="📥 Descargando desde YouTube..."))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_label.config(text="✅ Procesando archivo de audio..."))
    
    def _download_completed(self):
        """Se ejecuta cuando la descarga se completa"""
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        self.download_btn.config(state='normal', text="⬇️ DESCARGAR AUDIO EN M4A")
        self.download_status.config(text="🎉 ¡Descarga completada exitosamente!", foreground='#27AE60')
        self.is_downloading = False
        
        # Guardar información para mostrar en mensajes
        video_title = self.video_info['title'] if self.video_info else "Video"
        download_path = self.download_folder.get()
        
        self.log("=" * 55)
        self.log("🎉 ¡DESCARGA COMPLETADA EXITOSAMENTE!")
        self.log("=" * 55)
        self.log(f"📀 Formato: M4A (Alta Calidad)")
        self.log(f"📁 Ubicación: {download_path}")
        self.log(f"📹 Archivo: {video_title}")
        
        messagebox.showinfo(
            "🎉 ¡Descarga Completada!",
            f"El audio se ha descargado correctamente.\n\n"
            f"📹 {video_title}\n"
            f"📀 Formato: M4A (Alta Calidad)\n"
            f"📁 Ubicación: {download_path}"
        )
        
        # Preguntar si abrir carpeta
        if messagebox.askyesno("📂 Abrir Carpeta", 
                              "¿Deseas abrir la carpeta de descargas?"):
            try:
                if sys.platform == "win32":
                    os.startfile(download_path)
                elif sys.platform == "darwin":
                    os.system(f'open "{download_path}"')
                else:
                    os.system(f'xdg-open "{download_path}"')
                self.log("📂 Carpeta de descargas abierta")
            except Exception as e:
                self.log(f"⚠️ No se pudo abrir la carpeta: {e}")
        
        # Resetear todo al estado inicial después de 2 segundos
        self.root.after(2000, self.reset_to_default)
    
    def _download_error(self, error_msg):
        """Se ejecuta cuando hay un error en la descarga"""
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        self.download_btn.config(state='normal', text="⬇️ DESCARGAR AUDIO EN M4A")
        self.download_status.config(text="❌ Error en la descarga - Intenta de nuevo", foreground='#E74C3C')
        self.is_downloading = False
        
        self.log(error_msg)
        messagebox.showerror("❌ Error de Descarga", error_msg)
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()


def main():
    """Función principal"""
    missing_deps = []
    
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    if not PIL_AVAILABLE:
        missing_deps.append("pillow")
    
    if not REQUESTS_AVAILABLE:
        missing_deps.append("requests")
    
    if missing_deps:
        messagebox.showerror(
            "Dependencias Faltantes",
            f"Faltan las siguientes dependencias:\n{', '.join(missing_deps)}\n\n"
            "Instala las dependencias necesarias:\n"
            "pip install yt-dlp pillow requests"
        )
        return
    
    # Crear y ejecutar aplicación
    app = YouTubeDownloaderPortable()
    app.run()


if __name__ == "__main__":
    main()