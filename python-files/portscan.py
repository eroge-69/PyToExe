import psutil
import platform
import subprocess
import re
import os
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

def get_connection_by_port(port):
    """Retrieve network connection details for a given port."""
    try:
        conns = psutil.net_connections(kind='inet')
        for conn in conns:
            if getattr(conn, 'laddr', None) and conn.laddr.port == port:
                return conn
        return None
    except psutil.AccessDenied:
        return None

def get_process_info(pid):
    """Retrieve information about a process by its PID."""
    try:
        proc = psutil.Process(pid)
        return {
            'name': proc.name(),
            'exe': proc.exe(),
            'cmdline': proc.cmdline(),
            'username': proc.username(),
            'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return {'error': f"Unable to retrieve process info: {str(e)}"}

def get_tasklist_info(pid):
    """Retrieve tasklist details for a PID on Windows."""
    if platform.system() != "Windows":
        return {"image_name": "Not supported", "pid": "N/A", "session_name": "N/A", 
                "session_num": "N/A", "mem_usage": "N/A"}
    try:
        result = subprocess.check_output(
            f'tasklist /fi "PID eq {pid}" /fo csv',
            shell=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        lines = result.strip().split('\n')
        for line in lines[1:]:  # Skip header
            if f'"{pid}"' in line:
                # Parse CSV line
                parts = line.strip().split('","')
                if len(parts) >= 5:
                    return {
                        "image_name": parts[0].strip('"'),
                        "pid": parts[1].strip('"'),
                        "session_name": parts[2].strip('"'),
                        "session_num": parts[3].strip('"'),
                        "mem_usage": parts[4].strip('"')
                    }
        return {"image_name": "N/A", "pid": str(pid), "session_name": "N/A", 
                "session_num": "N/A", "mem_usage": "N/A"}
    except subprocess.CalledProcessError:
        return {"image_name": "Error", "pid": str(pid), "session_name": "Error", 
                "session_num": "Error", "mem_usage": "Error"}

def get_services_windows(pid):
    """Retrieve all services associated with a PID on Windows."""
    if platform.system() != "Windows":
        return "Not supported on non-Windows."
    try:
        result = subprocess.check_output(
            f'tasklist /svc /fi "PID eq {pid}"',
            shell=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        lines = result.strip().split('\n')
        for line in lines[2:]:  # Skip header and separator
            if str(pid) in line:
                parts = line.split()
                if len(parts) > 2:
                    return parts[2] if parts[2] != "N/A" else "None"
        return "None"
    except subprocess.CalledProcessError:
        return "Error retrieving services"

def check_signature_windows(exe_path):
    """Check the digital signature of an executable on Windows."""
    if not exe_path or platform.system() != "Windows":
        return {"status": "Not supported", "issuer": "N/A"}
    try:
        exe_path = re.sub(r'[&|;<>]', '', exe_path)  # Sanitize path
        cmd = f'powershell -Command "(Get-AuthenticodeSignature \'{exe_path}\').Status, (Get-AuthenticodeSignature \'{exe_path}\').SignerCertificate.Subject"'
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        status, issuer = result.strip().split('\n')
        issuer = issuer.split(',')[0] if ',' in issuer else issuer
        return {"status": status, "issuer": issuer}
    except subprocess.CalledProcessError:
        return {"status": "Error", "issuer": "N/A"}

def get_file_location_info(exe_path):
    """Retrieve file location details and metadata."""
    if not exe_path or not os.path.exists(exe_path):
        return {"location": "N/A", "is_system": "N/A", "file_size": "N/A", "file_created": "N/A"}
    try:
        is_system = "Yes" if any(exe_path.lower().startswith(path.lower()) for path in 
                                [r"C:\Windows\System32", r"C:\Windows\SysWOW64", r"C:\Program Files"]) else "No"
        file_stat = os.stat(exe_path)
        file_size = f"{file_stat.st_size / 1024:.2f} KB"
        file_created = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        return {
            "location": exe_path,
            "is_system": is_system,
            "file_size": file_size,
            "file_created": file_created
        }
    except (OSError, PermissionError):
        return {"location": exe_path, "is_system": "Error", "file_size": "Error", "file_created": "Error"}

def truncate_string(s, max_length=50):
    """Truncate string to prevent excessive length."""
    return s if len(s) <= max_length else s[:max_length-3] + "..."

def analyze_port(port):
    """Analyze a given port and return connection and process details."""
    result = {
        "Port": str(port),
        "Status": "No connection",
        "PID": "N/A",
        "Local Address": "N/A",
        "Remote Address": "N/A",
        "Process Name": "N/A",
        "Executable Path": "N/A",
        "Username": "N/A",
        "Command Line": "N/A",
        "Created": "N/A",
        "Services": "N/A",
        "Signature Status": "N/A",
        "Issuer": "N/A",
        "Image Name": "N/A",
        "Session Name": "N/A",
        "Session Number": "N/A",
        "Memory Usage": "N/A",
        "File Location": "N/A",
        "Is System Path": "N/A",
        "File Size": "N/A",
        "File Created": "N/A"
    }

    conn = get_connection_by_port(port)
    if not conn:
        return result

    result["Status"] = conn.status
    result["PID"] = str(conn.pid)
    result["Local Address"] = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
    result["Remote Address"] = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"

    proc_info = get_process_info(conn.pid)
    if 'error' not in proc_info:
        result["Process Name"] = truncate_string(proc_info['name'])
        result["Executable Path"] = truncate_string(proc_info['exe'])
        result["Username"] = truncate_string(proc_info['username'])
        result["Command Line"] = truncate_string(' '.join(proc_info['cmdline']))
        result["Created"] = proc_info['create_time']
        result["Services"] = truncate_string(get_services_windows(conn.pid))
        sig_info = check_signature_windows(proc_info['exe'])
        result["Signature Status"] = sig_info['status']
        result["Issuer"] = truncate_string(sig_info['issuer'])

        # Tasklist details
        task_info = get_tasklist_info(conn.pid)
        result["Image Name"] = truncate_string(task_info['image_name'])
        result["Session Name"] = truncate_string(task_info['session_name'])
        result["Session Number"] = task_info['session_num']
        result["Memory Usage"] = truncate_string(task_info['mem_usage'])

        # File location details
        loc_info = get_file_location_info(proc_info['exe'])
        result["File Location"] = truncate_string(loc_info['location'])
        result["Is System Path"] = loc_info['is_system']
        result["File Size"] = loc_info['file_size']
        result["File Created"] = loc_info['file_created']

    return result

def print_vertical_output(results):
    """Print results in a vertical, color-coded format."""
    print(f"\n{Style.BRIGHT}{Fore.GREEN}Port Analysis Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")
    for i, result in enumerate(results, 1):
        print(f"{Style.BRIGHT}{Fore.GREEN}--- Port {result['Port']} ---{Style.RESET_ALL}")
        for key, value in result.items():
            color = Fore.RED if value in ["No connection", "Not supported", "N/A", "None"] or "Error" in value else Fore.CYAN
            print(f"{Style.BRIGHT}{Fore.GREEN}{key:20}{Style.RESET_ALL}: {color}{value}{Style.RESET_ALL}")
        if i < len(results):
            print()  # Add spacing between ports

if __name__ == "__main__":
    try:
        user_input = input("Enter port number(s) to analyze (comma-separated, e.g., 80,443,445): ")
        ports = [int(p.strip()) for p in user_input.split(',')]
        invalid_ports = [p for p in ports if p < 0 or p > 65535]
        if invalid_ports:
            print(f"{Fore.RED}Invalid port number(s): {', '.join(map(str, invalid_ports))}. Ports must be between 0 and 65535.{Style.RESET_ALL}")
            exit(1)

        results = [analyze_port(port) for port in ports]
        print_vertical_output(results)

    except ValueError:
        print(f"{Fore.RED}Please enter valid port numbers (comma-separated).{Style.RESET_ALL}")