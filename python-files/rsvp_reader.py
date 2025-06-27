import os
import sys
import time
import re
import msvcrt
import ctypes
from PyPDF2 import PdfReader

def set_console_size():
    """Set console window size to 80x25 characters."""
    os.system('mode con: cols=80 lines=25')

def set_console_position(x, y):
    """Set console window position to (x, y) pixels on the screen."""
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001 | 0x0004)

def clear_console():
    """Clear the Windows console."""
    os.system('cls')

def read_txt_file(file_path):
    """Read content from a .txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading .txt file: {e}")
        return None

def read_pdf_file(file_path):
    """Read content from a .pdf file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading .pdf file: {e}")
        return None

def process_text(text):
    """Process text into a list of words, removing punctuation."""
    words = re.findall(r'\b\w+\b', text.lower())
    return words

def display_lines(lines, console_width=80):
    """Display multiple lines of word chunks, centered in the console."""
    max_len = max(len(' '.join(line)) for line in lines) if lines else console_width
    vertical_padding = (15 - len(lines)) // 2  # Vertical centering (15 lines available)
    print('\n' * vertical_padding)
    for line in lines:
        line_text = ' '.join(line)
        horizontal_padding = (console_width - len(line_text)) // 2
        print(' ' * horizontal_padding + line_text)
    print('\n' * vertical_padding)

def rsvp_display(words, wpm, chunk_size, num_lines, pause_enabled):
    """Display words using RSVP with multiple lines per frame."""
    if not words:
        print("No words to display.")
        return
    words_per_frame = chunk_size * num_lines
    delay = 60.0 / wpm * words_per_frame  # Seconds per frame
    i = 0
    paused = False
    while i < len(words):
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'p' and pause_enabled:
                paused = not paused
                clear_console()
                print("Paused. Press 'p' to resume." if paused else "Resumed.")
                time.sleep(0.5)
        if paused:
            time.sleep(0.1)
            continue
        # Prepare lines for the current frame
        lines = []
        for j in range(num_lines):
            start = i + j * chunk_size
            if start < len(words):
                chunk = words[start:start + chunk_size]
                if chunk:
                    lines.append(chunk)
        if lines:
            clear_console()
            display_lines(lines)
            time.sleep(max(delay, 0.01))  # Ensure minimum delay for console refresh
        i += words_per_frame
        if i >= len(words):
            break
    clear_console()
    print("End of text.")

def get_valid_input(prompt, type_func, min_val=None, max_val=None):
    """Get validated user input."""
    while True:
        try:
            value = type_func(input(prompt))
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                print(f"Please enter a value between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Try again.")

def main():
    """Main function to run the RSVP reader."""
    set_console_size()
    print("Welcome to RSVP Reader!")
    
    # Get file path
    while True:
        file_path = input("Enter the path to a .txt or .pdf file: ").strip()
        if not os.path.exists(file_path):
            print("File does not exist. Try again.")
            continue
        if not file_path.lower().endswith(('.txt', '.pdf')):
            print("Only .txt and .pdf files are supported. Try again.")
            continue
        break
    
    # Read file content
    if file_path.lower().endswith('.txt'):
        text = read_txt_file(file_path)
    else:
        text = read_pdf_file(file_path)
    
    if not text:
        print("Failed to read the file. Exiting.")
        sys.exit(1)
    
    words = process_text(text)
    if not words:
        print("No valid words found in the file. Exiting.")
        sys.exit(1)
    
    # Get RSVP settings
    wpm = get_valid_input("Enter speed (words per minute, 100-5000): ", int, 100, 5000)
    chunk_size = get_valid_input("Enter words per line (1-5): ", int, 1, 5)
    num_lines = get_valid_input("Enter number of lines per frame (1-5): ", int, 1, 5)
    x_pos = get_valid_input("Enter window X position (pixels, 0-1920): ", int, 0, 1920)
    y_pos = get_valid_input("Enter window Y position (pixels, 0-1080): ", int, 0, 1080)
    
    # Set console position
    set_console_position(x_pos, y_pos)
    
    # Start RSVP
    print("Starting RSVP. Press 'p' to pause/resume, or Ctrl+C to exit.")
    time.sleep(2)
    try:
        rsvp_display(words, wpm, chunk_size, num_lines, pause_enabled=True)
    except KeyboardInterrupt:
        clear_console()
        print("RSVP stopped by user.")
    
    print("Program ended.")

if __name__ == "__main__":
    main()