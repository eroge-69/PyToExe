import platform
import psutil
import datetime
import socket

def get_size(bytes, suffix="B"):
    """Convert bytes to readable format"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def generate_report():
    report = []
    report.append("=== SYSTEM PERFORMANCE REPORT ===\n")

    # System Info
    uname = platform.uname()
    report.append(f"System: {uname.system}")
    report.append(f"Node Name: {uname.node}")
    report.append(f"Release: {uname.release}")
    report.append(f"Version: {uname.version}")
    report.append(f"Machine: {uname.machine}")
    report.append(f"Processor: {uname.processor}")
    report.append(f"IP Address: {socket.gethostbyname(socket.gethostname())}\n")

    # Boot Time
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    report.append(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # CPU Info
    report.append("=== CPU INFO ===")
    report.append(f"Physical cores: {psutil.cpu_count(logical=False)}")
    report.append(f"Total cores: {psutil.cpu_count(logical=True)}")
    report.append(f"CPU usage per core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        report.append(f"  Core {i}: {percentage}%")
    report.append(f"Total CPU Usage: {psutil.cpu_percent()}%\n")

    # Memory Info
    svmem = psutil.virtual_memory()
    report.append("=== MEMORY INFO ===")
    report.append(f"Total: {get_size(svmem.total)}")
    report.append(f"Available: {get_size(svmem.available)}")
    report.append(f"Used: {get_size(svmem.used)}")
    report.append(f"Percentage: {svmem.percent}%\n")

    # Disk Info
    report.append("=== DISK INFO ===")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            report.append(f"Drive: {partition.device}")
            report.append(f"  Total Size: {get_size(usage.total)}")
            report.append(f"  Used: {get_size(usage.used)}")
            report.append(f"  Free: {get_size(usage.free)}")
            report.append(f"  Percentage: {usage.percent}%\n")
        except PermissionError:
            continue

    # Top CPU-consuming processes
    report.append("=== TOP 5 CPU USAGE PROCESSES ===")
    processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
    for proc in processes:
        report.append(f"PID={proc.info['pid']}, Name={proc.info['name']}, CPU={proc.info['cpu_percent']}%")

    # Top Memory-consuming processes
    report.append("\n=== TOP 5 MEMORY USAGE PROCESSES ===")
    processes = sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), key=lambda p: p.info['memory_percent'], reverse=True)[:5]
    for proc in processes:
        report.append(f"PID={proc.info['pid']}, Name={proc.info['name']}, Memory={proc.info['memory_percent']:.2f}%")

    # Save to file
    with open("system_report.txt", "w") as f:
        f.write("\n".join(report))

    print("✅ Report generated: system_report.txt")

if __name__ == "__main__":
    generate_report()
