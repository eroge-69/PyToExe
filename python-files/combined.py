
import time
import numpy as np
import sys
import os
import hashlib
import platform
import subprocess
import requests
import win32api
import win32con
from configparser import ConfigParser
import cv2
import bettercam
from pyautogui import size
import serial
import socket
import threading
import datetime
import ctypes
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows
init()


def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart the script with administrator privileges"""
    if is_admin():
        # Already running as admin
        return True
    else:
        print("Requesting administrator privileges...")
        try:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                " ".join(sys.argv), 
                None, 
                1
            )
            return False  # Original process should exit
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            return False



def read_hex(string):
    return int(string, 16)


class UI:
    def __init__(self):
        self.license_info = {}
        self.connection_status = "Disconnected"
        self.aimbot_status = "OFF"
        self.recoil_status = "OFF"
        self.startup_displayed = False
    
    def set_license_info(self, expiry_date, time_left):
        """Set license information"""
        self.license_info = {
            'expiry': expiry_date,
            'time_left': time_left
        }
    
    def set_connection_status(self, status):
        """Set connection status"""
        self.connection_status = "Connected" if status else "Disconnected"
    
    def set_aimbot_status(self, status):
        """Set aimbot status"""
        self.aimbot_status = "ON" if status else "OFF"
    
    def set_recoil_status(self, status):
        """Set recoil status"""
        self.recoil_status = "ON" if status else "OFF"
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_colored_status(self, status):
        """Return colored status text - green for ON, red for OFF"""
        if status == "ON":
            return f"{Fore.GREEN}{status}{Style.RESET_ALL}"
        elif status == "OFF":
            return f"{Fore.RED}{status}{Style.RESET_ALL}"
        else:
            return status
    
    def display_header(self):
        """Display the main header"""
        print("=" * 60)
        print("                    VALORANT COLOR BOT")
        print("=" * 60)
        
        if self.license_info:
            print(f"Expires: {self.license_info['expiry']}")
            print(f"Time left: {self.license_info['time_left']}")
        
        print("-" * 60)
        print(f"Connection: {self.connection_status}")
        print(f"Aimbot: {self.get_colored_status(self.aimbot_status)}")
        print(f"Recoil: {self.get_colored_status(self.recoil_status)}")
        print("=" * 60)
    
    def display_startup(self):
        """Display startup information"""
        if not self.startup_displayed:
            self.clear_screen()
            self.display_header()
            print("ValoAim started")
            print("ValoAim ON")
            print("\nReady to use! Use your configured hotkeys to toggle features.")
            self.startup_displayed = True
    
    def update_status(self, aim_status=None, recoil_status=None, connection_status=None):
        """Update and redisplay status"""
        if aim_status is not None:
            self.set_aimbot_status(aim_status)
        if recoil_status is not None:
            self.set_recoil_status(recoil_status)
        if connection_status is not None:
            self.set_connection_status(connection_status)
        
        # Redisplay the interface
        self.clear_screen()
        self.display_header()
    
    def display_message(self, message):
        """Display a message below the header"""
        print(f"> {message}")



class ConfigReader:
    def __init__(self):
        self.parser = ConfigParser()

        # Communication
        self.com_type = None
        self.ip = None
        self.port = None
        self.com_port = None

        # Screen
        self.detection_threshold = None
        self.upper_color = None
        self.lower_color = None
        self.fov_x = None
        self.fov_y = None
        self.aim_fov_x = None
        self.aim_fov_y = None
        self.fps = None
        self.auto_detect_resolution = None
        self.resolution_x = None
        self.resolution_y = None

        # Aim
        self.offset = None
        self.smooth = None
        self.speed = None
        self.y_speed = None
        self.aim_height = None

        # Recoil
        self.recoil_mode = None
        self.recoil_x = None
        self.recoil_y = None
        self.max_offset = None
        self.recoil_recover = None

        # Trigger
        self.trigger_delay = None
        self.trigger_randomization = None
        self.trigger_threshold = None

        # Rapid fire
        self.target_cps = None

        # Key binds
        self.key_reload_config = None
        self.key_toggle_aim = None
        self.key_toggle_recoil = None
        self.key_exit = None
        self.key_trigger = None
        self.key_rapid_fire = None

        self.aim_keys = []

        # Debug
        self.debug = None
        self.debug_always_on = None
        self.display_mode = None
        self.license_debug = None

        # Get config path and read it
        self.path = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.parser.read(self.path)

    def read_config(self):
        # Get communication settings
        value = self.parser.get('communication', 'type').lower()
        com_type_list = ['none', 'driver', 'serial', 'socket']
        if value in com_type_list:
            self.com_type = value
        else:
            print('WARNING: Invalid com_type value')
        
        match self.com_type:
            case 'socket':
                self.ip = self.parser.get('communication', 'ip')
                self.port = int(self.parser.get('communication', 'port'))
            case 'serial':
                self.com_port = self.parser.get('communication', 'com_port')

        # Get screen settings
        values_str = self.parser.get('screen', 'detection_threshold').split(',')
        self.detection_threshold = (int(values_str[0].strip()), int(values_str[1].strip()))

        upper_color = self.parser.get('screen', 'upper_color').split(',')
        lower_color = self.parser.get('screen', 'lower_color').split(',')
        for i in range(0, 3):
            upper_color[i] = int(upper_color[i].strip())
        for i in range(0, 3):
            lower_color[i] = int(lower_color[i].strip())
        self.upper_color = np.array(upper_color)
        self.lower_color = np.array(lower_color)

        self.fov_x = int(self.parser.get('screen', 'fov_x'))
        self.fov_y = int(self.parser.get('screen', 'fov_y'))
        self.aim_fov_x = int(self.parser.get('screen', 'aim_fov_x'))
        self.aim_fov_y = int(self.parser.get('screen', 'aim_fov_y'))
        fps_value = int(self.parser.get('screen', 'fps'))
        self.fps = int(np.floor(1000 / fps_value + 1))

        value = self.parser.get('screen', 'auto_detect_resolution').lower()
        if value == 'true':
            self.auto_detect_resolution = True
        else:
            self.auto_detect_resolution = False

        self.resolution_x = int(self.parser.get('screen', 'resolution_x'))
        self.resolution_y = int(self.parser.get('screen', 'resolution_y'))

        # Get aim settings
        self.offset = int(self.parser.get('aim', 'offset'))

        value = float(self.parser.get('aim', 'smooth'))
        if 0 <= value <= 1:
            self.smooth = 1 - value / 1.25
        else:
            print('WARNING: Invalid smooth value')

        self.speed = float(self.parser.get('aim', 'speed'))
        self.y_speed = float(self.parser.get('aim', 'y_speed'))

        value = float(self.parser.get('aim', 'aim_height'))
        if 0 <= value <= 1:
            self.aim_height = value
        else:
            print('WARNING: Invalid aim_height value')

        # Get recoil settings
        value = self.parser.get('recoil', 'mode').lower()
        recoil_mode_list = ['move', 'offset']
        if value in recoil_mode_list:
            self.recoil_mode = value
        else:
            print('WARNING: Invalid recoil_mode value')

        self.recoil_x = float(self.parser.get('recoil', 'recoil_x'))
        self.recoil_y = float(self.parser.get('recoil', 'recoil_y'))
        self.max_offset = int(self.parser.get('recoil', 'max_offset'))
        self.recoil_recover = float(self.parser.get('recoil', 'recover'))

        # Get trigger settings
        self.trigger_delay = int(self.parser.get('trigger', 'trigger_delay'))
        self.trigger_randomization = int(self.parser.get('trigger', 'trigger_randomization'))
        self.trigger_threshold = int(self.parser.get('trigger', 'trigger_threshold'))

        # Get rapid fire settings
        self.target_cps = int(self.parser.get('rapid_fire', 'target_cps'))

        # Get keybind settings
        self.key_reload_config = read_hex(self.parser.get('key_binds', 'key_reload_config'))
        self.key_toggle_aim = read_hex(self.parser.get('key_binds', 'key_toggle_aim'))
        self.key_toggle_recoil = read_hex(self.parser.get('key_binds', 'key_toggle_recoil'))
        self.key_exit = read_hex(self.parser.get('key_binds', 'key_exit'))
        self.key_trigger = read_hex(self.parser.get('key_binds', 'key_trigger'))
        self.key_rapid_fire = read_hex(self.parser.get('key_binds', 'key_rapid_fire'))

        aim_keys_str = self.parser.get('key_binds', 'aim_keys')
        if not aim_keys_str == 'off':
            aim_keys_str = aim_keys_str.split(',')
            for key in aim_keys_str:
                self.aim_keys.append(read_hex(key))
        else:
            self.aim_keys = ['off']

        # Get debug settings
        value = self.parser.get('debug', 'enabled').lower()
        if value == 'true':
            self.debug = True
        else:
            self.debug = False

        value = self.parser.get('debug', 'always_on').lower()
        if value == 'true':
            self.debug_always_on = True
        else:
            self.debug_always_on = False

        value = self.parser.get('debug', 'display_mode').lower()
        display_mode_list = ['game', 'mask']
        if value in display_mode_list:
            self.display_mode = value
        else:
            print('WARNING: Invalid display_mode value')

        value = self.parser.get('debug', 'license_debug').lower()
        if value == 'true':
            self.license_debug = True
        else:
            self.license_debug = False



class Utils:
    def __init__(self, ui=None):
        self.config = ConfigReader()
        self.reload_config()
        self.ui = ui

        self.delay = 0.25
        self.key_reload_config = self.config.key_reload_config
        self.key_toggle_aim = self.config.key_toggle_aim
        self.key_toggle_recoil = self.config.key_toggle_recoil
        self.key_exit = self.config.key_exit
        self.key_trigger = self.config.key_trigger
        self.key_rapid_fire = self.config.key_rapid_fire

        self.aim_keys = self.config.aim_keys
        self.aim_state = False
        self.recoil_state = False

    def check_key_binds(self):  # Return a boolean based on if the config needs to be reloaded
        if win32api.GetAsyncKeyState(self.key_reload_config) < 0:
            return True

        if win32api.GetAsyncKeyState(self.key_toggle_aim) < 0:
            self.aim_state = not self.aim_state
            if self.ui:
                self.ui.update_status(aim_status=self.aim_state)
                status_text = 'ON' if self.aim_state else 'OFF'
                colored_status = self.ui.get_colored_status(status_text)
                self.ui.display_message(f"Aimbot: {colored_status}")
            else:
                print("AIM: " + str(self.aim_state))
            time.sleep(self.delay)

        if win32api.GetAsyncKeyState(self.key_toggle_recoil) < 0:
            self.recoil_state = not self.recoil_state
            if self.ui:
                self.ui.update_status(recoil_status=self.recoil_state)
                status_text = 'ON' if self.recoil_state else 'OFF'
                colored_status = self.ui.get_colored_status(status_text)
                self.ui.display_message(f"Recoil: {colored_status}")
            else:
                print("RECOIL: " + str(self.recoil_state))
            time.sleep(self.delay)
        
        if win32api.GetAsyncKeyState(self.key_exit) < 0:
            if self.ui:
                self.ui.display_message("Exiting...")
            else:
                print("Exiting")
            exit(1)
        return False

    def reload_config(self):
        self.config.read_config()

    def get_aim_state(self):
        if self.aim_state:
            if self.aim_keys[0] == 'off':
                return True
            else:
                for key in self.aim_keys:
                    if win32api.GetAsyncKeyState(key) < 0:
                        return True
        return False

    def get_trigger_state(self):
        if win32api.GetAsyncKeyState(self.key_trigger) < 0:
            return True
        return False

    def get_rapid_fire_state(self):
        if win32api.GetAsyncKeyState(self.key_rapid_fire) < 0:
            return True
        return False

    @staticmethod
    def print_attributes(obj):
        attributes = vars(obj)
        for attribute, value in attributes.items():
            print(f'{attribute}: {value}')



class Cheats:
    def __init__(self, config):
        # Aim
        self.move_x, self.move_y = (0, 0)
        self.previous_x, self.previous_y = (0, 0)
        self.smooth = config.smooth
        self.speed = config.speed
        self.y_speed = config.y_speed

        # Recoil
        self.recoil_offset = 0
        self.recoil_mode = config.recoil_mode
        self.recoil_x = config.recoil_x
        self.recoil_y = config.recoil_y
        self.max_offset = config.max_offset
        self.recoil_recover = config.recoil_recover

    def calculate_aim(self, state, target):
        if state and target is not None:
            x, y = target

            # Calculate x and y speed
            x *= self.speed
            y *= self.speed * self.y_speed

            # Apply smoothing with the previous x and y value
            x = (1 - self.smooth) * self.previous_x + self.smooth * x
            y = (1 - self.smooth) * self.previous_y + self.smooth * y

            # Store the calculated values for next calculation
            self.previous_x, self.previous_y = (x, y)
            # Apply x and y to the move variables
            self.move_x, self.move_y = (x, y)

    def apply_recoil(self, state, delta_time):
        if state and delta_time != 0:
            # Mode move just applies configured movement to the move values
            if self.recoil_mode == 'move' and win32api.GetAsyncKeyState(0x01) < 0:
                self.move_x += self.recoil_x * delta_time
                self.move_y += self.recoil_y * delta_time
            # Mode offset moves the camera upward, so it aims below target
            elif self.recoil_mode == 'offset':
                # Add recoil_y to the offset when mouse1 is down
                if win32api.GetAsyncKeyState(0x01) < 0:
                    if self.recoil_offset < self.max_offset:
                        self.recoil_offset += self.recoil_y * delta_time
                        if self.recoil_offset > self.max_offset:
                            self.recoil_offset = self.max_offset
                # Start resetting the offset bit by bit if mouse1 is not down
                else:
                    if self.recoil_offset > 0:
                        self.recoil_offset -= self.recoil_recover * delta_time
                        if self.recoil_offset < 0:
                            self.recoil_offset = 0
        else:
            # Reset recoil offset if recoil is off
            self.recoil_offset = 0



class Mouse:
    def __init__(self, config, ui=None):
        self.com_type = config.com_type
        self.click_thread = threading.Thread(target=self.send_click)
        self.last_click_time = time.time()
        self.target_cps = config.target_cps
        self.ui = ui
        self.connected = False

        # Create a lock, so we can use it to not send multiple mouse clicks at the same time
        self.lock = threading.Lock()

        self.ip = config.ip
        self.port = config.port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.com_port = config.com_port
        self.board = None

        # Create variables to store the remainder decimal points for our mouse move function
        self.remainder_x = 0
        self.remainder_y = 0
        
        match self.com_type:
            case 'socket':
                if self.ui:
                    self.ui.display_message(f'Connecting to {self.ip}:{self.port}...')
                else:
                    print(f'Connecting to {self.ip}:{self.port}...')
                try:
                    self.client.connect((self.ip, self.port))
                    self.connected = True
                    if self.ui:
                        self.ui.update_status(connection_status=True)
                        self.ui.display_message('Socket connected')
                    else:
                        print('Socket connected')
                except Exception as e:
                    if self.ui:
                        self.ui.display_message(f'ERROR: Could not connect (Socket). {e}')
                    else:
                        print(f'ERROR: Could not connect (Socket). {e}')
                    self.close_connection()
            case 'serial':
                try:
                    self.board = serial.Serial(self.com_port, 115200)
                    self.connected = True
                    if self.ui:
                        self.ui.update_status(connection_status=True)
                        self.ui.display_message('Serial connected')
                    else:
                        print('Serial connected')
                except Exception as e:
                    if self.ui:
                        self.ui.display_message(f'ERROR: Could not connect (Serial). {e}')
                    else:
                        print(f'ERROR: Could not connect (Serial). {e}')
                    self.close_connection()
            case 'driver':
                import interception
                interception.auto_capture_devices(mouse=True)
                self.connected = True
                if self.ui:
                    self.ui.update_status(connection_status=True)
                    self.ui.display_message('Driver connected')
            case 'none':
                self.connected = True
                if self.ui:
                    self.ui.update_status(connection_status=True)
                    self.ui.display_message('Direct input mode enabled')

    def __del__(self):
        self.close_connection()

    def close_connection(self):
        if self.com_type == 'socket':
            if self.client is not None:
                self.client.close()
        elif self.com_type == 'serial':
            if self.board is not None:
                self.board.close()
        
        self.connected = False
        if self.ui:
            self.ui.update_status(connection_status=False)

    def move(self, x, y):
        # Add the remainder from the previous calculation
        x += self.remainder_x
        y += self.remainder_y

        # Round x and y, and calculate the new remainder
        self.remainder_x = x
        self.remainder_y = y
        x = int(x)
        y = int(y)
        self.remainder_x -= x
        self.remainder_y -= y

        if x != 0 or y != 0:  # Don't send anything if there's no movement
            match self.com_type:
                case 'socket' | 'serial':
                    self.send_command(f'M{x},{y}\r')
                case 'driver':
                    interception.move_relative(x, y)
                    print(f'M({x}, {y})')
                case 'none':
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
                    print(f'M({x}, {y})')

    def click(self, delay_before_click=0):
        if (
                not self.click_thread.is_alive() and
                time.time() - self.last_click_time >= 1 / self.target_cps
        ):
            self.click_thread = threading.Thread(target=self.send_click, args=(delay_before_click,))
            self.click_thread.start()

    def send_click(self, delay_before_click=0):
        time.sleep(delay_before_click)
        self.last_click_time = time.time()
        match self.com_type:
            case 'socket' | 'serial':
                self.send_command('C\r')
            case 'driver':
                random_delay = (np.random.randint(40) + 40) / 1000
                interception.mouse_down('left')
                time.sleep(random_delay)
                interception.mouse_up('left')
                print(f'C({random_delay * 1000:g})')
            case 'none':
                random_delay = (np.random.randint(40) + 40) / 1000
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(random_delay)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                print(f'C({random_delay * 1000:g})')
        time.sleep((np.random.randint(10) + 25) / 1000)  # Sleep to avoid sending another click instantly after mouseup

    def send_command(self, command):
        with self.lock:
            match self.com_type:
                case 'socket':
                    self.client.sendall(command.encode())
                case 'serial':
                    self.board.write(command.encode())
            # Removed debug prints for cleaner output
            self.get_response()

    def get_response(self):  # Waits for a response before sending a new instruction
        match self.com_type:
            case 'socket':
                return self.client.recv(4).decode()
            case 'serial':
                while True:
                    receive = self.board.readline().decode('utf-8').strip()
                    if len(receive) > 0:
                        return receive


# ===== SCREEN CLASS =====
class Screen:
    def __init__(self, config):
        self.cam = bettercam.create(output_color="BGR")

        self.offset = config.offset

        if config.auto_detect_resolution:
            screen_size = size()
            self.screen = (screen_size.width, screen_size.height)
        else:
            self.screen = (config.resolution_x, config.resolution_y)

        self.screen_center = (self.screen[0] // 2, self.screen[1] // 2)
        self.screen_region = (
            0,
            0,
            self.screen[0],
            self.screen[1]
        )
        self.fov = (config.fov_x, config.fov_y)
        self.fov_center = (self.fov[0] // 2, self.fov[1] // 2)
        self.fov_region = (
            self.screen_center[0] - self.fov[0] // 2,
            self.screen_center[1] - self.fov[1] // 2 - self.offset,
            self.screen_center[0] + self.fov[0] // 2,
            self.screen_center[1] + self.fov[1] // 2 - self.offset
        )
        self.detection_threshold = config.detection_threshold
        self.upper_color = config.upper_color
        self.lower_color = config.lower_color
        self.fps = config.fps
        self.aim_height = config.aim_height
        self.debug = config.debug
        self.thresh = None
        self.target = None
        self.closest_contour = None
        self.img = None
        self.trigger_threshold = config.trigger_threshold
        self.aim_fov = (config.aim_fov_x, config.aim_fov_y)

        # Setup debug display
        if self.debug:
            self.display_mode = config.display_mode
            self.window_name = 'Riot Games'
            self.window_resolution = (
                self.screen[0] // 4,  # Changed from 1/2 to 1/4 of screen width
                self.screen[1] // 4   # Changed from 1/2 to 1/4 of screen height
            )
            # Create normal window
            cv2.namedWindow(self.window_name)
            # Make window always stay on top
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
            # Position the window in the bottom right corner
            window_x = self.screen[0] - self.window_resolution[0] - 20  # 20px margin from right
            window_y = self.screen[1] - self.window_resolution[1] - 60  # 60px margin from bottom
            cv2.moveWindow(self.window_name, window_x, window_y)

    def __del__(self):
        del self.cam

    def screenshot(self, region):
        while True:
            image = self.cam.grab(region)
            if image is not None:
                return np.array(image)

    def get_target(self, recoil_offset):
        # Convert the offset to an integer, since it is used to define the capture region
        recoil_offset = int(recoil_offset)

        # Reset variables
        self.target = None
        trigger = False
        self.closest_contour = None

        # Capture a screenshot
        self.img = self.screenshot(self.get_region(self.fov_region, recoil_offset))

        # Convert the screenshot to HSV color space for color detection
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # Create a mask to identify pixels within the specified color range
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        # Apply morphological dilation to increase the size of the detected color blobs
        kernel = np.ones((self.detection_threshold[0], self.detection_threshold[1]), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=5)

        # Apply thresholding to convert the mask into a binary image
        self.thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]

        # Find contours of the detected color blobs
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Identify the closest target contour
        if len(contours) != 0:
            min_distance = float('inf')
            for contour in contours:
                # Make a bounding rectangle for the target
                rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)

                # Calculate the coordinates of the center of the target
                x = rect_x + rect_w // 2 - self.fov_center[0]
                y = int(rect_y + rect_h * (1 - self.aim_height)) - self.fov_center[1]

                # Update the closest target if the current target is closer
                distance = np.sqrt(x**2 + y**2)
                if distance < min_distance:
                    min_distance = distance
                    self.closest_contour = contour
                    if (
                            -self.aim_fov[0] <= x <= self.aim_fov[0] and
                            -self.aim_fov[1] <= y <= self.aim_fov[1]
                    ):
                        self.target = (x, y)

            if (
                # Check if crosshair is inside the closest target
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0], self.fov_center[1]), False) >= 0 and

                # Eliminate a lot of false positives by also checking pixels near the crosshair.
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0] + self.trigger_threshold, self.fov_center[1]), False) >= 0 and
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0] - self.trigger_threshold, self.fov_center[1]), False) >= 0 and
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0], self.fov_center[1] + self.trigger_threshold), False) >= 0 and
                cv2.pointPolygonTest(
                    self.closest_contour, (self.fov_center[0], self.fov_center[1] - self.trigger_threshold), False) >= 0
            ):
                trigger = True

        if self.debug:
            self.debug_display(recoil_offset)

        return self.target, trigger

    @staticmethod
    def get_region(region, recoil_offset):
        region = (
            region[0],
            region[1] - recoil_offset,
            region[2],
            region[3] - recoil_offset
        )
        return region

    def debug_display(self, recoil_offset):
        if self.display_mode == 'game':
            debug_img = self.img
        else:
            debug_img = self.thresh
            debug_img = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)

        full_img = self.screenshot(self.screen_region)

        # Draw line to the closest target
        if self.target is not None:
            debug_img = cv2.line(
                debug_img,
                self.fov_center,
                (self.target[0] + self.fov_center[0], self.target[1] + self.fov_center[1]),
                (0, 255, 0),
                2
            )

        # Draw rectangle around closest target
        if self.closest_contour is not None:
            x, y, w, h = cv2.boundingRect(self.closest_contour)
            debug_img = cv2.rectangle(
                debug_img,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )

        # Draw FOV, a green rectangle
        debug_img = cv2.rectangle(
            debug_img,
            (0, 0),
            (self.fov[0], self.fov[1]),
            (0, 255, 0),
            2
        )

        # Draw Aim FOV, a yellow rectangle
        debug_img = cv2.rectangle(
            debug_img,
            (
                self.fov[0] // 2 - self.aim_fov[0] // 2,
                self.fov[1] // 2 - self.aim_fov[1] // 2
            ),
            (
                self.fov[0] // 2 + self.aim_fov[0] // 2,
                self.fov[1] // 2 + self.aim_fov[1] // 2
            ),
            (0, 255, 255),
            2
        )

        offset_x = (self.screen[0] - self.fov[0]) // 2
        offset_y = (self.screen[1] - self.fov[1]) // 2 - self.offset - recoil_offset
        full_img[offset_y:offset_y+debug_img.shape[0], offset_x:offset_x+debug_img.shape[1]] = debug_img
        # Draw a rectangle crosshair
        full_img = cv2.rectangle(
            full_img,
            (self.screen_center[0] - 5, self.screen_center[1] - 5),
            (self.screen_center[0] + 5, self.screen_center[1] + 5),
            (255, 255, 255),
            1
        )
        full_img = cv2.resize(full_img, self.window_resolution)
        cv2.imshow(self.window_name, full_img)
        cv2.waitKey(1)


# ===== MAIN FUNCTIONS =====
def getchecksum():
    try:
        if getattr(sys, 'frozen', False):
            path = sys.executable
        else:
            path = os.path.abspath(__file__)
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return "debug_mode"

def get_hwid():
    try:
        info = []
        try:
            cpu = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().strip()
            info.append(cpu.split('\n')[1].strip())
        except:
            pass
        try:
            mb = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().strip()
            info.append(mb.split('\n')[1].strip())
        except:
            pass
        combined = ''.join(info) if info else platform.node()
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    except:
        return hashlib.sha256(platform.node().encode()).hexdigest()[:32]

def save_license_to_config(license_key):
    """Save license key to config file"""
    try:
        import configparser
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
        
        if 'license' not in config:
            config.add_section('license')
        
        config['license']['key'] = license_key
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    except:
        pass

def get_license_from_config():
    """Get license key from config file"""
    try:
        import configparser
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
        
        if 'license' in config and 'key' in config['license']:
            return config['license']['key'].strip()
    except:
        pass
    return ""

def keyauth_login():
    keyauthapp = {
        'name': "aimbot",
        'ownerid': "1DhjzbeWgc", 
        'version': "1.0",
        'hash': getchecksum()
    }
    
    hwid = get_hwid()
    
    # Init
    try:
        r = requests.post("https://keyauth.win/api/1.2/", data={
            'type': 'init',
            'name': keyauthapp['name'],
            'ownerid': keyauthapp['ownerid'],
            'ver': keyauthapp['version'],
            'hash': keyauthapp['hash'],
            'hwid': hwid
        })
        response = r.json()
        if not response['success']:
            print(f"Init failed: {response['message']}")
            input("Press Enter to exit...")
            sys.exit(1)
        sessionid = response['sessionid']
    except:
        print("Connection failed!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Try license from config first
    saved_license = get_license_from_config()
    if saved_license:
        success, expiry, time_left = try_license(saved_license, hwid, sessionid, keyauthapp)
        if success:
            return sessionid, keyauthapp, expiry, time_left
    
    # License Login Only
    while True:
        license = input("License Key: ")
        
        # Clear screen and show fresh prompt
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        if not license.strip():
            print("License failed: No license key entered, try again.\n")
            continue
        
        success, expiry, time_left = try_license(license, hwid, sessionid, keyauthapp)
        if success:
            # Save successful license to config
            save_license_to_config(license)
            return sessionid, keyauthapp, expiry, time_left

def try_license(license, hwid, sessionid, keyauthapp):
    """Try to authenticate with a license key"""
    try:
        r = requests.post("https://keyauth.win/api/1.2/", data={
            'type': 'license',
            'key': license,
            'hwid': hwid,
            'sessionid': sessionid,
            'name': keyauthapp['name'],
            'ownerid': keyauthapp['ownerid']
        })
        response = r.json()
        if response['success']:
            # Get expiry time
            expiry = response['info']['subscriptions'][0]['expiry']
            expiry_date = datetime.datetime.fromtimestamp(int(expiry))
            current_time = datetime.datetime.now()
            time_left = expiry_date - current_time
            
            # Check if license is expired
            if time_left.total_seconds() <= 0:
                print("License failed: Your license has expired. Please renew your subscription.\n")
                return False, None, None
            
            print("License activated successfully!")
            
            # Format expiry date
            expiry_str = expiry_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate time left properly
            total_seconds = int(time_left.total_seconds())
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            # Format time left display
            time_parts = []
            if days > 0:
                time_parts.append(f"{days} days")
            if hours > 0:
                time_parts.append(f"{hours} hours")
            if minutes > 0:
                time_parts.append(f"{minutes} minutes")
            if seconds > 0 or not time_parts:  # Show seconds if it's the only unit or if nothing else
                time_parts.append(f"{seconds} seconds")
            
            time_left_str = ', '.join(time_parts)
            
            print(f"Expires: {expiry_str}")
            print(f"Time left: {time_left_str}\n")
            
            return True, expiry_str, time_left_str
        else:
            print(f"License failed: {response['message']}\n")
            return False, None, None
    except Exception as e:
        print(f"License failed: Connection error, try again.\n")
        return False, None, None

def check_license_validity(sessionid, keyauthapp, debug_enabled=False):
    """Check if license is still valid"""
    try:
        hwid = get_hwid()
        r = requests.post("https://keyauth.win/api/1.2/", data={
            'type': 'check',
            'sessionid': sessionid,
            'name': keyauthapp['name'],
            'ownerid': keyauthapp['ownerid']
        }, timeout=10)  # Add timeout to prevent hanging
        
        if r.status_code != 200:
            if debug_enabled:
                print(f"[DEBUG] License check failed - HTTP {r.status_code}")
            return True  # Assume valid on network errors to prevent false positives
            
        response = r.json()
        if response['success']:
            # Check if subscriptions exist and have expiry data
            if 'info' not in response or 'subscriptions' not in response['info'] or not response['info']['subscriptions']:
                if debug_enabled:
                    print("[DEBUG] License check failed - Invalid response structure")
                return True  # Assume valid if structure is unexpected
                
            # Check expiry
            expiry = response['info']['subscriptions'][0]['expiry']
            import datetime
            expiry_date = datetime.datetime.fromtimestamp(int(expiry))
            current_time = datetime.datetime.now()
            time_left = expiry_date - current_time
            
            if time_left.total_seconds() <= 0:
                if debug_enabled:
                    print(f"[DEBUG] License actually expired: {expiry_date}")
                return False
            return True
        else:
            if debug_enabled:
                print(f"[DEBUG] License check failed - API response: {response.get('message', 'Unknown error')}")
            return True  # Assume valid on API errors to prevent false positives
    except requests.exceptions.RequestException as e:
        if debug_enabled:
            print(f"[DEBUG] License check failed - Network error: {e}")
        return True  # Assume valid on network errors
    except Exception as e:
        if debug_enabled:
            print(f"[DEBUG] License check failed - Unexpected error: {e}")
        return True  # Assume valid on unexpected errors

def main():
    # Check for admin privileges and restart if needed
    if not run_as_admin():
        print("Restarting with administrator privileges...")
        sys.exit(0)
    
    print(f"{Fore.GREEN}Running with administrator privileges!{Style.RESET_ALL}")
    
    # KeyAuth
    sessionid, keyauthapp, expiry, time_left = keyauth_login()
    
    # Initialize UI
    ui = UI()
    ui.set_license_info(expiry, time_left)
    
    # Log usage
    try:
        requests.post("https://keyauth.win/api/1.2/", data={
            'type': 'log',
            'pcuser': os.getenv('USERNAME', 'Unknown'),
            'message': f"ValoAim started - HWID: {get_hwid()}",
            'sessionid': sessionid,
            'name': keyauthapp['name'],
            'ownerid': keyauthapp['ownerid']
        })
    except:
        pass
    
    # Display startup with UI
    ui.display_startup()
    
    # Get initial config for license debugging
    initial_utils = Utils(ui)
    license_debug_enabled = initial_utils.config.license_debug
    del initial_utils
    
    # License monitoring setup
    import threading
    license_valid = True
    failed_checks = 0  # Track consecutive failed checks
    
    def license_monitor():
        nonlocal license_valid, failed_checks
        while license_valid:
            time.sleep(300)  # Check every 5 minutes
            
            if not license_valid:  # Exit if main thread set license_valid to False
                break
                
            if license_debug_enabled:
                print("[DEBUG] Performing periodic license check...")
            
            # Check license validity
            is_valid = check_license_validity(sessionid, keyauthapp, license_debug_enabled)
            
            if not is_valid:
                failed_checks += 1
                print(f"\n[WARNING] License check failed ({failed_checks}/3)")
                
                # Only exit after 3 consecutive failures to avoid false positives
                if failed_checks >= 3:
                    print("\n[WARNING] License expired after multiple checks! Application will close in 10 seconds...")
                    license_valid = False
                    time.sleep(10)
                    os._exit(1)
            else:
                # Reset failed checks counter on successful validation
                if failed_checks > 0 and license_debug_enabled:
                    print("[DEBUG] License check successful - resetting failed counter")
                failed_checks = 0
    
    # Start license monitoring in background
    license_thread = threading.Thread(target=license_monitor, daemon=True)
    license_thread.start()

    # Program loop
    while license_valid:
        # Track delta time
        start_time = time.time()

        utils = Utils(ui)
        config = utils.config
        cheats = Cheats(config)
        mouse = Mouse(config, ui)
        screen = Screen(config)

        # Update UI with current settings
        ui.set_aimbot_status(utils.aim_state)
        ui.set_recoil_status(utils.recoil_state)
        if hasattr(mouse, 'connected'):
            ui.set_connection_status(mouse.connected)
        else:
            # Fallback for connection types that don't set connected status
            ui.set_connection_status(True)

        # Cheat loop
        while True:
            delta_time = time.time() - start_time
            start_time = time.time()
            
            reload_config = utils.check_key_binds()
            if reload_config:
                break

            if (utils.get_aim_state() or utils.get_trigger_state()) or (config.debug and config.debug_always_on):
                # Get target position and check if there is a target in the center of the screen
                target, trigger = screen.get_target(cheats.recoil_offset)

                # Shoot if target in the center of the screen
                if utils.get_trigger_state() and trigger:
                    if config.trigger_delay != 0:
                        delay_before_click = (np.random.randint(config.trigger_randomization) + config.trigger_delay) / 1000
                    else:
                        delay_before_click = 0
                    mouse.click(delay_before_click)

                # Calculate movement based on target position
                cheats.calculate_aim(utils.get_aim_state(), target)

            if utils.get_rapid_fire_state():
                mouse.click()

            # Apply recoil
            cheats.apply_recoil(utils.recoil_state, delta_time)

            # Move the mouse based on the previous calculations
            mouse.move(cheats.move_x, cheats.move_y)

            # Reset move values so the aim doesn't keep drifting when no targets are on the screen
            cheats.move_x, cheats.move_y = (0, 0)

            # Do not loop above the set refresh rate
            time_spent = (time.time() - start_time) * 1000
            if time_spent < screen.fps:
                time.sleep((screen.fps - time_spent) / 1000)

        del utils
        del cheats
        del mouse
        del screen

        ui.display_message('Reloading configuration...')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pass