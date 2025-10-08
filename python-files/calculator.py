import tkinter as tk
from tkinter import font
import math

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, fg_color, active_bg, canvas_bg):
        tk.Canvas.__init__(self, parent, bg=canvas_bg, highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.active_bg = active_bg
        self.text = text
        
        self.bind("<Configure>", self.draw_button)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def draw_button(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        if w <= 1 or h <= 1:
            return
        
        radius = 15
        
        # Draw rounded rectangle with semi-transparent effect
        self.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc(w-radius*2, 0, w, radius*2, start=0, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc(0, h-radius*2, radius*2, h, start=180, extent=90, fill=self.bg_color, outline=self.bg_color)
        self.create_arc(w-radius*2, h-radius*2, w, h, start=270, extent=90, fill=self.bg_color, outline=self.bg_color)
        
        self.create_rectangle(radius, 0, w-radius, h, fill=self.bg_color, outline=self.bg_color)
        self.create_rectangle(0, radius, w, h-radius, fill=self.bg_color, outline=self.bg_color)
        
        # Draw text with Comic Sans
        self.create_text(w/2, h/2, text=self.text, fill=self.fg_color, font=("Comic Sans MS", 14, "bold"))
    
    def on_click(self, event):
        self.command()
    
    def on_enter(self, event):
        original_color = self.bg_color
        self.bg_color = self.active_bg
        self.draw_button()
    
    def on_leave(self, event):
        self.bg_color = self.bg_color if hasattr(self, 'original_color') else self.bg_color
        # Reset to original color
        if self.text == '=':
            self.bg_color = "#4CAF50"
        elif self.text in ['C', '←']:
            self.bg_color = "#f44336"
        elif self.text in ['/', '*', '-', '+', '%', '^']:
            self.bg_color = "#ff9800"
        elif self.text in ['sin', 'cos', 'tan', '√', 'x²', 'log', 'ln', '|x|', 'n!', 'π', 'e', 'ans', '(', ')']:
            self.bg_color = "#9C27B0"
        else:
            self.bg_color = "#606060"
        self.draw_button()

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator - Basic Mode")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        self.expression = ""
        self.input_text = tk.StringVar()
        self.advanced_mode = False
        self.dark_mode = True
        self.history = []
        self.history_visible = False
        
        # Color schemes
        self.colors = {
            'dark': {
                'bg': '#1e1e1e',
                'display_bg': '#3d3d3d',
                'display_frame': '#2d2d2d',
                'text': '#ffffff',
                'canvas_bg': '#1e1e1e'
            },
            'light': {
                'bg': '#f0f0f0',
                'display_bg': '#ffffff',
                'display_frame': '#e0e0e0',
                'text': '#000000',
                'canvas_bg': '#f0f0f0'
            }
        }
        
        # Set window transparency and background
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg=self.get_color('bg'))
        
        # Create top bar with theme toggle
        top_bar = tk.Frame(self.root, bg=self.get_color('bg'))
        top_bar.pack(fill="x", padx=10, pady=(10, 0))
        
        # Exit button (small, top left)
        self.exit_button = tk.Button(
            top_bar,
            text="✕",
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            bd=0,
            width=3,
            command=self.root.quit
        )
        self.exit_button.pack(side="left")
        
        # Welcome text (center)
        self.welcome_label = tk.Label(
            top_bar,
            text="👋 Welcome to the Calculator!",
            font=("Comic Sans MS", 12, "bold"),
            bg=self.get_color('bg'),
            fg=self.get_color('text')
        )
        self.welcome_label.pack(side="left", expand=True)
        
        # Theme toggle button (small, top right)
        self.theme_button = tk.Button(
            top_bar,
            text="🌙",
            font=("Segoe UI Emoji", 16),
            bg="#404040",
            fg="white",
            activebackground="#505050",
            bd=0,
            width=3,
            command=self.toggle_theme
        )
        self.theme_button.pack(side="right")
        
        self.expression = ""
        self.input_text = tk.StringVar()
        self.advanced_mode = False
        self.dark_mode = True
        
        # Color schemes
        self.colors = {
            'dark': {
                'bg': '#1e1e1e',
                'display_bg': '#3d3d3d',
                'display_frame': '#2d2d2d',
                'text': '#ffffff',
                'canvas_bg': '#1e1e1e'
            },
            'light': {
                'bg': '#f0f0f0',
                'display_bg': '#ffffff',
                'display_frame': '#e0e0e0',
                'text': '#000000',
                'canvas_bg': '#f0f0f0'
            }
        }
        
        # Create display frame with blur effect
        display_frame = tk.Frame(self.root, bg=self.get_color('display_frame'))
        display_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create display
        self.display = tk.Entry(
            display_frame,
            font=("Comic Sans MS", 24, "bold"),
            textvariable=self.input_text,
            bd=0,
            insertwidth=4,
            width=14,
            borderwidth=4,
            justify="right",
            bg=self.get_color('display_bg'),
            fg=self.get_color('text')
        )
        self.display.pack(ipady=20)
        
        # Create mode toggle button
        mode_frame = tk.Frame(self.root, bg=self.get_color('bg'))
        mode_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.mode_button = tk.Button(
            mode_frame,
            text="Advanced Mode",
            font=("Comic Sans MS", 12, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            bd=0,
            command=self.toggle_mode
        )
        self.mode_button.pack(fill="x")
        
        # Create buttons frame
        self.buttons_frame = tk.Frame(self.root, bg=self.get_color('bg'))
        self.buttons_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        # Show basic mode by default
        self.show_basic_mode()
        
        # Bind keyboard events
        self.root.bind('<Key>', self.on_key_press)
    
    def get_color(self, key):
        mode = 'dark' if self.dark_mode else 'light'
        return self.colors[mode][key]
    
    def update_theme(self):
        self.root.configure(bg=self.get_color('bg'))
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        
        # Update theme button
        self.theme_button.config(
            text="🌙" if self.dark_mode else "☀",
            bg="#404040" if self.dark_mode else "#d0d0d0",
            fg="white" if self.dark_mode else "black",
            activebackground="#505050" if self.dark_mode else "#c0c0c0"
        )
        
        # Update window title with theme
        mode = "Advanced Mode" if self.advanced_mode else "Basic Mode"
        theme = "Dark" if self.dark_mode else "Light"
        self.root.title(f"Calculator - {mode} - {theme}")
        
        # Update welcome label
        self.welcome_label.config(
            bg=self.get_color('bg'),
            fg=self.get_color('text')
        )
        
        # Update history text widget if visible
        if hasattr(self, 'history_text') and self.history_visible:
            self.history_text.config(
                bg=self.get_color('display_bg'),
                fg=self.get_color('text')
            )
            if hasattr(self, 'history_window'):
                self.history_window.configure(bg=self.get_color('bg'))
        
        # Update all colors
        self.root.configure(bg=self.get_color('bg'))
        self.display.config(bg=self.get_color('display_bg'), fg=self.get_color('text'))
        
        # Update parent frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=self.get_color('bg'))
        
        # Rebuild buttons with new theme
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        if self.advanced_mode:
            self.show_advanced_mode()
        else:
            self.show_basic_mode()
    
    def toggle_mode(self):
        self.advanced_mode = not self.advanced_mode
        
        # Clear existing buttons
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        # Reset grid configuration first
        for i in range(10):
            self.buttons_frame.grid_rowconfigure(i, weight=0)
        for j in range(10):
            self.buttons_frame.grid_columnconfigure(j, weight=0)
        
        if self.advanced_mode:
            self.mode_button.config(text="Basic Mode")
            self.root.geometry("600x600")
            self.root.title("Calculator - Advanced Mode")
            self.show_advanced_mode()
        else:
            self.mode_button.config(text="Advanced Mode")
            self.root.geometry("400x600")
            self.root.title("Calculator - Basic Mode")
            self.show_basic_mode()
    
    def show_basic_mode(self):
        # Button layout
        buttons = [
            ['C', '←', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', '📜']
        ]
        
        # Reset grid configuration
        for i in range(10):
            self.buttons_frame.grid_rowconfigure(i, weight=0)
        for j in range(10):
            self.buttons_frame.grid_columnconfigure(j, weight=0)
        
        self.create_buttons(buttons, 4)
    
    def show_advanced_mode(self):
        # Advanced button layout
        buttons = [
            ['C', '←', '(', ')', '^', '%', '/'],
            ['sin', 'cos', 'tan', '7', '8', '9', '*'],
            ['√', 'x²', 'π', '4', '5', '6', '-'],
            ['log', 'ln', 'e', '1', '2', '3', '+'],
            ['|x|', 'n!', 'ans', '0', '.', '=', '📜']
        ]
        
        # Reset grid configuration
        for i in range(10):
            self.buttons_frame.grid_rowconfigure(i, weight=0)
        for j in range(10):
            self.buttons_frame.grid_columnconfigure(j, weight=0)
        
        self.create_buttons(buttons, 7)
    
    def create_buttons(self, buttons, columns):
        for i, row in enumerate(buttons):
            for j, button in enumerate(row):
                if button == '':
                    continue
                
                # Determine colors with semi-transparency effect
                if button == '=':
                    bg = "#4CAF50"
                    active = "#45a049"
                elif button in ['C', '←']:
                    bg = "#f44336"
                    active = "#da190b"
                elif button in ['/', '*', '-', '+', '%', '^']:
                    bg = "#ff9800"
                    active = "#e68900"
                elif button in ['sin', 'cos', 'tan', '√', 'x²', 'log', 'ln', '|x|', 'n!', 'π', 'e', 'ans', '(', ')']:
                    bg = "#9C27B0"
                    active = "#7B1FA2"
                elif button == '📜':
                    bg = "#2196F3"
                    active = "#1976D2"
                else:
                    bg = "#606060"
                    active = "#505050"
                
                btn = RoundedButton(
                    self.buttons_frame,
                    text=button,
                    command=lambda x=button: self.on_button_click(x),
                    bg_color=bg,
                    fg_color="white",
                    active_bg=active,
                    canvas_bg=self.get_color('canvas_bg')
                )
                
                btn.grid(row=i, column=j, sticky="nsew", padx=4, pady=4)
        
        # Configure grid weights
        for i in range(len(buttons)):
            self.buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(columns):
            self.buttons_frame.grid_columnconfigure(j, weight=1)
    
    def on_button_click(self, button):
        if button == 'C':
            self.expression = ""
            self.input_text.set("")
        elif button == '←':
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
        elif button == '=':
            try:
                # Replace special symbols for evaluation
                expr = self.expression.replace('^', '**')
                expr = expr.replace('π', str(math.pi))
                expr = expr.replace('e', str(math.e))
                
                result = str(eval(expr))
                
                # Add to history
                self.add_to_history(f"{self.expression} = {result}")
                
                self.input_text.set(result)
                self.last_answer = result
                self.expression = result
            except:
                self.input_text.set("Error")
                self.expression = ""
        elif button == 'π':
            self.expression += 'π'
            self.input_text.set(self.expression)
        elif button == 'e':
            self.expression += 'e'
            self.input_text.set(self.expression)
        elif button == '^':
            self.expression += '^'
            self.input_text.set(self.expression)
        elif button == '√':
            self.expression += 'math.sqrt('
            self.input_text.set(self.expression)
        elif button == 'x²':
            self.expression += '**2'
            self.input_text.set(self.expression)
        elif button == 'sin':
            self.expression += 'math.sin('
            self.input_text.set(self.expression)
        elif button == 'cos':
            self.expression += 'math.cos('
            self.input_text.set(self.expression)
        elif button == 'tan':
            self.expression += 'math.tan('
            self.input_text.set(self.expression)
        elif button == 'log':
            self.expression += 'math.log10('
            self.input_text.set(self.expression)
        elif button == 'ln':
            self.expression += 'math.log('
            self.input_text.set(self.expression)
        elif button == '|x|':
            self.expression += 'abs('
            self.input_text.set(self.expression)
        elif button == 'n!':
            self.expression += 'math.factorial('
            self.input_text.set(self.expression)
        elif button == 'ans':
            if hasattr(self, 'last_answer'):
                self.expression += self.last_answer
                self.input_text.set(self.expression)
        elif button == '📜':
            self.toggle_history()
        else:
            self.expression += str(button)
            self.input_text.set(self.expression)
    
    def on_key_press(self, event):
        key = event.char
        
        # Handle 'x' or 'X' as multiplication
        if key.lower() == 'x':
            self.expression += '*'
            self.input_text.set(self.expression)
        
        # Handle numbers and operators
        elif key in '0123456789+-*/.%()':
            self.expression += key
            self.input_text.set(self.expression)
        
        # Handle Enter/Return for equals
        elif event.keysym == 'Return':
            self.on_button_click('=')
        
        # Handle Backspace
        elif event.keysym == 'BackSpace':
            self.on_button_click('←')
        
        # Handle Escape or Delete for clear
        elif event.keysym in ['Escape', 'Delete']:
            self.on_button_click('C')
        
        # Handle ^ for power
        elif key == '^':
            self.expression += '^'
            self.input_text.set(self.expression)
    
    def add_to_history(self, calculation):
        self.history.append(calculation)
        if hasattr(self, 'history_text'):
            self.history_text.config(state="normal")
            self.history_text.insert("1.0", calculation + "\n")
            self.history_text.config(state="disabled")
            self.history_text.see("1.0")
    
    def clear_history(self):
        self.history = []
        if hasattr(self, 'history_text'):
            self.history_text.config(state="normal")
            self.history_text.delete("1.0", "end")
            self.history_text.config(state="disabled")
    
    def toggle_history(self):
        self.history_visible = not self.history_visible
        
        if self.history_visible:
            # Create history window
            self.history_window = tk.Toplevel(self.root)
            self.history_window.title("Calculator - History")
            self.history_window.geometry("300x400")
            self.history_window.configure(bg=self.get_color('bg'))
            self.history_window.attributes('-alpha', 0.95)
            
            # History label
            history_label = tk.Label(
                self.history_window,
                text="📜 History",
                font=("Comic Sans MS", 14, "bold"),
                bg=self.get_color('bg'),
                fg=self.get_color('text')
            )
            history_label.pack(pady=10)
            
            # History text widget with scrollbar
            history_container = tk.Frame(self.history_window, bg=self.get_color('bg'))
            history_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            scrollbar = tk.Scrollbar(history_container)
            scrollbar.pack(side="right", fill="y")
            
            self.history_text = tk.Text(
                history_container,
                font=("Comic Sans MS", 11),
                bg=self.get_color('display_bg'),
                fg=self.get_color('text'),
                wrap="word",
                yscrollcommand=scrollbar.set,
                state="disabled"
            )
            self.history_text.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=self.history_text.yview)
            
            # Load existing history
            self.history_text.config(state="normal")
            for calc in reversed(self.history):
                self.history_text.insert("end", calc + "\n")
            self.history_text.config(state="disabled")
            
            # Clear history button
            clear_history_btn = tk.Button(
                self.history_window,
                text="Clear History",
                font=("Comic Sans MS", 10, "bold"),
                bg="#ff5722",
                fg="white",
                activebackground="#e64a19",
                bd=0,
                command=self.clear_history
            )
            clear_history_btn.pack(pady=(0, 10))
            
            # Handle window close
            self.history_window.protocol("WM_DELETE_WINDOW", self.toggle_history)
        else:
            # Close history window
            if hasattr(self, 'history_window'):
                self.history_window.destroy()
                delattr(self, 'history_text')

if __name__ == "__main__":
    root = tk.Tk()
    
    # Hide console window on Windows
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    calculator = Calculator(root)
    root.mainloop()
