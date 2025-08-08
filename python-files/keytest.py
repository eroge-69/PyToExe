import tkinter as tk
from tkinter import ttk
from collections import defaultdict

class KeyboardTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyboard Tester")
        self.root.geometry("1200x500")
        
        # Initialize dictionaries to track keys
        self.key_buttons = {}  # This was missing
        self.keys_ever_pressed = set()
        self.currently_pressed = set()
        self.all_keys = set()
        
        # Create main frames
        self.create_widgets()
        
        # Bind keyboard events
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # Focus on the main window
        self.root.focus_set()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Press keys on your keyboard to test them. Keys turn RED while pressed and LIGHT GREEN when released.",
            wraplength=1000,
            justify="center",
            font=('Helvetica', 10, 'bold')
        )
        instructions.pack(pady=(0, 10))
        
        # Keyboard frame
        keyboard_frame = ttk.Frame(main_frame)
        keyboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create keyboard sections
        self.create_function_row(keyboard_frame)
        self.create_main_keyboard(keyboard_frame)
        self.create_arrow_keys(keyboard_frame)
        self.create_numpad(keyboard_frame)
        
        # Stats frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.keys_pressed_label = ttk.Label(
            stats_frame,
            text="Keys pressed: 0",
            font=('Helvetica', 10, 'bold')
        )
        self.keys_pressed_label.pack(side=tk.LEFT, padx=5)
        
        self.keys_not_pressed_label = ttk.Label(
            stats_frame,
            text="Keys not pressed: 0",
            font=('Helvetica', 10, 'bold')
        )
        self.keys_not_pressed_label.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_button = ttk.Button(
            main_frame,
            text="Reset Test",
            command=self.reset_test
        )
        reset_button.pack(pady=10)
        
    def create_function_row(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 5))
        
        keys = [
            ('Esc', ['Escape']),
            ('F1', ['F1']), ('F2', ['F2']), ('F3', ['F3']), ('F4', ['F4']),
            ('F5', ['F5']), ('F6', ['F6']), ('F7', ['F7']), ('F8', ['F8']),
            ('F9', ['F9']), ('F10', ['F10']), ('F11', ['F11']), ('F12', ['F12']),
            ('PrtSc', ['Print']), ('ScrLk', ['Scroll_Lock']), ('Pause', ['Pause'])
        ]
        
        for key, key_symbols in keys:
            self.create_key_button(frame, key, key_symbols, width=4)
    
    def create_main_keyboard(self, parent):
        # Main keyboard rows
        rows = [
            # Row 1
            [('`~', ['grave', 'asciitilde']), ('1!', ['1', 'exclam']), 
             ('2@', ['2', 'at']), ('3#', ['3', 'numbersign']), 
             ('4$', ['4', 'dollar']), ('5%', ['5', 'percent']), 
             ('6^', ['6', 'asciicircum']), ('7&', ['7', 'ampersand']), 
             ('8*', ['8', 'asterisk']), ('9(', ['9', 'parenleft']), 
             ('0)', ['0', 'parenright']), ('-_', ['minus', 'underscore']), 
             ('=+', ['equal', 'plus']), ('Backspace', ['BackSpace'], 10)],
            
            # Row 2
            [('Tab', ['Tab'], 8), ('Q', ['q']), ('W', ['w']), ('E', ['e']), 
             ('R', ['r']), ('T', ['t']), ('Y', ['y']), ('U', ['u']), 
             ('I', ['i']), ('O', ['o']), ('P', ['p']), ('[{', ['bracketleft', 'braceleft']), 
             (']}', ['bracketright', 'braceright']), ('\\|', ['backslash', 'bar'], 8)],
            
            # Row 3
            [('Caps', ['Caps_Lock'], 9), ('A', ['a']), ('S', ['s']), 
             ('D', ['d']), ('F', ['f']), ('G', ['g']), ('H', ['h']), 
             ('J', ['j']), ('K', ['k']), ('L', ['l']), (';:', ['semicolon', 'colon']), 
             ('"\'', ['quoteright', 'quotedbl']), ('Enter', ['Return'], 12)],
            
            # Row 4
            [('L-Shift', ['Shift_L'], 12), ('Z', ['z']), ('X', ['x']), 
             ('C', ['c']), ('V', ['v']), ('B', ['b']), ('N', ['n']), 
             ('M', ['m']), (',<', ['comma', 'less']), ('.>', ['period', 'greater']), 
             ('/?', ['slash', 'question']), ('R-Shift', ['Shift_R'], 15)],
            
            # Row 5
            [('L-Ctrl', ['Control_L'], 8), ('L-Win', ['Super_L'], 8), 
             ('L-Alt', ['Alt_L'], 8), ('Space', ['space'], 40), 
             ('R-Alt', ['Alt_R'], 8), ('R-Win', ['Super_R'], 8), 
             ('Menu', ['Menu']), ('R-Ctrl', ['Control_R'], 8)]
        ]
        
        for row in rows:
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=1)
            for key_info in row:
                if len(key_info) == 3:
                    key, key_symbols, width = key_info
                else:
                    key, key_symbols = key_info
                    width = 4
                self.create_key_button(frame, key, key_symbols, width)
    
    def create_arrow_keys(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(5, 0))
        
        # Spacer to align with main keyboard
        spacer = ttk.Frame(frame, width=420)
        spacer.pack(side=tk.LEFT)
        
        # Arrow keys
        keys = [
            ('↑', ['Up'], 4),
            ('←', ['Left'], 4), ('↓', ['Down'], 4), ('→', ['Right'], 4)
        ]
        
        for key, key_symbols, width in keys:
            self.create_key_button(frame, key, key_symbols, width)
    
    def create_numpad(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(5, 0))
        
        # Spacer to position numpad on the right
        spacer = ttk.Frame(frame, width=780)
        spacer.pack(side=tk.LEFT)
        
        # Numpad rows
        numpad_rows = [
            [('Num\nLock', ['Num_Lock']), ('/', ['KP_Divide']), ('*', ['KP_Multiply']), ('-', ['KP_Subtract'])],
            [('7\nHome', ['KP_7', 'KP_Home']), ('8\n↑', ['KP_8', 'KP_Up']), ('9\nPgUp', ['KP_9', 'KP_Prior']), ('+', ['KP_Add'], 4, 3)],
            [('4\n←', ['KP_4', 'KP_Left']), ('5', ['KP_5']), ('6\n→', ['KP_6', 'KP_Right'])],
            [('1\nEnd', ['KP_1', 'KP_End']), ('2\n↓', ['KP_2', 'KP_Down']), ('3\nPgDn', ['KP_3', 'KP_Next']), ('Enter', ['KP_Enter'], 4, 3)],
            [('0\nIns', ['KP_0', 'KP_Insert'], 8), ('.\nDel', ['KP_Decimal', 'KP_Delete'])]
        ]
        
        for row in numpad_rows:
            row_frame = ttk.Frame(frame)
            row_frame.pack(side=tk.LEFT, padx=1)
            for key_info in row:
                if len(key_info) == 4:
                    key, key_symbols, width, height = key_info
                elif len(key_info) == 3:
                    key, key_symbols, width = key_info
                    height = 2
                else:
                    key, key_symbols = key_info
                    width = 4
                    height = 2
                self.create_key_button(row_frame, key, key_symbols, width, height)
    
    def create_key_button(self, parent, text, key_symbols, width=4, height=2):
        # Add to all_keys set
        for sym in key_symbols:
            self.all_keys.add(sym.lower())
        
        # Create button
        btn = tk.Button(
            parent,
            text=text,
            width=width,
            height=height,
            bg='SystemButtonFace',
            relief=tk.RAISED,
            borderwidth=2,
            font=('Helvetica', 8 if '\n' in text else 9),
            justify=tk.CENTER,
            wraplength=width*8
        )
        btn.pack(side=tk.LEFT, padx=1)
        
        # Store button reference
        for sym in key_symbols:
            self.key_buttons[sym.lower()] = (btn, text)
    
    def on_key_press(self, event):
        key = event.keysym.lower()
        
        if key not in self.currently_pressed:
            self.currently_pressed.add(key)
            self.keys_ever_pressed.add(key)
            
            # Update button appearance
            if key in self.key_buttons:
                btn, display_name = self.key_buttons[key]
                
                # Special colors for modifier keys
                if display_name.startswith('L-'):
                    btn.config(bg='#ff9999', fg='black')  # Light red for left modifiers
                elif display_name.startswith('R-'):
                    btn.config(bg='#ff6666', fg='black')  # Darker red for right modifiers
                else:
                    btn.config(bg='red', fg='white')  # Regular red for other keys
        
        # Update stats
        self.update_stats()
    
    def on_key_release(self, event):
        key = event.keysym.lower()
        
        if key in self.currently_pressed:
            self.currently_pressed.remove(key)
            
            # Update button appearance
            if key in self.key_buttons:
                btn, display_name = self.key_buttons[key]
                
                # Special colors for modifier keys
                if display_name.startswith('L-'):
                    btn.config(bg='#ccffcc', fg='black')  # Light green for left modifiers
                elif display_name.startswith('R-'):
                    btn.config(bg='#99ff99', fg='black')  # Slightly darker green for right modifiers
                else:
                    btn.config(bg='#aaffaa', fg='black')  # Regular light green for other keys
        
        # Update stats
        self.update_stats()
    
    def update_stats(self):
        pressed_count = len(self.keys_ever_pressed)
        not_pressed_count = len(self.all_keys) - pressed_count
        
        self.keys_pressed_label.config(text=f"Keys pressed: {pressed_count}")
        self.keys_not_pressed_label.config(text=f"Keys not pressed: {not_pressed_count}")
    
    def reset_test(self):
        # Reset all tracking
        self.keys_ever_pressed.clear()
        self.currently_pressed.clear()
        
        # Reset all buttons to default style
        for btn_info in self.key_buttons.values():
            btn = btn_info[0]
            btn.config(bg='SystemButtonFace', fg='black')
        
        # Reset stats
        self.update_stats()
        
        # Focus back on the window
        self.root.focus_set()

def main():
    root = tk.Tk()
    app = KeyboardTesterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()