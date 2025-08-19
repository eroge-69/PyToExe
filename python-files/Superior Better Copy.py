import time, re, threading
import pyautogui
import customtkinter as ctk
import win32api, win32con  # type: ignore
import keyboard
import pyperclip
from typing import Optional


class AutoTyperApp(ctk.CTk):
    """Auto-typing app with special commands."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Superior Better Copy")
        self.geometry("500x600")  # Window size
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # App settings
        self.typing_speed: float = 0.01  # How fast to type (0.01 ms per character)
        self.typing_thread: Optional[threading.Thread] = None
        self.stop_typing_flag: bool = False
        self.last_typed_char: Optional[str] = None  # Track last character typed
        self.ignore_mode: bool = True  # Default to ignore mode

        # Make the GUI
        self._setup_widgets()
        
        # Set up global hotkey for Ctrl+F7 (works even when app is not focused)
        keyboard.add_hotkey('ctrl+f7', self.start_typing_from_clipboard)

    def _setup_widgets(self) -> None:
        """Create all the buttons and text areas."""
        self.label: ctk.CTkLabel = ctk.CTkLabel(
            self, 
            text="Enter text to type:", 
            font=("Arial", 16),
            text_color="#00E6E6"
        )
        self.label.pack(pady=10)

        self.help_label: ctk.CTkLabel = ctk.CTkLabel(
            self, 
            text="Special features:\n• [backspace] - Press backspace\n• [enter] - Press enter key\n• [arrow up/left/right/down] - Arrow keys\n• [delay 2.5] - Wait 2.5 seconds\n• [ctrl+c] - Press Ctrl+C\n• [shift+tab] - Press Shift+Tab",
            font=("Arial", 14),
            text_color="#B0E0E6"
        )
        self.help_label.pack(pady=5)

        self.ignore_checkbox: ctk.CTkCheckBox = ctk.CTkCheckBox(
            self,
            text="Ignore mode (type brackets as text)",
            command=self._toggle_ignore_mode,
            font=("Arial", 12),
            text_color="#B0E0E6"
        )
        self.ignore_checkbox.pack(pady=5)
        self.ignore_checkbox.select()  # Default to checked

        self.text_box: ctk.CTkTextbox = ctk.CTkTextbox(
            self, 
            width=450, 
            height=250, 
            font=("Arial", 22)
        )
        self.text_box.pack(pady=10)

        self.start_button: ctk.CTkButton = ctk.CTkButton(
            self, 
            text="Start Typing (Ctrl+F7)", 
            command=self.start_typing, 
            font=("Arial", 14, "bold"),
            fg_color="#00B4B4",
            hover_color="#00D4D4",
            text_color="#FFFFFF"
        )
        self.start_button.pack(pady=10)

        self.stop_button: ctk.CTkButton = ctk.CTkButton(
            self, 
            text="Stop Typing", 
            command=self.stop_typing, 
            font=("Arial", 14, "bold"),
            fg_color="#008080",
            hover_color="#00A0A0",
            text_color="#FFFFFF"
        )
        self.stop_button.pack(pady=5)



    def start_typing(self) -> None:
        """Start typing the text."""
        if self.typing_thread and self.typing_thread.is_alive():
            return  # Don't start twice

        self.stop_typing_flag = False
        text: str = self.text_box.get("0.0", "end-1c")
        self.typing_thread = threading.Thread(target=self._type_text, args=(text,))
        self.typing_thread.start()

    def start_typing_from_clipboard(self) -> None:
        """Start typing text from clipboard."""
        try:
            clipboard_text: str = pyperclip.paste()
            if clipboard_text.strip():
                if self.typing_thread and self.typing_thread.is_alive():
                    return  # Don't start twice

                self.stop_typing_flag = False
                self.typing_thread = threading.Thread(target=self._type_text, args=(clipboard_text,))
                self.typing_thread.start()
        except Exception as e:
            print(f"Error accessing clipboard: {e}")

    def stop_typing(self) -> None:
        """Stop typing."""
        self.stop_typing_flag = True

    def _toggle_ignore_mode(self) -> None:
        """Toggle ignore mode based on checkbox state."""
        self.ignore_mode = self.ignore_checkbox.get()

    def _type_text(self, text: str) -> None:
        """Do the actual typing with commands."""
        time.sleep(2)  # Wait for user to switch windows
        
        pattern: re.Pattern = re.compile(r'\[(.*?)\]')
        index: int = 0
        
        while index < len(text):
            if self.stop_typing_flag:
                break
                
            if text[index] == '[':
                match: Optional[re.Match] = pattern.match(text, index)
                if match:
                    combo_text: str = match.group(1).lower()
                    
                    # Type brackets as text in ignore mode
                    if self.ignore_mode:
                        for char in match.group(0):
                            if self.stop_typing_flag:
                                break
                            self._type_character(char)
                        index += len(match.group(0))
                        continue
                    
                    # Handle special commands
                    if combo_text == 'backspace':
                        pyautogui.press('backspace')
                        self.last_typed_char = None
                    elif combo_text == 'enter':
                        pyautogui.press('enter')
                        self.last_typed_char = '\n'
                    elif combo_text.startswith('arrow '):
                        direction = combo_text[6:].lower()
                        if direction in ['up', 'down', 'left', 'right']:
                            pyautogui.press(direction)
                        self.last_typed_char = None
                    elif combo_text.startswith('delay'):
                        try:
                            if combo_text == 'delay':
                                time.sleep(0.5)  # Default delay
                            else:
                                delay_seconds: float = float(combo_text.split(' ')[1])
                                time.sleep(delay_seconds)
                        except (IndexError, ValueError):
                            time.sleep(1)  # If error, wait 1 second
                        self.last_typed_char = None
                    else:
                        # Handle key combos like ctrl+c
                        combo: list[str] = combo_text.split('+')
                        for key in combo:
                            pyautogui.keyDown(key.strip())
                        for key in reversed(combo):
                            pyautogui.keyUp(key.strip())
                        self.last_typed_char = None
                    
                    index += len(match.group(0))
                    continue
            
            # Type normal characters
            char: str = text[index]
            self._type_character(char)
            index += 1

    def _type_character(self, char: str) -> None:
        """Type one character."""
        if char == '\n':
            pyautogui.press('enter')
        elif char == '\t':
            pyautogui.press('tab')
        elif char == ' ':
            pyautogui.press('space')
            self.last_typed_char = ' '
        elif char.isalpha():
            if char.isupper():
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                win32api.keybd_event(0x41 + ord(char.lower()) - ord('a'), 0, 0, 0)
                win32api.keybd_event(0x41 + ord(char.lower()) - ord('a'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            else:
                win32api.keybd_event(0x41 + ord(char) - ord('a'), 0, 0, 0)
                win32api.keybd_event(0x41 + ord(char) - ord('a'), 0, win32con.KEYEVENTF_KEYUP, 0)
            self.last_typed_char = char
        else:
            pyautogui.typewrite(char)
        
        # Wait between characters
        if self.typing_speed > 0:
            time.sleep(self.typing_speed / 1000)


if __name__ == "__main__":
    app: AutoTyperApp = AutoTyperApp()
    app.mainloop()  # Start the app
