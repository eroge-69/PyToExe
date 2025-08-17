global pickaxe_bind_key  # inserted
global keyauthapp  # inserted
global listener  # inserted
global gui_visible  # inserted
global volx_instance  # inserted
global main_gui_window  # inserted
global listener_thread  # inserted
global fov_overlay_instance  # inserted
global custom_binds  # inserted
global overlay_control_signals  # inserted
import json
import os
import sys
import threading
import ctypes
import cv2
import math
import numpy as np
import time
import torch
import uuid
import win32api
import win32con
import traceback
import platform
import hashlib
from time import sleep
from datetime import datetime, timezone, timedelta
import random
import binascii
import subprocess
from PIL import Image
import json as jsond
try:
    import requests
    import qrcode
    from discord_interactions import verify_key
    if platform.system() == 'Windows':
        import win32security
except ModuleNotFoundError:
    print('ERROR Fucking authentication libraries not found! What a shitshow.')
    print(' You need to install this crap for the auth to work.')
    print(' Run this command, dumbass pip install requests qrcode discord_interactions Pillow pywin32')
    sys.exit(1)

class api:
    name = ownerid = version = hash_to_check = ''

    def __init__(self, name, ownerid, version, hash_to_check):
        if len(ownerid)!= 10:
            print('ERROR: Invalid ownerid length. Please check your KeyAuth configuration.')
            time.sleep(3)
            os._exit(1)
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.init()
    sessionid = enckey = ''
    initialized = False

    def init(self):
        if self.sessionid!= '':
            print("You've already initialized!")
            time.sleep(3)
            os._exit(1)
        post_data = {
            'type': 'init',
            'ver': self.version,
            'hash': self.hash_to_check,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        if response == 'KeyAuth_Invalid':
            print("The application doesn't exist")
            time.sleep(3)
            os._exit(1)
        json = jsond.loads(response)
        if json['message'] == 'invalidver':
            if json['download']!= '':
                print('New Version Available')
                download_link = json['download']
                os.system(f'start {download_link}')
                time.sleep(3)
                os._exit(1)
            else:
                print('Invalid Version, Contact owner to add download link to latest app version')
                time.sleep(3)
                os._exit(1)
        if not json['success']:
            print(json['message'])
            time.sleep(3)
            os._exit(1)
        self.sessionid = json['sessionid']
        self.initialized = True

    def register(self, user, password, license, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()
        post_data = {
            'type': 'register',
            'username': user,
            'pass': password,
            'key': license,
            'hwid': hwid,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            print(json['message'])
            self.__load_user_data(json['info'])
        else:
            print(json['message'])
            time.sleep(3)
            os._exit(1)

    def upgrade(self, user, license):
        self.checkinit()
        post_data = {
            'type': 'upgrade',
            'username': user,
            'key': license,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            print(json['message'])
            print('Please restart program and login')
            time.sleep(3)
            os._exit(1)
        else:
            print(json['message'])
            time.sleep(3)
            os._exit(1)

    def login(self, user, password, code=None, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()
        post_data = {
            'type': 'login',
            'username': user,
            'pass': password,
            'hwid': hwid,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        if code is not None:
            post_data['code'] = code
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            self.__load_user_data(json['info'])
            print(json['message'])
        else:
            print(json['message'])
            time.sleep(3)
            os._exit(1)

    def license(self, key, code=None, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()
        post_data = {
            'type': 'license',
            'key': key,
            'hwid': hwid,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        if code is not None:
            post_data['code'] = code
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            self.__load_user_data(json['info'])
            print(json['message'])
        else:
            print(json['message'])
            time.sleep(3)
            os._exit(1)

    def var(self, name):
        self.checkinit()
        post_data = {
            'type': 'var',
            'varid': name,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return json['message']
        print(json['message'])
        time.sleep(3)
        os._exit(1)

    def getvar(self, var_name):
        self.checkinit()
        post_data = {
            'type': 'getvar',
            'var': var_name,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return json['response']
        print(f"NOTE This is commonly misunderstood. This is for user variables, not the normal variables.\nUse keyauthapp.var({var_name}) for normal variables")
        print(json['message'])
        time.sleep(3)
        os._exit(1)

    def setvar(self, var_name, var_data):
        self.checkinit()
        post_data = {
            'type': 'setvar',
            'var': var_name,
            'data': var_data,
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return True
        print(json['message'])
        time.sleep(3)
        os._exit(1)

    def ban(self):
        self.checkinit()
        post_data = {
            'type': 'ban',
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return True
        print(json['message'])
        time.sleep(3)
        os._exit(1)

    def file(self, fileid):
        self.checkinit()
        post_data = {'type': 'file', 'fileid': fileid, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if not json['success']:
            print(json['message'])
            time.sleep(3)
            os._exit(1)
        return binascii.unhexlify(json['contents'])

    def webhook(self, webid, param, body='', conttype=''):
        self.checkinit()
        post_data = {'type': 'webhook', 'webid': webid, 'params': param, 'body': body, 'conttype': conttype, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return json['message']
        print(json['message'])
        time.sleep(3)
        os._exit(1)

    def check(self):
        self.checkinit()
        post_data = {'type': 'check', 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return True
        return False

    def checkblacklist(self):
        self.checkinit()
        hwid = others.get_hwid()
        post_data = {'type': 'checkblacklist', 'hwid': hwid, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return True
        return False

    def log(self, message):
        self.checkinit()
        post_data = {'type': 'log', 'pcuser': os.getenv('username'), 'message': message, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        self.__do_request(post_data)

    def fetchOnline(self):
        self.checkinit()
        post_data = {'type': 'fetchOnline', 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            if len(json['users']) == 0:
                return
            return json['users']

    def fetchStats(self):
        self.checkinit()
        post_data = {'type': 'fetchStats', 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            self.__load_app_data(json['appinfo'])

    def chatGet(self, channel):
        self.checkinit()
        post_data = {'type': 'chatget', 'channel': channel, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return json['messages']
        return None

    def chatSend(self, message, channel):
        self.checkinit()
        post_data = {'type': 'chatsend', 'message': message, 'channel': channel, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            return True
        return False

    def checkinit(self):
        if not self.initialized:
            print('Initialize first, in order to use the functions')
            time.sleep(3)
            os._exit(1)

    def changeUsername(self, username):
        self.checkinit()
        post_data = {'type': 'changeUsername', 'newUsername': username, 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            print('Successfully changed username')
            return
        print(json['message'])
        time.sleep(3)
        os._exit(1)

    def logout(self):
        self.checkinit()
        post_data = {'type': 'logout', 'sessionid': self.sessionid, 'name': self.name, 'ownerid': self.ownerid}
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            print('Successfully logged out')
            time.sleep(3)
            os._exit(1)
        else:
            print(json['message'])
            time.sleep(3)
            os._exit(1)

    def enable2fa(self, code=None):
        self.checkinit()
        post_data = {
            'type': '2faenable',
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid,
            'code': code,
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        if json['success']:
            if code is None:
                print(f"Your 2FA secret code is {json['2fa']['secret_code']}")
                qr_code = json['2fa']['QRCode']
                self.display_qr_code(qr_code)
                code_input = input('Enter the 6 digit 2fa code to enable 2fa ')
                self.enable2fa(code_input)
            else:
                print('2FA has been successfully enabled!')
                time.sleep(3)
        else:
            print(f"Error {json['message']}")
            time.sleep(3)
            os._exit(1)

    def disable2fa(self, code=None):
        self.checkinit()
        code = input('Enter the 6 digit 2fa code to disable 2fa ')
        post_data = {
            'type': '2fadisable',
            'sessionid': self.sessionid,
            'name': self.name,
            'ownerid': self.ownerid,
            'code': code,
        }
        response = self.__do_request(post_data)
        json = jsond.loads(response)
        print(json['message'])
        time.sleep(3)

    def display_qr_code(self, qr_code_url):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_code_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.show()

    def __do_request(self, post_data):
        try:
            response = requests.post('https://keyauth.win/api/1.3/', data=post_data, timeout=10)
            if post_data['type'] in ('log', 'file', '2faenable', '2fadisable'):
                return response.text
            signature = response.headers.get('x-signature-ed25519')
            timestamp = response.headers.get('x-signature-timestamp')
            if not signature or not timestamp:
                print('Missing headers for signature verification.')
                time.sleep(3)
                os._exit(1)
            server_time = datetime.fromtimestamp(int(timestamp), timezone.utc)
            current_time = datetime.now(timezone.utc)
            buffer_seconds = 5
            time_difference = current_time - server_time
            if time_difference > timedelta(seconds=20 + buffer_seconds):
                print('Timestamp is too old (exceeded 20 seconds + buffer).')
                time.sleep(3)
                os._exit(1)
            if not verify_key(response.text.encode('utf-8'), signature, timestamp, '5586b4bc69c7a4b487e4563a4cd96afd39140f919bd31cea7d1c6a1e8439422b'):
                print('Signature checksum failed. Request was tampered with or session ended most likely.')
                time.sleep(3)
                os._exit(1)
            return response.text
        except requests.exceptions.Timeout:
            print('Request timed out. Server is probably downslow at the moment')
            return None

    class application_data_class:
        numUsers = numKeys = app_ver = customer_panel = onlineUsers = ''

    class user_data_class:
        username = ip = hwid = expires = createdate = lastlogin = subscription = subscriptions = ''
    user_data = user_data_class()
    app_data = application_data_class()

    def __load_app_data(self, data):
        self.app_data.numUsers = data['numUsers']
        self.app_data.numKeys = data['numKeys']
        self.app_data.app_ver = data['version']
        self.app_data.customer_panel = data['customerPanelLink']
        self.app_data.onlineUsers = data['numOnlineUsers']

    def __load_user_data(self, data):
        self.user_data.username = data['username']
        self.user_data.ip = data['ip']
        self.user_data.hwid = data['hwid'] or 'NA'
        self.user_data.expires = data['subscriptions'][0]['expiry']
        self.user_data.createdate = data['createdate']
        self.user_data.lastlogin = data['lastlogin']
        self.user_data.subscription = data['subscriptions'][0]['subscription']
        self.user_data.subscriptions = data['subscriptions']

class others:
    @staticmethod
    def get_hwid():
        if platform.system() == 'Linux':
            with open('/etc/machine-id') as f:
                hwid = f.read()
                return hwid
        else:
            if platform.system() == 'Windows':
                winuser = os.getlogin()
                sid = win32security.LookupAccountName(None, winuser)[0]
                hwid = win32security.ConvertSidToStringSid(sid)
                return hwid
            if platform.system() == 'Darwin':
                output = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", stdout=subprocess.PIPE, shell=True).communicate()[0]
                serial = output.decode().split('=', 1)[1].strip().replace('"', '')
                hwid = serial.strip()
                return hwid
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QSlider, QRadioButton, QLineEdit, QScrollArea, QStackedWidget, QFrame, QMessageBox, QInputDialog, QSizePolicy, QSpacerItem, QFormLayout, QButtonGroup, QColorDialog
    from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QAction, QIcon
    from PySide6.QtCore import Qt, QTimer, QRect, QPoint, QMetaObject, QCoreApplication, Signal, QObject, QThread, QSize, Slot, QRectF
    print("[INFO] Successfully imported 'PySide6' for the new GUI.")
except ModuleNotFoundError:
    print("ERROR GUI library 'PySide6' not found!")
    print(' Run pip install PySide6')
    sys.exit(1)
try:
    from pynput import keyboard
except ModuleNotFoundError:
    print("ERROR Input library 'pynput' not found!")
    print(' Run pip install pynput')
    sys.exit(1)
try:
    import serial
    import serial.tools.list_ports
except ModuleNotFoundError:
    print("ERROR Serial library 'pyserial' not found!")
    print(' Run pip install pyserial')
    sys.exit(1)
try:
    from termcolor import colored
    if platform.system() == 'Windows':
        import pygame
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
except ModuleNotFoundError:
    if platform.system() == 'Windows':
        print("ERROR Required library 'termcolor' or 'pygame' not found!")
        print(' Run pip install termcolor pygame')
    else:
        print("ERROR Required library 'termcolor' not found!")
        print(' Run pip install termcolor')
    sys.exit(1)
except ImportError:
    if platform.system() == 'Windows':
        print('ERROR Pygame failed to import.')
try:
    import bettercam
    print(colored("[INFO] Successfully imported 'bettercam' library.", 'green'))
except ModuleNotFoundError:
    try:
        print(colored("[ERROR] Screen capture library 'bettercam' not found!", 'red'))
        print(colored(" This is needed for GPU-accelerated screen capture. It's better than that other shit.", 'yellow'))
        print(colored(' Run pip install bettercam', 'yellow'))
    except NameError:
        print("[ERROR] Screen capture library 'bettercam' not found!")
        print(' This is needed for GPU-accelerated screen capture.')
        print(' Run pip install bettercam')
    sys.exit(1)
try:
    from ultralytics import YOLO
    print(colored("[INFO] Successfully imported 'ultralytics' library.", 'green'))
except ModuleNotFoundError:
    print(colored("[ERROR] Required library 'ultralytics' not found!", 'red'))
    print(colored(' This library is needed to load and run the models.', 'yellow'))
    print(colored(' Run pip install ultralytics', 'yellow'))
    sys.exit(1)
try:
    import tensorrt
    print(colored('[INFO] TensorRT library found.', 'green'))
except ModuleNotFoundError:
    print(colored("[WARN] TensorRT library ('tensorrt') not found!", 'yellow'))
    print(colored(" If Ultralytics can't load the '.engine' file directly, you might need this.", 'yellow'))
    print(colored(" Installing TensorRT can be complex, check NVIDIA's documentation.", 'yellow'))
except ImportError as e:
    print(colored(f'[WARN] TensorRT library found but failed to import {e}', 'yellow'))
    print(colored(' Check your TensorRT installation and PATHenvironment variables.', 'yellow'))
GHUB_MOUSE_DRIVER = None
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [('wVk', ctypes.c_ushort), ('wScan', ctypes.c_ushort), ('dwFlags', ctypes.c_ulong), ('time', ctypes.c_ulong), ('dwExtraInfo', PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [('uMsg', ctypes.c_ulong), ('wParamL', ctypes.c_short), ('wParamH', ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_long), ('dy', ctypes.c_long), ('mouseData', ctypes.c_ulong), ('dwFlags', ctypes.c_ulong), ('time', ctypes.c_ulong), ('dwExtraInfo', PUL)]

class Input_I(ctypes.Union):
    _fields_ = [('ki', KeyBdInput), ('mi', MouseInput), ('hi', HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [('type', ctypes.c_ulong), ('ii', Input_I)]

class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
if platform.system() == 'Windows':
    print(colored('[INFO] Win32 API input calls will be made directly using SendInput.', 'cyan'))
else:
    print(colored('[WARN] Not on Windows. Win32 API input methods will not be available.', 'yellow'))
volx_instance = None
listener_thread = None
aimbot_thread = None
main_gui_window = None
gui_visible = True
fov_overlay_available = True
fov_overlay_instance = None
overlay_thread = None
overlay_control_signals = None
listener = None
keyauthapp = None
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, 'lib', 'config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
VERSION = '1.0'

def clear_console():
    if platform.system() == 'Windows':
        os.system('cls')
    elif platform.system() == 'Linux':
        os.system('clear')
    elif platform.system() == 'Darwin':
        os.system("clear && printf '\x1b[3J'")

def getchecksum():
    script_path = sys.argv[0]
    if not os.path.exists(script_path):
        print(colored(f'[ERROR] Cannot find script file for checksum {script_path}', 'red'))
        return
    try:
        md5_hash = hashlib.md5()
        with open(script_path, 'rb') as file:
            md5_hash.update(file.read())
        digest = md5_hash.hexdigest()
        return digest
    except Exception as e:
        print(colored(f'[ERROR] Error calculating checksum {e}', 'red'))
        return None

def initialize_keyauth():
    global keyauthapp  # inserted
    checksum = getchecksum()
    try:
        # TODO: Replace these placeholder values with your actual KeyAuth credentials
        # Visit https://keyauth.cc/app and copy the Python code from your application
        # Replace the values below with your actual application details
        keyauthapp = api(
            name="Pentium's Application",  # Replace with your actual app name
            ownerid="kqVVq5ovJ0",  # Replace with your actual 10-character owner ID
            version="1.0",  # Replace with your actual app version
            hash_to_check=checksum
        )
        return True
    except Exception as e:
        print(colored('[FATAL ERROR] KeyAuth initialization failed!', 'red'))
        print(colored(f'Error: {e}', 'red'))
        if 'invalid ownerid' in str(e).lower() or 'invalid name' in str(e).lower():
            print(colored(" CHECK YOUR 'name' and 'ownerid' in the script!", 'yellow'))
        elif 'hash' in str(e).lower():
            print(colored(' Hash check failed. Is the script modified? Update hash on dashboard.', 'yellow'))
        elif 'network' in str(e).lower() or 'connection' in str(e).lower():
            print(colored(' Network error. Check your internet connection!', 'yellow'))
        else:
            print(colored(' Check KeyAuth dashboard status and other potential issues.', 'yellow'))
        print(colored('\nTo fix this:', 'cyan'))
        print(colored('1. Visit https://keyauth.cc/app', 'cyan'))
        print(colored('2. Create or select your application', 'cyan'))
        print(colored('3. Copy the Python code from the dashboard', 'cyan'))
        print(colored('4. Replace the placeholder values in the initialize_keyauth() function', 'cyan'))
        return False

def handle_keyauth_authentication_pyqt(parent_window=None):
    max_attempts = 3
    attempts = 0
    temp_parent_created = False
    if parent_window is None:
        if QApplication.instance() is None:
            print(colored('[CRITICAL] QApplication not initialized before KeyAuth dialogs!', 'red'))
            return False
        parent_window = QWidget()
        temp_parent_created = True
    while attempts < max_attempts:
        try:
            clear_console()
            options = ['Login', 'Register', 'License Key Only']
            choice, ok = QInputDialog.getItem(parent_window, 'Volx Authentication', 'Select Option', options, 0, False)
            if not ok or not choice:
                QMessageBox.warning(parent_window, 'Auth Cancelled', 'Authentication cancelled. Exiting.')
                if temp_parent_created:
                    parent_window.deleteLater()
                return False
            if choice == 'Login':
                user, ok1 = QInputDialog.getText(parent_window, 'Login', 'Provide username')
                if not ok1:
                    if temp_parent_created:
                        parent_window.deleteLater()
                    return False
                password, ok2 = QInputDialog.getText(parent_window, 'Login', 'Provide password', QLineEdit.EchoMode.Password)
                if not ok2:
                    if temp_parent_created:
                        parent_window.deleteLater()
                    return False
                keyauthapp.login(user, password)
                QMessageBox.information(parent_window, 'Login Success', 'Login Successful! Welcome!')
                if temp_parent_created:
                    parent_window.deleteLater()
                return True
            if choice == 'Register':
                user, ok1 = QInputDialog.getText(parent_window, 'Register', 'Provide username')
                if not ok1:
                    if temp_parent_created:
                        parent_window.deleteLater()
                    return False
                password, ok2 = QInputDialog.getText(parent_window, 'Register', 'Provide password', QLineEdit.EchoMode.Password)
                if not ok2:
                    if temp_parent_created:
                        parent_window.deleteLater()
                    return False
                license_key, ok3 = QInputDialog.getText(parent_window, 'Register', 'Provide License Key')
                if not ok3:
                    if temp_parent_created:
                        parent_window.deleteLater()
                    return False
                keyauthapp.register(user, password, license_key)
                QMessageBox.information(parent_window, 'Registration Success', 'Registration Successful! Welcome!')
                if temp_parent_created:
                    parent_window.deleteLater()
                return True
            if choice == 'License Key Only':
                key, ok1 = QInputDialog.getText(parent_window, 'License Activation', 'Enter your license')
                if not ok1:
                    if temp_parent_created:
                        parent_window.deleteLater()
                    return False
                keyauthapp.license(key)
                QMessageBox.information(parent_window, 'License Validated', 'License Validated! Access Granted!')
                if temp_parent_created:
                    parent_window.deleteLater()
                return True
            QMessageBox.warning(parent_window, 'Invalid Option', 'Invalid option selected.')
            attempts += 1
        except Exception as e:
            error_msg = f"Authentication Failed!\nKeyAuth Error {e}"
            print(colored('n[ERROR] Authentication Failed!', 'red'))
            print(colored(f'KeyAuth Error {e}', 'red'))
            QMessageBox.critical(parent_window, 'Auth Error', error_msg)
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                QMessageBox.warning(parent_window, 'Try Again', f'You have {remaining} attempt(s) left. Please try again.')
            else:
                QMessageBox.critical(parent_window, 'Too Many Failures', 'Too many failed attempts. Exiting.')
                if temp_parent_created:
                    parent_window.deleteLater()
                return False
        except KeyboardInterrupt:
            QMessageBox.warning(parent_window, 'Auth Aborted', 'Operation aborted. Exiting.')
            if temp_parent_created:
                parent_window.deleteLater()
            return False
    if temp_parent_created:
        parent_window.deleteLater()
    return False

def display_keyauth_data():
    if not keyauthapp or not hasattr(keyauthapp, 'user_data'):
        return None
    try:
        print('n' + colored('--- Session Information ---', 'blue', attrs=['bold']))
        print(colored('User Data', 'cyan'))
        print(f'  Username {keyauthapp.user_data.username}')
        print(f'  IP address {keyauthapp.user_data.ip}')
        print(f'  Hardware-Id {keyauthapp.user_data.hwid}')
        created_dt = datetime.fromtimestamp(int(keyauthapp.user_data.createdate), tz=timezone.utc)
        lastlogin_dt = datetime.fromtimestamp(int(keyauthapp.user_data.lastlogin), tz=timezone.utc)
        expires_dt = datetime.fromtimestamp(int(keyauthapp.user_data.expires), tz=timezone.utc)
        print(f"  Created at {created_dt.strftime('%Y-%m-%d %H%M%S %Z')}")
        print(f"  Last login at {lastlogin_dt.strftime('%Y-%m-%d %H%M%S %Z')}")
        print(f"  Subscription Expires at {expires_dt.strftime('%Y-%m-%d %H%M%S %Z')}")
        subs = keyauthapp.user_data.subscriptions
        if subs:
            print(colored('Other Subscriptions', 'cyan'))
            for i, sub_info in enumerate(subs):
                sub = sub_info.get('subscription', 'NA')
                expiry_ts = sub_info.get('expiry')
                expiry_str = 'NA'
                if expiry_ts:
                    expiry_dt = datetime.fromtimestamp(int(expiry_ts), tz=timezone.utc)
                    expiry_str = expiry_dt.strftime('%Y-%m-%d %H%M%S %Z')
                print(f'  [{i + 1}{len(subs)}]  Name {sub}  Expiry {expiry_str}')
        else:
            print(colored('  No other active subscriptions found.', 'yellow'))
        print('-------------------------')
    except AttributeError as e:
        print(colored(f'[ERROR] Error accessing KeyAuth data attributes {e}', 'red'))
        print(colored(' Was authentication fully successful Is user_data populated', 'yellow'))
    except Exception as e:
        print(colored(f'[ERROR] Unexpected error displaying KeyAuth data {e}', 'red'))
        traceback.print_exc()
    
VK_CODE_MAP = {
    'lmb': win32con.VK_LBUTTON,
    'rmb': win32con.VK_RBUTTON,
    'mmb': win32con.VK_MBUTTON,
    'mouse4': win32con.VK_XBUTTON1,
    'mouse5': win32con.VK_XBUTTON2,
    'backspace': win32con.VK_BACK,
    'tab': win32con.VK_TAB,
    'enter': win32con.VK_RETURN,
    'shift': win32con.VK_SHIFT,
    'ctrl': win32con.VK_CONTROL,
    'alt': win32con.VK_MENU,
    'pause': win32con.VK_PAUSE,
    'capslock': win32con.VK_CAPITAL,
    'esc': win32con.VK_ESCAPE,
    'space': win32con.VK_SPACE,
    'pageup': win32con.VK_PRIOR,
    'pagedown': win32con.VK_NEXT,
    'end': win32con.VK_END,
    'home': win32con.VK_HOME,
}

VK_NAME_MAP = {v: k for k, v in VK_CODE_MAP.items()}
VK_NAME_MAP.update({
    win32con.VK_SHIFT: 'shift',
    win32con.VK_CONTROL: 'ctrl',
    win32con.VK_MENU: 'alt',
    win32con.VK_LBUTTON: 'lmb',
    win32con.VK_RBUTTON: 'rmb',
    win32con.VK_MBUTTON: 'mmb',
    win32con.VK_XBUTTON1: 'mouse4',
    win32con.VK_XBUTTON2: 'mouse5',
    win32con.VK_CAPITAL: 'capslock',
    win32con.VK_TAB: 'tab',
    win32con.VK_INSERT: 'insert',
    186: ';',
    187: '=',
    188: ',',
    189: '-',
    190: '.',
    191: '/',
    192: '`',
    219: '[',
    220: "\\",
    221: ']',
    222: "'",
})

def get_vk_code(key_name):
    key_name = key_name.lower().strip()
    return VK_CODE_MAP.get(key_name)

def get_key_name(vk_code):
    return VK_NAME_MAP.get(vk_code, f'VK_{vk_code}')

class OverlayControlSignals(QObject):
    toggle_visibility_signal = Signal(bool)
    update_params_signal = Signal()

class FOVOverlayWidget(QWidget):
    def __init__(self, aimbot_ref, overlay_signals_ref):
        super().__init__()
        self.aimbot_ref = aimbot_ref
        self.overlay_signals_ref = overlay_signals_ref
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.current_fov_radius_pixels = 0
        self.capture_region_center_x = screen_geometry.width() // 2
        self.capture_region_center_y = screen_geometry.height() // 2
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_params_and_repaint_from_timer)
        self.timer.start(33)
        if self.overlay_signals_ref:
            self.overlay_signals_ref.update_params_signal.connect(self._update_params_and_repaint_from_timer)

    def _update_params_and_repaint_from_timer(self):
        if not self.aimbot_ref:
            return
        if self.aimbot_ref.capture_region:
            reg_left, reg_top, reg_right, reg_bottom = self.aimbot_ref.capture_region
            capture_width = reg_right - reg_left
            capture_height = reg_bottom - reg_top
            self.capture_region_center_x = reg_left + capture_width // 2
            self.capture_region_center_y = reg_top + capture_height // 2
        else:
            screen_geometry = QApplication.primaryScreen().geometry()
            self.capture_region_center_x = screen_geometry.width() // 2
            self.capture_region_center_y = screen_geometry.height() // 2
        is_aiming_with_key = Aimbot.is_targeted()
        if Aimbot.ads_fov_enabled and is_aiming_with_key:
            self.current_fov_radius_pixels = Aimbot.ads_fov_radius
        else:
            self.current_fov_radius_pixels = Aimbot.fov_radius
        self.update()

    @Slot(bool)
    def set_visibility_slot(self, visible):
        effective_visible = visible and Aimbot.fov_overlay_enabled and (not getattr(Aimbot, 'pickaxe_mode_active', False))
        if effective_visible:
            if not self.isVisible():
                self.show()
        else:
            if self.isVisible():
                self.hide()
        self.update()

    def paintEvent(self, event):
        if not Aimbot.aimbot_enabled_internal or not Aimbot.fov_overlay_enabled or getattr(Aimbot, 'pickaxe_mode_active', False):
            return None
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r, g, b, a = Aimbot.fov_overlay_color_rgba
        pen = QPen(QColor(r, g, b, a))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        center_point = QPoint(int(self.capture_region_center_x), int(self.capture_region_center_y))
        if Aimbot.fov_overlay_shape == 'Circle':
            radius = self.current_fov_radius_pixels
            if radius > 0:
                painter.drawEllipse(center_point, int(radius), int(radius))
        else:
            if Aimbot.fov_overlay_shape == 'Rectangle':
                width = Aimbot.fov_rectangle_width
                height = Aimbot.fov_rectangle_height
                corner_radius = Aimbot.fov_rectangle_corner_radius
                if width > 0 and height > 0:
                    rect_top_left_x = self.capture_region_center_x - width / 2.0
                    rect_top_left_y = self.capture_region_center_y - height / 2.0
                    rect = QRectF(rect_top_left_x, rect_top_left_y, width, height)
                    painter.drawRoundedRect(rect, corner_radius, corner_radius)

    def closeEvent(self, event):
        self.timer.stop()
        if self.overlay_signals_ref:
            try:
                self.overlay_signals_ref.update_params_signal.disconnect(self._update_params_and_repaint_from_timer)
            except TypeError:
                pass
        event.accept()

class Aimbot:
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    aimbot_enabled_internal = False
    _stop_requested = False
    yolo_model = None
    ser = None
    camera = None
    capture_region = None
    input_method = 'Send Input'
    mouse_dll = None
    arduino_port = None
    serial_lock = threading.Lock()
    aim_key_vk = win32con.VK_RBUTTON
    aim_key_name = 'rmb'
    clahe = None
    was_aiming_last_frame = False
    fov_overlay_enabled = True
    fov_overlay_shape = 'Circle'
    fov_overlay_color_rgba = (255, 255, 255, 200)
    fov_rectangle_width = 200.0
    fov_rectangle_height = 150.0
    fov_rectangle_corner_radius = 15.0
    selected_model_file = 'universal.engine'
    ai_aim_strength = 100.0
    fov_radius = 100.0
    current_confidence = 0.45
    current_iou = 0.45
    target_body_part = 'Body'
    ads_fov_enabled = False
    ads_fov_radius = 50.0
    sticky_strength = 0.5
    humanization_enabled = False
    humanization_reaction_delay_ms = 80.0
    humanization_reaction_time_randomness_ms = 40.0
    humanization_jitter_strength = 0.5
    humanization_curve_selection = 'Random'
    max_detections_to_consider = 1
    target_game_sens = 0.3
    x_game_sens_multiplier = 1.0
    y_game_sens_multiplier = 1.0
    mouse_dpi = 800
    game_resolution_width = 1920
    game_resolution_height = 1080
    _REFERENCE_GAME_SENS = 0.5
    _REFERENCE_DPI = 800.0
    _MIN_EFFECTIVE_SENS = 0.01
    smoothing_steps = 1
    smoothing_delay = 0.0001
    anti_lag_enabled = True
    anti_lag_strength_multiplier = 1000.0
    anti_lag_sticky_radius = 500
    anti_lag_sticky_force = 1.1
    bloom_reducer_enabled = False
    fps_capper_enabled = False
    target_fps_cap = 240
    collect_data_enabled = False
    collect_data_output_resolution_str = 'native'
    collect_data_final_resize_enabled = False
    collect_data_final_resize_resolution_str = 'native'
    dynamic_close_range_threshold = 65
    dynamic_close_range_speed_boost = 5.0
    dynamic_close_range_damping_reduction = 0.6
    dynamic_far_range_threshold = 280
    dynamic_far_range_speed_boost = 4.0
    dynamic_vertical_threshold = 70
    dynamic_vertical_speed_boost = 5.0
    dynamic_vertical_damping_reduction = 0.5
    tracking_dampening_reduction = 0.8
    volx_aim_smooth = 80.0
    volx_pixel_increment = 1000.0
    volx_randomness = 0.25
    volx_sensitivity = 0.005
    volx_distance_to_scale = 100.0
    volx_smoothing_type = 'Default'
    volx_snap_strength = 1.0
    prediction_enabled = False
    PREDICTION_LEAD_TIME_SECONDS = 0.06
    _target_history = {}
    _target_history_max_age = 1.0
    adaptive_smoothing_enabled = True
    adaptive_slow_threshold_pps = 50
    adaptive_fast_threshold_pps = 200
    adaptive_smoothing_factor_slow_steps = 1.2
    adaptive_smoothing_factor_fast_steps = 0.5
    adaptive_smoothing_factor_slow_delay = 1.1
    adaptive_smoothing_factor_fast_delay = 0.5
    fps_updated = Signal(int)
    aimbot_status_changed_signal = Signal(bool)
    pickaxe_mode_active = False

    def __init__(self, box_constant=416, debug=False):
        self._stop_requested = False
        self.box_constant = box_constant
        self.debug = debug
        self.serial_lock = threading.Lock()
        self.was_aiming_last_frame = False
        self.capture_region = None
        Aimbot.pickaxe_mode_active = False
        if not self.load_config():
            print(colored('[WARN] Config loading had issues or file not found. Using defaults where needed.', 'yellow'))
        try:
            Aimbot.clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        except Exception as e:
            print(colored(f'[ERROR] Failed to create CLAHE object {e}. Bloom Reducer will be non-functional!', 'red'))
            Aimbot.clahe = None
        try:
            model_path = os.path.join(SCRIPT_DIR, 'lib', Aimbot.selected_model_file)
            if not os.path.exists(model_path):
                self.handle_error(f"TensorRT Engine file '{model_path}' is missing! Please place it in the 'lib' folder.", critical=True)
            self.yolo_model = YOLO(model_path, task='detect')
            if torch.cuda.is_available():
                pass
            else:
                self.handle_error("TensorRT engine requires CUDA, but it's not available. Cannot continue.", critical=True)
        except FileNotFoundError:
            self.handle_error(f"TensorRT Engine file '{model_path}' is missing! Put it in the 'lib' folder.", critical=True)
        except Exception as e:
            err_str = str(e).lower()
            if 'tensorrt' in err_str or 'engine' in err_str or 'deserialize' in err_str:
                extra_msg = f"Error loading the TensorRT engine ('{Aimbot.selected_model_file}'). Is it compatible? Was it built for your GPU/TensorRT version?"
            elif 'cuda' in err_str or 'gpu' in err_str:
                extra_msg = f"CUDA related error loading the TensorRT engine ('{Aimbot.selected_model_file}'). Check drivers, PyTorch CUDA version, and TensorRT compatibility."
            else:
                extra_msg = f"Check ultralytics, TensorRT installation and engine file ('{Aimbot.selected_model_file}') integrity."
            self.handle_error(f"Error loading TensorRT engine or initializing Aimbot {e}\n{extra_msg}\n{traceback.format_exc()}", critical=True)
        print('[INFO] Initializing screen capture with BetterCam...', flush=True)
        try:
            self.camera = bettercam.create(output_color='BGR', output_idx=0)
            if self.camera is None:
                self.handle_error('Failed to create BetterCam instance. Is a display connected Check drivers.', critical=True)
            current_target_fps_for_start = 0
            if Aimbot.fps_capper_enabled and Aimbot.target_fps_cap > 0:
                current_target_fps_for_start = Aimbot.target_fps_cap
            desktop_width = ctypes.windll.user32.GetSystemMetrics(0)
            desktop_height = ctypes.windll.user32.GetSystemMetrics(1)
            box_w = int(self.box_constant)
            box_h = int(self.box_constant)
            reg_left = int((desktop_width - box_w) / 2)
            reg_top = int((desktop_height - box_h) / 2)
            reg_right = reg_left + box_w
            reg_bottom = reg_top + box_h
            self.capture_region = (reg_left, reg_top, reg_right, reg_bottom)
            self.camera.start(region=self.capture_region, target_fps=current_target_fps_for_start)
        except Exception as e:
            self.handle_error(f"Failed to initialize BetterCam {e}\n{traceback.format_exc()}", critical=True)
        self.set_input_method(Aimbot.input_method, initial_load=True)

    def load_config(self):
        global pickaxe_bind_key  # inserted
        config_data = {}
        try:
            if not os.path.exists(CONFIG_PATH):
                print(colored(f"[WARN] Config file '{CONFIG_PATH}' not found! Using built-in defaults. Save from GUI to create one.", 'yellow'))
                return False
            with open(CONFIG_PATH) as f:
                config_data = json.load(f)
            Aimbot.selected_model_file = config_data.get('selected_model_file', Aimbot.selected_model_file)
            if Aimbot.selected_model_file not in ['fortnite.engine', 'universal.engine']:
                print(colored(f"[WARN] Invalid selected_model_file ('{Aimbot.selected_model_file}') in config. Defaulting to 'universal.engine'.", 'yellow'))
                Aimbot.selected_model_file = 'universal.engine'
            Aimbot.ai_aim_strength = float(config_data.get('ai_aim_strength', Aimbot.ai_aim_strength))
            Aimbot.fov_radius = float(config_data.get('fov_radius', Aimbot.fov_radius))
            Aimbot.fov_overlay_enabled = bool(config_data.get('fov_overlay_enabled', Aimbot.fov_overlay_enabled))
            Aimbot.fov_overlay_shape = config_data.get('fov_overlay_shape', Aimbot.fov_overlay_shape)
            loaded_fov_color = config_data.get('fov_overlay_color_rgba', Aimbot.fov_overlay_color_rgba)
            if isinstance(loaded_fov_color, list) and len(loaded_fov_color) == 4 and all((isinstance(c, int) and 0 <= c <= 255) for c in loaded_fov_color):
                Aimbot.fov_overlay_color_rgba = tuple(loaded_fov_color)
            else:
                print(colored(f"[WARN] Invalid fov_overlay_color_rgba ('{loaded_fov_color}') in config. Using default.", 'yellow'))
                Aimbot.fov_overlay_color_rgba = (255, 255, 255, 200)
            Aimbot.fov_rectangle_width = float(config_data.get('fov_rectangle_width', Aimbot.fov_rectangle_width))
            Aimbot.fov_rectangle_height = float(config_data.get('fov_rectangle_height', Aimbot.fov_rectangle_height))
            Aimbot.fov_rectangle_corner_radius = float(config_data.get('fov_rectangle_corner_radius', Aimbot.fov_rectangle_corner_radius))
            Aimbot.smoothing_steps = int(config_data.get('smoothing_steps', Aimbot.smoothing_steps))
            Aimbot.smoothing_delay = float(config_data.get('smoothing_delay', Aimbot.smoothing_delay))
            Aimbot.sticky_strength = float(config_data.get('sticky_strength', Aimbot.sticky_strength))
            Aimbot.humanization_enabled = bool(config_data.get('humanization_enabled', Aimbot.humanization_enabled))
            Aimbot.humanization_reaction_delay_ms = float(config_data.get('humanization_reaction_delay_ms', Aimbot.humanization_reaction_delay_ms))
            Aimbot.humanization_reaction_time_randomness_ms = float(config_data.get('humanization_reaction_time_randomness_ms', Aimbot.humanization_reaction_time_randomness_ms))
            Aimbot.humanization_jitter_strength = float(config_data.get('humanization_jitter_strength', Aimbot.humanization_jitter_strength))
            Aimbot.humanization_curve_selection = config_data.get('humanization_curve_selection', Aimbot.humanization_curve_selection)
            Aimbot.max_detections_to_consider = int(config_data.get('max_detections_to_consider', Aimbot.max_detections_to_consider))
            Aimbot.target_game_sens = float(config_data.get('target_game_sens', Aimbot.target_game_sens))
            Aimbot.x_game_sens_multiplier = float(config_data.get('x_game_sens_multiplier', Aimbot.x_game_sens_multiplier))
            Aimbot.y_game_sens_multiplier = float(config_data.get('y_game_sens_multiplier', Aimbot.y_game_sens_multiplier))
            Aimbot.mouse_dpi = int(config_data.get('mouse_dpi', Aimbot.mouse_dpi))
            res_str = config_data.get('game_resolution', f"{Aimbot.game_resolution_width}x{Aimbot.game_resolution_height}")
            try:
                w_str, h_str = res_str.lower().split('x')
                Aimbot.game_resolution_width = int(w_str)
                Aimbot.game_resolution_height = int(h_str)
            except ValueError:
                print(colored(f"[WARN] Invalid game_resolution format '{res_str}' in config. Using defaults.", 'yellow'))
            Aimbot.anti_lag_strength_multiplier = float(config_data.get('anti_lag_strength_multiplier', Aimbot.anti_lag_strength_multiplier))
            Aimbot.anti_lag_sticky_radius = int(config_data.get('anti_lag_sticky_radius', Aimbot.anti_lag_sticky_radius))
            Aimbot.bloom_reducer_enabled = bool(config_data.get('bloom_reducer_enabled', Aimbot.bloom_reducer_enabled))
            Aimbot.fps_capper_enabled = bool(config_data.get('fps_capper_enabled', Aimbot.fps_capper_enabled))
            loaded_fps_cap = int(config_data.get('target_fps_cap', Aimbot.target_fps_cap))
            Aimbot.target_fps_cap = max(30, min(1000, loaded_fps_cap))
            Aimbot.ads_fov_enabled = bool(config_data.get('ads_fov_enabled', Aimbot.ads_fov_enabled))
            Aimbot.ads_fov_radius = float(config_data.get('ads_fov_radius', Aimbot.ads_fov_radius))
            Aimbot.collect_data_enabled = bool(config_data.get('collect_data_enabled', Aimbot.collect_data_enabled))
            Aimbot.collect_data_output_resolution_str = config_data.get('collect_data_output_resolution_str', Aimbot.collect_data_output_resolution_str)
            Aimbot.collect_data_final_resize_enabled = bool(config_data.get('collect_data_final_resize_enabled', Aimbot.collect_data_final_resize_enabled))
            Aimbot.collect_data_final_resize_resolution_str = config_data.get('collect_data_final_resize_resolution_str', Aimbot.collect_data_final_resize_resolution_str)
            Aimbot.arduino_port = config_data.get('arduino_port', Aimbot.arduino_port)
            loaded_input_method = config_data.get('input_method', Aimbot.input_method)
            if loaded_input_method in ['Send Input', 'Arduino', 'DDXoft']:
                Aimbot.input_method = loaded_input_method
            else:
                Aimbot.input_method = 'Send Input'
            loaded_target = config_data.get('target_body_part', Aimbot.target_body_part)
            if loaded_target in ['Head', 'Neck', 'Body']:
                Aimbot.target_body_part = loaded_target
            else:
                print(colored(f"[WARN] Invalid target_body_part '{loaded_target}' in config. Using default '{Aimbot.target_body_part}'.", 'yellow'))
            loaded_aim_key_name = config_data.get('aim_key', Aimbot.aim_key_name).lower().strip()
            vk_code = get_vk_code(loaded_aim_key_name)
            if vk_code:
                Aimbot.aim_key_name = loaded_aim_key_name
                Aimbot.aim_key_vk = vk_code
            else:
                print(colored(f"[WARN] Invalid 'aim_key' ('{loaded_aim_key_name}') found in config! Defaulting to '{Aimbot.aim_key_name}'. Please fix your config.", 'yellow'))
            Aimbot.volx_aim_smooth = float(config_data.get('volx_aim_smooth', Aimbot.volx_aim_smooth))
            Aimbot.volx_pixel_increment = float(config_data.get('volx_pixel_increment', Aimbot.volx_pixel_increment))
            Aimbot.volx_randomness = float(config_data.get('volx_randomness', Aimbot.volx_randomness))
            Aimbot.volx_sensitivity = float(config_data.get('volx_sensitivity', Aimbot.volx_sensitivity))
            Aimbot.volx_distance_to_scale = float(config_data.get('volx_distance_to_scale', Aimbot.volx_distance_to_scale))
            Aimbot.volx_smoothing_type = config_data.get('volx_smoothing_type', Aimbot.volx_smoothing_type)
            Aimbot.volx_snap_strength = float(config_data.get('volx_snap_strength', Aimbot.volx_snap_strength))
            if 'custom_binds' in config_data and isinstance(config_data['custom_binds'], list):
                loaded_binds = config_data['custom_binds']
                for i, bind in enumerate(loaded_binds[:len(custom_binds)]):
                    custom_binds[i].update(bind)
            pickaxe_bind_key = config_data.get('pickaxe_bind_key', '').strip().lower()
            return True
        except json.JSONDecodeError:
            self.handle_error(f"Config file '{CONFIG_PATH}' is corrupted! Delete it and run setup or fix it manually.", critical=True)
            return False
        except ValueError as e:
            self.handle_error(f"Config file '{CONFIG_PATH}' has invalid number format for one or more settings! Error {e}. Using defaults for problematic keys.", critical=False)
            return True
        except Exception as e:
            self.handle_error(f"Failed to load config '{CONFIG_PATH}' {e}\n{traceback.format_exc()}", critical=True)
            return False

    def print_loaded_config(self):
        print(f'[INFO] --- Loaded Config Values ({VERSION}) ---')
        print('  Screen Capture BetterCam (GPU Accelerated)')
        print(f'  Model File {Aimbot.selected_model_file} (TensorRT Engine, GPU Inference)')
        fov_overlay_stat_color = 'green' if Aimbot.fov_overlay_enabled else 'yellow'
        fov_overlay_stat_icon = 'ON' if Aimbot.fov_overlay_enabled else 'OFF'
        print(colored(f'  FOV Overlay Enabled {fov_overlay_stat_icon}', fov_overlay_stat_color) + f" (PySide6 {'Available' if fov_overlay_available else 'Missing!'})")
        print(f'  FOV Overlay Shape {Aimbot.fov_overlay_shape}')
        if Aimbot.fov_overlay_shape == 'Rectangle':
            print(f"    Rectangle Width {Aimbot.fov_rectangle_width:.1f}px, Height {Aimbot.fov_rectangle_height:.1f}px, Corner Radius {Aimbot.fov_rectangle_corner_radius:.1f}px")
        print(f'  FOV Overlay Color (RGBA) {Aimbot.fov_overlay_color_rgba}')
        print(f"  AI Aimbot Strength {Aimbot.ai_aim_strength:.1f}/100.0")
        print(f"  Sensitivity Game={Aimbot.target_game_sens:.3f}, X-Mult={Aimbot.x_game_sens_multiplier:.2f}, Y-Mult={Aimbot.y_game_sens_multiplier:.2f}, DPI={Aimbot.mouse_dpi}")
        print(f'  Game Resolution {Aimbot.game_resolution_width}x{Aimbot.game_resolution_height}')
        print(f"  Sticky Strength {Aimbot.sticky_strength:.2f}")
        print(f"  FOV Radius (Hipfire Circle) {Aimbot.fov_radius:.1f}px")
        ads_fov_stat = f"{Aimbot.ads_fov_radius:.1f}px" if Aimbot.ads_fov_enabled else 'Disabled'
        print(f"  FOV Radius (ADS Circle) {colored(ads_fov_stat, 'cyan' if Aimbot.ads_fov_enabled else 'grey')}")
        print(f'  Target Body Part {Aimbot.target_body_part}')
        print(f'  Max Targets to Consider {Aimbot.max_detections_to_consider}')
        print(f"  Humanization Enabled {('YES' if Aimbot.humanization_enabled else 'NO')}")
        print('  Prediction Enabled NO')
        print(f'  Aim Activation Key (KBM) {Aimbot.aim_key_name} (VK {Aimbot.aim_key_vk})')
        print(f'  Smoothing Steps {Aimbot.smoothing_steps}, Step Delay {Aimbot.smoothing_delay}s')
        print(f"  Arduino COM Port {(Aimbot.arduino_port if Aimbot.arduino_port else 'Not Set')}")
        input_method_display = Aimbot.input_method
        if input_method_display == 'Send Input':
            input_method_display = 'Send Input (via WinAPI SendInput)'
        else:
            if input_method_display == 'Arduino':
                input_method_display = 'Arduino'
            else:
                if input_method_display == 'DDXoft':
                    input_method_display = 'DDXoft (Driver)'
        print(f'  Input Method {input_method_display} (Mouse Control)')
        print(f"  Anti-Lag Pull Strength Multiplier {Aimbot.anti_lag_strength_multiplier:.2f}x")
        print(f"  Anti-Lag Sticky Lock Radius {Aimbot.anti_lag_sticky_radius} px (Sticky Force {Aimbot.anti_lag_sticky_force:.2f})")
        print(f"  Bloom Reducer Enabled {('YES' if Aimbot.bloom_reducer_enabled else 'Standard')}")
        print(f"  FPS Capper Enabled {('YES' if Aimbot.fps_capper_enabled else 'NO')}")
        print(f'  Target FPS Cap {Aimbot.target_fps_cap} FPS' if Aimbot.fps_capper_enabled else '  Target FPS Cap NA (BetterCam uses this at init if enabled)')
        print(colored('  NumPy Optimization ACTIVE', 'green'))
        print('----------------------------------------')
        print(f'    Volx Aim Smoothness {Aimbot.volx_aim_smooth}')
        print(f'    Volx Smoothing Type {Aimbot.volx_smoothing_type}')
        print(f'    Volx Sensitivity {Aimbot.volx_sensitivity}')
        print(f"    Volx Snap Strength {Aimbot.volx_snap_strength:.2f}")

    def handle_error(self, message, critical=False):
        print(colored(f'[ERROR] {message}', 'red'))
        if critical:
            if main_gui_window and gui_visible:
                try:
                    main_gui_window.show_critical_error_signal.emit(message)
                except Exception as gui_e:
                    print(f'(GUI QMessageBox failed via signalslot {gui_e})')
            if False:
                pass  # postinserted
            print(colored(' CRITICAL ERROR - EXITING ', 'red'))
            time.sleep(1.5)
            os._exit(1)

    def update_status_aimbot(self):
        Aimbot.aimbot_enabled_internal = not Aimbot.aimbot_enabled_internal
        if not Aimbot.aimbot_enabled_internal:
            self.was_aiming_last_frame = False
        if main_gui_window:
            main_gui_window.update_aimbot_status_signal.emit(Aimbot.aimbot_enabled_internal)
            main_gui_window.update_controls_state_signal.emit()

    def set_strength(self, strength_value):
        if not self.yolo_model:
            return
        Aimbot.current_confidence = max(0.01, strength_value / 100.0)

    def set_fov(self, fov_value):
        Aimbot.fov_radius = max(1.0, fov_value)
        if overlay_control_signals:
            overlay_control_signals.update_params_signal.emit()

    def set_humanization_reaction_delay(self, delay_ms):
        Aimbot.humanization_reaction_delay_ms = float(delay_ms)

    def set_humanization_reaction_randomness(self, randomness_ms):
        Aimbot.humanization_reaction_time_randomness_ms = float(randomness_ms)

    def set_humanization_jitter_strength(self, strength):
        Aimbot.humanization_jitter_strength = float(strength)

    def set_humanization_curve(self, curve_name):
        if curve_name in ['Random', 'Ease Out', 'Ease In', 'Linear']:
            Aimbot.humanization_curve_selection = curve_name

    def toggle_humanization(self):
        Aimbot.humanization_enabled = not Aimbot.humanization_enabled
        if main_gui_window:
            main_gui_window.update_humanization_signal.emit(Aimbot.humanization_enabled)
            main_gui_window.update_controls_state_signal.emit()

    def set_max_detections(self, num_detections):
        Aimbot.max_detections_to_consider = int(max(1, min(10, num_detections)))

    def set_sticky_strength(self, strength_value):
        Aimbot.sticky_strength = float(max(0.0, min(1.0, strength_value)))

    def set_volx_snap_strength(self, strength_value):
        Aimbot.volx_snap_strength = float(max(0.0, min(1.0, strength_value)))

    def toggle_ads_fov(self):
        Aimbot.ads_fov_enabled = not Aimbot.ads_fov_enabled
        if main_gui_window:
            main_gui_window.update_ads_fov_signal.emit(Aimbot.ads_fov_enabled)
            main_gui_window.update_controls_state_signal.emit()
        if overlay_control_signals:
            overlay_control_signals.update_params_signal.emit()

    def set_ads_fov_radius(self, fov_value):
        Aimbot.ads_fov_radius = max(1.0, fov_value)
        if overlay_control_signals:
            overlay_control_signals.update_params_signal.emit()

    def set_target_part(self, part_name):
        if part_name in ['Head', 'Neck', 'Body']:
            Aimbot.target_body_part = part_name

    def set_anti_lag_strength(self, strength_multiplier):
        Aimbot.anti_lag_strength_multiplier = float(strength_multiplier)

    def set_anti_lag_sticky_radius(self, radius_px):
        Aimbot.anti_lag_sticky_radius = int(radius_px)

    def toggle_bloom_reducer(self):
        Aimbot.bloom_reducer_enabled = not Aimbot.bloom_reducer_enabled
        if main_gui_window:
            main_gui_window.update_bloom_reducer_signal.emit(Aimbot.bloom_reducer_enabled)

    def toggle_fps_capper(self):
        Aimbot.fps_capper_enabled = not Aimbot.fps_capper_enabled
        if main_gui_window:
            main_gui_window.update_fps_capper_signal.emit(Aimbot.fps_capper_enabled)
            main_gui_window.update_controls_state_signal.emit()

    def set_target_fps_cap(self, fps_value):
        Aimbot.target_fps_cap = int(max(30, min(1000, fps_value)))

    def set_ai_aim_strength(self, strength_value):
        Aimbot.ai_aim_strength = float(max(0.0, min(100.0, strength_value)))

    def set_target_game_sens(self, sens_value_str):
        try:
            Aimbot.target_game_sens = float(sens_value_str)
            return True
        except ValueError:
            return False

    def set_x_game_sens_multiplier(self, mult_value_str):
        try:
            Aimbot.x_game_sens_multiplier = float(mult_value_str)
            return True
        except ValueError:
            return False

    def set_y_game_sens_multiplier(self, mult_value_str):
        try:
            Aimbot.y_game_sens_multiplier = float(mult_value_str)
            return True
        except ValueError:
            return False

    def set_mouse_dpi(self, dpi_value_str):
        try:
            Aimbot.mouse_dpi = int(dpi_value_str)
            return True
        except ValueError:
            return False

    def set_game_resolution(self, res_str):
        try:
            w_str, h_str = res_str.lower().split('x')
            Aimbot.game_resolution_width = int(w_str)
            Aimbot.game_resolution_height = int(h_str)
            return True
        except ValueError:
            return False

    def set_smoothing_steps(self, steps):
        Aimbot.smoothing_steps = int(steps)

    def set_smoothing_delay(self, delay_sec):
        Aimbot.smoothing_delay = float(delay_sec)

    def set_input_method(self, method, initial_load=False):
        should_print = not initial_load or method!= Aimbot.input_method
        with self.serial_lock:
            if self.ser and self.ser.is_open:
                if method!= 'Arduino' or not initial_load:
                    try:
                        self.ser.close()
                    except Exception as e:
                        print(colored(f'[WARN] Error closing serial port {e}', 'yellow'))
                    self.ser = None
            Aimbot.input_method = method
            if method == 'Arduino':
                if not Aimbot.arduino_port:
                    if should_print:
                        self.handle_error('Arduino COM Port not configured. Please set it up first.', critical=False)
                    self._fallback_to_sendinput()
                    return
                
                # Check if the COM port is actually available
                try:
                    import serial.tools.list_ports
                    available_ports = [port.device for port in serial.tools.list_ports.comports()]
                    if Aimbot.arduino_port not in available_ports:
                        if should_print:
                            self.handle_error(f'Arduino COM Port {Aimbot.arduino_port} is not available. Available ports: {", ".join(available_ports)}', critical=False)
                        self._fallback_to_sendinput()
                        return
                except ImportError:
                    # If list_ports is not available, continue with connection attempt
                    pass
                
                if self.ser and self.ser.is_open:
                    try:
                        self.ser.close()
                        self.ser = None
                    except Exception as e:
                        print(colored(f'[WARN] Error closing serial port before reconnect {e}', 'yellow'))
                
                try:
                    # Use a shorter timeout to prevent GUI freezing
                    self.ser = serial.Serial(port=Aimbot.arduino_port, baudrate=115200, timeout=0.1, write_timeout=0.05)
                    # Reduced sleep time to prevent long GUI freezes
                    time.sleep(0.2)
                    if not self.ser.is_open:
                        if should_print:
                            self.handle_error(f'Failed to open serial port {Aimbot.arduino_port} (no exception).', critical=False)
                        self.ser = None
                        self._fallback_to_sendinput()
                    else:
                        if should_print:
                            print(colored(f'[INFO] Successfully connected to Arduino on {Aimbot.arduino_port}', 'green'))
                except serial.SerialException as e:
                    if should_print:
                        self.handle_error(f'Failed to connect to Arduino on {Aimbot.arduino_port} {e}', critical=False)
                    self.ser = None
                    self._fallback_to_sendinput()
                except Exception as e:
                    if should_print:
                        self.handle_error(f'Unexpected error connecting to Arduino {e}', critical=False)
                    self.ser = None
                    self._fallback_to_sendinput()
            if method == 'Send Input':
                pass
            if method == 'DDXoft':
                if platform.system()!= 'Windows':
                    if should_print:
                        self.handle_error('DDXoft is only available on Windows.', critical=False)
                    self._fallback_to_sendinput()
                    return
                dll_path = os.path.abspath('libmousedd40605x64.dll')
                if not os.path.exists(dll_path):
                    if should_print:
                        self.handle_error(f'DDXoft DLL not found at {dll_path}', critical=False)
                    self._fallback_to_sendinput()
                    return
                try:
                    Aimbot.mouse_dll = ctypes.WinDLL(dll_path)
                    time.sleep(1)
                    Aimbot.mouse_dll.DD_btn.argtypes = [ctypes.c_int]
                    Aimbot.mouse_dll.DD_btn.restype = ctypes.c_int
                    Aimbot.mouse_dll.DD_movR.argtypes = [ctypes.c_int, ctypes.c_int]
                    Aimbot.mouse_dll.DD_movR.restype = ctypes.c_int
                    init_code = Aimbot.mouse_dll.DD_btn(0)
                    if init_code!= 1:
                        if should_print:
                            self.handle_error(f'Failed to initialize DDXoft mouse driver (Code {init_code}). Check if another process is using it.', critical=False)
                        Aimbot.mouse_dll = None
                        self._fallback_to_sendinput()
                    else:
                        if should_print:
                            print(colored('[INFO] Loaded DDXoft driver successfully!', 'green'))
                except Exception as e:
                    if should_print:
                        self.handle_error(f'Error loading DDXoft DLL {e}', critical=False)
                    Aimbot.mouse_dll = None
                    traceback.print_exc()
                    self._fallback_to_sendinput()

    def _fallback_to_sendinput(self):
        if main_gui_window and Aimbot.input_method!= 'Send Input':
            main_gui_window.update_input_method_signal.emit('Send Input')
        if Aimbot.input_method!= 'Send Input':
            Aimbot.input_method = 'Send Input'
            print("[WARN] Falling back to 'Send Input' (via WinAPI SendInput).")

    def _send_arduino_move(self, dx, dy):
        with self.serial_lock:
            if self.ser:
                if self.ser.is_open:
                    if dx == 0 and dy == 0:
                        return
                    command = f"M {int(dx)} {int(dy)}\n"
                    try:
                        self.ser.write(command.encode('ascii'))
                    except serial.SerialTimeoutException:
                        pass
                    except serial.SerialException as e:
                        self.handle_error(f'Arduino disconnected due to write error {e}', critical=False)
                        try:
                            self.ser.close()
                        except Exception:
                            pass
                        self.ser = None
                        self._fallback_to_sendinput()
                    except Exception as e:
                        traceback.print_exc()
                        try:
                            self.ser.close()
                        except Exception:
                            pass
                        self.ser = None
                        self._fallback_to_sendinput()

    @staticmethod
    def left_click():
        if Aimbot.input_method == 'Send Input':
            mi_down = MouseInput(dx=0, dy=0, mouseData=0, dwFlags=2, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
            inp_down = Input(type=0, ii=Input_I(mi=mi_down))
            ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
            Aimbot.sleep(0.0001)
            mi_up = MouseInput(dx=0, dy=0, mouseData=0, dwFlags=4, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
            inp_up = Input(type=0, ii=Input_I(mi=mi_up))
            ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))
        else:
            if Aimbot.input_method == 'Arduino':
                return
            if Aimbot.input_method == 'DDXoft':
                if Aimbot.mouse_dll:
                    Aimbot.mouse_dll.DD_btn(1)
                    Aimbot.sleep(0.001)
                    Aimbot.mouse_dll.DD_btn(2)
                else:
                    pass
            else:
                mi_down = MouseInput(dx=0, dy=0, mouseData=0, dwFlags=2, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
                inp_down = Input(type=0, ii=Input_I(mi=mi_down))
                ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
                Aimbot.sleep(0.0001)
                mi_up = MouseInput(dx=0, dy=0, mouseData=0, dwFlags=4, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
                inp_up = Input(type=0, ii=Input_I(mi=mi_up))
                ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))

    @staticmethod
    def sleep(duration, get_now=time.perf_counter):
        if duration <= 0:
            return
        now = get_now()
        end = now + duration
        while now < end:
            now = get_now()

    @staticmethod
    def is_targeted():
        keyboard_aiming = False
        if Aimbot.aim_key_vk is not None:
            try:
                keyboard_aiming = (ctypes.windll.user32.GetAsyncKeyState(Aimbot.aim_key_vk) & 0x8000) != 0
                return keyboard_aiming
            except Exception as e:
                print(colored(f'[ERROR] Error checking key state for VK {Aimbot.aim_key_vk} ({Aimbot.aim_key_name}) {e}', 'red'))
                return keyboard_aiming
        return keyboard_aiming

    def _perform_snap(self, target_x, target_y, target_vx_pps=0):
        try:
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            center_x = screen_width // 2
            center_y = screen_height // 2
            eff_target_x = target_x
            if Aimbot.prediction_enabled and target_vx_pps!= 0:
                prediction_pixel_offset_x = target_vx_pps * Aimbot.PREDICTION_LEAD_TIME_SECONDS
                eff_target_x = target_x + prediction_pixel_offset_x
            snap_dx_pixels = eff_target_x - center_x
            snap_dy_pixels = target_y - center_y
            eff_sens_x_num = Aimbot.target_game_sens * Aimbot.x_game_sens_multiplier * (Aimbot.mouse_dpi / Aimbot._REFERENCE_DPI)
            eff_sens_y_num = Aimbot.target_game_sens * Aimbot.y_game_sens_multiplier * (Aimbot.mouse_dpi / Aimbot._REFERENCE_DPI)
            eff_sens_x_den = Aimbot._REFERENCE_GAME_SENS
            eff_sens_y_den = Aimbot._REFERENCE_GAME_SENS
            eff_sens_x_num = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_x_num)
            eff_sens_y_num = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_y_num)
            eff_sens_x_den = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_x_den)
            eff_sens_y_den = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_y_den)
            sens_factor_x = eff_sens_x_num / eff_sens_x_den
            sens_factor_y = eff_sens_y_num / eff_sens_y_den
            final_snap_dx = int(round(snap_dx_pixels / sens_factor_x)) if sens_factor_x!= 0 else 0
            final_snap_dy = int(round(snap_dy_pixels / sens_factor_y)) if sens_factor_y!= 0 else 0
            final_snap_dx = int(round(final_snap_dx * Aimbot.volx_snap_strength))
            final_snap_dy = int(round(final_snap_dy * Aimbot.volx_snap_strength))
            if final_snap_dx == 0 and final_snap_dy == 0:
                return
            num_internal_snap_steps = 1
            delay_per_internal_step = 0.0
            accumulated_dx_sent = 0
            accumulated_dy_sent = 0
            for i_step in range(1, num_internal_snap_steps + 1):
                target_sub_dx = round(final_snap_dx * (i_step / num_internal_snap_steps))
                target_sub_dy = round(final_snap_dy * (i_step / num_internal_snap_steps))
                move_this_sub_step_dx = int(target_sub_dx - accumulated_dx_sent)
                move_this_sub_step_dy = int(target_sub_dy - accumulated_dy_sent)
                if move_this_sub_step_dx!= 0 or move_this_sub_step_dy!= 0:
                    if Aimbot.input_method == 'Send Input':
                        mi_sub = MouseInput(dx=move_this_sub_step_dx, dy=move_this_sub_step_dy, mouseData=0, dwFlags=1, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
                        inp_sub = Input(type=0, ii=Input_I(mi=mi_sub))
                        ctypes.windll.user32.SendInput(1, ctypes.byref(inp_sub), ctypes.sizeof(inp_sub))
                    else:
                        if Aimbot.input_method == 'Arduino':
                            if self.ser and self.ser.is_open:
                                self._send_arduino_move(move_this_sub_step_dx, move_this_sub_step_dy)
                        else:
                            if Aimbot.input_method == 'DDXoft' and Aimbot.mouse_dll:
                                Aimbot.mouse_dll.DD_movR(move_this_sub_step_dx, move_this_sub_step_dy)
                    accumulated_dx_sent += move_this_sub_step_dx
                    accumulated_dy_sent += move_this_sub_step_dy
                if i_step < num_internal_snap_steps and delay_per_internal_step > 0:
                    Aimbot.sleep(delay_per_internal_step)
        except Exception as e:
            traceback.print_exc()

    def move_crosshair(self, target_x, target_y, target_velocity_pps=0, target_vx_pps=0):
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        center_x = screen_width // 2
        center_y = screen_height // 2
        current_target_rel_x = target_x - center_x
        current_target_rel_y = target_y - center_y
        if Aimbot.prediction_enabled and target_vx_pps!= 0:
            prediction_pixel_offset_x = target_vx_pps * Aimbot.PREDICTION_LEAD_TIME_SECONDS
            current_target_rel_x += prediction_pixel_offset_x
        distance = math.hypot(current_target_rel_x, current_target_rel_y)
        norm_strength = Aimbot.ai_aim_strength / 100.0
        base_correction_factor = norm_strength * 2.0
        current_correction_factor_h = base_correction_factor
        current_correction_factor_v = base_correction_factor
        is_aiming_flag = self.is_targeted()
        sticky_lock_applied = False
        if is_aiming_flag:
            if distance < Aimbot.anti_lag_sticky_radius:
                sticky_pixel_move_x = current_target_rel_x * Aimbot.anti_lag_sticky_force
                sticky_pixel_move_y = current_target_rel_y * Aimbot.anti_lag_sticky_force
                eff_sens_x_num = Aimbot.target_game_sens * Aimbot.x_game_sens_multiplier * (Aimbot.mouse_dpi / Aimbot._REFERENCE_DPI)
                eff_sens_y_num = Aimbot.target_game_sens * Aimbot.y_game_sens_multiplier * (Aimbot.mouse_dpi / Aimbot._REFERENCE_DPI)
                sens_factor_x = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_x_num / max(Aimbot._MIN_EFFECTIVE_SENS, Aimbot._REFERENCE_GAME_SENS))
                sens_factor_y = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_y_num / max(Aimbot._MIN_EFFECTIVE_SENS, Aimbot._REFERENCE_GAME_SENS))
                final_sticky_input_dx = round(sticky_pixel_move_x / sens_factor_x) if sens_factor_x!= 0 else 0
                final_sticky_input_dy = round(sticky_pixel_move_y / sens_factor_y) if sens_factor_y!= 0 else 0
                if final_sticky_input_dx!= 0 or final_sticky_input_dy!= 0:
                    if Aimbot.input_method == 'Send Input':
                        mi_sticky = MouseInput(dx=int(final_sticky_input_dx), dy=int(final_sticky_input_dy), mouseData=0, dwFlags=1, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
                        inp_sticky = Input(type=0, ii=Input_I(mi=mi_sticky))
                        ctypes.windll.user32.SendInput(1, ctypes.byref(inp_sticky), ctypes.sizeof(inp_sticky))
                    else:
                        if Aimbot.input_method == 'Arduino' and self.ser and self.ser.is_open:
                            self._send_arduino_move(int(final_sticky_input_dx), int(final_sticky_input_dy))
                        else:
                            if Aimbot.input_method == 'DDXoft' and Aimbot.mouse_dll:
                                Aimbot.mouse_dll.DD_movR(int(final_sticky_input_dx), int(final_sticky_input_dy))
                sticky_lock_applied = True
            else:
                if distance > 0:
                    boost = Aimbot.anti_lag_strength_multiplier
                    current_correction_factor_h = boost
                    current_correction_factor_v = boost
        if not sticky_lock_applied:
            if not (is_aiming_flag and distance > 0):
                if distance < Aimbot.dynamic_close_range_threshold:
                    current_correction_factor_h = Aimbot.dynamic_close_range_speed_boost
                    current_correction_factor_v = Aimbot.dynamic_close_range_speed_boost
                else:
                    if distance > Aimbot.dynamic_far_range_threshold:
                        current_correction_factor_h = Aimbot.dynamic_far_range_speed_boost
                        current_correction_factor_v = Aimbot.dynamic_far_range_speed_boost
                if abs(current_target_rel_y) > Aimbot.dynamic_vertical_threshold:
                    current_correction_factor_v = Aimbot.dynamic_vertical_speed_boost
            desired_pixel_move_x = current_target_rel_x * current_correction_factor_h
            desired_pixel_move_y = current_target_rel_y * current_correction_factor_v
            if not is_aiming_flag:
                desired_pixel_move_x = Aimbot.sticky_strength
                desired_pixel_move_y = Aimbot.sticky_strength
            # Removed overly restrictive vertical stabilization that was preventing vertical aiming
            eff_sens_x_num = Aimbot.target_game_sens * Aimbot.x_game_sens_multiplier * (Aimbot.mouse_dpi / Aimbot._REFERENCE_DPI)
            eff_sens_y_num = Aimbot.target_game_sens * Aimbot.y_game_sens_multiplier * (Aimbot.mouse_dpi / Aimbot._REFERENCE_DPI)
            sens_factor_x = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_x_num / max(Aimbot._MIN_EFFECTIVE_SENS, Aimbot._REFERENCE_GAME_SENS))
            sens_factor_y = max(Aimbot._MIN_EFFECTIVE_SENS, eff_sens_y_num / max(Aimbot._MIN_EFFECTIVE_SENS, Aimbot._REFERENCE_GAME_SENS))
            final_input_dx_raw = desired_pixel_move_x / sens_factor_x if sens_factor_x!= 0 else 0
            final_input_dy_raw = desired_pixel_move_y / sens_factor_y if sens_factor_y!= 0 else 0
            final_input_dx = round(final_input_dx_raw)
            final_input_dy = round(final_input_dy_raw)
            if final_input_dx == 0 and final_input_dy == 0:
                return
            current_smoothing_steps = Aimbot.smoothing_steps
            current_smoothing_delay = Aimbot.smoothing_delay
            if Aimbot.adaptive_smoothing_enabled and target_velocity_pps > 0:
                if target_velocity_pps < Aimbot.adaptive_slow_threshold_pps:
                    current_smoothing_steps = int(Aimbot.smoothing_steps * Aimbot.adaptive_smoothing_factor_slow_steps)
                    current_smoothing_delay = Aimbot.smoothing_delay * Aimbot.adaptive_smoothing_factor_slow_delay
                else:
                    if target_velocity_pps > Aimbot.adaptive_fast_threshold_pps:
                        current_smoothing_steps = int(Aimbot.smoothing_steps * Aimbot.adaptive_smoothing_factor_fast_steps)
                        current_smoothing_delay = Aimbot.smoothing_delay * Aimbot.adaptive_smoothing_factor_fast_delay
            current_smoothing_steps = max(1, current_smoothing_steps)
            current_smoothing_delay = max(0.0, current_smoothing_delay)
            selected_curve_type = Aimbot.humanization_curve_selection
            if Aimbot.humanization_enabled and selected_curve_type == 'Random':
                selected_curve_type = random.choice(['Ease Out', 'Ease In', 'Linear'])
            num_steps = current_smoothing_steps
            total_moved_x = 0
            total_moved_y = 0
            for step in range(1, num_steps + 1):
                progress = step / num_steps
                if Aimbot.humanization_enabled:
                    if selected_curve_type == 'Ease Out':
                        eased_progress = 1 - pow(1 - progress, 3)
                    else:
                        if selected_curve_type == 'Ease In':
                            eased_progress = pow(progress, 3)
                        else:
                            eased_progress = progress
                else:
                    eased_progress = progress * (2 - progress)
                current_target_x_input = round(final_input_dx * eased_progress)
                current_target_y_input = round(final_input_dy * eased_progress)
                move_this_step_x_input = current_target_x_input - total_moved_x
                move_this_step_y_input = current_target_y_input - total_moved_y
                if Aimbot.humanization_enabled and Aimbot.humanization_jitter_strength > 0:
                    jitter_x = random.uniform(-Aimbot.humanization_jitter_strength, Aimbot.humanization_jitter_strength)
                    jitter_y = random.uniform(-Aimbot.humanization_jitter_strength, Aimbot.humanization_jitter_strength)
                    move_this_step_x_input += jitter_x
                    move_this_step_y_input += jitter_y
                if move_this_step_x_input!= 0 or move_this_step_y_input!= 0:
                    if Aimbot.input_method == 'Send Input':
                        mi_step = MouseInput(dx=int(move_this_step_x_input), dy=int(move_this_step_y_input), mouseData=0, dwFlags=1, time=0, dwExtraInfo=ctypes.pointer(Aimbot.extra))
                        inp_step = Input(type=0, ii=Input_I(mi=mi_step))
                        ctypes.windll.user32.SendInput(1, ctypes.byref(inp_step), ctypes.sizeof(inp_step))
                    else:
                        if Aimbot.input_method == 'Arduino':
                            if self.ser and self.ser.is_open:
                                self._send_arduino_move(int(move_this_step_x_input), int(move_this_step_y_input))
                        else:
                            if Aimbot.input_method == 'DDXoft':
                                if Aimbot.mouse_dll:
                                    Aimbot.mouse_dll.DD_movR(int(move_this_step_x_input), int(move_this_step_y_input))
                    total_moved_x += move_this_step_x_input
                    total_moved_y += move_this_step_y_input
                if num_steps > 1 and current_smoothing_delay > 0:
                    Aimbot.sleep(current_smoothing_delay)

    def start(self):
        if not self.yolo_model or not self.camera:
            print(colored(f'[ERROR] Aimbot detection model ({Aimbot.selected_model_file}) or camera not loaded. Cannot start detection thread.', 'red'))
            self._stop_requested = True
            return
        box_width = int(self.box_constant)
        box_height = int(self.box_constant)
        box_center_x = box_width // 2
        box_center_y = box_height // 2
        if not self.capture_region:
            print(colored('[ERROR] BetterCam capture_region not set before Aimbot.start()!', 'red'))
            self._stop_requested = True
            return
        capture_box_left_abs = self.capture_region[0]
        capture_box_top_abs = self.capture_region[1]
        data_dir = os.path.join('lib', 'data')
        collect_pause = 0
        if Aimbot.collect_data_enabled and (not os.path.exists(data_dir)):
            try:
                os.makedirs(data_dir)
            except OSError as e:
                print(colored(f'Failed to create data dir {e}.', 'red'))
                Aimbot.collect_data_enabled = False
        frame_count = 0
        fps_update_counter = 0
        self.was_aiming_last_frame = False
        while not self._stop_requested:
            loop_start_time = time.perf_counter()
            is_currently_aiming = self.is_targeted()
            frame_bgr = self.camera.get_latest_frame()
            if frame_bgr is None:
                Aimbot.sleep(0.001)
                continue
            try:
                processed_frame_for_yolo = frame_bgr
                if Aimbot.bloom_reducer_enabled and Aimbot.clahe:
                    lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    l_clahe = Aimbot.clahe.apply(l)
                    lab_clahe = cv2.merge((l_clahe, a, b))
                    processed_frame_for_yolo = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
                results = self.yolo_model(source=processed_frame_for_yolo, imgsz=640, conf=Aimbot.current_confidence, iou=Aimbot.current_iou, verbose=False)
                result = results[0]
                boxes = result.boxes
                best_target_info = None
                now_time = time.perf_counter()
                if boxes is not None and len(boxes) > 0:
                    xyxy_coords_all = boxes.xyxy.cpu().numpy()
                    x1_all, y1_all, x2_all, y2_all = (xyxy_coords_all[:, 0], xyxy_coords_all[:, 1], xyxy_coords_all[:, 2], xyxy_coords_all[:, 3])
                    relative_target_X_in_box_all = (x1_all + x2_all) / 2
                    heights_all = np.maximum(1, y2_all - y1_all)
                    y_offset_multiplier = 0.5
                    if Aimbot.target_body_part == 'Head':
                        y_offset_multiplier = 0.15
                    else:
                        if Aimbot.target_body_part == 'Neck':
                            y_offset_multiplier = 0.3
                    relative_target_Y_in_box_all = y1_all + heights_all * y_offset_multiplier
                    dx_in_box_all = relative_target_X_in_box_all - box_center_x
                    dy_in_box_all = relative_target_Y_in_box_all - box_center_y
                    crosshair_distances_all = np.hypot(dx_in_box_all, dy_in_box_all)
                    fov_mask = np.zeros_like(crosshair_distances_all, dtype=bool)
                    if Aimbot.fov_overlay_shape == 'Circle':
                        current_fov_to_use = Aimbot.ads_fov_radius if Aimbot.ads_fov_enabled and is_currently_aiming else Aimbot.fov_radius
                        fov_mask = crosshair_distances_all <= current_fov_to_use
                    else:
                        if Aimbot.fov_overlay_shape == 'Rectangle':
                            half_width = Aimbot.fov_rectangle_width / 2.0
                            half_height = Aimbot.fov_rectangle_height / 2.0
                            fov_mask = (np.abs(dx_in_box_all) <= half_width) & (np.abs(dy_in_box_all) <= half_height)
                    combined_mask = fov_mask
                    potential_target_indices_orig = np.where(combined_mask)[0]
                    if len(potential_target_indices_orig) > 0:
                        if Aimbot.max_detections_to_consider > 0 and len(potential_target_indices_orig) > Aimbot.max_detections_to_consider:
                            distances_of_potential_targets = crosshair_distances_all[potential_target_indices_orig]
                            sorted_indices_within_potential = np.argsort(distances_of_potential_targets)
                            top_n_indices_within_potential = sorted_indices_within_potential[:Aimbot.max_detections_to_consider]
                            final_candidate_indices_orig = potential_target_indices_orig[top_n_indices_within_potential]
                        else:
                            final_candidate_indices_orig = potential_target_indices_orig
                        if len(final_candidate_indices_orig) > 0:
                            distances_of_final_candidates = crosshair_distances_all[final_candidate_indices_orig]
                            closest_idx_within_final_candidates = np.argmin(distances_of_final_candidates)
                            best_original_index = final_candidate_indices_orig[closest_idx_within_final_candidates]
                            abs_x = relative_target_X_in_box_all[best_original_index] + capture_box_left_abs
                            abs_y = relative_target_Y_in_box_all[best_original_index] + capture_box_top_abs
                            target_id = self._get_target_id(abs_x, abs_y)
                            target_vx, target_vy = self._predict_target_velocities(target_id, abs_x, abs_y, now_time)
                            self._update_target_history(target_id, abs_x, abs_y, now_time)
                            best_target_info = {'absolute_X': abs_x, 'absolute_Y': abs_y, 'velocity_x_pps': target_vx, 'velocity_y_pps': target_vy}
                snap_occurred_this_frame = False
                final_target_x, final_target_y = (None, None)
                current_target_velocity_pps = 0
                if best_target_info:
                    final_target_x = best_target_info['absolute_X']
                    final_target_y = best_target_info['absolute_Y']
                    current_target_velocity_pps = math.hypot(best_target_info['velocity_x_pps'], best_target_info['velocity_y_pps'])
                can_aim_this_frame = Aimbot.aimbot_enabled_internal and is_currently_aiming and (not Aimbot.pickaxe_mode_active)
                if can_aim_this_frame and (not self.was_aiming_last_frame) and (final_target_x is not None):
                    if Aimbot.humanization_enabled:
                        base_delay_sec = Aimbot.humanization_reaction_delay_ms / 1000.0
                        random_offset_sec = random.uniform(-Aimbot.humanization_reaction_time_randomness_ms, Aimbot.humanization_reaction_time_randomness_ms) / 1000.0
                        total_delay = max(0, base_delay_sec + random_offset_sec)
                        Aimbot.sleep(total_delay)
                    self._perform_snap(final_target_x, final_target_y, best_target_info.get('velocity_x_pps', 0))
                    snap_occurred_this_frame = True
                else:
                    if can_aim_this_frame and final_target_x is not None and (not snap_occurred_this_frame):
                        self.move_crosshair(final_target_x, final_target_y, current_target_velocity_pps, best_target_info.get('velocity_x_pps', 0))
                self.was_aiming_last_frame = is_currently_aiming
                if Aimbot.collect_data_enabled and best_target_info and Aimbot.aimbot_enabled_internal and is_currently_aiming:
                    if collect_pause == 0:
                        collect_pause = 5
                    else:
                        collect_pause -= 1
            except Exception as e:
                print(colored(f'r[ERROR] Error during detectionprocessing {e}.', 'red'), end='')
                traceback.print_exc()
                Aimbot.sleep(0.1)
            processing_end_time = time.perf_counter()
            if Aimbot.fps_capper_enabled and Aimbot.target_fps_cap > 0:
                elapsed_processing_time = processing_end_time - loop_start_time
                target_frame_duration = 1.0 / Aimbot.target_fps_cap
                sleep_duration = target_frame_duration - elapsed_processing_time
                if sleep_duration > 0:
                    Aimbot.sleep(sleep_duration)
            loop_final_end_time = time.perf_counter()
            actual_loop_time = loop_final_end_time - loop_start_time
            frame_count += 1
            fps_update_counter += 1
            current_fps_estimate = (1.0 / actual_loop_time) if actual_loop_time > 0 else 0
            if fps_update_counter == 10:
                if main_gui_window:
                    main_gui_window.update_fps_signal.emit(int(current_fps_estimate))
                fps_update_counter = 0

    def request_stop(self):
        self._stop_requested = True
        if self.camera:
            try:
                self.camera.stop()
            except Exception as e:
                print(colored(f'[WARN] Error stopping BetterCam {e}.', 'yellow'))

    @staticmethod
    def clean_up():
        if volx_instance:
            volx_instance.request_stop()
        if listener:
            try:
                listener.stop()
            except Exception as e:
                print(f'[WARN] Error signaling keyboard listener stop {e}.')
        if volx_instance and volx_instance.ser and volx_instance.ser.is_open:
            with volx_instance.serial_lock:
                try:
                    volx_instance.ser.close()
                except Exception as e:
                    print(colored(f'[WARN] Error closing Arduino connection during cleanup {e}.', 'yellow'))
                volx_instance.ser = None
        if volx_instance and volx_instance.camera:
            try:
                volx_instance.camera.stop()
            except Exception as e:
                print(f'[WARN] Error during final BetterCam stop {e}.')
            volx_instance.camera = None
        if fov_overlay_instance:
            try:
                fov_overlay_instance.close()
            except Exception as e:
                print(colored(f'[WARN] Error closing FOV overlay {e}.', 'yellow'))
        if aimbot_thread and aimbot_thread.is_alive():
            aimbot_thread.join(timeout=3.0)
        if listener_thread and listener_thread.is_alive():
            listener_thread.join(timeout=1.0)
        if platform.system() == 'Windows':
            try:
                if 'pygame' in sys.modules and pygame.get_init():
                    pygame.quit()
            except Exception as e:
                print(colored(f'[WARN] Error quitting pygame {e}.', 'yellow'))
        if QApplication.instance():
            QApplication.instance().quit()

    def _get_target_id(self, x, y):
        return (int(x / 10), int(y / 10))

    def _update_target_history(self, target_id, x, y, t):
        self._target_history[target_id] = {'pos': (x, y), 'time': t}
        to_del = [tid for tid, data in self._target_history.items() if t - data['time'] > self._target_history_max_age]
        for tid in to_del:
            del self._target_history[tid]

    def _predict_target_velocities(self, target_id, x, y, t):
        prev = self._target_history.get(target_id)
        vx, vy = (0, 0)
        if prev:
            prev_x, prev_y = prev['pos']
            prev_t = prev['time']
            dt = t - prev_t
            if 0.001 < dt < 0.5:
                vx = (x - prev_x) / dt
                vy = (y - prev_y) / dt
            else:
                return (vx, vy)
        return (vx, vy)

    def toggle_collect_data(self, enabled):
        Aimbot.collect_data_enabled = enabled
        if main_gui_window:
            main_gui_window.update_collect_data_signal.emit(Aimbot.collect_data_enabled)

    def set_collect_data_output_res(self, res_str):
        Aimbot.collect_data_output_resolution_str = res_str.strip().lower()
        if not Aimbot.collect_data_output_resolution_str:
            Aimbot.collect_data_output_resolution_str = 'native'

    def toggle_collect_data_final_resize(self, enabled):
        Aimbot.collect_data_final_resize_enabled = enabled
        if main_gui_window:
            main_gui_window.update_collect_data_final_resize_signal.emit(Aimbot.collect_data_final_resize_enabled)

    def set_collect_data_final_resize_res(self, res_str):
        Aimbot.collect_data_final_resize_resolution_str = res_str.strip().lower()
        if not Aimbot.collect_data_final_resize_resolution_str:
            Aimbot.collect_data_final_resize_resolution_str = 'native'
custom_binds = [
    {'key': '', 'smoothing_delay': 0.002, 'ads_fov': 50.0, 'strength': 50.0, 'smoothing_steps': 8},
    {'key': '', 'smoothing_delay': 0.002, 'ads_fov': 50.0, 'strength': 50.0, 'smoothing_steps': 8},
    {'key': '', 'smoothing_delay': 0.002, 'ads_fov': 50.0, 'strength': 50.0, 'smoothing_steps': 8},
    {'key': '', 'smoothing_delay': 0.002, 'ads_fov': 50.0, 'strength': 50.0, 'smoothing_steps': 8},
]
pickaxe_bind_key = ''
STYLESHEET = '''
    QMainWindow, QWidget {
        background-color: #0A0A0A;
        color: #D3D3D3;
    }
    QFrame#NavPanel {
        background-color: #000000;
        border-bottom: 1px solid #36454F;
    }
    QPushButton {
        background-color: #191970;
        color: #FFFFFF;
        border: 1px solid #36454F;
        padding: 5px;
        min-height: 20px;
        font-weight: bold;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #4169E1;
    }
    QPushButton:disabled {
        background-color: #192a40;
        color: #A0A0A0;
    }
    QPushButton#NavPageButton {
        background-color: transparent;
        color: #D3D3D3;
        border: 1px solid #36454F;
        border-radius: 4px;
        font-weight: normal;
    }
    QPushButton#NavPageButton:hover {
        background-color: #252525;
        border-color: #4169E1;
    }
    QPushButton#NavPageButton:checked {
        background-color: #191970;
        color: #FFFFFF;
        border-color: #4169E1;
    }
    QLabel {
        color: #D3D3D3;
        padding: 2px;
    }
    QLabel:disabled {
        color: #808080;
    }
    QLabel#NavTitleLabel {
        color: #4169E1;
        font-size: 18px;
    }
    QCheckBox {
        spacing: 5px;
        color: #D3D3D3;
    }
    QCheckBox::indicator {
        width: 13px;
        height: 13px;
        border: 1px solid #36454F;
        border-radius: 3px;
    }
    QCheckBox::indicator:unchecked {
        background-color: #2F4F4F;
    }
    QCheckBox::indicator:checked {
        background-color: #0047AB;
    }
    QCheckBox:disabled {
        color: #808080;
    }
    QCheckBox::indicator:disabled {
        border-color: #2F4F4F;
        background-color: #202020;
    }
    QRadioButton {
        spacing: 5px;
        color: #D3D3D3;
    }
    QRadioButton::indicator {
        width: 13px;
        height: 13px;
        border: 1px solid #36454F;
        border-radius: 7px;
    }
    QRadioButton::indicator:unchecked {
        background-color: #2F4F4F;
    }
    QRadioButton::indicator:checked {
        background-color: #0047AB;
    }
    QRadioButton:disabled { 
        color: #808080; 
    }
    QRadioButton::indicator:disabled { 
        border-color: #2F4F4F; 
        background-color: #202020;
    }
    QLineEdit {
        background-color: #2A2A2A;
        border: 1px solid #36454F;
        padding: 3px;
        border-radius: 3px;
        color: #D3D3D3;
    }
    QLineEdit:disabled {
        background-color: #1E1E1E;
        color: #707070;
    }
                        QSlider::groove:horizontal {
                        border: 1px solid #4A5568;
                        height: 6px;
                        background: #2D3748;
                        margin: 2px 0;
                        border-radius: 3px;
                    }
                    QSlider::handle:horizontal {
                        background: #4A5568;
                        border: 1px solid #2D3748;
                        width: 12px;
                        height: 12px;
                        margin: -3px 0;
                        border-radius: 6px;
                    }
                    QSlider::handle:horizontal:hover {
                        background: #718096;
                        border-color: #4A5568;
                    }
                    QSlider::handle:horizontal:pressed {
                        background: #2D3748;
                        border-color: #1A202C;
                    }
                    QSlider::sub-page:horizontal {
                        background: #4A5568;
                        border: 1px solid #2D3748;
                        height: 6px;
                        border-radius: 3px;
                    }
    QScrollArea {
        border: none;
    }
    QScrollBar:vertical {
        border: 1px solid #000000;
        background: #1E1E1E;
        width: 12px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #191970;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #4169E1;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
         background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
         background: none;
    }
    QScrollBar:horizontal {
        border: 1px solid #000000;
        background: #1E1E1E;
        height: 12px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:horizontal {
        background: #191970;
        min-width: 20px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #4169E1;
    }
'''

class VolxPrimeGUI(QMainWindow):
    update_fps_signal = Signal(int)
    update_aimbot_status_signal = Signal(bool)
    update_controls_state_signal = Signal()
    update_humanization_signal = Signal(bool)
    update_ads_fov_signal = Signal(bool)
    update_bloom_reducer_signal = Signal(bool)
    update_fps_capper_signal = Signal(bool)
    update_collect_data_signal = Signal(bool)
    update_collect_data_final_resize_signal = Signal(bool)
    update_input_method_signal = Signal(str)
    show_critical_error_signal = Signal(str)
    save_result_signal = Signal(bool, str, str)
    toggle_visibility_signal = Signal()

    def __init__(self, aimbot_instance_ref):
        global overlay_control_signals  # inserted
        super().__init__()
        self.volx = aimbot_instance_ref
        self.fov_overlay = None
        self.fov_overlay_control_signals_obj = OverlayControlSignals()
        self.setWindowTitle(f'Volx {VERSION}')
        self.setFixedSize(420, 500)
        self.move(100, 100)
        self.setStyleSheet(STYLESHEET)
        self.init_ui()
        self.connect_signals()
        self.load_initial_gui_state()
        self.update_all_control_widgets_state_gui_slot()
        overlay_control_signals = self.fov_overlay_control_signals_obj
        if fov_overlay_available:
            self.fov_overlay = FOVOverlayWidget(self.volx, self.fov_overlay_control_signals_obj)
            self.fov_overlay_control_signals_obj.toggle_visibility_signal.connect(self.fov_overlay.set_visibility_slot)
            effective_visibility_fov = Aimbot.fov_overlay_enabled and (not getattr(Aimbot, 'pickaxe_mode_active', False))
            self.fov_overlay_control_signals_obj.toggle_visibility_signal.emit(effective_visibility_fov)
            if self.fov_overlay:
                self.fov_overlay_control_signals_obj.update_params_signal.emit()
        if Aimbot.ads_fov_enabled and self.volx:
            Aimbot.ads_fov_enabled = False
            self.volx.toggle_ads_fov()

    def connect_signals(self):
        self.update_fps_signal.connect(self.update_fps_label_slot)
        self.update_aimbot_status_signal.connect(self.update_aimbot_status_gui_slot)
        self.update_controls_state_signal.connect(self.update_all_control_widgets_state_gui_slot)
        self.update_humanization_signal.connect(self.update_humanization_gui_slot)
        self.update_ads_fov_signal.connect(self.update_ads_fov_gui_slot)
        self.update_bloom_reducer_signal.connect(self.update_bloom_reducer_gui_slot)
        self.update_fps_capper_signal.connect(self.update_fps_capper_gui_slot)
        self.update_collect_data_signal.connect(self.update_collect_data_gui_slot)
        self.update_collect_data_final_resize_signal.connect(self.update_collect_data_final_resize_gui_slot)
        self.update_input_method_signal.connect(self.update_input_method_gui_slot_internal)
        self.show_critical_error_signal.connect(self.show_critical_error_message_slot)
        self.save_result_signal.connect(self._save_worker_gui_callback)
        self.toggle_visibility_signal.connect(self.toggle_visibility_slot)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)
        nav_panel = QFrame()
        nav_panel.setObjectName('NavPanel')
        nav_panel.setFixedHeight(50)
        nav_layout = QHBoxLayout(nav_panel)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(8)
        nav_layout.addSpacing(10)
        self.stacked_widget = QStackedWidget()
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)
        self.page_buttons = []
        page_data = [('Main Settings', '⚙'), ('Keys & Sens', '⌨'), ('Core Config', '🔧'), ('Data Ops', '📁'), ('Custom Binds', '🔗'), ('Visuals', '👁')]
        self.pages = {}
        for i, (name, icon_char) in enumerate(page_data):
            page_widget = QWidget()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(page_widget)
            self.pages[name] = page_widget
            self.stacked_widget.addWidget(scroll_area)
            button = QPushButton(icon_char)
            button.setObjectName('NavPageButton')
            button.setCheckable(True)
            button.setToolTip(name)
            font = button.font()
            font.setPointSize(14)
            button.setFont(font)
            button.setFixedSize(QSize(45, 35))
            self.nav_button_group.addButton(button, i)
            nav_layout.addWidget(button)
            self.page_buttons.append(button)
        if self.page_buttons:
            self.page_buttons[0].setChecked(True)
        self.nav_button_group.idClicked.connect(self.stacked_widget.setCurrentIndex)
        nav_layout.addStretch(1)
        self.fps_label_widget = QLabel('FPS --')
        self.fps_label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.fps_label_widget)
        main_layout.addWidget(nav_panel)
        main_layout.addWidget(self.stacked_widget, 1)
        self._create_page1_main_settings(self.pages['Main Settings'])
        self._create_page2_keys_sens(self.pages['Keys & Sens'])
        self._create_page3_core_config(self.pages['Core Config'])
        self._create_page4_data_ops(self.pages['Data Ops'])
        self._create_page5_custom_binds(self.pages['Custom Binds'])
        self._create_page6_visuals(self.pages['Visuals'])
        self.stacked_widget.setCurrentIndex(0)

    def _create_label_slider_pair(self, parent_layout, label_text, min_val, max_val, initial_val, step, callback, is_float=False, float_decimals=1):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        label_widget = QLabel(label_text)
        slider = QSlider(Qt.Orientation.Horizontal)
        scale = (10 ** float_decimals) if is_float else 1
        slider.setMinimum(int(min_val * scale))
        slider.setMaximum(int(max_val * scale))
        slider.setValue(int(initial_val * scale))
        if step > 0:
            slider.setSingleStep(int(step * scale))
            slider.setPageStep(int(step * scale * 5))

        def slider_value_changed(value):
            actual_value = (value / scale) if is_float else value
            parts = label_text.split('(')
            base_label = parts[0].strip()
            suffix = ''
            if len(parts) > 1:
                suffix = ' (' + '('.join(parts[1:])
            if is_float:
                label_widget.setText(f'{base_label} {actual_value:.{float_decimals}f}{suffix}')
                callback(actual_value)
            else:
                label_widget.setText(f'{base_label} {int(actual_value)}{suffix}')
                callback(int(actual_value))
        slider.valueChanged.connect(slider_value_changed)
        parts = label_text.split('(')
        init_base_label = parts[0].strip()
        init_suffix = ''
        if len(parts) > 1:
            init_suffix = ' (' + '('.join(parts[1:])
        init_actual_val = initial_val
        if is_float:
            label_widget.setText(f'{init_base_label} {init_actual_val:.{float_decimals}f}{init_suffix}')
        else:
            label_widget.setText(f'{init_base_label} {int(init_actual_val)}{init_suffix}')
        layout.addWidget(label_widget, 1)
        layout.addWidget(slider, 2)
        parent_layout.addWidget(container)
        return (container, label_widget, slider)

    def _create_page1_main_settings(self, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        self.aimbot_checkbox = QCheckBox('AI Aimbot')
        self.aimbot_checkbox.stateChanged.connect(self.toggle_aimbot_gui_action)
        layout.addWidget(self.aimbot_checkbox)
        model_selection_box = QHBoxLayout()
        model_selection_label = QLabel('AI Model')
        model_selection_box.addWidget(model_selection_label)
        self.model_radio_group_widget = QWidget()
        model_radio_layout = QHBoxLayout(self.model_radio_group_widget)
        model_radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_model_fortnite = QRadioButton('Fortnite')
        self.radio_model_universal = QRadioButton('Universal')
        self.model_button_group = QButtonGroup(self)
        self.model_button_group.addButton(self.radio_model_fortnite)
        self.model_button_group.addButton(self.radio_model_universal)
        self.radio_model_fortnite.toggled.connect(lambda checked: self.update_selected_model_gui_action('fortnite.engine') if checked else None)
        self.radio_model_universal.toggled.connect(lambda checked: self.update_selected_model_gui_action('universal.engine') if checked else None)
        model_radio_layout.addWidget(self.radio_model_fortnite)
        model_radio_layout.addWidget(self.radio_model_universal)
        model_radio_layout.addStretch()
        model_selection_box.addWidget(self.model_radio_group_widget)
        model_selection_box.addStretch()
        layout.addLayout(model_selection_box)
        aim_key_layout = QHBoxLayout()
        aim_key_label = QLabel('Aim Activation Key')
        self.aim_key_entry = QLineEdit(Aimbot.aim_key_name)
        self.aim_key_entry.setFixedWidth(100)
        aim_key_layout.addWidget(aim_key_label)
        aim_key_layout.addWidget(self.aim_key_entry)
        aim_key_layout.addStretch()
        layout.addLayout(aim_key_layout)
        _, self.ai_aim_strength_label, self.ai_aim_strength_slider = self._create_label_slider_pair(layout, 'AI Aim Strength', 0.0, 100.0, Aimbot.ai_aim_strength, 1.0, lambda val: self.volx.set_ai_aim_strength(val) if self.volx else None, is_float=True, float_decimals=1)
        _, self.strength_label, self.strength_slider = self._create_label_slider_pair(layout, 'Detection Confidence (%)', 1, 100, int(Aimbot.current_confidence * 100), 1, lambda val: self.volx.set_strength(val) if self.volx else None)
        _, self.fov_label, self.fov_slider = self._create_label_slider_pair(layout, 'Circle Hipfire FOV Radius (px)', 10, 500, Aimbot.fov_radius, 10, lambda val: self.volx.set_fov(val) if self.volx else None)
        self.ads_fov_checkbox = QCheckBox('ADS FOV')
        self.ads_fov_checkbox.stateChanged.connect(self.toggle_ads_fov_gui_action)
        layout.addWidget(self.ads_fov_checkbox)
        _, self.ads_fov_label, self.ads_fov_slider = self._create_label_slider_pair(layout, 'Circle ADS FOV Radius (px)', 5, 250, Aimbot.ads_fov_radius, 5, lambda val: self.volx.set_ads_fov_radius(val) if self.volx else None)
        target_part_box = QHBoxLayout()
        target_part_label = QLabel('Aim Bone')
        target_part_box.addWidget(target_part_label)
        self.target_part_group_widget = QWidget()
        target_part_radio_layout = QHBoxLayout(self.target_part_group_widget)
        target_part_radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_head = QRadioButton('Head')
        self.radio_neck = QRadioButton('Neck')
        self.radio_body = QRadioButton('Body')
        self.radio_head.toggled.connect(lambda: self.update_target_part_gui_action('Head') if self.radio_head.isChecked() else None)
        self.radio_neck.toggled.connect(lambda: self.update_target_part_gui_action('Neck') if self.radio_neck.isChecked() else None)
        self.radio_body.toggled.connect(lambda: self.update_target_part_gui_action('Body') if self.radio_body.isChecked() else None)
        self.target_part_button_group = QButtonGroup(self)
        self.target_part_button_group.addButton(self.radio_head)
        self.target_part_button_group.addButton(self.radio_neck)
        self.target_part_button_group.addButton(self.radio_body)
        target_part_radio_layout.addWidget(self.radio_head)
        target_part_radio_layout.addWidget(self.radio_neck)
        target_part_radio_layout.addWidget(self.radio_body)
        target_part_radio_layout.addStretch()
        target_part_box.addWidget(self.target_part_group_widget)
        target_part_box.addStretch()
        layout.addLayout(target_part_box)
        _, self.max_detections_label, self.max_detections_slider = self._create_label_slider_pair(layout, 'Max Targets to Consider', 1, 5, Aimbot.max_detections_to_consider, 1, lambda val: self.volx.set_max_detections(val) if self.volx else None)
        self.bloom_reducer_checkbox = QCheckBox('Bloom Reducer')
        self.bloom_reducer_checkbox.stateChanged.connect(self.toggle_bloom_reducer_gui_action)
        layout.addWidget(self.bloom_reducer_checkbox)
        self.humanization_checkbox = QCheckBox('Humanization')
        self.humanization_checkbox.stateChanged.connect(self.toggle_humanization_gui_action)
        layout.addWidget(self.humanization_checkbox)
        self.humanization_options_widget = QWidget()
        humanization_layout = QVBoxLayout(self.humanization_options_widget)
        humanization_layout.setContentsMargins(10, 5, 5, 5)
        _, self.reaction_delay_label, self.reaction_delay_slider = self._create_label_slider_pair(humanization_layout, 'Reaction Delay (ms)', 0, 300, Aimbot.humanization_reaction_delay_ms, 10, lambda val: self.volx.set_humanization_reaction_delay(val) if self.volx else None)
        _, self.reaction_randomness_label, self.reaction_randomness_slider = self._create_label_slider_pair(humanization_layout, 'Reaction Randomness (ms)', 0, 150, Aimbot.humanization_reaction_time_randomness_ms, 10, lambda val: self.volx.set_humanization_reaction_randomness(val) if self.volx else None)
        _, self.jitter_strength_label, self.jitter_strength_slider = self._create_label_slider_pair(humanization_layout, 'Jitter Strength (px)', 0.0, 5.0, Aimbot.humanization_jitter_strength, 0.1, lambda val: self.volx.set_humanization_jitter_strength(val) if self.volx else None, is_float=True, float_decimals=1)
        curve_box = QHBoxLayout()
        curve_label = QLabel('Movement Curve')
        curve_box.addWidget(curve_label)
        self.curve_group_widget = QWidget()
        curve_radio_layout = QHBoxLayout(self.curve_group_widget)
        curve_radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_curve_random = QRadioButton('Random')
        self.radio_curve_ease_out = QRadioButton('Ease Out')
        self.radio_curve_ease_in = QRadioButton('Ease In')
        self.radio_curve_linear = QRadioButton('Linear')
        self.curve_button_group = QButtonGroup(self)
        self.curve_button_group.addButton(self.radio_curve_random)
        self.curve_button_group.addButton(self.radio_curve_ease_out)
        self.curve_button_group.addButton(self.radio_curve_ease_in)
        self.curve_button_group.addButton(self.radio_curve_linear)
        self.radio_curve_random.toggled.connect(lambda checked: self.volx.set_humanization_curve('Random') if checked and self.volx else None)
        self.radio_curve_ease_out.toggled.connect(lambda checked: self.volx.set_humanization_curve('Ease Out') if checked and self.volx else None)
        self.radio_curve_ease_in.toggled.connect(lambda checked: self.volx.set_humanization_curve('Ease In') if checked and self.volx else None)
        self.radio_curve_linear.toggled.connect(lambda checked: self.volx.set_humanization_curve('Linear') if checked and self.volx else None)
        curve_radio_layout.addWidget(self.radio_curve_random)
        curve_radio_layout.addWidget(self.radio_curve_ease_out)
        curve_radio_layout.addWidget(self.radio_curve_ease_in)
        curve_radio_layout.addWidget(self.radio_curve_linear)
        curve_radio_layout.addStretch()
        curve_box.addWidget(self.curve_group_widget)
        curve_box.addStretch()
        humanization_layout.addLayout(curve_box)
        layout.addWidget(self.humanization_options_widget)

    def _create_page2_keys_sens(self, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        input_method_box = QHBoxLayout()
        input_method_label = QLabel('Mouse Input Method')
        input_method_box.addWidget(input_method_label)
        self.input_method_group_widget = QWidget()
        input_method_radio_layout = QHBoxLayout(self.input_method_group_widget)
        input_method_radio_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_sendinput = QRadioButton('Send Input')
        self.radio_arduino = QRadioButton('Arduino')
        self.radio_ddxoft = QRadioButton('DDXoft')
        self.input_method_button_group = QButtonGroup(self)
        self.input_method_button_group.addButton(self.radio_sendinput)
        self.input_method_button_group.addButton(self.radio_arduino)
        self.input_method_button_group.addButton(self.radio_ddxoft)
        self.radio_sendinput.toggled.connect(lambda: self.update_input_method_gui_action('Send Input') if self.radio_sendinput.isChecked() else None)
        self.radio_arduino.toggled.connect(lambda: self._safe_arduino_connection() if self.radio_arduino.isChecked() else None)
        self.radio_ddxoft.toggled.connect(lambda: self.update_input_method_gui_action('DDXoft') if self.radio_ddxoft.isChecked() else None)
        input_method_radio_layout.addWidget(self.radio_sendinput)
        input_method_radio_layout.addWidget(self.radio_arduino)
        input_method_radio_layout.addWidget(self.radio_ddxoft)
        input_method_radio_layout.addStretch()
        input_method_box.addWidget(self.input_method_group_widget)
        input_method_box.addStretch()
        layout.addLayout(input_method_box)
        self.apply_keys_button = QPushButton('Apply Aim Activation Key (Live)')
        self.apply_keys_button.clicked.connect(self.apply_keybinds_gui_action)
        layout.addWidget(self.apply_keys_button, 0, Qt.AlignmentFlag.AlignCenter)
        sens_res_form_layout = QFormLayout()
        self.target_sens_entry = QLineEdit(f'{Aimbot.target_game_sens:.3f}')
        sens_res_form_layout.addRow('Target Game Sens', self.target_sens_entry)
        self.x_sens_mult_entry = QLineEdit(f'{Aimbot.x_game_sens_multiplier:.2f}')
        sens_res_form_layout.addRow('X Sens Multiplier', self.x_sens_mult_entry)
        self.y_sens_mult_entry = QLineEdit(f'{Aimbot.y_game_sens_multiplier:.2f}')
        sens_res_form_layout.addRow('Y Sens Multiplier', self.y_sens_mult_entry)
        self.dpi_entry = QLineEdit(str(Aimbot.mouse_dpi))
        sens_res_form_layout.addRow('Mouse DPI', self.dpi_entry)
        self.game_res_entry = QLineEdit(f'{Aimbot.game_resolution_width}x{Aimbot.game_resolution_height}')
        sens_res_form_layout.addRow('Game Resolution (WxH)', self.game_res_entry)
        layout.addLayout(sens_res_form_layout)
        self.hide_cmd_button = QPushButton('Hide Console Window' if platform.system() == 'Windows' else 'Hide Console (Win Only)')
        if platform.system()!= 'Windows':
            self.hide_cmd_button.setEnabled(False)
        self.hide_cmd_button.clicked.connect(self.hide_console_window_gui_action)
        layout.addWidget(self.hide_cmd_button)
        layout.addStretch(1)

    def _create_page3_core_config(self, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        layout.addWidget(QLabel('--- General Tracking ---'))
        _, self.sticky_strength_label_widget, self.sticky_strength_slider = self._create_label_slider_pair(layout, 'Sticky Strength (Tracking Feel)', 0.0, 1.0, Aimbot.sticky_strength, 0.05, lambda val: self.volx.set_sticky_strength(val) if self.volx else None, is_float=True, float_decimals=2)
        layout.addWidget(QLabel('--- Smoothing ---'))
        _, self.smoothing_steps_label_widget, self.smoothing_steps_slider = self._create_label_slider_pair(layout, 'Smoothing Steps', 1, 20, Aimbot.smoothing_steps, 1, lambda val: self.volx.set_smoothing_steps(val) if self.volx else None)
        _, self.smoothing_delay_label_widget, self.smoothing_delay_slider = self._create_label_slider_pair(layout, 'Smoothing Delay (s)', 0.0001, 0.01, Aimbot.smoothing_delay, 0.0005, lambda val: self.volx.set_smoothing_delay(val) if self.volx else None, is_float=True, float_decimals=4)
        layout.addWidget(QLabel('--- STICKY AIM Advanced Settings ---'))
        _, self.anti_lag_strength_label_widget, self.anti_lag_strength_slider = self._create_label_slider_pair(layout, 'Sticky PULL Strength (x)', 1.0, 5.0, Aimbot.anti_lag_strength_multiplier, 0.1, lambda val: self.volx.set_anti_lag_strength(val) if self.volx else None, is_float=True, float_decimals=1)
        _, self.anti_lag_sticky_radius_label_widget, self.anti_lag_sticky_radius_slider = self._create_label_slider_pair(layout, 'Sticky Lock Radius (px)', 1, 20, Aimbot.anti_lag_sticky_radius, 1, lambda val: self.volx.set_anti_lag_sticky_radius(val) if self.volx else None)
        self.fps_capper_checkbox = QCheckBox('Enable AI FPS Capper')
        self.fps_capper_checkbox.stateChanged.connect(self.toggle_fps_capper_gui_action)
        layout.addWidget(self.fps_capper_checkbox)
        _, self.target_fps_cap_label_widget, self.target_fps_cap_slider = self._create_label_slider_pair(layout, 'Target FPS Cap', 30, 1000, Aimbot.target_fps_cap, 10, lambda val: self.volx.set_target_fps_cap(val) if self.volx else None)
        hardware_form_layout = QFormLayout()
        self.arduino_port_entry = QLineEdit(Aimbot.arduino_port if Aimbot.arduino_port else '')
        self.arduino_port_entry.setPlaceholderText('e.g., COM3 or blank')
        hardware_form_layout.addRow('Arduino COM Port', self.arduino_port_entry)
        layout.addLayout(hardware_form_layout)
        self.save_settings_button = QPushButton('Save ALL Core Settings to Config')
        self.save_settings_button.clicked.connect(self.save_core_settings_gui_action)
        layout.addWidget(self.save_settings_button)
        layout.addStretch(1)

    def _create_page4_data_ops(self, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        layout.addWidget(QLabel('--- Data Collection Operations ---'))
        self.collect_data_checkbox = QCheckBox('Data Collection')
        self.collect_data_checkbox.stateChanged.connect(self.toggle_collect_data_gui_action)
        layout.addWidget(self.collect_data_checkbox)
        data_form = QFormLayout()
        self.collect_data_output_res_entry = QLineEdit(Aimbot.collect_data_output_resolution_str)
        self.collect_data_output_res_entry.editingFinished.connect(lambda: self.volx.set_collect_data_output_res(self.collect_data_output_res_entry.text()) if self.volx else None)
        data_form.addRow('Output Resolution (e.g., 640x640 or native)', self.collect_data_output_res_entry)
        self.collect_data_final_resize_checkbox = QCheckBox('Final ResizeStretch')
        self.collect_data_final_resize_checkbox.stateChanged.connect(self.toggle_collect_data_final_resize_gui_action)
        layout.addWidget(self.collect_data_final_resize_checkbox)
        self.collect_data_final_resize_res_entry = QLineEdit(Aimbot.collect_data_final_resize_resolution_str)
        self.collect_data_final_resize_res_entry.editingFinished.connect(lambda: self.volx.set_collect_data_final_resize_res(self.collect_data_final_resize_res_entry.text()) if self.volx else None)
        data_form.addRow('Final Resize Resolution (e.g., 224x224)', self.collect_data_final_resize_res_entry)
        layout.addLayout(data_form)
        save_path_label = QLabel(f"Data saved to {os.path.join('lib', 'data')}")
        save_path_label.setStyleSheet('font-style italic; color #A0A0A0;')
        layout.addWidget(save_path_label)
        layout.addStretch(1)

    def _create_page5_custom_binds(self, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(6)
        layout.addWidget(QLabel('--- Custom Profile Binds ---'))
        self.custom_bind_widgets = []
        for i in range(4):
            bind_group_box = QFrame()
            bind_group_box.setFrameShape(QFrame.Shape.StyledPanel)
            bind_layout = QFormLayout(bind_group_box)
            bind_label = QLabel(f'Bind Profile {i + 1}')
            font = bind_label.font()
            font.setBold(True)
            bind_label.setFont(font)
            bind_layout.addRow(bind_label)
            key_entry = QLineEdit(custom_binds[i]['key'])
            bind_layout.addRow('Hotkey', key_entry)
            _, smooth_delay_label_widget, smooth_delay_slider = self._create_label_slider_pair(bind_layout, 'Smoothing Delay', 0.0001, 0.01, custom_binds[i]['smoothing_delay'], 0.0001, lambda val, idx=i: self.update_custom_bind_value(idx, 'smoothing_delay', val), is_float=True, float_decimals=4)
            _, smooth_steps_label_widget, smooth_steps_slider = self._create_label_slider_pair(bind_layout, 'Smoothing Steps', 1, 20, custom_binds[i]['smoothing_steps'], 1, lambda val, idx=i: self.update_custom_bind_value(idx, 'smoothing_steps', val))
            _, ads_fov_label_widget, ads_fov_slider = self._create_label_slider_pair(bind_layout, 'ADS FOV', 5, 250, custom_binds[i]['ads_fov'], 5, lambda val, idx=i: self.update_custom_bind_value(idx, 'ads_fov', val))
            _, strength_label_widget, strength_slider = self._create_label_slider_pair(bind_layout, 'AI Strength', 0.0, 100.0, custom_binds[i]['strength'], 1.0, lambda val, idx=i: self.update_custom_bind_value(idx, 'strength', val), is_float=True, float_decimals=1)
            layout.addWidget(bind_group_box)
            self.custom_bind_widgets.append({'key': key_entry, 'smoothing_delay_slider': smooth_delay_slider, 'ads_fov_slider': ads_fov_slider, 'strength_slider': strength_slider, 'smoothing_steps_slider': smooth_steps_slider, 'smoothing_delay_label': smooth_delay_label_widget, 'smoothing_steps_label': smooth_steps_label_widget, 'ads_fov_label': ads_fov_label_widget, 'strength_label': strength_label_widget})
        pickaxe_form_layout = QFormLayout()
        self.pickaxe_key_entry = QLineEdit(pickaxe_bind_key)
        pickaxe_form_layout.addRow('Pickaxe Key (Disables Aim Temporarily)', self.pickaxe_key_entry)
        layout.addLayout(pickaxe_form_layout)
        self.save_custom_binds_button = QPushButton('Save Custom Binds & Pickaxe Key to Config')
        self.save_custom_binds_button.clicked.connect(self.save_custom_binds_gui_action)
        layout.addWidget(self.save_custom_binds_button)
        layout.addStretch(1)

    def _create_page6_visuals(self, page_widget):
        layout = QVBoxLayout(page_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        layout.addWidget(QLabel('--- Visual Enhancements ---'))
        fov_group_box = QFrame()
        fov_group_box.setFrameShape(QFrame.Shape.StyledPanel)
        fov_layout = QVBoxLayout(fov_group_box)
        fov_layout.addWidget(QLabel('FOV Overlay Settings'))
        self.fov_overlay_checkbox = QCheckBox('FOV Overlay')
        self.fov_overlay_checkbox.setChecked(Aimbot.fov_overlay_enabled)
        self.fov_overlay_checkbox.stateChanged.connect(self.toggle_fov_overlay_visibility_gui_action)
        if not fov_overlay_available:
            self.fov_overlay_checkbox.setText('Enable FOV Overlay (PySide6 ErrorMissing)')
            self.fov_overlay_checkbox.setEnabled(False)
        fov_layout.addWidget(self.fov_overlay_checkbox)
        if fov_overlay_available:
            fov_shape_box = QHBoxLayout()
            fov_shape_label = QLabel('FOV Shape')
            fov_shape_box.addWidget(fov_shape_label)
            self.fov_shape_group_widget = QWidget()
            fov_shape_radio_layout = QHBoxLayout(self.fov_shape_group_widget)
            fov_shape_radio_layout.setContentsMargins(0, 0, 0, 0)
            self.radio_circle = QRadioButton('Circle')
            self.radio_rectangle = QRadioButton('Rectangle')
            self.fov_shape_button_group = QButtonGroup(self)
            self.fov_shape_button_group.addButton(self.radio_circle)
            self.fov_shape_button_group.addButton(self.radio_rectangle)
            if Aimbot.fov_overlay_shape == 'Circle':
                self.radio_circle.setChecked(True)
            else:  # inserted
                self.radio_rectangle.setChecked(True)
            self.radio_circle.toggled.connect(lambda: self.update_fov_overlay_shape_gui_action('Circle') if self.radio_circle.isChecked() else None)
            self.radio_rectangle.toggled.connect(lambda: self.update_fov_overlay_shape_gui_action('Rectangle') if self.radio_rectangle.isChecked() else None)
            fov_shape_radio_layout.addWidget(self.radio_circle)
            fov_shape_radio_layout.addWidget(self.radio_rectangle)
            fov_shape_radio_layout.addStretch()
            fov_shape_box.addWidget(self.fov_shape_group_widget)
            fov_shape_box.addStretch()
            fov_layout.addLayout(fov_shape_box)
            self.rect_fov_width_container, self.rect_fov_width_label, self.rect_fov_width_slider = self._create_label_slider_pair(fov_layout, 'Rectangle FOV Width (px)', 10, 1000, Aimbot.fov_rectangle_width, 10, self.update_rect_fov_width_gui_action, is_float=True, float_decimals=1)
            self.rect_fov_height_container, self.rect_fov_height_label, self.rect_fov_height_slider = self._create_label_slider_pair(fov_layout, 'Rectangle FOV Height (px)', 10, 1000, Aimbot.fov_rectangle_height, 10, self.update_rect_fov_height_gui_action, is_float=True, float_decimals=1)
            self.rect_fov_corner_radius_container, self.rect_fov_corner_radius_label, self.rect_fov_corner_radius_slider = self._create_label_slider_pair(fov_layout, 'Rectangle Corner Radius (px)', 0, 100, Aimbot.fov_rectangle_corner_radius, 1, self.update_rect_fov_corner_radius_gui_action, is_float=True, float_decimals=1)
            self.fov_color_button = QPushButton('Change FOV Overlay Color')
            self.fov_color_button.clicked.connect(self.change_fov_overlay_color_gui_action)
            fov_layout.addWidget(self.fov_color_button)
        layout.addWidget(fov_group_box)
        layout.addStretch(1)

    def update_custom_bind_value(self, bind_index, key, value):
        if 0 <= bind_index < len(custom_binds):
            custom_binds[bind_index][key] = value

    def toggle_aimbot_gui_action(self, state):
        if self.volx:
            self.volx.update_status_aimbot()
        else:
            self.aimbot_checkbox.setChecked(False)

    def update_selected_model_gui_action(self, model_filename):
        if model_filename in ['fortnite.engine', 'universal.engine']:
            Aimbot.selected_model_file = model_filename
            QMessageBox.information(self, 'Model Selection Changed', f'AI Model set to {model_filename}.nnPlease save settings (on Core Config page) and RESTART the application for this change to take effect.')
        self.setFocus()

    def toggle_fov_overlay_visibility_gui_action(self, state_int):
        state = bool(state_int == Qt.CheckState.Checked.value)
        Aimbot.fov_overlay_enabled = state
        effective_visibility = Aimbot.fov_overlay_enabled and (not getattr(Aimbot, 'pickaxe_mode_active', False))
        if self.fov_overlay and fov_overlay_available:
            self.fov_overlay_control_signals_obj.toggle_visibility_signal.emit(effective_visibility)
        self.update_all_control_widgets_state_gui_slot()

    def update_fov_overlay_shape_gui_action(self, shape):
        Aimbot.fov_overlay_shape = shape
        if self.fov_overlay and fov_overlay_available and self.volx:
            self.fov_overlay_control_signals_obj.update_params_signal.emit()
        self.update_all_control_widgets_state_gui_slot()

    def update_rect_fov_width_gui_action(self, value):
        Aimbot.fov_rectangle_width = float(value)
        if self.fov_overlay_control_signals_obj:
            self.fov_overlay_control_signals_obj.update_params_signal.emit()

    def update_rect_fov_height_gui_action(self, value):
        Aimbot.fov_rectangle_height = float(value)
        if self.fov_overlay_control_signals_obj:
            self.fov_overlay_control_signals_obj.update_params_signal.emit()

    def update_rect_fov_corner_radius_gui_action(self, value):
        Aimbot.fov_rectangle_corner_radius = float(value)
        if self.fov_overlay_control_signals_obj:
            self.fov_overlay_control_signals_obj.update_params_signal.emit()

    def change_fov_overlay_color_gui_action(self):
        if not self.volx or not fov_overlay_available:
            QMessageBox.warning(self, 'Error', 'Cannot change color Aimbot or Overlay not available.')
            return
        r, g, b, a = Aimbot.fov_overlay_color_rgba
        initial_color = QColor(r, g, b, a)
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle('Select FOV Overlay Color')
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        color_dialog.setCurrentColor(initial_color)
        if color_dialog.exec():
            chosen_color = color_dialog.currentColor()
            if chosen_color.isValid():
                Aimbot.fov_overlay_color_rgba = (chosen_color.red(), chosen_color.green(), chosen_color.blue(), chosen_color.alpha())
                if self.fov_overlay_control_signals_obj:
                    self.fov_overlay_control_signals_obj.update_params_signal.emit()
        self.setFocus()

    def toggle_ads_fov_gui_action(self, qt_check_state_int):
        if self.volx:
            self.volx.toggle_ads_fov()

    def update_target_part_gui_action(self, part_name):
        if self.volx:
            self.volx.set_target_part(part_name)

    def toggle_humanization_gui_action(self, state_int):
        if self.volx:
            self.volx.toggle_humanization()

    def toggle_bloom_reducer_gui_action(self, state_int):
        if self.volx:
            self.volx.toggle_bloom_reducer()

    def _safe_arduino_connection(self):
        """Safely handle Arduino connection to prevent GUI freezing"""
        if not self.volx:
            return
        
        # Check if Arduino port is configured
        if not Aimbot.arduino_port:
            QMessageBox.warning(self, 'Arduino Setup Required', 
                              'Please configure the Arduino COM Port first in the Core Config tab before selecting Arduino input method.')
            # Reset the radio button to previous selection
            self.radio_arduino.setChecked(False)
            return
        
        # Show connection status
        self.radio_arduino.setText('Arduino (Connecting...)')
        self.radio_arduino.setEnabled(False)
        
        # Use threading to prevent GUI freeze
        def connect_arduino():
            try:
                self.volx.set_input_method('Arduino')
                # Update GUI on success
                self.radio_arduino.setText('Arduino')
                self.radio_arduino.setEnabled(True)
            except Exception as e:
                print(f"[ERROR] Arduino connection failed: {e}")
                # Fallback to Send Input on error
                self.volx.set_input_method('Send Input')
                # Reset GUI on failure
                self.radio_arduino.setText('Arduino')
                self.radio_arduino.setEnabled(True)
                self.radio_arduino.setChecked(False)
        
        # Start Arduino connection in background thread
        threading.Thread(target=connect_arduino, daemon=True).start()

    def update_input_method_gui_action(self, method):
        if self.volx:
            self.volx.set_input_method(method)

    def apply_keybinds_gui_action(self):
        if not self.volx:
            QMessageBox.critical(self, 'Error', 'Aimbot not initialized!')
            return
        new_aim_key = self.aim_key_entry.text().strip().lower()
        if not new_aim_key:
            QMessageBox.critical(self, 'Keybind Error', 'Aim Activation Key cannot be empty!')
            return
        new_aim_vk = get_vk_code(new_aim_key)
        if not new_aim_vk:
            QMessageBox.critical(self, 'Keybind Error', f"Invalid KBM Aim Key '{new_aim_key}'.")
            self.aim_key_entry.setText(Aimbot.aim_key_name)
            return
        Aimbot.aim_key_name = new_aim_key
        Aimbot.aim_key_vk = new_aim_vk
        QMessageBox.information(self, 'KBM Aim Key Updated', f'KBM Aim Activation Key set to {Aimbot.aim_key_name}n(Save on Core Config page for persistence)')
        self.setFocus()

    def hide_console_window_gui_action(self):
        if platform.system() == 'Windows':
            try:
                console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if console_hwnd!= 0:
                    ctypes.windll.user32.ShowWindow(console_hwnd, 0)
                    self.hide_cmd_button.setEnabled(False)
                    self.hide_cmd_button.setText('Console Hidden')
            except Exception as e:
                QMessageBox.critical(self, 'Hide Console Error', f'Failed to hide console {e}.')
        else:
            QMessageBox.warning(self, 'Platform Error', 'Hiding console is Windows-only.')

    def toggle_fps_capper_gui_action(self, state_int):
        if self.volx:
            self.volx.toggle_fps_capper()

    def toggle_collect_data_gui_action(self, state_int):
        if self.volx:
            self.volx.toggle_collect_data(bool(state_int == Qt.CheckState.Checked.value))

    def toggle_collect_data_final_resize_gui_action(self, state_int):
        if self.volx:
            self.volx.toggle_collect_data_final_resize(bool(state_int == Qt.CheckState.Checked.value))

    def save_core_settings_gui_action(self):
        if not self.volx:
            QMessageBox.critical(self, 'Save Error', 'Aimbot not initialized.')
            return
        Aimbot.arduino_port = self.arduino_port_entry.text().strip().upper()
        if not Aimbot.arduino_port:
            Aimbot.arduino_port = None
        try:
            Aimbot.target_game_sens = float(self.target_sens_entry.text())
            Aimbot.x_game_sens_multiplier = float(self.x_sens_mult_entry.text())
            Aimbot.y_game_sens_multiplier = float(self.y_sens_mult_entry.text())
            Aimbot.mouse_dpi = int(self.dpi_entry.text())
            res_str = self.game_res_entry.text().lower().strip()
            w_str, h_str = res_str.split('x')
            Aimbot.game_resolution_width = int(w_str)
            Aimbot.game_resolution_height = int(h_str)
            Aimbot.target_game_sens = max(Aimbot._MIN_EFFECTIVE_SENS, Aimbot.target_game_sens)
        except ValueError as e:
            QMessageBox.critical(self, 'Save Error', f'Invalid SensitivityDPIResolution input {e}nPlease use numbers.')
            return None
        current_gui_aim_key = self.aim_key_entry.text().strip().lower()
        vk_code_check = get_vk_code(current_gui_aim_key)
        if vk_code_check:
            Aimbot.aim_key_name = current_gui_aim_key
            Aimbot.aim_key_vk = vk_code_check
        else:
            QMessageBox.critical(self, 'Save Error', f"Invalid Aim Activation Key '{current_gui_aim_key}' for saving. Reverting to last valid or default.")
            self.aim_key_entry.setText(Aimbot.aim_key_name)
            return
        settings_to_save = {
            'selected_model_file': Aimbot.selected_model_file,
            'ai_aim_strength': Aimbot.ai_aim_strength,
            'target_game_sens': Aimbot.target_game_sens,
            'x_game_sens_multiplier': Aimbot.x_game_sens_multiplier,
            'y_game_sens_multiplier': Aimbot.y_game_sens_multiplier,
            'mouse_dpi': Aimbot.mouse_dpi,
            'game_resolution': f'{Aimbot.game_resolution_width}x{Aimbot.game_resolution_height}',
            'sticky_strength': Aimbot.sticky_strength,
            'fov_radius': Aimbot.fov_radius,
            'fov_overlay_enabled': Aimbot.fov_overlay_enabled,
            'fov_overlay_shape': Aimbot.fov_overlay_shape,
            'fov_overlay_color_rgba': Aimbot.fov_overlay_color_rgba,
            'fov_rectangle_width': Aimbot.fov_rectangle_width,
            'fov_rectangle_height': Aimbot.fov_rectangle_height,
            'fov_rectangle_corner_radius': Aimbot.fov_rectangle_corner_radius,
            'ads_fov_enabled': Aimbot.ads_fov_enabled,
            'ads_fov_radius': Aimbot.ads_fov_radius,
            'target_body_part': Aimbot.target_body_part,
            'humanization_enabled': Aimbot.humanization_enabled,
            'humanization_reaction_delay_ms': Aimbot.humanization_reaction_delay_ms,
            'humanization_reaction_time_randomness_ms': Aimbot.humanization_reaction_time_randomness_ms,
            'humanization_jitter_strength': Aimbot.humanization_jitter_strength,
            'humanization_curve_selection': Aimbot.humanization_curve_selection,
            'max_detections_to_consider': Aimbot.max_detections_to_consider,
        }
        original_text = self.save_settings_button.text()
        self.save_settings_button.setText('Saving Core Config...')
        self.save_settings_button.setEnabled(False)
        threading.Thread(target=self._save_worker_thread, args=(settings_to_save, CONFIG_PATH, 'core'), daemon=True).start()

    def save_custom_binds_gui_action(self):
        global pickaxe_bind_key  # inserted
        if not self.volx:
            QMessageBox.critical(self, 'Save Error', 'Aimbot not initialized.')
            return
        for i, bind_widgets_dict in enumerate(self.custom_bind_widgets):
            custom_binds[i]['key'] = bind_widgets_dict['key'].text().strip().lower()
        pickaxe_bind_key = self.pickaxe_key_entry.text().strip().lower()
        config_data_to_save = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config_data_to_save = json.load(f)
            except Exception as e:
                QMessageBox.warning(self, 'Config Read Warning', f'Could not load existing config to merge binds {e}. Saving binds only.')
                config_data_to_save = {}
        config_data_to_save['custom_binds'] = custom_binds
        config_data_to_save['pickaxe_bind_key'] = pickaxe_bind_key
        original_text = self.save_custom_binds_button.text()
        self.save_custom_binds_button.setText('Saving Binds...')
        self.save_custom_binds_button.setEnabled(False)
        threading.Thread(target=self._save_worker_thread, args=(config_data_to_save, CONFIG_PATH, 'binds'), daemon=True).start()

    def _save_worker_thread(self, settings_dict, path, save_type='core'):
        success, message = _write_config_json(settings_dict, path)
        self.save_result_signal.emit(success, message, save_type)

    @Slot(bool, str, str)
    def _save_worker_gui_callback(self, success, message, save_type):
        button_to_reset = None
        info_message = ''
        if save_type == 'core':
            button_to_reset = self.save_settings_button
            info_message = 'ALL core settings saved successfully to config.json.'
            if success and Aimbot.input_method == 'Arduino' and Aimbot.arduino_port and self.volx:
                self.volx.set_input_method('Arduino')
        else:
            if save_type == 'binds':
                button_to_reset = self.save_custom_binds_button
                info_message = 'Custom binds & pickaxe key saved to config.json!'
        if button_to_reset:
            original_text_map = {'core': 'Save ALL Core Settings to Config', 'binds': 'Save Custom Binds & Pickaxe Key to Config'}
            button_to_reset.setText(original_text_map.get(save_type, 'Save'))
            button_to_reset.setEnabled(True)
        if success:
            QMessageBox.information(self, 'Settings Saved', info_message)
        else:
            QMessageBox.critical(self, 'Save Error', message)
        self.setFocus()

    @Slot(int)
    def update_fps_label_slot(self, fps):
        self.fps_label_widget.setText(f'FPS {fps}')

    @Slot(bool)
    def update_aimbot_status_gui_slot(self, is_enabled):
        was_blocked = self.aimbot_checkbox.signalsBlocked()
        self.aimbot_checkbox.blockSignals(True)
        self.aimbot_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.aimbot_checkbox.blockSignals(False)
        self.update_all_control_widgets_state_gui_slot()

    @Slot()
    def update_all_control_widgets_state_gui_slot(self):
        aimbot_on = Aimbot.aimbot_enabled_internal
        self.model_radio_group_widget.setEnabled(True)
        self.aim_key_entry.setEnabled(True)
        self.ai_aim_strength_slider.setEnabled(aimbot_on)
        self.strength_slider.setEnabled(aimbot_on)
        self.fov_slider.setEnabled(aimbot_on)
        self.ads_fov_checkbox.setEnabled(aimbot_on)
        self.ads_fov_slider.setEnabled(aimbot_on and Aimbot.ads_fov_enabled)
        self.max_detections_slider.setEnabled(aimbot_on)
        self.bloom_reducer_checkbox.setEnabled(aimbot_on)
        self.target_part_group_widget.setEnabled(aimbot_on)
        self.humanization_checkbox.setEnabled(aimbot_on)
        humanization_options_enabled = aimbot_on and Aimbot.humanization_enabled
        self.humanization_options_widget.setEnabled(humanization_options_enabled)
        self.input_method_group_widget.setEnabled(True)
        self.radio_ddxoft.setEnabled(platform.system() == 'Windows')
        self.apply_keys_button.setEnabled(True)
        self.target_sens_entry.setEnabled(True)
        self.x_sens_mult_entry.setEnabled(True)
        self.y_sens_mult_entry.setEnabled(True)
        self.dpi_entry.setEnabled(True)
        self.game_res_entry.setEnabled(True)
        self.sticky_strength_slider.setEnabled(aimbot_on)
        self.smoothing_steps_slider.setEnabled(aimbot_on)
        self.smoothing_delay_slider.setEnabled(aimbot_on)
        self.anti_lag_strength_slider.setEnabled(aimbot_on)
        self.anti_lag_sticky_radius_slider.setEnabled(aimbot_on)
        self.fps_capper_checkbox.setEnabled(aimbot_on)
        fps_capper_widgets_enabled = aimbot_on and Aimbot.fps_capper_enabled
        self.target_fps_cap_slider.setEnabled(fps_capper_widgets_enabled)
        self.target_fps_cap_label_widget.setEnabled(fps_capper_widgets_enabled)
        self.arduino_port_entry.setEnabled(True)
        self.save_settings_button.setEnabled(True)
        self.collect_data_checkbox.setEnabled(True)
        self.collect_data_output_res_entry.setEnabled(Aimbot.collect_data_enabled)
        self.collect_data_final_resize_checkbox.setEnabled(Aimbot.collect_data_enabled)
        self.collect_data_final_resize_res_entry.setEnabled(Aimbot.collect_data_enabled and Aimbot.collect_data_final_resize_enabled)
        for bind_widget_set in self.custom_bind_widgets:
            for widget_key, widget in bind_widget_set.items():
                if hasattr(widget, 'setEnabled'):
                    widget.setEnabled(True)
        self.pickaxe_key_entry.setEnabled(True)
        self.save_custom_binds_button.setEnabled(True)
        is_pickaxe_active = getattr(Aimbot, 'pickaxe_mode_active', False)
        can_enable_visuals = fov_overlay_available and (not is_pickaxe_active)
        self.fov_overlay_checkbox.setEnabled(can_enable_visuals)
        fov_overlay_specific_controls_enabled = can_enable_visuals and Aimbot.fov_overlay_enabled
        if hasattr(self, 'fov_shape_group_widget'):
            self.fov_shape_group_widget.setEnabled(fov_overlay_specific_controls_enabled)
        if hasattr(self, 'fov_color_button'):
            self.fov_color_button.setEnabled(fov_overlay_specific_controls_enabled)
        is_rect_shape_fov = Aimbot.fov_overlay_shape == 'Rectangle'
        rect_fov_sliders_enabled = fov_overlay_specific_controls_enabled and is_rect_shape_fov
        if hasattr(self, 'rect_fov_width_container'):
            self.rect_fov_width_container.setEnabled(rect_fov_sliders_enabled)
        if hasattr(self, 'rect_fov_height_container'):
            self.rect_fov_height_container.setEnabled(rect_fov_sliders_enabled)
        if hasattr(self, 'rect_fov_corner_radius_container'):
            self.rect_fov_corner_radius_container.setEnabled(rect_fov_sliders_enabled)

    @Slot(bool)
    def update_humanization_gui_slot(self, is_enabled):
        was_blocked = self.humanization_checkbox.signalsBlocked()
        self.humanization_checkbox.blockSignals(True)
        self.humanization_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.humanization_checkbox.blockSignals(False)
        self.update_all_control_widgets_state_gui_slot()

    @Slot(bool)
    def update_ads_fov_gui_slot(self, is_enabled):
        was_blocked = self.ads_fov_checkbox.signalsBlocked()
        self.ads_fov_checkbox.blockSignals(True)
        self.ads_fov_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.ads_fov_checkbox.blockSignals(False)
        self.update_all_control_widgets_state_gui_slot()

    @Slot(bool)
    def update_bloom_reducer_gui_slot(self, is_enabled):
        was_blocked = self.bloom_reducer_checkbox.signalsBlocked()
        self.bloom_reducer_checkbox.blockSignals(True)
        self.bloom_reducer_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.bloom_reducer_checkbox.blockSignals(False)

    @Slot(bool)
    def update_fps_capper_gui_slot(self, is_enabled):
        was_blocked = self.fps_capper_checkbox.signalsBlocked()
        self.fps_capper_checkbox.blockSignals(True)
        self.fps_capper_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.fps_capper_checkbox.blockSignals(False)
        self.update_all_control_widgets_state_gui_slot()

    @Slot(bool)
    def update_collect_data_gui_slot(self, is_enabled):
        was_blocked = self.collect_data_checkbox.signalsBlocked()
        self.collect_data_checkbox.blockSignals(True)
        self.collect_data_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.collect_data_checkbox.blockSignals(False)
        self.update_all_control_widgets_state_gui_slot()

    @Slot(bool)
    def update_collect_data_final_resize_gui_slot(self, is_enabled):
        was_blocked = self.collect_data_final_resize_checkbox.signalsBlocked()
        self.collect_data_final_resize_checkbox.blockSignals(True)
        self.collect_data_final_resize_checkbox.setChecked(is_enabled)
        if not was_blocked:
            self.collect_data_final_resize_checkbox.blockSignals(False)
        self.update_all_control_widgets_state_gui_slot()

    @Slot(str)
    def update_input_method_gui_slot_internal(self, method_name):
        radios_exist = all((hasattr(self, radio_attr) for radio_attr in ['radio_sendinput', 'radio_arduino', 'radio_ddxoft']))
        if not radios_exist:
            return
        radios = [self.radio_sendinput, self.radio_arduino, self.radio_ddxoft]
        for r in radios:
            r.blockSignals(True)
        if method_name == 'Send Input':
            self.radio_sendinput.setChecked(True)
        else:
            if method_name == 'Arduino':
                self.radio_arduino.setChecked(True)
            else:
                if method_name == 'DDXoft':
                    self.radio_ddxoft.setChecked(True)
                else:
                    self.radio_sendinput.setChecked(True)
        for r in radios:
            r.blockSignals(False)

    @Slot(str)
    def show_critical_error_message_slot(self, message):
        QMessageBox.critical(self, 'Volx Critical Error', message)

    @Slot()
    def load_initial_gui_state(self):
        self.radio_model_fortnite.blockSignals(True)
        self.radio_model_universal.blockSignals(True)
        if Aimbot.selected_model_file == 'fortnite.engine':
            self.radio_model_fortnite.setChecked(True)
        else:
            self.radio_model_universal.setChecked(True)
        self.radio_model_fortnite.blockSignals(False)
        self.radio_model_universal.blockSignals(False)
        self.radio_head.blockSignals(True)
        self.radio_neck.blockSignals(True)
        self.radio_body.blockSignals(True)
        if Aimbot.target_body_part == 'Head':
            self.radio_head.setChecked(True)
        else:
            if Aimbot.target_body_part == 'Neck':
                self.radio_neck.setChecked(True)
            else:
                self.radio_body.setChecked(True)
        self.radio_head.blockSignals(False)
        self.radio_neck.blockSignals(False)
        self.radio_body.blockSignals(False)
        if hasattr(self, 'radio_sendinput'):
            self.radio_sendinput.blockSignals(True)
            self.radio_arduino.blockSignals(True)
            self.radio_ddxoft.blockSignals(True)
            if Aimbot.input_method == 'Send Input':
                self.radio_sendinput.setChecked(True)
            else:
                if Aimbot.input_method == 'Arduino':
                    self.radio_arduino.setChecked(True)
                else:
                    if Aimbot.input_method == 'DDXoft':
                        self.radio_ddxoft.setChecked(True)
            self.radio_sendinput.blockSignals(False)
            self.radio_arduino.blockSignals(False)
            self.radio_ddxoft.blockSignals(False)
        if hasattr(self, 'radio_circle'):
            self.radio_circle.blockSignals(True)
            self.radio_rectangle.blockSignals(True)
            if Aimbot.fov_overlay_shape == 'Circle':
                self.radio_circle.setChecked(True)
            else:
                self.radio_rectangle.setChecked(True)
            self.radio_circle.blockSignals(False)
            self.radio_rectangle.blockSignals(False)
        if hasattr(self, 'radio_curve_random'):
            radios = [self.radio_curve_random, self.radio_curve_ease_out, self.radio_curve_ease_in, self.radio_curve_linear]
            for r in radios:
                r.blockSignals(True)
            if Aimbot.humanization_curve_selection == 'Random':
                self.radio_curve_random.setChecked(True)
            else:
                if Aimbot.humanization_curve_selection == 'Ease Out':
                    self.radio_curve_ease_out.setChecked(True)
                else:
                    if Aimbot.humanization_curve_selection == 'Ease In':
                        self.radio_curve_ease_in.setChecked(True)
                    else:
                        if Aimbot.humanization_curve_selection == 'Linear':
                            self.radio_curve_linear.setChecked(True)
            for r in radios:
                r.blockSignals(False)
        self.aimbot_checkbox.setChecked(Aimbot.aimbot_enabled_internal)
        self.ads_fov_checkbox.setChecked(Aimbot.ads_fov_enabled)
        self.humanization_checkbox.setChecked(Aimbot.humanization_enabled)
        self.bloom_reducer_checkbox.setChecked(Aimbot.bloom_reducer_enabled)
        self.fps_capper_checkbox.setChecked(Aimbot.fps_capper_enabled)
        self.collect_data_checkbox.setChecked(Aimbot.collect_data_enabled)
        self.collect_data_final_resize_checkbox.setChecked(Aimbot.collect_data_final_resize_enabled)
        if hasattr(self, 'fov_overlay_checkbox'):
            self.fov_overlay_checkbox.setChecked(Aimbot.fov_overlay_enabled)
        self.ai_aim_strength_slider.setValue(int(Aimbot.ai_aim_strength * 10))
        self.strength_slider.setValue(int(Aimbot.current_confidence * 100))
        self.fov_slider.setValue(int(Aimbot.fov_radius))
        self.ads_fov_slider.setValue(int(Aimbot.ads_fov_radius))
        self.max_detections_slider.setValue(Aimbot.max_detections_to_consider)
        self.sticky_strength_slider.setValue(int(Aimbot.sticky_strength * 100))
        self.smoothing_steps_slider.setValue(Aimbot.smoothing_steps)
        self.smoothing_delay_slider.setValue(int(Aimbot.smoothing_delay * 10000))
        self.anti_lag_strength_slider.setValue(int(Aimbot.anti_lag_strength_multiplier * 10))
        self.anti_lag_sticky_radius_slider.setValue(Aimbot.anti_lag_sticky_radius)
        self.target_fps_cap_slider.setValue(Aimbot.target_fps_cap)
        if hasattr(self, 'rect_fov_width_slider'):
            self.rect_fov_width_slider.setValue(int(Aimbot.fov_rectangle_width * 10))
        if hasattr(self, 'rect_fov_height_slider'):
            self.rect_fov_height_slider.setValue(int(Aimbot.fov_rectangle_height * 10))
        if hasattr(self, 'rect_fov_corner_radius_slider'):
            self.rect_fov_corner_radius_slider.setValue(int(Aimbot.fov_rectangle_corner_radius * 10))
        if hasattr(self, 'reaction_delay_slider'):
            self.reaction_delay_slider.setValue(int(Aimbot.humanization_reaction_delay_ms))
        if hasattr(self, 'reaction_randomness_slider'):
            self.reaction_randomness_slider.setValue(int(Aimbot.humanization_reaction_time_randomness_ms))
        if hasattr(self, 'jitter_strength_slider'):
            self.jitter_strength_slider.setValue(int(Aimbot.humanization_jitter_strength * 10))
        self.aim_key_entry.setText(Aimbot.aim_key_name)
        self.target_sens_entry.setText(f'{Aimbot.target_game_sens:.3f}')
        self.x_sens_mult_entry.setText(f'{Aimbot.x_game_sens_multiplier:.2f}')
        self.y_sens_mult_entry.setText(f'{Aimbot.y_game_sens_multiplier:.2f}')
        self.dpi_entry.setText(str(Aimbot.mouse_dpi))
        self.game_res_entry.setText(f'{Aimbot.game_resolution_width}x{Aimbot.game_resolution_height}')
        self.arduino_port_entry.setText(Aimbot.arduino_port if Aimbot.arduino_port else '')
        self.collect_data_output_res_entry.setText(Aimbot.collect_data_output_resolution_str)
        self.collect_data_final_resize_res_entry.setText(Aimbot.collect_data_final_resize_resolution_str)
        for i, bind_widgets_dict in enumerate(self.custom_bind_widgets):
            bind_widgets_dict['key'].setText(custom_binds[i]['key'])
            bind_widgets_dict['smoothing_delay_slider'].setValue(int(custom_binds[i]['smoothing_delay'] * 10000))
            bind_widgets_dict['smoothing_steps_slider'].setValue(custom_binds[i]['smoothing_steps'])
            bind_widgets_dict['ads_fov_slider'].setValue(int(custom_binds[i]['ads_fov']))
            bind_widgets_dict['strength_slider'].setValue(int(custom_binds[i]['strength'] * 10))
        self.pickaxe_key_entry.setText(pickaxe_bind_key)

    def quit_application_gui(self):
        if self.volx:
            Aimbot.clean_up()
        else:
            if QApplication.instance():
                QApplication.instance().quit()

    def closeEvent(self, event):
        self.quit_application_gui()
        event.accept()

    @Slot()
    def toggle_visibility_slot(self):
        global gui_visible  # inserted
        if self.isVisible():
            self.hide()
            gui_visible = False
        else:
            self.show()
            self.activateWindow()
            self.raise_()

def on_press(key):
    try:
        if key == keyboard.Key.insert and main_gui_window:
            main_gui_window.toggle_visibility_signal.emit()
    except RuntimeError as e:
        traceback.print_exc()
    except Exception as e:
        traceback.print_exc()

def on_release(key):
    try:
        key_name = None
        if hasattr(key, 'vk') and key.vk is not None:
            key_name = get_key_name(key.vk)
        else:  # inserted
            if hasattr(key, 'name'):
                key_name = key.name
            else:  # inserted
                if hasattr(key, 'char') and key.char:
                    key_name = key.char
        if key_name:
            key_name_lower = str(key_name).lower()
            for i, bind_data in enumerate(custom_binds):
                bind_key_config = bind_data['key'].strip().lower()
                if key_name_lower == bind_key_config and bind_key_config:
                    if not getattr(Aimbot, 'pickaxe_mode_active', False):
                        Aimbot.smoothing_delay = bind_data['smoothing_delay']
                        Aimbot.ads_fov_radius = bind_data['ads_fov']
                        Aimbot.ai_aim_strength = bind_data['strength']
                        Aimbot.smoothing_steps = bind_data['smoothing_steps']
                        if main_gui_window:
                            main_gui_window.load_initial_gui_state()
                            main_gui_window.update_all_control_widgets_state_gui_slot()
                        if overlay_control_signals:
                            overlay_control_signals.update_params_signal.emit()
                    break
            _pk_key_lower = pickaxe_bind_key.strip().lower()
            if key_name_lower == _pk_key_lower and _pk_key_lower:
                Aimbot.pickaxe_mode_active = not Aimbot.pickaxe_mode_active
                if overlay_control_signals and main_gui_window and main_gui_window.fov_overlay:
                    effective_visibility_fov = Aimbot.fov_overlay_enabled and (not Aimbot.pickaxe_mode_active)
                    main_gui_window.fov_overlay_control_signals_obj.toggle_visibility_signal.emit(effective_visibility_fov)
                if Aimbot.pickaxe_mode_active and volx_instance:
                    volx_instance.was_aiming_last_frame = False
                if main_gui_window and gui_visible:
                    main_gui_window.update_controls_state_signal.emit()
    except RuntimeError as e:
        print(colored(f'RUNTIME ERROR in on_release {e}.', 'red'))
        traceback.print_exc()
    except Exception as e:
        print(colored(f'UNEXPECTED ERROR in on_release {e}.', 'red'))
        traceback.print_exc()

def start_listener():
    global listener  # inserted
    try:
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
    except Exception as e:
        print(colored(f'[ERROR] Keyboard listener thread failed to start {e}.', 'red'))
        traceback.print_exc()

def _write_config_json(settings_dict, path):
    try:
        config_dir = os.path.dirname(path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        current_config = {}
        if os.path.exists(path):
            try:
                with open(path, 'r') as f_read:
                    current_config = json.load(f_read)
            except json.JSONDecodeError:
                print(colored(f"[WARN] Existing config '{path}' corrupted. Overwriting with new settings.", 'yellow'))
                current_config = {}
        merged_config = {**current_config, **settings_dict}
        if 'custom_binds' not in settings_dict:
            merged_config['custom_binds'] = custom_binds
        if 'pickaxe_bind_key' not in settings_dict:
            merged_config['pickaxe_bind_key'] = pickaxe_bind_key
        with open(path, 'w') as outfile:
            json.dump(merged_config, outfile, indent=4)
        return (True, f"[SUCCESS] Configuration saved to {path}!")
    except Exception as e:
        error_msg = f'[ERROR] Could not writeprepare config {e}. Check disk space or permissions.'
        print(colored(error_msg, 'red'))
        traceback.print_exc()
        return (False, f'Error saving confign{e}.')

def _sendinput_mouse_move(dx, dy):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(dx, dy, 0, 1, 0, ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(0), ii_)
    if platform.system() == 'Windows':
        ctypes.windll.user32.SendInput(1, ctypes.byref(command), ctypes.sizeof(command))

def _sendinput_mouse_click():
    extra = ctypes.c_ulong(0)
    ii_down = Input_I()
    ii_up = Input_I()
    ii_down.mi = MouseInput(0, 0, 0, 2, 0, ctypes.pointer(extra))
    command_down = Input(ctypes.c_ulong(0), ii_down)
    ii_up.mi = MouseInput(0, 0, 0, 4, 0, ctypes.pointer(extra))
    command_up = Input(ctypes.c_ulong(0), ii_up)
    if platform.system() == 'Windows':
        ctypes.windll.user32.SendInput(1, ctypes.byref(command_down), ctypes.sizeof(command_down))
        time.sleep(random.uniform(0.015, 0.045))
        ctypes.windll.user32.SendInput(1, ctypes.byref(command_up), ctypes.sizeof(command_up))

def human_like_mouse_move(dx, dy, total_time=None):
    steps = max(8, int(np.hypot(dx, dy) / 5))
    if total_time is None:
        total_time = random.uniform(0.04, 0.12) + 0.001 * abs(dx + dy)
    step_time = total_time / steps
    x, y = (0, 0)
    for i in range(steps):
        remain_x = dx - x
        remain_y = dy - y
        if i == steps - 1:
            move_x, move_y = (remain_x, remain_y)
        else:
            move_x = int(round(remain_x / (steps - i) + random.uniform(-1, 1)))
            move_y = int(round(remain_y / (steps - i) + random.uniform(-1, 1)))
        _sendinput_mouse_move(move_x, move_y)
        x += move_x
        y += move_y
        time.sleep(random.uniform(step_time * 0.7, step_time * 1.3))

def human_like_left_click():
    if random.random() < 0.1:
        _sendinput_mouse_move(random.randint(-2, 2), random.randint(-2, 2))
        time.sleep(random.uniform(0.005, 0.02))
    _sendinput_mouse_click()
    if random.random() < 0.1:
        _sendinput_mouse_move(random.randint(-2, 2), random.randint(-2, 2))
        time.sleep(random.uniform(0.005, 0.02))

def human_like_key_press(vk_code):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii2_ = Input_I()
    ii_.ki = KeyBdInput(vk_code, 0, 0, 0, ctypes.pointer(extra))
    command_down = Input(ctypes.c_ulong(1), ii_)
    ii2_.ki = KeyBdInput(vk_code, 0, 2, 0, ctypes.pointer(extra))
    command_up = Input(ctypes.c_ulong(1), ii2_)
    if platform.system() == 'Windows':
        ctypes.windll.user32.SendInput(1, ctypes.byref(command_down), ctypes.sizeof(command_down))
        time.sleep(random.uniform(0.04, 0.13))
        ctypes.windll.user32.SendInput(1, ctypes.byref(command_up), ctypes.sizeof(command_up))
    time.sleep(random.uniform(0.01, 0.04))
if __name__ == '__main__':
    app = None
    exit_code = 1
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        print('[INFO] QApplication object CREATED.', flush=True)
        clear_console()
        print(colored(f'--- VOLX LAUNCHER {VERSION} (PYSIDE6 GUI) ---', 'cyan', attrs=['bold']), flush=True)
        if platform.system() == 'Windows':
            try:
                if 'pygame' not in sys.modules:
                    import pygame
                pygame.init()
            except Exception as e:
                print(colored(f'[WARN] Pygame init failed {e}. Pygame support may be limited.', 'yellow'), flush=True)
        print('[INFO] Initializing KeyAuth...', flush=True)
        if not initialize_keyauth():
            QMessageBox.critical(None, 'KeyAuth Error', 'KeyAuth failed to initialize. Check console. Exiting.')
            sys.exit(1)
        if not handle_keyauth_authentication_pyqt():
            print(colored('[FATAL ERROR] Authentication failed or cancelled. Exiting.', 'red'), flush=True)
            sys.exit(1)
        print('[INFO] KeyAuth authenticated successfully!', flush=True)
        sleep(0.5)
        clear_console()
        print(colored(f'--- Loading Volx Aimbot ({VERSION}) ---', 'cyan', attrs=['bold']), flush=True)
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
            except OSError as e:
                QMessageBox.critical(None, 'Config Error', f'Could not create config directory {e}.')
                sys.exit(1)
        print(f'[INFO] Initializing Aimbot instance ({VERSION})...', flush=True)
        debug_flag = 'debug' in [arg.lower() for arg in sys.argv]
        volx_instance = Aimbot(debug=debug_flag)
        if not volx_instance.yolo_model or not volx_instance.camera:
            volx_instance.handle_error(f"TensorRT Engine ('{Aimbot.selected_model_file}') or BetterCam failed to load. Critical. Cannot continue.", critical=True)
        print('[INFO] Aimbot instance created successfully.', flush=True)
        print('[INFO] Initializing Volx Control GUI (PySide6)...', flush=True)
        main_gui_window = VolxPrimeGUI(volx_instance)
        main_gui_window.show()
        gui_visible = True
        print(f'[INFO] Starting background operations ({VERSION} Aimbot & Listener)...', flush=True)
        if Aimbot.input_method == 'Arduino' and (not volx_instance.ser or not volx_instance.ser.is_open):
            print(colored('[WARN] Initial Arduino connection failed. Using Send Input fallback for now.', 'yellow'), flush=True)
        if Aimbot.input_method == 'DDXoft' and (not Aimbot.mouse_dll):
            print(colored('[WARN] Initial DDXoft driver load failed or not available. Using Send Input fallback for now.', 'yellow'), flush=True)
        aimbot_thread = threading.Thread(target=volx_instance.start, daemon=True)
        aimbot_thread.start()
        listener_thread = threading.Thread(target=start_listener, daemon=True)
        listener_thread.start()
        overlay_status_parts = []
        if fov_overlay_available and Aimbot.fov_overlay_enabled and (not Aimbot.pickaxe_mode_active):
            overlay_status_parts.append('FOV Overlay active')
        overlay_status_str = ', '.join(overlay_status_parts) + '.' if overlay_status_parts else 'FOV Overlay may be off or unavailable (or pickaxe mode active).'
        print(colored(f'[SUCCESS] Volx Control GUI {VERSION} (PySide6) is live! Model {Aimbot.selected_model_file}. {overlay_status_str}', 'green', attrs=['bold']), flush=True)
        exit_code = app.exec()
    except Exception as top_level_main_error:
        print(colored(f'[CRITICAL ERROR] Error in __main__ {top_level_main_error}', 'red', attrs=['bold']), flush=True)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        try:
            if QApplication.instance():
                QMessageBox.critical(None, 'Volx Critical Failure', f"A critical error occurred\n{top_level_main_error}\n\nCheck console for details. Exiting.")
        except Exception as qmsg_err_final:
            print(colored(f"[ERROR] Couldn't show QMessageBox for the critical error {qmsg_err_final}.", 'red'), flush=True)
        exit_code = 1
    finally:
        print('[INFO] Main execution block finished or errored. Running final cleanup...', flush=True)
        if 'volx_instance' in locals() and volx_instance:
            Aimbot.clean_up()
        else:
            if app and QApplication.instance():
                QApplication.instance().quit()