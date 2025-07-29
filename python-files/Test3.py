import sys
sys.path.append("C:\\Users\\Daniel.APOLLO\\Desktop\\MC servers")

import socket
import time
import subprocess
import os
import psutil
import subprocess
import threading


###### SERVER HOST FOR A SERVER #######
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('26.185.66.247', 9999))

server.listen(10)

print("Started")

### SERVER VARIABLES
is_running = False
server_process = None  # Keep track of the server process

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def kill_playit():
    # Kill all playit.exe processes (your original working code)
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == "playit.exe":
            proc.terminate()

while True:
    client, addr = server.accept()

    if is_running:
        client.send("\n\n\nServer is Currently running at IP:\n privacy-trout.gl.joinmc.link".encode())
    else:
        client.send("\n\n\nServer is currently offline".encode())

    client.send("\n\n\nWhat would you like to do?\n1) Start Server \n2) Stop Server\nPlease input 1 or 2".encode())

    received_bytes = client.recv(1024)
    client_choice = received_bytes.decode("utf-8").strip()

    print(f"Client choice: {client_choice}")

    if client_choice == "1":
        if not is_running:
            # Launch playit.exe first
            os.startfile("C:\\Users\\Daniel.APOLLO\\Desktop\\playit.exe")

            # Start the Minecraft server process
            server_dir = r"C:\Users\Daniel.APOLLO\Desktop\MC servers\Super SMP"
            java_cmd = [
                "java",
                "@user_jvm_args.txt",
                "@libraries/net/minecraftforge/forge/1.20.1-47.4.4/win_args.txt"
            ]


            server_process = subprocess.Popen(
                java_cmd,
                cwd=server_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # === DISPLAY OUTPUT IN REAL TIME ===
            def stream_output():
                for line in server_process.stdout:
                    print("[MC SERVER]", line.strip())

            threading.Thread(target=stream_output, daemon=True).start()
            is_running = True

            client.send("\n\n\nServer starting".encode())
            time.sleep(15)  # Wait a bit for the server to start
            client.send("\n\n\nServer started".encode())
        else:
            client.send("\n\n\nServer is already online".encode())

    elif client_choice == "2":
        if is_running and server_process:
            try:
                # Send the stop command to the Minecraft server
                server_process.stdin.write("stop\n")
                server_process.stdin.flush()
                client.send("\n\n\nStopping server...".encode())

                # Wait for the server to shut down gracefully
                server_process.wait(timeout=30)
                client.send("\n\n\nServer stopped gracefully.".encode())
            except subprocess.TimeoutExpired:
                client.send("\n\n\nServer did not stop in time, killing process.".encode())
                server_process.kill()
                server_process.wait()
                client.send("\n\n\nServer killed.".encode())
            finally:
                # Kill playit.exe
                kill_playit()

                is_running = False
                server_process = None

                # Clear the Python console
                clear_console()
                print("Server stopped. Console cleared.")
        else:
            client.send("\n\n\nServer is not running.".encode())

    client.close()