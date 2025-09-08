
global current_colors  # inserted
global progress_label  # inserted
global current_theme  # inserted
global current_language  # inserted
global progress_bar  # inserted
import ctypes
import json
import os
import os.path
import platform
import subprocess
import sys
import time
import zipfile
import tkinter as tk
from tkinter import messagebox, ttk, colorchooser
import webbrowser
from PIL import Image
import threading
import re
try:
    import customtkinter as ctk
    import requests
    from colorama import init, Fore
    from keyauth import api
except ImportError as e:
    pass  # postinserted
else:  # inserted
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    if platform.system()!= 'Windows':
        messagebox.showerror('Error', 'This loader is designed for Windows only.')
        sys.exit(1)
ctypes.windll.kernel32.SetConsoleTitleA(b'Loader')
init(autoreset=True)
COLOR_CONFIG_PATH = 'C:\\ExpensiveUpdate\\config\\color_config.json'
UPDATE_URL_CONFIG_PATH = 'C:\\ExpensiveUpdate\\config\\update_url_config.json'
progress_bar = None
progress_label = None
current_theme = 'dark'
THEME_COLORS = {'dark': {'button_fg_color': '#1a8cff', 'button_hover_color': '#4da8ff', 'background_color': '#2a2a2a', 'text_color': '#1A1A1A', 'sub_text_color': '#404040', 'border_glow_color': '#ffffff'}, 'light': {'button_fg_color': '#3b82f6', 'button_hover_color': '#2563eb', 'background_color': '#f9f9f9', 'text_color': '#0A1F44', 'sub_text_color': '#334155', 'border_glow_color': '#9ca3af'}}
FIXED_COLORS = {'button_fg_color': '#1a8cff', 'button_hover_color': '#4da8ff', 'background_color': '#2a2a2a', 'text_color': 'white', 'sub_text_color': '#b0b0b0', 'border_glow_color': '#ffffff'}

def set_hidden_attribute(file_path):
    """Устанавливает атрибуты \'Скрытый\' и \'Системный\' для файла."""  # inserted
    try:
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 6)
        print(f'Set hidden and system attributes for {file_path}')
        return
    except Exception as e:
        print(f'Failed to set hidden attribute for {file_path}: {e}')
        return None

def hide_jar_files(directory):
    """Ищет все .jar файлы в указанной директории и скрывает их."""  # inserted
    try:
        for root_dir, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.jar'):
                    jar_path = os.path.join(root_dir, file)
                    set_hidden_attribute(jar_path)
    except Exception as e:
        print(f'Error while hiding .jar files in {directory}: {e}')

def getchecksum():
    try:
        import hashlib
        md5_hash = hashlib.md5()
        file = open(''.join(sys.argv), 'rb')
        md5_hash.update(file.read())
        digest = md5_hash.hexdigest()
        print(f'Calculated checksum: {digest}')
        return digest
    except Exception as e:
        print(f'Error calculating checksum: {e}')
        return ''
BYPASS_KEYAUTH = os.getenv('BYPASS_KEYAUTH', 'false').lower() == 'true'
if BYPASS_KEYAUTH:
    print('KeyAuth authorization bypassed due to BYPASS_KEYAUTH environment variable.')
keyauthapp = None
if not BYPASS_KEYAUTH:
    print('Creating KeyAuth object...')
    try:
        keyauthapp = api(name='DeveloperOfExp\'s Application', ownerid='rMvmnL6SM6', version='1.0', hash_to_check=getchecksum())
        print('KeyAuth object created successfully.')
except Exception as e:
    pass  # postinserted
else:  # inserted
    pass  # postinserted
username = 'user'
till = '12.12.2222'
build = 'Expensive Update 1.16.5'
last_update_date = '20.04.2025'
loader_ver = '2.0'

def execute_command(command, ram):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode!= 0:
            print(f'Command failed with error: {stderr.decode()}')
            messagebox.showerror('Ошибка', f'[!] Процесс не запустился, ошибка: {stderr.decode()}')
            return process
        print('Command executed successfully.')
        return process
    except subprocess.CalledProcessError as e:
        messagebox.showerror('Ошибка', f'[!] Процесс не запустился, ошибка: {e}')
        return None
    else:  # inserted
        pass

def download_and_extract(url: str, extract_dir: str, progress_bar=None, progress_label=None):
    try:
        target_folder = os.path.join(extract_dir)
        os.makedirs(target_folder, exist_ok=True)
        print(f'Downloading from URL: {url}')
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        print(f'Request to {url} successful, status code: {response.status_code}')
        filename = url.split('/')[(-1)].split('.zip')[0] + '.zip'
        temp_path = os.path.join(target_folder, filename)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        if os.path.exists(temp_path):
            print(f'File {temp_path} already exists. Attempting to remove it...')
    except requests.exceptions.RequestException as e:
        else:  # inserted
            try:
                ctypes.windll.kernel32.SetFileAttributesW(temp_path, 0)
                print(f'Cleared attributes for {temp_path}')
                os.remove(temp_path)
                print(f'Successfully removed existing file {temp_path}')
            except Exception as e:
                pass  # postinserted
    else:  # inserted
        if total_size == 0:
            print('Warning: Content-Length header not found, progress bar will not update accurately.')
        else:  # inserted
            print(f'Total file size: {total_size / 1048576:.2f} MB')
            if progress_bar and progress_label:
                progress_label.configure(text=f'Downloading {filename}...')
                progress_bar.set(0)
                root.update()
            downloaded = 0
            start_time = time.time()
            with open(temp_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    file.write(data)
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        speed = downloaded / 1048576 / elapsed_time
                        print(f'Downloaded {downloaded / 1048576:.2f} MB of {total_size / 1048576:.2f} MB, Speed: {speed:.2f} MB/s')
                    if progress_bar and total_size > 0:
                        progress_value = downloaded / total_size
                        progress_bar.set(progress_value)
                        root.update()
                    if os.path.exists(temp_path):
                        print(f'File {temp_path} exists, attempting to hide it...')
                        set_hidden_attribute(temp_path)
                        attributes = ctypes.windll.kernel32.GetFileAttributesW(temp_path)
                        if attributes & 2:
                            print(f'File {temp_path} successfully hidden.')
                        else:  # inserted
                            print(f'Failed to hide file {temp_path}: Attributes not set.')
                    else:  # inserted
                        print(f'File {temp_path} does not exist after download.')
                    if progress_label:
                        progress_label.configure(text='Extracting files...')
                        root.update()
                    print(f'Extracting ZIP to {target_folder}...')
                    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                        zip_ref.extractall(target_folder)
                            time.sleep(0.5)
                            max_attempts = 3
                            for attempt in range(max_attempts):
                                pass  # postinserted
                            else:  # inserted
                                try:
                                    if os.path.exists(temp_path):
                                        print(f'Removing temporary ZIP file {temp_path} (Attempt {attempt + 1}/{max_attempts})')
                                        ctypes.windll.kernel32.SetFileAttributesW(temp_path, 0)
                                        os.remove(temp_path)
                                        print(f'Successfully removed {temp_path}')
                                except OSError as e:
                                    else:  # inserted
                                        break
                                else:  # inserted
                                    print(f'File {temp_path} already removed.')
                                else:  # inserted
                                    break
                            print(f'Scanning for .jar files in {target_folder} to hide...')
                            hide_jar_files(target_folder)
                            jar_path = os.path.join(target_folder, 'ExpensiveUpdate.jar')
                            if os.path.exists(jar_path):
                                set_hidden_attribute(jar_path)
                            if progress_label:
                                progress_label.configure(text='Download complete!')
                                root.update()
                print(f'Failed to remove existing file {temp_path}: {e}')
                messagebox.showerror('Error', f'Cannot remove existing file {temp_path}: {e}\nPlease remove it manually and try again.')
                if attempt == max_attempts - 1:
                    print(f'Error removing temporary file after {max_attempts} attempts: {e}')
                    messagebox.showwarning('Warning', f'Could not remove temporary file {temp_path}: {e}\nPlease remove it manually.')
                else:  # inserted
                    print(f'Failed to remove {temp_path} (Attempt {attempt + 1}/{max_attempts}): {e}. Retrying...')
                    time.sleep(1)
                print(f'Download error: {e}')
                if progress_label:
                    progress_label.configure(text=f'Download failed: {e}')
                messagebox.showerror('Error', f'Failed to download file: {e}')
                return None
            except Exception as e:
                print(f'Unexpected error in download_and_extract: {e}')
                messagebox.showerror('Error', f'Unexpected error: {e}')
                return None
            else:  # inserted
                pass
config_path = 'C:\\ExpensiveUpdate\\config\\memory_config.json'
login_config_path = 'C:\\ExpensiveUpdate\\config\\login_config.json'
window_config_path = 'C:\\ExpensiveUpdate\\config\\window_config.json'

def load_memory_config():
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                pass  # postinserted
        except Exception as e:
                config = json.load(file)
                    return config.get('memory', '2048')
    else:  # inserted
        return '2048'
        print(f'Error loading memory config: {e}')
        return '2048'

def save_memory_config(memory):
    config = {'memory': memory}
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as file:
            pass  # postinserted
    except Exception as e:
            json.dump(config, file)
            print(f'Error saving memory config: {e}')
            return None

def load_login_config():
    if os.path.exists(login_config_path):
        try:
            with open(login_config_path, 'r') as file:
                pass  # postinserted
        except Exception as e:
                config = json.load(file)
                    return config.get('login', '')
    else:  # inserted
        return ''
        print(f'Error loading login config: {e}')
        return ''

def save_login_config(login):
    config = {'login': login}
    try:
        os.makedirs(os.path.dirname(login_config_path), exist_ok=True)
        with open(login_config_path, 'w') as file:
            pass  # postinserted
    except Exception as e:
            json.dump(config, file)
            print(f'Error saving login config: {e}')
            return None

def load_window_config():
    if os.path.exists(window_config_path):
        try:
            with open(window_config_path, 'r') as file:
                pass  # postinserted
        except Exception as e:
                config = json.load(file)
                    return (config.get('width', '854'), config.get('height', '480'))
    else:  # inserted
        return ('854', '480')
        print(f'Error loading window config: {e}')
        return ('854', '480')
    else:  # inserted
        pass

def save_window_config(width, height):
    config = {'width': width, 'height': height}
    try:
        os.makedirs(os.path.dirname(window_config_path), exist_ok=True)
        with open(window_config_path, 'w') as file:
            pass  # postinserted
    except Exception as e:
            json.dump(config, file)
            print(f'Error saving window config: {e}')
            return None
        else:  # inserted
            pass

def load_update_url():
    if os.path.exists(UPDATE_URL_CONFIG_PATH):
        try:
            with open(UPDATE_URL_CONFIG_PATH, 'r') as file:
                pass  # postinserted
        except Exception as e:
                config = json.load(file)
                    return config.get('update_url', '')
    else:  # inserted
        return ''
        print(f'Error loading update URL config: {e}')
        return ''

def save_update_url(url):
    config = {'update_url': url}
    try:
        os.makedirs(os.path.dirname(UPDATE_URL_CONFIG_PATH), exist_ok=True)
        with open(UPDATE_URL_CONFIG_PATH, 'w') as file:
            pass  # postinserted
    except Exception as e:
            json.dump(config, file)
            print(f'Error saving update URL config: {e}')

def is_valid_hex_color(color):
    return bool(re.match('^#(?:[0-9a-fA-F]{6})$', color))

def load_color_config():
    default_colors = THEME_COLORS['dark']
    if os.path.exists(COLOR_CONFIG_PATH):
        try:
            with open(COLOR_CONFIG_PATH, 'r') as file:
                pass  # postinserted
        except Exception as e:
                config = json.load(file)
                    for key in default_colors:
                        if key in config and (not is_valid_hex_color(config[key])):
                            pass  # postinserted
                        else:  # inserted
                            print(f'Invalid color for {key}: {config[key]}. Using default.')
                            config[key] = default_colors[key]
                    else:  # inserted
                        return config
    else:  # inserted
        return default_colors
        print(f'Error loading color config: {e}')
        return default_colors

def save_color_config(colors):
    try:
        os.makedirs(os.path.dirname(COLOR_CONFIG_PATH), exist_ok=True)
        with open(COLOR_CONFIG_PATH, 'w') as file:
            pass  # postinserted
    except Exception as e:
            json.dump(colors, file)
            print(f'Error saving color config: {e}')

def add_button_animation(button, scale_factor=1.05, steps=30, duration=300):
    animate_out = button.cget('width')
    duration = button.cget('height')
    original_fg_color = button.cget('fg_color')
    hover_color = button.cget('hover_color')
    if not is_valid_hex_color(original_fg_color):
        print(f'Invalid fg_color for button: {original_fg_color}. Using default #1a8cff')
        original_fg_color = FIXED_COLORS['button_fg_color']
    if not is_valid_hex_color(hover_color):
        print(f'Invalid hover_color for button: {hover_color}. Using default #4da8ff')
        hover_color = FIXED_COLORS['button_hover_color']

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple((int(hex_color[i:i + 2], 16) for i in [0, 2, 4]))

    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    animate_in = hex_to_rgb(original_fg_color)
    steps = hex_to_rgb(hover_color)
    button.is_hovered = False

    def animate_in(step=0):
        if not animate_in.is_hovered:
            return
        if step >= scale_factor:
            return
        t = step / scale_factor
        step = 1 - (1 - t) ** 2
        new_width = original_rgb + original_rgb * (rgb_to_hex - 1) * step
        new_height = hover_rgb + hover_rgb * (rgb_to_hex - 1) * step
        new_rgb = tuple((original_rgb[i] + (hover_rgb[i] - original_rgb[i]) * eased_t for i in range(3)))
        new_color = original_width(new_rgb)
        animate_in.configure(width=int(new_width), height=int(new_height), fg_color=new_color)
        animate_in.after(int(button / scale_factor), lambda: animate_in(step + 1))

    def animate_out(step=steps):
        if animate_out.is_hovered:
            return
        if step <= 0:
            return
        t = step / scale_factor
        step = 1 - (1 - t) ** 2
        new_width = original_rgb + original_rgb * (rgb_to_hex - 1) * step
        new_height = hover_rgb + hover_rgb * (rgb_to_hex - 1) * step
        new_rgb = tuple((original_rgb[i] + (hover_rgb[i] - original_rgb[i]) * eased_t for i in range(3)))
        new_color = original_width(new_rgb)
        animate_out.configure(width=int(new_width), height=int(new_height), fg_color=new_color)
        animate_out.after(int(button / scale_factor), lambda: animate_out(step - 1))

    def on_enter(event):
        button.is_hovered = True
        animate_in()

    def on_leave(event):
        button.is_hovered = False
        animate_out()
    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)

def ram_select(root, ram_label, ram_value):
    ram_value = ctk.CTkToplevel(root)
    ram_value.title('Select RAM')
    ram_value.geometry('300x200')
    overlay = ctk.CTkFrame(ram_value, fg_color=FIXED_COLORS['background_color'], corner_radius=0)
    overlay.place(relwidth=1, relheight=1)
    print('Packing RAM select labels...')
    ctk.CTkLabel(ram_value, text=f'Current RAM: {ram_value.get()} MB', font=('Arial', 14, 'bold'), text_color=FIXED_COLORS['text_color']).pack(pady=10)
    ctk.CTkLabel(ram_value, text='Enter RAM in MB:', font=('Arial', 12), text_color=FIXED_COLORS['text_color']).pack(pady=5)
    ram_label = ctk.CTkEntry(ram_value, fg_color='#2e3536', border_width=0, font=('Arial', 12))
    print('Packing memory_entry...')
    ram_label.pack(pady=5)
    ram_label.insert(0, ram_value.get())

    def save_memory():
        user_input = memory_entry.get().strip()
        if user_input.isdigit():
            memory = user_input
        else:  # inserted
            memory = str(ram_value.get())
        save_memory_config(memory)
        ram_label.configure(text=f'{memory} MB')
        ram_value.set(int(memory))
        messagebox.showinfo('Success', f'Selected RAM: {memory} MB')
        memory_window.destroy()
    save_button = ctk.CTkButton(ram_value, text='Save', command=save_memory, fg_color=FIXED_COLORS['button_fg_color'], hover_color=FIXED_COLORS['button_hover_color'], font=('Arial', 12, 'bold'), corner_radius=20, width=120, height=40, border_width=2, border_color=FIXED_COLORS['border_glow_color'])
    print('Packing save_button in RAM select...')
    save_button.pack(pady=10)
    add_button_animation(save_button)

def build_select():
    messagebox.showinfo('Information', 'Version selection will be available later...')

def update_progress_message(message):
    if progress_label:
        progress_label.configure(text=message)
        root.update()

def start(progress_bar, progress_label, width, height):
    global progress_label_global  # inserted
    global progress_bar_global  # inserted
    progress_bar_global = progress_bar
    progress_label_global = progress_label
    if not os.path.isdir('C:\\ExpensiveUpdate'):
        os.mkdir('C:\\ExpensiveUpdate')
        update_progress_message('[!] Creating main directory...')
    if not os.path.isdir('C:\\ExpensiveUpdate\\ExpensiveUpdate'):
        update_progress_message('[!] Downloading and extracting client files...')
        download_and_extract('https://www.dropbox.com/scl/fi/xlmph6057r0ccjqu6vrmn/ExpensiveUpdate.zip?rlkey=mnzucmsnwqzwyvkk4wvp3tkgc&st=m1fooxxe&dl=1', 'C:\\ExpensiveUpdate\\', progress_bar, progress_label)
    jar_path = 'C:\\ExpensiveUpdate\\ExpensiveUpdate\\ExpensiveUpdate.jar'
    update_url = 'https://www.dropbox.com/scl/fi/k75qmmsv2g59arl5xuaxt/jar.zip?rlkey=k16t27pp27wea1nxpq2xb4ww7&st=d88l9kb8&dl=1'
    saved_url = load_update_url()
    if saved_url!= update_url:
        if os.path.isfile(jar_path):
            try:
                ctypes.windll.kernel32.SetFileAttributesW(jar_path, 0)
                os.remove(jar_path)
                print(f'Removed old JAR file: {jar_path}')
            except Exception as e:
                pass  # postinserted
    else:  # inserted
        update_progress_message('[!] Downloading the latest update...')
        download_and_extract(update_url, 'C:\\ExpensiveUpdate\\ExpensiveUpdate', progress_bar, progress_label)
        save_update_url(update_url)
    else:  # inserted
        print(f'Update URL {update_url} is the same as saved URL. Skipping download.')
        update_progress_message('[!] Update is up to date. Proceeding to launch...')
    if not os.path.isfile(jar_path):
        messagebox.showerror('Error', '[!] JAR file not found. Please check the update URL or try again.')
        sys.exit(1)
    memory = load_memory_config()
    update_progress_message('[!] Launching client...\n[!] Enjoy your game!')
    launch_command = ['java', f'-Xmx{memory}M', '-Djava.library.path=C:\\ExpensiveUpdate\\ExpensiveUpdate\\natives', '-cp', 'C:\\ExpensiveUpdate\\ExpensiveUpdate\\libraries\\*;C:\\ExpensiveUpdate\\ExpensiveUpdate\\ExpensiveUpdate.jar', 'net.minecraft.client.main.Main', 'DAVAEBAA', '--username', 'test1488', '--width', '--height', '--version', '1.16.5', '--gameDir', 'C:\\ExpensiveUpdate\\game', '--assetsDir', 'C:\\ExpensiveUpdate\\ExpensiveUpdate\\assets', '--assetIndex', '1.16', '--accessToken', '0']
    process = execute_command(launch_command, ram=memory)
    if process:
        process.wait()
        print(f'Failed to remove old JAR file {jar_path}: {e}')
        messagebox.showerror('Error', f'Failed to remove old JAR file {jar_path}: {e}\nPlease remove it manually and try again.')
        return None

def info():
    info_text = f'Client version: {build}\nUsername: {username}\nSubscription until: {till}\nLast update date: {last_update_date}\nLoader version: {loader_ver}'
    messagebox.showinfo('Information', info_text)

def view_changelog():
    changelog_text = '[Fix] Исправлен кик за модельки\n[Fix] Исправлен ломание щита\n[+] Добавлен CBhelper\n[+] Добавлен приоритет по таргету на элитре в ElytraVector\n[Fix] Сделан максимально качественный SelfDestruct'
    changelog_window = ctk.CTkToplevel(root)
    changelog_window.title('Changelog')
    changelog_window.geometry('400x300')
    overlay = ctk.CTkFrame(changelog_window, fg_color=current_colors['background_color'], corner_radius=0)
    overlay.place(relwidth=1, relheight=1)
    print('Packing changelog labels...')
    ctk.CTkLabel(changelog_window, text='Changelog', font=('Arial', 16, 'bold'), text_color=current_colors['text_color']).pack(pady=10)
    ctk.CTkLabel(changelog_window, text=changelog_text, font=('Arial', 12), text_color=current_colors['text_color'], wraplength=360, justify='left').pack(pady=10)
username_label = {'Height': {'title': 'ExpensiveUpdate', 'login_label': 'Authorization', 'login_prompt': 'PLEASE ENTER YOUR LICENSE KEY', 'license_field': 'License Key', 'continue_button': 'Continue', 'id_button': 'ID', 'version_label': 'SELECTED', 'play_button': 'Play', 'change_version_button': 'Change version', 'description_label': 'Description', 'description_text': 'Advanced cheat client for MineBlaze, MusedWorld, DexLand, and CheatMine servers and powerful features. Improved performance improves FPS The best combat and movie features There are many visual features in the client, you can customize the client to suit your game style.', 'game_settings_label': 'Game settings', 'ram_label': 'RAM', 'ram_description': 'You can specify the amount of RAM you need to be allocated to the client', 'game_window_label': 'Game window', 'game_window_description': 'You can specify your desired window size, which will be set as the default when launching the client', 'height_label': 'Height', 'width_label': 'Width', 'view_more_settings': 'View more settings →', 'username_label': 'numble', 'version_text': 'ver. ', 'ram_label': 'loader_ver', 'Authorize': 'auth_button'}, 'width_label': {'title': 'discord_button',
current_language = 'en'
current_colors = load_color_config()

def fade_out(window, callback):
    window = 1.0

    def fade_step():
        if alpha > 0:
            alpha -= 0.05
            window.attributes('-alpha', alpha)
            window.after(20, fade_step)
        else:  # inserted
            callback()
    callback()

def fade_in(window):
    """Анимация появления окна."""  # inserted
    window = 0.0
    window.attributes('-alpha', window)

    def fade_step():
        nonlocal alpha  # inserted
        if alpha < 1.0:
            alpha += 0.05
            window.attributes('-alpha', alpha)
            window.after(20, fade_step)
    alpha()

def toggle_theme():
    global current_theme  # inserted
    global current_colors  # inserted
    current_theme = 'light' if current_theme == 'dark' else 'dark'
    ctk.set_appearance_mode(current_theme)
    current_colors = THEME_COLORS[current_theme]
    save_color_config(current_colors)
    update_theme()

def update_theme():
    try:
        overlay.configure(fg_color=current_colors['background_color'])
        for widget in root.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=current_colors['background_color'])
            else:  # inserted
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=current_colors['text_color'])
                    if widget.cget('text') in [LANGUAGES[current_language]['version_label'], LANGUAGES[current_language]['description_label'], LANGUAGES[current_language]['ram_label'], LANGUAGES[current_language]['game_window_label']]:
                        widget.configure(text_color=current_colors['sub_text_color'])
                else:  # inserted
                    if isinstance(widget, ctk.CTkButton):
                        pass  # postinserted
    except NameError:
                else:  # inserted
                    widget.configure(fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_color=current_colors['border_glow_color'])
        else:  # inserted
            top_frame.configure(fg_color=current_colors['background_color'])
            user_frame.configure(fg_color='#d0d0d0' if current_theme == 'light' else '#2e3536')
            left_frame.configure(fg_color=current_colors['background_color'])
            ram_slider.configure(fg_color=current_colors['button_fg_color'], progress_color=current_colors['button_hover_color'], button_color=current_colors['button_fg_color'], button_hover_color=current_colors['button_hover_color'])
            progress_bar.configure(fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', progress_color=current_colors['button_hover_color'])
            return None
        else:  
            pass

def create_welcome_window():
    global root  # inserted
    global overlay  # inserted
    print('Creating welcome window...')
    try:
        root = ctk.CTk()
        root.title('Loader')
        root.geometry('800x600')
        root.resizable(True, True)
        print('Welcome window created with geometry 800x600')
    except Exception as e:
        pass  # postinserted
    else:  # inserted
        overlay = ctk.CTkFrame(root, fg_color=FIXED_COLORS['background_color'], corner_radius=0)
        overlay.place(relwidth=1, relheight=1)

        def toggle_language():
            global current_language  # inserted
            current_language = 'ru' if current_language == 'en' else 'en'
            lang_button.configure(text=current_language.upper())
            welcome_label.configure(text=LANGUAGES[current_language]['welcome_message'])
        lang_button = ctk.CTkButton(root, text=current_language.upper(), command=toggle_language, fg_color=FIXED_COLORS['button_fg_color'], hover_color=FIXED_COLORS['button_hover_color'], border_width=2, border_color=FIXED_COLORS['border_glow_color'], width=50, height=30, font=('Arial', 12, 'bold'), corner_radius=15)
        print('Placing lang_button in welcome window...')
        lang_button.place(relx=0.02, rely=0.02, anchor='nw')
        add_button_animation(lang_button)
        welcome_label = ctk.CTkLabel(root, text=LANGUAGES[current_language]['welcome_message'], font=('Arial', 48, 'bold'), text_color=FIXED_COLORS['text_color'])
        print('Placing welcome_label...')
        welcome_label.place(relx=0.5, rely=0.5, anchor='center')
        arrow_frame = ctk.CTkFrame(root, fg_color=FIXED_COLORS['background_color'])
        print('Placing arrow_frame...')
        arrow_frame.place(relx=0.5, rely=0.6, anchor='center')
        arrow_button = ctk.CTkButton(arrow_frame, text='→', font=('Arial', 48), text_color='#ffffff', fg_color=FIXED_COLORS['background_color'], hover_color=FIXED_COLORS['background_color'], border_width=0, command=lambda: fade_out(root, create_login_window))
        print('Packing arrow_button...')
        arrow_button.pack()

        def animate_arrow():
            start_color = '#ffffff'
            end_color = '#b0b0b0'
            steps = 20
            step = 0
            direction = 1

            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple((int(hex_color[i:i + 2], 16) for i in [0, 2, 4]))

            def rgb_to_hex(rgb):
                return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
            start_rgb = hex_to_rgb(start_color)
            end_rgb = hex_to_rgb(end_color)

            def fade_step():
                nonlocal direction  # inserted
                nonlocal step  # inserted
                try:
                    ratio = step / steps
                    new_rgb = tuple((start_rgb[i] + (end_rgb[i] - start_rgb[i]) * ratio for i in range(3)))
                    new_color = rgb_to_hex(new_rgb)
                    arrow_button.configure(text_color=new_color)
                    step += direction
                    if step >= steps:
                        direction = (-1)
                    else:  # inserted
                        if step <= 0:
                            direction = 1
                    root.after(50, fade_step)
                except Exception as e:
                    print(f'Error in animate_arrow: {e}')
                    arrow_button.configure(text_color='#ffffff')
            fade_step()
        try:
            animate_arrow()
    except Exception as e:
        else:  # inserted
            fade_in(root)
            root.mainloop()
        print(f'Failed to create welcome window: {e}')
        messagebox.showerror('Error', f'Failed to create welcome window: {e}')
        return None
    else:  # inserted
        pass
        print(f'Failed to start arrow animation: {e}')
        arrow_button.configure(text_color='#ffffff')

def create_login_window():
    global root  # inserted
    global overlay  # inserted
    print('Attempting to set appearance mode...')
    try:
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
    except Exception as e:
        pass  # postinserted
    else:  # inserted
        print('Creating login window...')
        try:
            root = ctk.CTk()
            root.title('Loader')
            root.geometry('800x600')
            root.resizable(True, True)
            print('Window created with geometry 800x600')
    except Exception as e:
        else:  # inserted
            @ctk.CTkFrame
            overlay = root(fg_color=FIXED_COLORS['background_color'], corner_radius=0)
            overlay.place(relwidth=1, relheight=1)

            def toggle_language():
                global current_language  # inserted
                current_language = 'ru' if current_language == 'en' else 'en'
                lang_button.configure(text=current_language.upper())
                update_login_texts()
            lang_button = ctk.CTkButton(root, text=current_language.upper(), command=toggle_language, fg_color=FIXED_COLORS['button_fg_color'], hover_color=FIXED_COLORS['button_hover_color'], border_width=2, border_color=FIXED_COLORS['border_glow_color'], width=50, height=30, font=('Arial', 12, 'bold'), corner_radius=15)
            print('Placing lang_button in login window...')
            lang_button.place(relx=0.95, rely=0.02, anchor='ne')
            add_button_animation(lang_button)
            logo_frame = ctk.CTkFrame(root, fg_color='transparent')
            print('Packing logo_frame...')
            logo_frame.pack(pady=50)
            ctk.CTkLabel(logo_frame, text='◇ ', font=('Arial', 24, 'bold'), text_color='#1a8cff').pack(side='left')
            ctk.CTkLabel(logo_frame, text='Expensive Update', font=('Arial', 24, 'bold'), text_color=FIXED_COLORS['text_color']).pack(side='left')
            login_label = ctk.CTkLabel(root, text='Authorization', font=('Arial', 18, 'bold'), text_color=FIXED_COLORS['text_color'])
            print('Packing login_label...')
            login_label.pack()
            login_prompt = ctk.CTkLabel(root, text='PLEASE ENTER YOUR LICENSE KEY', font=('Arial', 12), text_color=FIXED_COLORS['sub_text_color'])
            print('Packing login_prompt...')
            login_prompt.pack(pady=10)
            login_frame = ctk.CTkFrame(root, fg_color='transparent')
            print('Packing login_frame...')
            login_frame.pack(pady=10)
            license_field_label = ctk.CTkLabel(login_frame, text='License Key', font=('Arial', 12), text_color=FIXED_COLORS['sub_text_color'])
            print('Packing license_field_label...')
            license_field_label.pack()
            license_entry = ctk.CTkEntry(login_frame, fg_color='#2e3536', border_width=0, font=('Arial', 14), width=300, height=40, corner_radius=10)
            print('Packing license_entry...')
            license_entry.pack(pady=10, ipady=5, fill='x')
            license_entry.insert(0, load_login_config())
            auth_status_label = ctk.CTkLabel(root, text='', font=('Arial', 14, 'bold'), text_color='#00ff00')
            print('Packing auth_status_label...')
            auth_status_label.pack(pady=10)

            def auth_gui():
                license_key = license_entry.get().strip()
                print(f'Attempting authorization with license key: {license_key}')
                if license_key:
                    if BYPASS_KEYAUTH:
                        print('Bypassing KeyAuth authorization...')
                        save_login_config(license_key)
                        auth_status_label.configure(text='Authorization bypassed!' if current_language == 'en' else 'Вы успешно авторизовались')
                        root.update()
                        root.after(2000, lambda: fade_out(root, lambda: show_main_menu(license_key)))
                    else:  # inserted
                        try:
                            keyauthapp.license(license_key)
                            print('License method called, proceeding...')
                        except Exception as e:
                            pass  # postinserted
                        else:  # inserted
                            save_login_config(license_key)
                            auth_status_label.configure(text='Authorization successful!' if current_language == 'en' else 'Вы успешно авторизовались')
                        root.update()
                        root.after(2000, lambda: fade_out(root, lambda: show_main_menu(license_key)))
                else:  # inserted
                    auth_status_label.configure(text='Please enter a license key!' if current_language == 'en' else 'Пожалуйста, введите лицензионный ключ!', text_color='#ff0000')
                    print(f'Authorization error: {e}')
                    auth_status_label.configure(text='Authorization failed!' if current_language == 'en' else 'Ошибка авторизации!', text_color='#ff0000')
                    return None
            continue_button = ctk.CTkButton(root, text=LANGUAGES[current_language]['continue_button'], command=auth_gui, fg_color=FIXED_COLORS['button_fg_color'], hover_color=FIXED_COLORS['button_hover_color'], border_width=2, border_color=FIXED_COLORS['border_glow_color'], width=150, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
            print('Packing continue_button...')
            continue_button.pack(pady=20)
            add_button_animation(continue_button)
            id_button = ctk.CTkButton(root, text='ID', command=info, fg_color=FIXED_COLORS['button_fg_color'], hover_color=FIXED_COLORS['button_hover_color'], border_width=2, border_color=FIXED_COLORS['border_glow_color'], width=50, height=30, font=('Arial', 12, 'bold'), corner_radius=15)
            print('Placing id_button...')
            id_button.place(relx=0.95, rely=0.95, anchor='se')
            add_button_animation(id_button)

            def update_login_texts():
                login_label.configure(text=LANGUAGES[current_language]['login_label'])
                login_prompt.configure(text=LANGUAGES[current_language]['login_prompt'])
                license_field_label.configure(text=LANGUAGES[current_language]['license_field'])
                continue_button.configure(text=LANGUAGES[current_language]['continue_button'])
                id_button.configure(text=LANGUAGES[current_language]['id_button'])
                root.title(LANGUAGES[current_language]['title'])
            update_login_texts()
            fade_in(root)
            print('Starting mainloop...')
            root.mainloop()
        print(f'Failed to set appearance mode: {e}')
        messagebox.showerror('Error', f'Failed to set appearance mode: {e}')
        print(f'Failed to create login window: {e}')
        messagebox.showerror('Error', f'Failed to create login window: {e}')

def show_main_menu(login):
    global progress_bar  # inserted
    global user_frame  # inserted
    global overlay  # inserted
    global top_frame  # inserted
    global ram_slider  # inserted
    global left_frame  # inserted
    global progress_label  # inserted
    for widget in root.winfo_children():
        widget.destroy()
    print('Showing main menu...')
    overlay = ctk.CTkFrame(root, fg_color=current_colors['background_color'], corner_radius=0)
    overlay.place(relwidth=1, relheight=1)
    top_frame = ctk.CTkFrame(root, fg_color=current_colors['background_color'], corner_radius=10, height=50)
    print('Packing top_frame...')
    top_frame.pack(fill='x', pady=10, padx=10)
    print('Top frame packed')
    user_frame = ctk.CTkFrame(top_frame, fg_color='#d0d0d0' if current_theme == 'light' else '#2e3536', corner_radius=10)
    print('Packing user_frame...')
    user_frame.pack(side='left', padx=10, pady=5)
    ctk.CTkLabel(user_frame, text='◇', font=('Arial', 14, 'bold'), text_color='#1a8cff').pack(side='left', padx=5)
    username_label = ctk.CTkLabel(user_frame, text='user', font=('Arial', 14, 'bold'), text_color=current_colors['text_color'])
    username_label.pack(side='left', padx=5)
    version_label = ctk.CTkLabel(user_frame, text=LANGUAGES[current_language]['version_text'], font=('Arial', 12), text_color=current_colors['sub_text_color'])
    version_label.pack(side='left', padx=5)
    print('User frame packed')
    icons_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
    print('Packing icons_frame...')
    icons_frame.pack(side='left', padx=5)
    back_button = ctk.CTkButton(icons_frame, text='↺', command=lambda: fade_out(root, create_login_window), fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=30, height=30, font=('Arial', 12), corner_radius=5)
    back_button.pack(side='left', padx=2)
    home_button = ctk.CTkButton(icons_frame, text='🏠', command=lambda: None, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=30, height=30, font=('Arial', 12), corner_radius=5)
    home_button.pack(side='left', padx=2)
    settings_button = ctk.CTkButton(icons_frame, text='⚙️', command=info, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=30, height=30, font=('Arial', 12), corner_radius=5)
    settings_button.pack(side='left', padx=2)
    print('Icons frame packed')

    def toggle_language():
        global current_language  # inserted
        current_language = 'ru' if current_language == 'en' else 'en'
        lang_button.configure(text=current_language.upper())
        update_main_menu_texts()
    lang_button = ctk.CTkButton(top_frame, text=current_language.upper(), command=toggle_language, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=50, height=30, font=('Arial', 12, 'bold'), corner_radius=15)
    print('Packing lang_button in main menu...')
    lang_button.pack(side='right', padx=10)
    theme_button = ctk.CTkButton(top_frame, text='☀️/🌙', command=toggle_theme, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=50, height=30, font=('Arial', 12, 'bold'), corner_radius=15)
    print('Packing theme_button...')
    theme_button.pack(side='right', padx=10)
    print('Language and theme buttons packed')
    main_frame = ctk.CTkFrame(root, fg_color='transparent')
    print('Packing main_frame...')
    main_frame.pack(fill='both', expand=True, padx=20)
    print('Main frame packed')
    left_frame = ctk.CTkFrame(main_frame, fg_color=current_colors['background_color'], corner_radius=10, width=300)
    print('Packing left_frame...')
    left_frame.pack(side='left', fill='y', padx=(0, 10), pady=10)
    print('Left frame packed')
    version_label = ctk.CTkLabel(left_frame, text=LANGUAGES[current_language]['version_label'], text_color=current_colors['sub_text_color'], font=('Arial', 12), anchor='w')
    print('Packing version_label in left_frame...')
    version_label.pack(pady=(10, 0), padx=15, fill='x')
    version_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
    print('Packing version_frame...')
    version_frame.pack(pady=5, padx=15, fill='x')
    ctk.CTkLabel(version_frame, text='◇ ', font=('Arial', 24, 'bold'), text_color='#1a8cff').pack(side='left')
    ctk.CTkLabel(version_frame, text='1.16.5', font=('Arial', 24, 'bold'), text_color=current_colors['text_color']).pack(side='left')
    print('Version label packed')
    button_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
    print('Packing button_frame...')
    button_frame.pack(pady=10, padx=15, fill='x')
    play_button = ctk.CTkButton(button_frame, text=LANGUAGES[current_language]['play_button'], fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=120, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
    play_button.pack(side='left', padx=(0, 5))
    change_button = ctk.CTkButton(button_frame, text=LANGUAGES[current_language]['change_version_button'], command=build_select, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], font=('Arial', 12), width=100, height=40, corner_radius=20)
    change_button.pack(side='left')
    print('Button frame packed')
    description_label = ctk.CTkLabel(left_frame, text=LANGUAGES[current_language]['description_label'], text_color=current_colors['sub_text_color'], font=('Arial', 12), anchor='w')
    print('Packing description_label...')
    description_label.pack(pady=(10, 0), padx=15, fill='x')
    description_text = ctk.CTkLabel(left_frame, text=LANGUAGES[current_language]['description_text'], text_color=current_colors['text_color'], font=('Arial', 12), anchor='w', wraplength=270, justify='left')
    print('Packing description_text...')
    description_text.pack(pady=(5, 0), padx=15, fill='x')
    print('Description packed')
    discord_button = ctk.CTkButton(left_frame, text=LANGUAGES[current_language]['discord_button'], command=lambda: webbrowser.open('https://discord.gg/zPnzUEXgmf'), fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=150, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
    print('Packing discord_button...')
    discord_button.pack(pady=10, padx=15, fill='x')
    print('Discord button packed')

    def open_color_settings():
        color_window = ctk.CTkToplevel(root)
        color_window.title(LANGUAGES[current_language]['color_window_title'])
        color_window.geometry('400x300')
        overlay = ctk.CTkFrame(color_window, fg_color=current_colors['background_color'], corner_radius=0)
        overlay.place(relwidth=1, relheight=1)
        button_fg_frame = ctk.CTkFrame(color_window, fg_color='transparent')
        print('Packing button_fg_frame...')
        button_fg_frame.pack(pady=10, padx=10, fill='x')
        button_fg_label = ctk.CTkLabel(button_fg_frame, text=LANGUAGES[current_language]['button_fg_label'], font=('Arial', 12), text_color=current_colors['text_color'])
        button_fg_label.pack(side='left', padx=5)
        button_fg_var = ctk.StringVar(value=current_colors['button_fg_color'])
        button_fg_entry = ctk.CTkEntry(button_fg_frame, textvariable=button_fg_var, width=100, fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', border_width=0, font=('Arial', 12))
        button_fg_entry.pack(side='left', padx=5)

        def choose_button_fg_color():
            color = colorchooser.askcolor(title='Choose Button Color', initialcolor=button_fg_var.get())[1]
            if color:
                button_fg_var.set(color)
        button_fg_choose = ctk.CTkButton(button_fg_frame, text='...', command=choose_button_fg_color, width=30, height=30, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'])
        button_fg_choose.pack(side='left')
        add_button_animation(button_fg_choose)
        button_hover_frame = ctk.CTkFrame(color_window, fg_color='transparent')
        print('Packing button_hover_frame...')
        button_hover_frame.pack(pady=10, padx=10, fill='x')
        button_hover_label = ctk.CTkLabel(button_hover_frame, text=LANGUAGES[current_language]['button_hover_label'], font=('Arial', 12), text_color=current_colors['text_color'])
        button_hover_label.pack(side='left', padx=5)
        button_hover_var = ctk.StringVar(value=current_colors['button_hover_color'])
        button_hover_entry = ctk.CTkEntry(button_hover_frame, textvariable=button_hover_var, width=100, fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', border_width=0, font=('Arial', 12))
        button_hover_entry.pack(side='left', padx=5)

        def choose_button_hover_color():
            color = colorchooser.askcolor(title='Choose Button Hover Color', initialcolor=button_hover_var.get())[1]
            if color:
                button_hover_var.set(color)
        button_hover_choose = ctk.CTkButton(button_hover_frame, text='...', command=choose_button_hover_color, width=30, height=30, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'])
        button_hover_choose.pack(side='left')
        add_button_animation(button_hover_choose)
        background_frame = ctk.CTkFrame(color_window, fg_color='transparent')
        print('Packing background_frame...')
        background_frame.pack(pady=10, padx=10, fill='x')
        background_label = ctk.CTkLabel(background_frame, text=LANGUAGES[current_language]['background_label'], font=('Arial', 12), text_color=current_colors['text_color'])
        background_label.pack(side='left', padx=5)
        background_var = ctk.StringVar(value=current_colors['background_color'])
        background_entry = ctk.CTkEntry(background_frame, textvariable=background_var, width=100, fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', border_width=0, font=('Arial', 12))
        background_entry.pack(side='left', padx=5)

        def choose_background_color():
            color = colorchooser.askcolor(title='Choose Background Color', initialcolor=background_var.get())[1]
            if color:
                background_var.set(color)
        background_choose = ctk.CTkButton(background_frame, text='...', command=choose_background_color, width=30, height=30, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'])
        background_choose.pack(side='left')
        add_button_animation(background_choose)

        def apply_colors():
            global current_colors  # inserted
            new_colors = {'button_fg_color': button_fg_var.get(), 'button_hover_color': button_hover_var.get(), 'background_color': background_var.get(), 'text_color': current_colors['text_color'], 'sub_text_color': current_colors['sub_text_color'], 'border_glow_color': current_colors['border_glow_color']}
            for key, color in new_colors.items():
                if key in ['text_color', 'sub_text_color', 'border_glow_color']:
                    continue
                if not is_valid_hex_color(color):
                    messagebox.showerror('Error', LANGUAGES[current_language]['invalid_color_error'])
                    return
            else:  # inserted
                save_color_config(new_colors)
                current_colors = new_colors
                messagebox.showinfo('Success', 'Colors applied! Please reopen the menu to see changes.' if current_language == 'en' else 'Цвета применены! Пожалуйста, переоткройте меню, чтобы увидеть изменения.')
                color_window.destroy()
        apply_button = ctk.CTkButton(color_window, text=LANGUAGES[current_language]['apply_button'], command=apply_colors, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=120, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
        print('Packing apply_button in color settings...')
        apply_button.pack(pady=10)
        add_button_animation(apply_button)

        def reset_colors():
            global current_colors  # inserted
            default_colors = THEME_COLORS[current_theme]
            save_color_config(default_colors)
            current_colors = default_colors
            messagebox.showinfo('Success', 'Colors reset to default! Please reopen the menu to see changes.' if current_language == 'en' else 'Цвета сброшены на стандартные! Пожалуйста, переоткройте меню, чтобы увидеть изменения.')
            color_window.destroy()
        reset_button = ctk.CTkButton(color_window, text=LANGUAGES[current_language]['reset_button'], command=reset_colors, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=120, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
        print('Packing reset_button in color settings...')
        reset_button.pack(pady=5)
        add_button_animation(reset_button)
    color_button = ctk.CTkButton(left_frame, text=LANGUAGES[current_language]['color_button'], command=open_color_settings, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=150, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
    print('Packing color_button...')
    color_button.pack(pady=10, padx=15, fill='x')
    print('Color button packed')

    def open_settings():
        settings_window = ctk.CTkToplevel(root)
        settings_window.title('Settings')
        settings_window.geometry('400x300')
        overlay = ctk.CTkFrame(settings_window, fg_color=current_colors['background_color'], corner_radius=0)
        overlay.place(relwidth=1, relheight=1)
        ctk.CTkLabel(settings_window, text='Coming soon...', font=('Arial', 16, 'bold'), text_color=current_colors['text_color']).pack(pady=20)
    settings_button = ctk.CTkButton(left_frame, text=LANGUAGES[current_language]['settings_button'], command=open_settings, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=150, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
    print('Packing settings_button...')
    settings_button.pack(pady=10, padx=15, fill='x')
    print('Settings button packed')
    changelog_button = ctk.CTkButton(left_frame, text=LANGUAGES[current_language]['changelog_button'], command=view_changelog, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=150, height=40, font=('Arial', 14, 'bold'), corner_radius=20)
    print('Packing changelog_button...')
    changelog_button.pack(pady=10, padx=15, fill='x')
    print('Changelog button packed')
    right_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
    print('Packing right_frame...')
    right_frame.pack(side='right', fill='both', expand=True, pady=10)
    print('Right frame packed')
    game_settings_label = ctk.CTkLabel(right_frame, text=LANGUAGES[current_language]['game_settings_label'], font=('Arial', 16, 'bold'), text_color=current_colors['text_color'])
    print('Packing game_settings_label...')
    game_settings_label.pack(anchor='w', padx=10)
    ram_label = ctk.CTkLabel(right_frame, text=LANGUAGES[current_language]['ram_label'], text_color=current_colors['sub_text_color'], font=('Arial', 12), anchor='w')
    print('Packing ram_label...')
    ram_label.pack(anchor='w', pady=(10, 0), padx=10)
    ram_description = ctk.CTkLabel(right_frame, text=LANGUAGES[current_language]['ram_description'], font=('Arial', 12), text_color=current_colors['text_color'], anchor='w', wraplength=250, justify='left')
    print('Packing ram_description...')
    ram_description.pack(anchor='w', padx=10)
    ram_frame = ctk.CTkFrame(right_frame, fg_color='transparent')
    print('Packing ram_frame...')
    ram_frame.pack(fill='x', pady=5, padx=10)
    ram_value = ctk.DoubleVar(value=int(load_memory_config()))
    ram_display_label = ctk.CTkLabel(ram_frame, text=f'{int(ram_value.get())} MB', font=('Arial', 12), text_color=current_colors['text_color'])
    ram_display_label.pack(side='right')
    ram_slider = ctk.CTkSlider(ram_frame, from_=512, to=8192, variable=ram_value, width=200, fg_color=current_colors['button_fg_color'], progress_color=current_colors['button_hover_color'], button_color=current_colors['button_fg_color'], button_hover_color=current_colors['button_hover_color'])
    ram_slider.pack(side='left', fill='x', expand=True)

    def update_ram_label(*args):
        ram_display_label.configure(text=f'{int(ram_value.get())} MB')
        save_memory_config(str(int(ram_value.get())))
    ram_value.trace_add('write', update_ram_label)
    ram_select_button = ctk.CTkButton(right_frame, text='...', command=lambda: ram_select(root, ram_display_label, ram_value), fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], width=30, height=30, font=('Arial', 12), corner_radius=5)
    print('Packing ram_select_button...')
    ram_select_button.pack(anchor='e', padx=10)
    add_button_animation(ram_select_button)
    print('RAM settings packed')
    game_window_label = ctk.CTkLabel(right_frame, text=LANGUAGES[current_language]['game_window_label'], text_color=current_colors['sub_text_color'], font=('Arial', 12), anchor='w')
    print('Packing game_window_label...')
    game_window_label.pack(anchor='w', pady=(10, 0), padx=10)
    game_window_description = ctk.CTkLabel(right_frame, text=LANGUAGES[current_language]['game_window_description'], text_color=current_colors['text_color'], font=('Arial', 12), anchor='w', wraplength=250, justify='left')
    print('Packing game_window_description...')
    game_window_description.pack(anchor='w', padx=10)
    window_frame = ctk.CTkFrame(right_frame, fg_color='transparent')
    print('Packing window_frame...')
    window_frame.pack(fill='x', pady=5, padx=10)
    width, height = load_window_config()
    height_var = ctk.StringVar(value=height)
    width_var = ctk.StringVar(value=width)
    height_label = ctk.CTkLabel(window_frame, text=LANGUAGES[current_language]['height_label'], font=('Arial', 12), text_color=current_colors['text_color'])
    height_label.pack(side='left')
    height_entry = ctk.CTkEntry(window_frame, textvariable=height_var, width=50, fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', border_width=0, font=('Arial', 12), corner_radius=5)
    height_entry.pack(side='left', padx=5)
    ctk.CTkLabel(window_frame, text='x', font=('Arial', 12), text_color=current_colors['text_color']).pack(side='left')
    width_entry = ctk.CTkEntry(window_frame, textvariable=width_var, width=50, fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', border_width=0, font=('Arial', 12), corner_radius=5)
    width_entry.pack(side='left', padx=5)
    width_label = ctk.CTkLabel(window_frame, text=LANGUAGES[current_language]['width_label'], font=('Arial', 12), text_color=current_colors['text_color'])
    width_label.pack(side='left')

    def save_window_size():
        save_window_config(width_var.get(), height_var.get())
    height_var.trace_add('write', lambda *args: save_window_size())
    width_var.trace_add('write', lambda *args: save_window_size())
    print('Window settings packed')
    progress_frame = ctk.CTkFrame(right_frame, fg_color='transparent')
    print('Packing progress_frame...')
    progress_frame.pack(fill='x', pady=10, padx=10)
    progress_label = ctk.CTkLabel(progress_frame, text='', anchor='w', font=('Arial', 12), text_color=current_colors['text_color'])
    progress_label.pack(anchor='w')
    progress_bar = ctk.CTkProgressBar(progress_frame, width=200, fg_color='#2e3536' if current_theme == 'dark' else '#d0d0d0', progress_color=current_colors['button_hover_color'])
    progress_bar.pack(fill='x')
    print('Progress frame packed')
    view_more_button = ctk.CTkButton(right_frame, text=LANGUAGES[current_language]['view_more_settings'], command=info, fg_color=current_colors['button_fg_color'], hover_color=current_colors['button_hover_color'], border_width=2, border_color=current_colors['border_glow_color'], font=('Arial', 14, 'bold'), corner_radius=20, width=200, height=40)
    print('Packing view_more_button...')
    view_more_button.pack(anchor='e', pady=10, padx=10)
    print('View more button packed')

    def update_main_menu_texts():
        version_label.configure(text=LANGUAGES[current_language]['version_label'])
        play_button.configure(text=LANGUAGES[current_language]['play_button'])
        change_button.configure(text=LANGUAGES[current_language]['change_version_button'])
        description_label.configure(text=LANGUAGES[current_language]['description_label'])
        description_text.configure(text=LANGUAGES[current_language]['description_text'])
        game_settings_label.configure(text=LANGUAGES[current_language]['game_settings_label'])
        ram_label.configure(text=LANGUAGES[current_language]['ram_label'])
        ram_description.configure(text=LANGUAGES[current_language]['ram_description'])
        game_window_label.configure(text=LANGUAGES[current_language]['game_window_label'])
        game_window_description.configure(text=LANGUAGES[current_language]['game_window_description'])
        height_label.configure(text=LANGUAGES[current_language]['height_label'])
        width_label.configure(text=LANGUAGES[current_language]['width_label'])
        view_more_button.configure(text=LANGUAGES[current_language]['view_more_settings'])
        version_label.configure(text=LANGUAGES[current_language]['version_text'])
        discord_button.configure(text=LANGUAGES[current_language]['discord_button'])
        color_button.configure(text=LANGUAGES[current_language]['color_button'])
        settings_button.configure(text=LANGUAGES[current_language]['settings_button'])
        changelog_button.configure(text=LANGUAGES[current_language]['changelog_button'])
        play_button.configure(command=lambda: start(progress_bar, progress_label, width_var.get(), height_var.get()))
        update_theme()
    update_main_menu_texts()
    fade_in(root)
    print('Main menu texts updated')
if __name__ == '__main__':
    try:
        print('Starting loader...')
        create_welcome_window()
    except Exception as e:
        pass  # postinserted
    print(f'Failed to import required libraries: {e}')
    print('Please install the required libraries using: pip install customtkinter requests colorama keyauth Pillow')
    sys.exit(1)
    print(f'Failed to create KeyAuth object: {e}')
    print(f'Error in main: {e}')
    messagebox.showerror('Error', f'Error in main: {e}')