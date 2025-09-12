import psutil
import os
import datetime
import time
from rich.console import Console
from rich.table import Table

console = Console()

# Log file for deleted executables
DELETED_LOG = "deleted_exe_log.txt"
SCAN_INTERVAL = 5  # seconds between scans

# Track previously seen PIDs to avoid duplicate log entries
logged_pids = set()

def get_exe_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'exe']):
        try:
            name = proc.info['name'] or "N/A"
            pid = proc.info['pid']
            exe_path = proc.info['exe']
            if exe_path and exe_path.lower().endswith('.exe'):
                start_time = datetime.datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                file_exists = os.path.exists(exe_path)
                status = "FILE EXISTS" if file_exists else "DELETED"
                processes.append((status, name, pid, start_time, exe_path))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def log_deleted_process(proc_info):
    status, name, pid, start_time, path = proc_info
    if pid in logged_pids:
        return  # Already logged
    with open(DELETED_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] DELETED EXE: {name} (PID: {pid}) | Started: {start_time} | Path: {path}\n")
    logged_pids.add(pid)

def print_exe_table(processes):
    table = Table(title="🧠 Real-Time .exe Monitor (with Deleted Detection)", show_lines=False)
    table.add_column("STATUS", style="bold green")
    table.add_column("Name", style="cyan")
    table.add_column("PID", style="magenta")
    table.add_column("Started", style="yellow")
    table.add_column("Path", style="white")

    for status, name, pid, start_time, path in sorted(processes, key=lambda x: x[3], reverse=True):
        color = "green" if status == "FILE EXISTS" else "bold red"
        table.add_row(f"[{color}]{status}[/{color}]", name, str(pid), start_time, path)

    console.clear()
    console.print(table)

def monitor_loop():
    console.print("[bold cyan]🔍 Starting Real-Time .exe Monitor... Press Ctrl+C to stop[/bold cyan]\n")
    while True:
        try:
            processes = get_exe_processes()
            print_exe_table(processes)

            for proc_info in processes:
                if proc_info[0] == "DELETED":
                    log_deleted_process(proc_info)

            time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            console.print("\n[bold red]🛑 Monitoring stopped by user.[/bold red]")
            break

if __name__ == "__main__":
    monitor_loop()
    input("\nPress Enter to exit...")