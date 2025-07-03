import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel, simpledialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import time
import os
import json
import hashlib
import platform
import subprocess
import queue
import webbrowser
import random
import datetime
import zipfile # Added for ZIP file handling
import urllib.parse # Added for URL encoding in VirusTotal URL scan
import shutil # Added for directory cleanup

# Import for Excel logging
import openpyxl
from openpyxl import Workbook, load_workbook

# Importing Yara
try:
    import yara
except ImportError:
    print("WARNING: YARA library (yara-python) not found. Please install it using: pip install yara-python")
    print("Without YARA, local file scanning functionality will be limited.")
    yara = None

# Importing OpenCV for QR code scanning
try:
    import cv2
    import numpy as np
except ImportError:
    print("WARNING: OpenCV (cv2) library not found. Please install it using: pip install opencv-python")
    print("QR code scanning functionality will be unavailable.")
    cv2 = None
    np = None

# Importing win32api, wmi, and pythoncom for better Windows USB detection and COM threading issues
if platform.system() == "Windows":
    try:
        import win32api
        import wmi
        import pythoncom
    except ImportError:
        print("WARNING: win32api, wmi, or pythoncom not found. USB detection might be less robust on Windows.")
        win32api = None
        wmi = None
        pythoncom = None
else:
    win32api = None
    wmi = None
    pythoncom = None

# --- Configuration ---
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

# --- Color Palette (Refined) ---
COLOR_DARK_BLUE = "#003366"
COLOR_PRIMARY_BLUE = "#3498DB"
COLOR_HOVER_BLUE = "#2980B9"

COLOR_ACCENT_GREEN = "#2ECC71"
COLOR_HOVER_GREEN = "#27AE60"

COLOR_WARNING_ORANGE = "#F39C12"
COLOR_HOVER_ORANGE = "#E67E22"

COLOR_ERROR_RED = "#E74C3C"
COLOR_HOVER_RED = "#C0392B"

COLOR_LIGHT_YELLOW = "#FFEB3B"
COLOR_HOVER_LIGHT_YELLOW = "#FDD835"

COLOR_PEACH = "#FFDAB9"
COLOR_HOVER_PEACH = "#FFC699"

COLOR_LIGHT_GREY = "#F0F0F0"
COLOR_HOVER_LIGHT_GREY = "#E0E0E0"

COLOR_LIGHT_PURPLE = "#E0BBE4"  # New color for USB scan button
COLOR_HOVER_PURPLE = "#C3A1CE"  # New hover color for USB scan button

COLOR_LIGHT_GREEN_BG = "#A7D9B4" # New color for QR File Upload button
COLOR_HOVER_GREEN_BG = "#8BF09D" # New hover color for QR File Upload button


COLOR_BACKGROUND_LIGHT = "#E8F5FF"
COLOR_BACKGROUND_HOVER_LIGHT = "#DAECF7"
COLOR_CARD_BACKGROUND = "#FFFFFF"
COLOR_TEXT_DARK = "#333333"
COLOR_TEXT_MUTED = "#666666"
COLOR_HOVER_MUTED = "#505050"
COLOR_BORDER_GREY = "#CCCCCC"

# --- Antivirus Specific Configurations ---
MALICIOUS_LOG_FILE = "malicious_detections.xlsx"
YARA_RULES_FILE = "rules.yar"
QUARANTINE_DIR = "quarantine"
DOWNLOAD_MONITOR_DIR = os.path.join(os.path.expanduser("~"), "Downloads") # Monitor user's Downloads folder
TEMP_EXTRACT_DIR = "temp_zip_extract" # Directory for temporary ZIP extraction

# !!! IMPORTANT: Replace with your actual VirusTotal API Key !!!
# You can get one by signing up on VirusTotal.
# Be aware of API usage limits for public API keys (4 requests/minute, 500 requests/day).
VIRUSTOTAL_API_KEY = "402cd9a8fbe0ef86ba0e5b70beaac3b4b72f2ab500fff391fe64161d26eaaaf7"
VIRUSTOTAL_API_URL = "https://www.virustotal.com/api/v3/files"
VIRUSTOTAL_SCAN_INTERVAL = 15 # Seconds to wait between VirusTotal API calls to respect rate limits.

# --- Dummy Data (for simulation and testing) ---
# Simulating a small set of virus definitions (hashes)
dummy_virus_definitions = {
    "e2d4d03e4d0d0f5e1f0e4d0d0f5e1f0e4d0d0f5e1f0e4d0d0f5e1f0e4d0d0f5e": "EICAR-Test-File",
    "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2": "Dummy.Malware.A",
    "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef": "Dummy.Ransomware.X"
}
# Simulating a small set of trusted file hashes (e.g., system files)
dummy_trusted_files = {
    "f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e6d7c8b9a0f1e2": "System.DLL",
    "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef": "LegitApp.EXE"
}


# --- Function to load image from URL (requires 'requests' library) ---
def load_image_from_url(url, size=(24, 24)):
    try:
        if os.path.exists(url):
            pil_image = Image.open(url)
        else:
            response = requests.get(url, stream=True, timeout=5)
            response.raise_for_status()
            pil_image = Image.open(BytesIO(response.content))
        return ctk.CTkImage(pil_image, size=size)
    except requests.exceptions.Timeout:
        print(f"ERROR: Timeout loading image from URL: {url}.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network/HTTP error loading image from URL: {url} - {e}.")
        return None
    except FileNotFoundError:
        print(f"ERROR: Local icon file not found: {url}.")
        return None
    except Exception as e:
        print(f"ERROR: Failed to process image from URL/Path {url}: {e}")
        return None

# --- Dummy File Creation (for YARA rules and EICAR test) ---
def create_dummy_files():
    """Creates dummy YARA rules and an EICAR test file for demonstration."""
    # Create dummy YARA rules file
    yara_rules_content = """
rule EICAR_Test {
  strings:
    $a = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
  condition:
    $a
}
rule Dummy_Malware_A {
  strings:
    $s1 = "This is a dummy malware signature A" ascii wide
  condition:
    $s1
}
"""
    try:
        with open(YARA_RULES_FILE, "w") as f:
            f.write(yara_rules_content)
        print(f"Created dummy YARA rules file: {YARA_RULES_FILE}")
    except Exception as e:
        print(f"Error creating YARA rules file: {e}")

    # Create EICAR test file
    eicar_content = r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    try:
        with open("eicar_test.txt", "w") as f:
            f.write(eicar_content)
        print("Created EICAR test file: eicar_test.txt")
    except Exception as e:
        print("Error creating EICAR test file: {e}")

    # Create dummy quarantine directory
    if not os.path.exists(QUARANTINE_DIR):
        try:
            os.makedirs(QUARANTINE_DIR)
            print(f"Created quarantine directory: {QUARANTINE_DIR}")
        except Exception as e:
            print(f"Error creating quarantine directory: {e}")


# --- Helper for getting drive letters on Windows ---
def get_drive_letters():
    """Returns a list of drive letters on Windows."""
    if platform.system() == "Windows" and win32api:
        drive_letters = []
        for i in range(26):
            drive_letter = chr(ord('A') + i) + ":\\"
            try:
                # Check if the drive is ready and accessible (not just a placeholder)
                win32api.GetVolumeInformation(drive_letter)
                drive_letters.append(drive_letter)
            except Exception:
                continue
        return drive_letters
    return []

# --- Helper for getting USB drives ---
def get_usb_drives():
    """Identifies connected USB drives (simplified for cross-platform demo)."""
    usb_drives = []
    if platform.system() == "Windows":
        if wmi:
            try:
                # Initialize COM for WMI if not already done in the thread
                # This function might be called from various threads (main or monitor)
                if pythoncom:
                    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
                c = wmi.WMI()
                # WQL query to get logical disks that are removable
                for drive in c.Win32_LogicalDisk():
                    if drive.DriveType == 2:  # 2 means Removable Disk
                        usb_drives.append(drive.Caption + "\\")
            except Exception as e:
                # print(f"WMI error getting USB drives: {e}. Falling back to simple drive check.") # Keep for debugging if needed
                # Fallback if WMI fails or not installed
                for drive in get_drive_letters():
                    # Simple check: if a drive exists and is not C:
                    if os.path.exists(drive) and drive.upper() != "C:\\":
                        usb_drives.append(drive)
            finally:
                if pythoncom:
                    # Uninitialize COM if it was initialized in this function
                    # This check is crucial to avoid CoUninitialize called too many times
                    pythoncom.CoUninitialize()
        else:
            # Fallback if wmi is not available
            for drive in get_drive_letters():
                if os.path.exists(drive) and drive.upper() != "C:\\":
                    usb_drives.append(drive)
    elif platform.system() == "Linux":
        # Basic Linux approach (needs refinement for robustness)
        # Often USB drives are mounted under /media or /mnt
        media_dir = "/media"
        if os.path.exists(media_dir):
            for user_dir in os.listdir(media_dir):
                full_user_dir = os.path.join(media_dir, user_dir)
                if os.path.isdir(full_user_dir):
                    for drive in os.listdir(full_user_dir):
                        full_drive_path = os.path.join(full_user_dir, drive)
                        if os.path.isdir(full_drive_path) and os.path.ismount(full_drive_path):
                            usb_drives.append(full_drive_path)
    elif platform.system() == "Darwin": # macOS
        # Basic macOS approach (needs refinement)
        # USB drives typically mount under /Volumes
        volumes_dir = "/Volumes"
        if os.path.exists(volumes_dir):
            for drive in os.listdir(volumes_dir):
                full_drive_path = os.path.join(volumes_dir, drive)
                if os.path.isdir(full_drive_path) and os.path.ismount(full_drive_path) and not drive.startswith('.'):
                    # Exclude macOS system volumes that might appear
                    # A more robust check would involve diskutil
                    usb_drives.append(full_drive_path)
    return list(set(usb_drives)) # Return unique drives


# --- Main Application Class ---
class AdvancedSecurityAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Advanced Security Analyzer")
        self.geometry("800x700") # Adjusted geometry to accommodate new sections
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BACKGROUND_LIGHT)

        # Configure grid layout
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0) # Added more rows
        self.grid_columnconfigure(0, weight=1)

        # --- Load Icons ---
        self.usb_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/usb-connected.png")
        self.stop_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/stop.png")
        self.log_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/document.png")
        self.camera_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/camera--v1.png")
        self.file_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/file.png")
        self.analyze_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/search--v1.png")
        self.link_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/link--v1.png")
        self.close_icon = load_image_from_url("https://img.icons8.com/ios-glyphs/60/delete-sign.png")

        # --- AntivirusApp Integration Variables ---
        self.rules = None
        self.running_scan_thread = None
        self.stop_scan_flag = False
        self.download_monitor_stop_flag = False
        self.usb_monitor_stop_flag = False
        
        # Initialize thread attributes to None to avoid AttributeError
        self.download_monitor_thread = None
        self.usb_monitor_thread = None

        # QR Camera specific variables
        self.qr_camera_thread = None
        self.qr_camera_running = False
        self.cap = None # OpenCV video capture object
        self.qr_detector = None # OpenCV QR code detector

        self.scan_history_file = "scan_history.json"
        
        self.files_scanned = 0
        self.threats_found = 0

        # Initialize log_messages and log_popup_text_widget before log_queue and load_scan_history
        self.log_messages = []  # To store log history for the log viewer
        self.log_popup_text_widget = None # Will be set when the log viewer popup is active

        # Queue for inter-thread communication (e.g., logging)
        self.log_queue = queue.Queue()
        self._process_log_queue() # Start processing log messages
        
        # Load scan history after log_queue is initialized as load_scan_history logs messages
        self.scan_history = self.load_scan_history()
        self.scanned_usb_identifiers = {d['path_id'] for d in self.scan_history.get('usbs', [])}
        self.scanned_file_hashes = {f['hash'] for f in self.scan_history.get('files', [])}
        
        # NEW: Keep track of files already processed by download monitor to avoid re-scanning
        self.processed_download_files = set()


        self.create_widgets()
        
        # --- Initialize Antivirus Components ---
        create_dummy_files() # Ensure rules and EICAR are present
        self.load_yara_rules(YARA_RULES_FILE)
        self._initialize_excel_log()
        self.update_status_label("System ready. YARA rules loaded.", COLOR_ACCENT_GREEN)
        self.update_scan_info()

        # Start monitors in separate threads
        self.start_download_monitor_thread() # NEW: Start download monitor
        self.start_usb_monitor_thread()


    def create_widgets(self):
        # 1. Main Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Advanced Security Analyzer",
            font=ctk.CTkFont(size=32, weight="bold", family="Arial"),
            text_color=COLOR_DARK_BLUE
        )
        self.title_label.grid(row=0, column=0, pady=(30, 20), sticky="n")

        # 2. Status and Progress Bar Section (Card)
        self.status_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=COLOR_CARD_BACKGROUND)
        self.status_frame.grid(row=1, column=0, padx=30, pady=15, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Initializing...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_WARNING_ORANGE
        )
        self.status_label.grid(row=0, column=0, pady=(20, 5))

        self.scan_info_label = ctk.CTkLabel(
            self.status_frame,
            text="Files Scanned: 0 | Threats Found: 0",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=COLOR_TEXT_MUTED
        )
        self.scan_info_label.grid(row=1, column=0, pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            orientation="horizontal",
            mode="determinate",
            height=12,
            corner_radius=6,
            fg_color=COLOR_BORDER_GREY,
            progress_color=COLOR_ACCENT_GREEN
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=2, column=0, padx=25, pady=(0, 20), sticky="ew")

        # 3. General Scan Options Frame (for USB, Stop, Logs)
        self.general_scan_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=COLOR_CARD_BACKGROUND)
        self.general_scan_frame.grid(row=2, column=0, padx=30, pady=15, sticky="ew")
        self.general_scan_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        button_pady = 10
        button_padx = 10
        
        self.usb_scan_button = ctk.CTkButton(
            self.general_scan_frame,
            text="Scan USB Drive",
            command=self.start_usb_scan,
            compound="left",
            image=self.usb_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_LIGHT_PURPLE, # Changed to light purple
            hover_color=COLOR_HOVER_PURPLE, # Changed to hover purple
            text_color=COLOR_TEXT_DARK, # Set text color to black
            height=45
        )
        self.usb_scan_button.grid(row=0, column=0, padx=button_padx, pady=button_pady, sticky="ew")

        self.stop_scan_button = ctk.CTkButton(
            self.general_scan_frame,
            text="Stop Scan",
            command=self.stop_scan,
            compound="left",
            image=self.stop_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_ERROR_RED,
            hover_color=COLOR_HOVER_RED,
            text_color=COLOR_TEXT_DARK, # Set text color to black
            height=45
        )
        self.stop_scan_button.grid(row=0, column=1, padx=button_padx, pady=button_pady, sticky="ew")

        self.view_logs_button = ctk.CTkButton(
            self.general_scan_frame,
            text="View Scan Logs",
            command=self.view_scan_logs,
            compound="left",
            image=self.log_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_LIGHT_YELLOW,
            text_color=COLOR_TEXT_DARK,
            hover_color=COLOR_HOVER_LIGHT_YELLOW,
            height=45
        )
        self.view_logs_button.grid(row=0, column=2, padx=button_padx, pady=button_pady, sticky="ew")


        # 4. File Analysis Section (New Frame for QR and File/ZIP analysis)
        self.file_analysis_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=COLOR_CARD_BACKGROUND)
        self.file_analysis_frame.grid(row=3, column=0, padx=30, pady=15, sticky="ew")
        self.file_analysis_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.file_analysis_frame.grid_rowconfigure(0, weight=0) # For title
        self.file_analysis_frame.grid_rowconfigure(1, weight=1) # For buttons

        self.file_analysis_label = ctk.CTkLabel(
            self.file_analysis_frame,
            text="File Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_DARK_BLUE
        )
        self.file_analysis_label.grid(row=0, column=0, columnspan=3, pady=(15, 10))

        self.scan_qr_camera_button = ctk.CTkButton(
            self.file_analysis_frame,
            text="QR Scan", # Changed text as per screenshot
            command=self.scan_qr_camera,
            compound="left",
            image=self.camera_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_PEACH,
            text_color=COLOR_TEXT_DARK,
            hover_color=COLOR_HOVER_PEACH,
            height=45
        )
        self.scan_qr_camera_button.grid(row=1, column=0, padx=button_padx, pady=(0, button_pady), sticky="ew")

        self.scan_qr_file_button = ctk.CTkButton(
            self.file_analysis_frame,
            text="QR File Upload", # Changed text as per screenshot
            command=self.scan_qr_file,
            compound="left",
            image=self.file_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_LIGHT_GREEN_BG, # Changed to light green
            text_color=COLOR_TEXT_DARK,
            hover_color=COLOR_HOVER_GREEN_BG, # Changed to hover green
            height=45
        )
        self.scan_qr_file_button.grid(row=1, column=1, padx=button_padx, pady=(0, button_pady), sticky="ew")

        self.analyze_file_zip_button = ctk.CTkButton(
            self.file_analysis_frame,
            text="Analyze File/ZIP",
            command=self.analyze_file_zip,
            compound="left",
            image=self.analyze_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_WARNING_ORANGE,
            hover_color=COLOR_HOVER_ORANGE,
            text_color=COLOR_TEXT_DARK, # Set text color to black
            height=45
        )
        self.analyze_file_zip_button.grid(row=1, column=2, padx=button_padx, pady=(0, button_pady), sticky="ew")

        # 5. URL Analysis Section (Existing frame with new title)
        self.url_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=COLOR_CARD_BACKGROUND)
        self.url_frame.grid(row=4, column=0, padx=30, pady=15, sticky="ew") # Moved to row 4
        self.url_frame.grid_columnconfigure(0, weight=4)
        self.url_frame.grid_columnconfigure(1, weight=1)
        self.url_frame.grid_rowconfigure(0, weight=0) # For title
        self.url_frame.grid_rowconfigure(1, weight=1) # For entry and button

        self.url_analysis_label = ctk.CTkLabel(
            self.url_frame,
            text="URL Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_DARK_BLUE
        )
        self.url_analysis_label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Enter URL to check...",
            font=ctk.CTkFont(size=14),
            fg_color=COLOR_LIGHT_GREY, # Changed to match check_url_button background
            text_color=COLOR_TEXT_DARK,
            border_color=COLOR_BORDER_GREY,
            height=40
        )
        self.url_entry.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew") # pady adjusted

        self.check_url_button = ctk.CTkButton(
            self.url_frame,
            text="Check URL",
            command=self.check_url,
            compound="left",
            image=self.link_icon,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_LIGHT_GREY,
            text_color=COLOR_TEXT_DARK,
            hover_color=COLOR_HOVER_LIGHT_GREY,
            height=40
        )
        self.check_url_button.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="ew") # pady adjusted

        # 6. Close Application Button
        self.close_button = ctk.CTkButton(
            self,
            text="Close",  # Changed text to "Close"
            command=self.close_application,
            compound="left",
            image=self.close_icon,
            font=ctk.CTkFont(size=15, weight="bold"), # Ensured font is bold
            fg_color=COLOR_PRIMARY_BLUE, 
            hover_color=COLOR_HOVER_BLUE, 
            text_color="black", # Changed text color to black
            height=50
        )
        self.close_button.grid(row=5, column=0, padx=30, pady=(10, 30), sticky="s")


    # --- AntivirusApp Merged Methods (all methods below are unchanged from previous version) ---
    def update_status_label(self, message, color="black"):
        self.after(0, lambda: self.status_label.configure(text=f"Status: {message}", text_color=color))

    def update_scan_info(self):
        self.after(0, lambda: self.scan_info_label.configure(text=f"Files Scanned: {self.files_scanned} | Threats Found: {self.threats_found}"))

    def log_result(self, message, color="black"):
        """Logs messages to an internal list and updates the log viewer if open."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_queue.put((formatted_message, color)) # Put messages into a queue

    def _process_log_queue(self):
        """Processes messages from the log queue and updates the log viewer."""
        while not self.log_queue.empty():
            message, color = self.log_queue.get()
            self.log_messages.append((message, color))
            if self.log_popup_text_widget:
                self.log_popup_text_widget.configure(state='normal')
                self.log_popup_text_widget.insert(tk.END, message + "\n", color)
                self.log_popup_text_widget.configure(state='disabled')
                self.log_popup_text_widget.see(tk.END)
        self.after(100, self._process_log_queue) # Schedule next check

    def _initialize_excel_log(self):
        """Initializes the Excel file for malicious detections with headers if it doesn't exist."""
        if not os.path.exists(MALICIOUS_LOG_FILE):
            try:
                wb = Workbook()
                ws = wb.active
                ws.title = "Malicious Files"
                headers = ["Timestamp", "File Path", "File Hash", "Threat Details", "Scan Type"]
                ws.append(headers)
                wb.save(MALICIOUS_LOG_FILE)
                self.log_result(f"Initialized new malicious detections log at: {MALICIOUS_LOG_FILE}", "blue")
            except Exception as e:
                self.log_result(f"CRITICAL ERROR: Failed to create malicious log Excel file: {e}", "red")
        else:
            self.log_result(f"Malicious detections log found at: {MALICIOUS_LOG_FILE}", "blue")

    def _log_malicious_entry(self, file_path, file_hash, threat_details, scan_type):
        """Logs a detected malicious entry to the Excel file."""
        try:
            wb = load_workbook(MALICIOUS_LOG_FILE)
            ws = wb["Malicious Files"]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [timestamp, file_path, file_hash, threat_details, scan_type]
            ws.append(row_data)
            wb.save(MALICIOUS_LOG_FILE)
            self.log_result(f"Logged malicious entry to Excel: {os.path.basename(file_path)}", "red")
        except Exception as e:
            self.log_result(f"ERROR: Failed to log malicious entry to Excel for {os.path.basename(file_path)}: {e}", "orange")

    def load_scan_history(self):
        """Loads scan history from JSON file."""
        if os.path.exists(self.scan_history_file):
            try:
                with open(self.scan_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                self.log_result(f"Loaded scan history: {len(history.get('usbs', []))} USBs, {len(history.get('files', []))} files.", color="blue")
                return history
            except json.JSONDecodeError as e:
                self.log_result(f"Error decoding scan history JSON: {e}. Starting with empty history.", color="orange")
                return {"usbs": [], "files": []}
            except Exception as e:
                self.log_result(f"Unexpected error loading scan history: {e}. Starting with empty history.", color="orange")
                return {"usbs": [], "files": []}
        return {"usbs": [], "files": []}

    def save_scan_history(self):
        """Saves scan history to JSON file."""
        try:
            with open(self.scan_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.scan_history, f, indent=4)
            self.log_result("Scan history saved.", color="blue")
        except Exception as e:
            self.log_result(f"Error saving scan history: {e}", "red")

    def get_usb_identifier(self, drive_path):
        """Generates a unique identifier for a USB drive based on OS."""
        try:
            if platform.system() == "Windows" and win32api:
                volume_info = win32api.GetVolumeInformation(drive_path.rstrip('\\') + '\\')
                serial_number = volume_info[1]
                return f"WIN_{drive_path}_{serial_number}"
            elif os.path.exists(drive_path):
                stat = os.statvfs(drive_path)
                total_size_bytes = stat.f_blocks * stat.f_bsize
                return f"GENERIC_{drive_path}_{total_size_bytes}"
            return f"UNKNOWN_{drive_path}"
        except Exception as e:
            return f"FALLBACK_ID_{drive_path}"

    def is_usb_already_scanned(self, drive_path):
        """Checks if a USB drive has been scanned recently based on its identifier."""
        usb_id = self.get_usb_identifier(drive_path)
        return usb_id in self.scanned_usb_identifiers

    def add_scanned_usb(self, drive_path, threats_found):
        """Adds a USB drive to the scanned history with its scan results."""
        usb_id = self.get_usb_identifier(drive_path)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.scan_history['usbs'] = [u for u in self.scan_history.get('usbs', []) if u['path_id'] != usb_id]
        self.scan_history.setdefault('usbs', []).append({
            "path": drive_path,
            "path_id": usb_id,
            "timestamp": timestamp,
            "type": "USB",
            "threats_found": threats_found
        })
        self.scanned_usb_identifiers.add(usb_id)
        self.save_scan_history()
        self.log_result(f"USB Scanned: {os.path.basename(drive_path)} (Threats: {threats_found}) recorded in history.", color="blue")

    def get_file_hash(self, file_path, hash_algo='sha256'):
        """Generates hash for a file's content."""
        hasher = hashlib.new(hash_algo)
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            return None
        except PermissionError:
            self.log_result(f"Permission denied to hash file: {os.path.basename(file_path)}", "orange")
            return None
        except Exception as e:
            self.log_result(f"Error hashing file {os.path.basename(file_path)}: {e}", "orange")
            return None

    def is_file_already_scanned(self, file_path):
        """Checks if a file (by content hash) has been scanned."""
        file_hash = self.get_file_hash(file_path)
        if file_hash:
            return file_hash in self.scanned_file_hashes
        return False

    def add_scanned_file_hash(self, file_path, is_malicious):
        """Adds a file's hash to the scanned history."""
        file_hash = self.get_file_hash(file_path)
        if file_hash:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            # Remove old entry if exists to update timestamp/status
            self.scan_history['files'] = [f for f in self.scan_history.get('files', []) if f['hash'] != file_hash]
            self.scan_history.setdefault('files', []).append({
                "path": file_path,
                "hash": file_hash,
                "timestamp": timestamp,
                "type": "File",
                "malicious": is_malicious
            })
            self.scanned_file_hashes.add(file_hash)
            self.save_scan_history()
            self.log_result(f"File: {os.path.basename(file_path)} (Malicious: {is_malicious}) recorded in history.", color="blue")

    def load_yara_rules(self, rules_file):
        """Loads YARA rules from the specified file."""
        if yara:
            try:
                self.rules = yara.compile(filepath=rules_file)
                self.log_result(f"YARA rules loaded from {rules_file}", "green")
            except yara.Error as e:
                self.log_result(f"Error loading YARA rules from {rules_file}: {e}", "red")
                self.rules = None
        else:
            self.log_result("YARA library not available. Cannot load rules.", "orange")

    def _display_scan_popup(self, is_malicious):
        """Displays a red or green popup with the specified messages."""
        if is_malicious:
            messagebox.showerror("Scan Result", "STOP! File is malicious.", icon="warning")
        else:
            messagebox.showinfo("Scan Result", "GO AHEAD! File is not malicious.", icon="info")

    def _scan_file_thread(self, file_path, source="Manual Scan", show_action_popup=True):
        """Performs file scanning in a separate thread."""
        if self.stop_scan_flag:
            self.log_result(f"Scan of {os.path.basename(file_path)} skipped due to stop flag.", "orange")
            return
        
        if not os.path.exists(file_path):
            self.log_result(f"File not found: {file_path}", "red")
            self.update_status_label(f"Scan failed: {os.path.basename(file_path)} not found.", COLOR_ERROR_RED)
            return

        self.update_status_label(f"Scanning: {os.path.basename(file_path)}", COLOR_PRIMARY_BLUE)
        self.log_result(f"Starting scan for: {os.path.basename(file_path)} (Source: {source})", "blue")
        
        is_malicious = False
        threat_details = []

        # 1. Hash check against dummy definitions
        hash_check_result = self.check_hash_definitions(file_path)
        if hash_check_result and hash_check_result["detected"]:
            is_malicious = True
            threat_details.append(f"Hash Match: {hash_check_result['details']}")
            self.log_result(f"Threat found by Hash: {hash_check_result['details']}", "red")

        # 2. YARA scan
        yara_matches = self.scan_file_with_yara(file_path)
        if yara_matches:
            is_malicious = True
            match_names = ", ".join([m.rule for m in yara_matches])
            threat_details.append(f"YARA Match: {match_names}")
            self.log_result(f"Threat found by YARA: {match_names}", "red")

        # 3. VirusTotal scan (only if not already detected by local methods, or if deeper scan is needed)
        # You might want to adjust this logic based on how aggressive you want the VT scan to be.
        # For simplicity, if not already malicious by hash/yara, then check VT.
        vt_result = None # Initialize vt_result outside the if block
        if not is_malicious: # Only call VT if not already found malicious by local checks
            vt_result = self.scan_file_with_virustotal(file_path)
            if vt_result and vt_result["detected"]:
                is_malicious = True
                threat_details.append(f"VirusTotal: {vt_result['details']}")
                self.log_result(f"Threat found by VirusTotal: {vt_result['details']}", "red")
            elif vt_result and not vt_result["detected"]:
                self.log_result(f"VirusTotal scan for {os.path.basename(file_path)}: Clean.", "green")
            else:
                self.log_result(f"VirusTotal scan for {os.path.basename(file_path)}: Could not complete or no definitive result.", "orange")
        
        # Update counters and history
        self.files_scanned += 1
        if is_malicious:
            self.threats_found += 1
            threat_summary = "; ".join(threat_details)
            self._log_malicious_entry(file_path, self.get_file_hash(file_path), threat_summary, source)
            self.log_result(f"File: {os.path.basename(file_path)} is MALICIOUS! Details: {threat_summary}", "red")
            self.update_status_label(f"MALICIOUS: {os.path.basename(file_path)}!", COLOR_ERROR_RED)
            
            self._display_scan_popup(True) # Show red popup
            if show_action_popup: # Still provide quarantine/delete options after popup
                response = messagebox.askyesno(
                    "Malicious File Detected!",
                    f"File '{os.path.basename(file_path)}' detected as MALICIOUS!\n\n"
                    f"Details: {threat_summary}\n\n"
                    f"Do you want to Quarantine it (Yes) or Delete it (No)?\n"
                    f"Cancel to do nothing."
                )
                if response is True:
                    self.quarantine_file(file_path, threat_summary)
                elif response is False:
                    self.delete_file(file_path)
        else:
            self.log_result(f"File: {os.path.basename(file_path)} is CLEAN.", "green")
            self.update_status_label(f"CLEAN: {os.path.basename(file_path)}", COLOR_ACCENT_GREEN)
            self._display_scan_popup(False) # Show green popup
        
        self.add_scanned_file_hash(file_path, is_malicious) # Record scan result in history
        self.update_scan_info()

    def start_scan_thread(self, file_path, source="Manual Scan", show_action_popup=True):
        """Starts a file scan in a new thread."""
        if self.running_scan_thread and self.running_scan_thread.is_alive():
            self.log_result("Another scan is already in progress. Please wait.", "orange")
            messagebox.showwarning("Scan in Progress", "Another scan is already running. Please wait for it to complete.")
            return
        
        self.stop_scan_flag = False
        self.running_scan_thread = threading.Thread(target=self._scan_file_thread, args=(file_path, source, show_action_popup), daemon=True)
        self.running_scan_thread.start()
        self.log_result(f"Scan thread started for {os.path.basename(file_path)}", "blue")
        self.update_status_label("Scan in progress...", COLOR_WARNING_ORANGE)

    def scan_selected_file(self):
        """Opens a file dialog for the user to select a file for scanning."""
        file_path = filedialog.askopenfilename(
            title="Select File to Scan",
            filetypes=[("All Files", "*.*")]
        )
        if file_path:
            self.start_scan_thread(file_path, source="Manual File Scan", show_action_popup=True)
        else:
            self.log_result("File scan cancelled.", "orange")

    def quarantine_file(self, file_path, reason="Detected as malicious"):
        """Moves a detected malicious file to a quarantine directory."""
        if not os.path.exists(QUARANTINE_DIR):
            os.makedirs(QUARANTINE_DIR)
        
        file_name = os.path.basename(file_path)
        quarantine_path = os.path.join(QUARANTINE_DIR, file_name)

        # Handle case where file with same name already exists in quarantine
        counter = 1
        original_quarantine_path = quarantine_path
        while os.path.exists(quarantine_path):
            name, ext = os.path.splitext(file_name)
            quarantine_path = os.path.join(QUARANTINE_DIR, f"{name}_{counter}{ext}")
            counter += 1

        try:
            shutil.move(file_path, quarantine_path)
            self.log_result(f"Quarantined malicious file: {file_name} to {quarantine_path} (Reason: {reason})", "red")
            return True
        except FileNotFoundError:
            self.log_result(f"Error quarantining {file_name}: File not found.", "orange")
        except PermissionError:
            self.log_result(f"Error quarantining {file_name}: Permission denied. Run as administrator.", "red")
        except Exception as e:
            self.log_result(f"Error quarantining {file_name}: {e}", "red")
        return False

    def delete_file(self, file_path):
        """Deletes a detected malicious file permanently."""
        try:
            os.remove(file_path)
            self.log_result(f"Deleted malicious file: {file_path}", "red")
            return True
        except FileNotFoundError:
            self.log_result(f"Error deleting {file_path}: File not found.", "orange")
        except PermissionError:
            self.log_result(f"Error deleting {file_path}: Permission denied. Run as administrator.", "red")
        except Exception as e:
            self.log_result(f"Error deleting {file_path}: {e}", "red")
        return False

    def scan_file_with_yara(self, file_path):
        """Scans a file using loaded YARA rules."""
        if not yara or not self.rules:
            self.log_result("YARA rules not loaded or YARA not installed. Skipping YARA scan.", "orange")
            return []
        try:
            matches = self.rules.match(filepath=file_path)
            if matches:
                self.log_result(f"YARA detected threats in {os.path.basename(file_path)}: {', '.join([m.rule for m in matches])}", "red")
                return matches
        except yara.Error as e:
            self.log_result(f"YARA scan error for {os.path.basename(file_path)}: {e}", "orange")
        except Exception as e:
            self.log_result(f"Unexpected error during YARA scan for {os.path.basename(file_path)}: {e}", "orange")
        return []

    def scan_file_with_virustotal(self, file_path):
        """Submits a file to VirusTotal for analysis and retrieves the report."""
        if not VIRUSTOTAL_API_KEY:
            self.log_result("VirusTotal API Key not configured. Skipping VirusTotal scan.", "orange")
            return {"detected": False, "details": "API Key not set"}

        try:
            self.log_result(f"Submitting {os.path.basename(file_path)} to VirusTotal...", "blue")
            
            # First, check if the file has been scanned before using its hash
            file_hash = self.get_file_hash(file_path)
            if not file_hash:
                return {"detected": False, "details": "Could not get file hash."}

            headers = {
                "x-apikey": VIRUSTOTAL_API_KEY
            }
            
            # Check for existing report
            report_url = f"{VIRUSTOTAL_API_URL}/{file_hash}"
            response = requests.get(report_url, headers=headers, timeout=10)
            response.raise_for_status()
            report_data = response.json()

            if report_data and report_data.get('data'):
                attributes = report_data['data']['attributes']
                last_analysis_stats = attributes.get('last_analysis_stats', {})
                malicious_count = last_analysis_stats.get('malicious', 0) + last_analysis_stats.get('suspicious', 0)
                
                if malicious_count > 0:
                    self.log_result(f"VirusTotal report found for {os.path.basename(file_path)}: MALICIOUS (Detections: {malicious_count})", "red")
                    return {"detected": True, "details": f"VirusTotal Detections: {malicious_count}"}
                else:
                    self.log_result(f"VirusTotal report found for {os.path.basename(file_path)}: CLEAN", "green")
                    return {"detected": False, "details": "Clean"}
            else:
                self.log_result(f"No existing VirusTotal report for {os.path.basename(file_path)}. Uploading for analysis...", "blue")
                # If no report exists, upload the file
                with open(file_path, "rb") as f:
                    files = {"file": (os.path.basename(file_path), f)}
                    upload_response = requests.post(VIRUSTOTAL_API_URL, headers=headers, files=files, timeout=60)
                    upload_response.raise_for_status()
                    upload_data = upload_response.json()
                    
                    if upload_data and upload_data.get('data') and upload_data['data'].get('id'):
                        analysis_id = upload_data['data']['id']
                        self.log_result(f"File uploaded to VirusTotal. Analysis ID: {analysis_id}. Waiting for report...", "blue")
                        
                        # Poll for the report
                        for _ in range(10): # Try polling 10 times
                            time.sleep(VIRUSTOTAL_SCAN_INTERVAL) # Wait before polling again
                            analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
                            analysis_response = requests.get(analysis_url, headers=headers, timeout=10)
                            analysis_response.raise_for_status()
                            analysis_data = analysis_response.json()
                            
                            if analysis_data.get('data') and analysis_data['data'].get('attributes', {}).get('status') == 'completed':
                                stats = analysis_data['data']['attributes']['stats']
                                malicious_count = stats.get('malicious', 0) + stats.get('suspicious', 0)
                                if malicious_count > 0:
                                    self.log_result(f"VirusTotal analysis completed: MALICIOUS (Detections: {malicious_count})", "red")
                                    return {"detected": True, "details": f"VirusTotal Detections: {malicious_count}"}
                                else:
                                    self.log_result(f"VirusTotal analysis completed: CLEAN", "green")
                                    return {"detected": False, "details": "Clean"}
                            elif analysis_data.get('data') and analysis_data['data'].get('attributes', {}).get('status') == 'queued':
                                self.log_result(f"VirusTotal analysis for {os.path.basename(file_path)} is still queued...", "blue")
                            else:
                                self.log_result(f"VirusTotal analysis for {os.path.basename(file_path)} status: {analysis_data.get('data', {}).get('attributes', {}).get('status', 'unknown')}", "orange")
                        
                        self.log_result(f"VirusTotal analysis timed out for {os.path.basename(file_path)}.", "orange")
                        return {"detected": False, "details": "Analysis timed out"}
                    else:
                        self.log_result(f"Failed to upload file to VirusTotal: {upload_response.status_code} - {upload_response.text}", "red")
                        return {"detected": False, "details": "Upload failed"}
        except requests.exceptions.RequestException as e:
            self.log_result(f"Network error during VirusTotal scan for {os.path.basename(file_path)}: {e}", "orange")
            return {"detected": False, "details": f"Network Error: {e}"}
        except json.JSONDecodeError:
            self.log_result(f"Invalid JSON response from VirusTotal for {os.path.basename(file_path)}.", "orange")
            return {"detected": False, "details": "Invalid VT response"}
        except Exception as e:
            self.log_result(f"An unexpected error occurred during VirusTotal scan for {os.path.basename(file_path)}: {e}", "red")
            return {"detected": False, "details": f"Unexpected Error: {e}"}

    def check_hash_definitions(self, file_path):
        """Checks file hash against dummy virus and trusted definitions."""
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return {"detected": False, "details": "Could not get file hash."}

        if file_hash in dummy_virus_definitions:
            return {"detected": True, "details": dummy_virus_definitions[file_hash]}
        elif file_hash in dummy_trusted_files:
            return {"detected": False, "details": dummy_trusted_files[file_hash], "trusted": True}
        else:
            return {"detected": False, "details": "No direct hash match."}

    def stop_scan(self):
        """Sets a flag to stop the currently running scan thread."""
        self.stop_scan_flag = True
        self.download_monitor_stop_flag = True # Also stop download monitor
        self.usb_monitor_stop_flag = True # Also stop USB monitor
        self.qr_camera_running = False # Stop QR camera if running
        self.update_status_label("Scan stopped by user.", COLOR_WARNING_ORANGE)
        self.log_result("Scan and monitoring stopped by user.", "orange")

    def view_scan_logs(self):
        """Opens a new window to display scan logs."""
        log_popup = Toplevel(self)
        log_popup.title("Scan Logs")
        log_popup.geometry("600x400")
        log_popup.transient(self) # Set to be on top of the main window
        log_popup.grab_set() # Make it modal

        text_widget = scrolledtext.ScrolledText(
            log_popup,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="black",
            fg="white",
            insertbackground="white"
        )
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Configure tags for colors
        text_widget.tag_config("red", foreground=COLOR_ERROR_RED)
        text_widget.tag_config("green", foreground=COLOR_ACCENT_GREEN)
        text_widget.tag_config("blue", foreground=COLOR_PRIMARY_BLUE)
        text_widget.tag_config("orange", foreground=COLOR_WARNING_ORANGE)
        text_widget.tag_config("black", foreground="white") # Default to white for black color

        # Insert existing logs
        for msg, color in self.log_messages:
            text_widget.insert(tk.END, msg + "\n", color)
        
        text_widget.configure(state='disabled') # Make it read-only
        self.log_popup_text_widget = text_widget # Store reference for real-time updates

        # Clear reference when window is closed
        def on_log_popup_close():
            self.log_popup_text_widget = None
            log_popup.destroy()
        log_popup.protocol("WM_DELETE_WINDOW", on_log_popup_close)

    def _monitor_downloads_thread(self):
        """Continuously monitors the downloads directory for new files."""
        self.log_result(f"Download monitor started for: {DOWNLOAD_MONITOR_DIR}", "blue")
        last_checked_files = set(os.listdir(DOWNLOAD_MONITOR_DIR)) if os.path.exists(DOWNLOAD_MONITOR_DIR) else set()
        
        # Add initially existing files to processed_download_files to prevent immediate scan
        for f in last_checked_files:
            full_path = os.path.join(DOWNLOAD_MONITOR_DIR, f)
            if os.path.isfile(full_path):
                self.processed_download_files.add(full_path)


        while not self.download_monitor_stop_flag:
            try:
                if not os.path.exists(DOWNLOAD_MONITOR_DIR):
                    self.log_result(f"Download directory not found: {DOWNLOAD_MONITOR_DIR}. Retrying...", "orange")
                    time.sleep(5)
                    continue

                current_files = set(os.listdir(DOWNLOAD_MONITOR_DIR))
                new_files = current_files - last_checked_files

                for file_name in new_files:
                    file_path = os.path.join(DOWNLOAD_MONITOR_DIR, file_name)
                    if os.path.isfile(file_path):
                        if file_path not in self.processed_download_files:
                            self.log_result(f"New file detected in downloads: {file_name}. Scanning...", "blue")
                            # It's crucial to run the scan in a *new* thread
                            # or ensure _scan_file_thread is non-blocking.
                            # Since _scan_file_thread already handles threading, we just call it.
                            self.start_scan_thread(file_path, source="Download Monitor", show_action_popup=True)
                            self.processed_download_files.add(file_path) # Mark as processed
                
                last_checked_files = current_files
                time.sleep(5) # Check every 5 seconds
            except Exception as e:
                self.log_result(f"Error in download monitor thread: {e}", "red")
                time.sleep(10) # Wait longer on error

    def start_download_monitor_thread(self):
        """Starts the download monitoring in a separate daemon thread."""
        if not self.download_monitor_thread or not self.download_monitor_thread.is_alive():
            self.download_monitor_stop_flag = False
            self.download_monitor_thread = threading.Thread(target=self._monitor_downloads_thread, daemon=True)
            self.download_monitor_thread.start()
        else:
            self.log_result("Download monitor is already running.", "blue")

    def _monitor_usb_thread(self):
        """Continuously monitors for USB drive connections and scans them."""
        self.log_result("USB monitor started.", "blue")
        known_drives = set(get_usb_drives())

        while not self.usb_monitor_stop_flag:
            try:
                current_drives = set(get_usb_drives())
                new_drives = current_drives - known_drives

                for drive_path in new_drives:
                    if not self.is_usb_already_scanned(drive_path):
                        self.log_result(f"New USB drive detected: {drive_path}. Starting scan...", "blue")
                        # Start a new thread for scanning the USB drive
                        threading.Thread(target=self._scan_usb_drive, args=(drive_path,), daemon=True).start()
                    else:
                        self.log_result(f"USB drive {drive_path} detected but already scanned recently. Skipping.", "blue")
                
                known_drives = current_drives
                time.sleep(10) # Check every 10 seconds
            except Exception as e:
                self.log_result(f"Error in USB monitor thread: {e}", "red")
                time.sleep(10) # Wait longer on error

    def start_usb_monitor_thread(self):
        """Starts the USB monitoring in a separate daemon thread."""
        if not self.usb_monitor_thread or not self.usb_monitor_thread.is_alive():
            self.usb_monitor_stop_flag = False
            self.usb_monitor_thread = threading.Thread(target=self._monitor_usb_thread, daemon=True)
            self.usb_monitor_thread.start()
        else:
            self.log_result("USB monitor is already running.", "blue")

    def _scan_usb_drive(self, drive_path):
        """Scans all files on a given USB drive."""
        self.update_status_label(f"Scanning USB: {drive_path}", COLOR_PRIMARY_BLUE)
        self.log_result(f"Starting full scan of USB drive: {drive_path}", "blue")
        threats_on_usb = 0
        total_files = 0

        for root, _, files in os.walk(drive_path):
            if self.stop_scan_flag:
                self.log_result(f"USB scan of {drive_path} interrupted.", "orange")
                break
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if not os.path.islink(file_path): # Avoid scanning symlinks repeatedly
                    try:
                        if os.path.isfile(file_path): # Ensure it's a file
                            total_files += 1
                            # Scan individual files on the USB drive
                            # Do not show immediate popups for every file on USB, aggregate results
                            # Use a separate thread for each file scan if needed, or make _scan_file_thread quick
                            # For simplicity, calling _scan_file_thread synchronously here,
                            # but in a real app, this might need more robust threading/queuing for UI responsiveness.
                            
                            # Check if file was already scanned based on hash
                            if not self.is_file_already_scanned(file_path):
                                self.log_result(f"Scanning file on USB: {os.path.basename(file_path)}", "blue")
                                # Run file scan in its own thread to prevent blocking USB enumeration
                                # and to allow individual popups for malicious files
                                file_scan_thread = threading.Thread(target=self._scan_file_thread, args=(file_path, "USB Scan", True), daemon=True)
                                file_scan_thread.start()
                                file_scan_thread.join(timeout=30) # Wait a bit for it to finish, or refine logic
                                
                                # Re-check self.threats_found after the file scan thread potentially updates it
                                # This is a simplification; a shared counter or queue would be more robust for totals.
                                if "MALICIOUS" in self.status_label.cget("text"): # Heuristic check
                                    threats_on_usb += 1
                            else:
                                self.log_result(f"File on USB: {os.path.basename(file_path)} already scanned. Skipping.", "blue")
                    except PermissionError:
                        self.log_result(f"Permission denied to access {file_path} on USB.", "orange")
                    except Exception as e:
                        self.log_result(f"Error accessing {file_path} on USB: {e}", "red")

        self.update_status_label(f"USB Scan of {drive_path} completed. Found {threats_on_usb} threats.", COLOR_ACCENT_GREEN)
        self.log_result(f"Finished full scan of USB drive: {drive_path}. Total files: {total_files}, Threats found: {threats_on_usb}.", "green")
        self.add_scanned_usb(drive_path, threats_on_usb) # Record scan result for the USB drive

    def start_usb_scan(self):
        """Initiates a manual scan of a connected USB drive."""
        usb_drives = get_usb_drives()
        if not usb_drives:
            messagebox.showinfo("No USB Drives", "No USB drives detected.")
            self.log_result("No USB drives found to scan.", "orange")
            self.update_status_label("No USB drives detected.", COLOR_WARNING_ORANGE)
            return

        # For simplicity, let's just pick the first detected USB drive
        # In a real application, you might want to present a list to the user.
        selected_drive = usb_drives[0] 
        self.log_result(f"User initiated scan for USB drive: {selected_drive}", "blue")

        if self.running_scan_thread and self.running_scan_thread.is_alive():
            messagebox.showwarning("Scan in Progress", "Another scan is already running. Please wait.")
            self.log_result("User attempted USB scan while another scan was in progress.", "orange")
            return

        self.stop_scan_flag = False
        self.running_scan_thread = threading.Thread(target=self._scan_usb_drive, args=(selected_drive,), daemon=True)
        self.running_scan_thread.start()

    def scan_qr_camera(self):
        """Starts real-time QR code scanning using the camera."""
        if cv2 is None:
            messagebox.showerror("Error", "OpenCV is not installed. QR code scanning is unavailable.")
            self.log_result("Attempted QR camera scan, but OpenCV is not installed.", "red")
            self.update_status_label("OpenCV missing for QR camera scan.", COLOR_ERROR_RED)
            return

        if self.qr_camera_running:
            self.log_result("QR camera already running.", "blue")
            messagebox.showinfo("Info", "QR camera is already active.")
            return

        self.qr_camera_running = True
        self.log_result("Starting QR camera scan...", "blue")
        self.update_status_label("QR camera active. Scan a QR code.", COLOR_PRIMARY_BLUE)

        # Start camera capture in a separate thread to not block GUI
        self.qr_camera_thread = threading.Thread(target=self._qr_camera_loop, daemon=True)
        self.qr_camera_thread.start()

    def _qr_camera_loop(self):
        """The main loop for QR code detection from camera feed."""
        self.cap = cv2.VideoCapture(0) # 0 for default camera
        if not self.cap.isOpened():
            self.log_result("Error: Could not open camera.", "red")
            self.update_status_label("Camera error. QR scan failed.", COLOR_ERROR_RED)
            self.qr_camera_running = False
            return

        self.qr_detector = cv2.QRCodeDetector()
        
        # Create a Toplevel window for camera feed
        camera_window = Toplevel(self)
        camera_window.title("QR Camera Feed")
        camera_window.protocol("WM_DELETE_WINDOW", lambda: self._stop_qr_camera(camera_window))
        
        # Use a CTkLabel to display the image
        self.camera_label = ctk.CTkLabel(camera_window)
        self.camera_label.pack(padx=10, pady=10)

        while self.qr_camera_running:
            ret, frame = self.cap.read()
            if not ret:
                self.log_result("Failed to grab frame from camera.", "orange")
                break

            decoded_text, points, _ = self.qr_detector.detectAndDecode(frame)

            if decoded_text:
                self.log_result(f"QR Code detected: {decoded_text}", "green")
                self.handle_qr_content(decoded_text)
                
                # Draw bounding box (optional, for visual feedback)
                if points is not None:
                    points = points[0].astype(int)
                    for i in range(len(points)):
                        pt1 = tuple(points[i])
                        pt2 = tuple(points[(i + 1) % len(points)])
                        cv2.line(frame, pt1, pt2, (0, 255, 0), 3) # Green bounding box

                # Stop camera after detection, or continue scanning
                self.qr_camera_running = False # Stop after first successful scan
                self._stop_qr_camera(camera_window)
                break
            
            # Convert frame for CTkinter display
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tk = ctk.CTkImage(img, size=(frame.shape[1], frame.shape[0])) # Maintain aspect ratio
            self.camera_label.configure(image=img_tk)
            self.camera_label.image = img_tk # Keep a reference

            camera_window.update_idletasks() # Update the Tkinter window

        self._stop_qr_camera(camera_window) # Ensure cleanup if loop exits
        self.log_result("QR Camera scan stopped.", "blue")
        self.update_status_label("QR camera inactive.", COLOR_TEXT_MUTED)

    def _stop_qr_camera(self, camera_window=None):
        """Stops the QR camera feed and releases resources."""
        self.qr_camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if camera_window and camera_window.winfo_exists():
            camera_window.destroy()
        self.log_result("QR Camera resources released.", "blue")

    def scan_qr_file(self):
        """Allows user to upload an image file containing a QR code."""
        if cv2 is None:
            messagebox.showerror("Error", "OpenCV is not installed. QR code scanning is unavailable.")
            self.log_result("Attempted QR file scan, but OpenCV is not installed.", "red")
            self.update_status_label("OpenCV missing for QR file scan.", COLOR_ERROR_RED)
            return

        file_path = filedialog.askopenfilename(
            title="Select Image with QR Code",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.log_result(f"Scanning QR from file: {os.path.basename(file_path)}", "blue")
            self.update_status_label(f"Scanning QR from {os.path.basename(file_path)}...", COLOR_PRIMARY_BLUE)
            
            try:
                img = cv2.imread(file_path)
                if img is None:
                    self.log_result(f"Error: Could not load image from {file_path}", "red")
                    messagebox.showerror("Error", "Could not load image file.")
                    self.update_status_label("QR file scan failed.", COLOR_ERROR_RED)
                    return
                
                qr_detector = cv2.QRCodeDetector()
                decoded_text, _, _ = qr_detector.detectAndDecode(img)

                if decoded_text:
                    self.log_result(f"QR Code detected from file: {decoded_text}", "green")
                    self.update_status_label("QR code scanned successfully!", COLOR_ACCENT_GREEN)
                    self.handle_qr_content(decoded_text)
                else:
                    self.log_result(f"No QR code found in file: {os.path.basename(file_path)}", "orange")
                    self.update_status_label("No QR code found.", COLOR_WARNING_ORANGE)
                    messagebox.showinfo("No QR Code", "No QR code found in the selected image.")
            except Exception as e:
                self.log_result(f"Error processing QR file: {e}", "red")
                self.update_status_label("QR file scan error.", COLOR_ERROR_RED)
                messagebox.showerror("Error", f"An error occurred during QR code processing: {e}")
        else:
            self.log_result("QR file scan cancelled.", "orange")

    def handle_qr_content(self, content):
        """Processes the content decoded from a QR code."""
        if content.startswith("http://") or content.startswith("https://"):
            self.log_result(f"QR Code contained URL: {content}. Initiating URL scan.", "blue")
            # Directly call URL check function, removing the option to open in browser.
            self._perform_url_check(content) 
        elif os.path.exists(content) and os.path.isfile(content):
            response = messagebox.askyesno(
                "QR Code File Path Detected",
                f"A local file path was detected:\n\n{content}\n\nDo you want to scan this file?"
            )
            if response:
                self.start_scan_thread(content, source="QR Code File Path", show_action_popup=True)
            else:
                self.log_result(f"User chose not to scan file from QR code path: {content}", "orange")
        else:
            messagebox.showinfo("QR Code Content", f"QR Code content:\n\n{content}")
            self.log_result(f"QR Code contained plain text: {content}", "blue")


    def analyze_file_zip(self):
        """Opens a file dialog for the user to select a file or ZIP for analysis."""
        file_path = filedialog.askopenfilename(
            title="Select File or ZIP to Analyze",
            filetypes=[("All Files", "*.*"), ("ZIP Files", "*.zip")]
        )
        if file_path:
            if zipfile.is_zipfile(file_path):
                self.log_result(f"ZIP file selected for analysis: {os.path.basename(file_path)}", "blue")
                self.extract_and_scan_zip(file_path)
            else:
                self.log_result(f"File selected for analysis: {os.path.basename(file_path)}", "blue")
                self.start_scan_thread(file_path, source="Manual File/ZIP Scan", show_action_popup=True)
        else:
            self.log_result("File/ZIP analysis cancelled.", "orange")

    def extract_and_scan_zip(self, zip_path):
        """Extracts a ZIP file to a temporary directory and scans its contents."""
        self.update_status_label(f"Extracting and scanning ZIP: {os.path.basename(zip_path)}", COLOR_PRIMARY_BLUE)
        self.log_result(f"Attempting to extract ZIP: {zip_path}", "blue")

        if os.path.exists(TEMP_EXTRACT_DIR):
            try:
                shutil.rmtree(TEMP_EXTRACT_DIR)
                self.log_result(f"Cleared existing temporary extraction directory: {TEMP_EXTRACT_DIR}", "blue")
            except Exception as e:
                self.log_result(f"Warning: Could not clear temp extraction directory {TEMP_EXTRACT_DIR}: {e}", "orange")
                # Continue anyway, extraction might still work if it's empty or can overwrite

        try:
            os.makedirs(TEMP_EXTRACT_DIR, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Security consideration: Validate filenames within the ZIP to prevent path traversal
                for member in zip_ref.namelist():
                    if not member.startswith('/') and '..' not in member: # Basic check
                        zip_ref.extract(member, TEMP_EXTRACT_DIR)
                        extracted_file_path = os.path.join(TEMP_EXTRACT_DIR, member)
                        if os.path.isfile(extracted_file_path):
                            self.log_result(f"Extracted: {member}. Scanning...", "blue")
                            # Scan each extracted file
                            self.start_scan_thread(extracted_file_path, source=f"ZIP: {os.path.basename(zip_path)}", show_action_popup=False) # No popup per file
                        else:
                            self.log_result(f"Extracted directory: {member}. Skipping scan.", "blue")
            
            self.log_result(f"Finished extracting and queuing scans for ZIP: {os.path.basename(zip_path)}", "green")
            self.update_status_label(f"ZIP {os.path.basename(zip_path)} extracted and scans initiated.", COLOR_ACCENT_GREEN)
            messagebox.showinfo("ZIP Scan", f"ZIP file '{os.path.basename(zip_path)}' extracted and its contents are being scanned in the background.")
        
        except zipfile.BadZipFile:
            self.log_result(f"Error: {zip_path} is not a valid ZIP file.", "red")
            self.update_status_label("Invalid ZIP file.", COLOR_ERROR_RED)
            messagebox.showerror("ZIP Error", "The selected file is not a valid ZIP archive.")
        except Exception as e:
            self.log_result(f"Error extracting or scanning ZIP {zip_path}: {e}", "red")
            self.update_status_label("ZIP extraction/scan failed.", COLOR_ERROR_RED)
            messagebox.showerror("ZIP Error", f"An error occurred during ZIP processing: {e}")
        finally:
            # Clean up temporary directory after a delay or upon application exit
            # For immediate cleanup, uncommenting below will remove files quickly,
            # potentially before scans complete if not properly threaded/managed.
            # It's better to clean on app exit as implemented in close_application.
            pass


    def check_url(self):
        """Checks the entered URL using VirusTotal API."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL to check.")
            self.log_result("URL check attempted with empty URL.", "orange")
            return
        
        self.log_result(f"Checking URL: {url}", "blue")
        self.update_status_label(f"Checking URL: {url}", COLOR_PRIMARY_BLUE)

        if not VIRUSTOTAL_API_KEY:
            self.log_result("VirusTotal API Key not configured. Cannot check URL.", "red")
            self.update_status_label("VirusTotal API Key missing.", COLOR_ERROR_RED)
            messagebox.showerror("API Key Missing", "VirusTotal API Key is not configured. Cannot check URLs.")
            return

        # Use a thread for URL check to keep GUI responsive
        threading.Thread(target=self._perform_url_check, args=(url,), daemon=True).start()

    def _perform_url_check(self, url):
        """Performs the actual URL check with VirusTotal in a separate thread."""
        try:
            headers = {
                "x-apikey": VIRUSTOTAL_API_KEY,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # URL encode the URL for the API request
            encoded_url = urllib.parse.quote(url, safe='')
            
            # First, get a report if it exists
            report_url = f"https://www.virustotal.com/api/v3/urls/{hashlib.sha256(url.encode()).hexdigest()}"
            response = requests.get(report_url, headers=headers, timeout=10)
            response.raise_for_status()
            report_data = response.json()

            if report_data and report_data.get('data'):
                attributes = report_data['data']['attributes']
                last_analysis_stats = attributes.get('last_analysis_stats', {})
                malicious_count = last_analysis_stats.get('malicious', 0) + last_analysis_stats.get('suspicious', 0)
                
                if malicious_count > 0:
                    self.log_result(f"URL: {url} is MALICIOUS! Detections: {malicious_count}", "red")
                    self.update_status_label(f"MALICIOUS URL: {url}", COLOR_ERROR_RED)
                    messagebox.showerror("URL Scan Result", f"DANGER! The URL is MALICIOUS!\n\nDetails: {malicious_count} detections.")
                else:
                    self.log_result(f"URL: {url} is CLEAN.", "green")
                    self.update_status_label(f"CLEAN URL: {url}", COLOR_ACCENT_GREEN)
                    messagebox.showinfo("URL Scan Result", "SAFE! The URL is not malicious.")
            else:
                self.log_result(f"No existing VirusTotal report for URL: {url}. Submitting for analysis...", "blue")
                # If no report, submit the URL for analysis
                post_data = f"url={encoded_url}"
                submission_response = requests.post("https://www.virustotal.com/api/v3/urls", headers=headers, data=post_data, timeout=10)
                submission_response.raise_for_status()
                submission_data = submission_response.json()
                
                if submission_data and submission_data.get('data') and submission_data['data'].get('id'):
                    analysis_id = submission_data['data']['id']
                    self.log_result(f"URL submitted to VirusTotal. Analysis ID: {analysis_id}. Waiting for report...", "blue")
                    self.update_status_label("URL analysis in progress...", COLOR_WARNING_ORANGE)

                    # Poll for the report
                    for _ in range(10): # Try polling 10 times
                        time.sleep(VIRUSTOTAL_SCAN_INTERVAL) # Wait before polling again
                        analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
                        analysis_response = requests.get(analysis_url, headers=headers, timeout=10)
                        analysis_response.raise_for_status()
                        analysis_data = analysis_response.json()
                        
                        if analysis_data.get('data') and analysis_data['data'].get('attributes', {}).get('status') == 'completed':
                            stats = analysis_data['data']['attributes']['stats']
                            malicious_count = stats.get('malicious', 0) + stats.get('suspicious', 0)
                            if malicious_count > 0:
                                self.log_result(f"URL analysis completed: MALICIOUS (Detections: {malicious_count})", "red")
                                self.update_status_label(f"MALICIOUS URL: {url}", COLOR_ERROR_RED)
                                messagebox.showerror("URL Scan Result", f"DANGER! The URL is MALICIOUS!\n\nDetails: {malicious_count} detections.")
                            else:
                                self.log_result(f"URL analysis completed: CLEAN", "green")
                                self.update_status_label(f"CLEAN URL: {url}", COLOR_ACCENT_GREEN)
                                messagebox.showinfo("URL Scan Result", "SAFE! The URL is not malicious.")
                            return
                        elif analysis_data.get('data') and analysis_data['data'].get('attributes', {}).get('status') == 'queued':
                            self.log_result(f"URL analysis for {url} is still queued...", "blue")
                        else:
                            self.log_result(f"URL analysis for {url} status: {analysis_data.get('data', {}).get('attributes', {}).get('status', 'unknown')}", "orange")
                    
                    self.log_result(f"URL analysis timed out for {url}.", "orange")
                    self.update_status_label("URL analysis timed out.", COLOR_WARNING_ORANGE)
                    messagebox.showwarning("URL Scan Result", "Could not get a definitive scan result for the URL within the timeout period.")
                else:
                    self.log_result(f"Failed to submit URL to VirusTotal: {submission_response.status_code} - {submission_response.text}", "red")
                    self.update_status_label("URL submission failed.", COLOR_ERROR_RED)
                    messagebox.showerror("URL Scan Error", "Failed to submit URL for analysis.")
        
        except requests.exceptions.RequestException as e:
            self.log_result(f"Network error during URL scan for {url}: {e}", "red")
            self.update_status_label("URL scan network error.", COLOR_ERROR_RED)
            messagebox.showerror("Network Error", f"Could not connect to VirusTotal. Please check your internet connection. Error: {e}")
        except json.JSONDecodeError:
            self.log_result(f"Invalid JSON response from VirusTotal for URL: {url}.", "red")
            self.update_status_label("Invalid VT response.", COLOR_ERROR_RED)
            messagebox.showerror("API Error", "Received an invalid response from VirusTotal.")
        except Exception as e:
            self.log_result(f"An unexpected error occurred during URL scan for {url}: {e}", "red")
            self.update_status_label("URL scan failed.", COLOR_ERROR_RED)
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            self.url_entry.delete(0, tk.END) # Clear the entry field


    def close_application(self):
        """Stops all monitoring threads and closes the application."""
        self.log_result("Closing application. Stopping all background tasks...", "blue")
        self.stop_scan_flag = True
        self.download_monitor_stop_flag = True
        self.usb_monitor_stop_flag = True
        self.qr_camera_running = False
        
        # Wait for threads to finish (optional, for cleaner shutdown)
        if self.running_scan_thread and self.running_scan_thread.is_alive():
            self.running_scan_thread.join(timeout=2)
        if self.download_monitor_thread and self.download_monitor_thread.is_alive():
            self.download_monitor_thread.join(timeout=2)
        if self.usb_monitor_thread and self.usb_monitor_thread.is_alive():
            self.usb_monitor_thread.join(timeout=2)
        if self.qr_camera_thread and self.qr_camera_thread.is_alive():
            self.qr_camera_thread.join(timeout=2)

        # Clean up temporary directory
        if os.path.exists(TEMP_EXTRACT_DIR):
            try:
                shutil.rmtree(TEMP_EXTRACT_DIR)
                self.log_result(f"Cleaned up temporary extraction directory: {TEMP_EXTRACT_DIR}", "blue")
            except Exception as e:
                self.log_result(f"Error cleaning up temporary directory {TEMP_EXTRACT_DIR}: {e}", "orange")
        
        self.destroy() # Close the main application window

if __name__ == "__main__":
    app = AdvancedSecurityAnalyzer()
    app.mainloop()