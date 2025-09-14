import socket
import paramiko
import os
import traceback
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException, NoValidConnectionsError, AuthenticationException

def connect_and_get_info(ip, port, username, password):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())  # حفظ AutoAddPolicy
    try:
        ssh.connect(ip, port, username, password, timeout=10)
        
        info = {}
        commands = [
            ("Uptime", "uptime"),
            ("CPU Info", "cat /proc/cpuinfo | grep 'model name' | uniq"),
            ("RAM Info", "free -h"),
            ("Disk Info", "df -h")
        ]
        
        for desc, cmd in commands:
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                
                if output:
                    info[desc] = output
                elif error:
                    info[desc] = f"Command failed: {error}"
                else:
                    info[desc] = "No output received"
            except Exception as e:
                info[desc] = f"Command execution error: {str(e)}"
        
        return "good", info
        
    except (SSHException, NoValidConnectionsError, AuthenticationException, socket.error) as e:
        return "bad", f"Failed to connect to {ip}:{port}. Error: {e}"
    except Exception as e:
        return "bad", f"Unexpected error on {ip}. Error: {e}"
    finally:
        try:
            ssh.close()
        except:
            pass

def process_servers(input_file):
    with open("good.txt", "w") as good_file, open("bad.txt", "w") as bad_file:
        
        servers = []
        with open(input_file, "r") as file:
            servers = file.readlines()
        
        good_output = ""
        bad_output = ""
        
        for server_line in servers:
            try:
                server = server_line.strip()
                if not server or server.startswith('#') or server.isspace():
                    continue
                
                parts = server.split(':', 3)
                if len(parts) == 4:
                    ip, port_str, user, password = parts
                    try:
                        port = int(port_str)
                    except ValueError:
                        bad_output += f"Server: {server}\n"
                        bad_output += f"    Error: Invalid port number '{port_str}'\n"
                        bad_output += "--------------------------------------------------\n"
                        continue
                    
                    print(f"Processing server: {ip}:{port}")
                    status, result = connect_and_get_info(ip, port, user, password)
                    
                    if status == "good":
                        print(f"Server {ip}:{port} is GOOD.")
                        good_output += f"Server: {ip}:{port}\n"
                        for key, value in result.items():
                            good_output += f"    {key}: {value}\n"
                        good_output += "--------------------------------------------------\n"
                        
                    elif status == "bad":
                        print(f"Server {ip}:{port} is BAD.")
                        print(f"    Error: {result}")
                        bad_output += f"Server: {ip}:{port}\n"
                        bad_output += f"    Error: {result}\n"
                        bad_output += "--------------------------------------------------\n"
                else:
                    print(f"Error processing server {server}: Invalid format.")
                    bad_output += f"Server: {server}\n"
                    bad_output += "    Error: Invalid format. Expected format: IP:Port:Username:Password\n"
                    bad_output += "--------------------------------------------------\n"
            
            except Exception as e:
                error_details = traceback.format_exc()
                print(f"Error processing server: {server_line.strip()}. Error: {error_details}")
                bad_output += f"Server: {server_line.strip()}\n"
                bad_output += f"    Error: {error_details}\n"
                bad_output += "--------------------------------------------------\n"
                
        good_file.write(good_output)
        good_file.flush()
        bad_file.write(bad_output)
        bad_file.flush()

def print_welcome_message():
    print(r"""
 ____           _         _       _    _  
/ ___|  _   _  __| |   ___      / \   _ __ ___  (_) _ __ | |__ 
\___ \ | | | |/ _` |  / _ \    / _ \ | '_ ` _ \ | || '__|| '_ \
 ___) || |_| || (_| | | (_) |  / ___ \| | | | | || || |   | | | |
|____/  \__,_| \__,_|  \___/_____/_/   \_\|_| |_| |_||_||_|   |_| |_|
                         |_____|                           
    """)

def main():
    print_welcome_message()
    input_file = input("Please enter the path to the input file: ")
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found.")
        return
    process_servers(input_file)

if __name__ == "__main__":
    main()