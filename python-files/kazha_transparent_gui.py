import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import io
import base64
import webbrowser
import math
import threading
import time
import sys
import traceback

class KazhaLoginGUI:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("KAZHA Authentication")
            self.root.geometry("450x500")
            self.root.resizable(False, False)
            
            # Remove window decorations (borderless/frameless window)
            self.root.overrideredirect(True)
            
            # Make window almost transparent (0.85 = 85% opacity, 15% transparent)
            self.root.wm_attributes('-alpha', 0.85)
            
            # Set background color
            self.root.configure(bg='#1a1a1a')
            
            # Disable window closing with Alt+F4 or window controls except custom X
            self.root.protocol("WM_DELETE_WINDOW", self.do_nothing)
            
            # Modern color scheme
            self.colors = {
                'bg': '#0a0a0a',
                'card_bg': '#1a1a1a',
                'glass_bg': '#ffffff0d',
                'accent': '#00d4ff',
                'accent_hover': '#00b8e6',
                'text_primary': '#ffffff',
                'text_secondary': '#b0b0b0',
                'success': '#00ff88',
                'error': '#ff4757',
                'gradient_start': '#667eea',
                'gradient_end': '#764ba2'
            }
            
            # Center the window
            self.center_window()
            
            # Setup the modern GUI
            self.setup_modern_gui()
            
            # Correct key
            self.correct_key = "KAZHA-FREE"
            
            # Link to open after successful authentication
            self.target_url = "https://gofile.io/d/uiLfmJ"
            
            # Animation variables
            self.animation_frame = 0
            self.pulse_direction = 1
            self.start_animations()
            
        except Exception as e:
            pass
            
    def do_nothing(self):
        """Prevent window closing except through custom X button"""
        pass
            
    def center_window(self):
        """Center the window on screen"""
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
        except Exception as e:
            pass
    
    def setup_modern_gui(self):
        """Setup the modern GUI elements"""
        try:
            # Main container - this is the visible card
            main_container = tk.Frame(self.root, bg='#2a2a2a')
            main_container.place(x=0, y=0, width=450, height=500)
            
            # Make the entire main container draggable
            main_container.bind('<Button-1>', self.start_drag)
            main_container.bind('<B1-Motion>', self.drag_window)
            
            # Glass card effect with semi-transparent background
            glass_card = tk.Frame(main_container, bg='#1a1a1a', relief='flat', bd=0)
            glass_card.place(x=0, y=0, width=450, height=500)
            
            # Make glass card draggable too
            glass_card.bind('<Button-1>', self.start_drag)
            glass_card.bind('<B1-Motion>', self.drag_window)
            
            # Add subtle border
            border_frame = tk.Frame(glass_card, bg=self.colors['accent'], height=2)
            border_frame.place(x=0, y=0, relwidth=1)
            
            # Close button (top right corner of card)
            close_btn = tk.Button(
                glass_card,
                text="×",
                command=self.close_app,
                font=("Arial", 16, "bold"),
                bg='#1a1a1a',
                fg=self.colors['text_primary'],
                activebackground='#ff4757',
                activeforeground='#ffffff',
                relief='flat',
                bd=0,
                width=3,
                height=1,
                cursor='hand2'
            )
            close_btn.place(x=400, y=5)
            
            # Logo frame - make it draggable
            logo_frame = tk.Frame(glass_card, bg='#1a1a1a', height=120)
            logo_frame.place(x=0, y=20, relwidth=1)
            logo_frame.bind('<Button-1>', self.start_drag)
            logo_frame.bind('<B1-Motion>', self.drag_window)
            
            # Modern KAZHA logo
            logo_label = tk.Label(
                logo_frame,
                text="KAZHA",
                font=("Arial", 32, "bold"),
                fg=self.colors['accent'],
                bg='#1a1a1a'
            )
            logo_label.pack(pady=10)
            logo_label.bind('<Button-1>', self.start_drag)
            logo_label.bind('<B1-Motion>', self.drag_window)
            
            # Subtitle with modern font
            subtitle_label = tk.Label(
                logo_frame,
                text="SECURE AUTHENTICATION",
                font=("Arial", 11, "normal"),
                fg=self.colors['text_secondary'],
                bg='#1a1a1a'
            )
            subtitle_label.pack()
            subtitle_label.bind('<Button-1>', self.start_drag)
            subtitle_label.bind('<B1-Motion>', self.drag_window)
            
            # Input section
            input_frame = tk.Frame(glass_card, bg='#1a1a1a')
            input_frame.place(x=50, y=200, width=350, height=150)
            input_frame.bind('<Button-1>', self.start_drag)
            input_frame.bind('<B1-Motion>', self.drag_window)
            
            # Modern input label
            input_label = tk.Label(
                input_frame,
                text="Access Key",
                font=("Arial", 12, "normal"),
                fg=self.colors['text_primary'],
                bg='#1a1a1a'
            )
            input_label.pack(anchor='w', pady=(0, 10))
            input_label.bind('<Button-1>', self.start_drag)
            input_label.bind('<B1-Motion>', self.drag_window)
            
            # Modern input field
            self.key_var = tk.StringVar()
            input_container = tk.Frame(input_frame, bg='#2a2a2a', height=50)
            input_container.pack(fill='x', pady=(0, 20))
            input_container.pack_propagate(False)
            
            self.key_entry = tk.Entry(
                input_container,
                textvariable=self.key_var,
                font=("Arial", 14),
                bg='#2a2a2a',
                fg=self.colors['text_primary'],
                insertbackground=self.colors['accent'],
                relief='flat',
                bd=0,
                justify='left'
            )
            self.key_entry.place(x=15, y=12, width=320, height=26)
            self.key_entry.bind('<Return>', self.check_key)
            self.key_entry.bind('<FocusIn>', self.on_entry_focus)
            self.key_entry.bind('<FocusOut>', self.on_entry_unfocus)
            
            # Modern buttons
            button_frame = tk.Frame(input_frame, bg='#1a1a1a')
            button_frame.pack(fill='x', pady=10)
            button_frame.bind('<Button-1>', self.start_drag)
            button_frame.bind('<B1-Motion>', self.drag_window)
            
            # Authenticate button with modern style
            self.auth_btn = tk.Button(
                button_frame,
                text="AUTHENTICATE",
                command=self.check_key,
                font=("Arial", 12, "bold"),
                bg=self.colors['accent'],
                fg='#ffffff',
                activebackground=self.colors['accent_hover'],
                activeforeground='#ffffff',
                relief='flat',
                bd=0,
                padx=30,
                pady=15,
                cursor='hand2'
            )
            self.auth_btn.pack(side='left', fill='x', expand=True)
            
            # Status area
            self.status_frame = tk.Frame(glass_card, bg='#1a1a1a', height=80)
            self.status_frame.place(x=50, y=380, width=350)
            self.status_frame.bind('<Button-1>', self.start_drag)
            self.status_frame.bind('<B1-Motion>', self.drag_window)
            
            self.status_label = tk.Label(
                self.status_frame,
                text="Ready for authentication...",
                font=("Arial", 11),
                fg=self.colors['text_secondary'],
                bg='#1a1a1a'
            )
            self.status_label.pack(pady=20)
            self.status_label.bind('<Button-1>', self.start_drag)
            self.status_label.bind('<B1-Motion>', self.drag_window)
            
            # Progress bar (hidden initially)
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(
                self.status_frame,
                variable=self.progress_var,
                maximum=100,
                length=300,
                mode='determinate'
            )
            
            # Style the progress bar
            try:
                style = ttk.Style()
                style.theme_use('clam')
                style.configure("TProgressbar", 
                               background=self.colors['accent'],
                               darkcolor=self.colors['accent'],
                               lightcolor=self.colors['accent'],
                               bordercolor='#2a2a2a',
                               troughcolor='#2a2a2a')
            except:
                pass
            
            # Set focus to entry field
            self.key_entry.focus_set()
            
        except Exception as e:
            pass
        
    def start_drag(self, event):
        """Start window dragging"""
        try:
            self.drag_start_x = event.x_root - self.root.winfo_x()
            self.drag_start_y = event.y_root - self.root.winfo_y()
        except Exception as e:
            pass
        
    def drag_window(self, event):
        """Drag the window"""
        try:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
        except Exception as e:
            pass
        
    def close_app(self):
        """Close the application - only way to close"""
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            pass
        
    def on_entry_focus(self, event):
        """Handle entry focus - add glow effect"""
        try:
            self.key_entry.config(bg='#333333')
        except Exception as e:
            pass
        
    def on_entry_unfocus(self, event):
        """Handle entry unfocus - remove glow effect"""
        try:
            self.key_entry.config(bg='#2a2a2a')
        except Exception as e:
            pass
        
    def start_animations(self):
        """Start subtle animations"""
        try:
            self.animate_pulse()
        except Exception as e:
            pass
        
    def animate_pulse(self):
        """Animate button pulse effect"""
        try:
            self.animation_frame += self.pulse_direction
            
            if self.animation_frame >= 20:
                self.pulse_direction = -1
            elif self.animation_frame <= 0:
                self.pulse_direction = 1
                
            self.root.after(100, self.animate_pulse)
        except Exception as e:
            pass
        
    def check_key(self, event=None):
        """Check if the entered key is correct with modern feedback"""
        try:
            entered_key = self.key_var.get().strip()
            
            if not entered_key:
                self.show_status("Please enter an access key", "error")
                return
                
            # Show loading state
            self.auth_btn.config(text="AUTHENTICATING...", state='disabled')
            self.show_progress()
            
            # Simulate authentication delay for better UX
            self.root.after(1500, lambda: self.complete_authentication(entered_key))
            
        except Exception as e:
            pass
        
    def show_progress(self):
        """Show progress bar animation"""
        try:
            self.progress_bar.pack(pady=10)
            self.animate_progress()
        except Exception as e:
            pass
        
    def animate_progress(self):
        """Animate progress bar"""
        try:
            current = self.progress_var.get()
            if current < 100:
                self.progress_var.set(current + 2)
                self.root.after(30, self.animate_progress)
        except Exception as e:
            pass
            
    def complete_authentication(self, entered_key):
        """Complete the authentication process"""
        try:
            self.progress_bar.pack_forget()
            self.progress_var.set(0)
            
            if entered_key == self.correct_key:
                self.show_status("✓ Authentication Successful", "success")
                self.auth_btn.config(text="ACCESS GRANTED", bg=self.colors['success'])
                self.root.after(1000, self.show_success)
            else:
                self.show_status("✗ Access Denied - Invalid Key", "error")
                self.auth_btn.config(text="AUTHENTICATE", state='normal', bg=self.colors['accent'])
                self.key_entry.delete(0, tk.END)
                self.modern_shake()
                
        except Exception as e:
            pass
            
    def show_status(self, message, status_type):
        """Show status message with modern styling"""
        try:
            if status_type == "success":
                color = self.colors['success']
            elif status_type == "error":
                color = self.colors['error']
            else:
                color = self.colors['text_secondary']
                
            self.status_label.config(text=message, fg=color)
            
        except Exception as e:
            pass
        
    def modern_shake(self):
        """Modern shake animation"""
        try:
            original_x = self.root.winfo_x()
            original_y = self.root.winfo_y()
            
            def shake_step(step):
                try:
                    if step < 8:
                        offset = 10 * math.sin(step * math.pi / 2)
                        self.root.geometry(f"+{int(original_x + offset)}+{original_y}")
                        self.root.after(50, lambda: shake_step(step + 1))
                    else:
                        self.root.geometry(f"+{original_x}+{original_y}")
                except Exception as e:
                    pass
                    
            shake_step(0)
            
        except Exception as e:
            pass
        
    def show_success(self):
        """Open link directly without popup"""
        try:
            # Try to open the link directly
            try:
                webbrowser.open(self.target_url)
            except Exception as e:
                pass
                
            # Close the application after a delay
            self.root.after(2000, self.close_app)
            
        except Exception as e:
            pass
        
    def run(self):
        """Run the GUI application"""
        try:
            self.root.mainloop()
        except Exception as e:
            pass

if __name__ == "__main__":
    try:
        app = KazhaLoginGUI()
        app.run()
    except Exception as e:
        pass