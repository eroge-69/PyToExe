import time
import threading
import sys
import subprocess
from pynput import keyboard, mouse
from pynput.mouse import Button
import psutil
import win32gui
import win32process

def install_and_import_dependencies():
    """Install and import required packages with better error handling"""
    required_packages = {
        'pynput': 'pynput',
        'psutil': 'psutil', 
        'pywin32': 'pywin32'
    }
    
    print("🔧 Checking dependencies...")
    
    for import_name, package_name in required_packages.items():
        try:
            if import_name == 'pywin32':
                import win32gui
                import win32process
                print(f"✓ {package_name} already installed")
            else:
                __import__(import_name)
                print(f"✓ {package_name} already installed")
        except ImportError:
            print(f"📦 Installing {package_name}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name], 
                                    capture_output=True, text=True)
                print(f"✓ {package_name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package_name}: {e}")
                print("Please manually install with: pip install pynput psutil pywin32")
                input("Press Enter to exit...")
                sys.exit(1)
    
    # Now import everything
    try:
        global psutil, win32gui, win32process, keyboard, mouse, Button
        import psutil
        import win32gui
        import win32process
        from pynput import keyboard, mouse
        from pynput.mouse import Button
        print("✓ All dependencies loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import dependencies: {e}")
        input("Press Enter to exit...")
        return False

class ProcessAutoClicker:
    def __init__(self, target_process_name):
        self.target_process_name = target_process_name.lower()
        self.is_h_pressed = False
        self.clicking = False
        self.mouse_controller = mouse.Controller()
        self.click_rate = 30  # clicks per second
        self.click_interval = 1.0 / self.click_rate
        self.running = True  # Added running flag for better control
        self.pressed_keys = set()
        
        print(f"\n✓ Auto-clicker attached to process: {target_process_name}")
        print("━" * 50)
        print("CONTROLS:")
        print("  Hold 'H' → Start rapid right-clicking")
        print("  Release 'H' → Stop clicking")
        print("  Press 'ESC' in target app → Exit program")
        print("  Press 'Ctrl+Shift+Q' anywhere → Force exit")
        print("━" * 50)
        print("⚠️  Only works when target process is the active window")
        print("🚀 Ready! Switch to your target application and hold 'H'")
        print()
    
    def get_active_process_name(self):
        """Get the name of the currently active window's process"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return None
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name().lower()
        except Exception as e:
            print(f"Debug: Error getting active process: {e}")
            return None
    
    def is_target_process_active(self):
        """Check if the target process is currently active"""
        active_process = self.get_active_process_name()
        if active_process:
            return self.target_process_name in active_process or active_process in self.target_process_name
        return False
    
    def click_loop(self):
        """Continuous clicking loop that runs in a separate thread"""
        print("🔄 Click thread started")
        while self.clicking and self.running:
            try:
                if self.is_h_pressed and self.is_target_process_active():
                    self.mouse_controller.click(Button.right)
                time.sleep(self.click_interval)
            except Exception as e:
                print(f"❌ Click error: {e}")
                time.sleep(0.1)  # Brief pause on error
        print("🔄 Click thread stopped")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            self.pressed_keys.add(key)
            
            if hasattr(key, 'char') and key.char and key.char.lower() == 'h':
                if not self.is_h_pressed:
                    self.is_h_pressed = True
                    if self.is_target_process_active():
                        print("🔥 CLICKING STARTED (30/sec)")
                    else:
                        print("⚠️  H pressed but target process not active")
        except AttributeError:
            if key == keyboard.Key.esc and self.is_target_process_active():
                print("\n👋 ESC pressed in target process - Exiting auto-clicker...")
                self.stop()
                return False
        except Exception as e:
            print(f"❌ Key press error: {e}")
        
        if (keyboard.Key.ctrl in self.pressed_keys and 
            keyboard.Key.shift in self.pressed_keys and 
            hasattr(key, 'char') and key.char and key.char.lower() == 'q'):
            print("\n👋 Ctrl+Shift+Q pressed - Force exiting auto-clicker...")
            self.stop()
            return False
    
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            self.pressed_keys.discard(key)
            
            if hasattr(key, 'char') and key.char and key.char.lower() == 'h':
                self.is_h_pressed = False
                print("⏹️  CLICKING STOPPED")
        except AttributeError:
            pass
        except Exception as e:
            print(f"❌ Key release error: {e}")
    
    def start(self):
        """Start the auto-clicker"""
        try:
            print("🎯 Starting auto-clicker...")
            self.clicking = True
            self.running = True
            
            click_thread = threading.Thread(target=self.click_loop, daemon=True)
            click_thread.start()
            
            print("⌨️  Keyboard listener starting...")
            
            with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            ) as listener:
                print("✓ Keyboard listener active")
                listener.join()
                
        except Exception as e:
            print(f"❌ Error in start(): {e}")
            self.stop()
    
    def stop(self):
        """Stop the auto-clicker"""
        print("🛑 Stopping auto-clicker...")
        self.running = False
        self.clicking = False
        self.is_h_pressed = False

def get_running_processes():
    """Get list of running processes with windows"""
    print("🔍 Scanning processes...")
    processes = []
    seen_names = set()
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                if name and name not in seen_names and len(name) > 0:
                    # Check if process has windows
                    try:
                        pid = proc.info['pid']
                        def enum_windows_callback(hwnd, results):
                            try:
                                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                                if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                                    window_title = win32gui.GetWindowText(hwnd)
                                    if window_title.strip():
                                        results.append((name, window_title))
                            except:
                                pass
                            return True
                        
                        windows = []
                        win32gui.EnumWindows(enum_windows_callback, windows)
                        
                        if windows:
                            processes.append((name, windows[0][1]))
                            seen_names.add(name)
                    except:
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        print(f"❌ Error scanning processes: {e}")
    
    return sorted(processes, key=lambda x: x[0].lower())

def select_process():
    """Interactive process selection"""
    try:
        processes = get_running_processes()
        
        if not processes:
            print("❌ No processes with windows found!")
            print("Make sure you have some applications open with visible windows.")
            input("Press Enter to exit...")
            return None
        
        print(f"\n📋 Found {len(processes)} processes:")
        print("━" * 60)
        
        for i, (name, title) in enumerate(processes, 1):
            title_preview = title[:40] + "..." if len(title) > 40 else title
            print(f"{i:2d}. {name:<20} | {title_preview}")
        
        print("━" * 60)
        
        while True:
            try:
                choice = input(f"\n🎯 Select process (1-{len(processes)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(processes):
                    selected_process = processes[index][0]
                    print(f"\n✅ Selected: {selected_process}")
                    return selected_process
                else:
                    print(f"❌ Please enter a number between 1 and {len(processes)}")
            
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return None
    except Exception as e:
        print(f"❌ Error in process selection: {e}")
        input("Press Enter to exit...")
        return None

def main():
    try:
        print("🎮 PROCESS AUTO-CLICKER")
        print("=" * 50)
        
        if not install_and_import_dependencies():
            return
        
        # Select target process
        target_process = select_process()
        if not target_process:
            print("No process selected. Exiting...")
            input("Press Enter to exit...")
            return
        
        try:
            clicker = ProcessAutoClicker(target_process)
            clicker.start()
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user...")
        except Exception as e:
            print(f"❌ Clicker error: {e}")
            print("This might be due to permissions or system compatibility.")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("\n" + "="*50)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
