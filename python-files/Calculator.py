import tkinter as tk
from tkinter import font as tkfont, messagebox
import math

class iPhoneCalculator:
    def __init__(self, master):
        self.master = master
        master.title("iPhone Calculator")
        master.configure(bg='#000000')
        master.resizable(True, True)  # Allow resizing
        master.minsize(350, 600)  # Set minimum size
        
        # Theme settings
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg": '#000000',
                "display_bg": '#000000',
                "text": '#ffffff',
                "orange": '#ff9500',
                "light_gray": '#a5a5a5',
                "dark_gray": '#333333'
            },
            "light": {
                "bg": '#ffffff',
                "display_bg": '#ffffff',
                "text": '#000000',
                "orange": '#ff9500',
                "light_gray": '#d4d4d2',
                "dark_gray": '#f0f0f0'
            },
            "system": {
                "bg": '#000000',
                "display_bg": '#000000',
                "text": '#ffffff',
                "orange": '#ff9500',
                "light_gray": '#a5a5a5',
                "dark_gray": '#333333'
            }
        }
        
        # Initialize colors
        self.update_colors()
        
        # Custom fonts
        self.display_font = tkfont.Font(family='Arial', size=80, weight='normal')
        self.history_font = tkfont.Font(family='Arial', size=24)
        self.button_font = tkfont.Font(family='Arial', size=32, weight='normal')
        
        # Create main container
        self.main_frame = tk.Frame(master, bg=self.bg_color)
        self.main_frame.pack(expand=True, fill='both')
        
        # Create menu bar
        self.create_menu()
        
        # Display section
        self.display_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.display_frame.pack(fill='x', padx=20, pady=(40, 20), expand=True)
        
        # History display
        self.history_var = tk.StringVar()
        self.history_label = tk.Label(
            self.display_frame,
            textvariable=self.history_var,
            font=self.history_font,
            bg=self.bg_color,
            fg=self.text_color,
            anchor='e',
            height=1
        )
        self.history_label.pack(fill='x', expand=True)
        
        # Main display
        self.result_var = tk.StringVar()
        self.result_var.set('0')
        self.display_label = tk.Label(
            self.display_frame,
            textvariable=self.result_var,
            font=self.display_font,
            bg=self.bg_color,
            fg=self.text_color,
            anchor='e',
            height=1
        )
        self.display_label.pack(fill='x', expand=True)
        
        # Button grid
        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.button_frame.pack(expand=True, fill='both', padx=20, pady=(0, 20))
        
        # Configure grid weights
        for i in range(5):
            self.button_frame.grid_rowconfigure(i, weight=1, uniform='row')
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1, uniform='col')
        
        # Button definitions (iPhone layout)
        buttons = [
            ('AC', 0, 0, self.light_gray, 'function'),
            ('±', 0, 1, self.light_gray, 'function'),
            ('%', 0, 2, self.light_gray, 'function'),
            ('÷', 0, 3, self.orange_color, 'operator'),
            ('7', 1, 0, self.dark_gray, 'number'),
            ('8', 1, 1, self.dark_gray, 'number'),
            ('9', 1, 2, self.dark_gray, 'number'),
            ('×', 1, 3, self.orange_color, 'operator'),
            ('4', 2, 0, self.dark_gray, 'number'),
            ('5', 2, 1, self.dark_gray, 'number'),
            ('6', 2, 2, self.dark_gray, 'number'),
            ('−', 2, 3, self.orange_color, 'operator'),
            ('1', 3, 0, self.dark_gray, 'number'),
            ('2', 3, 1, self.dark_gray, 'number'),
            ('3', 3, 2, self.dark_gray, 'number'),
            ('+', 3, 3, self.orange_color, 'operator'),
            ('0', 4, 0, self.dark_gray, 'number', 2),  # Span 2 columns
            ('.', 4, 2, self.dark_gray, 'number'),
            ('=', 4, 3, self.orange_color, 'equal'),
        ]
        
        # Create buttons
        self.buttons = {}
        for button_info in buttons:
            if len(button_info) == 5:
                text, row, col, bg, btn_type = button_info
                colspan = 1
            else:
                text, row, col, bg, btn_type, colspan = button_info
            
            btn = tk.Button(
                self.button_frame,
                text=text,
                font=self.button_font,
                bg=bg,
                fg=self.text_color,
                activebackground=self.lighten_color(bg),
                activeforeground=self.text_color,
                bd=0,
                relief='flat',
                command=lambda t=text: self.on_button_click(t)
            )
            btn.grid(row=row, column=col, columnspan=colspan, padx=3, pady=3, sticky='nsew')
            
            # Store button reference for theme updates
            self.buttons[text] = btn
        
        # Initialize variables
        self.current_expression = ""
        self.last_result = "0"
        self.new_number = True
        self.clear_next = False
        self.calculation_history = []
        
        # Bind keyboard events
        self.bind_keyboard_events()
        
    def bind_keyboard_events(self):
        """Bind keyboard events for number and operator input"""
        self.master.bind('<Key>', self.on_key_press)
        self.master.focus_set()
        
    def on_key_press(self, event):
        """Handle keyboard input"""
        key = event.char
        if key in '0123456789.':
            self.add_digit(key)
        elif key in '+-*/':
            # Map keyboard operators to calculator operators
            operator_map = {'+': '+', '-': '−', '*': '×', '/': '÷'}
            self.add_operator(operator_map[key])
        elif event.keysym == 'Return' or event.keysym == 'equal':
            self.calculate_result()
        elif event.keysym == 'Escape':
            self.clear_all()
        elif event.keysym == 'BackSpace':
            self.backspace()
        
    def create_menu(self):
        """Create the menu bar with settings"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Settings menu with icon (using text symbol as icon)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️", menu=settings_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Dark", command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label="Light", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="System Default", command=lambda: self.change_theme("system"))
        
        # History menu
        settings_menu.add_separator()
        settings_menu.add_command(label="History", command=self.show_history)
        
        # About menu
        settings_menu.add_separator()
        settings_menu.add_command(label="About", command=self.show_about)
        
    def update_colors(self):
        """Update colors based on current theme"""
        theme = self.themes[self.current_theme]
        self.bg_color = theme["bg"]
        self.display_bg = theme["display_bg"]
        self.text_color = theme["text"]
        self.orange_color = theme["orange"]
        self.light_gray = theme["light_gray"]
        self.dark_gray = theme["dark_gray"]
        self.operator_color = theme["orange"]
        
    def change_theme(self, theme_name):
        """Change the calculator theme"""
        self.current_theme = theme_name
        self.update_colors()
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        # Update main frame
        self.main_frame.config(bg=self.bg_color)
        self.master.config(bg=self.bg_color)
        
        # Update display frame
        self.display_frame.config(bg=self.bg_color)
        
        # Update labels
        self.history_label.config(bg=self.bg_color, fg=self.text_color)
        self.display_label.config(bg=self.bg_color, fg=self.text_color)
        
        # Update button frame
        self.button_frame.config(bg=self.bg_color)
        
        # Update buttons
        button_colors = {
            'AC': self.light_gray, '±': self.light_gray, '%': self.light_gray,
            '÷': self.orange_color, '×': self.orange_color, '−': self.orange_color,
            '+': self.orange_color, '=': self.orange_color,
            '7': self.dark_gray, '8': self.dark_gray, '9': self.dark_gray,
            '4': self.dark_gray, '5': self.dark_gray, '6': self.dark_gray,
            '1': self.dark_gray, '2': self.dark_gray, '3': self.dark_gray,
            '0': self.dark_gray, '.': self.dark_gray
        }
        
        for text, btn in self.buttons.items():
            if text in button_colors:
                btn.config(bg=button_colors[text], fg=self.text_color)
                # Re-bind hover events with correct colors
                btn.bind("<Enter>", lambda e, b=btn, c=button_colors[text]: b.config(bg=self.lighten_color(c)))
                btn.bind("<Leave>", lambda e, b=btn, c=button_colors[text]: b.config(bg=c))
    
    def backspace(self):
        """Handle backspace functionality"""
        current = self.result_var.get()
        if current != 'Error' and len(current) > 1:
            self.result_var.set(current[:-1])
        elif len(current) == 1:
            self.result_var.set("0")
            self.new_number = True
    
    def show_about(self):
        """Show about dialog"""
        about_text = """iPhone Calculator Clone
Version: 1.0.0

A Python Tkinter implementation of the iPhone calculator with:
• Authentic iPhone design and colors
• Multiple theme support (Dark, Light, System)
• Responsive layout
• Standard calculator functionality

Created with ❤️ using Python and Tkinter"""
        
        messagebox.showinfo("About", about_text)
        
    def lighten_color(self, color):
        """Lighten a color for hover effects"""
        if color == self.dark_gray:
            return '#4a4a4a' if self.current_theme == "dark" else '#e0e0e0'
        elif color == self.light_gray:
            return '#b5b5b5' if self.current_theme == "dark" else '#c4c4c4'
        elif color == self.orange_color:
            return '#ffaa33'
        else:
            return color
    
    def on_button_click(self, char):
        if char == '=':
            self.calculate_result()
        elif char == 'AC':
            self.clear_all()
        elif char == '±':
            self.toggle_sign()
        elif char == '%':
            self.percentage()
        elif char in '0123456789.':
            self.add_digit(char)
        elif char in '+-×÷':
            self.add_operator(char)
    
    def add_digit(self, digit):
        if self.clear_next:
            self.result_var.set(digit)
            self.clear_next = False
            self.new_number = False
        elif self.new_number:
            self.result_var.set(digit)
            self.new_number = False
        else:
            current = self.result_var.get()
            if digit == '.' and '.' in current:
                return
            if current == '0' and digit != '.':
                self.result_var.set(digit)
            else:
                self.result_var.set(current + digit)
    
    def add_operator(self, operator):
        current = self.result_var.get()
        if current != 'Error':
            if self.current_expression:
                # Continue calculation
                self.calculate_result()
                self.current_expression = self.result_var.get() + ' ' + operator + ' '
            else:
                # Start new calculation
                self.current_expression = current + ' ' + operator + ' '
            self.history_var.set(self.current_expression)
            self.clear_next = True
    
    def calculate_result(self):
        try:
            current = self.result_var.get()
            if current == 'Error':
                return
            
            if not self.current_expression:
                return
            
            expression = self.current_expression + current
            expression = expression.replace('×', '*').replace('÷', '/').replace('−', '-')
            
            # Safe eval with limited functions
            result = eval(expression, {"__builtins__": None})
            
            # Store in history
            history_entry = f"{expression} = {result}"
            self.calculation_history.append(history_entry)
            
            self.history_var.set(expression + " =")
            self.result_var.set(str(result))
            self.current_expression = ""
            self.new_number = True
            
        except Exception as e:
            self.result_var.set("Error")
            self.current_expression = ""
            self.new_number = True
    
    def show_history(self):
        """Show calculation history window"""
        history_window = tk.Toplevel(self.master)
        history_window.title("Calculation History")
        history_window.geometry("400x500")
        history_window.configure(bg=self.bg_color)
        history_window.resizable(True, True)
        
        # Make window modal
        history_window.transient(self.master)
        history_window.grab_set()
        
        # Header frame
        header_frame = tk.Frame(history_window, bg=self.bg_color)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Calculation History",
            font=tkfont.Font(family='Arial', size=18, weight='bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(side='left')
        
        # Clear button
        clear_btn = tk.Button(
            header_frame,
            text="Clear All",
            font=tkfont.Font(family='Arial', size=12),
            bg=self.orange_color,
            fg=self.text_color,
            bd=0,
            relief='flat',
            command=lambda: self.clear_history(history_window, history_listbox)
        )
        clear_btn.pack(side='right')
        
        # History listbox
        listbox_frame = tk.Frame(history_window, bg=self.bg_color)
        listbox_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        history_listbox = tk.Listbox(
            listbox_frame,
            bg=self.display_bg,
            fg=self.text_color,
            font=tkfont.Font(family='Arial', size=12),
            selectmode='single',
            yscrollcommand=scrollbar.set,
            bd=0,
            highlightthickness=0
        )
        history_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=history_listbox.yview)
        
        # Populate history
        for entry in reversed(self.calculation_history):
            history_listbox.insert(0, entry)
        
        # Double-click to use result
        history_listbox.bind('<Double-Button-1>', lambda e: self.use_history_result(history_listbox, history_window))
        
        # Center window on screen
        history_window.update_idletasks()
        x = (history_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (history_window.winfo_screenheight() // 2) - (500 // 2)
        history_window.geometry(f"400x500+{x}+{y}")
    
    def clear_history(self, window, listbox):
        """Clear all history entries"""
        self.calculation_history.clear()
        listbox.delete(0, tk.END)
        messagebox.showinfo("History Cleared", "All calculation history has been cleared.")
    
    def use_history_result(self, listbox, window):
        """Use selected history result in calculator"""
        selection = listbox.curselection()
        if selection:
            entry = listbox.get(selection[0])
            # Extract result from history entry (everything after "= ")
            if " = " in entry:
                result = entry.split(" = ")[1]
                self.result_var.set(result)
                self.current_expression = ""
                self.new_number = True
                window.destroy()
                messagebox.showinfo("Result Applied", f"Result '{result}' has been applied to the calculator.")
    
    def clear_all(self):
        self.current_expression = ""
        self.result_var.set("0")
        self.history_var.set("")
        self.new_number = True
        self.clear_next = False
    
    def toggle_sign(self):
        current = self.result_var.get()
        if current != '0' and current != 'Error':
            if current.startswith('-'):
                self.result_var.set(current[1:])
            else:
                self.result_var.set('-' + current)
    
    def percentage(self):
        try:
            current = float(self.result_var.get())
            result = current / 100
            self.result_var.set(str(result))
            self.new_number = True
        except:
            self.result_var.set("Error")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x700")  # Initial size, but can be resized
    calc = iPhoneCalculator(root)
    root.mainloop()
