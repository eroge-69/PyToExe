import tkinter as tk
from tkinter import ttk, messagebox
import pytchat
import pygetwindow as gw
import threading
import time
import re
import win32gui
import pyautogui

class YoutubeChatKeystrokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Chat Relay")
        self.root.geometry("550x600")
        
        self.chat_thread = None
        self.stop_flag = False
        self.chat = None
        
        self.setup_ui()
        self.refresh_programs()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # YouTube URL input
        ttk.Label(main_frame, text="YouTube URL/ID:").pack(anchor=tk.W, pady=(0, 5))
        self.youtube_input = ttk.Entry(main_frame, width=60)
        self.youtube_input.pack(fill=tk.X, pady=(0, 15))
        
        # Program selection
        ttk.Label(main_frame, text="Target Program:").pack(anchor=tk.W, pady=(0, 5))
        program_frame = ttk.Frame(main_frame)
        program_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.program_var = tk.StringVar()
        self.program_dropdown = ttk.Combobox(program_frame, textvariable=self.program_var, state="readonly")
        self.program_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.refresh_btn = ttk.Button(program_frame, text="Refresh", command=self.refresh_programs)
        self.refresh_btn.pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=15)
        
        self.start_btn = ttk.Button(control_frame, text="Start", command=self.start_relay, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_relay, width=15, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings
        ttk.Label(main_frame, text="Settings:").pack(anchor=tk.W, pady=(15, 5))
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Left column
        left_frame = ttk.Frame(settings_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Message Delay (ms):").pack(anchor=tk.W)
        self.delay_var = tk.StringVar(value="500")
        ttk.Entry(left_frame, textvariable=self.delay_var, width=15).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(left_frame, text="Process Delay (ms):").pack(anchor=tk.W)
        self.process_delay_var = tk.StringVar(value="100")
        ttk.Entry(left_frame, textvariable=self.process_delay_var, width=15).pack(anchor=tk.W)
        
        # Right column
        right_frame = ttk.Frame(settings_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(right_frame, text="Max Characters:").pack(anchor=tk.W)
        self.max_chars_var = tk.StringVar(value="100")
        ttk.Entry(right_frame, textvariable=self.max_chars_var, width=15).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(right_frame, text="Enter Delay (ms):").pack(anchor=tk.W)
        self.enter_delay_var = tk.StringVar(value="50")
        ttk.Entry(right_frame, textvariable=self.enter_delay_var, width=15).pack(anchor=tk.W)
        
        # Status log
        ttk.Label(main_frame, text="Status:").pack(anchor=tk.W, pady=(15, 5))
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=10, wrap=tk.WORD, state="disabled")
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        
    def refresh_programs(self):
        try:
            windows = gw.getAllWindows()
            window_titles = [w.title for w in windows if w.title and w.visible]
            window_titles = list(set(window_titles))
            window_titles.sort()
            
            self.program_dropdown['values'] = window_titles
            
            if window_titles:
                self.program_dropdown.current(0)
                
            self.add_status("Program list refreshed")
        except Exception as e:
            self.add_status(f"Error refreshing programs: {e}")
    
    def extract_video_id(self, url_or_id):
        if "youtube.com/watch?v=" in url_or_id:
            match = re.search(r'v=([a-zA-Z0-9_-]+)', url_or_id)
            if match:
                return match.group(1)
        elif "youtu.be/" in url_or_id:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url_or_id)
            if match:
                return match.group(1)
        return url_or_id
    
    def add_status(self, message):
        self.status_text.config(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
    
    def send_message_to_window(self, window_title, message):
        try:
            # Check character limit
            max_chars = int(self.max_chars_var.get())
            if len(message) > max_chars:
                self.add_status(f"Message too long ({len(message)} chars > {max_chars}), skipping")
                return True  # Return True to continue processing other messages
            
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                self.add_status(f"Window '{window_title}' not found")
                return False
            
            window = windows[0]
            hwnd = window._hWnd
            
            # Get delay settings
            process_delay = int(self.process_delay_var.get()) / 1000.0  # Convert ms to seconds
            enter_delay = int(self.enter_delay_var.get()) / 1000.0  # Convert ms to seconds
            
            # Use PyAutoGUI - the only method that works
            try:
                # Delay before processing
                time.sleep(process_delay)
                
                # Focus the window
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                
                # Type the message
                pyautogui.typewrite(message, interval=0.01)
                
                # Delay before Enter
                time.sleep(enter_delay)
                
                # Send Enter key
                pyautogui.press('enter')
                
                return True
            except Exception as e:
                self.add_status(f"Failed to send message: {e}")
                return False
                    
        except Exception as e:
            self.add_status(f"Error sending message: {e}")
            return False
    
    def relay_chat(self, video_id, window_title):
        try:
            self.add_status(f"Connecting to YouTube chat for video: {video_id}")
            
            delay_ms = int(self.delay_var.get())
            delay_sec = delay_ms / 1000.0
            
            # Create chat object with interruptable_get for threading compatibility
            self.chat = pytchat.create(video_id=video_id, interruptable=False)
            
            if not self.chat:
                self.add_status("Failed to connect to YouTube chat")
                return
            
            self.add_status("Connected! Relaying messages...")
            
            while self.chat.is_alive() and not self.stop_flag:
                try:
                    # Use get() with timeout to make it interruptable
                    chat_data = self.chat.get()
                    if chat_data and chat_data.items:
                        for c in chat_data.items:
                            if self.stop_flag:
                                break
                            
                            message = c.message
                            author = c.author.name
                            
                            self.add_status(f"{author}: {message}")
                            
                            if self.send_message_to_window(window_title, message):
                                pass
                            else:
                                self.add_status("Failed to send message, stopping...")
                                self.stop_flag = True
                                break
                            
                            time.sleep(delay_sec)
                    else:
                        # Small sleep when no messages to prevent busy waiting
                        time.sleep(0.1)
                except Exception as e:
                    if not self.stop_flag:
                        self.add_status(f"Error in chat loop: {e}")
                    break
            
        except Exception as e:
            self.add_status(f"Error connecting to chat: {e}")
        finally:
            if self.chat:
                try:
                    self.chat.terminate()
                except:
                    pass
                self.chat = None
            self.add_status("Chat relay stopped")
            self.root.after(0, self.reset_buttons)
    
    def start_relay(self):
        youtube_input = self.youtube_input.get().strip()
        selected_program = self.program_var.get()
        
        if not youtube_input:
            messagebox.showerror("Error", "Please enter a YouTube URL or video ID")
            return
        
        if not selected_program:
            messagebox.showerror("Error", "Please select a target program")
            return
        
        video_id = self.extract_video_id(youtube_input)
        self.add_status(f"Starting relay for video ID: {video_id}")
        self.add_status(f"Target program: {selected_program}")
        
        self.stop_flag = False
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.youtube_input.config(state="disabled")
        self.program_dropdown.config(state="disabled")
        self.refresh_btn.config(state="disabled")
        
        self.chat_thread = threading.Thread(target=self.relay_chat, args=(video_id, selected_program), daemon=True)
        self.chat_thread.start()
    
    def stop_relay(self):
        self.add_status("Stopping chat relay...")
        self.stop_flag = True
        
        if self.chat:
            try:
                self.chat.terminate()
            except:
                pass
        
        self.reset_buttons()
    
    def reset_buttons(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.youtube_input.config(state="normal")
        self.program_dropdown.config(state="readonly")
        self.refresh_btn.config(state="normal")

def main():
    root = tk.Tk()
    app = YoutubeChatKeystrokeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()