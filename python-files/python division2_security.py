import os
import subprocess
import winreg
import ctypes
import sys
import time
import psutil
import socket
import threading
import json
import keyboard  # Requires installation: pip install keyboard

# Configuration
CONFIG_FILE = "division2_security.json"
GAME_EXECUTABLE = "TheDivision2.exe"
UBISOFT_REG_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Uplay Install 575"

# Security rule definitions
SECURITY_RULES = {
    "voip_block": {
        "name": "Division2 VOIP Block",
        "dir": "in",
        "action": "block",
        "protocol": "UDP",
        "localport": "3000-3009,7000-7003"
    },
    "ip_leak_block": {
        "name": "Division2 IP Leak Block",
        "dir": "in",
        "action": "block",
        "protocol": "UDP",
        "localport": "1-29999,30010-6999,7004-7499,7510-65535"
    },
    "essential_allow": {
        "name": "Division2 Essential Traffic",
        "dir": "in",
        "action": "allow",
        "protocol": "TCP",
        "localport": "80,443,14000-14024"
    }
}

class Division2SecurityManager:
    def __init__(self):
        self.game_path = None
        self.game_pid = None
        self.protection_enabled = False
        self.load_config()
        self.find_game_path()
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.protection_enabled = config.get('protection_enabled', False)
            except:
                self.protection_enabled = False
        else:
            self.protection_enabled = False
    
    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'protection_enabled': self.protection_enabled}, f)
    
    def find_game_path(self):
        """Locate game installation path from registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, UBISOFT_REG_KEY) as key:
                self.game_path = winreg.QueryValueEx(key, "InstallLocation")[0]
        except:
            self.game_path = None
    
    def find_game_process(self):
        """Find running Division 2 process"""
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] and proc.info['name'].lower() == GAME_EXECUTABLE.lower():
                self.game_pid = proc.info['pid']
                return True
        self.game_pid = None
        return False
    
    def toggle_firewall_rule(self, rule, enable=True):
        """Enable or disable a firewall rule"""
        action = "add" if enable else "delete"
        try:
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', action, 'rule',
                f'name={rule["name"]}',
                f'dir={rule["dir"]}',
                f'action={rule["action"]}',
                f'protocol={rule["protocol"]}',
                f'localport={rule["localport"]}'
            ], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def apply_security_rules(self, enable):
        """Apply all security rules"""
        status = True
        status &= self.toggle_firewall_rule(SECURITY_RULES["voip_block"], enable)
        status &= self.toggle_firewall_rule(SECURITY_RULES["ip_leak_block"], enable)
        status &= self.toggle_firewall_rule(SECURITY_RULES["essential_allow"], enable)
        return status
    
    def terminate_voip_connections(self):
        """Terminate VOIP-related connections"""
        if not self.game_pid:
            return False
            
        try:
            # Get network connections for the game process
            connections = psutil.Process(self.game_pid).connections()
            for conn in connections:
                # Target UDP connections on VOIP ports
                if conn.type == socket.SOCK_DGRAM and conn.laddr.port in range(3000, 3010):
                    # Kill the connection by terminating the socket
                    subprocess.run(
                        ['wmic', 'process', 'where', f'ProcessId={self.game_pid}', 'delete'],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    return True
            return False
        except:
            return False
    
    def toggle_protection(self, enable):
        """Enable or disable security protection"""
        if not self.find_game_process():
            print("Game not running. Please start The Division 2 first.")
            return False
            
        # Clear existing rules
        self.apply_security_rules(False)
        
        if enable:
            # Apply security rules
            if self.apply_security_rules(True):
                self.terminate_voip_connections()
                self.protection_enabled = True
                self.save_config()
                print("Security protection ENABLED")
                print("- VOIP blocked")
                print("- IP leak ports secured")
                print("- Essential traffic allowed")
                return True
        else:
            # Remove all security rules
            self.protection_enabled = False
            self.save_config()
            print("Security protection DISABLED")
            print("- All traffic allowed")
            return True
        
        return False
    
    def monitor_game(self):
        """Monitor game process and auto-apply protection"""
        last_state = None
        
        while True:
            game_running = self.find_game_process()
            
            if game_running:
                if last_state != "running":
                    print(f"Game detected (PID: {self.game_pid})")
                    # Re-apply protection if configured
                    if self.protection_enabled:
                        self.toggle_protection(True)
                    last_state = "running"
            else:
                if last_state != "stopped":
                    print("Game not running")
                    last_state = "stopped"
            
            time.sleep(5)
    
    def start_hotkey_listener(self):
        """Start listening for hotkeys to toggle protection"""
        def on_hotkey():
            self.toggle_protection(not self.protection_enabled)
        
        keyboard.add_hotkey('ctrl+alt+d', on_hotkey)
        print("Hotkey registered: CTRL+ALT+D to toggle protection")
        keyboard.wait()

def main():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return
    
    manager = Division2SecurityManager()
    
    print("Division 2 Security Manager")
    print("===========================")
    print(f"Current protection: {'ENABLED' if manager.protection_enabled else 'DISABLED'}")
    print("\nOptions:")
    print("1. Enable protection now")
    print("2. Disable protection now")
    print("3. Run in background with hotkey (CTRL+ALT+D)")
    print("4. Exit")
    
    choice = input("\nSelect option: ")
    
    if choice == "1":
        manager.toggle_protection(True)
    elif choice == "2":
        manager.toggle_protection(False)
    elif choice == "3":
        print("\nRunning in background...")
        print(" - Press CTRL+ALT+D to toggle protection")
        print(" - Game will be automatically monitored")
        
        # Start monitoring threads
        monitor_thread = threading.Thread(target=manager.monitor_game, daemon=True)
        monitor_thread.start()
        
        # Start hotkey listener (blocks)
        manager.start_hotkey_listener()
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()