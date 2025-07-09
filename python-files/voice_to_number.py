import tkinter as tk
from tkinter import ttk
import threading
import queue
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import re
import speech_recognition as sr

# ------------------ Persian number conversion helpers ------------------
_UNIT_NUMBERS = {
    "صفر": 0, "یک": 1, "دو": 2, "سه": 3, "چهار": 4, "پنج": 5, "شش": 6,
    "هفت": 7, "هشت": 8, "نه": 9
}
_TEENS = {
    "ده": 10, "یازده": 11, "دوازده": 12, "سیزده": 13, "چهارده": 14,
    "پانزده": 15, "شانزده": 16, "هفده": 17, "هجده": 18, "نوزده": 19
}
_TENS = {
    "بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50, "شصت": 60,
    "هفتاد": 70, "هشتاد": 80, "نود": 90
}
_HUNDREDS = {
    "صد": 100, "دویست": 200, "سیصد": 300, "چهارصد": 400, "پانصد": 500,
    "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900
}
_MULTIPLIERS = {
    "هزار": 1000, "میلیون": 1_000_000, "میلیارد": 1_000_000_000
}

_PERSIAN_NUM_WORDS = {**_UNIT_NUMBERS, **_TEENS, **_TENS, **_HUNDREDS}


def persian_words_to_number(text: str) -> int:
    """Convert Persian number words to integer. Basic support up to billions."""
    if not text:
        return 0

    tokens = re.split(r"[\s\u200c]+", text.strip())  # split by space or ZWNJ
    total = 0
    section = 0
    for word in tokens:
        if word == "و":
            continue  # skip conjunction
        if word in _PERSIAN_NUM_WORDS:
            section += _PERSIAN_NUM_WORDS[word]
        elif word in _MULTIPLIERS:
            multiplier = _MULTIPLIERS[word]
            if section == 0:
                section = 1  # e.g., "هزار" => 1000
            total += section * multiplier
            section = 0
        else:
            # Try to parse any digits that slipped through
            if word.isdigit():
                section += int(word)
            # otherwise ignore unknown tokens
    return total + section

# Add digit translation map and helper
_PERSIAN_TO_ASCII_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def extract_digits(text: str) -> int | None:
    """Return int if the text contains explicit digits (ASCII or Persian)."""
    # Replace Persian digits with ASCII
    normalized = text.translate(_PERSIAN_TO_ASCII_DIGITS)
    # Remove thousand separators like , or ٬
    normalized = re.sub(r"[٬,]", "", normalized)
    digits = re.findall(r"\d+", normalized)
    if digits:
        # Join all found groups (e.g., "1 234" -> 1234)
        num_str = "".join(digits)
        try:
            return int(num_str)
        except ValueError:
            return None
    return None

# ------------------ Audio recording and recognition ------------------

def save_wav(filename: str, data: np.ndarray, samplerate: int):
    """Save numpy int16 array as WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16 bits => 2 bytes
        wf.setframerate(samplerate)
        wf.writeframes(data.tobytes())


class VoiceRecorder:
    """Handles audio recording in a background thread using sounddevice."""

    def __init__(self, samplerate: int = 16000):
        self.samplerate = samplerate
        self._recording = False
        self._frames = []
        self._stream = None
        self._lock = threading.Lock()

    def _callback(self, indata, frames, time, status):  # noqa: N802
        if status:
            print(f"Recording status: {status}")
        with self._lock:
            if self._recording:
                # Copy the data as int16
                self._frames.append(indata.copy())

    def start(self):
        if self._recording:
            return
        self._frames.clear()
        self._recording = True
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="int16",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        if not self._recording:
            return np.array([], dtype=np.int16)
        self._recording = False
        self._stream.stop()
        self._stream.close()
        self._stream = None
        with self._lock:
            if not self._frames:
                return np.array([], dtype=np.int16)
            audio = np.concatenate(self._frames, axis=0)
        return audio.flatten()


# ------------------ GUI ------------------

# Modern color palette - redesigned for harmony
PRIMARY_DARK = "#1a1a2e"
SECONDARY_DARK = "#16213e"
ACCENT_BLUE = "#0f3460"
CARD_BG = "#ffffff"
GRADIENT_START = "#4facfe"
GRADIENT_END = "#00f2fe"
ACCENT_PURPLE = "#667eea"
ACCENT_GREEN = "#4facfe"
ACCENT_CORAL = "#ff6b6b"
TEXT_LIGHT = "#ffffff"
TEXT_SECONDARY = "#a8b2d1"
TEXT_DARK = "#2d3748"
RESULT_COLOR = "#0f3460"


class RoundedButton(tk.Canvas):
    """Custom rounded button using Canvas with high-quality rendering."""
    def __init__(self, parent, text, bg_color, hover_color, command=None, state="normal", **kwargs):
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text = text
        self.command = command
        self.button_state = state
        
        # Canvas dimensions with higher resolution
        width = kwargs.get('width', 120)
        height = kwargs.get('height', 40)
        
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent.cget('bg'),
                        relief='flat', bd=0)
        
        self.draw_button()
        
        # Bind events
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def draw_button(self, is_hover=False):
        self.delete("all")
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        radius = min(height // 2 - 2, 18)  # Adaptive radius
        
        # Choose color
        color = self.hover_color if is_hover else self.bg_color
        if self.button_state == "disabled":
            color = "#7f8c8d"
        
        # Create smoother rounded rectangle using arcs
        self.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, 
                       fill=color, outline=color, style='pieslice')
        self.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, 
                       fill=color, outline=color, style='pieslice')
        self.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, 
                       fill=color, outline=color, style='pieslice')
        self.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, 
                       fill=color, outline=color, style='pieslice')
        
        # Fill rectangles to complete the shape
        self.create_rectangle(radius, 0, width-radius, height, fill=color, outline=color)
        self.create_rectangle(0, radius, width, height-radius, fill=color, outline=color)
        
        # Draw text with better positioning
        text_color = "white" if self.button_state != "disabled" else "#bdc3c7"
        self.create_text(width//2, height//2, text=self.text, 
                        fill=text_color, font=("Segoe UI", 11, "bold"),
                        anchor="center")
    
    def _on_enter(self, e):
        if self.button_state != "disabled":
            self.draw_button(is_hover=True)
            self.config(cursor="hand2")
    
    def _on_leave(self, e):
        if self.button_state != "disabled":
            self.draw_button(is_hover=False)
            self.config(cursor="")
    
    def _on_click(self, e):
        if self.button_state != "disabled" and self.command:
            self.command()
    
    def _on_release(self, e):
        pass
    
    def config_state(self, state):
        self.button_state = state
        self.draw_button()


class RoundedCard(tk.Canvas):
    """Custom rounded card using Canvas with high-quality rendering."""
    def __init__(self, parent, bg_color=CARD_BG, width=400, height=300, **kwargs):
        self.bg_color = bg_color
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=parent.cget('bg'),
                        relief='flat', bd=0)
        self.draw_card()
        
        # Create a frame inside for content
        self.content_frame = tk.Frame(self, bg=bg_color)
        self.content_frame.place(x=20, y=20, width=width-40, height=height-40)
        
    def draw_card(self):
        self.delete("card")
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        radius = 20  # Reasonable radius for smoother rendering
        
        # Draw card background using arcs for perfect curves
        self.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, 
                       fill=self.bg_color, outline="#e0e0e0", width=1, style='pieslice', tags="card")
        self.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, 
                       fill=self.bg_color, outline="#e0e0e0", width=1, style='pieslice', tags="card")
        self.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, 
                       fill=self.bg_color, outline="#e0e0e0", width=1, style='pieslice', tags="card")
        self.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, 
                       fill=self.bg_color, outline="#e0e0e0", width=1, style='pieslice', tags="card")
        
        # Fill rectangles
        self.create_rectangle(radius, 0, width-radius, height, 
                             fill=self.bg_color, outline="#e0e0e0", width=1, tags="card")
        self.create_rectangle(0, radius, width, height-radius, 
                             fill=self.bg_color, outline="#e0e0e0", width=1, tags="card")
        
        # Draw border lines
        self.create_line(radius, 0, width-radius, 0, fill="#e0e0e0", width=1, tags="card")
        self.create_line(radius, height-1, width-radius, height-1, fill="#e0e0e0", width=1, tags="card")
        self.create_line(0, radius, 0, height-radius, fill="#e0e0e0", width=1, tags="card")
        self.create_line(width-1, radius, width-1, height-radius, fill="#e0e0e0", width=1, tags="card")


# Replace AnimatedButton usage with RoundedButton
class AnimatedButton(RoundedButton):
    """Alias for compatibility."""
    pass


class GradientFrame(tk.Canvas):
    """Canvas that simulates gradient background."""
    def __init__(self, parent, color1, color2, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind('<Configure>', self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        if width > 1 and height > 1:
            # Simple vertical gradient simulation
            for i in range(height):
                ratio = i / height
                r1, g1, b1 = self._hex_to_rgb(self.color1)
                r2, g2, b2 = self._hex_to_rgb(self.color2)
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.create_line(0, i, width, i, fill=color, tags="gradient")
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VitaSense")
        self.root.geometry("550x480")
        self.root.configure(bg=PRIMARY_DARK)
        self.root.resizable(False, False)
        
        # Create gradient background
        self.bg_gradient = GradientFrame(self.root, PRIMARY_DARK, SECONDARY_DARK, 
                                        width=550, height=480)
        self.bg_gradient.pack(fill="both", expand=True)
        
        # Main container
        main_container = tk.Frame(self.bg_gradient, bg=PRIMARY_DARK, bd=0)
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header section
        header_frame = tk.Frame(main_container, bg=PRIMARY_DARK, bd=0)
        header_frame.pack(pady=(0, 25))
        
        # App title
        title_main = tk.Label(header_frame, text="VitaSense", 
                             font=("Segoe UI", 28, "bold"),
                             fg=TEXT_LIGHT, bg=PRIMARY_DARK)
        title_main.pack()
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="🎙️ تبدیل هوشمند صدا به عدد", 
                           font=("Tahoma", 11),
                           fg=TEXT_SECONDARY, bg=PRIMARY_DARK)
        subtitle.pack(pady=(5, 0))
        
        # Modern card container
        card_container = tk.Frame(main_container, bg=PRIMARY_DARK, bd=0)
        card_container.pack(pady=10)
        
        # Main rounded card
        self.rounded_card = RoundedCard(card_container, bg_color=CARD_BG, width=420, height=340)
        self.rounded_card.pack()
        
        # Use the content frame inside the rounded card
        self.card = self.rounded_card.content_frame
        
        # Result section
        result_section = tk.Frame(self.card, bg=CARD_BG, bd=0)
        result_section.pack(pady=(5, 15))
        
        result_title = tk.Label(result_section, text="نتیجه", 
                               font=("Tahoma", 12, "bold"),
                               fg=TEXT_DARK, bg=CARD_BG)
        result_title.pack()
        
        # Result display with rounded background
        result_bg_canvas = tk.Canvas(result_section, height=60, width=300,
                                    bg=CARD_BG, highlightthickness=0, relief='flat', bd=0)
        result_bg_canvas.pack(pady=(8, 0))
        
        # Draw rounded rectangle for result background using arcs
        radius = 12
        result_bg_canvas.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, 
                                   fill="#f8f9fa", outline="#e0e0e0", width=1, style='pieslice')
        result_bg_canvas.create_arc(300-radius*2, 0, 300, radius*2, start=0, extent=90, 
                                   fill="#f8f9fa", outline="#e0e0e0", width=1, style='pieslice')
        result_bg_canvas.create_arc(0, 60-radius*2, radius*2, 60, start=180, extent=90, 
                                   fill="#f8f9fa", outline="#e0e0e0", width=1, style='pieslice')
        result_bg_canvas.create_arc(300-radius*2, 60-radius*2, 300, 60, start=270, extent=90, 
                                   fill="#f8f9fa", outline="#e0e0e0", width=1, style='pieslice')
        
        # Fill rectangles for result background
        result_bg_canvas.create_rectangle(radius, 0, 300-radius, 60, fill="#f8f9fa", outline="")
        result_bg_canvas.create_rectangle(0, radius, 300, 60-radius, fill="#f8f9fa", outline="")
        
        # Draw border lines for result background
        result_bg_canvas.create_line(radius, 0, 300-radius, 0, fill="#e0e0e0", width=1)
        result_bg_canvas.create_line(radius, 59, 300-radius, 59, fill="#e0e0e0", width=1)
        result_bg_canvas.create_line(0, radius, 0, 60-radius, fill="#e0e0e0", width=1)
        result_bg_canvas.create_line(299, radius, 299, 60-radius, fill="#e0e0e0", width=1)
        
        self.result_var = tk.StringVar(value="—")
        self.result_display = tk.Label(result_bg_canvas, textvariable=self.result_var,
                                      font=("Segoe UI", 24, "bold"),
                                      fg=RESULT_COLOR, bg="#f8f9fa")
        result_bg_canvas.create_window(150, 30, window=self.result_display)
        
        # Controls section
        controls_frame = tk.Frame(self.card, bg=CARD_BG, bd=0)
        controls_frame.pack(pady=(0, 10))
        
        # Action buttons row
        btn_row = tk.Frame(controls_frame, bg=CARD_BG, bd=0)
        btn_row.pack(pady=(0, 10))
        
        self.start_btn = AnimatedButton(btn_row, 
                                       text="🎙️ شروع",
                                       bg_color=ACCENT_GREEN, 
                                       hover_color="#00d4ff",
                                       command=self.start_recording,
                                       width=110, height=45)
        self.start_btn.pack(side="left", padx=8)
        
        self.stop_btn = AnimatedButton(btn_row, 
                                      text="⏹️ توقف",
                                      bg_color=ACCENT_CORAL, 
                                      hover_color="#ff5252",
                                      command=self.stop_recording,
                                      state="disabled",
                                      width=110, height=45)
        self.stop_btn.pack(side="left", padx=8)
        
        # Copy button (separate)
        self.copy_btn = AnimatedButton(controls_frame, 
                                      text="📋 کپی کردن",
                                      bg_color=ACCENT_PURPLE, 
                                      hover_color="#7986cb",
                                      command=self.copy_result,
                                      state="disabled",
                                      width=160, height=45)
        self.copy_btn.pack()
        
        # Progress section
        progress_section = tk.Frame(self.card, bg=CARD_BG, bd=0)
        progress_section.pack(pady=(5, 0))
        
        # Progress bar container
        self.progress_frame = tk.Frame(progress_section, bg=CARD_BG, bd=0)
        self.progress_canvas = tk.Canvas(self.progress_frame, height=4, width=300,
                                        bg="#e9ecef", highlightthickness=0)
        self.progress_canvas.pack()
        
        # Status text
        self.status_label = tk.Label(progress_section, text="آماده برای ضبط", 
                                    font=("Tahoma", 9),
                                    fg="#6c757d", bg=CARD_BG)
        self.status_label.pack(pady=(8, 0))
        
        # Initialize components
        self.recorder = VoiceRecorder()
        self.recognizer = sr.Recognizer()
        self.audio_queue: "queue.Queue[str]" = queue.Queue()
        
        # Animation state
        self.progress_pos = 0
        self.is_recording = False
        
        self.root.after(100, self._process_queue)
        self.root.after(50, self._animate_progress)

    # ------------- GUI Callbacks -------------
    def start_recording(self):
        self.recorder.start()
        self.start_btn.config_state(tk.DISABLED)
        self.stop_btn.config_state(tk.NORMAL)
        self.result_var.set("در حال ضبط...")
        self.copy_btn.config_state(tk.DISABLED)
        # show progress bar
        self.progress_frame.pack(pady=10)
        self.is_recording = True
        self.status_label.config(text="در حال ضبط...")

    def stop_recording(self):
        audio_data = self.recorder.stop()
        self.start_btn.config_state(tk.NORMAL)
        self.stop_btn.config_state(tk.DISABLED)
        self.is_recording = False  # Stop animation
        if audio_data.size == 0:
            self.result_var.set("صدایی ضبط نشد")
            self.status_label.config(text="آماده برای ضبط")
            return

        # Process audio in separate thread to keep GUI responsive
        threading.Thread(target=self._recognize_thread, args=(audio_data,), daemon=True).start()
        self.result_var.set("در حال پردازش...")
        self.status_label.config(text="در حال پردازش...")

    def copy_result(self):
        text = self.result_var.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # now it stays on the clipboard after the window is closed

    # ------------- Background processing -------------
    def _recognize_thread(self, audio_data: np.ndarray):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                save_wav(tmp.name, audio_data, self.recorder.samplerate)
                tmp_path = tmp.name
            with sr.AudioFile(tmp_path) as source:
                audio = self.recognizer.record(source)
            os.unlink(tmp_path)
            text = self.recognizer.recognize_google(audio, language="fa-IR")
            print("Recognized:", text)
            num_value = extract_digits(text)
            if num_value is None:
                num_value = persian_words_to_number(text)
            self.audio_queue.put(str(num_value))
        except sr.UnknownValueError:
            self.audio_queue.put("متوجه نشدم :(")
        except Exception as e:
            self.audio_queue.put(f"خطا: {e}")

    def _process_queue(self):
        try:
            while True:
                result = self.audio_queue.get_nowait()
                self.result_var.set(result)
                # hide progress bar once we have result
                self.progress_frame.pack_forget()
                self.progress_frame.pack(pady=10) # Re-pack to show it again
                self.status_label.config(text="آماده برای ضبط")
                if result and result[0].isdigit():
                    self.copy_btn.config_state(tk.NORMAL)
                else:
                    self.copy_btn.config_state(tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_queue)

    def _animate_progress(self):
        if self.is_recording:
            self.progress_pos += 2
            if self.progress_pos > 250:
                self.progress_pos = 0
            self.progress_canvas.delete("progress")
            self.progress_canvas.create_rectangle(0, 0, self.progress_pos, 6, fill=GRADIENT_START, outline="", tags="progress")
        else:
            self.progress_canvas.delete("progress")
        self.root.after(50, self._animate_progress)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Instruction: Install dependencies beforehand: pip install SpeechRecognition sounddevice numpy
    App().run() 