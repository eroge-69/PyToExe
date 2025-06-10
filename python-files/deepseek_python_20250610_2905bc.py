import socket
import psutil
import argparse
from datetime import datetime

def get_all_sockets():
    """Get all active TCP sockets"""
    sockets = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            conns = proc.connections(kind='tcp')
            for conn in conns:
                if conn.status == psutil.CONN_ESTABLISHED and conn.fd:
                    sockets.append((proc.pid, conn.fd, conn.laddr, conn.raddr))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return sockets

def set_tcp_nodelay(enable):
    """Enable or disable TCP_NODELAY on all sockets"""
    action = "Enabling" if enable else "Disabling"
    print(f"{action} TCP_NODELAY (Nagle's algorithm {'disabled' if enable else 'enabled'})")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    modified = 0
    for pid, fd, laddr, raddr in get_all_sockets():
        try:
            # Create a socket object from the file descriptor
            with socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM) as s:
                current = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
                if current != enable:
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, enable)
                    modified += 1
                    print(f"PID: {pid:6} | FD: {fd:3} | Local: {laddr[0]}:{laddr[1]:5} | "
                          f"Remote: {raddr[0]}:{raddr[1]:5} | Changed TCP_NODELAY to {enable}")
        except (OSError, socket.error) as e:
            print(f"Error modifying socket (PID: {pid}, FD: {fd}): {e}")
            continue
    
    print("-" * 50)
    print(f"Total sockets modified: {modified}")
    print(f"Operation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enable or disable TCP_NODELAY (Nagle's algorithm) on all sockets")
    parser.add_argument('action', choices=['enable', 'disable'], 
                       help="'enable' to enable TCP_NODELAY (disable Nagle's), 'disable' to disable TCP_NODELAY (enable Nagle's)")
    
    args = parser.parse_args()
    set_tcp_nodelay(args.action == 'enable')