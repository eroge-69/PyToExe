import requests
import time
import tkinter as tk
from tkinter import ttk, messagebox
import json
from functools import partial
import keyboard
import os
from PIL import Image, ImageTk
import psutil  # Add this import at the top
import ctypes  # Add this import at the top
import threading
from datetime import datetime
import tldextract
import queue
import socket

try:
    import pydivert
    PYDIVERT_AVAILABLE = True
except ImportError:
    PYDIVERT_AVAILABLE = False

import struct
import ssl


# URL of the Flask server (Admin server)
SETTINGS_FILE = 'settings.json'

# Default settings
DEFAULT_SETTINGS = {
    'SERVER_URL': 'http://192.168.80.139:5000',
    'PIN': '2312'
}

# Load settings from file or use defaults
settings = DEFAULT_SETTINGS.copy()
def load_settings():
    global settings
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings.update(json.load(f))
    except FileNotFoundError:
        pass

def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

load_settings()
SERVER_URL = settings['SERVER_URL']
PC_SELECTION_FILE = 'pc_selection.json'

# Global variables
pc_label = None
status_label = None
selected_pc = None
selection_frame = None
main_frame = None
selection_dropdown = None
desktop_button = None
pc_buttons = []
lock_screen = None  # Variable to hold the lock screen window

TELEGRAM_BOT_TOKEN = '7303058896:AAGqQd-s2xG8903SX7mmRd6N6KkbqagKWTk'
TELEGRAM_USER_ID = 687911625


def load_pc_selection():
    try:
        with open(PC_SELECTION_FILE, 'r') as f:
            return json.load(f).get('selected_pc')
    except FileNotFoundError:
        return None

def get_pc_status():
    try:
        response = requests.get(f"{SERVER_URL}/get_pcs")
        pcs = response.json()
        for pc in pcs:
            if pc['pc_name'] == selected_pc.get():
                return pc
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la obținerea statusului PC: {str(e)}")
    return None

def get_active_application():
    """Get the name of the currently active application."""
    try:
        # Get the active window
        active_window = psutil.Process(psutil.win32.process_get_current_process_id())
        return active_window.name()
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la obținerea aplicației active: {str(e)}")
    return None


def hide_lock_screen():
    global lock_screen
    if lock_screen:
        lock_screen.destroy()
        lock_screen = None

def show_message(message_data):
    global lock_screen

    
    message_window = tk.Toplevel(root)
    message_window.title("Mesaj")
    message_window.attributes('-fullscreen', True)
    message_window.configure(bg='black')
    
    # Make message window stay on top of everything
    message_window.attributes('-topmost', True)
    message_window.lift()
    message_window.focus_force()
    
    # Create message frame
    message_frame = tk.Frame(message_window, bg='black')
    message_frame.pack(expand=True)
    
    # Add Vibe Academy logo
    try:
        logo_image = Image.open("static/media/vibe_logo_white.png")
        logo_image = logo_image.resize((109, 95), Image.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(message_frame, image=logo_photo, bg='black')
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.pack(pady=(0, 20))
    except Exception as e:
        print(f"Eroare la încărcarea logoului: {e}")
    
    # Message text
    message_label = tk.Label(
        message_frame,
        text=message_data['text'],
        fg='white',
        bg='black',
        font=('Outfit', 24),
        wraplength=800
    )
    message_label.pack(pady=20)
    
    # Close button for simple messages
    if message_data['type'] == 'simple':
        close_button = tk.Button(
            message_frame,
            text="Închide",
            command=message_window.destroy,
            bg='#2E7BFF',
            fg='white',
            font=('Outfit', 12, 'bold'),
            width=10,
            relief='flat',
            borderwidth=0
        )
        close_button.pack(pady=20)
    
    # Auto-close for time messages
    if message_data['type'] == 'time':
        duration = int(message_data['duration'])
        message_window.after(duration * 1000, message_window.destroy)
    
    # Function to keep message on top
    def keep_message_on_top():
        if message_window.winfo_exists():
            message_window.lift()
            message_window.attributes('-topmost', True)
            message_window.after(100, keep_message_on_top)
    
    keep_message_on_top()

def check_session_status():
    while True:
        pc_status = get_pc_status()
        if pc_status:
            if pc_status['is_active']:

                if pc_status.get('is_locked', False):
                    status_label.config(text="PC-ul este blocat. Vă rugăm să așteptați...", fg="#bf0101", font=('Outfit', 29, 'bold'))
                    root.deiconify()  # Show the window
                    root.attributes('-topmost', True)
                    root.lift()  # Bring the window to the front
                    root.focus_force()  # Focus on the window
                    desktop_button.pack_forget()  # Hide the desktop button when locked
                    for button in pc_buttons:
                        button.pack_forget()
                    # Block all system keys when PC is locked
                    try:
                        keyboard._listener.blocking_keys.clear()  # Clear all blocked keys first
                        keyboard.block_key('Win')
                        keyboard.block_key('Alt')
                        keyboard.block_key('Tab')
                        keyboard.block_key('Ctrl')
                        keyboard.block_key('Delete')
                        keyboard.block_key('F4')
                        keyboard.block_key('F5')
                        keyboard.block_key('F6')
                        keyboard.block_key('F7')
                        keyboard.block_key('F8')
                        keyboard.block_key('F9')
                        keyboard.block_key('F10')
                        keyboard.block_key('F11')
                        keyboard.block_key('F12')
                        keyboard.block_key('Esc')
                    except:
                        pass
                else:
                    hide_lock_screen()  # Hide the lock screen
                    status_label.config(text=f"Sesiunea a început pentru {pc_status['user_name']}", fg="#06d406", font=('Outfit', 29, 'bold'))
                    root.attributes('-topmost', False)
                    desktop_button.pack(pady=20)  # Show the desktop button when unlocked
                    for button in pc_buttons:
                        button.pack(pady=5)  # Show the button again
                    # Unblock all keys when PC is unlocked
                    try:
                        keyboard._listener.blocking_keys.clear()  # Clear all blocked keys first
                        keyboard.unblock_key('Win')
                        keyboard.unblock_key('Alt')
                        keyboard.unblock_key('Tab')
                        keyboard.unblock_key('Ctrl')
                        keyboard.unblock_key('Delete')
                        keyboard.unblock_key('F4')
                        keyboard.unblock_key('F5')
                        keyboard.unblock_key('F6')
                        keyboard.unblock_key('F7')
                        keyboard.unblock_key('F8')
                        keyboard.unblock_key('F9')
                        keyboard.unblock_key('F10')
                        keyboard.unblock_key('F11')
                        keyboard.unblock_key('F12')
                        keyboard.unblock_key('Esc')
                        keyboard.block_key('Win+Tab')
                    except:
                        pass
            else:
                hide_lock_screen()  # Hide the lock screen
                status_label.config(text="Sesiunea nu a început", fg="#bf0101")
                desktop_button.pack_forget()  # Hide the desktop button when no session is active
                for button in pc_buttons:
                    button.pack_forget()
                # Block all system keys when no session is active
                try:
                    keyboard._listener.blocking_keys.clear()  # Clear all blocked keys first
                    keyboard.block_key('Win')
                    keyboard.block_key('Alt')
                    keyboard.block_key('Tab')
                    keyboard.block_key('Ctrl')
                    keyboard.block_key('Delete')
                    keyboard.block_key('F4')
                    keyboard.block_key('F5')
                    keyboard.block_key('F6')
                    keyboard.block_key('F7')
                    keyboard.block_key('F8')
                    keyboard.block_key('F9')
                    keyboard.block_key('F10')
                    keyboard.block_key('F11')
                    keyboard.block_key('F12')
                    keyboard.block_key('Esc')
                    keyboard.block_key('Win+Tab')
                except:
                    pass
            
            # Check for messages regardless of PC lock status
            if 'message' in pc_status:
                message_data = pc_status['message']
                current_time = time.time()
                
                # Check if message is scheduled
                if message_data.get('scheduled_time'):
                    try:
                        # Convert scheduled time from ISO format to timestamp
                        scheduled_time = time.mktime(time.strptime(message_data['scheduled_time'], '%Y-%m-%dT%H:%M'))
                        if current_time >= scheduled_time:
                            show_message(message_data)
                            # Clear the message after showing
                            requests.post(f"{SERVER_URL}/clear_message/{pc_status['pc_name']}")
                    except ValueError as e:
                        print(f"Eroare la parsarea timpului programat: {e}")
                else:
                    # Show message immediately
                    show_message(message_data)
                    # Clear the message after showing
                    requests.post(f"{SERVER_URL}/clear_message/{pc_status['pc_name']}")
        
        # Update button states based on current session status
        update_button_states()
        
        time.sleep(1)

def is_pc_in_use(pc_name):
    try:
        response = requests.get(f"{SERVER_URL}/get_pcs")
        pcs = response.json()
        for pc in pcs:
            if pc['pc_name'] == pc_name and pc.get('is_active', False):
                return True
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la verificarea stării PC-ului: {str(e)}")
    return False

def is_pc_locked(pc_name):
    try:
        response = requests.get(f"{SERVER_URL}/get_pcs")
        pcs = response.json()
        for pc in pcs:
            if pc['pc_name'] == pc_name:
                return pc.get('is_locked', False)
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la verificarea stării blocate a PC-ului: {str(e)}")
    return False

def update_button_states():
    try:
        response = requests.get(f"{SERVER_URL}/get_pcs")
        pcs = response.json()
        
        # Create a dictionary of PC states
        pc_states = {pc['pc_name']: pc for pc in pcs}
        
        # Update each button based on its PC's state
        for button in pc_buttons:
            pc_name = button.cget('text')
            if pc_name in pc_states:
                pc = pc_states[pc_name]
                if pc.get('is_active', False):
                    button.config(bg='grey', state='disabled')
                else:
                    button.config(bg='#2E7BFF', state='normal')
    except Exception as e:
        print(f"Eroare la actualizarea stărilor butoanelor: {e}")

def get_pc_number(pc_name):
    # Extract number from PC name (e.g., "PC1" -> 1)
    try:
        return int(''.join(filter(str.isdigit, pc_name)))
    except ValueError:
        return 0  # Return 0 if no number found

def update_available_pcs():
    if selection_frame.winfo_ismapped():  # Only update if selection frame is visible
        try:
            response = requests.get(f"{SERVER_URL}/get_pcs")
            pcs = response.json()
            
            # Sort PCs by number
            pcs.sort(key=lambda x: get_pc_number(x['pc_name']))
            
            # Create a dictionary of current buttons
            current_buttons = {button.cget('text'): button for button in pc_buttons}
            
            # Get all PC names (both active and inactive)
            all_pc_names = [pc['pc_name'] for pc in pcs]
            
            # Remove buttons for PCs that no longer exist
            for pc_name, button in list(current_buttons.items()):
                if pc_name not in all_pc_names:
                    button.destroy()
                    pc_buttons.remove(button)
            
            # Create or update buttons for all PCs
            for pc in pcs:
                pc_name = pc['pc_name']
                if pc_name not in current_buttons:
                    # Create new button
                    pc_button = tk.Button(
                        selection_frame,
                        text=pc_name,
                        command=lambda name=pc_name: confirm_pc_selection(name),
                        bg='#2E7BFF' if not pc.get('is_active', False) else 'grey',
                        fg='white',
                        font=('Outfit', 12, 'bold'),
                        width=15,
                        relief='flat',
                        borderwidth=0,
                        state='disabled' if pc.get('is_active', False) else 'normal'
                    )
                    pc_button.pack(pady=5)
                    pc_buttons.append(pc_button)
                else:
                    # Update existing button
                    button = current_buttons[pc_name]
                    button.config(
                        bg='#2E7BFF' if not pc.get('is_active', False) else 'grey',
                        state='disabled' if pc.get('is_active', False) else 'normal'
                    )
            
        except Exception as e:
            print(f"Eroare la actualizarea PC-urilor disponibile: {e}")

    # Schedule next update
    root.after(1000, update_available_pcs)

def create_selection_frame():
    global selection_frame, pc_buttons
    
    selection_frame = tk.Frame(container, bg='#17181D')
    selection_frame.pack(expand=True, fill='both')
    
    title_label = tk.Label(
        selection_frame, 
        text="Selectează PC", 
        fg='white', 
        bg='#17181D', 
        font=('Outfit', 18, 'bold')
    )
    title_label.pack(pady=20)

    # Create a frame to hold the buttons
    button_frame = tk.Frame(selection_frame, bg='#17181D')
    button_frame.pack(pady=10)

    # Clear previous buttons if any
    pc_buttons.clear()

    # Fetch all PCs from the server
    try:
        response = requests.get(f"{SERVER_URL}/get_pcs")
        pcs = response.json()
        
        # Sort PCs by number
        pcs.sort(key=lambda x: get_pc_number(x['pc_name']))
        
        # Create buttons for all PCs
        for pc in pcs:
            pc_button = tk.Button(
                button_frame,
                text=pc['pc_name'],
                command=lambda name=pc['pc_name']: confirm_pc_selection(name),
                bg='#2E7BFF' if not pc.get('is_active', False) else 'grey',
                fg='white',
                font=('Outfit', 12, 'bold'),
                width=15,
                relief='flat',
                borderwidth=0,
                state='disabled' if pc.get('is_active', False) else 'normal'
            )
            pc_button.pack(pady=5)
            pc_buttons.append(pc_button)
    except Exception as e:
        print(f"Eroare la crearea frame-ului de selecție: {e}")

def confirm_pc_selection(pc_name):
    if not pc_name:
        messagebox.showerror("Eroare", "Vă rugăm să selectați un PC")
        return
    
    if is_pc_in_use(pc_name):
        messagebox.showerror("Eroare", "Acest PC este deja folosit")
        return
    
    if is_pc_locked(pc_name):
        messagebox.showerror("Eroare", "Acest PC este blocat momentan")
        return
    
    if messagebox.askyesno("Confirmare", f"Sigur doriți să selectați {pc_name}?"):
        selected_pc.set(pc_name)
        register_pc_with_server(pc_name)
        
        # Update the is_used field in the JSON on the server
        try:
            response = requests.get(f"{SERVER_URL}/get_pcs")
            pcs = response.json()
            for pc in pcs:
                if pc['pc_name'] == pc_name:
                    pc['is_used'] = True  # Set is_used to true for the selected PC
                    break
            
            # Send the update to the server
            requests.post(f"{SERVER_URL}/update_pc/{pcs.index(pc)}", json=pc)
            
            pc_label.config(text=f"PC selectat: {pc_name}", fg="white")
            status_label.config(text="PC selectat. Se așteaptă sesiunea...", fg="#f9ff50")
            
            # Send Telegram alert for PC selection
            send_telegram_alert(domain="-", url="-", timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pc_name=pc_name)
            
            # Hide selection frame and show main frame
            selection_frame.pack_forget()
            main_frame.pack(expand=True, fill='both')
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la confirmarea selecției PC: {str(e)}")

def minimize_all_windows():
    ctypes.windll.user32.ShowWindow(ctypes.windll.user32.GetForegroundWindow(), 2)  # 2 = SW_MINIMIZE

def create_main_frame():
    global main_frame, pc_label, status_label, desktop_button
    
    main_frame = tk.Frame(container, bg='#17181D')
    
    # Create title section
    title_frame = tk.Frame(main_frame, bg='#17181D')
    title_frame.pack(pady=(0, 20))
    
    if logo_photo:
        logo_label = tk.Label(title_frame, image=logo_photo, bg='#17181D')
        logo_label.pack(side='left', padx=(0, 30))
    
    title_label = tk.Label(
        title_frame, 
        text="Client PC", 
        fg='white', 
        bg='#17181D', 
        font=('Outfit', 18, 'bold')
    )
    title_label.pack(side='left')
    
    # Create PC selection section
    pc_frame = tk.Frame(main_frame, bg='#17181D')
    pc_frame.pack(pady=10)
    
    pc_label = tk.Label(
        pc_frame, 
        text="", 
        fg='white', 
        bg='#17181D', 
        font=('Outfit', 12)
    )
    pc_label.pack()
    
    # Create status section
    status_frame = tk.Frame(main_frame, bg='#17181D')
    status_frame.pack(pady=20)
    
    status_label = tk.Label(
        status_frame, 
        text="Se așteaptă sesiunea...", 
        bg='#17181D', 
        fg="#f9ff50", 
        font=('Outfit', 12, 'bold')
    )
    status_label.pack()

    # Create Desktop button
    desktop_button = tk.Button(
        main_frame,
        text="Desktop",
        command=minimize_all_windows,  # Use the new function to minimize all windows
        bg='#2E7BFF',
        fg='white',
        font=('Outfit', 12, 'bold'),
        width=10,
        relief='flat',
        borderwidth=0
    )
    desktop_button.pack(pady=20)
    desktop_button.pack_forget()  # Initially hide the button

def show_settings_window():
    def save_and_close():
        new_url = url_entry.get().strip()
        if new_url:
            settings['SERVER_URL'] = new_url
            save_settings()
            global SERVER_URL
            SERVER_URL = new_url
        settings_win.destroy()

    def cancel():
        settings_win.destroy()

    def kill_app():
        root.destroy()

    settings_win = tk.Toplevel(root)
    settings_win.title('Setări')
    settings_win.geometry('420x320')
    settings_win.configure(bg='#17181D')
    settings_win.grab_set()
    settings_win.transient(root)
    settings_win.resizable(False, False)

    # Add logo if available
    try:
        logo_image = Image.open("static/media/vibe_logo_white.png")
        logo_image = logo_image.resize((70, 60), Image.LANCZOS)
        logo_photo_settings = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(settings_win, image=logo_photo_settings, bg='#17181D')
        logo_label.image = logo_photo_settings
        logo_label.pack(pady=(18, 0))
    except:
        logo_label = None

    # Title
    title_label = tk.Label(settings_win, text='Setări', bg='#17181D', fg='white', font=('Outfit', 18, 'bold'))
    title_label.pack(pady=(10, 18))

    # Server URL
    label = tk.Label(settings_win, text='URL Server:', bg='#17181D', fg='white', font=('Outfit', 12))
    label.pack(pady=(0, 5))
    url_entry = tk.Entry(settings_win, width=40, font=('Outfit', 12), bg='#23242A', fg='white', insertbackground='white', relief='flat', highlightthickness=1, highlightbackground='#2E7BFF')
    url_entry.insert(0, settings.get('SERVER_URL', ''))
    url_entry.pack(pady=5)

    # Button frame
    button_frame = tk.Frame(settings_win, bg='#17181D')
    button_frame.pack(pady=35)

    save_btn = tk.Button(
        button_frame, text='Salvează', command=save_and_close,
        bg='#2E7BFF', fg='white', font=('Outfit', 11, 'bold'), width=10, relief='flat', borderwidth=0, activebackground='#1a5dcc', activeforeground='white'
    )
    save_btn.pack(side='left', padx=10)

    cancel_btn = tk.Button(
        button_frame, text='Anulează', command=cancel,
        bg='#555', fg='white', font=('Outfit', 11), width=10, relief='flat', borderwidth=0, activebackground='#333', activeforeground='white'
    )
    cancel_btn.pack(side='left', padx=10)

    kill_btn = tk.Button(
        button_frame, text='Kill', command=kill_app,
        bg='#bf0101', fg='white', font=('Outfit', 11, 'bold'), width=10, relief='flat', borderwidth=0, activebackground='#8a0000', activeforeground='white'
    )
    kill_btn.pack(side='left', padx=10)

root = tk.Tk()
root.title("Client PC")
root.attributes('-fullscreen', True)
root.configure(bg='#17181D')

# Load and set the logo
try:
    logo_image = Image.open("static/media/vibe_logo_white.png")
    logo_image = logo_image.resize((109, 95), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
except:
    logo_photo = None

# Create main container
container = tk.Frame(root, bg='#17181D')
container.pack(expand=True, fill='both', padx=25, pady=25)

# Initialize variables
selected_pc = tk.StringVar(root)

# Create frames
create_selection_frame()
create_main_frame()

# Check if there's a saved PC selection
saved_pc = load_pc_selection()
if saved_pc and not is_pc_in_use(saved_pc):
    selected_pc.set(saved_pc)
    pc_label.config(text=f"PC selectat: {saved_pc}", fg="white")
    selection_frame.pack_forget()
    main_frame.pack(expand=True, fill='both')
else:
    main_frame.pack_forget()

# Start PC availability check
update_available_pcs()

def send_telegram_alert(domain, url, timestamp, pc_name):
    message = f"[ALERT] Site de joc detectat:\nPC: {saved_pc}\nDomeniu: {domain}\nTimp: {timestamp}\nURL: {url}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_USER_ID,
        'text': message
    }
    try:
        requests.post(telegram_url, data=payload, timeout=5)
    except Exception as e:
        print(f"Eroare la trimiterea mesajului Telegram: {e}")

def register_pc_with_server(pc_name):
    try:
        requests.post(f"{SERVER_URL}/register_pc_name", json={
            "hostname": socket.gethostname().lower(),
            "pc_name": pc_name
        }, timeout=5)
    except Exception as e:
        print(f"Failed to register PC name: {e}")

# # Create close button
# def on_enter(e):
#     close_button['bg'] = '#bf0101'

# def on_leave(e):
#     close_button['bg'] = '#ff5555'

# def close_app():
#     root.quit()

# close_button = tk.Button(
#     root, 
#     text="X", 
#     command=close_app,
#     bg='#ff5555',
#     fg='white',
#     font=('Outfit', 12, 'bold'),
#     width=3,
#     height=1,
#     relief='flat',
#     borderwidth=0
# )
# close_button.place(relx=0.98, rely=0.02, anchor='ne')
# close_button.bind('<Enter>', on_enter)
# close_button.bind('<Leave>', on_leave)

# Start status checking thread
import threading
thread = threading.Thread(target=check_session_status)
thread.daemon = True
thread.start()

# Block system keys initially
try:
    keyboard.block_key('Win')
    keyboard.block_key('Alt')
    keyboard.block_key('Tab')
    keyboard.block_key('Ctrl')
    keyboard.block_key('Delete')
    keyboard.block_key('F4')
    keyboard.block_key('F5')
    keyboard.block_key('F6')
    keyboard.block_key('F7')
    keyboard.block_key('F8')
    keyboard.block_key('F9')
    keyboard.block_key('F10')
    keyboard.block_key('F11')
    keyboard.block_key('F12')
    keyboard.block_key('Esc')
    keyboard.block_key('Win+Tab')
except:
    pass

# Add Alt+F4 handler to prevent app closing
def on_alt_f4(event):
    return False  # This will prevent the window from closing

root.bind('<Alt-F4>', on_alt_f4)
root.protocol('WM_DELETE_WINDOW', lambda: None)  # Prevent window closing via X button

# Add invisible settings button in the top-left corner
settings_button = tk.Button(
    root,
    text='',
    command=lambda: ask_for_pin(),
    bg='#17181D',
    activebackground='#17181D',
    bd=0,
    highlightthickness=0
)
settings_button.place(x=0, y=0, width=30, height=30)
settings_button.lift()  # Make sure it's on top
settings_button.lower()  # Keep it invisible (but clickable)
settings_button.config(cursor='hand2')

# PIN entry popup before showing settings

def ask_for_pin():
    def check_pin():
        entered = pin_entry.get()
        if entered == settings.get('PIN', '2312'):
            pin_win.destroy()
            show_settings_window()
        else:
            error_label.config(text='PIN incorect', fg='#bf0101')
            pin_entry.delete(0, 'end')
            pin_entry.focus_set()

    pin_win = tk.Toplevel(root)
    pin_win.title('Introduceți PIN-ul')
    pin_win.geometry('340x220')
    pin_win.configure(bg='#17181D')
    pin_win.grab_set()
    pin_win.transient(root)
    pin_win.resizable(False, False)

    # Add lock icon if available
    icon_frame = tk.Frame(pin_win, bg='#17181D')
    icon_frame.pack(pady=(18, 0))
    try:
        lock_img = Image.open("static/media/lock_icon.png")
        lock_img = lock_img.resize((38, 38), Image.LANCZOS)
        lock_photo = ImageTk.PhotoImage(lock_img)
        lock_label = tk.Label(icon_frame, image=lock_photo, bg='#17181D')
        lock_label.image = lock_photo
        lock_label.pack()
    except:
        # fallback: show emoji
        lock_label = tk.Label(icon_frame, text='🔒', bg='#17181D', fg='white', font=('Outfit', 28))
        lock_label.pack()

    # Title
    title_label = tk.Label(pin_win, text='Introduceți PIN-ul', bg='#17181D', fg='white', font=('Outfit', 16, 'bold'))
    title_label.pack(pady=(10, 8))

    # PIN entry
    pin_entry = tk.Entry(pin_win, show='*', width=18, font=('Outfit', 15, 'bold'), bg='#23242A', fg='white', insertbackground='white', relief='flat', highlightthickness=2, highlightbackground='#2E7BFF', justify='center')
    pin_entry.pack(pady=8)
    pin_entry.focus_set()

    # Error label
    error_label = tk.Label(pin_win, text='', bg='#17181D', fg='#bf0101', font=('Outfit', 10, 'bold'))
    error_label.pack(pady=(5, 0))

    # OK button
    btn = tk.Button(pin_win, text='OK', command=check_pin, bg='#2E7BFF', fg='white', font=('Outfit', 12, 'bold'), width=12, relief='flat', borderwidth=0, activebackground='#1a5dcc', activeforeground='white')
    btn.pack(pady=18)

    pin_win.bind('<Return>', lambda event: check_pin())

root.mainloop()