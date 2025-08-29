import os
import json
import ctypes
import curses
from curses import wrapper
from cryptography.fernet import Fernet

PASSWORD_FILE = "passwords.json"
KEY_FILE = "key.key"
DLL_FILE = "password_decryptor.dll"

class PasswordDecryptorDLL:
    def __init__(self):
        self.dll_loaded = False
        self.load_dll()
    
    def load_dll(self):
        try:
            if os.path.exists(DLL_FILE):
                self.dll = ctypes.CDLL(DLL_FILE)
                self.dll_loaded = True
            else:
                pass  # DLL not found, fallback
        except Exception:
            pass
    
    def decrypt_password(self, encrypted_data, key):
        if self.dll_loaded:
            try:
                enc_bytes = encrypted_data.encode('utf-8')
                key_bytes = key
                
                self.dll.decrypt_password.argtypes = [
                    ctypes.c_char_p,
                    ctypes.c_int,
                    ctypes.c_char_p,
                    ctypes.c_int,
                    ctypes.c_char_p,
                    ctypes.c_int
                ]
                self.dll.decrypt_password.restype = ctypes.c_int
                
                buffer_size = 256
                output_buffer = ctypes.create_string_buffer(buffer_size)
                
                result = self.dll.decrypt_password(
                    enc_bytes, len(enc_bytes),
                    key_bytes, len(key_bytes),
                    output_buffer, buffer_size
                )
                
                if result > 0:
                    return output_buffer.value.decode('utf-8')
                else:
                    return None
            except Exception:
                return None
        else:
            return self.python_decrypt(encrypted_data, key)
    
    def python_decrypt(self, encrypted_data, key):
        try:
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data.encode())
            return decrypted.decode('utf-8')
        except Exception:
            return None

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return key

def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        return {}
    try:
        with open(PASSWORD_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_passwords(passwords):
    with open(PASSWORD_FILE, 'w') as f:
        json.dump(passwords, f)

def encrypt_password(password, key):
    cipher = Fernet(key)
    encrypted = cipher.encrypt(password.encode())
    return encrypted.decode('utf-8')

def input_prompt(stdscr, prompt):
    curses.echo()
    stdscr.addstr(prompt)
    stdscr.refresh()
    input_str = stdscr.getstr().decode('utf-8').strip()
    curses.noecho()
    return input_str

def message_box(stdscr, message):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    lines = message.split('\n')
    for i, line in enumerate(lines):
        x = w//2 - len(line)//2
        y = h//2 - len(lines)//2 + i
        stdscr.addstr(y, x, line)
    stdscr.addstr(h-2, 0, "Press any key to continue...")
    stdscr.refresh()
    stdscr.getch()

def menu(stdscr, options, title="Menu"):
    current_row = 0
    curses.curs_set(0)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Enable mouse events
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    
    while True:
        stdscr.clear()
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(1, w//2 - len(title)//2, title)
        stdscr.attroff(curses.A_BOLD)
        
        # Draw instructions
        instructions = "↑↓ Arrows / Mouse Click / Enter"
        stdscr.addstr(h-3, w//2 - len(instructions)//2, instructions, curses.A_DIM)

        # Draw menu options
        for idx, option in enumerate(options):
            x = w//2 - len(option)//2
            y = 3 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, option)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, option)
        stdscr.refresh()

        key = stdscr.getch()

        # Handle keyboard navigation
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            return current_row
        
        # Handle mouse events
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, _ = curses.getmouse()
                
                # Check if click is within menu area
                menu_start_y = 3
                menu_end_y = 3 + len(options)
                
                if menu_start_y <= my < menu_end_y:
                    clicked_row = my - menu_start_y
                    if 0 <= clicked_row < len(options):
                        # Check if click is within the option text horizontally
                        option_text = options[clicked_row]
                        option_start_x = w//2 - len(option_text)//2
                        option_end_x = option_start_x + len(option_text)
                        
                        if option_start_x <= mx < option_end_x:
                            return clicked_row
            except:
                pass  # Ignore mouse errors

def list_passwords_screen(stdscr, passwords):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, w//2 - 7, "Saved Passwords", curses.A_BOLD)
    if not passwords:
        stdscr.addstr(h//2, w//2 - 10, "No saved passwords.")
    else:
        sorted_services = sorted(passwords.keys())
        max_display = min(len(sorted_services), h - 5)
        for idx, service in enumerate(sorted_services[:max_display]):
            stdscr.addstr(3 + idx, 4, f"{idx+1}. {service}")
        if len(sorted_services) > max_display:
            stdscr.addstr(h-3, 4, f"... and {len(sorted_services) - max_display} more")
    stdscr.addstr(h-2, 0, "Press any key or click to return to menu...")
    stdscr.refresh()
    stdscr.getch()

def add_password_screen(stdscr, passwords, key):
    stdscr.clear()
    stdscr.addstr(1, 2, "Add New Password", curses.A_BOLD)
    service = input_prompt(stdscr, "Service name: ")
    if not service:
        message_box(stdscr, "Service name cannot be empty.")
        return
    password = input_prompt(stdscr, "Password: ")
    if not password:
        message_box(stdscr, "Password cannot be empty.")
        return
    if service in passwords:
        confirm = input_prompt(stdscr, f"'{service}' exists. Overwrite? (y/n): ").lower()
        if confirm != 'y':
            message_box(stdscr, "Add cancelled.")
            return
    encrypted = encrypt_password(password, key)
    passwords[service] = encrypted
    save_passwords(passwords)
    message_box(stdscr, f"Password for '{service}' saved.")

def view_password_screen(stdscr, passwords, decryptor, key):
    stdscr.clear()
    stdscr.addstr(1, 2, "View Password", curses.A_BOLD)
    service = input_prompt(stdscr, "Service name: ")
    if service not in passwords:
        message_box(stdscr, f"No password found for '{service}'.")
        return
    encrypted = passwords[service]
    decrypted = decryptor.decrypt_password(encrypted, key)
    if decrypted:
        message_box(stdscr, f"Password for '{service}':\n\n{decrypted}")
    else:
        message_box(stdscr, "Failed to decrypt password.")

def delete_password_screen(stdscr, passwords):
    stdscr.clear()
    stdscr.addstr(1, 2, "Delete Password", curses.A_BOLD)
    service = input_prompt(stdscr, "Service name: ")
    if service not in passwords:
        message_box(stdscr, f"No password found for '{service}'.")
        return
    confirm = input_prompt(stdscr, f"Delete password for '{service}'? (y/n): ").lower()
    if confirm == 'y':
        del passwords[service]
        save_passwords(passwords)
        message_box(stdscr, f"Password for '{service}' deleted.")
    else:
        message_box(stdscr, "Delete cancelled.")

def main(stdscr):
    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)  # Faster mouse response
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    key = load_key()
    decryptor = PasswordDecryptorDLL()
    passwords = load_passwords()

    options = ["List Passwords", "Add Password", "View Password", "Delete Password", "Exit"]

    while True:
        choice = menu(stdscr, options, "Password Manager")
        if choice == 0:
            list_passwords_screen(stdscr, passwords)
        elif choice == 1:
            add_password_screen(stdscr, passwords, key)
        elif choice == 2:
            view_password_screen(stdscr, passwords, decryptor, key)
        elif choice == 3:
            delete_password_screen(stdscr, passwords)
        elif choice == 4:
            break

if __name__ == "__main__":
    wrapper(main)
