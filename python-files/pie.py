import re
import time
import threading
from pynput.keyboard import Key, Controller
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class MusicAutoPlayer:
    def __init__(self):
        self.keyboard = Controller()
        self.is_playing = False
        self.play_thread = None
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Musical Notation Auto Player - Cannon in D")
        self.root.geometry("800x600")
        
        # Input text area
        input_frame = ttk.LabelFrame(self.root, text="Musical Notation Input", padding=10)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(input_frame, height=15, width=80)
        self.text_input.pack(fill="both", expand=True)
        
        # Default input (your Cannon in D notation)
        default_input = """[8f] [5d] [6s] [3a] [4p] [1o] [4p] [5a] [8s] a [0s] u [wr] o [7y] u [6t] s [8a] p [5a] f [3h] j [4g] f [6d] g [8f] d [3s] a [4p] o [6i] u [5y] i [2u] y [1h] [8f] g [0wh] [8f] g [5h] o [5p] a [79s] d [5f] g [6f] [6s] d [80f] [6u] i [3o] p [3o] i [57o] s [3a] s [4p] [4s] a [68p] [4o] i [1o] i [1u] i [35o] p [1a] s [4p] [4s] a [68s] [4a] p [5o] p [5a] s [79d] f [5g] h [1f] [8u] [0wi] [8u] [5o] y [9wo] a [%d] O [W0f] d [6s] [0u] [8t] [0ep] [3o] u [7r] u [0w] [7r] [5u] [3o] [4e] [8p] [qa] [8p] [18o] u t u [1w] t u o [4e] p [48qo] [qetp] [5a] r s t [79d] y [5f] u [1osfh] 5 [8sf] [9dg] [0fh] w [0sf] [8dg] [5ah] [2oa] [5ps] [6ad] [7sf] [9ad] [7sf] [5ag] [6pf] 3 [6ps] [7ad] [8sf] 0 [8tu] [6yi] [3uo] [ip?] [3uo] [5yi] [7uo] [0ts] [7ua] [5us] [4ip] 1 [4ps] [6oa] [8ip] q [8uo] [6yi] [1uo] [5yi] [8tu] [9yi] [0uo] [wip] [0oa] [8ps] [4ip] 8 [qps] [woa] [eps] t [eoa] [qip] [5oa] [9ps] [wad] [eps] [rad] [ysf] [rdg] [wah] [8of] [0wt] [us] [0wt] [8od] [0wt] [us] [0wt] [5ya] [79w] [ad] [79w] [5af] [79w] [%ad] [70W] [6ps] [80e] [tp] [80e] [6to] [80e] [tp] [80e] [3uoa] 7 [0wr] 7 [5wu] 7 [0wry] 7 [4et] 8 q [8ps] [4ad] [8q] [4ag] [8q] [1of] 5 [8us] [9uo] [0us] w [0of] 8 [4ps] 8 [qpg] w [epf] t [epg] q [59woad] 5 [59wyo] 5 [25oaf] 5 [25oad] 5 [1us] 1 5 8 0 [woafh] t [5oafh] [pj] [woh] 0 [7ig] 5 [6upsf] e 0 r 0 [tupsf] 0 [3uoaf] 7 [0ig] w [ruf] w [0yd] 7 [4tips] 8 q [wpj] [eak] w [qpj] 8 [1sfhl] 8 [0w] 8 [0wrosfh] 8 [0wt] 8 [4sfhl] 8 [qPJ] w [epj] t [ePJ] q [5wk] h g [5d] a o i y [5r] [5w] [5r] [5w] [5t] [5w] [5t] [5w] [5T] [5w] [5T] [5w] [5y] [5w] [5y] [5w] [5u?] [5w] [5u] [5w] [5i] [5w] [5i] [5w] [5I] [5w] [5I] [5w] [5o] [5w] [5o] [5w] [5o?] w r [5y] o r [5y] o [4a] y o [4a] d o [4a] d [3h] a d [3h] k d [3h] k [2z] h k [2z] v h [2k] z [5v?] h k [5z?] v h [5k?] z [5v?] h k [5z?] v h [5k?] z [5v?] h k [5z?] v h [5k?] z [5v?] [ts] [ts] [ts] [ts] [ts] [ts] [ts] [ts] [1tuos] [8tuos] [5ra] [1tuos] 3 5 8 [10u] 3 5 2 [5wryo] 5 2 5 ? 5 [29y] 5 [5wo] 5 [2ep] 5 [ra?] 5 [2wo] 5 [6ts] 1 3 6 [8ts] 0 [era] 0 [8ts] 6 3 1 [6uf] 1 3 ? [3oafh] 5 ? 3 5 7 [0wo] 7 [5oh] 3 [wo?] 5 [3oh] 5 [pj?] 3 [4ipsg] 1 4 6 [8ig] q [euf] t [eyd] q 8 6 [4ig] 1 6 4 [1uf] [1uf] 5 [1yd] 3 [5tuos] 8 0 w [rta] w 0 8 [4etip] 1 4 6 [8wo] q 8 6 [4qi] 6 8 q [8tups] 6 4 1 [6tups] t u p [6s] f j l [5ryoa] r y o [5a] d h k [1tuos] [8ts] [5ra] [1tus] 3 5 8 [10u] 3 [5ep] 2 [5wryo] 5 2 5 ? 5 [29wry] 5 [5wo] 5 [2ep] 5 [%ra] % [3yd] % [6tups] 1 3 6 [8ts] 0 [era] 0 [8tu"""
        
        self.text_input.insert("1.0", default_input)
        
        # Control frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Speed control
        speed_frame = ttk.LabelFrame(control_frame, text="Playback Speed", padding=5)
        speed_frame.pack(side="left", padx=(0, 10))
        
        ttk.Label(speed_frame, text="Delay (ms):").pack(side="left")
        self.speed_var = tk.StringVar(value="200")
        speed_entry = ttk.Entry(speed_frame, textvariable=self.speed_var, width=8)
        speed_entry.pack(side="left", padx=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side="right")
        
        self.play_button = ttk.Button(button_frame, text="Play", command=self.toggle_play)
        self.play_button.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Stop", command=self.stop_play).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_input).pack(side="left", padx=5)
        
        # Instructions
        instructions = """
Instructions:
1. Paste your musical notation in the text area above
2. Set playback speed (delay between keystrokes in milliseconds)
3. Click Play to start auto-typing the sequence
4. The program will automatically handle:
   - Single keys: a, s, d, f, etc.
   - Chords in brackets: [8f], [5d], [68p] (played simultaneously)
   - Numbers and special characters
5. Click Stop to halt playback
6. Make sure the target application (like a piano software) is in focus when playing

Note: This will send actual keystrokes to whatever application is currently focused.
Make sure your piano/music software is the active window before clicking Play.
        """
        
        info_frame = ttk.LabelFrame(self.root, text="Instructions", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        info_label = ttk.Label(info_frame, text=instructions, justify="left")
        info_label.pack(anchor="w")
    
    def parse_notation(self, notation):
        """Parse the musical notation into a sequence of keystrokes"""
        # Remove extra whitespace and split into tokens
        tokens = re.findall(r'\[[^\]]+\]|[^\s\[\]]+', notation.strip())
        
        parsed_sequence = []
        
        for token in tokens:
            if token.startswith('[') and token.endswith(']'):
                # Chord - extract all characters inside brackets
                chord_keys = token[1:-1]  # Remove brackets
                # Split chord into individual characters/keys
                keys = list(chord_keys)
                parsed_sequence.append(('chord', keys))
            else:
                # Single key or sequence of single keys
                for char in token:
                    if char.strip():  # Ignore empty characters
                        parsed_sequence.append(('single', char))
        
        return parsed_sequence
    
    def play_sequence(self, sequence, delay):
        """Play the parsed sequence"""
        try:
            for i, (note_type, keys) in enumerate(sequence):
                if not self.is_playing:
                    break
                
                if note_type == 'chord':
                    # Press all keys in chord simultaneously
                    pressed_keys = []
                    for key in keys:
                        try:
                            self.keyboard.press(key)
                            pressed_keys.append(key)
                        except:
                            pass  # Skip invalid keys
                    
                    # Small delay to ensure all keys are registered
                    time.sleep(0.05)
                    
                    # Release all keys
                    for key in pressed_keys:
                        try:
                            self.keyboard.release(key)
                        except:
                            pass
                
                elif note_type == 'single':
                    # Press and release single key
                    try:
                        self.keyboard.press(keys)
                        time.sleep(0.05)
                        self.keyboard.release(keys)
                    except:
                        pass  # Skip invalid keys
                
                # Wait for specified delay
                time.sleep(delay / 1000.0)
                
                # Update progress (optional - could add a progress bar)
                progress = (i + 1) / len(sequence) * 100
                
        except Exception as e:
            messagebox.showerror("Playback Error", f"An error occurred during playback: {str(e)}")
        finally:
            self.is_playing = False
            self.play_button.config(text="Play")
    
    def toggle_play(self):
        if not self.is_playing:
            # Start playing
            notation = self.text_input.get("1.0", "end-1c").strip()
            if not notation:
                messagebox.showwarning("No Input", "Please enter musical notation to play.")
                return
            
            try:
                delay = float(self.speed_var.get())
                if delay < 0:
                    raise ValueError("Delay must be positive")
            except ValueError:
                messagebox.showerror("Invalid Speed", "Please enter a valid positive number for delay.")
                return
            
            # Parse the notation
            try:
                sequence = self.parse_notation(notation)
                if not sequence:
                    messagebox.showwarning("Parse Error", "No valid musical notation found.")
                    return
            except Exception as e:
                messagebox.showerror("Parse Error", f"Error parsing notation: {str(e)}")
                return
            
            # Start playback in separate thread
            self.is_playing = True
            self.play_button.config(text="Playing...")
            
            # Give user 3 seconds to switch to target application
            messagebox.showinfo("Get Ready", "Playback will start in 3 seconds.\nSwitch to your piano/music application now!")
            
            def delayed_start():
                time.sleep(3)
                if self.is_playing:  # Check if still playing (user might have stopped)
                    self.play_sequence(sequence, delay)
            
            self.play_thread = threading.Thread(target=delayed_start, daemon=True)
            self.play_thread.start()
        
        else:
            # Stop playing
            self.stop_play()
    
    def stop_play(self):
        self.is_playing = False
        self.play_button.config(text="Play")
        if self.play_thread and self.play_thread.is_alive():
            # Thread will stop on next iteration due to self.is_playing = False
            pass
    
    def clear_input(self):
        self.text_input.delete("1.0", "end")
    
    def run(self):
        self.root.mainloop()

# Installation instructions and requirements
installation_info = """
INSTALLATION REQUIREMENTS:

1. Install Python 3.6 or higher
2. Install required packages:
   pip install pynput tkinter

USAGE:
1. Run this script: python music_auto_player.py
2. The GUI will open with Cannon in D notation pre-loaded
3. Adjust playback speed if needed
4. Click Play and quickly switch to your piano software
5. The program will start typing the keys after 3 seconds

IMPORTANT NOTES:
- This sends actual keystrokes to whatever application is focused
- Make sure your piano/music software is the active window before playback starts
- The program handles both single keys and chords (keys in brackets)
- Use the Stop button to halt playback at any time
- Numbers and special characters in the notation are preserved
"""

if __name__ == "__main__":
    print(installation_info)
    print("\nStarting Musical Notation Auto Player...")
    
    app = MusicAutoPlayer()
    app.run()