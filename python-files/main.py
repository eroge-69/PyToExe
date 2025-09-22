import pygame
import pygame.freetype
import sys
import math
import random
import time
import os
import subprocess
import platform
import threading
from datetime import datetime
from collections import deque
from typing import Dict, List, Any, Tuple, Optional

# Inicialização do Pygame
pygame.init()
pygame.freetype.init()


class SovietConfig3D:

    def __init__(self):
        self.system_name = "SOVIET PURE OS 3D"
        self.version = "3.1.4"
        self.codename = "RED PYTHON 3D"

        # Configurações de tela
        self.screen_width = 1380
        self.screen_height = 500
        self.fullscreen = True  # já abre em fullscreen
        self.refresh_rate = 60

        # Inicializa a tela
        self.init_display()

        pygame.display.set_caption("Soviet Pure OS 3D")

        # Cores do tema soviético
        self.colors = {
            'background': (10, 15, 20),
            'panel': (30, 40, 50),
            'accent': (200, 30, 30),
            'accent_light': (220, 50, 50),
            'green': (30, 200, 30),
            'cyan': (30, 180, 200),
            'yellow': (220, 200, 30),
            'text': (220, 220, 220),
            'text_highlight': (255, 255, 255),
            'warning': (255, 100, 0),
            'danger': (255, 30, 30),
            'success': (50, 200, 50),
        }

        # Configurações 3D
        self.camera_distance = 10
        self.camera_height = 3
        self.rotation_speed = 0.005
        self.panel_spacing = 2.5

        # Configurações de sistema
        self.vpn_servers = [
            "vpn.moscow.soviet",
            "vpn.leningrad.soviet",
            "vpn.stalingrad.soviet",
            "vpn.siberia.soviet"
        ]

        # Configurações de segurança
        self.vpn_rotate_interval = 30
        self.suspicious_processes = [
            "keylogger", "rat", "backdoor", "trojan", "spyware",
            "malware", "virus", "ransomware", "exploit", "rootkit"
        ]

        # Linguagem criptografada do terminal
        self.crypto_language = {
            "scan": "просканировать",
            "hack": "взламывать",
            "encrypt": "шифровать",
            "decrypt": "расшифровать",
            "firewall": "брандмауэр",
            "vpn": "впн",
            "analyze": "анализировать",
            "protect": "защищать",
            "attack": "атаковать",
            "defend": "защищаться",
            "system": "система",
            "network": "сеть",
            "security": "безопасность",
            "process": "процесс",
            "monitor": "монитор",
            "detect": "обнаружить",
            "terminate": "завершить",
            "connect": "подключить",
            "disconnect": "отключить",
            "status": "статус"
        }

    # =========================
    # Tela
    # =========================
    def init_display(self):
        """Cria a tela de acordo com fullscreen ou janela"""
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), flags
        )
        self.screen_width, self.screen_height = self.screen.get_size()

    def toggle_fullscreen(self):
        """Alterna fullscreen / janela sem quebrar o resto do código"""
        self.fullscreen = not self.fullscreen
        self.init_display()


# =============================================================================
# SISTEMA DE TELEMETRIA
# =============================================================================
class QuantumTelemetry:
    def __init__(self):
        self.cpu_history = deque(maxlen=20)
        self.mem_history = deque(maxlen=20)
        self.net_history = deque(maxlen=20)
        self.last_net_io = (0, 0)
        self.processes = []
        self.network_packets = deque(maxlen=50)
        self.key_events = deque(maxlen=100)
        self.suspicious_activity = []

    def get_cpu_usage(self) -> float:
        """Obtém uso da CPU de forma cross-platform"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'loadpercentage'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return float(lines[1].strip())
            else:
                # Linux/Mac
                result = subprocess.run(
                    ['top', '-bn1'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if '%Cpu(s)' in line:
                        parts = line.split(',')
                        idle = float(parts[3].split('%')[0].strip())
                        return 100 - idle
        except:
            pass
        return random.uniform(5, 25)  # Fallback

    def get_memory_usage(self) -> Dict[str, Any]:
        """Obtém uso de memória"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    free = int(parts[0])
                    total = int(parts[1])
                    used = total - free
                    return {
                        'total': total,
                        'used': used,
                        'percent': (used / total) * 100
                    }
            else:
                # Linux/Mac
                result = subprocess.run(
                    ['free', '-m'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    total = int(parts[1])
                    used = int(parts[2])
                    return {
                        'total': total,
                        'used': used,
                        'percent': (used / total) * 100
                    }
        except:
            pass

        # Fallback
        return {
            'total': 8192,
            'used': 4096,
            'percent': 50.0
        }

    def get_network_usage(self) -> Dict[str, Any]:
        """Obtém uso de rede"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['netstat', '-e'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Bytes' in line and 'Received' in line:
                        parts = line.split()
                        received = int(parts[1])
                        sent = int(parts[2])
                        current_net = (received, sent)

                        # Calcular diferença
                        old_received, old_sent = self.last_net_io
                        diff_received = received - old_received
                        diff_sent = sent - old_sent

                        self.last_net_io = current_net

                        return {
                            'sent': diff_sent,
                            'received': diff_received,
                            'total': diff_sent + diff_received
                        }
            else:
                # Simular pacotes de rede para demonstração
                packet_types = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'DNS']
                for _ in range(random.randint(1, 5)):
                    self.network_packets.append({
                        'type': random.choice(packet_types),
                        'size': random.randint(64, 1500),
                        'direction': random.choice(['incoming', 'outgoing']),
                        'source': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        'destination': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        'timestamp': datetime.now()
                    })
        except:
            pass

        # Fallback
        return {
            'sent': random.randint(1000, 10000),
            'received': random.randint(1000, 10000),
            'total': random.randint(2000, 20000)
        }

    def get_disk_usage(self) -> Dict[str, Any]:
        """Obtém uso de disco"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'logicaldisk', 'where', 'drivetype=3', 'get', 'size,freespace'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    free = int(parts[0])
                    total = int(parts[1])
                    used = total - free
                    return {
                        'total': total,
                        'used': used,
                        'percent': (used / total) * 100
                    }
            else:
                result = subprocess.run(
                    ['df', '/'],
                    capture_output=True, text=True, timeout=2
                )
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    total = int(parts[1]) * 1024
                    used = int(parts[2]) * 1024
                    return {
                        'total': total,
                        'used': used,
                        'percent': (used / total) * 100
                    }
        except:
            pass

        # Fallback
        return {
            'total': 100000000000,
            'used': 50000000000,
            'percent': 50.0
        }

    def get_process_list(self) -> List[Dict[str, Any]]:
        """Obtém lista de processos (simulada para demonstração)"""
        if not self.processes:
            # Criar lista inicial de processos
            process_names = [
                "system", "explorer", "chrome", "firefox", "python",
                "svchost", "winlogon", "taskmgr", "cmd", "steam",
                "discord", "spotify", "code", "node", "java"
            ]

            for i, name in enumerate(process_names):
                cpu = random.uniform(0.1, 5.0)
                memory = random.uniform(10, 500)
                suspicious = any(susp in name.lower() for susp in [
                    "keylogger", "rat", "backdoor", "trojan", "spyware"
                ])

                self.processes.append({
                    'pid': 1000 + i,
                    'name': name,
                    'cpu': cpu,
                    'memory': memory,
                    'suspicious': suspicious
                })

        # Atualizar alguns processos aleatoriamente
        for process in random.sample(self.processes, min(5, len(self.processes))):
            process['cpu'] = max(0.1, process['cpu'] + random.uniform(-1, 1))
            process['memory'] = max(10, process['memory'] + random.uniform(-10, 10))

            # Aleatoriamente marcar algum processo como suspeito
            if random.random() < 0.05:  # 5% de chance
                process['suspicious'] = True
                if process not in self.suspicious_activity:
                    self.suspicious_activity.append({
                        'type': 'suspicious_process',
                        'process': process['name'],
                        'timestamp': datetime.now(),
                        'description': f"Processo suspeito detectado: {process['name']}"
                    })

        return self.processes

    def get_system_status(self) -> Dict[str, Any]:
        """Obtém status completo do sistema"""
        cpu_percent = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        network = self.get_network_usage()
        processes = self.get_process_list()

        # Atualizar históricos
        self.cpu_history.append(cpu_percent)
        self.mem_history.append(memory['percent'])
        self.net_history.append(network['total'])

        return {
            'cpu': {
                'percent': cpu_percent,
                'history': list(self.cpu_history),
                'cores': os.cpu_count() or 4
            },
            'memory': memory,
            'disk': disk,
            'network': network,
            'processes': processes,
            'packets': list(self.network_packets),
            'suspicious_activity': self.suspicious_activity[-10:],  # Últimas 10 atividades
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }


# =============================================================================
# SISTEMA DE REDE E VPN
# =============================================================================
class SovietNetwork:
    def __init__(self, config: SovietConfig3D):
        self.config = config
        self.vpn_status = "DISCONNECTED"
        self.vpn_server = None
        self.public_ip = "127.0.0.1"
        self.country = "LOCAL"
        self.city = "LOCALHOST"
        self.vpn_rotation_timer = 0
        self.port_scan_results = []
        self.firewall_rules = self.generate_firewall_rules()
        self.open_ports = []

    def generate_firewall_rules(self):
        """Gera regras de firewall simuladas"""
        rules = []
        protocols = ['TCP', 'UDP', 'ICMP']
        actions = ['ALLOW', 'DENY']
        directions = ['INBOUND', 'OUTBOUND']

        for i in range(15):
            rules.append({
                'id': i + 1,
                'protocol': random.choice(protocols),
                'port': random.randint(1, 65535),
                'action': random.choice(actions),
                'direction': random.choice(directions),
                'source': f"{random.randint(1, 255)}.0.0.0/{random.randint(8, 24)}",
                'destination': f"{random.randint(1, 255)}.0.0.0/{random.randint(8, 24)}",
                'enabled': random.random() > 0.3  # 70% de chance de estar habilitada
            })

        return rules

    def get_network_info(self) -> Dict[str, Any]:
        """Obtém informações de rede"""
        try:
            # Tentar obter IP público
            try:
                result = subprocess.run(
                    ['curl', '-s', 'https://api.ipify.org'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    self.public_ip = result.stdout.strip()
            except:
                pass
        except:
            pass

        # Atualizar temporizador de rotação VPN
        current_time = time.time()
        if self.vpn_status == "CONNECTED" and current_time - self.vpn_rotation_timer > self.config.vpn_rotate_interval:
            self.vpn_rotate()

        return {
            'public_ip': self.public_ip,
            'country': self.country,
            'city': self.city,
            'vpn_status': self.vpn_status,
            'vpn_server': self.vpn_server,
            'firewall_rules': self.firewall_rules,
            'open_ports': self.open_ports
        }

    def vpn_connect(self):
        """Simula conexão VPN"""
        self.vpn_status = "CONNECTED"
        self.vpn_server = random.choice(self.config.vpn_servers)
        self.country = "RUSSIA"
        self.city = "MOSCOW"
        self.vpn_rotation_timer = time.time()
        self.public_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def vpn_disconnect(self):
        """Simula desconexão VPN"""
        self.vpn_status = "DISCONNECTED"
        self.vpn_server = None
        self.country = "LOCAL"
        self.city = "LOCALHOST"
        self.public_ip = "127.0.0.1"

    def vpn_rotate(self):
        """Rotaciona servidor VPN"""
        if self.vpn_status == "CONNECTED":
            self.vpn_disconnect()
            time.sleep(1)
        self.vpn_connect()

    def scan_ports(self, target_ip: str = "127.0.0.1"):
        """Simula varredura de portas"""
        self.open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]

        for port in common_ports:
            if random.random() < 0.3:  # 30% de chance de porta aberta
                self.open_ports.append({
                    'port': port,
                    'service': self.get_service_name(port),
                    'status': 'OPEN',
                    'protocol': 'TCP'
                })

        return self.open_ports

    def get_service_name(self, port: int) -> str:
        """Retorna o nome do serviço baseado na porta"""
        services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            135: "RPC",
            139: "NetBIOS",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            993: "IMAPS",
            995: "POP3S",
            1723: "PPTP",
            3306: "MySQL",
            3389: "RDP",
            5900: "VNC",
            8080: "HTTP-Alt"
        }
        return services.get(port, "Unknown")


# =============================================================================
# ENCRYPTED TERMINAL
# =============================================================================
class CryptoTerminal:
    def __init__(self, config: SovietConfig3D):
        self.config = config
        self.history = deque(maxlen=100)
        self.current_input = ""
        self.cursor_position = 0
        self.active = False
        self.commands = {
            "scan": self.command_scan,
            "hack": self.command_hack,
            "encrypt": self.command_encrypt,
            "decrypt": self.command_decrypt,
            "firewall": self.command_firewall,
            "vpn": self.command_vpn,
            "analyze": self.command_analyze,
            "protect": self.command_protect,
            "attack": self.command_attack,
            "defend": self.command_defend,
            "system": self.command_system,
            "network": self.command_network,
            "security": self.command_security,
            "process": self.command_process,
            "monitor": self.command_monitor,
            "detect": self.command_detect,
            "terminate": self.command_terminate,
            "connect": self.command_connect,
            "disconnect": self.command_disconnect,
            "status": self.command_status
        }

    def translate_command(self, text: str) -> str:
        """Translates English commands into encrypted language"""
        words = text.split()
        translated = []

        for word in words:
            if word.lower() in self.config.crypto_language:
                translated.append(self.config.crypto_language[word.lower()])
            else:
                translated.append(word)

        return " ".join(translated)

    def execute_command(self, command: str):
        """Executes an encrypted command"""
        self.history.append(f"> {command}")

        cmd_parts = command.split()
        if not cmd_parts:
            self.history.append("Error: Empty command")
            return

        main_cmd = cmd_parts[0].lower()

        if main_cmd in self.commands:
            try:
                self.commands[main_cmd](cmd_parts[1:] if len(cmd_parts) > 1 else [])
            except Exception as e:
                self.history.append(f"Execution error: {str(e)}")
        else:
            self.history.append(f"Unknown command: {main_cmd}")

    # Terminal commands
    def command_scan(self, args):
        if args and args[0] == "ports":
            self.history.append("Scanning ports...")
            time.sleep(1)
            self.history.append("Found 5 open ports")
            self.history.append("21: FTP (OPEN)")
            self.history.append("22: SSH (OPEN)")
            self.history.append("80: HTTP (OPEN)")
            self.history.append("443: HTTPS (OPEN)")
            self.history.append("3389: RDP (OPEN)")
        else:
            self.history.append("Usage: scan ports")

    def command_hack(self, args):
        self.history.append("Initializing hacking protocol...")
        for i in range(5):
            time.sleep(0.3)
            self.history.append(f"Bypassing security {i + 1}/5...")
        self.history.append("System hacked successfully!")

    def command_encrypt(self, args):
        if args:
            filename = " ".join(args)
            self.history.append(f"Encrypting file {filename}...")
            time.sleep(1)
            self.history.append("File encrypted with AES-256")
        else:
            self.history.append("Usage: encrypt <file>")

    def command_decrypt(self, args):
        if args:
            filename = " ".join(args)
            self.history.append(f"Decrypting file {filename}...")
            time.sleep(1)
            self.history.append("File decrypted successfully")
        else:
            self.history.append("Usage: decrypt <file>")

    def command_firewall(self, args):
        self.history.append("Firewall status: ACTIVE")
        self.history.append("Rules loaded: 15")
        self.history.append("Last check: Today")

    def command_vpn(self, args):
        if args and args[0] == "status":
            self.history.append("VPN Status: ACTIVE")
            self.history.append("Server: vpn.moscow.soviet")
            self.history.append("Encryption: AES-256")
        else:
            self.history.append("Usage: vpn status")

    def command_analyze(self, args):
        self.history.append("Analyzing system...")
        time.sleep(1)
        self.history.append("No threats detected")
        self.history.append("All systems operational")

    def command_protect(self, args):
        self.history.append("Activating protection protocols...")
        for i in range(3):
            time.sleep(0.5)
            self.history.append(f"Protection level {i + 1} activated")
        self.history.append("System protected")

    def command_attack(self, args):
        self.history.append("Denied: Attack mode disabled")
        self.history.append("Activate KGB license for access")

    def command_defend(self, args):
        self.history.append("Defense mode activated")
        self.history.append("All incoming connections are being checked")

    def command_system(self, args):
        self.history.append(f"System: {self.config.system_name}")
        self.history.append(f"Version: {self.config.version}")
        self.history.append(f"Codename: {self.config.codename}")

    def command_network(self, args):
        self.history.append("Network status: ONLINE")
        self.history.append("Speed: 1 Gbps")
        self.history.append("Security: ENABLED")

    def command_security(self, args):
        self.history.append("Security level: HIGH")
        self.history.append("Last check: Today")
        self.history.append("Threats: 0")

    def command_process(self, args):
        self.history.append("Running processes: 42")
        self.history.append("System: 15")
        self.history.append("User: 27")

    def command_monitor(self, args):
        self.history.append("Monitoring enabled")
        self.history.append("All activities are being logged")

    def command_detect(self, args):
        self.history.append("Scanning for threats...")
        time.sleep(1)
        self.history.append("No threats detected")

    def command_terminate(self, args):
        if args:
            pid = args[0]
            self.history.append(f"Terminating process {pid}...")
            time.sleep(0.5)
            self.history.append(f"Process {pid} terminated")
        else:
            self.history.append("Usage: terminate <PID>")

    def command_connect(self, args):
        self.history.append("Establishing secure connection...")
        time.sleep(1)
        self.history.append("Connection established")

    def command_disconnect(self, args):
        self.history.append("Disconnecting...")
        time.sleep(0.5)
        self.history.append("Connection terminated")

    def command_status(self, args):
        self.history.append("System status: NORMAL")
        self.history.append("Memory: 45%")
        self.history.append("CPU: 22%")
        self.history.append("Disk: 60%")


# =============================================================================
# SISTEMA DE RENDERIZAÇÃO 3D (CORRIGIDO)
# =============================================================================
class SovietRenderer3D:
    def __init__(self, config: SovietConfig3D):
        self.config = config
        self.current_screen = "main"
        self.animation_frame = 0
        self.camera_angle = 0
        self.fonts = {}
        self.load_fonts()

        # Configurar display
        if self.config.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.config.screen_width, self.config.screen_height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode(
                (self.config.screen_width, self.config.screen_height)
            )

        pygame.display.set_caption(f"{config.system_name} v{config.version}")

        # Criar relógio para controlar FPS
        self.clock = pygame.time.Clock()

        # Carregar ícones e texturas
        self.icons = self.load_icons()

        # Históricos locais para gráficos
        self.cpu_history = deque(maxlen=20)
        self.memory_history = deque(maxlen=20)
        self.network_history = deque(maxlen=20)

    def load_fonts(self):
        """Carrega as fontes necessárias"""
        try:
            self.fonts['title'] = pygame.font.SysFont('Arial', 36)
            self.fonts['subtitle'] = pygame.font.SysFont('Arial', 24)
            self.fonts['normal'] = pygame.font.SysFont('Arial', 18)
            self.fonts['small'] = pygame.font.SysFont('Arial', 14)
        except:
            # Fallback para fontes padrão
            self.fonts['title'] = pygame.font.Font(None, 36)
            self.fonts['subtitle'] = pygame.font.Font(None, 24)
            self.fonts['normal'] = pygame.font.Font(None, 18)
            self.fonts['small'] = pygame.font.Font(None, 14)

    def load_icons(self):
        """Cria ícones simples programaticamente"""
        icons = {}

        # Ícone de CPU
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.config.colors['cyan'], (0, 16, 32, 16), border_radius=4)
        pygame.draw.rect(surf, self.config.colors['cyan'], (8, 0, 16, 32), border_radius=4)
        icons['cpu'] = surf

        # Ícone de memória
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.config.colors['green'], (0, 0, 32, 32), border_radius=6)
        pygame.draw.rect(surf, self.config.colors['background'], (4, 4, 24, 24))
        icons['memory'] = surf

        # Ícone de disco
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.config.colors['yellow'], (4, 4, 24, 24), border_radius=4)
        pygame.draw.rect(surf, self.config.colors['yellow'], (0, 12, 32, 8))
        icons['disk'] = surf

        # Ícone de rede
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.line(surf, self.config.colors['accent'], (0, 16), (32, 16), 3)
        pygame.draw.line(surf, self.config.colors['accent'], (16, 0), (16, 32), 3)
        for i in range(4):
            pygame.draw.circle(surf, self.config.colors['accent'],
                               (8 + i * 8, 16), 4 if i % 2 == 0 else 2)
        icons['network'] = surf

        return icons

    def update_histories(self, system_data: Dict[str, Any]):
        """Atualiza os históricos locais para gráficos"""
        self.cpu_history.append(system_data['cpu']['percent'])
        self.memory_history.append(system_data['memory']['percent'])
        self.network_history.append(system_data['network']['total'])

    def draw_progress_bar_3d(self, surface, rect, percent, color):
        """Desenha uma barra de progresso com efeito 3D"""
        x, y, w, h = rect

        # Fundo da barra
        pygame.draw.rect(surface, self.config.colors['panel'], rect, border_radius=4)

        # Preenchimento baseado na porcentagem
        fill_width = max(10, int(w * percent / 100))
        fill_rect = (x, y, fill_width, h)

        # Gradiente para o preenchimento
        for i in range(fill_width):
            alpha = 255 - int(i / fill_width * 100) if fill_width > 0 else 0
            shade_color = (
                min(255, color[0] + alpha // 10),
                min(255, color[1] + alpha // 10),
                min(255, color[2] + alpha // 10)
            )
            pygame.draw.rect(surface, shade_color, (x + i, y, 1, h))

        # Borda com efeito de luz
        pygame.draw.rect(surface, color, rect, 2, border_radius=4)

        # Texto de porcentagem
        percent_text = f"{percent:.1f}%"
        text_surf = self.fonts['small'].render(percent_text, True, self.config.colors['text_highlight'])
        text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
        surface.blit(text_surf, text_rect)

    def draw_panel_3d(self, surface, center_pos, size, title=""):
        """Desenha um painel 3D na posição especificada"""
        width, height = size
        x, y = center_pos

        # Calcular pontos do painel em 3D
        angle = self.camera_angle
        depth = 20

        # Pontos do painel (frente)
        points = [
            (x - width // 2, y - height // 2),  # Topo esquerdo
            (x + width // 2, y - height // 2),  # Topo direito
            (x + width // 2, y + height // 2),  # Base direita
            (x - width // 2, y + height // 2),  # Base esquerda
        ]

        # Pontos traseiros (para efeito 3D)
        back_points = [
            (x - width // 2 + depth * math.cos(angle), y - height // 2 + depth * math.sin(angle)),
            (x + width // 2 + depth * math.cos(angle), y - height // 2 + depth * math.sin(angle)),
            (x + width // 2 + depth * math.cos(angle), y + height // 2 + depth * math.sin(angle)),
            (x - width // 2 + depth * math.cos(angle), y + height // 2 + depth * math.sin(angle)),
        ]

        # Desenhar lados do painel
        for i in range(4):
            pygame.draw.polygon(surface, self.config.colors['panel'], [
                points[i], points[(i + 1) % 4], back_points[(i + 1) % 4], back_points[i]
            ])

        # Desenhar face frontal
        pygame.draw.polygon(surface, self.config.colors['panel'], points)
        pygame.draw.polygon(surface, self.config.colors['accent'], points, 2)

        # Desenhar título se fornecido
        if title:
            title_surf = self.fonts['subtitle'].render(title, True, self.config.colors['text_highlight'])
            title_rect = title_surf.get_rect(center=(x, y - height // 2 + 25))
            surface.blit(title_surf, title_rect)

        return points

    def draw_graph_3d(self, surface, center_pos, size, data, color, title=""):
        """Desenha um gráfico 3D dos dados fornecidos"""
        if not data:
            # Se não há dados, desenhar um painel vazio
            self.draw_panel_3d(surface, center_pos, size, title)
            return

        # Desenhar painel para o gráfico
        panel_points = self.draw_panel_3d(surface, center_pos, size, title)

        # Calcular área de desenho do gráfico
        x, y = center_pos
        width, height = size
        graph_rect = (
            x - width // 2 + 20,
            y - height // 2 + 40,
            width - 40,
            height - 60
        )

        # Desenhar eixos
        pygame.draw.line(surface, self.config.colors['text'],
                         (graph_rect[0], graph_rect[1] + graph_rect[3]),
                         (graph_rect[0] + graph_rect[2], graph_rect[1] + graph_rect[3]), 2)
        pygame.draw.line(surface, self.config.colors['text'],
                         (graph_rect[0], graph_rect[1]),
                         (graph_rect[0], graph_rect[1] + graph_rect[3]), 2)

        # Desenhar linhas do gráfico
        if len(data) > 1:
            max_val = max(data) if max(data) > 0 else 1
            points = []

            for i, value in enumerate(data):
                x_pos = graph_rect[0] + (i / (len(data) - 1)) * graph_rect[2]
                y_pos = graph_rect[1] + graph_rect[3] - (value / max_val) * graph_rect[3]
                points.append((x_pos, y_pos))

            # Desenhar linha do gráfico
            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 3)

                # Preencher área abaixo da linha
                fill_points = points + [
                    (graph_rect[0] + graph_rect[2], graph_rect[1] + graph_rect[3]),
                    (graph_rect[0], graph_rect[1] + graph_rect[3])
                ]
                pygame.draw.polygon(surface, (*color, 100), fill_points)

    def render_text(self, text, font_type, color, position, centered=False):
        """Renderiza texto na tela de forma segura"""
        try:
            text_surface = self.fonts[font_type].render(text, True, color)
            if centered:
                text_rect = text_surface.get_rect(center=position)
                self.screen.blit(text_surface, text_rect)
            else:
                self.screen.blit(text_surface, position)
        except:
            # Fallback em caso de erro
            pass

    def draw_network_packets(self, surface, packets, center_pos, size):
        """Desenha visualização 3D de pacotes de rede"""
        if not packets:
            return

        # Desenhar painel
        panel_points = self.draw_panel_3d(surface, center_pos, size, "NETWORK PACKETS")

        x, y = center_pos
        width, height = size

        # Desenhar área de visualização
        area_rect = (
            x - width // 2 + 20,
            y - height // 2 + 40,
            width - 40,
            height - 60
        )

        # Desenhar linha central (divisão incoming/outgoing)
        pygame.draw.line(surface, self.config.colors['text'],
                         (area_rect[0], area_rect[1] + area_rect[3] // 2),
                         (area_rect[0] + area_rect[2], area_rect[1] + area_rect[3] // 2), 1)

        # Desenhar pacotes (apenas os últimos 10)
        packet_count = min(10, len(packets))
        for i in range(packet_count):
            packet = packets[-(i + 1)]  # Pegar do final para o início
            packet_x = area_rect[0] + 10 + (i % 5) * (area_rect[2] // 5)
            packet_y = area_rect[1] + 20 + (i // 5) * 30

            # Cor baseada no tipo de pacote
            if packet['type'] in ['TCP', 'UDP']:
                color = self.config.colors['cyan']
            elif packet['type'] in ['HTTP', 'HTTPS']:
                color = self.config.colors['green']
            else:
                color = self.config.colors['yellow']

            # Posição baseada na direção
            if packet['direction'] == 'incoming':
                packet_y = area_rect[1] + area_rect[3] // 2 - 20 - (i // 5) * 30

            # Desenhar representação do pacote
            pygame.draw.rect(surface, color, (packet_x, packet_y, 20, 10), border_radius=2)

            # Seta indicando direção
            if packet['direction'] == 'incoming':
                pygame.draw.polygon(surface, color, [
                    (packet_x + 10, packet_y - 5),
                    (packet_x + 5, packet_y),
                    (packet_x + 15, packet_y)
                ])
            else:
                pygame.draw.polygon(surface, color, [
                    (packet_x + 10, packet_y + 15),
                    (packet_x + 5, packet_y + 10),
                    (packet_x + 15, packet_y + 10)
                ])

    def draw_process_cubes(self, surface, processes, center_pos, size):
        """Desenha processos como cubos 3D"""
        if not processes:
            return

        # Desenhar painel
        panel_points = self.draw_panel_3d(surface, center_pos, size, "PROCESS EXPLORER")

        x, y = center_pos
        width, height = size

        # Desenhar área de visualização
        area_rect = (
            x - width // 2 + 20,
            y - height // 2 + 40,
            width - 40,
            height - 60
        )

        # Desenhar processos como cubos (apenas os primeiros 12)
        process_count = min(12, len(processes))
        for i in range(process_count):
            process = processes[i]
            row = i // 4
            col = i % 4

            cube_x = area_rect[0] + col * (area_rect[2] // 4) + 30
            cube_y = area_rect[1] + row * (area_rect[3] // 3) + 30

            # Tamanho baseado no uso de CPU
            cube_size = 10 + min(30, process['cpu'] * 3)

            # Cor baseada se é suspeito
            if process['suspicious']:
                color = self.config.colors['danger']
            else:
                color = self.config.colors['cyan']

            # Desenhar cubo 3D
            self.draw_cube(surface, (cube_x, cube_y), cube_size, color)

            # Nome do processo
            name = process['name'][:8]  # Limitar tamanho do nome
            self.render_text(name, 'small', self.config.colors['text'], (cube_x, cube_y + cube_size + 10), True)

            # Uso de CPU
            cpu_text = f"{process['cpu']:.1f}%"
            self.render_text(cpu_text, 'small', self.config.colors['text_highlight'], (cube_x, cube_y - cube_size - 5),
                             True)

    def draw_cube(self, surface, position, size, color):
        """Desenha um cubo 3D simples"""
        x, y = position

        # Face frontal
        pygame.draw.rect(surface, color, (x - size // 2, y - size // 2, size, size))

        # Faces laterais (para efeito 3D)
        shade_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))

        # Face direita
        pygame.draw.polygon(surface, shade_color, [
            (x + size // 2, y - size // 2),
            (x + size, y - size // 4),
            (x + size, y + size // 4),
            (x + size // 2, y + size // 2)
        ])

        # Face superior
        pygame.draw.polygon(surface, shade_color, [
            (x - size // 2, y - size // 2),
            (x, y - size),
            (x + size // 2, y - size // 2),
            (x + size // 2, y - size // 2)
        ])

    def draw_firewall_rules(self, surface, rules, center_pos, size):
        """Desenha visualização 3D das regras de firewall"""
        if not rules:
            return

        # Desenhar painel
        panel_points = self.draw_panel_3d(surface, center_pos, size, "FIREWALL RULES")

        x, y = center_pos
        width, height = size

        # Desenhar área de visualização
        area_rect = (
            x - width // 2 + 20,
            y - height // 2 + 40,
            width - 40,
            height - 60
        )

        # Desenhar regras (apenas as primeiras 8)
        rule_count = min(8, len(rules))
        for i in range(rule_count):
            rule = rules[i]
            rule_y = area_rect[1] + 15 + i * 20

            # Cor baseada na ação
            if rule['action'] == 'ALLOW':
                color = self.config.colors['success']
            else:
                color = self.config.colors['danger']

            # Ícone de status
            if rule['enabled']:
                status_icon = "✓"
                status_color = self.config.colors['success']
            else:
                status_icon = "✗"
                status_color = self.config.colors['text']

            # Desenhar ícone de status
            self.render_text(status_icon, 'small', status_color, (area_rect[0] + 10, rule_y))

            # Texto da regra
            rule_text = f"{rule['protocol']}:{rule['port']} {rule['direction']}"
            self.render_text(rule_text, 'small', self.config.colors['text'], (area_rect[0] + 30, rule_y))

            # Indicador visual da ação
            pygame.draw.rect(surface, color, (area_rect[0] + area_rect[2] - 30, rule_y - 5, 20, 10), border_radius=2)

    def draw_terminal(self, surface, terminal, center_pos, size):
        """Desenha o terminal criptografado"""
        # Desenhar painel
        panel_points = self.draw_panel_3d(surface, center_pos, size, "SOVIET TERMINAL")

        x, y = center_pos
        width, height = size

        # Desenhar área do terminal
        term_rect = (
            x - width // 2 + 20,
            y - height // 2 + 40,
            width - 40,
            height - 60
        )

        # Fundo do terminal
        pygame.draw.rect(surface, (0, 0, 0), term_rect, border_radius=4)
        pygame.draw.rect(surface, self.config.colors['accent'], term_rect, 2, border_radius=4)

        # Desenhar histórico (apenas as últimas 10 linhas)
        history_size = len(terminal.history)
        lines_to_show = min(10, history_size)

        for i in range(lines_to_show):
            line = terminal.history[history_size - lines_to_show + i]
            line_y = term_rect[1] + 10 + i * 20
            if line_y < term_rect[1] + term_rect[3] - 30:  # Dentro da área visível
                self.render_text(line, 'small', self.config.colors['green'], (term_rect[0] + 10, line_y))

        # Desenhar linha de entrada
        input_y = term_rect[1] + term_rect[3] - 25
        prompt = "SOVIET> "
        self.render_text(prompt, 'small', self.config.colors['accent_light'], (term_rect[0] + 10, input_y))

        # Desenhar texto de entrada
        input_text = terminal.current_input
        self.render_text(input_text, 'small', self.config.colors['text_highlight'],
                         (term_rect[0] + 10 + self.fonts['small'].size(prompt)[0], input_y))

        # Cursor piscante
        if int(time.time() * 2) % 2 == 0:
            cursor_x = term_rect[0] + 10 + self.fonts['small'].size(prompt + input_text)[0]
            pygame.draw.line(surface, self.config.colors['text_highlight'],
                             (cursor_x, input_y - 10), (cursor_x, input_y + 5), 2)

    def render_main_screen(self, system_data: Dict[str, Any], network_data: Dict[str, Any], terminal: CryptoTerminal):
        """Renderiza a tela principal em 3D"""
        # Atualizar históricos
        self.update_histories(system_data)

        # Limpar tela
        self.screen.fill(self.config.colors['background'])

        # Atualizar ângulo da câmera para efeito de rotação
        self.camera_angle += self.config.rotation_speed

        # Desenhar painel de título
        title_pos = (self.config.screen_width // 2, 60)
        self.draw_panel_3d(self.screen, title_pos, (600, 80))

        # Desenhar título
        title_text = f"{self.config.system_name} v{self.config.version}"
        self.render_text(title_text, 'title', self.config.colors['accent_light'], title_pos, True)

        subtitle_text = self.config.codename
        self.render_text(subtitle_text, 'subtitle', self.config.colors['text'], (title_pos[0], title_pos[1] + 30), True)

        # Desenhar painéis de sistema
        panel_centers = [
            (self.config.screen_width // 4, 200),  # CPU
            (self.config.screen_width // 4 * 3, 200),  # Memória
            (self.config.screen_width // 4, 400),  # Disco
            (self.config.screen_width // 4 * 3, 400),  # Rede
        ]

        # Painel de CPU
        cpu_points = self.draw_panel_3d(self.screen, panel_centers[0], (280, 160), "CPU USAGE")
        self.screen.blit(self.icons['cpu'], (panel_centers[0][0] - 130, panel_centers[0][1] - 60))
        self.draw_progress_bar_3d(
            self.screen,
            (panel_centers[0][0] - 120, panel_centers[0][1] + 10, 240, 25),
            system_data['cpu']['percent'],
            self.config.colors['cyan']
        )

        # Informações adicionais da CPU
        cpu_info = f"Cores: {system_data['cpu']['cores']}"
        self.render_text(cpu_info, 'small', self.config.colors['text'],
                         (panel_centers[0][0] - 120, panel_centers[0][1] + 45))

        # Painel de Memória
        mem_points = self.draw_panel_3d(self.screen, panel_centers[1], (280, 160), "MEMORY USAGE")
        self.screen.blit(self.icons['memory'], (panel_centers[1][0] - 130, panel_centers[1][1] - 60))
        self.draw_progress_bar_3d(
            self.screen,
            (panel_centers[1][0] - 120, panel_centers[1][1] + 10, 240, 25),
            system_data['memory']['percent'],
            self.config.colors['green']
        )

        # Informações adicionais da Memória
        mem_used = system_data['memory']['used'] / (1024 ** 3)
        mem_total = system_data['memory']['total'] / (1024 ** 3)
        mem_info = f"Used: {mem_used:.1f} / {mem_total:.1f} GB"
        self.render_text(mem_info, 'small', self.config.colors['text'],
                         (panel_centers[1][0] - 120, panel_centers[1][1] + 45))

        # Painel de Disco
        disk_points = self.draw_panel_3d(self.screen, panel_centers[2], (280, 160), "DISK USAGE")
        self.screen.blit(self.icons['disk'], (panel_centers[2][0] - 130, panel_centers[2][1] - 60))
        self.draw_progress_bar_3d(
            self.screen,
            (panel_centers[2][0] - 120, panel_centers[2][1] + 10, 240, 25),
            system_data['disk']['percent'],
            self.config.colors['yellow']
        )

        # Informações adicionais do Disco
        disk_used = system_data['disk']['used'] / (1024 ** 3)
        disk_total = system_data['disk']['total'] / (1024 ** 3)
        disk_info = f"Used: {disk_used:.1f} / {disk_total:.1f} GB"
        self.render_text(disk_info, 'small', self.config.colors['text'],
                         (panel_centers[2][0] - 120, panel_centers[2][1] + 45))

        # Painel de Rede
        net_points = self.draw_panel_3d(self.screen, panel_centers[3], (280, 160), "NETWORK USAGE")
        self.screen.blit(self.icons['network'], (panel_centers[3][0] - 130, panel_centers[3][1] - 60))

        # Estatísticas de rede
        net_sent = system_data['network']['sent'] / 1024
        net_recv = system_data['network']['received'] / 1024

        sent_text = f"Sent: {net_sent:.1f} KB/s"
        recv_text = f"Received: {net_recv:.1f} KB/s"

        self.render_text(sent_text, 'small', self.config.colors['text'],
                         (panel_centers[3][0] - 120, panel_centers[3][1] + 10))
        self.render_text(recv_text, 'small', self.config.colors['text'],
                         (panel_centers[3][0] - 120, panel_centers[3][1] + 40))

        # Painel de informações de rede
        net_info_pos = (self.config.screen_width // 2, 550)
        net_info_points = self.draw_panel_3d(self.screen, net_info_pos, (600, 120), "NETWORK INFORMATION")

        # Informações de rede
        ip_text = f"IP: {network_data['public_ip']}"
        country_text = f"Country: {network_data['country']}"
        city_text = f"City: {network_data['city']}"
        vpn_text = f"VPN: {network_data['vpn_status']}"

        self.render_text(ip_text, 'normal', self.config.colors['text_highlight'],
                         (net_info_pos[0] - 290, net_info_pos[1] - 40))
        self.render_text(country_text, 'normal', self.config.colors['text_highlight'],
                         (net_info_pos[0] - 290, net_info_pos[1] - 15))
        self.render_text(city_text, 'normal', self.config.colors['text_highlight'],
                         (net_info_pos[0] - 290, net_info_pos[1] + 10))
        self.render_text(vpn_text, 'normal', self.config.colors['text_highlight'],
                         (net_info_pos[0] - 290, net_info_pos[1] + 35))

        # Desenhar gráficos em tempo real
        self.draw_graph_3d(
            self.screen,
            (self.config.screen_width // 2 - 200, 250),
            (400, 150),
            list(self.cpu_history),
            self.config.colors['cyan'],
            "CPU HISTORY"
        )

        self.draw_graph_3d(
            self.screen,
            (self.config.screen_width // 2 + 200, 250),
            (400, 150),
            list(self.memory_history),
            self.config.colors['green'],
            "MEMORY HISTORY"
        )

        # Desenhar terminal
        term_pos = (self.config.screen_width // 2, 700)
        self.draw_terminal(self.screen, terminal, term_pos, (800, 200))

        # Desenhar rodapé
        footer_text = "F1:Main F2:Network F3:System F4:Security F5:VPN F6:Processes F7:Terminal F8:Exit"
        self.render_text(footer_text, 'small', self.config.colors['text'],
                         (self.config.screen_width // 2, self.config.screen_height - 15), True)

        # Atualizar display
        pygame.display.flip()
        self.clock.tick(self.config.refresh_rate)

    def render_network_screen(self, system_data: Dict[str, Any], network_data: Dict[str, Any],
                              terminal: CryptoTerminal):
        """Renderiza a tela de rede em 3D"""
        # Atualizar históricos
        self.update_histories(system_data)

        # Implementação similar à tela principal, mas focada em rede
        self.screen.fill(self.config.colors['background'])

        # Atualizar ângulo da câmera
        self.camera_angle += self.config.rotation_speed

        # Título
        title_pos = (self.config.screen_width // 2, 60)
        self.draw_panel_3d(self.screen, title_pos, (600, 80))

        title_text = "NETWORK CONTROL CENTER"
        self.render_text(title_text, 'title', self.config.colors['accent_light'], title_pos, True)

        # Painel de informações de rede
        info_pos = (self.config.screen_width // 2, 180)
        self.draw_panel_3d(self.screen, info_pos, (600, 200), "NETWORK STATUS")
        # Informações de rede
        info_texts = [
            f"Public IP: {network_data['public_ip']}",
            f"Country: {network_data['country']}",
            f"City: {network_data['city']}",
            f"VPN Status: {network_data['vpn_status']}",
            f"VPN Server: {network_data['vpn_server'] or 'None'}"
        ]

        for i, text in enumerate(info_texts):
            self.render_text(text, 'normal', self.config.colors['text_highlight'],
                             (info_pos[0] - 290, info_pos[1] - 80 + i * 30))

        # Painel de estatísticas de rede
        stats_pos = (self.config.screen_width // 2, 400)
        self.draw_panel_3d(self.screen, stats_pos, (600, 150), "NETWORK STATISTICS")

        net_sent = system_data['network']['sent'] / 1024
        net_recv = system_data['network']['received'] / 1024

        stats_texts = [
            f"Sent: {net_sent:.1f} KB/s",
            f"Received: {net_recv:.1f} KB/s",
            f"Total: {(net_sent + net_recv):.1f} KB/s"
        ]

        for i, text in enumerate(stats_texts):
            self.render_text(text, 'normal', self.config.colors['text_highlight'],
                             (stats_pos[0] - 290, stats_pos[1] - 50 + i * 30))

        # Visualização de pacotes de rede
        packets_pos = (self.config.screen_width // 2, 580)
        self.draw_network_packets(self.screen, system_data['packets'], packets_pos, (600, 200))

        # Painel de servidores VPN
        vpn_pos = (self.config.screen_width // 2, 800)
        self.draw_panel_3d(self.screen, vpn_pos, (600, 150), "VPN SERVERS")

        for i, server in enumerate(self.config.vpn_servers):
            status = "✓" if server == network_data['vpn_server'] else "✗"
            color = self.config.colors['green'] if server == network_data['vpn_server'] else self.config.colors['text']
            server_text = f"{status} {server}"
            self.render_text(server_text, 'normal', color,
                             (vpn_pos[0] - 290, vpn_pos[1] - 50 + i * 30))

        # Visualização de regras de firewall
        firewall_pos = (self.config.screen_width // 2, 980)
        self.draw_firewall_rules(self.screen, network_data['firewall_rules'], firewall_pos, (600, 200))

        # Rodapé
        footer_text = "C:Connect D:Disconnect R:Rotate S:ScanPorts B:Back to Main"
        self.render_text(footer_text, 'small', self.config.colors['text'],
                         (self.config.screen_width // 2, self.config.screen_height - 15), True)

        pygame.display.flip()
        self.clock.tick(self.config.refresh_rate)

    def render_system_screen(self, system_data: Dict[str, Any], network_data: Dict[str, Any], terminal: CryptoTerminal):
        """Renderiza a tela de sistema em 3D"""
        # Atualizar históricos
        self.update_histories(system_data)

        # Implementação similar às outras telas, focada em informações do sistema
        self.screen.fill(self.config.colors['background'])

        # Atualizar ângulo da câmera
        self.camera_angle += self.config.rotation_speed

        # Título
        title_pos = (self.config.screen_width // 2, 60)
        self.draw_panel_3d(self.screen, title_pos, (600, 80))

        title_text = "SYSTEM INFORMATION"
        self.render_text(title_text, 'title', self.config.colors['accent_light'], title_pos, True)

        # Painel de informações do sistema
        sysinfo_pos = (self.config.screen_width // 2, 180)
        self.draw_panel_3d(self.screen, sysinfo_pos, (600, 200), "SYSTEM DETAILS")

        sys_info = [
            f"OS: {platform.system()} {platform.release()}",
            f"Python: {platform.python_version()}",
            f"CPU Cores: {system_data['cpu']['cores']}",
            f"Uptime: {system_data['timestamp']}",
            f"Screen: {self.config.screen_width}x{self.config.screen_height}"
        ]

        for i, text in enumerate(sys_info):
            self.render_text(text, 'normal', self.config.colors['text_highlight'],
                             (sysinfo_pos[0] - 290, sysinfo_pos[1] - 80 + i * 30))

        # Painel de uso de recursos
        usage_pos = (self.config.screen_width // 2, 400)
        self.draw_panel_3d(self.screen, usage_pos, (600, 250), "RESOURCE USAGE")

        # CPU
        cpu_text = f"CPU: {system_data['cpu']['percent']:.1f}%"
        self.render_text(cpu_text, 'normal', self.config.colors['text_highlight'],
                         (usage_pos[0] - 290, usage_pos[1] - 100))
        self.draw_progress_bar_3d(
            self.screen,
            (usage_pos[0] - 290, usage_pos[1] - 70, 580, 25),
            system_data['cpu']['percent'],
            self.config.colors['cyan']
        )

        # Memória
        mem_used = system_data['memory']['used'] / (1024 ** 3)
        mem_total = system_data['memory']['total'] / (1024 ** 3)
        mem_text = f"Memory: {system_data['memory']['percent']:.1f}% ({mem_used:.1f}/{mem_total:.1f} GB)"
        self.render_text(mem_text, 'normal', self.config.colors['text_highlight'],
                         (usage_pos[0] - 290, usage_pos[1] - 30))
        self.draw_progress_bar_3d(
            self.screen,
            (usage_pos[0] - 290, usage_pos[1], 580, 25),
            system_data['memory']['percent'],
            self.config.colors['green']
        )

        # Disco
        disk_used = system_data['disk']['used'] / (1024 ** 3)
        disk_total = system_data['disk']['total'] / (1024 ** 3)
        disk_text = f"Disk: {system_data['disk']['percent']:.1f}% ({disk_used:.1f}/{disk_total:.1f} GB)"
        self.render_text(disk_text, 'normal', self.config.colors['text_highlight'],
                         (usage_pos[0] - 290, usage_pos[1] + 40))
        self.draw_progress_bar_3d(
            self.screen,
            (usage_pos[0] - 290, usage_pos[1] + 70, 580, 25),
            system_data['disk']['percent'],
            self.config.colors['yellow']
        )

        # Visualização de processos 3D
        processes_pos = (self.config.screen_width // 2, 680)
        self.draw_process_cubes(self.screen, system_data['processes'], processes_pos, (800, 300))

        # Gráficos
        graph_pos = (self.config.screen_width // 2, 1020)
        self.draw_graph_3d(
            self.screen,
            (graph_pos[0] - 300, graph_pos[1]),
            (400, 150),
            list(self.cpu_history),
            self.config.colors['cyan'],
            "CPU HISTORY"
        )

        self.draw_graph_3d(
            self.screen,
            (graph_pos[0] + 300, graph_pos[1]),
            (400, 150),
            list(self.memory_history),
            self.config.colors['green'],
            "MEMORY HISTORY"
        )

        # Rodapé
        footer_text = "B:Back to Main"
        self.render_text(footer_text, 'small', self.config.colors['text'],
                         (self.config.screen_width // 2, self.config.screen_height - 15), True)

        pygame.display.flip()
        self.clock.tick(self.config.refresh_rate)

    def render_terminal_screen(self, system_data: Dict[str, Any], network_data: Dict[str, Any],
                               terminal: CryptoTerminal):
        """Renderiza a tela do terminal criptografado"""
        # Atualizar históricos
        self.update_histories(system_data)

        self.screen.fill(self.config.colors['background'])

        # Atualizar ângulo da câmera
        self.camera_angle += self.config.rotation_speed

        # Título
        title_pos = (self.config.screen_width // 2, 60)
        self.draw_panel_3d(self.screen, title_pos, (600, 80))

        title_text = "SOVIET CRYPTO TERMINAL"
        self.render_text(title_text, 'title', self.config.colors['accent_light'], title_pos, True)

        # Terminal principal
        term_pos = (self.config.screen_width // 2, 350)
        self.draw_terminal(self.screen, terminal, term_pos, (1000, 500))

        # Painel de ajuda
        help_pos = (self.config.screen_width // 2, 850)
        self.draw_panel_3d(self.screen, help_pos, (1000, 200), "COMMAND REFERENCE")

        # Comandos disponíveis (apenas os primeiros 16)
        commands = list(self.config.crypto_language.values())
        command_count = min(16, len(commands))

        for i in range(command_count):
            row = i // 4
            col = i % 4
            cmd = commands[i]
            self.render_text(cmd, 'small', self.config.colors['text_highlight'],
                             (help_pos[0] - 450 + col * 230, help_pos[1] - 70 + row * 25))

        # Rodapé
        footer_text = "ENTER:Execute Command TAB:Auto-complete B:Back to Main"
        self.render_text(footer_text, 'small', self.config.colors['text'],
                         (self.config.screen_width // 2, self.config.screen_height - 15), True)

        pygame.display.flip()
        self.clock.tick(self.config.refresh_rate)


# =============================================================================
# SISTEMA PRINCIPAL 3D (CORRIGIDO)
# =============================================================================
class SovietPureOS3D:
    def __init__(self):
        self.running = False
        self.config = SovietConfig3D()
        self.telemetry = QuantumTelemetry()
        self.network = SovietNetwork(self.config)
        self.terminal = CryptoTerminal(self.config)
        self.renderer = SovietRenderer3D(self.config)
        self.current_screen = "main"

    def start(self):
        """Inicia o sistema operacional 3D"""
        try:
            self.running = True
            print(f"🚀 Iniciando {self.config.system_name}...")

            self.main_loop()

        except KeyboardInterrupt:
            print(f"⚠️  Interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro fatal: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.shutdown()

    def main_loop(self):
        """Loop principal do sistema 3D"""
        last_update = time.time()

        while self.running:
            current_time = time.time()

            # Processar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self._process_key(event.key)

            # Atualizar dados periodicamente
            if current_time - last_update >= 1.0:  # Atualizar a cada segundo
                try:
                    system_data = self.telemetry.get_system_status()
                    network_data = self.network.get_network_info()
                    last_update = current_time

                    # Renderizar tela atual
                    if self.current_screen == "main":
                        self.renderer.render_main_screen(system_data, network_data, self.terminal)
                    elif self.current_screen == "network":
                        self.renderer.render_network_screen(system_data, network_data, self.terminal)
                    elif self.current_screen == "system":
                        self.renderer.render_system_screen(system_data, network_data, self.terminal)
                    elif self.current_screen == "terminal":
                        self.renderer.render_terminal_screen(system_data, network_data, self.terminal)

                except Exception as e:
                    print(f"Erro durante atualização: {e}")
                    # Continuar executando mesmo com erro

    def _process_key(self, key):
        """Processa entrada do teclado"""
        try:
            if key == pygame.K_F1:
                self.current_screen = "main"
            elif key == pygame.K_F2:
                self.current_screen = "network"
            elif key == pygame.K_F3:
                self.current_screen = "system"
            elif key == pygame.K_F7:
                self.current_screen = "terminal"
            elif key == pygame.K_F8 or key == pygame.K_ESCAPE:
                self.running = False

            # Comandos específicos da tela de rede
            elif key == pygame.K_c and self.current_screen == "network":
                self.network.vpn_connect()
            elif key == pygame.K_d and self.current_screen == "network":
                self.network.vpn_disconnect()
            elif key == pygame.K_r and self.current_screen == "network":
                self.network.vpn_rotate()
            elif key == pygame.K_s and self.current_screen == "network":
                self.network.scan_ports()

            # Comando de voltar
            elif key == pygame.K_b and self.current_screen != "main":
                self.current_screen = "main"

            # Comandos do terminal
            elif self.current_screen == "terminal":
                if key == pygame.K_RETURN:
                    if self.terminal.current_input.strip():
                        self.terminal.execute_command(self.terminal.current_input)
                    self.terminal.current_input = ""
                elif key == pygame.K_BACKSPACE:
                    if self.terminal.current_input:
                        self.terminal.current_input = self.terminal.current_input[:-1]
                elif key == pygame.K_TAB:
                    # Auto-completar
                    if self.terminal.current_input:
                        for cmd in self.terminal.commands.keys():
                            if cmd.startswith(self.terminal.current_input.lower()):
                                self.terminal.current_input = cmd
                                break
                elif key < 256:
                    # Adicionar caractere à entrada
                    char = chr(key)
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        char = char.upper()
                    else:
                        char = char.lower()
                    self.terminal.current_input += char

        except Exception as e:
            print(f"Erro ao processar tecla: {e}")

    def shutdown(self):
        """Desliga o sistema"""
        print(f"🔴 Desligando {self.config.system_name}...")
        pygame.quit()
        print(f"✅ Sistema desligado com sucesso!")


# =============================================================================
# CONFIGURAÇÃO CORRIGIDA
# =============================================================================
class SovietConfig3D:
    def __init__(self):
        self.system_name = "SOVIET PURE OS 3D"
        self.version = "3.1.4"
        self.codename = "RED PYTHON 3D"

        # Configurações de display
        self.screen_width = 1280
        self.screen_height = 1024  # Aumentado para caber todos os elementos
        self.fullscreen = False
        self.refresh_rate = 60

        # Cores do tema soviético
        self.colors = {
            'background': (10, 15, 20),
            'panel': (30, 40, 50),
            'accent': (200, 30, 30),
            'accent_light': (220, 50, 50),
            'green': (30, 200, 30),
            'cyan': (30, 180, 200),
            'yellow': (220, 200, 30),
            'text': (220, 220, 220),
            'text_highlight': (255, 255, 255),
            'warning': (255, 100, 0),
            'danger': (255, 30, 30),
            'success': (50, 200, 50),
        }

        # Configurações 3D
        self.camera_distance = 10
        self.camera_height = 3
        self.rotation_speed = 0.005
        self.panel_spacing = 2.5

        # Configurações de sistema
        self.vpn_servers = [
            "vpn.moscow.soviet",
            "vpn.leningrad.soviet",
            "vpn.stalingrad.soviet",
            "vpn.siberia.soviet"
        ]

        # Security settings
        self.vpn_rotate_interval = 30  # seconds
        self.suspicious_processes = [
            "keylogger", "rat", "backdoor", "trojan", "spyware",
            "malware", "virus", "ransomware", "exploit", "rootkit"
        ]

        # Encrypted terminal language (list format to avoid slicing issues)
        self.crypto_language_list = [
            "scan", "hack", "encrypt", "decrypt",
            "firewall", "vpn", "analyze", "protect",
            "attack", "defend", "system", "network",
            "security", "process", "monitor", "detect",
            "terminate", "connect", "disconnect", "status"
        ]

        # Mapping for encrypted commands
        self.crypto_language = {
            "scan": "scan",
            "hack": "hack",
            "encrypt": "encrypt",
            "decrypt": "decrypt",
            "firewall": "firewall",
            "vpn": "vpn",
            "analyze": "analyze",
            "protect": "protect",
            "attack": "attack",
            "defend": "defend",
            "system": "system",
            "network": "network",
            "security": "security",
            "process": "process",
            "monitor": "monitor",
            "detect": "detect",
            "terminate": "terminate",
            "connect": "connect",
            "disconnect": "disconnect",
            "status": "status"
        }

# =============================================================================
# PONTO DE ENTRADA CORRIGIDO
# =============================================================================
def main():
    """Função principal"""
    # Verificar e instalar dependências
    try:
        import pygame
    except ImportError:
        print("Instalando dependências...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("Dependências instaladas. Reinicie o programa.")
        return

    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print(f"""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║          SOVIET QUANTUM OS 3D v3.1.4 - RED PYTHON 3D                         ║
    ║           Terminal Criptografado & Sistema de Segurança                      ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    print("Controles:")
    print("F1 - Tela Principal | F2 - Rede | F3 - Sistema | F7 - Terminal | F8 - Sair")
    print("No Terminal: Digite comandos em inglês (ex: 'scan ports')")
    print("Auto-completar: TAB | Executar: ENTER")

    # Iniciar o sistema
    soviet_os = SovietPureOS3D()
    soviet_os.start()


if __name__ == "__main__":
    main()