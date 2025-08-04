# All_In_One_App.py (Final Version with All Suites, Error Logging & Embedded Firebase Login)
# Version 9.6 - Enhanced Video Suite with an option to enable/disable video overlay, improving user workflow flexibility.
# ==============================================================================
# Imports
# ==============================================================================
import sys
import os
import re
import asyncio
import random
import logging
import json
import shutil
import tempfile
import subprocess
import textwrap
import glob
import traceback
from urllib.parse import quote, urlencode
from datetime import timedelta, datetime

# --- Core PyQt5 Imports ---
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QFormLayout, QScrollArea, QMessageBox, QTabWidget, QGroupBox,
    QFileDialog, QCheckBox, QGridLayout, QProgressBar, QListWidget, QListWidgetItem,
    QSlider, QColorDialog, QStatusBar, QFrame, QInputDialog, QStyle,
    QDialog, QDialogButtonBox, QAction
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QProcess, QSettings

# --- Third-party libraries ---
import numpy as np
from PIL import Image
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import pysubs2
import configparser
import cloudscraper
from playwright.async_api import async_playwright
try:
    from playwright_stealth.stealth import stealth_async
except ImportError:
    from playwright_stealth import stealth_async
import qasync
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# --- Firebase Login Imports ---
import pyrebase
from requests.exceptions import HTTPError

# --- Imports for ProEditor Suite ---
try: from faster_whisper import WhisperModel
except ImportError: print("Warning: 'faster-whisper' not found. Transcription may not work. Run: pip install faster-whisper")
try: import edge_tts
except ImportError: print("Warning: 'edge-tts' not found. TTS functionality will not work. Run: pip install edge-tts")


# ==============================================================================
# Path Configuration for Packaged Executables & Data Files
# ==============================================================================
# Determine the base directory for the application, whether running as a script or a frozen executable.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Define Core Directories ---
# DATA_DIR: For user-managed files like configs, keys, and icons.
DATA_DIR = os.path.join(BASE_DIR, 'data')
# FILE_DIR: For application-specific executables like HandBrakeCLI and ffmpeg.
FILE_DIR = os.path.join(BASE_DIR, 'file')

# --- Define Full Paths for Data Files ---
ICON_PATH = os.path.join(DATA_DIR, 'icon.png')
PODCAST_CONFIG_FILE = os.path.join(DATA_DIR, 'config.ini')
LAST_KEY_FILE = os.path.join(DATA_DIR, 'last_key.txt')
# Path for config.json is defined but not used in the current script logic.
CONFIG_JSON_FILE = os.path.join(DATA_DIR, 'config.json')


# --- Critical Directory Existence Checks ---
# Check for 'data' directory
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        app_temp = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.information(None, "Data Folder Created", f"The required 'data' directory was not found and has been created at:\n{DATA_DIR}\n\nPlease add your 'config.ini' and other data files there.")
    except OSError as e:
        app_temp = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal Error", f"Could not create the required 'data' directory at:\n{DATA_DIR}\n\nPlease create it manually.\nError: {e}")
        sys.exit(1)

# Check for 'file' directory
if not os.path.exists(FILE_DIR):
    try:
        os.makedirs(FILE_DIR)
    except OSError as e:
        app_temp = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal Error", f"Could not create the required 'file' directory at:\n{FILE_DIR}\n\nPlease create it manually.\nError: {e}")
        sys.exit(1)

# ==============================================================================
# Configurations and Loggers
# ==============================================================================
styles = {
    'no-style': ('high quality, sharp focus, clear image', 'blurry, low quality, ugly, deformed, text'),
    'Cinematic (Default)': ('cinematic shot, dynamic lighting, 75mm, Technicolor, Panavision, cinemascope, sharp focus, fine details, 8k, HDR, realism, realistic, key visual, film still, superb cinematic color grading, depth of field', 'bad lighting, low-quality, deformed, text, poorly drawn, camera, bad art, boring, low-resolution, disfigured, cartoon, anime'),
    'Humorous Vector Cartoon': ('Full-color, humorous style with clean vector lines, expressive faces, and bold cartoon shading', ''),
    'Stylized Comic Art': ('Full color, stylized comic art with clean outlines and funny expressions', ''),
    'Intense Comic Exaggeration': ('Full-color illustration with sharp contrasts, intense facial expressions, comic-style exaggeration', ''),
    'Slapstick Humor': ('Full-color, slapstick humor style with bold outlines and dynamic character motion', ''),
    'Comical Stylized Art': ('Bright full-color, comical expressions, stylized comic art', ''),
    'Playful Festive Comic': ('Bright full-color, festive rural setting, playful comic style', ''),
    'Rich Color Comic Exaggeration': ('Rich colors, comic exaggeration', ''),
    'Clean Cartoon Graphics': ('Golden fields, palm trees, and blue skies in the background. Full-color, funny faces, clean cartoon graphics', ''),
    'Classic Humor': ('Rich color, expressive faces, classic humor', ''),
    'Humorous Action Scene': ('Full-color action scene in humorous style', ''),
    'Warm Neighborhood Comic': ('Comic expressions and warm neighborhood feel', ''),
    'Bright Cartoon Style': ('Bright cartoon style, paint splashes, joyful expressions, old wooden monastery in background', ''),
    'Clean Lines & Bright Palette': ('Funny panic faces, green rice paddies and bamboo fence in background. Clean lines, bright color palette', ''),
    'Exaggerated Comic Reactions': ('Water splashes, surprised fish, exaggerated comic reactions. Blue water, lush riverbank', ''),
    'Spooky Comic Twist': ('Night colors, firelight glow, soft spooky atmosphere with comic twist', '')
}

class MyWordlist:
    def __init__(self):
        self.wordlist = ["Dragon", "Castle", "Moon", "Forest", "Apple", "Fish", "Green", "Banana", "Queen", "Inspiration", "River", "Mountain", "Sword", "Magic", "Crystal", "Star", "Ancient", "Forgotten", "Secret", "Whisper"]
    def get_prompt(self, number=10):
        if number > len(self.wordlist): number = len(self.wordlist)
        return ', '.join(random.sample(self.wordlist, number))

network_logger = logging.getLogger('request-logger')
if not network_logger.handlers:
    file_handler = logging.FileHandler('network-log.log', mode='w')
    network_formatter = logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S')
    file_handler.setFormatter(network_formatter)
    network_logger.addHandler(file_handler)
    network_logger.setLevel(logging.INFO)

info_logger = logging.getLogger('Image Generation')
if not info_logger.handlers:
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S')
    stdout_handler.setFormatter(formatter)
    info_logger.addHandler(stdout_handler)
    info_logger.setLevel(logging.INFO)

# ==============================================================================
# Firebase Login System
# ==============================================================================
class LoginDialog(QDialog):
    """A professional login dialog window."""
    def __init__(self, firebase_auth, parent=None):
        super().__init__(parent)
        self.firebase_auth = firebase_auth
        self.user_info = None
        self.setWindowTitle("User Login")
        # Set icon for the dialog if it exists
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        else:
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.setModal(True)
        self.setMinimumWidth(350)

        # --- Widgets ---
        layout = QVBoxLayout(self)
        self.status_label = QLabel("Please enter your credentials to continue.")
        self.status_label.setWordWrap(True)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.remember_me_checkbox = QCheckBox("Remember Me")
        self.remember_me_checkbox.setChecked(True) # Default to checked

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        layout.addWidget(self.status_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.remember_me_checkbox)

        # --- Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.handle_login)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # Connect return key to login attempt
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        if not email or not password:
            self.status_label.setText("<font color='red'>Email and Password cannot be empty.</font>")
            return

        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        ok_button.setEnabled(False)
        ok_button.setText("Signing in...")
        QApplication.processEvents() # Update UI

        try:
            self.user_info = self.firebase_auth.sign_in_with_email_and_password(email, password)
            if self.remember_me_checkbox.isChecked():
                # Save the refresh token for persistent login
                settings = QSettings("AIOApp", "Auth")
                settings.setValue("refreshToken", self.user_info['refreshToken'])
            
            self.status_label.setText("<font color='green'>Login Successful!</font>")
            self.accept() # Close dialog and return QDialog.Accepted

        except HTTPError as e:
            error_json = e.args[1]
            error_message = json.loads(error_json).get('error', {}).get('message', "UNKNOWN_ERROR")
            if error_message == "INVALID_LOGIN_CREDENTIALS":
                self.status_label.setText("<font color='red'>Invalid email or password. Please try again.</font>")
            elif "USER_NOT_FOUND" in error_message:
                 self.status_label.setText("<font color='red'>This user account does not exist.</font>")
            else:
                self.status_label.setText(f"<font color='red'>Error: {error_message}</font>")
        except Exception as e:
             # Handle network errors etc.
            self.status_label.setText(f"<font color='red'>A network error occurred: {e}</font>")
        finally:
            ok_button.setEnabled(True)
            ok_button.setText("OK")

    def get_user(self):
        """Returns user info if login was successful."""
        return self.user_info
        
# ==============================================================================
# AI Director and Image Gen Backend
# ==============================================================================
async def make_request_with_retries(scraper, url, params=None, retries=3, timeout=90):
    last_exception = None
    for attempt in range(retries):
        try:
            response = await asyncio.to_thread(scraper.get, url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except (cloudscraper.requests.exceptions.RequestException, cloudscraper.exceptions.CloudflareException) as e:
            last_exception = e
            info_logger.warning(f"Request failed: {e}. Retrying... (Attempt {attempt+1}/{retries})")
            await asyncio.sleep(5)
    raise Exception(f"Request failed after {retries} retries: {last_exception}")

async def get_url_data():
    info_logger.info("Launching stealth browser to find a new key...")
    found_key_container = []
    def handle_request(request):
        if "userKey=" in request.url and not found_key_container:
            key_match = re.search(r'userKey=([a-f\d]{64})', request.url)
            if key_match:
                key = key_match.group(1)
                info_logger.info(f"Success! Found key in network request: {key[:10]}...")
                found_key_container.append(key)
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await stealth_async(page)
            page.on("request", handle_request)
            info_logger.info("Navigating to Perchance website...")
            await page.goto('https://perchance.org/ai-text-to-image-generator', timeout=90000, wait_until='networkidle')
            info_logger.info("Waiting for iframe to appear...")
            iframe_element = await page.wait_for_selector('//iframe[@src]', timeout=30000)
            frame = await iframe_element.content_frame()
            info_logger.info("Waiting for the generate button to be ready...")
            generate_button_selector = '#generateButtonEl'
            await frame.wait_for_selector(generate_button_selector, timeout=30000)
            await asyncio.sleep(random.uniform(1.5, 3.0))
            info_logger.info("Simulating mouse hover over the generate button...")
            await frame.hover(generate_button_selector)
            await asyncio.sleep(random.uniform(0.5, 1.2))
            info_logger.info("Clicking the generate button to trigger key generation...")
            await frame.click(generate_button_selector)
            info_logger.info("Waiting for key to be captured (up to 30 seconds)...")
            for _ in range(30):
                if found_key_container:
                    break
                await asyncio.sleep(1)
            await browser.close()
            if found_key_container:
                return found_key_container[0]
            else:
                raise Exception("Could not automatically find a new key, even with stealth. The website has likely changed its security or structure.")
    except Exception as e:
        info_logger.error(f"The Playwright (stealth) process failed: {e}")
        raise

async def get_key():
    scraper = cloudscraper.create_scraper()
    # MODIFIED: Use the centrally defined path for last_key.txt
    key_file_path = LAST_KEY_FILE
    if os.path.exists(key_file_path):
        with open(key_file_path, 'r') as file:
            line = file.readline().strip()
            if line:
                info_logger.info(f"Verifying key from {os.path.basename(key_file_path)}...")
                verification_url = 'https://image-generation.perchance.org/api/checkVerificationStatus'
                params = {'userKey': line, '__cacheBust': random.uniform(0, 1)}
                try:
                    response = await make_request_with_retries(scraper, verification_url, params=params, retries=2, timeout=15)
                    if 'not_verified' not in response.text:
                        info_logger.info(f'Found working key {line[:10]}... in file.')
                        return line
                    else:
                        info_logger.info("Key from file is no longer valid.")
                except Exception as e:
                    info_logger.warning(f"Could not verify key: {e}")
    info_logger.info('Could not find a valid key locally. Attempting to fetch a new one online...')
    key = await get_url_data()
    with open(key_file_path, 'w') as file: file.write(key)
    info_logger.info(f'Found and saved new key: {key[:10]}...')
    return key

async def image_generator(base_filename='', amount=1, prompt='RANDOM', prompt_size=10, negative_prompt='', style='RANDOM', resolution='512x768', guidance_scale=7, callback=None, character_map=None):
    scraper = cloudscraper.create_scraper()
    prompt_base = MyWordlist().get_prompt(prompt_size) if not prompt or prompt == 'RANDOM' else prompt
    style_choice = style
    if style == 'RANDOM':
        available_styles = [s for s in styles.keys() if s != 'no-style']
        style_choice = random.choice(available_styles) if available_styles else 'no-style'
    if style_choice not in styles: raise Exception(f'Style choice {style_choice} was not recognized.')
    prompt_style, negative_prompt_style = styles[style_choice]

    if character_map:
        for char_name, char_desc in character_map.items():
            prompt_base = prompt_base.replace(char_name, char_desc)

    full_prompt = f'{prompt_base}, {prompt_style}' if prompt_style else prompt_base
    full_negative_prompt = f'{negative_prompt}, {negative_prompt_style}' if negative_prompt_style else negative_prompt
    info_logger.info(f'Generating with prompt: "{prompt_base}" and style: "{style_choice}"')

    user_key = await get_key()
    for idx in range(1, amount + 1):
        info_logger.info(f"--- Starting Image {idx}/{amount} ---")
        while True:
            info_logger.info("Sending image creation request...")
            params = {'prompt': quote(f"'{full_prompt}'"), 'negative_prompt': quote(f"'{full_negative_prompt}'"), 'userKey': user_key, '__cache_bust': random.random(), 'seed': '-1', 'resolution': resolution, 'guidance_scale': str(guidance_scale), 'channel': 'ai-text-to-image-generator', 'subChannel': 'public', 'requestId': random.random()}
            create_response = await make_request_with_retries(scraper, 'https://image-generation.perchance.org/api/generate', params=urlencode(params, safe=':%'))
            if 'invalid_key' in create_response.text:
                info_logger.warning("Key expired. Fetching a new one...")
                # MODIFIED: Use the centrally defined path for last_key.txt
                key_file_path = LAST_KEY_FILE
                if os.path.exists(key_file_path):
                    os.remove(key_file_path)
                user_key = await get_key()
                info_logger.info("Retrying with new key...")
                continue
            image_id = None
            for attempt in range(20):
                try:
                    res_json = create_response.json()
                    if res_json.get('status') == 'success':
                        image_id = res_json.get('imageId')
                        if image_id:
                            info_logger.info(f"Success! Got image ID: {image_id}")
                            break
                    elif res_json.get('status') == 'pending':
                        info_logger.info(f"Request pending (Attempt {attempt+1}/20)...")
                    else:
                        raise Exception(f"API Error: {res_json.get('status', 'unknown')}")
                except Exception:
                    info_logger.warning(f"Response not ready. Retrying...")
                await asyncio.sleep(3)
                create_response = await make_request_with_retries(scraper, 'https://image-generation.perchance.org/api/generate', params=urlencode(params, safe=':%'))
            if image_id is None: raise Exception("Server did not provide a valid image ID in time.")
            info_logger.info("Downloading image...")
            dl_params = {'imageId': image_id}
            dl_response = await make_request_with_retries(scraper, 'https://image-generation.perchance.org/api/downloadTemporaryImage', params=dl_params)
            CACHE_DIR = '.cache'
            filename = f'{base_filename}{idx}.jpeg' if base_filename else f'{image_id}.jpeg'
            temp_path = os.path.join(CACHE_DIR, filename)
            with open(temp_path, 'wb') as file: file.write(dl_response.content)
            info_logger.info(f"SUCCESS: Saved temporary image {idx}/{amount} to {temp_path}")
            if callback: callback(temp_path)
            break

# ==============================================================================
# Helper Functions for Video Generation
# ==============================================================================
def seconds_to_srt_time(seconds):
    td = timedelta(seconds=seconds)
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{td.microseconds // 1000:03d}"

def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def zoom_in(clip, duration=None, factor=1.1):
    if duration is None: duration = clip.duration
    def resize_func(get_frame, t):
        if duration == 0: scale = 1
        else: scale = 1 + (factor - 1) * (t / duration)
        frame = get_frame(t)
        img = Image.fromarray(frame)
        new_size = (int(img.width * scale), int(img.height * scale))
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        left = (resized_img.width - img.width) / 2
        top = (resized_img.height - img.height) / 2
        right = (resized_img.width + img.width) / 2
        bottom = (resized_img.height + img.height) / 2
        return np.array(resized_img.crop((left, top, right, bottom)))
    return clip.fl(resize_func)

def mask_luminance(clip):
    mask_clip = mp.VideoClip(make_frame=lambda t: (clip.get_frame(t).mean(axis=2)) / 255.0,
                            ismask=True,
                            duration=clip.duration)
    return clip.set_mask(mask_clip)

# ==============================================================================
# Podcast Suite Backend Thread
# ==============================================================================
class TextGenerationThread(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)

    def __init__(self, api_keys_list, start_index, prompt_text, user_input_text="", speaker1_name="", speaker2_name="", task_type="generate_script", script_length="Medium"):
        super().__init__()
        self.ordered_keys = api_keys_list[start_index:] + api_keys_list[:start_index]
        self.prompt_text = prompt_text
        self.user_input_text = user_input_text
        self.speaker1_name = speaker1_name
        self.speaker2_name = speaker2_name
        self.task_type = task_type
        self.script_length = script_length

    def run(self):
        last_error = None
        for api_key in self.ordered_keys:
            try:
                self.status_update.emit(f"Attempting with key ...{api_key[-4:]}")
                if not api_key or api_key.strip() == "":
                    raise ValueError("Invalid API Key.")

                genai.configure(api_key=api_key)

                self.progress.emit(25)
                model = genai.GenerativeModel('gemini-1.5-flash')

                full_prompt = self.build_prompt()

                response = model.generate_content(full_prompt)
                self.progress.emit(75)

                if response and response.text:
                    self.status_update.emit(f"Generation successful with key ...{api_key[-4:]}!")
                    self.finished.emit(response.text)
                    return

            except (google_exceptions.PermissionDenied,
                    google_exceptions.ResourceExhausted,
                    google_exceptions.Unauthenticated) as e:
                last_error = e
                self.status_update.emit(f"Key ...{api_key[-4:]} failed. Trying next...")
                continue

            except Exception as e:
                log_filename = log_error_to_file(e, suite_name="Podcast Suite - Text Generation")
                self.finished.emit(f"A non-key related error occurred: {e}\n\nDetails saved to '{log_filename}'")
                return

        self.finished.emit(f"Error: All API keys failed. Last error: {last_error or 'Unknown API issue.'}")
        self.progress.emit(100)

    def build_prompt(self):
        if self.task_type == "generate_script":
            if self.script_length == "Short":
                length_instruction = "The final script should be concise, aiming for approximately 300-400 words, to create a listening experience of over 2 minutes."
            elif self.script_length == "Long":
                length_instruction = "The final script should be comprehensive and in-depth, aiming for approximately 900-1100 words, to create a listening experience of over 6 minutes."
            else: # Medium
                length_instruction = "The final script should be moderately detailed, aiming for approximately 600-750 words, to create a listening experience of over 4 minutes."

            return (
                f"You are a professional podcast script writer. The male speaker is named '{self.speaker1_name}' and the female speaker is named '{self.speaker2_name}'.\n\n"
                f"Based on the following content, generate a podcast script that flows naturally as a conversation between '{self.speaker1_name}' (as Speaker 1) and '{self.speaker2_name}' (as Speaker 2). "
                f"{length_instruction} Each speaker's turn should begin with 'Speaker 1:' or 'Speaker 2:'. "
                f"Incorporate their actual names ('{self.speaker1_name}' and '{self.speaker2_name}') into the dialogue where appropriate, making it sound like a real conversation. "
                f"Remove all explicit music cues and timestamps. The script should be engaging and informative. Apply any additional instructions from the user prompt: {self.prompt_text}\n\n"
                f"Original Content to be adapted into a script:\n{self.user_input_text}"
            )
        elif self.task_type == "generate_prompts":
            return (
                f"Based on the following podcast content, generate ONE comprehensive English prompt for an AI image generator. "
                f"This single prompt should describe a complex, multi-panel, and seamlessly blended digital art piece. "
                f"The prompt should suggest **three distinct blending approaches** for the AI to interpret. "
                f"Focus on the main themes, key concepts, and atmosphere from the content. "
                f"The overall image should create a cohesive, dreamlike, and evocative visual narrative in a high-detail digital painting style.\n\n"
                f"Here are the three blending approaches to suggest within the prompt:\n"
                f"1.  **Seamless Morphing/Dreamlike Flow:** Elements gradually transform and flow into each other without distinct edges.\n"
                f"2.  **Layered/Overlay Composition with Transparency:** Different scenes are layered with varying transparency, allowing multiple narrative layers to be visible simultaneously.\n"
                f"3.  **Segmented but Blended Panels:** The image is composed of distinct segments, but the boundaries are soft, brushstroke-like blurs that subtly merge one segment into the next.\n\n"
                f"Now, generate the single prompt using these principles, integrating content from:\n{self.user_input_text}"
            )
        return ""

# ==============================================================================
# GUI Helper Classes & Functions
# ==============================================================================
def log_error_to_file(e, suite_name="General"):
    """Logs an exception and its traceback to a file."""
    log_filename = os.path.join(BASE_DIR, "error_log.txt")
    error_details = traceback.format_exc()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_message = (
        f"============================================================\n"
        f"Error in: {suite_name}\n"
        f"Timestamp: {timestamp}\n"
        f"------------------------------------------------------------\n"
        f"Error: {e}\n\n"
        f"Traceback:\n{error_details}\n"
        f"============================================================\n\n"
    )
    try:
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_message)
        return log_filename
    except Exception as file_error:
        print(f"CRITICAL: Failed to write to error log file: {file_error}")
        print(log_message)
        return None

class QtLogStream(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    def emit(self, record):
        self.callback(self.format(record))

class SelectableImage(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox, 0, Qt.AlignCenter)
        self.image_label = QLabel()
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(250, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        self.setFixedWidth(270)
    def is_selected(self): return self.checkbox.isChecked()
    def set_selected(self, checked): self.checkbox.setChecked(checked)

# ==============================================================================
# CORRECTED VideoGenerationWorker (from pro.py logic)
# ==============================================================================
class VideoGenerationWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, photo_data, audio_file, smoke_overlay_file, captions, output_filename, font_path, font_size, font_color, shadow_color, video_ratio, logo_options, codec, handbrake_cli_path):
        super().__init__()
        self.photo_data = list(photo_data) # Make a copy
        self.audio_file = audio_file
        self.smoke_overlay_file = smoke_overlay_file
        self.captions = captions
        self.output_filename = output_filename
        self.font_path = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.shadow_color = shadow_color
        self.video_ratio_str = video_ratio
        self.logo_options = logo_options
        self.codec = codec
        self.handbrake_cli_path = handbrake_cli_path
        self.process = None # For QProcess

    def run(self):
        temp_video_path = None
        temp_srt_path = None
        temp_ass_path = None
        try:
            # === PART 1: Generate temporary video with MoviePy (WITH ALL EFFECTS) ===
            self.progress.emit(5, "Part 1: Preparing video clips...")

            if not self.photo_data:
                self.error.emit("No photos selected for video generation.")
                return

            # Pre-process images to a standard size for efficiency
            for i, photo_info in enumerate(self.photo_data):
                self.progress.emit(5 + int(i / len(self.photo_data) * 15), f"Processing image {i+1}/{len(self.photo_data)}")
                with Image.open(photo_info['path']) as img:
                    # Resize to a common HD format, 16:9 ratio. Crop will handle other ratios later.
                    resized_img = img.resize((1920, 1080), Image.Resampling.LANCZOS).convert("RGB")
                    photo_info['preprocessed_frame'] = np.array(resized_img)

            self.progress.emit(20, "Reading audio to determine duration...")
            audio_clip = mp.AudioFileClip(self.audio_file)
            photo_duration = audio_clip.duration / len(self.photo_data)

            photo_clips = []
            for photo_info in self.photo_data:
                clip = mp.ImageClip(photo_info['preprocessed_frame']).set_duration(photo_duration)
                
                if photo_info['effects'].get('zoom'):
                    zoom_factor = photo_info['effects'].get('zoom_factor', 1.1)
                    clip = zoom_in(clip, duration=photo_duration, factor=zoom_factor)
                
                photo_clips.append(clip)
            
            self.progress.emit(30, "Compositing base slideshow...")
            slideshow_video = mp.concatenate_videoclips(photo_clips, method="compose")

            # Apply continuous overlay effect if selected
            is_any_smoke_effect = any(p['effects'].get('smoke') for p in self.photo_data)
            if self.smoke_overlay_file and is_any_smoke_effect:
                self.progress.emit(32, "Applying continuous overlay effect...")
                smoke_clip = mp.VideoFileClip(self.smoke_overlay_file, has_mask=True).loop()
                smoke_clip = smoke_clip.set_duration(slideshow_video.duration).resize(slideshow_video.size)
                smoke_clip_with_mask = mask_luminance(smoke_clip)
                video = mp.CompositeVideoClip([slideshow_video, smoke_clip_with_mask.set_pos('center')])
            else:
                video = slideshow_video

            video = video.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)

            self.progress.emit(35, "Part 1: Applying video ratio...")
            if self.video_ratio_str != "Original":
                ratios = {"9:16 (TikTok/Shorts)": 9/16, "1:1 (Square)": 1.0, "4:3 (Classic)": 4/3}
                target_ratio = ratios.get(self.video_ratio_str, video.aspect_ratio)
                video = vfx.crop(video, x_center=video.w/2, y_center=video.h/2,
                                 width=int(target_ratio * video.h) if target_ratio < video.aspect_ratio else video.w,
                                 height=int(video.w / target_ratio) if target_ratio > video.aspect_ratio else video.h)

            self.progress.emit(38, "Part 1: Adding logo...")
            if self.logo_options['enabled'] and self.logo_options['path']:
                logo_clip = mp.ImageClip(self.logo_options['path']).set_duration(video.duration).set_opacity(0.8)
                target_logo_width = video.w * (self.logo_options['size'] / 100)
                logo_clip = logo_clip.resize(width=target_logo_width)
                pos_map = {"Top Right": ("right", "top"), "Top Left": ("left", "top"),
                           "Bottom Right": ("right", "bottom"), "Bottom Left": ("left", "bottom")}
                logo_clip = logo_clip.set_pos(pos_map.get(self.logo_options['position'], ("right", "top")))
                video = mp.CompositeVideoClip([video, logo_clip])

            video.audio = audio_clip
            temp_video_path = os.path.join(tempfile.gettempdir(), f"{os.path.basename(self.output_filename)}.tmp.mp4")
            
            self.progress.emit(40, "Part 1: Rendering temporary video (this may take a while)...")
            video.write_videofile(temp_video_path, codec="libx264", audio_codec="aac", fps=24, logger=None, threads=os.cpu_count() or 2, preset='ultrafast')
            
            # === PART 2: Create SRT and convert to styled ASS ===
            self.progress.emit(60, "Part 2: Creating styled subtitle file...")
            srt_content = f"1\n{seconds_to_srt_time(0)} --> {seconds_to_srt_time(video.duration)}\n{self.captions}"
            temp_srt_fd, temp_srt_path = tempfile.mkstemp(suffix=".srt", text=True)
            with os.fdopen(temp_srt_fd, 'w', encoding='utf-8') as f: f.write(srt_content)
            
            subs = pysubs2.load(temp_srt_path, encoding="utf-8")
            r_font, g_font, b_font = hex_to_rgb(self.font_color)
            r_shadow, g_shadow, b_shadow = hex_to_rgb(self.shadow_color)
            font_name = os.path.splitext(os.path.basename(self.font_path))[0] if self.font_path else "Arial"
            style = pysubs2.SSAStyle(fontname=font_name, fontsize=self.font_size, 
                                     primarycolor=pysubs2.Color(r_font, g_font, b_font),
                                     outlinecolor=pysubs2.Color(r_shadow, g_shadow, b_shadow), 
                                     backcolor=pysubs2.Color(0,0,0,128), borderstyle=1, outline=1.5, shadow=0.8, 
                                     alignment=pysubs2.Alignment.BOTTOM_CENTER, marginv=40)
            subs.styles["Default"] = style
            for line in subs: line.style = "Default"
            
            temp_ass_fd, temp_ass_path = tempfile.mkstemp(suffix=".ass", text=True)
            subs.save(temp_ass_path, encoding="utf-8-sig")
            os.close(temp_ass_fd)
            
            # === PART 3: Execute HandBrakeCLI using QProcess for live feedback ===
            self.progress.emit(65, "Part 3: Starting HandBrakeCLI for final encoding...")
            command = [self.handbrake_cli_path, "-i", temp_video_path, "-o", self.output_filename, "--ssa-file", temp_ass_path, "--ssa-burn", "-e", self.codec, "--quality", "20", "-a", "1", "--aencoder", "copy"]
            
            self.process = QProcess()
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.on_handbrake_output)
            self.process.start(command[0], command[1:])
            self.process.waitForFinished(-1)

            if self.process.exitStatus() == QProcess.NormalExit and self.process.exitCode() == 0:
                self.progress.emit(100, "Video generation successful!")
                self.finished.emit(f"Video saved successfully to:\n{self.output_filename}")
            else:
                raw_output = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
                self.error.emit(f"HandBrakeCLI failed.\nExit Code: {self.process.exitCode()}\nOutput:\n{raw_output}")

        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="Video Suite")
            self.error.emit(f"An error occurred. Full details saved to:\n{log_filename}\n\n{e}")

        finally:
            if self.process: self.process.kill()
            if temp_video_path and os.path.exists(temp_video_path): os.remove(temp_video_path)
            if temp_srt_path and os.path.exists(temp_srt_path): os.remove(temp_srt_path)
            if temp_ass_path and os.path.exists(temp_ass_path): os.remove(temp_ass_path)

    def on_handbrake_output(self):
        output = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
        # HandBrake's progress format is "Encoding: task 1 of 1, 12.34 %"
        match = re.search(r"Encoding: task \d+ of \d+, ([\d\.]+) %", output)
        if match:
            percent = float(match.group(1))
            # Handbrake is the last ~35% of the process
            self.progress.emit(65 + int(percent * 0.35), f"Part 3: Encoding with HandBrake... {percent:.2f}%")

# ==============================================================================
# Podcast Suite Tab
# ==============================================================================
class PodcastSuiteTab(QWidget):
    # ***** MODIFICATION START *****
    # The constructor now accepts the list of API keys directly.
    def __init__(self, api_keys):
        super().__init__()
        self.api_keys = api_keys # Store the API keys passed from the main window.
        self.init_ui()
        self.apply_custom_styling()
    # ***** MODIFICATION END *****

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        header_label = QLabel("AI Podcast Assistant")
        header_label.setFont(QFont("Arial", 28, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #FF6F00; margin-bottom: 20px; padding-bottom: 5px; border-bottom: 1px solid #3A3A3A;")
        main_layout.addWidget(header_label)

        settings_frame = QFrame(self)
        settings_frame.setObjectName("settingsFrame")
        settings_layout = QVBoxLayout(settings_frame)
        
        options_layout = QHBoxLayout()
        options_layout.setSpacing(15)
        speaker1_label = QLabel("Speaker 1 (Man):")
        speaker1_label.setFont(QFont("Myanmar Text", 10, QFont.Bold))
        options_layout.addWidget(speaker1_label)
        self.speaker1_combo = QComboBox()
        self.speaker1_combo.addItems(["ကိုဘမော်", "ကိုမျိုး", "ကိုစိုး", "ကိုထွန်း", "ကိုကျော်"])
        self.speaker1_combo.setFont(QFont("Myanmar Text", 10))
        options_layout.addWidget(self.speaker1_combo)
        speaker2_label = QLabel("Speaker 2 (Girl):")
        speaker2_label.setFont(QFont("Myanmar Text", 10, QFont.Bold))
        options_layout.addWidget(speaker2_label)
        self.speaker2_combo = QComboBox()
        self.speaker2_combo.addItems(["သူဇာ", "မေ", "နှင်း", "ခိုင်", "နွယ်"])
        self.speaker2_combo.setFont(QFont("Myanmar Text", 10))
        options_layout.addWidget(self.speaker2_combo)
        length_label = QLabel("Podcast အရှည်:")
        length_label.setFont(QFont("Myanmar Text", 10, QFont.Bold))
        options_layout.addWidget(length_label)
        self.length_combo = QComboBox()
        self.length_combo.addItems(["Short", "Medium", "Long"])
        self.length_combo.setCurrentIndex(1)
        self.length_combo.setFont(QFont("Myanmar Text", 10))
        options_layout.addWidget(self.length_combo)
        settings_layout.addLayout(options_layout)
        main_layout.addWidget(settings_frame)

        content_label = QLabel("Podcast အကြောင်းအရာ/မူရင်း Script ကို ဤနေရာတွင် ထည့်သွင်းပါ။")
        content_label.setFont(QFont("Myanmar Text", 11, QFont.Bold))
        main_layout.addWidget(content_label)
        self.original_script_input = QTextEdit()
        self.original_script_input.setPlaceholderText("ဥပမာ: 'ကျောက်စိမ်း - ရှေးပဝေသဏီက အဖိုးတန်ရတနာ' အကြောင်းအရာအပြည့်အစုံကို ဤနေရာတွင် ထည့်သွင်းပါ။")
        self.original_script_input.setFont(QFont("Myanmar Text", 9))
        self.original_script_input.setMinimumHeight(150)
        main_layout.addWidget(self.original_script_input)

        task_prompt_layout = QHBoxLayout()
        task_label = QLabel("ရွေးချယ်ရန် လုပ်ဆောင်ချက်:")
        task_label.setFont(QFont("Myanmar Text", 11, QFont.Bold))
        task_prompt_layout.addWidget(task_label)
        self.task_combo = QComboBox()
        self.task_combo.addItems(["Podcast Script ဖန်တီးပါ", "AI Prompts များ ထုတ်ပေးပါ"])
        self.task_combo.setFont(QFont("Myanmar Text", 10))
        self.task_combo.currentIndexChanged.connect(self.on_task_changed)
        task_prompt_layout.addWidget(self.task_combo)
        self.prompt_label = QLabel("AI အတွက် လမ်းညွှန်ချက် (Prompt):")
        self.prompt_label.setFont(QFont("Myanmar Text", 11, QFont.Bold))
        task_prompt_layout.addWidget(self.prompt_label)
        self.prompt_input = QTextEdit()
        self.prompt_input.setFont(QFont("Myanmar Text", 9))
        self.prompt_input.setMaximumHeight(80)
        task_prompt_layout.addWidget(self.prompt_input)
        main_layout.addLayout(task_prompt_layout)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("AI ဖြင့် စတင်ပါ")
        self.generate_button.setObjectName("podcastGenerateButton")
        self.generate_button.setFont(QFont("Myanmar Text", 13, QFont.Bold))
        self.generate_button.clicked.connect(self.start_generation)
        button_layout.addWidget(self.generate_button)
        self.clear_button = QPushButton("အားလုံးရှင်းလင်းပါ")
        self.clear_button.setObjectName("podcastClearButton")
        self.clear_button.setFont(QFont("Myanmar Text", 13, QFont.Bold))
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        output_label = QLabel("AI မှ ထုတ်လုပ်ထားသော ရလဒ်:")
        output_label.setFont(QFont("Myanmar Text", 11, QFont.Bold))
        main_layout.addWidget(output_label)
        self.generated_output = QTextEdit()
        self.generated_output.setReadOnly(True)
        self.generated_output.setFont(QFont("Myanmar Text", 9))
        self.generated_output.setMinimumHeight(150)
        main_layout.addWidget(self.generated_output)

        self.copy_button = QPushButton("ရလဒ์ကို ကူးပါ")
        self.copy_button.setObjectName("podcastCopyButton")
        self.copy_button.setFont(QFont("Myanmar Text", 12, QFont.Bold))
        self.copy_button.clicked.connect(self.copy_output_to_clipboard)
        main_layout.addWidget(self.copy_button, alignment=Qt.AlignRight)

        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.on_task_changed(0)

    def apply_custom_styling(self):
        # This function applies styles specific to this tab
        self.findChild(QFrame, "settingsFrame").setStyleSheet("QFrame { background-color: #282828; border-radius: 10px; padding: 10px; }")
        self.findChild(QPushButton, "podcastGenerateButton").setStyleSheet("background-color: #FF6F00; color: white;")
        self.findChild(QPushButton, "podcastClearButton").setStyleSheet("background-color: #6c757d; color: white;")
        self.findChild(QPushButton, "podcastCopyButton").setStyleSheet("background-color: #17A2B8; color: white;")

    def on_task_changed(self, index):
        is_script_task = (index == 0)
        self.prompt_label.setVisible(is_script_task)
        self.prompt_input.setVisible(is_script_task)
        self.speaker1_combo.setEnabled(is_script_task)
        self.speaker2_combo.setEnabled(is_script_task)
        self.length_combo.setEnabled(is_script_task)
        if is_script_task:
            self.prompt_input.setPlaceholderText("ဤနေရာတွင် အပိုဆောင်းလမ်းညွှန်ချက်များ ထည့်သွင်းပါ။")
            self.original_script_input.setPlaceholderText("ဥပမာ: 'ကျောက်စိမ်း' အကြောင်းအရာအပြည့်အစုံကို ဤနေရာတွင် ထည့်သွင်းပါ။")
        else:
            self.original_script_input.setPlaceholderText("Podcast Script မှ Prompts များ ထုတ်ပေးရန် ဤနေရာတွင်ထည့်ပါ။")

    def start_generation(self):
        # ***** MODIFICATION START *****
        # The complex parent-traversal logic is replaced with direct access
        # to the API keys stored during initialization.
        api_keys_list = self.api_keys
        # ***** MODIFICATION END *****

        if not api_keys_list:
            QMessageBox.warning(self, "API Key မရှိပါ", f"data/config.ini တွင် [APIKeys] section အောက်၌ API key များ ရှာမတွေ့ပါ။")
            return

        original_text = self.original_script_input.toPlainText().strip()
        if not original_text:
             QMessageBox.warning(self, "အကြောင်းအရာမရှိပါ", "လုပ်ဆောင်ရန်အတွက် Podcast အကြောင်းအရာကို ထည့်သွင်းပေးပါ။")
             return

        self.generate_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Starting generation process...")
        self.generated_output.clear()

        start_index = 0

        task_type_index = self.task_combo.currentIndex()
        task_type = "generate_script" if task_type_index == 0 else "generate_prompts"
        prompt_text = self.prompt_input.toPlainText().strip() if task_type == "generate_script" else ""
        script_length = self.length_combo.currentText() if task_type == "generate_script" else ""
        speaker1_name = self.speaker1_combo.currentText()
        speaker2_name = self.speaker2_combo.currentText()

        self.thread = TextGenerationThread(api_keys_list, start_index, prompt_text, original_text, speaker1_name, speaker2_name, task_type, script_length)
        self.thread.finished.connect(self.on_generation_finished)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.status_update.connect(self.status_bar.showMessage)
        self.thread.start()

    def on_generation_finished(self, result_text_or_error):
        self.generate_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if result_text_or_error.startswith("Error"):
            QMessageBox.critical(self, "လုပ်ဆောင်ခြင်း မအောင်မြင်ပါ", result_text_or_error)
            self.generated_output.setText(f"လုပ်ဆောင်ခြင်း မအောင်မြင်ပါ: {result_text_or_error}")
            self.status_bar.showMessage("လုပ်ဆောင်ခြင်း မအောင်မြင်ပါ။")
            self.copy_button.setEnabled(False)
        else:
            self.generated_output.setText(result_text_or_error)
            self.status_bar.showMessage("AI မှ လုပ်ဆောင်ခြင်း အောင်မြင်ပါသည်။")
            self.copy_button.setEnabled(True)

    def copy_output_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.generated_output.toPlainText())
        self.status_bar.showMessage("ရလဒ์ကို Clipboard သို့ ကူးယူပြီးပါပြီ။", 3000)

    def clear_fields(self):
        self.original_script_input.clear()
        self.prompt_input.clear()
        self.generated_output.clear()
        self.speaker1_combo.setCurrentIndex(0)
        self.speaker2_combo.setCurrentIndex(0)
        self.length_combo.setCurrentIndex(1)
        self.task_combo.setCurrentIndex(0)
        self.copy_button.setEnabled(False)
        self.status_bar.showMessage("အသင့်ဖြစ်ပါပြီ။")

# ==============================================================================
# Video Suite Tab
# ==============================================================================
class VideoSuiteTab(QWidget):
    def __init__(self):
        super().__init__()
        self.photo_data = []
        self.audio_file = None
        self.smoke_overlay_file = None
        self.worker = None
        self.font_map = {}
        self.font_color = "#FFFFFF"
        self.shadow_color = "#000000"
        self.handbrake_cli_path = self.find_handbrake_cli()
        self.init_ui()

    def find_handbrake_cli(self):
        expected_path = os.path.join(FILE_DIR, 'HandBrakeCLI.exe')
        return expected_path if os.path.exists(expected_path) else ""

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_panel_layout = QVBoxLayout()
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel_layout)
        left_panel_widget.setMaximumWidth(450)

        timeline_group = QGroupBox("Photo Timeline")
        timeline_layout = QVBoxLayout(timeline_group)
        self.photo_list = QListWidget()
        self.photo_list.currentItemChanged.connect(self.on_photo_selected)
        timeline_layout.addWidget(self.photo_list)
        timeline_buttons_layout = QHBoxLayout()
        btn_add_photos = QPushButton("➕ Add Photos")
        btn_add_photos.clicked.connect(self.add_photos)
        btn_clear_list = QPushButton("🗑️ Clear List")
        btn_clear_list.clicked.connect(self.clear_photo_list)
        timeline_buttons_layout.addWidget(btn_add_photos)
        timeline_buttons_layout.addWidget(btn_clear_list)
        timeline_layout.addLayout(timeline_buttons_layout)

        global_settings_group = QGroupBox("Global Settings")
        global_settings_group.setContentsMargins(10, 15, 10, 10)
        group_container_layout_1 = QVBoxLayout(global_settings_group)
        content_widget_1 = QWidget()
        global_settings_layout = QGridLayout(content_widget_1)
        global_settings_layout.setSpacing(10)
        global_settings_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_handbrake_path = QLabel()
        self.update_handbrake_status_label()
        self.btn_audio = QPushButton("🎵 Select Background Audio")
        self.btn_audio.clicked.connect(self.select_audio)
        self.lbl_audio_file = QLabel("No audio selected.")
        
        # ***** MODIFICATION START *****
        self.chk_enable_overlay = QCheckBox("Enable Video Overlay Effect")
        self.chk_enable_overlay.toggled.connect(self.toggle_overlay_controls)
        
        self.btn_smoke_overlay = QPushButton("💨 Select Overlay Video")
        self.btn_smoke_overlay.clicked.connect(self.select_smoke_overlay)
        self.lbl_smoke_file = QLabel("No overlay selected.")
        # ***** MODIFICATION END *****
        
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(["CPU (x264)", "NVIDIA (NVENC)", "AMD (VCE)", "Intel (QSV)"])
        self.codec_combo.setItemData(0, "x264")
        self.codec_combo.setItemData(1, "nvenc_h264")
        self.codec_combo.setItemData(2, "amf_h264")
        self.codec_combo.setItemData(3, "qsv_h264")
        global_settings_layout.addWidget(QLabel("<b>HandBrake Status:</b>"), 0, 0)
        global_settings_layout.addWidget(self.lbl_handbrake_path, 0, 1)
        global_settings_layout.addWidget(self.btn_audio, 1, 0, 1, 2)
        global_settings_layout.addWidget(self.lbl_audio_file, 2, 0, 1, 2)
        
        # ***** MODIFICATION START *****
        global_settings_layout.addWidget(self.chk_enable_overlay, 3, 0, 1, 2)
        global_settings_layout.addWidget(self.btn_smoke_overlay, 4, 0, 1, 2)
        global_settings_layout.addWidget(self.lbl_smoke_file, 5, 0, 1, 2)
        global_settings_layout.addWidget(QLabel("🚀 Hardware Acceleration:"), 6, 0)
        global_settings_layout.addWidget(self.codec_combo, 6, 1)
        # ***** MODIFICATION END *****
        
        global_settings_layout.setColumnStretch(1, 1)
        group_container_layout_1.addWidget(content_widget_1)

        self.btn_generate = QPushButton("🎬 Generate Video")
        self.btn_generate.setStyleSheet("background-color: #28a745; color: white; padding: 15px; font-size: 18px; font-weight: bold;")
        self.btn_generate.clicked.connect(self.start_video_generation)
        if not self.handbrake_cli_path:
            self.btn_generate.setEnabled(False)
            self.btn_generate.setText("HandBrakeCLI Not Found")
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready.")
        left_panel_layout.addWidget(timeline_group)
        left_panel_layout.addWidget(global_settings_group)
        left_panel_layout.addStretch()
        left_panel_layout.addWidget(self.btn_generate)
        left_panel_layout.addWidget(self.progress_bar)
        left_panel_layout.addWidget(self.status_label)

        right_panel_layout = QVBoxLayout()
        video_effects_group = QGroupBox("Video & Effects Settings")
        video_effects_group.setContentsMargins(10, 15, 10, 10)
        group_container_layout_2 = QVBoxLayout(video_effects_group)
        content_widget_2 = QWidget()
        video_effects_layout = QGridLayout(content_widget_2)
        video_effects_layout.setSpacing(10)
        video_effects_layout.setContentsMargins(0, 0, 0, 0)
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems(["Original", "9:16 (TikTok/Shorts)", "1:1 (Square)", "4:3 (Classic)"])
        video_effects_layout.addWidget(QLabel("🖼️ Video Aspect Ratio:"), 0, 0)
        video_effects_layout.addWidget(self.ratio_combo, 0, 1)

        self.logo_group = QGroupBox("✨ Add Logo/Watermark")
        self.logo_group.setCheckable(True)
        self.logo_group.setChecked(False)
        self.logo_group.setContentsMargins(10, 15, 10, 10)
        group_container_layout_3 = QVBoxLayout(self.logo_group)
        content_widget_3 = QWidget()
        logo_layout = QGridLayout(content_widget_3)
        logo_layout.setSpacing(10)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        self.logo_path_edit = QLineEdit()
        self.logo_path_edit.setReadOnly(True)
        self.logo_path_edit.setPlaceholderText("No logo selected")
        btn_browse_logo = QPushButton("Browse...")
        btn_browse_logo.clicked.connect(self.browse_logo)
        logo_file_layout = QHBoxLayout()
        logo_file_layout.addWidget(self.logo_path_edit)
        logo_file_layout.addWidget(btn_browse_logo)
        logo_layout.addWidget(QLabel("📂 Logo File:"), 0, 0)
        logo_layout.addLayout(logo_file_layout, 0, 1)
        self.logo_pos_combo = QComboBox()
        self.logo_pos_combo.addItems(["Top Right", "Top Left", "Bottom Right", "Bottom Left"])
        logo_layout.addWidget(QLabel("📍 Logo Position:"), 1, 0)
        logo_layout.addWidget(self.logo_pos_combo, 1, 1)
        self.logo_size_slider = QSlider(Qt.Horizontal)
        self.logo_size_slider.setRange(5, 30)
        self.logo_size_slider.setValue(10)
        self.logo_size_label = QLabel(f"{self.logo_size_slider.value()}%")
        self.logo_size_slider.valueChanged.connect(lambda v: self.logo_size_label.setText(f"{v}%"))
        logo_size_layout = QHBoxLayout()
        logo_size_layout.addWidget(self.logo_size_slider)
        logo_size_layout.addWidget(self.logo_size_label)
        logo_layout.addWidget(QLabel("📏 Logo Size:"), 2, 0)
        logo_layout.addLayout(logo_size_layout, 2, 1)
        logo_layout.setColumnStretch(1, 1)
        group_container_layout_3.addWidget(content_widget_3)

        video_effects_layout.addWidget(self.logo_group, 1, 0, 1, 2)
        video_effects_layout.setColumnStretch(1, 1)
        group_container_layout_2.addWidget(content_widget_2)

        self.effects_group = QGroupBox("Effects for Selected Photo")
        self.effects_group.setContentsMargins(10, 15, 10, 10)
        group_container_layout_4 = QVBoxLayout(self.effects_group)
        content_widget_4 = QWidget()
        effects_layout = QGridLayout(content_widget_4)
        effects_layout.setSpacing(10)
        effects_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_zoom = QCheckBox("Zoom-in Effect")
        self.chk_smoke = QCheckBox("Overlay Effect (per Photo)")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(101, 150)
        self.zoom_slider.setValue(110)
        self.zoom_label = QLabel(f"Intensity: {self.zoom_slider.value() / 100.0:.2f}x")
        self.zoom_slider.valueChanged.connect(self.update_zoom_setting)
        self.chk_zoom.stateChanged.connect(self.update_effect_setting)
        self.chk_smoke.stateChanged.connect(self.update_effect_setting)
        effects_layout.addWidget(self.chk_zoom, 0, 0, 1, 2)
        effects_layout.addWidget(QLabel("Zoom Intensity:"), 1, 0)
        effects_layout.addWidget(self.zoom_slider, 1, 1)
        effects_layout.addWidget(self.zoom_label, 2, 1, Qt.AlignLeft)
        effects_layout.addWidget(self.chk_smoke, 3, 0, 1, 2)
        effects_layout.setColumnStretch(1, 1)
        group_container_layout_4.addWidget(content_widget_4)
        self.effects_group.setEnabled(False)

        subtitle_style_group = QGroupBox("Subtitle Style Settings")
        subtitle_style_group.setContentsMargins(10, 15, 10, 10)
        group_container_layout_5 = QVBoxLayout(subtitle_style_group)
        content_widget_5 = QWidget()
        subtitle_style_layout = QGridLayout(content_widget_5)
        subtitle_style_layout.setSpacing(10)
        subtitle_style_layout.setContentsMargins(0, 0, 0, 0)
        self.font_combo = QComboBox()
        subtitle_style_layout.addWidget(QLabel("🔤 Font:"), 0, 0)
        subtitle_style_layout.addWidget(self.font_combo, 0, 1)
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(12, 100)
        self.font_size_spinbox.setValue(36)
        subtitle_style_layout.addWidget(QLabel("🔠 Font Size:"), 1, 0)
        subtitle_style_layout.addWidget(self.font_size_spinbox, 1, 1)
        self.btn_font_color = QPushButton("Choose Color")
        self.font_color_label = QLabel()
        self.update_color_label(self.font_color_label, self.font_color)
        self.btn_font_color.clicked.connect(self.choose_font_color)
        font_color_layout = QHBoxLayout()
        font_color_layout.addWidget(self.btn_font_color)
        font_color_layout.addWidget(self.font_color_label)
        subtitle_style_layout.addWidget(QLabel("🎨 Font Color:"), 2, 0)
        subtitle_style_layout.addLayout(font_color_layout, 2, 1)
        self.btn_shadow_color = QPushButton("Choose Color")
        self.shadow_color_label = QLabel()
        self.update_color_label(self.shadow_color_label, self.shadow_color)
        self.btn_shadow_color.clicked.connect(self.choose_shadow_color)
        shadow_color_layout = QHBoxLayout()
        shadow_color_layout.addWidget(self.btn_shadow_color)
        shadow_color_layout.addWidget(self.shadow_color_label)
        subtitle_style_layout.addWidget(QLabel("🎨 Shadow/Outline Color:"), 3, 0)
        subtitle_style_layout.addLayout(shadow_color_layout, 3, 1)
        subtitle_style_layout.setColumnStretch(1, 1)
        group_container_layout_5.addWidget(content_widget_5)

        caption_group = QGroupBox("Video Captions (Global)")
        caption_layout = QVBoxLayout(caption_group)
        self.input_line1 = QLineEdit()
        self.input_line1.setPlaceholderText("Caption Line 1 (မြန်မာစာ)")
        self.input_line2 = QLineEdit()
        self.input_line2.setPlaceholderText("Caption Line 2 (English)")
        caption_layout.addWidget(self.input_line1)
        caption_layout.addWidget(self.input_line2)

        right_panel_layout.addWidget(video_effects_group)
        right_panel_layout.addWidget(self.effects_group)
        right_panel_layout.addWidget(subtitle_style_group)
        right_panel_layout.addWidget(caption_group)
        right_panel_layout.addStretch()
        main_layout.addWidget(left_panel_widget)
        main_layout.addLayout(right_panel_layout)
        self.load_custom_fonts()
        
        # ***** MODIFICATION START *****
        self.toggle_overlay_controls(False) # Set initial state
        # ***** MODIFICATION END *****
    
    # ***** MODIFICATION START *****
    def toggle_overlay_controls(self, checked):
        """Enable or disable the overlay selection button based on the checkbox."""
        self.btn_smoke_overlay.setEnabled(checked)
        self.lbl_smoke_file.setEnabled(checked)
        if not checked:
            self.smoke_overlay_file = None
            self.lbl_smoke_file.setText("Overlay disabled.")
    # ***** MODIFICATION END *****

    def clear_photo_list(self):
        self.photo_list.clear()
        self.photo_data.clear()
        self.effects_group.setEnabled(False)

    def choose_font_color(self):
        color = QColorDialog.getColor(QColor(self.font_color))
        if color.isValid():
            self.font_color = color.name()
            self.update_color_label(self.font_color_label, self.font_color)

    def choose_shadow_color(self):
        color = QColorDialog.getColor(QColor(self.shadow_color))
        if color.isValid():
            self.shadow_color = color.name()
            self.update_color_label(self.shadow_color_label, self.shadow_color)

    def update_color_label(self, label, color_hex):
        label.setText(color_hex.upper())
        palette = label.palette()
        palette.setColor(QPalette.Window, QColor(color_hex))
        palette.setColor(QPalette.WindowText, QColor("#000000" if sum(hex_to_rgb(color_hex)) > 382 else "#FFFFFF"))
        label.setAutoFillBackground(True)
        label.setPalette(palette)

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo Image", BASE_DIR, "Images (*.png *.jpg)")
        if path:
            self.logo_path_edit.setText(path)

    def update_handbrake_status_label(self):
        if self.handbrake_cli_path:
            self.lbl_handbrake_path.setText("✅ HandBrakeCLI Found")
            self.lbl_handbrake_path.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.lbl_handbrake_path.setText(f"❌ HandBrakeCLI.exe not found in '{os.path.basename(FILE_DIR)}' folder!")
            self.lbl_handbrake_path.setStyleSheet("color: #F44336; font-weight: bold;")

    def load_custom_fonts(self):
        fonts_dir = os.path.join(BASE_DIR, 'fonts')
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
        for font_file in os.listdir(fonts_dir):
            if font_file.lower().endswith(('.ttf', '.otf')):
                font_name = os.path.splitext(font_file)[0]
                self.font_map[font_name] = os.path.join(fonts_dir, font_file)
                self.font_combo.addItem(font_name)
        if not self.font_map:
            self.font_combo.addItem("No fonts in 'fonts' folder")
            self.font_combo.setEnabled(False)

    def add_photos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Photos", BASE_DIR, "Images (*.png *.jpg *.jpeg)")
        if files:
            for file_path in files:
                self.photo_data.append({'path': file_path, 'effects': {'zoom': True, 'smoke': True, 'zoom_factor': 1.10}})
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                self.photo_list.addItem(item)
            if self.photo_list.count() > 0:
                self.photo_list.setCurrentRow(0)

    def select_audio(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Audio", BASE_DIR, "Audio (*.mp3 *.wav)")
        if file:
            self.audio_file = file
            self.lbl_audio_file.setText(f"Audio: {os.path.basename(file)}")

    def select_smoke_overlay(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Overlay Video", BASE_DIR, "Video (*.mp4 *.mov)")
        if file:
            self.smoke_overlay_file = file
            self.lbl_smoke_file.setText(f"Overlay: {os.path.basename(file)}")

    def on_photo_selected(self, current_item, previous_item):
        if not current_item:
            self.effects_group.setEnabled(False)
            return
        self.effects_group.setEnabled(True)
        path = current_item.data(Qt.UserRole)
        photo_info = next((item for item in self.photo_data if item['path'] == path), None)
        if photo_info:
            self.chk_zoom.blockSignals(True)
            self.chk_smoke.blockSignals(True)
            self.zoom_slider.blockSignals(True)
            
            self.chk_zoom.setChecked(photo_info['effects'].get('zoom', False))
            self.chk_smoke.setChecked(photo_info['effects'].get('smoke', False))
            zoom_factor = photo_info['effects'].get('zoom_factor', 1.10)
            self.zoom_slider.setValue(int(zoom_factor * 100))
            self.zoom_label.setText(f"Intensity: {zoom_factor:.2f}x")

            self.chk_zoom.blockSignals(False)
            self.chk_smoke.blockSignals(False)
            self.zoom_slider.blockSignals(False)

    def update_effect_setting(self):
        current_item = self.photo_list.currentItem()
        if not current_item: return
        path = current_item.data(Qt.UserRole)
        photo_info = next((item for item in self.photo_data if item['path'] == path), None)
        if photo_info:
            photo_info['effects']['zoom'] = self.chk_zoom.isChecked()
            photo_info['effects']['smoke'] = self.chk_smoke.isChecked()

    def update_zoom_setting(self):
        current_item = self.photo_list.currentItem()
        if not current_item: return
        path = current_item.data(Qt.UserRole)
        photo_info = next((item for item in self.photo_data if item['path'] == path), None)
        if photo_info:
            zoom_factor = self.zoom_slider.value() / 100.0
            photo_info['effects']['zoom_factor'] = zoom_factor
            self.zoom_label.setText(f"Intensity: {zoom_factor:.2f}x")

    def start_video_generation(self):
        if not self.photo_data or not self.audio_file:
            QMessageBox.warning(self, "Error", "Please add photos and select an audio file.")
            return
        
        # ***** MODIFICATION START *****
        is_any_smoke_effect = any(p['effects'].get('smoke') for p in self.photo_data)
        
        # The check now only triggers if the global overlay is enabled AND a photo uses the effect AND no file is selected.
        if self.chk_enable_overlay.isChecked() and is_any_smoke_effect and not self.smoke_overlay_file:
            QMessageBox.warning(self, "Overlay File Missing", "The global overlay effect is enabled and at least one photo uses it, but no overlay video has been selected.\n\nPlease select an overlay video or disable the global 'Enable Video Overlay Effect' checkbox.")
            return

        # Pass the overlay file to the worker ONLY if the global checkbox is checked.
        smoke_overlay_file_to_pass = self.smoke_overlay_file if self.chk_enable_overlay.isChecked() else None
        # ***** MODIFICATION END *****

        selected_font_name = self.font_combo.currentText()
        font_path = self.font_map.get(selected_font_name)
        if not font_path:
            QMessageBox.critical(self, "Font Error", "Please add a Myanmar Unicode font to the 'fonts' folder and select it.")
            return
        
        if self.logo_group.isChecked() and not self.logo_path_edit.text():
            QMessageBox.warning(self, "Error", "Logo is enabled, but no logo image selected.")
            return
            
        output_filename, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 (*.mp4)")
        if not output_filename: return
            
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Generating...")
        
        logo_options = {
            'enabled': self.logo_group.isChecked(),
            'path': self.logo_path_edit.text(),
            'position': self.logo_pos_combo.currentText(),
            'size': self.logo_size_slider.value()
        }
        captions = f"{self.input_line1.text().strip()}\n{self.input_line2.text().strip()}".strip()

        self.worker = VideoGenerationWorker(
            photo_data=self.photo_data,
            audio_file=self.audio_file,
            smoke_overlay_file=smoke_overlay_file_to_pass, # MODIFIED
            captions=captions,
            output_filename=output_filename,
            font_path=font_path,
            font_size=self.font_size_spinbox.value(),
            font_color=self.font_color,
            shadow_color=self.shadow_color,
            video_ratio=self.ratio_combo.currentText(),
            logo_options=logo_options,
            codec=self.codec_combo.currentData(),
            handbrake_cli_path=self.handbrake_cli_path
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()

    def on_generation_error(self, error_msg):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("🎬 Generate Video")
        self.progress_bar.setValue(0)
        self.status_label.setText("Error occurred.")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")

    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.status_label.setText(text)

    def on_generation_finished(self, message):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("🎬 Generate Video")
        self.status_label.setText("Done!")
        QMessageBox.information(self, "Success", message)

# ==============================================================================
# ProEditor Suite BACKEND (Workers & Helpers from Recap.py)
# ==============================================================================

def format_time_srt(seconds):
    """ Helper for ProEditor Suite """
    td = timedelta(seconds=seconds)
    minutes, rem_seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{rem_seconds:02d},{td.microseconds // 1000:03d}"

class ProRecapDownloadWorker(QThread):
    info_ready = pyqtSignal(list, list)
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, format_code=None, save_path='.'):
        super().__init__()
        self.url = url
        self.format_code = format_code
        self.save_path = save_path
        self._is_running = True

    def run(self):
        if not self._is_running:
            return
        if self.format_code:
            self._download_video()
        else:
            self._get_video_info()

    def _get_video_info(self):
        try:
            command = ['yt-dlp', '-F', self.url]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore', startupinfo=self._get_startup_info())
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                self.error.emit(f"Error getting info: {stderr}")
                return
            video_formats, audio_formats = [], []
            lines = stdout.split('\n')
            header_found = False
            for line in lines:
                if line.startswith('ID '):
                    header_found = True
                    continue
                if not header_found:
                    continue
                if line.strip() == '' or '---' in line: continue
                if 'video only' in line and 'audio only' not in line:
                    parts = line.split()
                    if len(parts) > 1: video_formats.append(f"{parts[0]}: {' '.join(parts[1:])}")
                elif 'audio only' in line:
                    parts = line.split()
                    if len(parts) > 1: audio_formats.append(f"{parts[0]}: {' '.join(parts[1:])}")

            if not video_formats or not audio_formats:
                self.error.emit("Could not parse separate video/audio formats. The video might be old, a livestream, or unavailable in high quality.")
            else:
                self.info_ready.emit(video_formats, audio_formats)
        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="Downloader - Get Info")
            self.error.emit(f"An exception occurred while getting info: {str(e)}\n\nDetails saved to '{log_filename}'")


    def _download_video(self):
        try:
            output_template = os.path.join(self.save_path, "%(title)s [%(id)s].%(ext)s")
            command = ['yt-dlp', '-f', self.format_code, '--no-warnings', '--progress', '-o', output_template, self.url]

            ffmpeg_path = os.path.join(FILE_DIR, "ffmpeg.exe")
            if sys.platform == "win32" and os.path.exists(ffmpeg_path):
                command.extend(['--ffmpeg-location', ffmpeg_path])

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore', bufsize=1, startupinfo=self._get_startup_info())

            for line in iter(process.stdout.readline, ''):
                if not self._is_running:
                    process.terminate()
                    self.finished.emit("Download cancelled.")
                    return
                progress_match = re.search(r"\[download\]\s+([0-9\.]+)%", line)
                if progress_match:
                    self.progress.emit(int(float(progress_match.group(1))))
            process.wait()
            if process.returncode == 0:
                self.finished.emit("Download finished successfully!")
            else:
                self.error.emit(f"Download failed: {process.stderr.read()}")
        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="Downloader - Download")
            self.error.emit(f"An exception occurred during download: {str(e)}\n\nDetails saved to '{log_filename}'")

    def stop(self):
        self._is_running = False

    def _get_startup_info(self):
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None

class ProRecapTranscriptionWorker(QThread):
    completion_signal = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    def __init__(self, input_file, model_size):
        super().__init__()
        self.input_file = input_file
        self.model_size = model_size
    def run(self):
        try:
            model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            segments, info = model.transcribe(self.input_file, beam_size=5)
            srt_filename = os.path.splitext(self.input_file)[0] + '_en.srt'
            with open(srt_filename, 'w', encoding='utf-8') as f:
                for i, seg in enumerate(segments):
                    f.write(f"{i+1}\n{format_time_srt(seg.start)} --> {format_time_srt(seg.end)}\n{seg.text.strip()}\n\n")
                    if info.duration > 0: self.progress_updated.emit(int(seg.end / info.duration * 100))
            self.completion_signal.emit(srt_filename)
        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="ProEditor - Transcription")
            self.error_occurred.emit(f"Transcription error: {e}\n\nDetails saved to '{log_filename}'")

class ProRecapTranslationWorker(QThread):
    completion_signal = pyqtSignal(str)
    status_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path, api_keys_list):
        super().__init__()
        self.file_path = file_path
        self.api_keys_list = api_keys_list

    def run(self):
        last_error = None
        for api_key in self.api_keys_list:
            try:
                self.status_message.emit(f"Translating with key ...{api_key[-4:]}")
                genai.configure(api_key=api_key)
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    srt_content = f.read()
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Please translate the following SRT subtitle content into natural, modern Burmese. Do not change the timestamps or the sequence numbers. Only translate the dialogue text. Return the full SRT content with the translated text.\n\nHere is the SRT content:\n---\n{srt_content}"
                response = model.generate_content(prompt)
                
                if response and response.text:
                    clean_text = response.text.replace("```srt", "").replace("```", "").strip()
                    directory, filename = os.path.split(self.file_path)
                    name, _ = os.path.splitext(filename)
                    srt_output_path = os.path.join(directory, f"{name.replace('_en', '')}_my.srt")
                    with open(srt_output_path, 'w', encoding='utf-8') as f:
                        f.write(clean_text)
                    self.completion_signal.emit(srt_output_path)
                    return # Success
            
            except (google_exceptions.PermissionDenied, google_exceptions.ResourceExhausted, google_exceptions.Unauthenticated) as e:
                last_error = e
                self.status_message.emit(f"Key ...{api_key[-4:]} failed. Trying next...")
                continue # Try next key
            
            except Exception as e:
                log_filename = log_error_to_file(e, suite_name="ProEditor - Translation")
                self.error_occurred.emit(f"Translation error: {e}\n\nDetails saved to '{log_filename}'")
                return

        # If the loop finishes
        self.error_occurred.emit(f"All API keys failed. Last error: {last_error or 'Unknown API issue.'}")

class ProRecapVideoProcessingWorker(QThread):
    completion_signal = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    def __init__(self, input_file, aspect_ratio, flip_mode, logo_options):
        super().__init__()
        self.input_file=input_file; self.aspect_ratio=aspect_ratio; self.flip_mode=flip_mode; self.logo_options = logo_options
    def run(self):
        try:
            base, _ = os.path.splitext(self.input_file); output_filename = f"{base}_processed.mp4"
            video = mp.VideoFileClip(self.input_file)
            if self.aspect_ratio != "Keep Original":
                ratios = {"9:16 (TikTok/Shorts)":9/16, "1:1 (Square)":1.0, "4:3 (Classic)":4/3}
                w, h = video.size; r = ratios.get(self.aspect_ratio)
                nw = int(r*h) if r<(w/h) else w; nh = int(w/r) if r>=(w/h) else h
                video = vfx.crop(video, width=nw, height=nh, x_center=w/2, y_center=h/2)
            if self.flip_mode == "Horizontal": video = vfx.mirror_x(video)
            elif self.flip_mode == "Vertical": video = vfx.mirror_y(video)
            if self.logo_options['enabled'] and self.logo_options['path'] and os.path.exists(self.logo_options['path']):
                logo_clip = mp.ImageClip(self.logo_options['path']).set_duration(video.duration).fadein(1.0).fadeout(1.0)
                target_logo_width = video.w * (self.logo_options['size'] / 100)
                logo_clip = logo_clip.resize(width=target_logo_width)
                if logo_clip.h > video.h * 0.25: logo_clip = logo_clip.resize(height=video.h * 0.25)
                side_padding, top_padding, bottom_padding = 20, 50, 20
                pos_str = self.logo_options['position']
                x_pos = side_padding if 'Left' in pos_str else (video.w - logo_clip.w - side_padding if 'Right' in pos_str else (video.w - logo_clip.w) / 2)
                y_pos = top_padding if 'Top' in pos_str else video.h - logo_clip.h - bottom_padding
                logo_clip = logo_clip.set_position((x_pos, y_pos))
                video = mp.CompositeVideoClip([video, logo_clip])
            video = video.without_audio()
            video.write_videofile(output_filename, codec="libx264", preset="ultrafast", threads=os.cpu_count(), logger=None)
            video.close()
            self.completion_signal.emit(output_filename)
        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="ProEditor - Video Processing")
            self.error_occurred.emit(f"Video processing error: {e}\n\nDetails saved to '{log_filename}'")

class ProRecapHardsubWorker(QThread):
    completion_signal = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, video_path, srt_path, output_path, color_hex, opacity_percent, subtitle_style):
        super().__init__()
        self.video_path = video_path; self.srt_path = srt_path; self.output_path = output_path
        self.color_hex = color_hex; self.opacity_percent = opacity_percent; self.subtitle_style = subtitle_style

    def run(self):
        output_dir = os.path.dirname(self.output_path)
        temp_ass_file = os.path.join(output_dir, "temp_styled.ass")
        try:
            self.status_message.emit(f"Processing subtitles ({self.subtitle_style} style)...")
            subs = pysubs2.load(self.srt_path, encoding="utf-8")
            processed_subs = pysubs2.SSAFile()
            total_original_lines = len(subs)
            if total_original_lines == 0:
                self.error_occurred.emit("The SRT file is empty or could not be read.")
                return

            if self.subtitle_style.startswith("Cumulative"):
                for i, line in enumerate(subs):
                    parts = line.text.split()
                    num_parts = len(parts)
                    if num_parts <= 1: processed_subs.append(line)
                    else:
                        duration_per_part = line.duration / num_parts
                        for j, part_text in enumerate(parts):
                            cumulative_text = " ".join(parts[0:j+1])
                            new_start = line.start + (j * duration_per_part)
                            new_end = line.end if j == num_parts - 1 else line.start + ((j + 1) * duration_per_part)
                            processed_subs.append(pysubs2.SSAEvent(start=new_start, end=new_end, text=cumulative_text))
                    self.progress_updated.emit(int(((i + 1) / total_original_lines) * 50))
            else: # Sequential Style
                for i, line in enumerate(subs):
                    parts = line.text.split()
                    num_parts = len(parts)
                    if num_parts <= 1: processed_subs.append(line)
                    else:
                        duration_per_part = line.duration / num_parts
                        for j, part_text in enumerate(parts):
                            new_start = line.start + (j * duration_per_part)
                            new_end = line.start + ((j + 1) * duration_per_part)
                            processed_subs.append(pysubs2.SSAEvent(start=new_start, end=new_end, text=part_text))
                    self.progress_updated.emit(int(((i + 1) / total_original_lines) * 50))

            self.status_message.emit("Creating styled subtitles (.ass)...")
            r, g, b = int(self.color_hex[0:2], 16), int(self.color_hex[2:4], 16), int(self.color_hex[4:6], 16)
            alpha = int((100 - self.opacity_percent) * 2.55)
            font_name, font_size, margin_v = 'Noto Sans Myanmar', 18, 25

            bg_style=pysubs2.SSAStyle(fontname=font_name, fontsize=font_size, primarycolor=pysubs2.Color(0,0,0,255), backcolor=pysubs2.Color(r,g,b,alpha), outlinecolor=pysubs2.Color(r,g,b,alpha), borderstyle=3, outline=3, shadow=0, alignment=pysubs2.Alignment.BOTTOM_CENTER, marginv=margin_v)
            fg_style=pysubs2.SSAStyle(fontname=font_name, fontsize=font_size, primarycolor=pysubs2.Color(255,255,255), outlinecolor=pysubs2.Color(0,0,0), backcolor=pysubs2.Color(0,0,0,255), borderstyle=1, outline=1.5, shadow=0.8, alignment=pysubs2.Alignment.BOTTOM_CENTER, marginv=margin_v)

            final_subs=pysubs2.SSAFile(); final_subs.info['YCbCr Matrix']='TV.709'
            final_subs.styles['Background']=bg_style; final_subs.styles['Foreground']=fg_style

            total_processed_lines = len(processed_subs)
            if total_processed_lines == 0:
                self.error_occurred.emit("No subtitles were available after processing.")
                return

            for i, line in enumerate(processed_subs):
                bg_line=line.copy(); bg_line.style="Background"; bg_line.layer=0; final_subs.append(bg_line)
                fg_line=line.copy(); fg_line.style="Foreground"; fg_line.layer=1; final_subs.append(fg_line)
                self.progress_updated.emit(50 + int(((i + 1) / total_processed_lines) * 50))

            final_subs.save(temp_ass_file,encoding="utf-8")
            self.status_message.emit("Burning subtitles with HandBrakeCLI...")
            self.progress_updated.emit(100)

            handbrake_cli_path = os.path.join(FILE_DIR, 'HandBrakeCLI.exe')
            command=[handbrake_cli_path,'-i',self.video_path,'-o',self.output_path,'--preset','Fast 1080p30','--ssa-file',temp_ass_file,'--ssa-burn']

            process=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)

            if process.returncode==0: self.completion_signal.emit(self.output_path)
            else: self.error_occurred.emit(f"HandBrakeCLI Error:\n{process.stderr if process.stderr else process.stdout}")

        except FileNotFoundError:
            self.error_occurred.emit(f"HandBrakeCLI.exe not found. Make sure it's inside the '{os.path.basename(FILE_DIR)}' subdirectory.")
        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="ProEditor - Hardsub")
            self.error_occurred.emit(f"Hardsub error: {e}\n\nDetails saved to '{log_filename}'")
        finally:
            if os.path.exists(temp_ass_file): os.remove(temp_ass_file)

TTS_VOICE_MAPPING = {
    "Myanmar Male (Thiha)": "my-MM-ThihaNeural",
    "Myanmar Female (Nilar)": "my-MM-NilarNeural",
}
DEFAULT_TTS_VOICE = "Myanmar Male (Thiha)"

class ProRecapTTSWorker(QThread):
    completion_signal = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, srt_file_path, video_file_path, voice_name, rate_percent, output_path):
        super().__init__()
        if not srt_file_path or not os.path.exists(srt_file_path):
            raise FileNotFoundError(f"SRT file not found for TTS process: {srt_file_path}")
        self.srt_file_path = srt_file_path
        self.video_file_path = video_file_path
        self.voice_name = voice_name
        self.rate_percent = rate_percent
        self.output_path = output_path
        self.output_dir = os.path.dirname(self.output_path)
        self.temp_audio_files = []

    def cleanup_temp_files(self):
        """Remove all temporary audio files created during the process."""
        all_temp_files = self.temp_audio_files + glob.glob(os.path.join(self.output_dir, "temp_tts_*.mp3"))
        for f in set(all_temp_files):
            try:
                if os.path.exists(f): os.remove(f)
            except OSError as e:
                print(f"Warning: Could not remove temp file {f}: {e}")
        self.temp_audio_files.clear()

    async def generate_and_adjust_line(self, text, target_duration_sec, line_index):
        """Generates a TTS clip and adjusts its speed."""
        raw_clip_path = os.path.join(self.output_dir, f"temp_tts_raw_{line_index}.mp3")
        adjusted_clip_path = os.path.join(self.output_dir, f"temp_tts_adj_{line_index}.mp3")
        rate_str = f"+{self.rate_percent}%" if self.rate_percent >= 0 else f"{self.rate_percent}%"

        communicate = edge_tts.Communicate(text, voice=self.voice_name, rate=rate_str)
        await communicate.save(raw_clip_path)

        try:
            with mp.AudioFileClip(raw_clip_path) as clip:
                if clip.duration > 0.1 and target_duration_sec > 0.1:
                    speed_factor = clip.duration / target_duration_sec
                    final_speed = max(0.8, min(speed_factor, 1.4))
                    current_progress = self.parent().progress_bar.value() if self.parent() and hasattr(self.parent(), 'progress_bar') else 0
                    self.progress_updated.emit(current_progress, f"Adjusting line {line_index+1} speed (x{final_speed:.2f})")
                    final_clip = vfx.speedx(clip, factor=final_speed)
                else:
                    final_clip = clip.copy()

                final_clip.write_audiofile(adjusted_clip_path, codec='mp3', logger=None)
                final_clip.close()
            self.temp_audio_files.append(adjusted_clip_path)
        finally:
            if os.path.exists(raw_clip_path): os.remove(raw_clip_path)

    async def main_tts_task(self):
        try:
            self.progress_updated.emit(0, "Parsing SRT file...")
            subs = pysubs2.load(self.srt_file_path, encoding="utf-8")
            if not subs: raise ValueError("The provided SRT file is empty or could not be parsed.")

            total_lines = len(subs)
            for i, line in enumerate(subs):
                text_to_speak = line.text.strip()
                if not text_to_speak:
                    continue 
                progress_percent = int(((i + 1) / total_lines) * 70)
                self.progress_updated.emit(progress_percent, f"Generating audio for line {i+1}/{total_lines}")
                await self.generate_and_adjust_line(text_to_speak, line.duration / 1000.0, i)

            self.progress_updated.emit(75, "Loading video and audio tracks...")
            video_clip = mp.VideoFileClip(self.video_file_path)

            audio_clips_for_composition = []
            for i, line in enumerate(subs):
                adj_clip_path = os.path.join(self.output_dir, f"temp_tts_adj_{i}.mp3")
                if os.path.exists(adj_clip_path):
                     audio_clip = mp.AudioFileClip(adj_clip_path).set_start(line.start / 1000.0)
                     audio_clips_for_composition.append(audio_clip)

            if not audio_clips_for_composition:
                if 'video_clip' in locals(): video_clip.close()
                self.error_occurred.emit("No audio clips were successfully generated.")
                return

            self.progress_updated.emit(85, "Compositing audio timeline...")
            final_audio = mp.CompositeAudioClip(audio_clips_for_composition).set_duration(video_clip.duration)

            self.progress_updated.emit(90, "Merging final audio with video...")
            final_video = video_clip.set_audio(final_audio)
            final_video.write_videofile(self.output_path, codec='libx264', audio_codec='aac', threads=os.cpu_count(), logger=None)

            final_video.close(); video_clip.close()
            for clip in audio_clips_for_composition: clip.close()
            final_audio.close()

            self.progress_updated.emit(100, "Process complete!")
            self.completion_signal.emit(self.output_path)

        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="ProEditor - TTS")
            self.error_occurred.emit(f"TTS process failed: {e}\n\nDetails saved to '{log_filename}'")
        finally:
            self.cleanup_temp_files()

    def run(self):
        """Starts the asynchronous event loop to run the TTS task."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main_tts_task())
        finally:
            loop.close()


# ==============================================================================
# Downloader Suite FRONTEND (UI)
# ==============================================================================
class DownloaderSuiteTab(QWidget):
    download_completed_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.settings = QSettings("AIOApp", "DownloaderSuite")
        self.download_path = self.settings.value("downloadPath", ".")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        downloader_group = QGroupBox("Video Downloader (Youtube, Bilibili, etc.)")
        downloader_layout = QVBoxLayout(downloader_group)
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Video URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video or playlist URL here")
        url_layout.addWidget(self.url_input)
        downloader_layout.addLayout(url_layout)

        self.get_info_button = QPushButton("Get Video Info")
        downloader_layout.addWidget(self.get_info_button)

        quality_layout = QGridLayout()
        quality_layout.addWidget(QLabel("Video Quality:"), 0, 0)
        self.video_quality_combo = QComboBox()
        quality_layout.addWidget(self.video_quality_combo, 0, 1)
        quality_layout.addWidget(QLabel("Audio Quality:"), 1, 0)
        self.audio_quality_combo = QComboBox()
        quality_layout.addWidget(self.audio_quality_combo, 1, 1)
        downloader_layout.addLayout(quality_layout)

        self.download_button = QPushButton("Download")
        downloader_layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar(alignment=Qt.AlignCenter)
        self.status_label = QLabel("Ready. Enter a URL and click 'Get Video Info'.")
        self.status_label.setStyleSheet("font-style: italic;")
        
        downloader_layout.addWidget(self.progress_bar)
        downloader_layout.addWidget(self.status_label)
        
        main_layout.addWidget(downloader_group)
        main_layout.addStretch()

        self.get_info_button.clicked.connect(self.fetch_video_info)
        self.download_button.clicked.connect(self.start_download)
        
        self.video_quality_combo.setEnabled(False)
        self.audio_quality_combo.setEnabled(False)
        self.download_button.setEnabled(False)

    def fetch_video_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a video URL.")
            return
        self.set_controls_enabled(False)
        self.status_label.setText("Fetching video information, please wait...")
        self.progress_bar.setValue(0)
        self.video_quality_combo.clear()
        self.audio_quality_combo.clear()
        self.worker = ProRecapDownloadWorker(url=url)
        self.worker.info_ready.connect(self.on_info_ready)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_info_ready(self, video_formats, audio_formats):
        self.video_quality_combo.addItems(video_formats)
        self.audio_quality_combo.addItems(audio_formats)
        self.status_label.setText("Info received. Please select formats and choose a folder to download.")
        self.set_controls_enabled(True)
        self.download_button.setEnabled(True)
        self.video_quality_combo.setEnabled(True)
        self.audio_quality_combo.setEnabled(True)

    def start_download(self):
        url = self.url_input.text().strip()
        video_format_text = self.video_quality_combo.currentText()
        audio_format_text = self.audio_quality_combo.currentText()
        if not video_format_text or not audio_format_text:
            QMessageBox.warning(self, "Warning", "Please select both video and audio formats.")
            return
        
        video_code = video_format_text.split(':')[0]
        audio_code = audio_format_text.split(':')[0]
        combined_format_code = f"{video_code}+{audio_code}"
        
        new_path = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_path)
        if not new_path: return 
            
        self.download_path = new_path
        self.settings.setValue("downloadPath", self.download_path)
        
        self.set_controls_enabled(False)
        self.status_label.setText(f"Starting download to '{self.download_path}'...")
        self.progress_bar.setValue(0)
        
        self.worker = ProRecapDownloadWorker(url=url, format_code=combined_format_code, save_path=self.download_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Downloading... {value}%")

    def on_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        self.set_controls_enabled(True)
        QMessageBox.information(self, "Success", message)
        
        latest_file = self.find_latest_downloaded_file()
        if latest_file:
            self.download_completed_signal.emit(latest_file)

    def find_latest_downloaded_file(self):
        list_of_files = glob.glob(os.path.join(self.download_path, '*.*')) 
        if not list_of_files: return None
        video_files = [f for f in list_of_files if f.lower().endswith(('.mp4', '.mkv', '.webm'))]
        if not video_files: return None
        return max(video_files, key=os.path.getctime)

    def on_error(self, error_message):
        self.status_label.setText("An error occurred.")
        self.set_controls_enabled(True)
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, "Error", error_message)

    def set_controls_enabled(self, enabled):
        self.get_info_button.setEnabled(enabled)
        self.download_button.setEnabled(enabled)
        self.url_input.setEnabled(enabled)
        self.video_quality_combo.setEnabled(enabled)
        self.audio_quality_combo.setEnabled(enabled)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

# ==============================================================================
# ProEditor Suite FRONTEND (UI - Now REFINED with QGridLayout)
# ==============================================================================
class ProEditorSuiteTab(QWidget):
    # ***** MODIFICATION START *****
    # The constructor now accepts the list of API keys directly.
    def __init__(self, api_keys):
        super().__init__()
        self.api_keys = api_keys # Store the API keys.
        self.color_map={'အနက်':'000000','အဖြူ':'FFFFFF','အဝါ':'FFFF00','အပြာ':'0000FF','အစိမ်း':'00FF00','အနီ':'FF0000','မီးခိုး':'808080','အပြာနု':'F0CAA6'}
        self.results={'original_video':None,'en_srt':None,'my_srt':None,'processed_video':None,'hardsub_video':None, 'final_video_with_tts':None}
        self.processor_thread = None

        self.init_ui()
        self.load_processor_settings()
    # ***** MODIFICATION END *****
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        processor_group = QGroupBox("ProEditor Workflow")
        processor_layout = QVBoxLayout(processor_group)

        file_layout=QHBoxLayout()
        file_layout.addWidget(QLabel("ဗီဒီယို ဖိုင်:"))
        self.proc_input_path_edit=QLineEdit()
        self.proc_input_path_edit.setReadOnly(True)
        self.proc_input_path_edit.setPlaceholderText("Select a video below or download one from the 'Downloader' tab")
        self.proc_browse_file_button=QPushButton("ဗီဒီယိုရွေးရန်..."); self.proc_browse_file_button.clicked.connect(self.browse_processor_file)
        file_layout.addWidget(self.proc_input_path_edit); file_layout.addWidget(self.proc_browse_file_button); processor_layout.addLayout(file_layout)

        options_layout_container = QHBoxLayout()
        
        self.proc_options_group=QGroupBox("Workflow Steps"); options_layout=QVBoxLayout()
        self.proc_translate_checkbox=QCheckBox("Translate to Burmese (Requires Key)"); self.proc_translate_checkbox.setChecked(True); options_layout.addWidget(self.proc_translate_checkbox)
        self.proc_process_video_checkbox=QCheckBox("Process Video (Flip, Ratio, Mute, Logo)"); self.proc_process_video_checkbox.setChecked(True); options_layout.addWidget(self.proc_process_video_checkbox)
        self.proc_hardsub_checkbox=QCheckBox("Burn Subtitles into Video"); self.proc_hardsub_checkbox.setChecked(True); options_layout.addWidget(self.proc_hardsub_checkbox)
        self.proc_add_tts_checkbox=QCheckBox("Add Voice-over (Replaces Audio)"); self.proc_add_tts_checkbox.setChecked(False); options_layout.addWidget(self.proc_add_tts_checkbox)
        self.proc_options_group.setLayout(options_layout)
        options_layout_container.addWidget(self.proc_options_group)

        self.proc_settings_group=QGroupBox("Settings")
        settings_grid_layout = QGridLayout()
        
        settings_grid_layout.addWidget(QLabel("Whisper Model:"), 0, 0)
        self.proc_model_combo=QComboBox(); self.proc_model_combo.addItems(["tiny","base","small","medium","large-v3"]); self.proc_model_combo.setCurrentText("medium")
        settings_grid_layout.addWidget(self.proc_model_combo, 0, 1)

        settings_grid_layout.addWidget(QLabel("Aspect Ratio:"), 1, 0)
        self.proc_ratio_combo=QComboBox(); self.proc_ratio_combo.addItems(["9:16 (TikTok/Shorts)","1:1 (Square)","4:3 (Classic)","Keep Original"])
        settings_grid_layout.addWidget(self.proc_ratio_combo, 1, 1)

        settings_grid_layout.addWidget(QLabel("Video Flip:"), 2, 0)
        self.proc_flip_combo=QComboBox(); self.proc_flip_combo.addItems(["Horizontal","Vertical","None"])
        settings_grid_layout.addWidget(self.proc_flip_combo, 2, 1)
        
        self.proc_logo_checkbox = QGroupBox("Logo / Watermark"); self.proc_logo_checkbox.setCheckable(True); self.proc_logo_checkbox.setChecked(False); logo_layout = QVBoxLayout()
        logo_file_layout = QHBoxLayout(); logo_file_layout.addWidget(QLabel("Logo Image:")); self.proc_logo_path_edit = QLineEdit(); self.proc_logo_path_edit.setReadOnly(True); self.proc_logo_browse_btn = QPushButton("Browse..."); self.proc_logo_browse_btn.clicked.connect(self.browse_logo_file); logo_file_layout.addWidget(self.proc_logo_path_edit); logo_file_layout.addWidget(self.proc_logo_browse_btn); logo_layout.addLayout(logo_file_layout)
        logo_opts_layout = QHBoxLayout(); logo_opts_layout.addWidget(QLabel("Position:")); self.proc_logo_pos_combo = QComboBox(); self.proc_logo_pos_combo.addItems(["Top Right", "Top Left", "Top Center", "Bottom Right", "Bottom Left", "Bottom Center"]); logo_opts_layout.addWidget(self.proc_logo_pos_combo); logo_opts_layout.addStretch(); logo_opts_layout.addWidget(QLabel("Size:")); self.proc_logo_size_slider = QSlider(Qt.Horizontal); self.proc_logo_size_slider.setRange(5, 30); self.proc_logo_size_slider.setValue(15); self.proc_logo_size_slider.setFixedWidth(100); self.proc_logo_size_slider.valueChanged.connect(lambda v: self.proc_logo_size_label.setText(f'{v}%')); self.proc_logo_size_label = QLabel("15%"); logo_opts_layout.addWidget(self.proc_logo_size_slider); logo_opts_layout.addWidget(self.proc_logo_size_label); logo_layout.addLayout(logo_opts_layout)
        self.proc_logo_checkbox.setLayout(logo_layout)
        settings_grid_layout.addWidget(self.proc_logo_checkbox, 3, 0, 1, 2)
        
        settings_grid_layout.addWidget(QLabel("Subtitle Style:"), 4, 0)
        self.proc_subtitle_style_combo = QComboBox(); self.proc_subtitle_style_combo.addItems(["Cumulative (Recommended)", "Sequential (Word by Word)"])
        settings_grid_layout.addWidget(self.proc_subtitle_style_combo, 4, 1)

        settings_grid_layout.addWidget(QLabel("Subtitle BG Color:"), 5, 0)
        self.proc_color_combo=QComboBox(); self.proc_color_combo.addItems(self.color_map.keys())
        settings_grid_layout.addWidget(self.proc_color_combo, 5, 1)

        settings_grid_layout.addWidget(QLabel("BG Opacity:"), 6, 0)
        opacity_layout = QHBoxLayout()
        self.proc_opacity_slider=QSlider(Qt.Horizontal); self.proc_opacity_slider.setRange(0,100); self.proc_opacity_slider.setValue(80); self.proc_opacity_slider.valueChanged.connect(lambda v: self.proc_opacity_value_label.setText(f'{v}%')); self.proc_opacity_value_label=QLabel("80%")
        opacity_layout.addWidget(self.proc_opacity_slider)
        opacity_layout.addWidget(self.proc_opacity_value_label)
        settings_grid_layout.addLayout(opacity_layout, 6, 1)
        
        self.proc_tts_settings_group = QGroupBox("Voice Settings"); tts_settings_layout = QVBoxLayout()
        tts_voice_layout = QHBoxLayout(); tts_settings_layout.addWidget(QLabel("Voice Type:")); self.proc_tts_voice_combo = QComboBox(); self.proc_tts_voice_combo.addItems(TTS_VOICE_MAPPING.keys()); self.proc_tts_voice_combo.setCurrentText(DEFAULT_TTS_VOICE); tts_voice_layout.addWidget(self.proc_tts_voice_combo); tts_settings_layout.addLayout(tts_voice_layout)
        tts_rate_layout = QHBoxLayout(); tts_settings_layout.addWidget(QLabel("Voice Speed:")); self.proc_tts_rate_slider = QSlider(Qt.Horizontal); self.proc_tts_rate_slider.setRange(-100,100); self.proc_tts_rate_slider.setValue(0); self.proc_tts_rate_slider.valueChanged.connect(lambda v: self.proc_tts_rate_label.setText(f'{v:+}%')); self.proc_tts_rate_label = QLabel("+0%"); tts_rate_layout.addWidget(self.proc_tts_rate_slider); tts_rate_layout.addWidget(self.proc_tts_rate_label); tts_settings_layout.addLayout(tts_rate_layout)
        self.proc_tts_settings_group.setLayout(tts_settings_layout)
        self.proc_tts_settings_group.setVisible(self.proc_add_tts_checkbox.isChecked()); self.proc_add_tts_checkbox.toggled.connect(self.proc_tts_settings_group.setVisible)
        settings_grid_layout.addWidget(self.proc_tts_settings_group, 7, 0, 1, 2)

        settings_grid_layout.addWidget(QLabel("Final Output Name:"), 8, 0)
        self.proc_output_path_edit=QLineEdit("final_video.mp4")
        settings_grid_layout.addWidget(self.proc_output_path_edit, 8, 1)

        settings_grid_layout.setColumnStretch(1, 1)
        self.proc_settings_group.setLayout(settings_grid_layout)
        options_layout_container.addWidget(self.proc_settings_group)
        processor_layout.addLayout(options_layout_container)
        
        self.proc_start_button=QPushButton("Start Workflow"); self.proc_start_button.setObjectName("proEditorStartButton"); self.proc_start_button.clicked.connect(self.start_master_process); processor_layout.addWidget(self.proc_start_button)
        processor_layout.addStretch()
        self.proc_progress_bar=QProgressBar(alignment=Qt.AlignCenter); processor_layout.addWidget(self.proc_progress_bar)
        self.proc_status_label=QLabel("Ready."); self.proc_status_label.setStyleSheet("font-style:italic;"); processor_layout.addWidget(self.proc_status_label)
        self.proc_logo_checkbox.toggled.connect(self.save_processor_settings)

        main_layout.addWidget(processor_group)
        self.setLayout(main_layout)

    def load_processor_settings(self):
        settings = QSettings("AIOApp", "ProEditorSuite")
        self.proc_logo_path_edit.setText(settings.value("logo_path", ""))
        is_logo_enabled = settings.value("logo_enabled", False, type=bool)
        if not self.proc_logo_path_edit.text(): is_logo_enabled = False
        self.proc_logo_checkbox.setChecked(is_logo_enabled)

    def save_processor_settings(self):
        settings = QSettings("AIOApp", "ProEditorSuite")
        settings.setValue("logo_path", self.proc_logo_path_edit.text())
        settings.setValue("logo_enabled", self.proc_logo_checkbox.isChecked())

    def browse_processor_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.mkv *.avi)")
        if path: self.proc_input_path_edit.setText(path)

    def browse_logo_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo File", "", "Image Files (*.png *.jpg *.jpeg)")
        if path: self.proc_logo_path_edit.setText(path); self.save_processor_settings()

    def set_input_video_path(self, path):
        """Public slot to receive a file path from another tab (like the Downloader)."""
        self.proc_input_path_edit.setText(path)
        QMessageBox.information(self, "File Path Updated", f"Downloaded video path has been set in ProEditor:\n{path}")


    def start_master_process(self):
        # ***** MODIFICATION START *****
        # Directly use the stored API keys.
        api_keys_list = self.api_keys
        # ***** MODIFICATION END *****

        self.results = {k:None for k in self.results}; self.results['original_video']=self.proc_input_path_edit.text()
        if not self.results['original_video']: QMessageBox.warning(self, "Input Error", "Please select a video file."); return
        
        if (self.proc_translate_checkbox.isChecked() or self.proc_add_tts_checkbox.isChecked()) and not api_keys_list:
            QMessageBox.critical(self,"Error",f"Translation/TTS is enabled, but no API keys were found in {os.path.basename(PODCAST_CONFIG_FILE)}."); return

        if self.proc_add_tts_checkbox.isChecked() and not self.proc_translate_checkbox.isChecked(): QMessageBox.warning(self, "Workflow Error", "To add TTS, the 'Translate to Burmese' option must also be checked."); return

        handbrake_cli_path = os.path.join(FILE_DIR, "HandBrakeCLI.exe")
        if self.proc_hardsub_checkbox.isChecked() and not os.path.exists(handbrake_cli_path):
            QMessageBox.critical(self, "Error", f"HandBrakeCLI.exe not found in the '{os.path.basename(FILE_DIR)}' subdirectory.")
            return
        if self.proc_logo_checkbox.isChecked() and not self.proc_logo_path_edit.text(): QMessageBox.warning(self,"Input Error","Logo is enabled, but no logo image was selected."); return

        self.set_processor_ui_state(is_running=True); self.update_processor_status("Step 1: Generating English SRT...",0)
        worker=ProRecapTranscriptionWorker(self.results['original_video'],self.proc_model_combo.currentText())
        self._run_processor_worker(worker, self.on_transcription_complete, is_tts=False)

    def on_transcription_complete(self, en_srt_path):
        self.results['en_srt'] = en_srt_path
        if self.proc_translate_checkbox.isChecked():
            # ***** MODIFICATION START *****
            # Directly use the stored API keys.
            api_keys_list = self.api_keys
            # ***** MODIFICATION END *****
            
            self.update_processor_status("Step 2: Translating to Burmese...", 25)
            worker=ProRecapTranslationWorker(en_srt_path, api_keys_list)
            self._run_processor_worker(worker,self.on_translation_complete, is_tts=False)
        else:
            self.on_translation_complete(None) # Skip to next step

    def on_translation_complete(self, my_srt_path):
        self.results['my_srt'] = my_srt_path
        if self.proc_process_video_checkbox.isChecked():
            self.update_processor_status("Step 3: Processing video (ratio, flip, logo)...", 50)
            logo_options={'enabled':self.proc_logo_checkbox.isChecked(),'path':self.proc_logo_path_edit.text(),'position':self.proc_logo_pos_combo.currentText(),'size':self.proc_logo_size_slider.value()}
            worker=ProRecapVideoProcessingWorker(self.results['original_video'], self.proc_ratio_combo.currentText(), self.proc_flip_combo.currentText(), logo_options)
            self._run_processor_worker(worker, self.on_video_processing_complete, is_tts=False)
        else:
            self.on_video_processing_complete(self.results['original_video']) # Use original video if not processing

    def on_video_processing_complete(self, processed_video_path):
        self.results['processed_video'] = processed_video_path
        srt_for_hardsub = self.results['my_srt'] or self.results['en_srt']
        if self.proc_hardsub_checkbox.isChecked() and srt_for_hardsub and processed_video_path:
            self.update_processor_status("Step 4: Burning subtitles into video...", 75)
            base_dir=os.path.dirname(self.results['original_video']); output_path=os.path.join(base_dir,self.proc_output_path_edit.text())
            color_hex = self.color_map[self.proc_color_combo.currentText()].replace("#","")
            subtitle_style = self.proc_subtitle_style_combo.currentText()
            worker=ProRecapHardsubWorker(processed_video_path,srt_for_hardsub,output_path,color_hex,self.proc_opacity_slider.value(), subtitle_style)
            self._run_processor_worker(worker,self.on_hardsub_complete, is_tts=False)
        else:
            self.on_hardsub_complete(None)

    def on_hardsub_complete(self, hardsub_video_path):
        self.results['hardsub_video'] = hardsub_video_path
        if self.proc_add_tts_checkbox.isChecked():
            self.start_tts_process()
        else:
            self.show_final_summary()
            self.reset_processor_ui_state()

    def start_tts_process(self):
        video_for_tts = self.results['hardsub_video'] or self.results['processed_video'] or self.results['original_video']
        if not self.results['my_srt'] or not video_for_tts:
            self.on_processor_error("Could not start TTS. Missing translated SRT (.my.srt) or a valid video file.")
            return

        self.update_processor_status("Step 5: Adding Timed Voice-over...", 90)
        base, _ = os.path.splitext(video_for_tts)
        output_path = f"{base}_with_TTS.mp4"
        voice_key = self.proc_tts_voice_combo.currentText()
        voice_id = TTS_VOICE_MAPPING[voice_key]
        rate = self.proc_tts_rate_slider.value()

        worker = ProRecapTTSWorker(self.results['my_srt'], video_for_tts, voice_id, rate, output_path)
        self._run_processor_worker(worker, self.on_tts_complete, is_tts=True)

    def on_tts_complete(self, tts_video_path):
        self.results['final_video_with_tts'] = tts_video_path
        self.show_final_summary()
        self.reset_processor_ui_state()

    def _run_processor_worker(self, worker, on_complete_slot, is_tts):
        self.processor_thread=worker
        worker.setParent(self) 
        worker.error_occurred.connect(self.on_processor_error)
        if hasattr(worker,'completion_signal'): worker.completion_signal.connect(on_complete_slot)
        if is_tts:
            worker.progress_updated.connect(lambda val, msg: self.update_processor_status(msg, val))
        else:
            if hasattr(worker,'progress_updated'): worker.progress_updated.connect(self.update_processor_progress)
            if hasattr(worker,'status_message'): worker.status_message.connect(self.update_status_no_progress)
        worker.start()

    def show_final_summary(self):
        message="✅ All selected processes completed!\n"
        final_video = self.results.get('final_video_with_tts')
        hardsub_video = self.results.get('hardsub_video')
        processed_video = self.results.get('processed_video')

        if final_video: message+=f"\n🏆 Final Video with TTS:\n{final_video}\n"
        elif hardsub_video: message+=f"\n🎬 Final Hardsubbed Video:\n{hardsub_video}\n"
        elif processed_video: message+=f"\n🎞️ Processed Video (No Subs/TTS):\n{processed_video}\n"
        else: message+=f"\n🤷 No final video was produced based on selections.\n"

        message+="\n--- Generated Files ---\n"
        if self.results['en_srt']: message+=f"📄 English SRT: {os.path.basename(self.results['en_srt'])}\n"
        if self.results['my_srt']: message+=f"📄 Burmese SRT: {os.path.basename(self.results['my_srt'])}\n"
        QMessageBox.information(self, "Success", message)

    def on_processor_error(self, message):
        QMessageBox.critical(self, "Error", f"An error occurred:\n{message}")
        self.reset_processor_ui_state()

    def set_processor_ui_state(self, is_running): self.proc_start_button.setEnabled(not is_running); self.proc_browse_file_button.setEnabled(not is_running)
    def reset_processor_ui_state(self): self.set_processor_ui_state(is_running=False); self.proc_progress_bar.setValue(0); self.proc_progress_bar.setFormat(""); self.proc_status_label.setText("Ready.")
    def update_processor_progress(self, value): self.proc_progress_bar.setValue(value)
    def update_processor_status(self, message, progress): self.proc_status_label.setText(message); self.proc_progress_bar.setValue(progress); self.proc_progress_bar.setFormat(f"{message} - %p%")
    def update_status_no_progress(self, message): self.proc_status_label.setText(message); self.proc_progress_bar.setFormat(message)

    def closeEvent(self, event):
        if self.processor_thread and isinstance(self.processor_thread, ProRecapTTSWorker):
            self.processor_thread.cleanup_temp_files()
        event.accept()

# ==============================================================================
# Main GUI Application Class
# ==============================================================================
class PerchanceGeneratorApp(QMainWindow):
    CACHE_DIR = '.cache'
    GRID_COLUMNS = 4

    def __init__(self, user):
        super().__init__()
        self.user = user 
        self.setWindowTitle(f"AI Director Suite (All-In-One) - Logged in as: {self.user['email']}")
        self.setGeometry(50, 50, 1400, 900)
        
        # MODIFIED: Set the application icon if it exists
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        
        self.api_keys = []
        self.image_previews = []
        self.generated_story_data = []
        self.character_map = {}

        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
            
        self.load_api_keys_from_config() 
        self.init_ui()
        self.setup_logging()
    
    def load_api_keys_from_config(self):
        config = configparser.ConfigParser()
        # MODIFIED: Use the centrally defined path for the config file
        if not os.path.exists(PODCAST_CONFIG_FILE):
            # MODIFIED: Update the warning message to reflect the new path
            info_logger.warning(f"'{os.path.join('data', 'config.ini')}' not found. API features will not work.")
            return
        
        config.read(PODCAST_CONFIG_FILE)
        if 'APIKeys' in config:
            sorted_keys = sorted(config['APIKeys'].items(), key=lambda x: x[0])
            self.api_keys = [value.strip() for key, value in sorted_keys if value.strip()]
            
            if self.api_keys:
                info_logger.info(f"Successfully loaded {len(self.api_keys)} API key(s) from config.ini.")
            else:
                info_logger.warning("Found [APIKeys] section in config.ini, but it contains no valid keys.")
        else:
            info_logger.warning("Could not find [APIKeys] section in config.ini.")

    def init_ui(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        controls_scroll_area = QScrollArea()
        controls_scroll_area.setWidgetResizable(True)
        controls_widget = QWidget()
        controls_scroll_area.setWidget(controls_widget)
        controls_layout = QVBoxLayout(controls_widget)
        director_group = QGroupBox("အဆင့် ၁: AI Director (Gemini ဖြင့် ဇာတ်လမ်းဖန်တီးပါ)")
        director_layout = QVBoxLayout(director_group)
        
        director_layout.addWidget(QLabel("ဇာတ်လမ်းစိတ်ကူး (Story Idea):"))
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("ဥပမာ- အိမ်ကိုလွမ်းနေသော ကောင်လေးတစ်ယောက်")
        self.script_input.setFixedHeight(100)
        director_layout.addWidget(self.script_input)

        director_layout.addWidget(QLabel("<b>ဇာတ်လမ်းပုံစံ निवရန် (Choose Story Style):</b>"))
        self.story_style_combo = QComboBox()
        self.story_style_combo.addItems([
            "အနုပညာမြောက် ဇာတ်လမ်းတို (Literary Short Story)",
            "ရုပ်ရှင်ဇာတ်ညွှန်း - အသေးစိတ် (Cinematic Screenplay)",
            "ကဗျာဆန်သော ဇာတ်ကြောင်း (Poetic Narrative)",
            "လึกลับစုံထောက်ပုံစံ (Gritty Noir / Mystery)",
            "ဒဏ္ဍာရီဆန်သော ရာဇဝင်ပုံပြင် (Mythological Tale)"
        ])
        director_layout.addWidget(self.story_style_combo)

        self.generate_prompts_button = QPushButton("✅ ဇာတ်လမ်းဖန်တီးမည်")
        self.generate_prompts_button.clicked.connect(self.generate_story_and_prompts)
        director_layout.addWidget(self.generate_prompts_button)
        self.save_script_button = QPushButton("💾 Script (TXT & SRT) သိမ်းမည်")
        self.save_script_button.clicked.connect(self.save_script_files)
        self.save_script_button.setEnabled(False)
        director_layout.addWidget(self.save_script_button)
        controls_layout.addWidget(director_group)
        prompts_group = QGroupBox("အဆင့် ၂: ပုံထုတ်ရန် Prompt များ (ပြင်ဆင်နိုင်ပါသည်)")
        prompts_layout = QVBoxLayout(prompts_group)
        textBoxStyle = "QTextEdit { background-color: #3C3C3C; border: 1px solid #CCCCCC; border-radius: 8px; padding: 8px; font-size: 10pt; color: #E0E0E0; } QTextEdit:focus { border: 2px solid #4D90FE; }"
        self.prompt_input = QTextEdit()
        self.prompt_input.setStyleSheet(textBoxStyle)
        self.prompt_input.setPlaceholderText("Prompt(s)...")
        self.prompt_input.textChanged.connect(self.update_ui_for_prompt)
        prompts_layout.addWidget(self.prompt_input)
        self.neg_prompt_input = QTextEdit()
        self.neg_prompt_input.setStyleSheet(textBoxStyle)
        self.neg_prompt_input.setPlaceholderText("Negative Prompt...")
        prompts_layout.addWidget(self.neg_prompt_input)
        controls_layout.addWidget(prompts_group)
        settings_group = QGroupBox("အဆင့် ၃: ပုံထုတ်လုပ်ခြင်းဆိုင်ရာ Settings")
        settings_form_layout = QFormLayout(settings_group)
        self.style_combo = QComboBox()
        self.style_combo.addItems(list(styles.keys()))
        self.style_combo.setCurrentText("Cinematic (Default)")
        settings_form_layout.addRow(QLabel("<b>Image Style:</b>"), self.style_combo)
        self.resolution_combo = QComboBox()
        self.resolution_combo.setEditable(True)
        self.resolution_combo.addItems(["512x768 (Portrait 2:3)", "768x512 (Landscape 3:2)", "512x512 (Square 1:1)", "1024x1024 (Square HD)", "1024x576 (Widescreen 16:9)"])
        settings_form_layout.addRow(QLabel("<b>Resolution:</b>"), self.resolution_combo)
        self.detected_scenes_label = QLabel("N/A")
        font = self.detected_scenes_label.font()
        font.setBold(True)
        self.detected_scenes_label.setFont(font)
        settings_form_layout.addRow(QLabel("Detected Scenes:"), self.detected_scenes_label)
        self.image_count_spin = QSpinBox()
        self.image_count_spin.setMinimum(1)
        settings_form_layout.addRow(QLabel("<b>Images per Prompt (Single Mode):</b>"), self.image_count_spin)

        controls_layout.addWidget(settings_group)
        controls_layout.addStretch()
        self.image_generate_button = QPushButton("ပုံဖန်တီးမည် (Generate)")
        self.image_generate_button.setObjectName("imageGenerateButton")
        self.image_generate_button.clicked.connect(self.start_generation)
        controls_layout.addWidget(self.image_generate_button)
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        right_side_tabs = QTabWidget()
        self.generated_prompts_preview = QTextEdit()
        self.generated_prompts_preview.setReadOnly(True)
        image_preview_widget = QWidget()
        image_preview_layout = QVBoxLayout(image_preview_widget)
        self.save_controls_widget = QWidget()
        save_layout = QHBoxLayout(self.save_controls_widget)
        save_layout.setContentsMargins(0, 5, 0, 5)
        self.select_all_button = QPushButton("Select All")
        self.deselect_all_button = QPushButton("Deselect All")
        self.save_selected_button = QPushButton("Save Selected Images...")
        self.save_selected_button.setObjectName("saveSelectedButton")
        save_layout.addWidget(self.select_all_button)
        save_layout.addWidget(self.deselect_all_button)
        save_layout.addStretch()
        save_layout.addWidget(self.save_selected_button)
        self.save_controls_widget.setVisible(False)
        self.select_all_button.clicked.connect(self.select_all_images)
        self.deselect_all_button.clicked.connect(self.deselect_all_images)
        self.save_selected_button.clicked.connect(self.save_selected_images)
        image_preview_layout.addWidget(QLabel("<b>Generated Image Previews:</b>"))
        image_preview_layout.addWidget(self.save_controls_widget)
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidgetResizable(True)
        self.image_display_widget = QWidget()
        self.image_display_layout = QGridLayout(self.image_display_widget)
        self.image_display_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.image_scroll_area.setWidget(self.image_display_widget)
        image_preview_layout.addWidget(self.image_scroll_area)

        self.video_suite_tab = VideoSuiteTab()
        # ***** MODIFICATION START *****
        # Pass the loaded API keys to the tabs that need them.
        self.podcast_suite_tab = PodcastSuiteTab(api_keys=self.api_keys)
        self.pro_editor_tab = ProEditorSuiteTab(api_keys=self.api_keys)
        # ***** MODIFICATION END *****
        self.downloader_tab = DownloaderSuiteTab()

        right_side_tabs.addTab(self.generated_prompts_preview, "AI Director")
        right_side_tabs.addTab(image_preview_widget, "Generated Images")
        right_side_tabs.addTab(self.video_suite_tab, "Video Suite")
        right_side_tabs.addTab(self.podcast_suite_tab, "Podcast Suite")
        right_side_tabs.addTab(self.downloader_tab, "Downloader")
        right_side_tabs.addTab(self.pro_editor_tab, "ProEditor Suite") 

        self.downloader_tab.download_completed_signal.connect(self.pro_editor_tab.set_input_video_path)

        output_layout.addWidget(right_side_tabs)
        main_layout.addWidget(controls_scroll_area, 1)
        main_layout.addWidget(output_widget, 2)

    def logout(self):
        """Clears stored credentials and restarts the application."""
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to log out?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            settings = QSettings("AIOApp", "Auth")
            settings.remove("refreshToken")
            self.close()
            QProcess.startDetached(sys.executable, sys.argv)

    def setup_logging(self):
        pass

    def update_ui_for_prompt(self):
        is_story = '📌' in self.prompt_input.toPlainText()
        self.image_count_spin.setEnabled(not is_story)
        if is_story:
            scene_count = self.prompt_input.toPlainText().count('📌')
            self.detected_scenes_label.setText(f"{scene_count} scenes found")
        else:
            self.detected_scenes_label.setText("Single Prompt Mode")

    @qasync.asyncSlot()
    async def generate_story_and_prompts(self):
        if not self.api_keys:
            QMessageBox.warning(self, "API Key Missing", f"Could not find any API keys in {os.path.join('data', 'config.ini')}'s [APIKeys] section.")
            return
        story_idea = self.script_input.toPlainText().strip()
        if not story_idea:
            QMessageBox.warning(self, "Story Idea Missing", "Please enter a story idea.")
            return

        self.generate_prompts_button.setEnabled(False)
        self.generate_prompts_button.setText("AI ဖန်တီးနေသည်...")
        self.generated_prompts_preview.setPlainText("Gemini မှ ဇာတ်လမ်းနှင့် ပုံအတွက် prompt များကို ဖန်တီးနေပါသည်... ဤအဆင့်သည် ပိုမိုကြာမြင့်နိုင်ပါသည်...")
        self.save_script_button.setEnabled(False)

        selected_style = self.story_style_combo.currentText()
        meta_prompt = ""

        if "Literary" in selected_style:
            meta_prompt = f"""
            You are an award-winning Burmese author, a modern master of the short story, revered for your profound, captivating, and poetic prose. Your objective is to elevate a simple user idea into a complete, emotionally resonant, and plot-driven short story.
            **STORY DEPTH, PLOT, AND LENGTH REQUIREMENT (NON-NEGOTIABLE):**
            - **Substantial Length:** The story must be a complete narrative, substantially longer than a few paragraphs. Aim for a word count appropriate for a full short story (e.g., 800-1200 words).
            - **Develop a Plot:** Do not just describe a single moment or feeling. You must create a plot. Give the character a clear **background**, a **reason** for their current situation (e.g., Why are they in the city?), and a **goal** (e.g., to earn money for family).
            - **Show, Don't Just Tell:** The story must be built around a series of **events, encounters, and internal reflections.**
            - **Introduce Minor Characters:** Add one or two minor characters that the narrator interacts with.
            - **Complex Emotional Arc:** The character's emotions must evolve. Show moments of frustration, fleeting hope, determination, weariness, and perhaps small, unexpected joys.
            **Core Principles of Your Literary Craft (Mandatory):**
            - **"Show, Don't Tell" in Action:** Instead of saying 'he missed his mother's cooking,' describe him eating a cheap, tasteless city meal and have that sensory experience trigger a vivid, detailed memory of a specific meal his mother once made for him.
            - **Masterful Pacing:** Vary your sentence structure.
            - **Figurative Language:** Weave metaphors, similes, and personification into the narrative.
            - **Powerful Narrative Arc:** The story must have a compelling beginning (a hook), a middle that builds tension, and a thoughtful, resonant conclusion.
            **Benchmark for Literary Quality (Your standard of excellence):**
            "တစ်နေ့မှာတော့ အရာအားလုံး ပြောင်းလဲသွားတယ်။ ကောင်းကင်ကြီးက ရုတ်တရက် မည်းမှောင်လာသလိုပဲ။ ... ကျွန်တော်တို့ရဲ့ ငြိမ်းချမ်းတဲ့ရွာလေးဟာ သုဿန်တစ်ခုလို ဖြစ်သွားတယ်။"
            ***Your writing must surpass this benchmark.***
            **Technical Requirements:**
            - **Language/Perspective:** Flawless, literary **BURMESE** in the first-person.
            - **Character Consistency:** Provide a `<character_sheet>` in **ENGLISH** with a physical description. This **MUST** be used in every `<prompt_english>`.
            - **Output Format:** <story_block><paragraph_burmese>[A paragraph]</paragraph_burmese><prompt_english>[A prompt]</prompt_english></story_block>
            **User's Story Idea:** {story_idea}
            Begin writing a masterpiece.
            """
        elif "Screenplay" in selected_style:
            meta_prompt = f"""
            You are a professional screenwriter, renowned for your ability to create vivid, emotionally resonant scenes. Your task is to turn a story idea into a high-quality, detailed screenplay.
            **CORE PRINCIPLE: VISUAL & EMOTIONAL STORYTELLING.** Your script must be so descriptive that a director can see the movie in their mind.
            - **Length & Plot:** Write a complete story with a full narrative arc, containing multiple scenes. It must have a beginning, middle, and end.
            - **Evocative Action Lines:** The 'action' section is not just for listing events. Use it to describe the setting's atmosphere, the character's body language, and the subtext of the scene. Show the character's feelings through their actions.
            - **Natural Dialogue:** Dialogue must sound like real people talking, revealing their personality and advancing the plot.
            **Technical Requirements:**
            - The screenplay (headings, action, dialogue) must be in **BURMESE**. The prompts must be in **ENGLISH**.
            - **Character Consistency:** Provide a `<character_sheet>` in **ENGLISH** with a physical description. This **MUST** be used in every `<prompt>`.
            - **Output Format (Strictly):**
              <scene_block>
              <scene_heading>မြင်ကွင်း - [Scene Number]။ [LOCATION] - [TIME OF DAY]</scene_heading>
              <action>[Highly descriptive and evocative scene and character actions in BURMESE.]</action>
              <dialogue>[Natural-sounding dialogue in BURMESE.]</dialogue>
              <prompt>[A detailed visual prompt in ENGLISH based on the scene's action and mood.]</prompt>
              </scene_block>
            **User's Story Idea:** {story_idea}
            Write the screenplay.
            """
        elif "Poetic" in selected_style:
            meta_prompt = f"""
            You are a poet who writes prose. Your goal is to capture a feeling, a moment, or a memory in the most beautiful, lyrical language possible. Plot is secondary to emotion and imagery.
            **CORE PRINCIPLE: LANGUAGE IS EVERYTHING.**
            - **Lyrical Prose:** Your writing must flow like a poem. Focus on the rhythm, sound, and musicality of the Burmese language.
            - **Figurative Language:** This is essential. The story must be rich with metaphors, similes, personification, and powerful imagery.
            - **Emotional Core:** Focus on a single, powerful emotion or theme (like nostalgia, loss, or joy) and explore it from different angles.
            - **Sensory Details:** Describe sights, sounds, and feelings in an abstract, artistic way.
            **Technical Requirements:**
            - **Language/Perspective:** Lyrical, beautiful **BURMESE** in the first-person.
            - **Character Consistency:** Provide a `<character_sheet>` in **ENGLISH** with a physical description. Use it in every `<prompt_english>`.
            - **Output Format:** <story_block><paragraph_burmese>[A paragraph of your poetic prose.]</paragraph_burmese><prompt_english>[An artistic and atmospheric prompt in ENGLISH.]</prompt_english></story_block>
            **User's Story Idea:** {story_idea}
            Create a work of art.
            """
        elif "Noir" in selected_style:
            meta_prompt = f"""
            You are a classic noir writer. Your world is one of shadows, moral ambiguity, and existential dread. Your task is to turn an idea into a gritty, atmospheric noir story.
            **CORE PRINCIPLE: MOOD AND ATMOSPHERE.**
            - **Setting the Scene:** The environment is a character. Describe rain-slicked streets, oppressive heat, dimly lit rooms, and the ever-present shadows.
            - **Cynical Narrator:** The first-person narrator should be world-weary, cynical, and introspective. Their observations about the world are sharp and often pessimistic.
            - **Pacing:** Use short, punchy sentences mixed with longer, reflective passages. The dialogue should be sharp and minimalistic.
            - **Plot:** The story must revolve around a central problem, a mystery, or a moral dilemma that the character cannot easily solve.
            **Technical Requirements:**
            - **Language/Perspective:** Gritty, cynical **BURMESE** in the first-person.
            - **Character Consistency:** Provide a `<character_sheet>` in **ENGLISH** with a physical description. Use it in every `<prompt_english>`.
            - **Output Format:** <story_block><paragraph_burmese>[A paragraph of your gritty noir story.]</paragraph_burmese><prompt_english>[A dark, high-contrast, atmospheric prompt in ENGLISH.]</prompt_english></story_block>
            **User's Story Idea:** {story_idea}
            Show me the darkness.
            """
        elif "Mythological" in selected_style:
            meta_prompt = f"""
            You are an ancient storyteller, a chronicler of myths and legends. Your voice is grand and timeless. Your task is to transform a simple idea into a heroic, mythological tale.
            **CORE PRINCIPLE: AN EPIC SCALE.**
            - **Elevated Language:** Use formal, grand, and majestic Burmese. The tone should be serious and momentous, as if recounting a sacred history.
            - **Grand Scale:** Describe legendary landscapes, heroic deeds, divine interventions, and powerful emotions on a grand scale. The stakes must feel high.
            - **Symbolism:** The story should be rich with symbolism. Characters and events represent larger ideas like courage, fate, or sacrifice.
            - **Timeless Quality:** The narrative should feel as if it has been passed down through generations.
            **Technical Requirements:**
            - **Language:** Formal, epic **BURMESE**.
            - **Character Consistency:** Provide a `<character_sheet>` in **ENGLISH** describing the hero in epic terms. Use this in every `<prompt_english>`.
            - **Output Format:** <story_block><paragraph_burmese>[A paragraph of your epic tale.]</paragraph_burmese><prompt_english>[A grand, majestic, and legendary prompt in ENGLISH.]</prompt_english></story_block>
            **User's Story Idea:** {story_idea}
            Recount the legend.
            """

        full_response_text = None
        last_error = None
        
        for api_key in self.api_keys:
            try:
                info_logger.info(f"Attempting story generation with key ending in...{api_key[-4:]}")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = await model.generate_content_async(meta_prompt)
                full_response_text = response.text
                info_logger.info(f"Key ...{api_key[-4:]} succeeded.")
                break 
            except (google_exceptions.PermissionDenied, google_exceptions.ResourceExhausted, google_exceptions.Unauthenticated) as e:
                last_error = e
                info_logger.warning(f"Key ...{api_key[-4:]} failed: {e}. Trying next key...")
                continue 
            except Exception as e:
                log_filename = log_error_to_file(e, suite_name="AI Director Story Generation")
                error_message = f"A non-key related error occurred: {e}\n\nDetails saved to '{log_filename}'"
                self.generated_prompts_preview.setPlainText(error_message)
                QMessageBox.critical(self, "Gemini API Error", error_message)
                self.generate_prompts_button.setEnabled(True)
                self.generate_prompts_button.setText("✅ ဇာတ်လမ်းဖန်တီးမည်")
                return

        if not full_response_text:
            error_message = f"All API keys failed. The last error was: {last_error or 'Unknown API issue.'}"
            self.generated_prompts_preview.setPlainText(error_message)
            QMessageBox.critical(self, "API Error", error_message)
            self.generate_prompts_button.setEnabled(True)
            self.generate_prompts_button.setText("✅ ဇာတ်လမ်းဖန်တီးမည်")
            return
            
        try:
            self.generated_story_data = []
            self.character_map = {}
            final_display_text = ""
            final_image_prompts = ""

            character_sheet_match = re.search(r"<character_sheet>(.*?)</character_sheet>", full_response_text, re.DOTALL)
            if character_sheet_match:
                character_text = character_sheet_match.group(1).strip()
                appearance_match = re.search(r"Appearance:\s*(.*)", character_text, re.DOTALL)
                if not appearance_match:
                    appearance_match = re.search(r"Physical Description:\s*(.*)", character_text, re.DOTALL)
                if appearance_match:
                    main_char_name = story_idea.split(" ")[-1]
                    self.character_map[main_char_name] = appearance_match.group(1).strip()
                final_display_text += "🎭 Character Sheet:\n" + character_text + "\n\n"

            if "Screenplay" in selected_style:
                scene_blocks = re.findall(r"<scene_heading>(.*?)</scene_heading>\s*<action>(.*?)</action>\s*<dialogue>(.*?)</dialogue>\s*<prompt>(.*?)</prompt>", full_response_text, re.DOTALL)
                if not scene_blocks: raise Exception("AI did not return the story in the expected Screenplay format.")

                for i, (heading, action, dialogue, prompt) in enumerate(scene_blocks):
                    full_narrative = f"{heading.strip()}\n\n{action.strip()}\n\n{dialogue.strip()}"
                    scene_data = {"scene_num": i + 1, "full_narrative": full_narrative, "prompt": prompt.strip()}
                    self.generated_story_data.append(scene_data)
                    final_display_text += f"🎬 SCENE {i+1}\n{full_narrative}\n\n"
                    final_image_prompts += f"📌 Scene {i+1}: {action.strip()}\nPrompt: {prompt.strip()}\n\n"
            else:
                story_blocks = re.findall(r"<paragraph_burmese>(.*?)</paragraph_burmese>\s*<prompt_english>(.*?)</prompt_english>", full_response_text, re.DOTALL)
                if not story_blocks: raise Exception("AI did not return the story in the expected Narrator/Story format.")

                for i, (paragraph, prompt) in enumerate(story_blocks):
                    paragraph = paragraph.strip()
                    prompt = prompt.strip()
                    scene_data = {"scene_num": i + 1, "paragraph": paragraph, "prompt": prompt}
                    self.generated_story_data.append(scene_data)
                    final_display_text += f"{paragraph}\n\n"
                    context_label = paragraph.splitlines()[0]
                    final_image_prompts += f"📌 Scene {i+1}: {context_label}...\nPrompt: {prompt}\n\n"

            self.generated_prompts_preview.setPlainText(final_display_text.strip())
            self.prompt_input.setPlainText(final_image_prompts.strip())
            self.save_script_button.setEnabled(True)
            QMessageBox.information(self, "Success", f"'{selected_style}' ပုံစံဖြင့် ဇာတ်လမ်းကို ဖန်တီးပြီးပါပြီ။")
        except Exception as e:
            QMessageBox.critical(self, "Parsing Error", f"The AI response was received but could not be parsed correctly: {e}")
        finally:
            self.generate_prompts_button.setEnabled(True)
            self.generate_prompts_button.setText("✅ ဇာတ်လမ်းဖန်တီးမည်")

    def save_script_files(self):
        if not self.generated_story_data:
            QMessageBox.warning(self, "No Script", "Please generate a story first.")
            return
        suggested_name = self.script_input.toPlainText().split('\n')[0].replace(' ', '_')
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Script Files", f"{suggested_name}.txt", "Text Files (*.txt);;SRT Files (*.srt)")
        if fileName:
            base_path, _ = os.path.splitext(fileName)
            try:
                with open(f"{base_path}.txt", 'w', encoding='utf-8') as f:
                    if 'paragraph' in self.generated_story_data[0]:
                        full_story = "\n\n".join([scene['paragraph'] for scene in self.generated_story_data])
                        f.write(full_story)
                    else:
                        full_story = "\n\n".join([scene['full_narrative'] for scene in self.generated_story_data])
                        f.write(full_story)
            except Exception as e: info_logger.error(f"Failed to save TXT file: {e}")
            try:
                self.write_srt_file(f"{base_path}.srt")
            except Exception as e: info_logger.error(f"Failed to save SRT file: {e}")
            QMessageBox.information(self, "Save Complete", f"Successfully saved script files to:\n{base_path}.txt\n{base_path}.srt")

    def format_time(self, seconds):
        td = timedelta(seconds=seconds)
        minutes, seconds = divmod(td.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = td.microseconds // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def write_srt_file(self, path):
        start_time = 0
        with open(path, 'w', encoding='utf-8') as f:
            for scene in self.generated_story_data:
                if 'paragraph' in scene:
                    narrative_text = scene['paragraph']
                else:
                    narrative_text = scene['full_narrative']

                word_count = len(narrative_text.split())
                duration = max(5, word_count // 3)
                end_time = start_time + duration
                f.write(f"{scene['scene_num']}\n{self.format_time(start_time)} --> {self.format_time(end_time)}\n{narrative_text}\n\n")
                start_time = end_time + 1

    @qasync.asyncSlot()
    async def start_generation(self):
        self.image_generate_button.setEnabled(False)
        self.image_generate_button.setText("ဖန်တီးနေသည်...")
        self.clear_previews_and_cache()
        self.save_controls_widget.setVisible(False)
        full_text_prompt = self.prompt_input.toPlainText().strip()
        prompts_to_generate = []
        is_story_mode = '📌' in full_text_prompt
        if is_story_mode:
            info_logger.info("Storyboard mode detected. Parsing scenes...")
            raw_prompts = re.findall(r"Prompt:\s*(.*)", full_text_prompt)
            for i, prompt_text in enumerate(raw_prompts):
                prompts_to_generate.append({"prompt": prompt_text.strip(), "scene_number": i + 1})
        else:
            info_logger.info("Single prompt mode detected.")
            prompts_to_generate.append({"prompt": full_text_prompt, "scene_number": 0})

        try:
            base_filename_prefix = ""
            total_prompts = len(prompts_to_generate)

            for i, item in enumerate(prompts_to_generate):
                scene_prompt, scene_num = item["prompt"], item["scene_number"]
                image_count = 1 if is_story_mode else self.image_count_spin.value()
                current_filename = f"{base_filename_prefix}Scene_{scene_num}_" if is_story_mode else base_filename_prefix
                resolution_text = self.resolution_combo.currentText().split(" ")[0]
                params = {
                    'base_filename': current_filename,
                    'amount': image_count,
                    'prompt': scene_prompt,
                    'negative_prompt': self.neg_prompt_input.toPlainText(),
                    'style': self.style_combo.currentText(),
                    'resolution': resolution_text,
                    'guidance_scale': 7.0,
                    'callback': self.display_image,
                    'character_map': self.character_map
                }
                info_logger.info(f"--- Preparing to generate for Scene {scene_num} ---")
                await image_generator(**params)
                if is_story_mode and i < total_prompts - 1:
                    info_logger.info(f"Scene {scene_num} finished. Waiting 45 seconds...")
                    await asyncio.sleep(45)
            if self.image_previews:
                self.save_controls_widget.setVisible(True)
            info_logger.info("--- ဇာတ်လမ်းပုံများအားလုံး ဖန်တီးပြီးပါပြီ ---")
        except Exception as e:
            log_filename = log_error_to_file(e, suite_name="AI Director Image Generation")
            error_text = str(e)
            if "Could not automatically find a new key" in error_text:
                QMessageBox.critical(self,
                    "Key ရယူခြင်း မအောင်မြင်ပါ (Automation Failed)",
                    "Stealth နည်းလမ်းဖြင့် ကြိုးစားသော်လည်း key ကို အလိုအလျောက် ရယူနိုင်ခြင်း မရှိသေးပါ။ Website ၏ လုံခြုံရေးစနစ်များ အလွန်အဆင့်မြင့်နေသောကြောင့် ဖြစ်နိုင်ပါသည်။\n\n"
                    "**နောက်ဆုံးနည်းလမ်းအဖြစ် Manual နည်းလမ်းကိုသာ ကြိုးစားကြည့်ရန် အကြံပြုလိုပါသည်**\n\n"
                    "အောက်ပါအဆင့်များအတိုင်း လုပ်ဆောင်ပါ:\n"
                    "1. Web Browser တွင် Perchance AI Image Generator website သို့သွားပါ။\n"
                    "2. Keyboard ပေါ်မှ **F12** ကိုနှိပ်၍ Developer Tools ကိုဖွင့်ပြီး **Network** tab ကိုရွေးပါ။\n"
                    "3. Website ပေါ်ရှိ **'Generate'** ခလုတ်ကိုတစ်ကြိမ်နှိပ်လိုက်ပါ။\n"
                    "4. Network tab ထဲတွင် `generate?prompt...` သို့မဟုတ် `checkVerificationStatus...` စသော request အသစ်များ ပေါ်လာပါမည်။ တစ်ခုခုကိုနှိပ်ပါ။\n"
                    "5. Panel အသစ်မှ **Headers** tab ကိုရှာပြီး **Query String Parameters** အပိုင်းတွင် `userKey` ကိုရှာပါ။\n"
                    "6. ထို `userKey` ၏ တန်ဖိုး (value) အရှည် (ဥပမာ: 696c44...f7a7841c3) ကို copy ကူးပါ။\n"
                    f"7. ယခု ပရိုဂရမ်ရှိရာ folder ထဲရှိ '{os.path.basename(DATA_DIR)}' ဖိုင်တွဲထဲတွင် `{os.path.basename(LAST_KEY_FILE)}` ဟုအမည်ပေးသော text file အသစ်တစ်ခုဖွင့်ပါ။\n"
                    f"8. Copy ကူးလာသော key ကို ထို `{os.path.basename(LAST_KEY_FILE)}` file ထဲသို့ paste လုပ်ပြီး save ပါ။\n"
                    "9. ပရိုဂရမ်ကိုပိတ်ပြီး ပြန်လည်စတင်ပါ။\n\n"
                    f"Error details have been saved to '{log_filename}'."
                )
            else:
                info_logger.error(f"An error occurred during generation: {error_text}", exc_info=True)
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {error_text}\n\nFull details have been saved to:\n{log_filename}")
        finally:
            self.image_generate_button.setEnabled(True)
            self.image_generate_button.setText("ပုံဖန်တီးမည် (Generate)")

    def clear_previews_and_cache(self):
        self.image_previews = []
        for i in reversed(range(self.image_display_layout.count())):
            widget = self.image_display_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        if os.path.exists(self.CACHE_DIR):
            shutil.rmtree(self.CACHE_DIR)
        os.makedirs(self.CACHE_DIR)

    def display_image(self, temp_image_path):
        preview_widget = SelectableImage(temp_image_path)
        self.image_previews.append(preview_widget)
        count = len(self.image_previews) - 1
        row = count // self.GRID_COLUMNS
        col = count % self.GRID_COLUMNS
        self.image_display_layout.addWidget(preview_widget, row, col)

    def select_all_images(self):
        for preview in self.image_previews:
            preview.set_selected(True)

    def deselect_all_images(self):
        for preview in self.image_previews:
            preview.set_selected(False)

    def save_selected_images(self):
        selected_paths = [p.image_path for p in self.image_previews if p.is_selected()]
        if not selected_paths:
            QMessageBox.warning(self, "No Images Selected", "Please select at least one image.")
            return
        save_directory = QFileDialog.getExistingDirectory(self, "Select Folder to Save Images")
        if save_directory:
            saved_count = 0
            for path in selected_paths:
                try:
                    filename = os.path.basename(path)
                    destination = os.path.join(save_directory, filename)
                    shutil.copy(path, destination)
                    saved_count += 1
                except Exception as e:
                    info_logger.error(f"Could not save {filename}: {e}")
            QMessageBox.information(self, "Save Complete", f"Successfully saved {saved_count} images to:\n{save_directory}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Application', 'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if hasattr(self, 'downloader_tab') and hasattr(self.downloader_tab, 'closeEvent'):
                self.downloader_tab.closeEvent(event)
            if hasattr(self, 'pro_editor_tab') and hasattr(self.pro_editor_tab, 'closeEvent'):
                self.pro_editor_tab.closeEvent(event)
            event.accept()
        else:
            event.ignore()

# ==============================================================================
# Main Execution Block
# ==============================================================================
def run_gui():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget { font-family: 'Segoe UI', 'Noto Sans Myanmar', sans-serif; font-size: 14px; color: #E0E0E0; background-color: #2D2D30; }
        QTabWidget::pane { background-color: #2D2D30; border: 1px solid #4A4A4A; }
        QTabBar::tab { background-color: #2D2D30; color: #E0E0E0; padding: 10px; margin-right: 2px; border: 1px solid #4A4A4A; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;}
        QTabBar::tab:selected { background-color: #4C566A; color: #FFFFFF; }
        QTabBar::tab:hover { background-color: #5E81AC; color: #FFFFFF; }
        QGroupBox { font-weight: bold; border: 1px solid #4A4A4A; border-radius: 8px; margin-top: 10px; padding: 10px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; background-color: #2D2D30; }
        QLabel { color: #CCCCCC; }
        QLineEdit, QComboBox, QSpinBox, QTextEdit, QDoubleSpinBox { background-color: #3C3C3C; border: 1px solid #555; border-radius: 4px; padding: 6px; color: #E0E0E0; }
        QComboBox QAbstractItemView { background-color: #3C3C3C; color: #E0E0E0; selection-background-color: #5E81AC; }
        QPushButton { background-color: #5E81AC; color: white; font-weight: bold; border: none; padding: 8px 12px; border-radius: 4px; }
        QPushButton:hover { background-color: #7395B8; }
        QPushButton:disabled { background-color: #444; color: #888; }
        QProgressBar { text-align: center; color: #FFFFFF; border: 1px solid #4A4A4A; border-radius: 4px; }
        QProgressBar::chunk { background-color: #5E81AC; border-radius: 4px; }
        QSlider::groove:horizontal { border: 1px solid #555; background: #555; height: 8px; border-radius: 4px; }
        QSlider::handle:horizontal { background: #88C0D0; border: 1px solid #88C0D0; width: 18px; margin: -5px 0; border-radius: 9px; }
        QStatusBar { background-color: #2B2B2B; color: #AAAAAA; padding: 5px; border-top: 1px solid #4A4A4A; }
        QMenuBar { background-color: #2D2D30; color: #E0E0E0; }
        QMenuBar::item { background: transparent; padding: 4px 8px; }
        QMenuBar::item:selected { background: #5E81AC; color: white; }
        QMenu { background-color: #3C3C3C; border: 1px solid #4A4A4A; color: #E0E0E0; }
        QMenu::item:selected { background-color: #5E81AC; color: white; }
        /* Podcast Tab Specific Styles */
        QPushButton#podcastGenerateButton { background-color: #FF6F00; color: white; }
        QPushButton#podcastClearButton { background-color: #6c757d; color: white; }
        QPushButton#podcastCopyButton { background-color: #17A2B8; color: white; }
        QPushButton#podcastGenerateButton:hover { background-color: #E06200; }
        QPushButton#podcastClearButton:hover { background-color: #5a6268; }
        QPushButton#podcastCopyButton:hover { background-color: #138496; }
        /* Main Action Button Styles */
        QPushButton#imageGenerateButton { background-color: #4CAF50; color: white; }
        QPushButton#imageGenerateButton:hover { background-color: #45a049; }
        QPushButton#saveSelectedButton { background-color: #007BFF; color: white; }
        QPushButton#saveSelectedButton:hover { background-color: #0069d9; }
        QPushButton#proEditorStartButton { background-color: #28a745; color: white; font-size: 16px; padding: 10px;}
        QPushButton#proEditorStartButton:hover { background-color: #218838; }
    """)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # --- Login Flow ---
    
    # <<< 1. သင်၏ Firebase အချက်အလက်များကို ဤနေရာတွင် ထည့်ပါ >>>
    # အရေးကြီး !!! - အောက်ပါ placeholder တန်ဖိုးများကို သင်၏ တကယ့် Firebase project credentials များဖြင့် အစားထိုးပါ။
    # ဤအချက်အလက်များကို Firebase Console မှ ရယူနိုင်ပါသည်။ (Project Settings -> General -> Your apps -> SDK setup and configuration)
    firebase_config = {
      "apiKey": "AIzaSyB2cmTNp5tZEW8kli4H3xv-ciWYwLVMQrg", # ဤနေရာတွင် သင်၏ API Key ကိုထည့်ပါ
      "authDomain": "aivideotool-943f5.firebaseapp.com", # ဤနေရာတွင် သင်၏ Auth Domain ကိုထည့်ပါ
      "databaseURL": "", # Database မသုံးလျှင် လွတ်ထားနိုင်သည်
      "storageBucket": "aivideotool-943f5.firebasestorage.app" # ဤနေရာတွင် သင်၏ Storage Bucket ကိုထည့်ပါ
    }

    # <<< 2. သင်၏ API Key ကိုစစ်ဆေးပါ (ယခု Comment ပိတ်ထားပါသည်) >>>
    # ပြဿနာရှာဖွေရန် ဤစစ်ဆေးမှုကို ခေတ္တပိတ်ထားပါသည်။ 
    # if "YOUR_API_KEY" in firebase_config["apiKey"]:
    #     QMessageBox.critical(None, "Configuration Error", "Firebase API Key is not set correctly in the script.\nPlease replace the placeholder values inside the `firebase_config` dictionary.")
    #     return

    try:
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
    except Exception as e:
        QMessageBox.critical(None, "Firebase Error", f"Failed to initialize Firebase. Please check your config and network.\nError: {e}")
        return

    user = None
    settings = QSettings("AIOApp", "Auth")
    refresh_token = settings.value("refreshToken", None)

    if refresh_token:
        try:
            print("Attempting to sign in with refresh token...")
            user = auth.refresh(refresh_token)
            settings.setValue("refreshToken", user['refreshToken'])
            
            # --- FIX: Fetch full user profile to get email ---
            account_info = auth.get_account_info(user['idToken'])
            user['email'] = account_info['users'][0]['email']
            # --- END FIX ---

            print("Token refresh successful.")
        except Exception:
            print("Refresh token is invalid or expired. Requiring manual login.")
            user = None 
            settings.remove("refreshToken")

    if not user:
        login_dialog = LoginDialog(auth)
        if login_dialog.exec_() == QDialog.Accepted:
            user = login_dialog.get_user()
        else:
            return # User cancelled login

    main_win = PerchanceGeneratorApp(user)
    main_win.show()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass

if __name__ == '__main__':
    if not os.path.exists('.cache'): os.makedirs('.cache')
    run_gui()