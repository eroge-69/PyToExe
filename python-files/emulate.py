import sys
import os
import time
import threading
import psutil
import win32pipe
import win32file
import pywintypes
import win32con
import win32job
import win32api
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QTimer

pipe_name = r'\\.\pipe\933823D3-C77B-4BAE-89D7-A92B567236BC'

valorant_running = False
stopped_once = False
current_job = None
log_callback = None

pipe_threads = []
pipe_handles = []
monitor_thread = None
monitored_pids = set()
monitored_lock = threading.Lock()
monitoring_active = False

def make_shutdown_event():
    return threading.Event()
shutdown_event = make_shutdown_event()

def log_message(msg):
    global log_callback
    if log_callback:
        log_callback(msg)

def stop_and_restart_vgc():
    os.system('sc stop vgc')
    time.sleep(0.5)
    os.system('sc start vgc')
    time.sleep(0.5)

def override_vgc_pipe():
    try:
        pipe = win32file.CreateFile(
            pipe_name,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            0, None, win32con.OPEN_EXISTING, 0, None)
        win32file.CloseHandle(pipe)
    except Exception:
        pass

def handle_client(pipe):
    global stopped_once
    try:
        while not shutdown_event.is_set():
            try:
                data = win32file.ReadFile(pipe, 4096)
                if data:
                    if not stopped_once:
                        os.system('sc stop vgc')
                        try:
                            import winsound
                            winsound.Beep(1000, 500)
                        except:
                            pass
                        stopped_once = True
                    win32file.WriteFile(pipe, data[1])
            except pywintypes.error as e:
                if e.winerror == 109:
                    break
                time.sleep(0.1)
    finally:
        try:
            win32file.CloseHandle(pipe)
        except Exception:
            pass

def create_named_pipe():
    global pipe_handles
    while not shutdown_event.is_set():
        try:
            pipe = win32pipe.CreateNamedPipe(
                pipe_name,
                win32con.PIPE_ACCESS_DUPLEX,
                win32con.PIPE_TYPE_MESSAGE | win32con.PIPE_WAIT,
                win32con.PIPE_UNLIMITED_INSTANCES,
                1048576, 1048576, 500, None)
            pipe_handles.append(pipe)
            win32pipe.ConnectNamedPipe(pipe, None)
            t = threading.Thread(target=handle_client, args=(pipe,), daemon=True)
            t.start()
            pipe_threads.append(t)
        except Exception:
            time.sleep(1)

def create_job_object():
    job = win32job.CreateJobObject(None, "")
    extended_info = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
    extended_info['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, extended_info)
    return job

def assign_valorant_to_job():
    global current_job
    if current_job:
        win32job.TerminateJobObject(current_job, 0)
        current_job.Close()
        current_job = None
        time.sleep(2)
    current_job = create_job_object()
    found = False
    while not found and not shutdown_event.is_set():
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and "VALORANT-Win64-Shipping.exe" in proc.info['name']:
                    h_process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, proc.info['pid'])
                    win32job.AssignProcessToJobObject(current_job, h_process)
                    found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if not found:
            time.sleep(1)

def launch_valorant():
    os.system('"C:\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=valorant --launch-patchline=live')
    assign_valorant_to_job()

def start_valorant():
    global valorant_running, current_job
    if not valorant_running:
        threading.Thread(target=launch_valorant, daemon=True).start()
        valorant_running = True
    else:
        if current_job:
            win32job.TerminateJobObject(current_job, 0)
            current_job.Close()
            current_job = None
        os.system('taskkill /f /im VALORANT-Win64-Shipping.exe')
        valorant_running = False

def monitor_new_exes():
    global monitored_pids, monitoring_active
    prev_pids = set(p.info['pid'] for p in psutil.process_iter(['pid']))
    while monitoring_active and not shutdown_event.is_set():
        current_pids = set(p.info['pid'] for p in psutil.process_iter(['pid']))
        new_pids = current_pids - prev_pids
        with monitored_lock:
            for pid in new_pids:
                try:
                    proc = psutil.Process(pid)
                    exe = proc.exe()
                    if exe:
                        monitored_pids.add(pid)
                except Exception:
                    continue
        prev_pids = current_pids
        time.sleep(0.5)

def start_monitoring_exes():
    global monitoring_active, monitor_thread, monitored_pids
    with monitored_lock:
        monitored_pids.clear()
    monitoring_active = True
    monitor_thread = threading.Thread(target=monitor_new_exes, daemon=True)
    monitor_thread.start()

def stop_monitoring_exes():
    global monitoring_active, monitor_thread
    monitoring_active = False
    if monitor_thread:
        monitor_thread.join(timeout=2)
        monitor_thread = None

def kill_monitored_exes():
    killed = []
    with monitored_lock:
        for pid in list(monitored_pids):
            try:
                proc = psutil.Process(pid)
                exe = proc.exe()
                if exe and proc.is_running():
                    proc.kill()
                    killed.append(exe)
            except Exception:
                pass
        monitored_pids.clear()
    return killed

def reset_shutdown_event():
    global shutdown_event
    shutdown_event = make_shutdown_event()

def close_all_pipes():
    global pipe_handles
    for h in pipe_handles:
        try:
            win32file.CloseHandle(h)
        except Exception:
            pass
    pipe_handles.clear()

def start_with_emulate():
    global stopped_once, valorant_running, current_job, pipe_threads
    stopped_once = False
    reset_shutdown_event()
    # önce eski pipe threadlerini ve handle'larını temizle
    close_all_pipes()
    pipe_threads.clear()
    if current_job:
        win32job.TerminateJobObject(current_job, 0)
        current_job.Close()
        current_job = None
    stop_and_restart_vgc()
    override_vgc_pipe()
    threading.Thread(target=create_named_pipe, daemon=True).start()
    start_monitoring_exes()
    threading.Thread(target=launch_valorant, daemon=True).start()
    valorant_running = True

def safe_exit():
    global valorant_running, current_job, stopped_once, pipe_threads
    shutdown_event.set()
    stopped_once = False
    # önce pipe threadlerini bitir
    try:
        for t in pipe_threads:
            t.join(timeout=1)
    except:
        pass
    pipe_threads.clear()
    close_all_pipes()
    if current_job:
        win32job.TerminateJobObject(current_job, 0)
        current_job.Close()
        current_job = None
    os.system('taskkill /f /im VALORANT-Win64-Shipping.exe')
    os.system('sc stop vgc')
    valorant_running = False
    stop_monitoring_exes()
    kill_monitored_exes()

class ValorantBypassApp(QWidget):
    def __init__(self):
        super().__init__()
        global log_callback
        log_callback = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.old_pos = None

        self.setStyleSheet("""
            QWidget {
                background-color: #fff;
                border: 2px solid #6100b8;
                border-radius: 22px;
            }
            QPushButton {
                background-color: #ece6fa;
                color: #333;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                padding: 16px;
                margin-bottom: 12px;
            }
            QPushButton:hover {
                background-color: #e2d6f7;
            }
            QLabel {
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #6100b8;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(28, 28, 28, 28)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start Valorant")
        self.start_button.clicked.connect(self.toggle_start_stop)
        self.layout.addWidget(self.start_button)

        self.emulate_button = QPushButton("Start with Emulate")
        self.emulate_button.clicked.connect(self.start_with_emulate_ui)
        self.layout.addWidget(self.emulate_button)

        self.safe_exit_button = QPushButton("Safe Exit")
        self.safe_exit_button.clicked.connect(self.safe_exit_ui)
        self.layout.addWidget(self.safe_exit_button)

        self.setLayout(self.layout)
        self.update_status()

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def toggle_start_stop(self):
        global valorant_running
        if not valorant_running:
            self.status_label.setText("Status: Starting Valorant...")
            threading.Thread(target=self.start_valorant_ui, daemon=True).start()
        else:
            self.status_label.setText("Status: Stopping Valorant...")
            start_valorant()
            self.update_status()

    def start_valorant_ui(self):
        start_valorant()
        self.update_status()

    def start_with_emulate_ui(self):
        self.status_label.setText("Status: Starting with emulate...")
        threading.Thread(target=self.do_emulate_and_update, daemon=True).start()

    def do_emulate_and_update(self):
        start_with_emulate()
        self.update_status()

    def safe_exit_ui(self):
        self.status_label.setText("Status: Safe exit...")
        threading.Thread(target=self.do_safe_exit_and_update, daemon=True).start()

    def do_safe_exit_and_update(self):
        safe_exit()
        self.update_status()

    def update_status(self):
        global valorant_running
        if valorant_running:
            self.start_button.setText("Stop Valorant")
            self.status_label.setText("Status: Valorant running")
        else:
            self.start_button.setText("Start Valorant")
            self.status_label.setText("Status: Valorant stopped")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ValorantBypassApp()
    window.resize(370, 270)
    window.show()
    sys.exit(app.exec())
