import json
import os
import time
import tempfile
from datetime import datetime
from pathlib import Path
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import colorama
from colorama import Fore, Style
import pandas as pd
import re
import sqlite3
from multiprocessing import Pool, Manager, Lock, cpu_count, Queue
import multiprocessing as mp
import signal
import sys
from contextlib import contextmanager
import threading
import shutil
import hashlib
from typing import Optional, Tuple, Dict, Any
import uuid

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
import queue

colorama.init(autoreset=True)

CONFIG_FILE = r"pdfc.config"
STATE_DB = r"pdfc_state.db"
config = {}
USE_COLORS = False
local_temp_dir = ""

log_lock = Lock()

dashboard_queue = None
dashboard_state = {
    'last_heartbeat': None,
    'last_polling': None,
    'files_in_queue': 0,
    'processing_count': 0,
    'total_files': 0,
    'files_being_processed': [],
    'all_logs': [],
    'process_activity': {},
    'active_processes': set(),
    'stats': {
        'total_processed': 0,
        'total_saved_mb': 0.0,
        'avg_compression_ratio': 0.0
    },
    'scroll_positions': {
        'queue': 0,
        'activity': 0,
        'logs': 0
    }
}

def sanitize_filename(filename: str) -> str:
    name, ext = os.path.splitext(filename)
    
    safe_name = re.sub(r'[<>:"/\\|?*&%!@#$^()+=`~\[\]{}]', '_', name)   # abdur rehman will check RE and advise
    safe_name = re.sub(r'_+', '_', safe_name)
    safe_name = safe_name.strip('_ ')
    
    if len(safe_name) > 50:
        safe_name = safe_name[:50]
    
    if not safe_name:
        safe_name = "file"
    
    return safe_name + ext

def create_local_temp_dir(watch_folder: str) -> str:
    global local_temp_dir
    try:
        local_temp_dir = os.path.join(watch_folder, "tmpProcessing")
        
        if not os.path.exists(local_temp_dir):
            os.makedirs(local_temp_dir, exist_ok=True)
            log_message(f"Created local temp directory: {local_temp_dir}")
        
        test_file = os.path.join(local_temp_dir, "write_test.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        
        log_message(f"Using local temp directory: {local_temp_dir}")
        return local_temp_dir
        
    except Exception as e:
        log_message(f"Failed to create local temp directory, falling back to system temp: {e}", "WARNING")
        local_temp_dir = tempfile.gettempdir()
        return local_temp_dir

def create_safe_temp_path(original_path: str, suffix: str = "_compressed") -> str:
    try:
        if not local_temp_dir or not os.path.exists(local_temp_dir):
            temp_dir = tempfile.gettempdir()
        else:
            temp_dir = local_temp_dir
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time()))[-6:]
        
        temp_filename = f"temp_{timestamp}_{unique_id}{suffix}.pdf"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        counter = 1
        while os.path.exists(temp_path):
            temp_filename = f"temp_{timestamp}_{unique_id}_{counter}{suffix}.pdf"
            temp_path = os.path.join(temp_dir, temp_filename)
            counter += 1
        
        log_message(f"Created safe temp path: {temp_path}", "DEBUG")
        return temp_path
        
    except Exception as e:
        log_message(f"Error creating safe temp path: {e}", "ERROR")
        return os.path.join(tempfile.gettempdir(), f"fallback_{os.getpid()}_{int(time.time())}.pdf")

def copy_to_safe_location(original_path: str) -> Tuple[str, bool]:
    try:
        problematic_chars = ['&', '%', '!', '@', '#', '$', '^', '(', ')', '+', '=', '`', '~', "'", '"', " - "]
        has_issues = (
            len(original_path) > 200 or 
            any(char in original_path for char in problematic_chars)
        )
        
        if has_issues:
            safe_path = create_safe_temp_path(original_path, "_input_copy")
            log_message(f"Copying problematic file to safe location: {os.path.basename(original_path)}", "DEBUG")
            shutil.copy2(original_path, safe_path)
            return safe_path, True
        else:
            return original_path, False
            
    except Exception as e:
        log_message(f"Error copying to safe location: {e}", "ERROR")
        return original_path, False

class GracefulKiller:
    def __init__(self):
        self.kill_now = threading.Event()
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        self.kill_now.set()

@contextmanager
def sqlite_connection(db_path: str, timeout: int = 30):
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=timeout, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def strip_ansi(text: str) -> str:
    ansi_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_regex.sub('', text)

def setup_logging(log_file_path: str) -> logging.Logger:
    logger = logging.getLogger('PDFCompressor')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    file_handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=10*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s [%(processName)s] %(levelname)s: %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_message(message: str, level: str = "INFO"):
    process_name = mp.current_process().name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with log_lock:
        if config.get("LoggingEnabled", False):
            logger = logging.getLogger('PDFCompressor')
            getattr(logger, level.lower(), logger.info)(message)
        
        if dashboard_queue is not None:
            try:
                dashboard_queue.put({
                    'type': 'log',
                    'process': process_name,
                    'message': message,
                    'level': level,
                    'timestamp': timestamp
                }, block=False)
            except Exception:
                pass

def update_dashboard_state(update_type: str, data: dict):
    if dashboard_queue is not None:
        try:
            process_name = mp.current_process().name
            dashboard_queue.put({
                'type': update_type,
                'data': data,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'process': process_name
            }, block=False)
        except Exception:
            pass

def send_process_heartbeat(activity_message: str, simple_status: str = "Active"):
    if dashboard_queue is not None:
        try:
            process_name = mp.current_process().name
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            dashboard_queue.put({
                'type': 'process_heartbeat',
                'process': process_name,
                'data': {
                    'activity': activity_message,
                    'simple_status': simple_status
                },
                'timestamp': timestamp
            }, block=False)
            
        except Exception:
            pass

def initialize_worker_process(shared_dashboard_queue):
    global dashboard_queue
    dashboard_queue = shared_dashboard_queue
    
    process_name = mp.current_process().name
    send_process_heartbeat(f"Worker {process_name} initialized and ready", "Ready")
    log_message(f"Worker process {process_name} initialized successfully")
    
    send_process_heartbeat(f"Worker {process_name} waiting for tasks", "Idle")

def create_dashboard_layout():
    layout = Layout()
    
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    
    layout["left"].split_column(
        Layout(name="status", size=12),
        Layout(name="processes", size=12),
        Layout(name="activity", size=12)
    )
    
    layout["right"].split_column(
        Layout(name="queue", size=24),
        Layout(name="logs", size=12)
    )
    
    return layout

def create_header_panel():
    title = Text("Auto PDF Compression - Server", style="bold blue")
    return Panel(Align.center(title), style="blue")

def create_footer_panel():
    footer_text = Text("Press Ctrl+C to stop processing and exit", style="dim")
    return Panel(Align.center(footer_text), style="dim")

def create_status_panel():
    table = Table(show_header=False, show_edge=False, padding=(0, 1))
    table.add_column("Label", style="bold cyan", width=20)
    table.add_column("Value", style="green")
    
    table.add_row("Last HeartBeat:", dashboard_state['last_heartbeat'] or "Not yet")
    table.add_row("Last Polling:", dashboard_state['last_polling'] or "Not yet")
    table.add_row("Files in Queue:", str(dashboard_state['files_in_queue']))
    
    active_count = len(dashboard_state['active_processes'])
    table.add_row("Active Processes:", str(active_count))
    
    if dashboard_state['total_files'] > 0:
        processed = max(0, dashboard_state['total_files'] - dashboard_state['files_in_queue'])
        table.add_row("Processing Count:", f"{processed}/{dashboard_state['total_files']}")
    else:
        table.add_row("Processing Count:", "0/0")
    
    table.add_row("Total Processed:", str(dashboard_state['stats']['total_processed']))
    table.add_row("Total Saved:", f"{dashboard_state['stats']['total_saved_mb']:.2f} MB")
    table.add_row("Avg Compression:", f"{dashboard_state['stats']['avg_compression_ratio']:.1f}%")
    
    return Panel(table, title="System Status", style="cyan")

def create_queue_panel():
    table = Table(show_header=True, show_edge=False, expand=True)
    table.add_column("File", style="yellow", width=40)
    table.add_column("Process", style="blue", width=15)
    table.add_column("Status", style="green", width=20)
    table.add_column("Size", style="cyan", width=10)
    
    if dashboard_state['files_being_processed']:
        files_to_show = dashboard_state['files_being_processed']
        max_display_files = 20
        
        scroll_pos = dashboard_state['scroll_positions']['queue']
        total_files = len(files_to_show)
        
        if total_files > max_display_files:
            start_idx = max(0, total_files - max_display_files)
            files_to_show = files_to_show[start_idx:]
            dashboard_state['scroll_positions']['queue'] = start_idx
        
        for file_info in files_to_show:
            display_filename = file_info['file']
            if len(display_filename) > 37:
                display_filename = display_filename[:34] + "..."
            
            file_size = file_info.get('size', 'Unknown')
            if isinstance(file_size, (int, float)) and file_size > 0:
                file_size = f"{file_size:.1f}MB"
            
            status = file_info.get('status', 'Queued')
            if status in ['Compressing', 'Processing']:
                status_style = "bold yellow"
            elif status == 'Completed':
                status_style = "bold green"
            elif status in ['Starting', 'Validating', 'Preparing']:
                status_style = "cyan"
            else:
                status_style = "white"
            
            table.add_row(
                display_filename,
                file_info['process'],
                status,
                str(file_size),
                style=status_style if status != 'Queued' else None
            )
        
        if total_files > max_display_files:
            table.add_row(
                f"... and {total_files - max_display_files} more files",
                "", "", "",
                style="dim italic"
            )
    else:
        table.add_row("No files currently in queue", "", "", "", style="dim")
    
    queue_count = len(dashboard_state['files_being_processed'])
    title = f"Files Queue ({queue_count} files)"
    
    return Panel(table, title=title, style="yellow")

def create_processes_panel():
    table = Table(show_header=True, show_edge=False)
    table.add_column("Process", style="bold magenta", width=18)
    table.add_column("Status", style="white", width=15)
    table.add_column("Last Update", style="cyan", width=15)

    expected_processes = ["MainProcess"]
    max_processes = config.get("NumProcesses", 4)

    # Adjusted: Skip SpawnPoolWorker-1 and start numbering from 2
    expected_processes.extend([f"SpawnPoolWorker-{i}" for i in range(2, max_processes + 2)])

    all_processes = set(expected_processes)
    for process_name in dashboard_state['process_activity'].keys():
        all_processes.add(process_name)
    for process_name in dashboard_state['active_processes']:
        all_processes.add(process_name)

    def sort_key(process_name):
        if process_name == "MainProcess":
            return (0, process_name)
        elif process_name.startswith("SpawnPoolWorker-"):
            try:
                num = int(process_name.split("-")[1])
                return (1, num)
            except:
                return (2, process_name)
        else:
            return (3, process_name)

    sorted_processes = sorted(all_processes, key=sort_key)

    current_time = time.time()
    activity_timeout = 120
    adjusted_index = 1  # Renumber visible workers starting from 1

    for process_name in sorted_processes:
        if process_name == "SpawnPoolWorker-1":
            # Skip reserved worker entirely
            continue

        display_name = process_name
        if process_name.startswith("SpawnPoolWorker-"):
            try:
                # Adjust numbering to start at 1 for visible workers
                display_name = f"SpawnPoolWorker-{adjusted_index}"
                adjusted_index += 1
            except:
                pass

        activity = dashboard_state['process_activity'].get(process_name)
        is_recently_active = process_name in dashboard_state['active_processes']

        if activity:
            try:
                activity_time = datetime.strptime(activity['timestamp'], "%Y-%m-%d %H:%M:%S")
                time_diff = (datetime.now() - activity_time).total_seconds()
                is_active = time_diff <= activity_timeout
            except:
                is_active = is_recently_active

            status_text = activity.get('simple_status', 'Active')
            time_part = activity['timestamp'][-8:] if len(activity['timestamp']) >= 8 else activity['timestamp']

            style = "green" if is_active else "dim"
            if not is_active:
                status_text = "Inactive"

            table.add_row(display_name, status_text, time_part, style=style)
        else:
            table.add_row(display_name, "Inactive", "N/A", style="dim")

    return Panel(table, title="Process Status", style="magenta")


def create_activity_panel():
    activity_text = Text()
    
    recent_activities = []
    for process_name in sorted(dashboard_state['active_processes']):
        activity = dashboard_state['process_activity'].get(process_name)
        if activity and activity.get('activity'):
            timestamp = activity.get('timestamp', '')
            time_part = timestamp[-8:] if len(timestamp) >= 8 else timestamp
            activity_line = f"[{time_part}] [{process_name}] {activity['activity']}"
            recent_activities.append(activity_line)
    
    max_activities = 6
    if len(recent_activities) > max_activities:
        recent_activities = recent_activities[-max_activities:]
        dashboard_state['scroll_positions']['activity'] = len(recent_activities) - max_activities
    
    if recent_activities:
        for activity in recent_activities:
            words = activity.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= 65:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        activity_text.append(current_line + "\n", style="white")
                    current_line = word
            
            if current_line:
                activity_text.append(current_line + "\n", style="white")
    else:
        activity_text.append("No current activity", style="dim")
    
    return Panel(activity_text, title="Current Activity", style="green")

def create_logs_panel():
    max_logs = 15
    recent_logs = dashboard_state['all_logs']
    
    if len(recent_logs) > max_logs:
        recent_logs = recent_logs[-max_logs:]
        dashboard_state['scroll_positions']['logs'] = len(dashboard_state['all_logs']) - max_logs
    
    log_text = Text()
    for log_entry in recent_logs:
        if log_entry['level'] == 'ERROR':
            style = "bold red"
        elif log_entry['level'] == 'WARNING':
            style = "bold yellow"
        elif log_entry['level'] == 'SUCCESS':
            style = "bold green"
        else:
            style = "white"
        
        time_part = log_entry['timestamp'][-8:]
        process_part = log_entry['process'][:12]
        message_part = log_entry['message'][:50] + "..." if len(log_entry['message']) > 50 else log_entry['message']
        
        log_line = f"[{time_part}] [{process_part}] {message_part}\n"
        log_text.append(log_line, style=style)
    
    if not recent_logs:
        log_text.append("No recent activity", style="dim")
    
    return Panel(log_text, title="Recent Logs", style="white")

def update_dashboard_data():
    updates_processed = 0
    max_updates_per_cycle = 100
    
    while updates_processed < max_updates_per_cycle:
        try:
            update = dashboard_queue.get_nowait()
            updates_processed += 1
            
            if update.get('process'):
                dashboard_state['active_processes'].add(update['process'])
                
                if update['process'] not in dashboard_state['process_activity']:
                    dashboard_state['process_activity'][update['process']] = {}
                
                dashboard_state['process_activity'][update['process']]['timestamp'] = update['timestamp']
            
            if update['type'] == 'process_heartbeat':
                process_name = update['process']
                activity_data = update['data']
                
                dashboard_state['active_processes'].add(process_name)
                dashboard_state['process_activity'][process_name] = {
                    'activity': activity_data['activity'],
                    'simple_status': activity_data['simple_status'],
                    'timestamp': update['timestamp']
                }
            
            elif update['type'] == 'log':
                log_entry = {
                    'message': update['message'],
                    'level': update['level'],
                    'timestamp': update['timestamp'],
                    'process': update['process']
                }
                dashboard_state['all_logs'].append(log_entry)
                
                if len(dashboard_state['all_logs']) > 200:
                    dashboard_state['all_logs'] = dashboard_state['all_logs'][-200:]
                
                simple_status = "Active"
                if "completed" in update['message'].lower():
                    simple_status = "Completed"
                elif "starting" in update['message'].lower() or "starting compression" in update['message'].lower():
                    simple_status = "Starting"
                elif "compressing" in update['message'].lower():
                    simple_status = "Compressing"
                elif "error" in update['message'].lower():
                    simple_status = "Error"
                elif "scan" in update['message'].lower():
                    simple_status = "Scanning"
                elif "heartbeat" in update['message'].lower():
                    simple_status = "Monitoring"
                elif "processing batch" in update['message'].lower():
                    simple_status = "Processing"
                
                dashboard_state['process_activity'][update['process']].update({
                    'activity': update['message'],
                    'simple_status': simple_status
                })
            
            elif update['type'] == 'heartbeat':
                dashboard_state['last_heartbeat'] = update['timestamp']
                dashboard_state['files_in_queue'] = update['data'].get('queue_size', 0)
                
                dashboard_state['active_processes'].add('MainProcess')
                dashboard_state['process_activity']['MainProcess'] = {
                    'activity': f"Heartbeat: {update['data'].get('queue_size', 0)} files in queue",
                    'simple_status': 'Monitoring',
                    'timestamp': update['timestamp']
                }
            
            elif update['type'] == 'polling':
                dashboard_state['last_polling'] = update.get('data', {}).get('timestamp', update['timestamp'])
                
                dashboard_state['active_processes'].add('MainProcess')
                dashboard_state['process_activity']['MainProcess'] = {
                    'activity': "Performing periodic file scan",
                    'simple_status': 'Scanning',
                    'timestamp': update['timestamp']
                }
            
            elif update['type'] == 'batch_start':
                dashboard_state['total_files'] = update['data'].get('total', 0)
                dashboard_state['files_in_queue'] = update['data'].get('total', 0)
                
                files = update['data'].get('files', [])
                dashboard_state['files_being_processed'] = []
                for file_path in files:
                    filename = os.path.basename(file_path)
                    try:
                        size_mb = get_file_size_mb(file_path)
                    except:
                        size_mb = 0
                    
                    dashboard_state['files_being_processed'].append({
                        'file': filename,
                        'process': 'MainProcess',
                        'status': 'Queued',
                        'size': size_mb
                    })
            
            elif update['type'] == 'file_start':
                filename = update['data']['filename']
                process_name = update['data']['process']
                
                found = False
                for file_info in dashboard_state['files_being_processed']:
                    if file_info['file'] == filename:
                        file_info['process'] = process_name
                        file_info['status'] = 'Starting'
                        found = True
                        break
                
                if not found:
                    try:
                        size_mb = update['data'].get('size', 0)
                    except:
                        size_mb = 0
                    
                    dashboard_state['files_being_processed'].append({
                        'file': filename,
                        'process': process_name,
                        'status': 'Starting',
                        'size': size_mb
                    })
                
                dashboard_state['process_activity'][process_name] = {
                    'activity': f"Starting {filename}",
                    'simple_status': 'Starting',
                    'timestamp': update['timestamp']
                }
            
            elif update['type'] == 'file_progress':
                filename = update['data']['filename']
                new_status = update['data'].get('status', 'Processing')
                process_name = update.get('process', 'Unknown')
                
                for file_info in dashboard_state['files_being_processed']:
                    if file_info['file'] == filename:
                        file_info['status'] = new_status
                        file_info['process'] = process_name
                        break
                
                dashboard_state['process_activity'][process_name] = {
                    'activity': f"{new_status}: {filename}",
                    'simple_status': new_status,
                    'timestamp': update['timestamp']
                }
            
            elif update['type'] == 'file_complete':
                filename = update['data']['filename']
                process_name = update.get('process', 'Unknown')
                
                dashboard_state['files_being_processed'] = [
                    f for f in dashboard_state['files_being_processed']
                    if f['file'] != filename
                ]
                
                dashboard_state['files_in_queue'] = max(0, dashboard_state['files_in_queue'] - 1)
                
                dashboard_state['process_activity'][process_name] = {
                    'activity': f"Completed {filename}",
                    'simple_status': 'Idle',
                    'timestamp': update['timestamp']
                }
            
            elif update['type'] == 'stats':
                dashboard_state['stats'].update(update['data'])
                
        except queue.Empty:
            break
        except Exception as e:
            pass

def run_dashboard():
    layout = create_dashboard_layout()
    
    try:
        with Live(layout, refresh_per_second=6, screen=True) as live:
            while True:
                try:
                    update_dashboard_data()
                    
                    layout["header"].update(create_header_panel())
                    layout["footer"].update(create_footer_panel())
                    layout["status"].update(create_status_panel())
                    layout["queue"].update(create_queue_panel())
                    layout["processes"].update(create_processes_panel())
                    layout["activity"].update(create_activity_panel())
                    layout["logs"].update(create_logs_panel())
                    
                    time.sleep(0.16)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    time.sleep(1)
    except Exception as e:
        pass

def validate_pdf_file(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                return False
            
            f.seek(0, 2)
            size = f.tell()
            if size < 1024:
                return False
                
        return True
    except Exception:
        return False

def get_file_size_mb(file_path: str) -> float:
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except Exception:
        return 0

def test_sqlite_write():
    temp_db = os.path.join(tempfile.gettempdir(), f"test_sqlite_{os.getpid()}.db")
    log_message(f"Testing SQLite write access: {temp_db}")
    
    try:
        with sqlite_connection(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
            cursor.execute("INSERT INTO test (id) VALUES (1)")
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            cursor.execute("DROP TABLE test")
            conn.commit()
            
            if count != 1:
                raise sqlite3.Error("Test data validation failed")
                
        log_message("SQLite write access validated successfully")
        
    except Exception as e:
        log_message(f"SQLite write test failed: {e}", "ERROR")
        raise
    finally:
        try:
            if os.path.exists(temp_db):
                os.remove(temp_db)
        except Exception:
            pass

def init_sqlite_db(db_path: str, processed_files: Optional[set] = None, skipped_files: Optional[set] = None):
    log_message(f"Initializing SQLite database: {db_path}")
    
    try:
        with sqlite_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(files)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if not existing_columns:
                log_message("Creating new files table")
                cursor.execute('''
                    CREATE TABLE files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        status TEXT NOT NULL CHECK(status IN ('processed', 'skipped', 'error')),
                        original_size_mb REAL,
                        compressed_size_mb REAL,
                        compression_ratio REAL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        error_message TEXT,
                        UNIQUE(path)
                    )
                ''')
            else:
                log_message("Migrating existing table schema")
                new_columns = [
                    ('original_size_mb', 'REAL'),
                    ('compressed_size_mb', 'REAL'),
                    ('compression_ratio', 'REAL'),
                    ('processed_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('error_message', 'TEXT')
                ]
                
                for col_name, col_type in new_columns:
                    if col_name not in existing_columns:
                        try:
                            cursor.execute(f"ALTER TABLE files ADD COLUMN {col_name} {col_type}")
                            log_message(f"Added column: {col_name}")
                        except sqlite3.Error as e:
                            log_message(f"Error adding column {col_name}: {e}", "WARNING")
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)')
            
            if processed_files or skipped_files:
                log_message("Migrating existing state to SQLite")
                
                if processed_files:
                    for path in processed_files:
                        cursor.execute(
                            "INSERT OR IGNORE INTO files (path, status) VALUES (?, ?)", 
                            (path, "processed")
                        )
                
                if skipped_files:
                    for path in skipped_files:
                        cursor.execute(
                            "INSERT OR IGNORE INTO files (path, status) VALUES (?, ?)", 
                            (path, "skipped")
                        )
                
                conn.commit()
                log_message(f"Migrated {len(processed_files or [])} processed and {len(skipped_files or [])} skipped files")
            
            if 'original_size_mb' not in existing_columns:
                cursor.execute('SELECT COUNT(*) FROM files WHERE status = "processed"')
                result = cursor.fetchone()
                return {
                    'total_processed': result[0] if result else 0,
                    'total_original_mb': 0,
                    'total_compressed_mb': 0,
                    'avg_compression_ratio': 0,
                    'total_saved_mb': 0
                }
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_processed,
                    COALESCE(SUM(original_size_mb), 0) as total_original_mb,
                    COALESCE(SUM(compressed_size_mb), 0) as total_compressed_mb,
                    COALESCE(AVG(compression_ratio), 0) as avg_compression_ratio
                FROM files 
                WHERE status = 'processed' AND original_size_mb IS NOT NULL
            ''')
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_processed': result[0] or 0,
                    'total_original_mb': result[1] or 0,
                    'total_compressed_mb': result[2] or 0,
                    'avg_compression_ratio': result[3] or 0,
                    'total_saved_mb': (result[1] or 0) - (result[2] or 0)
                }
            else:
                return {
                    'total_processed': 0,
                    'total_original_mb': 0,
                    'total_compressed_mb': 0,
                    'avg_compression_ratio': 0,
                    'total_saved_mb': 0
                }
        
        log_message("SQLite database initialized successfully")
        
    except Exception as e:
        log_message(f"Failed to initialize SQLite database: {e}", "ERROR")
        raise

def load_and_validate_config() -> Tuple[bool, Dict[str, Any]]:
    global config
    
    process_name = mp.current_process().name
    
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = {
            "LoggingEnabled": bool,
            "WatchFolder": str,
            "GhostscriptPath": str,
            "PDFSettings": str,
            "MinCreationDate": str,
            "EnableInitialScan": bool
        }
        
        for field, expected_type in required_fields.items():
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(config[field], expected_type):
                raise ValueError(f"Invalid type for {field}: expected {expected_type.__name__}")
        
        valid_pdf_settings = ["/screen", "/ebook", "/prepress", "/printer", "/default"]
        if config["PDFSettings"] not in valid_pdf_settings:
            raise ValueError(f"Invalid PDFSettings: {config['PDFSettings']}. Must be one of {valid_pdf_settings}")
        
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", config["MinCreationDate"]):
            raise ValueError("Invalid MinCreationDate format (expected YYYY-MM-DD)")
        
        try:
            min_date = datetime.strptime(config["MinCreationDate"], "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid MinCreationDate: {e}")
        
        max_date = None
        if "MaxCreationDate" in config:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", config["MaxCreationDate"]):
                raise ValueError("Invalid MaxCreationDate format (expected YYYY-MM-DD)")
            
            try:
                max_date = datetime.strptime(config["MaxCreationDate"], "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(f"Invalid MaxCreationDate: {e}")
            
            if max_date <= min_date:
                raise ValueError("MaxCreationDate must be after MinCreationDate")
        
        num_processes = config.get("NumProcesses", 4)
        if not isinstance(num_processes, int) or num_processes < 1 or num_processes > 16:
            raise ValueError("NumProcesses must be an integer between 1 and 16")
        
        if config["LoggingEnabled"] and not config.get("LogFile"):
            raise ValueError("LogFile is required when LoggingEnabled is true")
        
        log_message("Config file validated successfully")
        log_message(f"Min creation date: {min_date}")
        if max_date:
            log_message(f"Max creation date: {max_date}")
        log_message(f"Number of processes: {num_processes}")
        
        config_dict = {
            'watch_folder': config["WatchFolder"],
            'ghostscript_path': config["GhostscriptPath"],
            'pdf_settings': config["PDFSettings"],
            'min_date': min_date,
            'max_date': max_date,
            'num_processes': num_processes,
            'log_file': config.get("LogFile", ""),
            'log_dir': os.path.dirname(config.get("LogFile", "")) if config.get("LogFile") else "",
            'enable_initial_scan': config.get("EnableInitialScan", True)
        }
        
        return True, config_dict
        
    except Exception as e:
        print(f"[Process#{process_name}] Config validation failed: {e}")
        return False, {}

def validate_environment(config_dict: Dict[str, Any]) -> bool:
    process_name = mp.current_process().name
    
    watch_folder = config_dict['watch_folder']
    ghostscript_path = config_dict['ghostscript_path']
    log_dir = config_dict['log_dir']
    
    log_message(f"Validating write access to: {os.path.dirname(STATE_DB)}")
    try:
        test_file = os.path.join(os.path.dirname(STATE_DB), "testwrite.txt")
        with open(test_file, 'w') as f:
            f.write("Test")
        os.remove(test_file)
        log_message("Write access validated")
    except Exception as e:
        log_message(f"Failed to validate write access: {e}", "ERROR")
        return False
    
    log_message(f"Validating watch folder: {watch_folder}")
    try:
        if not os.path.exists(watch_folder):
            os.makedirs(watch_folder)
            log_message("Created watch folder")
        else:
            log_message("Watch folder validated")
    except Exception as e:
        log_message(f"Failed to validate watch folder: {e}", "ERROR")
        return False
    
    try:
        create_local_temp_dir(watch_folder)
    except Exception as e:
        log_message(f"Failed to create local temp directory: {e}", "WARNING")
    
    if config["LoggingEnabled"] and log_dir:
        log_message(f"Validating log folder: {log_dir}")
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            test_file = os.path.join(log_dir, "testwrite.txt")
            with open(test_file, 'w') as f:
                f.write("Test")
            os.remove(test_file)
            log_message("Log folder validated")
        except Exception as e:
            log_message(f"Failed to validate log folder: {e}", "ERROR")
            return False
    
    log_message(f"Validating Ghostscript: {ghostscript_path}")
    try:
        if not os.path.exists(ghostscript_path):
            raise FileNotFoundError(f"Ghostscript not found at {ghostscript_path}")
        
        for attempt in range(3):
            try:
                log_message(f"Ghostscript validation attempt {attempt+1}/3")
                result = subprocess.run(
                    [ghostscript_path, "-version"],
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=10
                )
                gs_version = result.stdout.strip()
                log_message(f"Ghostscript validated ({gs_version})")
                break
            except subprocess.TimeoutExpired:
                log_message(f"Ghostscript validation timed out (attempt {attempt+1}/3)", "WARNING")
                if attempt == 2:
                    raise Exception("Ghostscript validation failed after 3 attempts")
            except subprocess.CalledProcessError as e:
                raise Exception(f"Ghostscript validation failed: {e.stderr}")
                
    except Exception as e:
        log_message(f"Ghostscript validation error: {e}", "ERROR")
        return False
    
    return True

def test_file_stable(file_path: str, max_wait: int = 5) -> bool:
    try:
        initial_size = os.path.getsize(file_path)
        time.sleep(min(1, max_wait))
        final_size = os.path.getsize(file_path)
        return initial_size == final_size
    except Exception as e:
        log_message(f"Error checking file stability for {file_path}: {e}", "ERROR")
        return False

def is_file_in_date_range(file_path: str, min_date, max_date) -> bool:
    try:
        file_info = os.stat(file_path)
        creation_date = datetime.fromtimestamp(file_info.st_ctime).date()
        
        if creation_date < min_date:
            return False
        
        if max_date and creation_date > max_date:
            return False
        
        return True
    except Exception as e:
        log_message(f"Error checking date for {file_path}: {e}", "WARNING")
        return False

def compress_pdf(args):
    file_path, db_path, counter_lock, processed_count, total_files, pdf_settings, ghostscript_path, min_date, max_date, log_dir = args
    
    temp_output_file = None
    safe_input_path = None
    is_input_copy = False
    
    try:
        process_name = mp.current_process().name
        send_process_heartbeat(f"Worker {process_name} received task", "Starting")
        
        if not os.path.exists(file_path):
            log_message(f"File not found: {file_path}", "ERROR")
            return
        
        norm_path = os.path.normpath(os.path.abspath(file_path)).lower()
        filename = os.path.basename(file_path)
        
        send_process_heartbeat(f"Processing {filename}", "Processing")
        log_message(f"Worker {process_name} received file: {filename}")
        
        update_dashboard_state('file_start', {
            'filename': filename,
            'process': process_name,
            'size': get_file_size_mb(file_path)
        })
        
        log_message(f"Starting compression: {filename}")
        
        status = check_file_status(db_path, norm_path)
        if status in ["processed", "skipped"]:
            log_message(f"Skipping already {status} file: {filename}")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        send_process_heartbeat(f"Validating {filename}", "Validating")
        update_dashboard_state('file_progress', {
            'filename': filename,
            'status': 'Validating'
        })
        
        if not validate_pdf_file(file_path):
            log_message(f"Invalid PDF file: {file_path}", "WARNING")
            update_file_status(db_path, norm_path, "skipped", error_message="Invalid PDF format")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        if not is_file_in_date_range(file_path, min_date, max_date):
            if max_date:
                log_message(f"Skipping file outside date range ({min_date} to {max_date}): {file_path}")
                update_file_status(db_path, norm_path, "skipped", error_message=f"Outside date range {min_date} to {max_date}")
            else:
                log_message(f"Skipping file created before {min_date}: {file_path}")
                update_file_status(db_path, norm_path, "skipped", error_message=f"Created before {min_date}")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        send_process_heartbeat(f"Checking stability of {filename}", "Checking")
        update_dashboard_state('file_progress', {
            'filename': filename,
            'status': 'Checking stability'
        })
        
        retry = 0
        max_retries = 3
        while retry < max_retries:
            try:
                with open(file_path, 'rb'):
                    if test_file_stable(file_path):
                        break
                log_message(f"File unstable, retrying ({retry+1}/{max_retries}): {filename}", "WARNING")
            except Exception as e:
                log_message(f"File access error, retrying ({retry+1}/{max_retries}): {filename}", "WARNING")
            
            time.sleep(2 ** retry)
            retry += 1
        
        if retry >= max_retries:
            log_message(f"File unstable after {max_retries} attempts: {file_path}", "ERROR")
            update_file_status(db_path, norm_path, "error", error_message="File unstable or locked")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        original_size_mb = get_file_size_mb(file_path)
        
        if original_size_mb < 0.1:
            log_message(f"Skipping very small file ({original_size_mb}MB): {filename}")
            update_file_status(db_path, norm_path, "skipped", 
                             original_size_mb=original_size_mb,
                             error_message="File too small for compression")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        send_process_heartbeat(f"Preparing compression for {filename}", "Preparing")
        update_dashboard_state('file_progress', {
            'filename': filename,
            'status': 'Preparing'
        })
        
        safe_input_path, is_input_copy = copy_to_safe_location(file_path)
        
        temp_output_file = create_safe_temp_path(file_path, "_output")
        
        if os.path.abspath(safe_input_path).lower() == os.path.abspath(temp_output_file).lower():
            temp_output_file = create_safe_temp_path(file_path, f"_output_{int(time.time())}")
        
        gs_args = [
            ghostscript_path,
            "-sDEVICE=pdfwrite",
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            "-dSAFER",
            f"-dPDFSETTINGS={pdf_settings}",
            f"-sOutputFile={temp_output_file}",
            safe_input_path
        ]
        
        log_message(f"Compressing {filename} ({original_size_mb}MB)")
        log_message(f"Input: {safe_input_path}", "DEBUG")
        log_message(f"Output: {temp_output_file}", "DEBUG")
        log_message(f"Ghostscript command: {' '.join(gs_args)}", "DEBUG")
        
        send_process_heartbeat(f"Compressing {filename} - this may take a while", "Compressing")
        update_dashboard_state('file_progress', {
            'filename': filename,
            'status': 'Compressing'
        })
        
        try:
            process = subprocess.Popen(
                gs_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=local_temp_dir if local_temp_dir and os.path.exists(local_temp_dir) else None
            )
            
            start_time = time.time()
            while process.poll() is None:
                elapsed = time.time() - start_time
                if elapsed > 30:
                    send_process_heartbeat(f"Still compressing {filename} ({elapsed:.0f}s elapsed)", "Compressing")
                    start_time = time.time()
                time.sleep(5)
            
            stdout, stderr = process.communicate(timeout=300)
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore').strip()
                if not error_msg and stdout:
                    error_msg = stdout.decode('utf-8', errors='ignore').strip()
                if not error_msg:
                    error_msg = f"Ghostscript returned code {process.returncode}"
                
                log_message(f"Ghostscript error for {filename}: {error_msg}", "ERROR")
                update_file_status(db_path, norm_path, "error", 
                                 original_size_mb=original_size_mb,
                                 error_message=error_msg[:500])
                update_dashboard_state('file_complete', {'filename': filename})
                send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
                return
                
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.wait(timeout=5)
            except:
                pass
            log_message(f"Compression timed out: {filename}", "ERROR")
            update_file_status(db_path, norm_path, "error", 
                             original_size_mb=original_size_mb,
                             error_message="Compression timeout")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
            
        except Exception as e:
            log_message(f"Subprocess error for {filename}: {e}", "ERROR")
            update_file_status(db_path, norm_path, "error", 
                             original_size_mb=original_size_mb,
                             error_message=f"Subprocess error: {str(e)[:500]}")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        send_process_heartbeat(f"Validating output for {filename}", "Validating")
        update_dashboard_state('file_progress', {
            'filename': filename,
            'status': 'Validating output'
        })
        
        if not os.path.exists(temp_output_file):
            log_message(f"No output file created for: {filename}", "ERROR")
            update_file_status(db_path, norm_path, "error", 
                             original_size_mb=original_size_mb,
                             error_message="No output file created")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        if not validate_pdf_file(temp_output_file):
            log_message(f"Compressed file is invalid: {filename}", "ERROR")
            update_file_status(db_path, norm_path, "error", 
                             original_size_mb=original_size_mb,
                             error_message="Compressed file is invalid")
            update_dashboard_state('file_complete', {'filename': filename})
            send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
            return
        
        compressed_size_mb = get_file_size_mb(temp_output_file)
        
        send_process_heartbeat(f"Finalizing {filename}", "Finalizing")
        update_dashboard_state('file_progress', {
            'filename': filename,
            'status': 'Finalizing'
        })
        
        min_reduction_threshold = 0.05
        if compressed_size_mb < original_size_mb * (1 - min_reduction_threshold):
            backup_path = f"{file_path}.backup"
            try:
                shutil.copy2(file_path, backup_path)
                
                shutil.move(temp_output_file, file_path)
                temp_output_file = None
                
                os.remove(backup_path)
                
                compression_ratio = ((original_size_mb - compressed_size_mb) / original_size_mb) * 100
                saved_mb = original_size_mb - compressed_size_mb
                
                log_message(f"SUCCESS: {filename} "
                           f"{original_size_mb}MB → {compressed_size_mb}MB "
                           f"({compression_ratio:.1f}% reduction, {saved_mb:.2f}MB saved)", "SUCCESS")
                
                update_file_status(db_path, norm_path, "processed",
                                 original_size_mb=original_size_mb,
                                 compressed_size_mb=compressed_size_mb,
                                 compression_ratio=compression_ratio)
                
            except Exception as e:
                log_message(f"Error replacing file {filename}: {e}", "ERROR")
                if os.path.exists(backup_path):
                    try:
                        shutil.move(backup_path, file_path)
                        log_message(f"Restored from backup: {filename}")
                    except Exception:
                        pass
                
                update_file_status(db_path, norm_path, "error", 
                                 original_size_mb=original_size_mb,
                                 error_message=f"File replacement error: {str(e)[:500]}")
                update_dashboard_state('file_complete', {'filename': filename})
                send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
                return
        else:
            compression_ratio = ((original_size_mb - compressed_size_mb) / original_size_mb) * 100
            log_message(f"Minimal benefit: {filename} "
                       f"({original_size_mb}MB → {compressed_size_mb}MB, {compression_ratio:.1f}%)")
            
            update_file_status(db_path, norm_path, "processed",
                             original_size_mb=original_size_mb,
                             compressed_size_mb=original_size_mb,
                             compression_ratio=0)
        
        if config.get("LoggingEnabled") and log_dir:
            try:
                csv_file = os.path.join(log_dir, "compression_results.csv")
                with log_lock:
                    df = pd.DataFrame([{
                        "FileName": filename,
                        "OriginalSizeMB": original_size_mb,
                        "CompressedSizeMB": compressed_size_mb,
                        "ReductionPercent": compression_ratio if 'compression_ratio' in locals() else 0,
                        "SavedMB": max(0, original_size_mb - compressed_size_mb),
                        "ProcessedAt": datetime.now().isoformat()
                    }])
                    df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)
            except Exception as e:
                log_message(f"Error writing to CSV: {e}", "WARNING")
        
        with counter_lock:
            processed_count.value += 1
            if total_files.value > 0:
                progress = (processed_count.value / total_files.value) * 100
                log_message(f"Progress: {processed_count.value}/{total_files.value} ({progress:.1f}%)")
        
        send_process_heartbeat(f"Completed {filename} successfully", "Completed")
        update_dashboard_state('file_complete', {'filename': filename})
        
        log_message(f"Worker {process_name} completed processing {filename}")
        send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
        
    except Exception as e:
        log_message(f"Unexpected error processing {filename if 'filename' in locals() else 'unknown file'}: {e}", "ERROR")
        if 'norm_path' in locals():
            update_file_status(db_path, norm_path, "error", error_message=str(e)[:500])
        if 'filename' in locals():
            update_dashboard_state('file_complete', {'filename': filename})
        process_name = mp.current_process().name
        send_process_heartbeat(f"Worker {process_name} waiting for next task", "Idle")
    
    finally:
        cleanup_files = []
        
        if temp_output_file and os.path.exists(temp_output_file):
            cleanup_files.append(temp_output_file)
        
        if is_input_copy and safe_input_path and safe_input_path != file_path and os.path.exists(safe_input_path):
            cleanup_files.append(safe_input_path)
        
        for temp_file in cleanup_files:
            try:
                os.remove(temp_file)
                log_message(f"Cleaned up: {temp_file}", "DEBUG")
            except Exception as e:
                log_message(f"Cleanup error for {temp_file}: {e}", "WARNING")

class PDFWatcher(FileSystemEventHandler):
    
    def __init__(self, file_queue, db_path, min_date, max_date):
        self.file_queue = file_queue
        self.db_path = db_path
        self.min_date = min_date
        self.max_date = max_date
        super().__init__()
    
    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file_event(event.src_path, "CREATED")
    
    def on_moved(self, event):
        if event.is_directory:
            return
        self._process_file_event(event.dest_path, "MOVED")
    
    def _process_file_event(self, file_path, event_type):
        try:
            if not file_path or not os.path.exists(file_path):
                return
            
            if not file_path.lower().endswith('.pdf'):
                return
            
            filename_lower = os.path.basename(file_path).lower()
            skip_patterns = ['.tmp.', '.backup', 'temp_', 'tmpprocessing']
            if any(pattern in file_path.lower() for pattern in skip_patterns):
                return
            
            norm_path = os.path.normpath(os.path.abspath(file_path)).lower()
            filename = os.path.basename(file_path)
            
            log_message(f"Watcher detected {event_type}: {filename}")
            
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_dashboard_state('polling', {'timestamp': current_timestamp})
            
            status = check_file_status(self.db_path, norm_path)
            if status in ["processed", "skipped"]:
                log_message(f"Skipping already {status} file: {filename}")
                return
            
            if norm_path in self.file_queue:
                log_message(f"File already queued: {filename}")
                return
            
            if len(file_path) > 250:
                log_message(f"Path too long (>{250} chars): {file_path}", "WARNING")
                update_file_status(self.db_path, norm_path, "skipped", 
                                 error_message="Path too long")
                return
            
            if is_file_in_date_range(file_path, self.min_date, self.max_date):
                log_message(f"Queueing new PDF: {filename}")
                self.file_queue.append(norm_path)
            else:
                if self.max_date:
                    log_message(f"File outside date range ({self.min_date} to {self.max_date}): {filename}")
                    update_file_status(self.db_path, norm_path, "skipped", 
                                     error_message=f"Outside date range {self.min_date} to {self.max_date}")
                else:
                    log_message(f"File created before {self.min_date}: {filename}")
                    update_file_status(self.db_path, norm_path, "skipped", 
                                     error_message=f"Created before {self.min_date}")
                
        except Exception as e:
            log_message(f"Error processing file event for {file_path}: {e}", "ERROR")

def scan_existing_files(watch_folder, file_queue, db_path, min_date, max_date, batch_size=1000):
    log_message("Starting initial file scan")
    
    try:
        total_found = 0
        queued_count = 0
        skipped_count = 0
        
        pdf_files = Path(watch_folder).rglob("*.pdf")
        
        batch = []
        for pdf_file in pdf_files:
            try:
                file_path = str(pdf_file)
                
                skip_patterns = ['.tmp.', '.backup', 'temp_', 'tmpprocessing']
                if any(pattern in file_path.lower() for pattern in skip_patterns):
                    continue
                
                total_found += 1
                
                batch.append(file_path)
                if len(batch) >= batch_size:
                    queued, skipped = _process_file_batch(batch, file_queue, db_path, min_date, max_date)
                    queued_count += queued
                    skipped_count += skipped
                    batch = []
                    
                    if total_found % 500 == 0:
                        log_message(f"Scan progress: {total_found} files found, "
                                   f"{queued_count} queued, {skipped_count} skipped")
            
            except Exception as e:
                log_message(f"Error processing file during scan: {pdf_file} - {e}", "ERROR")
                skipped_count += 1
        
        if batch:
            queued, skipped = _process_file_batch(batch, file_queue, db_path, min_date, max_date)
            queued_count += queued
            skipped_count += skipped
        
        log_message(f"Initial scan completed: {total_found} files found, "
                   f"{queued_count} queued for processing, {skipped_count} skipped")
        
        return queued_count, skipped_count
        
    except Exception as e:
        log_message(f"Error during initial file scan: {e}", "ERROR")
        return 0, 0

def _process_file_batch(file_batch, file_queue, db_path, min_date, max_date):
    queued = 0
    skipped = 0
    
    for file_path in file_batch:
        try:
            if not os.path.exists(file_path):
                skipped += 1
                continue
            
            norm_path = os.path.normpath(os.path.abspath(file_path)).lower()
            
            status = check_file_status(db_path, norm_path)
            if status in ["processed", "skipped"]:
                continue
            
            if norm_path in file_queue:
                continue
            
            if len(file_path) > 250:
                update_file_status(db_path, norm_path, "skipped", 
                                 error_message="Path too long")
                skipped += 1
                continue
            
            if not validate_pdf_file(file_path):
                update_file_status(db_path, norm_path, "skipped", 
                                 error_message="Invalid PDF format")
                skipped += 1
                continue
            
            if is_file_in_date_range(file_path, min_date, max_date):
                file_queue.append(norm_path)
                queued += 1
            else:
                if max_date:
                    update_file_status(db_path, norm_path, "skipped", 
                                     error_message=f"Outside date range {min_date} to {max_date}")
                else:
                    update_file_status(db_path, norm_path, "skipped", 
                                     error_message=f"Created before {min_date}")
                skipped += 1
                
        except Exception as e:
            log_message(f"Error processing file in batch {file_path}: {e}", "ERROR")
            skipped += 1
    
    return queued, skipped

def periodic_scan(watch_folder, file_queue, db_path, min_date, max_date, last_scan_time, scan_interval=300):
    current_time = time.time()
    
    if (current_time - last_scan_time) < scan_interval:
        return last_scan_time
    
    log_message("Starting periodic file scan")
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_dashboard_state('polling', {'timestamp': current_timestamp})
    
    try:
        queued, skipped = scan_existing_files(watch_folder, file_queue, db_path, min_date, max_date, batch_size=500)
        log_message(f"Periodic scan completed: {queued} queued, {skipped} skipped")
        
        stats = get_compression_stats(db_path)
        if stats.get('total_processed', 0) > 0:
            log_message(f"Compression stats: {stats['total_processed']} files processed, "
                       f"{stats['total_saved_mb']:.2f}MB saved "
                       f"(avg {stats['avg_compression_ratio']:.1f}% reduction)")
            
            update_dashboard_state('stats', stats)
        
    except Exception as e:
        log_message(f"Error during periodic scan: {e}", "ERROR")
    
    return current_time

def cleanup_temp_directory():
    try:
        if not local_temp_dir or not os.path.exists(local_temp_dir):
            return
        
        current_time = time.time()
        cleanup_count = 0
        
        for filename in os.listdir(local_temp_dir):
            if filename.startswith('temp_') and filename.endswith('.pdf'):
                file_path = os.path.join(local_temp_dir, filename)
                try:
                    if current_time - os.path.getmtime(file_path) > 3600:
                        os.remove(file_path)
                        cleanup_count += 1
                except Exception as e:
                    log_message(f"Error cleaning up temp file {filename}: {e}", "WARNING")
        
        if cleanup_count > 0:
            log_message(f"Cleaned up {cleanup_count} old temporary files")
            
    except Exception as e:
        log_message(f"Error during temp directory cleanup: {e}", "WARNING")

def load_state(db_path: str, json_path: str) -> Tuple[set, set]:
    log_message(f"Loading state from {json_path} or {db_path}")
    processed_files = set()
    skipped_files = set()
    
    if os.path.exists(json_path):
        try:
            log_message(f"Loading legacy JSON state: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            processed_files = set(state.get("Processed", []))
            skipped_files = set(state.get("Skipped", []))
            log_message(f"Loaded {len(processed_files)} processed and {len(skipped_files)} skipped files from JSON")
        except Exception as e:
            log_message(f"Error loading JSON state: {e}", "WARNING")
    
    try:
        init_sqlite_db(db_path, processed_files, skipped_files)
    except Exception as e:
        log_message(f"Failed to initialize SQLite database: {e}", "ERROR")
        raise
    
    return processed_files, skipped_files

def check_file_status(db_path: str, norm_path: str) -> Optional[str]:
    try:
        with sqlite_connection(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM files WHERE path = ?", (norm_path,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        log_message(f"Error checking status for {norm_path}: {e}", "ERROR")
        return None

def update_file_status(db_path: str, norm_path: str, status: str, **kwargs):
    try:
        with sqlite_connection(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(files)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            fields = ["path", "status"]
            values = [norm_path, status]
            placeholders = ["?", "?"]
            
            column_mapping = {
                'original_size_mb': 'original_size_mb',
                'compressed_size_mb': 'compressed_size_mb', 
                'compression_ratio': 'compression_ratio',
                'error_message': 'error_message'
            }
            
            for key, value in kwargs.items():
                if key in column_mapping and column_mapping[key] in existing_columns:
                    fields.append(column_mapping[key])
                    values.append(value)
                    placeholders.append("?")
            
            query = f"""
                INSERT OR REPLACE INTO files ({', '.join(fields)}) 
                VALUES ({', '.join(placeholders)})
            """
            
            cursor.execute(query, values)
            conn.commit()
            
    except Exception as e:
        log_message(f"Error updating status for {norm_path}: {e}", "ERROR")

def get_compression_stats(db_path: str) -> Dict[str, Any]:
    try:
        with sqlite_connection(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(files)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if 'original_size_mb' not in existing_columns:
                cursor.execute('SELECT COUNT(*) FROM files WHERE status = "processed"')
                result = cursor.fetchone()
                return {
                    'total_processed': result[0] if result else 0,
                    'total_original_mb': 0,
                    'total_compressed_mb': 0,
                    'avg_compression_ratio': 0,
                    'total_saved_mb': 0
                }
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_processed,
                    COALESCE(SUM(original_size_mb), 0) as total_original_mb,
                    COALESCE(SUM(compressed_size_mb), 0) as total_compressed_mb,
                    COALESCE(AVG(compression_ratio), 0) as avg_compression_ratio
                FROM files 
                WHERE status = 'processed' AND original_size_mb IS NOT NULL
            ''')
            result = cursor.fetchone()
            
            if result:
                return {
                    'total_processed': result[0] or 0,
                    'total_original_mb': result[1] or 0,
                    'total_compressed_mb': result[2] or 0,
                    'avg_compression_ratio': result[3] or 0,
                    'total_saved_mb': (result[1] or 0) - (result[2] or 0)
                }
            else:
                return {
                    'total_processed': 0,
                    'total_original_mb': 0,
                    'total_compressed_mb': 0,
                    'avg_compression_ratio': 0,
                    'total_saved_mb': 0
                }
                
    except Exception as e:
        log_message(f"Error getting compression stats: {e}", "ERROR")
        return {
            'total_processed': 0,
            'total_original_mb': 0,
            'total_compressed_mb': 0,
            'avg_compression_ratio': 0,
            'total_saved_mb': 0
        }

def main():
    global dashboard_queue
    
    killer = GracefulKiller()
    
    dashboard_queue = Queue(maxsize=2000)
    
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    try:
        config_valid, config_dict = load_and_validate_config()
        if not config_valid:
            sys.exit(1)
        
        watch_folder = config_dict['watch_folder']
        ghostscript_path = config_dict['ghostscript_path']
        pdf_settings = config_dict['pdf_settings']
        min_date = config_dict['min_date']
        max_date = config_dict['max_date']
        num_processes = config_dict['num_processes']
        log_file = config_dict['log_file']
        log_dir = config_dict['log_dir']
        enable_initial_scan = config_dict['enable_initial_scan']
        
        if config.get("LoggingEnabled"):
            logger = setup_logging(log_file)
            log_message("PDF Compression Monitor started")
        
        if not validate_environment(config_dict):
            sys.exit(1)
        
        log_message("Testing SQLite database access")
        try:
            test_sqlite_write()
        except Exception as e:
            log_message(f"SQLite test failed: {e}", "ERROR")
            sys.exit(1)
        
        log_message("Loading application state")
        try:
            processed_files, skipped_files = load_state(STATE_DB, r"C:\pdfTask\py\pdfc_state.json")
        except Exception as e:
            log_message(f"Failed to load state: {e}", "ERROR")
            sys.exit(1)
        
        log_message("Initializing multiprocessing components")
        manager = Manager()
        file_queue = manager.list()
        counter_lock = manager.Lock()
        processed_count = manager.Value('i', 0)
        total_files = manager.Value('i', 0)
        
        log_message(f"Using {num_processes} processes for compression")
        
        if enable_initial_scan:
            log_message("Performing initial file scan (EnableInitialScan=true)")
            try:
                queued_count, skipped_count = scan_existing_files(watch_folder, file_queue, STATE_DB, min_date, max_date)
                log_message(f"Initial scan results: {queued_count} files queued, {skipped_count} skipped")
                
                if queued_count > 0:
                    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update_dashboard_state('polling', {'timestamp': current_timestamp})
                    
            except Exception as e:
                log_message(f"Initial scan failed: {e}", "ERROR")
                sys.exit(1)
        else:
            log_message("Skipping initial file scan (EnableInitialScan=false)")
            queued_count, skipped_count = 0, 0
        
        log_message("Setting up file system watcher")
        try:
            observer = Observer()
            watcher = PDFWatcher(file_queue, STATE_DB, min_date, max_date)
            observer.schedule(watcher, watch_folder, recursive=True)
            observer.start()
            log_message("File system watcher started")
        except Exception as e:
            log_message(f"Failed to setup file watcher: {e}", "ERROR")
            sys.exit(1)
        
        log_message("Initializing processing pool with shared resources")
        pool = Pool(
            processes=num_processes,
            initializer=initialize_worker_process,
            initargs=(dashboard_queue,)
        )
        
        log_message("=== MONITORING ACTIVE ===")
        log_message(f"Watch Folder: {watch_folder}")
        log_message(f"Local Temp Dir: {local_temp_dir}")
        log_message(f"Min Creation Date: {config['MinCreationDate']}")
        if config.get('MaxCreationDate'):
            log_message(f"Max Creation Date: {config['MaxCreationDate']}")
        log_message(f"PDF Settings: {pdf_settings}")
        log_message(f"Log File: {log_file}")
        log_message(f"Processes: {num_processes}")
        log_message(f"Initial queue: {len(file_queue)} files")
        
        last_scan_time = time.time()
        last_heartbeat = time.time()
        last_cleanup = time.time()
        heartbeat_interval = 60
        scan_interval = 300
        cleanup_interval = 1800
        batch_size = num_processes
        
        try:
            while not killer.kill_now.is_set():
                current_time = time.time()
                
                if (current_time - last_heartbeat) >= heartbeat_interval:
                    queue_size = len(file_queue)
                    if queue_size > 0:
                        log_message(f"Heartbeat: {queue_size} files in queue")
                    else:
                        log_message("Heartbeat: System monitoring, no files in queue")
                    
                    update_dashboard_state('heartbeat', {'queue_size': queue_size})
                    last_heartbeat = current_time
                
                if (current_time - last_cleanup) >= cleanup_interval:
                    cleanup_temp_directory()
                    last_cleanup = current_time
                
                if len(file_queue) > 0:
                    if total_files.value == 0:
                        total_files.value = len(file_queue)
                        processed_count.value = 0
                        log_message(f"Starting batch processing of {total_files.value} files")
                        
                        files_list = list(file_queue)
                        update_dashboard_state('batch_start', {
                            'total': total_files.value,
                            'files': files_list
                        })
                    
                    files_to_process = []
                    batch_count = 0
                    
                    while file_queue and batch_count < batch_size:
                        files_to_process.append(file_queue.pop(0))
                        batch_count += 1
                    
                    if files_to_process:
                        log_message(f"Processing batch of {len(files_to_process)} files across {num_processes} processes")
                        
                        args_list = [
                            (f, STATE_DB, counter_lock, processed_count, total_files, 
                             pdf_settings, ghostscript_path, min_date, max_date, log_dir) 
                            for f in files_to_process
                        ]
                        
                        try:
                            result = pool.map_async(compress_pdf, args_list)
                            result.get(timeout=600)
                            log_message(f"Batch of {len(files_to_process)} files completed successfully")
                        except Exception as e:
                            log_message(f"Error in batch processing: {e}", "ERROR")
                            for file_path in files_to_process:
                                file_queue.append(file_path)
                    
                    if len(file_queue) == 0 and total_files.value > 0:
                        stats = get_compression_stats(STATE_DB)
                        log_message(f"Batch processing completed! "
                                   f"Processed: {stats.get('total_processed', 0)} files, "
                                   f"Saved: {stats.get('total_saved_mb', 0):.2f}MB")
                        
                        dashboard_state['files_being_processed'] = []
                        dashboard_state['files_in_queue'] = 0
                        
                        update_dashboard_state('stats', stats)
                        total_files.value = 0
                        processed_count.value = 0
                
                last_scan_time = periodic_scan(watch_folder, file_queue, STATE_DB, min_date, max_date,
                                             last_scan_time, scan_interval)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            log_message("Received interrupt signal, sending TERM signal...")
            killer.kill_now.set()
        
        except Exception as e:
            log_message(f"Error in main processing loop: {e}", "ERROR")
        
        finally:
            log_message("Shutting down...")
            
            if 'pool' in locals():
                log_message("Terminating processing pool...")
                pool.terminate()
                pool.join()
                log_message("Processing pool terminated")
            
            if 'observer' in locals():
                log_message("Stopping file system watcher...")
                observer.stop()
                observer.join()
                log_message("File system watcher stopped")
            
            cleanup_temp_directory()
            
            try:
                stats = get_compression_stats(STATE_DB)
                if stats.get('total_processed', 0) > 0:
                    log_message(f"Final statistics: "
                               f"{stats['total_processed']} files processed, "
                               f"{stats['total_saved_mb']:.2f}MB saved, "
                               f"Average compression: {stats['avg_compression_ratio']:.1f}%")
                    
                    update_dashboard_state('stats', stats)
            except Exception as e:
                log_message(f"Error getting final statistics: {e}", "WARNING")
            
            log_message("PDF Compression Monitor stopped")
    
    except Exception as e:
        log_message(f"Critical error in main function: {e}", "ERROR")
        sys.exit(1)

if __name__ == '__main__':
    try:
        from rich.console import Console
        main()
    except ImportError:
        print("Rich library not found. Please install it with: pip install rich")
        print("Falling back to console mode...")
        
        USE_COLORS = True
        
        def update_dashboard_state(*args, **kwargs):
            pass
        
        main()
