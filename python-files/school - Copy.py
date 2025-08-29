"""
NeuroBridge AI — Merged Edition
Neon UI from new.py + Enhanced Functionality from bolt.py
"""

import os
import json
import threading
import time
import io
from typing import List, Tuple, Optional
from datetime import datetime

# Optional dependencies
try:
    import requests
except Exception:
    requests = None

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_OK = True
except Exception:
    PIL_OK = False

try:
    import cv2
except Exception:
    cv2 = None

try:
    from deepface import DeepFace
except Exception:
    DeepFace = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    from googletrans import Translator
except Exception:
    Translator = None

try:
    import numpy as np
except Exception:
    import random
    class _NP:
        @staticmethod
        def random_choice(seq):
            return random.choice(seq)
    np = _NP()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter.scrolledtext import ScrolledText
import tkinter.font as tkfont

from dotenv import load_dotenv

# API Configuration - Support both Google Gemini and OpenAI
load_dotenv()

# Google Gemini API
try:
    import google.generativeai as genai
except Exception:
    genai = None

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

if genai and GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception:
        pass

# OpenAI API (fallback)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if (OpenAI and OPENAI_API_KEY) else None

# ---------------------- Neon Theme Colors ----------------------
NEON_COLORS = {
    # Background colors
    "bg": "#0b0f19",           # Main background
    "panel": "#0f1424",        # Panel background
    "surface": "#1a2035",      # Surface elements
    "elevated": "#1e2442",     # Elevated surfaces
    
    # Text colors
    "text": "#e6f1ff",         # Primary text
    "muted": "#9aa8c7",        # Muted text
    "text_dark": "#001016",    # Dark text for bright backgrounds
    
    # Neon accent colors
    "primary": "#00e5ff",      # Cyan primary
    "secondary": "#39ff14",    # Bright green
    "accent": "#ff00d4",       # Magenta accent
    "purple": "#8A2BE2",       # Purple
    "orange": "#FF6600",       # Orange
    
    # Status colors
    "success": "#00ff7f",      # Success green
    "warning": "#ffd60a",      # Warning yellow
    "danger": "#ff3b3b",       # Error red
    "info": "#00bfff",         # Info blue
    
    # Special elements
    "chip": "#1a2035",         # Chip background
    "glow": "#66f2ff",       # Glow effect
}

# Enhanced visual aids with educational content
ENHANCED_VISUALS = {
    "fractions": "https://images.pexels.com/photos/6238050/pexels-photo-6238050.jpeg?auto=compress&cs=tinysrgb&w=800",
    "emotions": "https://images.pexels.com/photos/4101143/pexels-photo-4101143.jpeg?auto=compress&cs=tinysrgb&w=800",
    "learning": "https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg?auto=compress&cs=tinysrgb&w=800",
    "communication": "https://images.pexels.com/photos/3184460/pexels-photo-3184460.jpeg?auto=compress&cs=tinysrgb&w=800",
    "math": "https://images.pexels.com/photos/3729557/pexels-photo-3729557.jpeg?auto=compress&cs=tinysrgb&w=800",
    "science": "https://images.pexels.com/photos/2280549/pexels-photo-2280549.jpeg?auto=compress&cs=tinysrgb&w=800",
    "reading": "https://images.pexels.com/photos/1370295/pexels-photo-1370295.jpeg?auto=compress&cs=tinysrgb&w=800",
    "social": "https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=800",
}

# ---------------------- Enhanced AI Functions ----------------------
def chatbot_reply(
    prompt: str,
    mode: str,
    emotion: Optional[str],
    history: List[Tuple[str, str]],
    controls: dict
) -> str:
    """Enhanced AI response with multiple API support"""
    
    # Enhanced system prompts for each mode
    mode_prompts = {
        'Autism': """You are NeuroBridge AI, specialized in autism support. 
        - Use calm tone. Break answer into short, numbered steps
        - Avoid idioms and be literal. Provide concrete examples
        - Be patient, understanding, and avoid overwhelming information
        - Use bullet points and structured responses""",
        
        'Dyslexia': """You are NeuroBridge AI, specialized in dyslexia support.
        - Use very short sentences and simple words
        - Break down complex concepts into smaller parts
        - Provide step-by-step explanations with extra spacing
        - Use analogies and visual descriptions""",
        
        'General': """You are NeuroBridge AI, a helpful accessible assistant.
        - Provide clear, inclusive communication
        - Be supportive and encouraging
        - Adapt your communication style to user needs
        - Answer naturally and clearly with examples"""
    }

    system_context = mode_prompts.get(mode, mode_prompts['General'])
    
    # Add emotional context
    if emotion and emotion.lower() != 'none':
        emotion_context = {
            'happy': 'The user seems happy. Match their positive energy while being helpful.',
            'sad': 'The user seems sad. Be extra supportive and gentle in your response.',
            'angry': 'The user seems frustrated. Be calm and understanding, offer solutions.',
            'surprise': 'The user seems surprised. Provide clear explanations.',
            'fear': 'The user seems anxious. Be reassuring and provide comfort.',
            'neutral': 'The user seems calm. Provide balanced, informative responses.'
        }
        system_context += f"\n\nUser's emotional state: {emotion_context.get(emotion.lower(), 'Be supportive.')}"

    # Add control preferences
    if controls.get("speak_slowly"):
        system_context += "\n- Use shorter sentences and simpler language."
    if controls.get("calm_mode"):
        system_context += "\n- Use a calm, reassuring tone with positive language."
    if controls.get("repeat"):
        system_context += "\n- Summarize key points at the end of your response."
    if controls.get("need_break"):
        system_context += "\n- Suggest taking breaks and offer shorter, manageable tasks."

    full_prompt = f"{system_context}\n\nUser: {prompt}"
    
    # Try Google Gemini first
    if genai and GOOGLE_API_KEY:
        try:
            # Build chat history for Gemini
            chat_history = []
            for q, a in history[-10:]:  # Last 10 exchanges for context
                if q:
                    chat_history.append({"role": "user", "parts": [q]})
                if a:
                    chat_history.append({"role": "model", "parts": [a]})
            
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            chat = model.start_chat(history=chat_history)
            
            response = chat.send_message(
                full_prompt,
                generation_config={
                    "max_output_tokens": 500,
                    "temperature": 0.7,
                }
            )
            
            return getattr(response, "text", str(response))
            
        except Exception as e:
            print(f"Gemini API error: {e}")
    
    # Fallback to OpenAI
    if openai_client and OPENAI_MODEL:
        try:
            # Build chat history for OpenAI
            messages = [{"role": "system", "content": system_context}]
            for q, a in history[-10:]:
                if q:
                    messages.append({"role": "user", "content": q})
                if a:
                    messages.append({"role": "assistant", "content": a})
            messages.append({"role": "user", "content": prompt})
            
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
    
    # Final fallback
    return "🤖 AI service temporarily unavailable. Please check your API keys in the .env file."


def detect_emotion_from_frame(frame_bgr) -> Optional[str]:
    """Enhanced emotion detection with better error handling"""
    if frame_bgr is None or DeepFace is None:
        return None
    try:
        result = DeepFace.analyze(
            frame_bgr, 
            actions=["emotion"], 
            enforce_detection=False,
            silent=True
        )
        if isinstance(result, list) and result:
            return result[0].get("dominant_emotion")
        elif isinstance(result, dict):
            return result.get("dominant_emotion")
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return None
    return None


def capture_and_analyze_emotion() -> Optional[str]:
    """Enhanced camera capture with better error handling"""
    if cv2 is None:
        return None
    
    cap = None
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        
        # Warm up camera
        for _ in range(5):
            ret, frame = cap.read()
            if ret:
                break
            time.sleep(0.1)
        
        if ret and frame is not None:
            return detect_emotion_from_frame(frame)
            
    except Exception as e:
        print(f"Camera capture error: {e}")
        return None
    finally:
        if cap:
            cap.release()
    
    return None


def transcribe_voice_blocking(timeout: int = 5) -> Optional[str]:
    """Enhanced speech recognition with better error handling"""
    if sr is None:
        return None
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
        
        return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        return "timeout"
    except sr.UnknownValueError:
        return "unclear"
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return None


# ---------------------- Enhanced UI Components ----------------------
def set_ttk_neon_style(root: tk.Tk):
    """Set up the neon theme styling"""
    style = ttk.Style(root)
    
    # Base theme
    if "clam" in style.theme_names():
        style.theme_use("clam")

    # Configure styles
    style.configure("NeonCard.TFrame", background=NEON_COLORS["panel"], borderwidth=0)
    style.configure("NeonMain.TFrame", background=NEON_COLORS["bg"])
    style.configure("Neon.TLabelframe", background=NEON_COLORS["panel"], foreground=NEON_COLORS["text"])
    style.configure("Neon.TLabelframe.Label", background=NEON_COLORS["panel"], foreground=NEON_COLORS["text"], font=("Segoe UI", 10, "bold"))

    # Button styles
    style.configure("NeonPrimary.TButton",
                    background=NEON_COLORS["primary"],
                    foreground=NEON_COLORS["text_dark"],
                    font=("Segoe UI", 10, "bold"),
                    padding=(16, 10))
    style.map("NeonPrimary.TButton",
              background=[("active", "#66f2ff")])

    style.configure("NeonSecondary.TButton",
                    background=NEON_COLORS["secondary"],
                    foreground=NEON_COLORS["text_dark"],
                    font=("Segoe UI", 10, "bold"),
                    padding=(14, 9))
    style.map("NeonSecondary.TButton",
              background=[("active", "#8cff86")])

    style.configure("NeonAccent.TButton",
                    background=NEON_COLORS["accent"],
                    foreground="#fff",
                    font=("Segoe UI", 10, "bold"),
                    padding=(12, 8))
    style.map("NeonAccent.TButton",
              background=[("active", "#ff66ea")])

    style.configure("NeonDanger.TButton",
                    background=NEON_COLORS["danger"],
                    foreground="#fff",
                    font=("Segoe UI", 10, "bold"),
                    padding=(12, 8))
    style.map("NeonDanger.TButton",
              background=[("active", "#ff6666")])

    # Label styles
    style.configure("Neon.TLabel", background=NEON_COLORS["panel"], foreground=NEON_COLORS["text"])
    style.configure("NeonHeader.TLabel", background=NEON_COLORS["panel"], foreground=NEON_COLORS["primary"], font=("Segoe UI", 20, "bold"))


def neon_glow_label(parent, text, fg=NEON_COLORS["primary"], font=("Segoe UI", 24, "bold")):
    """A label with faux neon glow using stacked shadows"""
    frame = tk.Frame(parent, bg=NEON_COLORS["panel"])
    # Create stacked labels for glow effect
    shadow1 = tk.Label(frame, text=text, font=font, fg=fg, bg=NEON_COLORS["panel"])
    shadow2 = tk.Label(frame, text=text, font=font, fg=fg, bg=NEON_COLORS["panel"])
    main = tk.Label(frame, text=text, font=font, fg=fg, bg=NEON_COLORS["panel"])
    shadow1.place(x=1, y=1)
    shadow2.place(x=2, y=2)
    main.place(x=0, y=0)
    # Adjust frame to fit text
    frame.update_idletasks()
    w = main.winfo_reqwidth() + 4
    h = main.winfo_reqheight() + 4
    frame.config(width=w, height=h)
    return frame


def rounded_rect_on_canvas(c: tk.Canvas, x1, y1, x2, y2, r=16, **kwargs):
    """Draw rounded rectangle on canvas"""
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1, x2, y1+r,
        x2, y2-r,
        x2, y2, x2-r, y2,
        x1+r, y2,
        x1, y2, x1, y2-r,
        x1, y1+r,
        x1, y1, x1+r, y1
    ]
    return c.create_polygon(points, smooth=True, **kwargs)


class NeonChatWindow(tk.Frame):
    """Enhanced scrollable neon chat bubble window"""
    def __init__(self, parent, *, bg=NEON_COLORS["bg"]):
        super().__init__(parent, bg=bg)

        self.canvas = tk.Canvas(self, bg=NEON_COLORS["panel"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=NEON_COLORS["panel"])

        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_w)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.bubble_max_width = 680
        self.message_history = []  # Store messages for TTS

    def _on_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_w(self, event):
        self.canvas.itemconfig(self.inner_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_bubble(self, text: str, role: str = "assistant", animate: bool = False):
        """Enhanced bubble with timestamps and animations"""
        # Store message for history
        self.message_history.append((text, role, datetime.now()))
        
        # Wrapper frame
        row = tk.Frame(self.inner, bg=NEON_COLORS["panel"])
        row.pack(fill="x", pady=6, padx=8, anchor="w")

        align = "w" if role == "assistant" else "e"
        
        # Bubble colors and styling
        if role == "assistant":
            neon = NEON_COLORS["primary"]
            text_fg = NEON_COLORS["text"]
            bubble_bg = "#0c1b26"
            emoji = "🤖"
        elif role == "user":
            neon = NEON_COLORS["accent"]
            text_fg = "#fff0ff"
            bubble_bg = "#1d0e1d"
            emoji = "👤"
        else:  # system
            neon = NEON_COLORS["warning"]
            text_fg = NEON_COLORS["text"]
            bubble_bg = "#1d1a0e"
            emoji = "⚙️"

        # Create bubble container with timestamp
        bubble_container = tk.Frame(row, bg=NEON_COLORS["panel"])
        bubble_container.pack(anchor=align, padx=4)

        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        time_label = tk.Label(
            bubble_container,
            text=f"{emoji} {timestamp}",
            bg=NEON_COLORS["panel"],
            fg=NEON_COLORS["muted"],
            font=("Segoe UI", 8)
        )
        time_label.pack(anchor=align)

        # Bubble canvas
        c = tk.Canvas(bubble_container, bg=NEON_COLORS["panel"], highlightthickness=0, width=self.bubble_max_width, height=10)
        c.pack(anchor=align, pady=(2, 0))

        # Compute text dimensions
        temp = tk.Label(c, text=text, font=("Segoe UI", 11), wraplength=self.bubble_max_width-40, justify="left")
        temp.update_idletasks()
        text_w = min(self.bubble_max_width-40, temp.winfo_reqwidth())
        text_h = temp.winfo_reqheight()
        bubble_w = text_w + 40
        bubble_h = text_h + 24

        c.config(width=bubble_w+6, height=bubble_h+6)

        # Draw glow layers for neon effect
        for pad, outline in [(2, "#66f2ff"), (1, "#99f7ff"), (0, neon)]:
            rounded_rect_on_canvas(c, 3+pad, 3+pad, 3+pad + bubble_w, 3+pad + bubble_h,
                                   r=16, fill=bubble_bg if pad==0 else "",
                                   outline=outline, width=1 if pad else 2)

        # Place text (typing effect if animate=True)
        if animate and role == "assistant":
            text_item = c.create_text(
                3+20, 3+12, text="", anchor="nw", fill=text_fg,
                font=("Segoe UI", 11), width=text_w
            )

            def type_char(i=0):
                if i <= len(text):
                    c.itemconfig(text_item, text=text[:i])
                    self.canvas.update_idletasks()
                    self.canvas.yview_moveto(1.0)
                    if i < len(text):  # ✅ stop after last char
                        c.after(25, lambda: type_char(i+1))

            type_char()
        else:
            c.create_text(3+20, 3+12, text=text, anchor="nw", fill=text_fg,
                          font=("Segoe UI", 11), width=text_w)

        # Auto-scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last assistant message for TTS"""
        for text, role, timestamp in reversed(self.message_history):
            if role == "assistant":
                return text
        return None

    def clear_messages(self):
        """Clear all messages"""
        for w in self.inner.winfo_children():
            w.destroy()
        self.message_history.clear()


# ---------------------- Main Application ----------------------
class NeuroBridgeGUI:
    """Enhanced NeuroBridge GUI with merged functionality"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧠 NeuroBridge AI — Enhanced Neon Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg=NEON_COLORS["bg"])
        set_ttk_neon_style(self.root)

        # Enhanced state management
        self.current_mode = tk.StringVar(self.root, value="Autism")
        self.detected_emotion = tk.StringVar(self.root, value="None")
        self.user_input = tk.StringVar(self.root)
        self.show_translation = tk.BooleanVar(self.root, value=False)
        self.font_size = tk.IntVar(self.root, value=12)
        self.is_listening = tk.BooleanVar(self.root, value=False)
        
        # Advanced controls from bolt.py
        self.controls = {
            "need_break": tk.BooleanVar(self.root, value=False),
            "speak_slowly": tk.BooleanVar(self.root, value=False),
            "repeat": tk.BooleanVar(self.root, value=False),
            "calm_mode": tk.BooleanVar(self.root, value=False)
        }
        
        # Conversation history
        self.history: List[Tuple[str, str]] = []
        self.emotion_history = []
        
        # UI state
        self.loading_id = None
        
        self._build_layout()
        self._center_window()

    def _build_layout(self):
        """Build the enhanced UI layout"""
        # Main container
        outer = ttk.Frame(self.root, style="NeonMain.TFrame")
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        # Enhanced header
        self._build_enhanced_header(outer)

        # Main content area
        content = ttk.Frame(outer, style="NeonMain.TFrame")
        content.pack(fill="both", expand=True, pady=(14, 0))

        # Left sidebar
        self._build_enhanced_sidebar(content)
        
        # Main chat area
        self._build_enhanced_main(content)

    def _build_enhanced_header(self, parent):
        """Enhanced header with more features"""
        header = ttk.Frame(parent, style="NeonCard.TFrame")
        header.pack(fill="x", pady=(0, 14))

        # Left side - branding
        left = ttk.Frame(header, style="NeonCard.TFrame")
        left.pack(side="left", padx=15, pady=15)

        title_glow = neon_glow_label(left, "🧠 NeuroBridge AI", fg=NEON_COLORS["primary"], font=("Segoe UI", 28, "bold"))
        title_glow.pack(anchor="w")

        subtitle = ttk.Label(left, text="Enhanced Assistive Learning Companion • Neon Edition", 
                           style="Neon.TLabel", foreground=NEON_COLORS["muted"])
        subtitle.pack(anchor="w", pady=(8, 0))

        # Status indicators
        status_frame = tk.Frame(left, bg=NEON_COLORS["panel"])
        status_frame.pack(anchor="w", pady=(8, 0))

        # API status
        api_status = "🟢 Connected" if (GOOGLE_API_KEY or OPENAI_API_KEY) else "🔴 No API"
        api_color = NEON_COLORS["success"] if (GOOGLE_API_KEY or OPENAI_API_KEY) else NEON_COLORS["danger"]
        
        tk.Label(status_frame, text=api_status, bg=NEON_COLORS["panel"], fg=api_color, 
                font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 15))

        # Conversation count
        tk.Label(status_frame, text=f"💬 Conversations: {len(self.history)}", 
                bg=NEON_COLORS["panel"], fg=NEON_COLORS["muted"], 
                font=("Segoe UI", 9)).pack(side="left")

        # Right side - controls
        right = ttk.Frame(header, style="NeonCard.TFrame")
        right.pack(side="right", padx=15, pady=15)

        # Quick actions
        actions_frame = tk.Frame(right, bg=NEON_COLORS["panel"])
        actions_frame.pack()

        quick_actions = [
            ("💾 Export", self.export_conversation, NEON_COLORS["secondary"]),
            ("📁 Load", self.load_profile, NEON_COLORS["primary"]),
            ("⚙️ Settings", self.show_settings, NEON_COLORS["warning"])
        ]

        for text, command, color in quick_actions:
            btn = tk.Button(actions_frame, text=text, fg="#001", bg=color, 
                          font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6,
                          activebackground=color, command=command)
            btn.pack(side="left", padx=2)

    def _build_enhanced_sidebar(self, parent):
        """Enhanced sidebar with more controls"""
        side = ttk.Frame(parent, style="NeonCard.TFrame")
        side.pack(side="left", fill="y", padx=(0, 16), ipadx=10, ipady=10)

        # Mode selector with descriptions
        modes = ttk.LabelFrame(side, text="🎯 Support Mode", style="Neon.TLabelframe", padding=15)
        modes.pack(fill="x", pady=(0, 15))

        mode_configs = [
            ("Autism", "🧩 Clear, step-by-step guidance\nStructured responses with examples", NEON_COLORS["primary"]),
            ("Dyslexia", "📖 Simple words, short sentences\nExtra spacing and visual aids", NEON_COLORS["secondary"]),
            ("General", "💬 Natural, adaptive responses\nFlexible communication style", NEON_COLORS["accent"]),
        ]

        for mode, desc, color in mode_configs:
            rb = tk.Radiobutton(modes, text=f"{mode}\n{desc}",
                                variable=self.current_mode, value=mode,
                                bg=NEON_COLORS["panel"], fg=color,
                                selectcolor=color, justify="left", 
                                font=("Segoe UI", 10), wraplength=220,
                                command=self._on_mode_change)
            rb.pack(fill="x", pady=6, anchor="w")

        # Enhanced emotion section
        emo = ttk.LabelFrame(side, text="😊 Emotion Analysis", style="Neon.TLabelframe", padding=15)
        emo.pack(fill="x", pady=(0, 15))

        self.emotion_display = tk.Label(emo, text="No emotion detected", 
                                       bg=NEON_COLORS["surface"], fg=NEON_COLORS["muted"],
                                       font=("Segoe UI", 10, "bold"), padx=15, pady=12, 
                                       relief="flat", bd=2)
        self.emotion_display.pack(fill="x", pady=(0, 10))

        # Emotion buttons
        emo_btn_frame = tk.Frame(emo, bg=NEON_COLORS["panel"])
        emo_btn_frame.pack(fill="x")

        ttk.Button(emo_btn_frame, text="📷 Real Analysis", style="NeonSecondary.TButton",
                   command=self.real_emotion_detection).pack(fill="x", pady=(0, 5))
        
        ttk.Button(emo_btn_frame, text="🎲 Simulate", style="NeonAccent.TButton",
                   command=self.simulate_emotion_detection).pack(fill="x")

        # Advanced controls
        controls = ttk.LabelFrame(side, text="🎛️ Advanced Controls", style="Neon.TLabelframe", padding=15)
        controls.pack(fill="x", pady=(0, 15))

        control_configs = [
            ("need_break", "⏸️ Need Break", NEON_COLORS["danger"]),
            ("speak_slowly", "🐌 Speak Slowly", NEON_COLORS["warning"]),
            ("repeat", "🔄 Repeat Info", NEON_COLORS["info"]),
            ("calm_mode", "😌 Calm Mode", NEON_COLORS["secondary"])
        ]

        for key, label, color in control_configs:
            cb = tk.Checkbutton(controls, text=label, variable=self.controls[key],
                               bg=NEON_COLORS["panel"], fg=color, 
                               selectcolor=color, font=("Segoe UI", 10))
            cb.pack(anchor="w", pady=2)

        # Quick Settings
        settings = ttk.LabelFrame(side, text="⚙️ Settings", style="Neon.TLabelframe", padding=15)
        settings.pack(fill="x")

        # Font size
        tk.Label(settings, text="Font Size", bg=NEON_COLORS["panel"], fg=NEON_COLORS["text"]).pack(anchor="w")
        scale = tk.Scale(settings, from_=10, to=22, orient="horizontal", variable=self.font_size,
                         bg=NEON_COLORS["panel"], fg=NEON_COLORS["text"], troughcolor=NEON_COLORS["surface"],
                         highlightthickness=0, command=self._update_font_size)
        scale.pack(fill="x", pady=(0, 10))

        # Translation toggle
        tk.Checkbutton(settings, text="🌐 Show Hindi Translation", variable=self.show_translation,
                       bg=NEON_COLORS["panel"], fg=NEON_COLORS["text"], 
                       selectcolor=NEON_COLORS["secondary"]).pack(anchor="w")

    def _build_enhanced_main(self, parent):
        """Enhanced main chat area"""
        main = ttk.Frame(parent, style="NeonMain.TFrame")
        main.pack(side="right", fill="both", expand=True)

        # Enhanced input section
        input_section = ttk.LabelFrame(main, text="💬 Ask Anything", style="Neon.TLabelframe", padding=15)
        input_section.pack(fill="x")

        # Input row
        input_row = tk.Frame(input_section, bg=NEON_COLORS["panel"])
        input_row.pack(fill="x")

        # Enhanced text entry
        self.entry = tk.Text(input_row, height=3, wrap=tk.WORD,
                           bg=NEON_COLORS["surface"], fg=NEON_COLORS["text"],
                           insertbackground=NEON_COLORS["primary"],
                           font=("Segoe UI", 12), relief="flat", bd=2,
                           selectbackground=NEON_COLORS["primary"])
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Control buttons
        btn_frame = tk.Frame(input_row, bg=NEON_COLORS["panel"])
        btn_frame.pack(side="right")

        # Voice button
        self.voice_btn = tk.Button(btn_frame, text="🎤" if not self.is_listening.get() else "⏹️",
                                  bg=NEON_COLORS["secondary"] if not self.is_listening.get() else NEON_COLORS["danger"],
                                  fg=NEON_COLORS["text_dark"], font=("Segoe UI", 12, "bold"),
                                  bd=0, padx=15, pady=10, command=self.toggle_voice)
        self.voice_btn.pack(fill="x", pady=(0, 5))

        # Send button
        send_btn = tk.Button(btn_frame, text="🚀 Send", 
                           bg=NEON_COLORS["primary"], fg=NEON_COLORS["text_dark"],
                           font=("Segoe UI", 12, "bold"), bd=0, padx=15, pady=10,
                           command=self.generate_response)
        send_btn.pack(fill="x")

        # Bind Enter key
        self.entry.bind('<Control-Return>', lambda e: self.generate_response())

        # Enhanced quick actions
        actions_section = ttk.LabelFrame(main, text="⚡ Quick Actions", style="Neon.TLabelframe", padding=15)
        actions_section.pack(fill="x", pady=(15, 0))

        actions_grid = tk.Frame(actions_section, bg=NEON_COLORS["panel"])
        actions_grid.pack(fill="x")

        quick_actions = [
            ("⏸️ I need a break", self._quick_break, NEON_COLORS["danger"]),
            ("🔊 Speak slower", self._quick_slow, NEON_COLORS["warning"]),
            ("🔄 Repeat that", self._quick_repeat, NEON_COLORS["info"]),
            ("😌 Calm mode", self._quick_calm, NEON_COLORS["secondary"]),
        ]

        for i, (label, command, color) in enumerate(quick_actions):
            btn = tk.Button(actions_grid, text=label, fg=NEON_COLORS["text_dark"], bg=color,
                          font=("Segoe UI", 10, "bold"), bd=0, padx=12, pady=8,
                          command=command)
            btn.grid(row=0, column=i, sticky="ew", padx=3)
            actions_grid.grid_columnconfigure(i, weight=1)

        # Enhanced chat window
        chat_section = ttk.LabelFrame(main, text=" Neuro Response ", style="Neon.TLabelframe", padding=10)
        chat_section.pack(fill="both", expand=True, pady=(15, 0))

        self.chat = NeonChatWindow(chat_section)
        self.chat.pack(fill="both", expand=True)

        # Enhanced bottom controls
        controls_section = tk.Frame(main, bg=NEON_COLORS["bg"])
        controls_section.pack(fill="x", pady=(10, 0))

        # Left controls
        left_controls = tk.Frame(controls_section, bg=NEON_COLORS["bg"])
        left_controls.pack(side="left")

        control_buttons = [
            ("🔊 Speak Response", self.speak_response, "NeonSecondary.TButton"),
            ("🖼️ Visual Aid", self.show_visual_aid, "NeonAccent.TButton"),
            ("📊 Emotion History", self.show_emotion_history, "NeonPrimary.TButton")
        ]

        for text, command, style in control_buttons:
            ttk.Button(left_controls, text=text, style=style, command=command).pack(side="left", padx=5)

        # Right controls
        right_controls = tk.Frame(controls_section, bg=NEON_COLORS["bg"])
        right_controls.pack(side="right")

        ttk.Button(right_controls, text="🗑️ Clear Chat", style="NeonDanger.TButton", 
                   command=self.clear_chat).pack(side="right", padx=5)

        # Initial greeting
        self.chat.add_bubble("🌟 Welcome to NeuroBridge AI Enhanced Edition! I'm your intelligent assistant specialized in accessible learning. Choose a support mode and ask me anything!", "assistant")

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")

    # ---------------------- Event Handlers ----------------------
    def _on_mode_change(self):
        """Handle mode change"""
        mode = self.current_mode.get()
        mode_messages = {
            "Autism": "🧩 Autism support mode activated. I'll provide clear, structured responses with concrete examples.",
            "Dyslexia": "📖 Dyslexia support mode activated. I'll use simple words and short sentences with extra clarity.",
            "General": "💬 General mode activated. I'll provide natural, adaptive responses based on your needs."
        }
        self.chat.add_bubble(mode_messages.get(mode, f"Mode switched to {mode}"), "system")

    def _update_font_size(self, _):
        """Update font size"""
        size = self.font_size.get()
        self.chat.add_bubble(f"⚙️ Font size updated to {size}pt. This applies to new messages.", "system")

    def toggle_voice(self):
        """Enhanced voice input toggle"""
        if self.is_listening.get():
            self.is_listening.set(False)
            self.voice_btn.config(text="🎤", bg=NEON_COLORS["secondary"])
            self.chat.add_bubble("🔇 Voice input stopped.", "system")
        else:
            if sr is None:
                messagebox.showerror("Voice Input", "Speech recognition not available. Please install speech_recognition library.")
                return
            
            self.is_listening.set(True)
            self.voice_btn.config(text="⏹️", bg=NEON_COLORS["danger"])
            self.chat.add_bubble("🎤 Listening... Please speak now.", "system")
            threading.Thread(target=self._process_voice_input, daemon=True).start()

    def _process_voice_input(self):
        """Process real voice input"""
        try:
            result = transcribe_voice_blocking(timeout=8)
            
            if result == "timeout":
                self.chat.add_bubble("⏰ Listening timeout - please try again.", "system")
            elif result == "unclear":
                self.chat.add_bubble("🤔 Couldn't understand - please try again or speak more clearly.", "system")
            elif result:
                # Set the recognized text and process it
                self.root.after(0, lambda: self.entry.insert("1.0", result))
                self.chat.add_bubble(f"🎤 Heard: {result}", "user")
                # Auto-generate response
                self.root.after(100, self.generate_response)
            else:
                self.chat.add_bubble("❌ Speech recognition failed. Please try again.", "system")
                
        except Exception as e:
            self.chat.add_bubble(f"❌ Voice input error: {str(e)}", "system")
        
        finally:
            self.is_listening.set(False)
            self.root.after(0, lambda: self.voice_btn.config(text="🎤", bg=NEON_COLORS["secondary"]))

    # Quick action handlers
    def _quick_break(self):
        self.controls["need_break"].set(True)
        self.chat.add_bubble("⏸️ Break time activated. Taking breaks helps your brain reset and process information better. When you're ready, we'll continue together. 🌿", "assistant")

    def _quick_slow(self):
        self.controls["speak_slowly"].set(True)
        self.chat.add_bubble("🐌 Slow mode activated. I'll use shorter sentences and give you more time to process information. ✅", "assistant")

    def _quick_repeat(self):
        self.controls["repeat"].set(True)
        last_msg = self.chat.get_last_assistant_message()
        if last_msg:
            self.chat.add_bubble(f"🔄 Repeating last response:\n\n{last_msg}", "assistant")
        else:
            self.chat.add_bubble("🔄 No previous message to repeat. Ask me something first!", "assistant")

    def _quick_calm(self):
        self.controls["calm_mode"].set(True)
        self.chat.add_bubble("😌 Calm mode activated. Take a deep breath... You're doing great, and I'm here to support you every step of the way. 💚", "assistant")

    # ---------------------- AI Response Generation ----------------------
    def generate_response(self):
        """Enhanced response generation"""
        user_text = self.entry.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showwarning("Input Required", "Please enter a question or message first.")
            return

        # Clear input
        self.entry.delete("1.0", tk.END)
        
        # Add user message
        self.chat.add_bubble(user_text, "user")
        
        # Show loading
        loading_msg = "🧠 Thinking..."
        self.chat.add_bubble(loading_msg, "assistant")

        def generate():
            try:
                # Get control states
                controls = {key: var.get() for key, var in self.controls.items()}
                
                # Generate response
                reply = chatbot_reply(
                    user_text,
                    self.current_mode.get(),
                    self.detected_emotion.get(),
                    self.history,
                    controls
                )
                
                # Add emotion context if detected
                emotion = self.detected_emotion.get()
                if emotion and emotion.lower() != 'none':
                    emotion_prefixes = {
                        'happy': "😊 I can sense your positive energy! ",
                        'sad': "💙 I'm here to support you. ",
                        'angry': "🕊️ Let's work through this calmly. ",
                        'fear': "🛡️ You're in a safe space to learn. ",
                        'surprise': "✨ I love your curiosity! ",
                        'neutral': "👍 "
                    }
                    prefix = emotion_prefixes.get(emotion.lower(), "")
                    reply = prefix + reply

                # Add translation if enabled
                if self.show_translation.get():
                    translation = self._translate_hindi(reply)
                    if translation:
                        reply += translation

                # Update history
                self.history.append((user_text, reply))
                
                # Add response (this will replace the loading message in UI)
                self.root.after(0, lambda: self.chat.add_bubble(reply, "assistant", animate=True))
                
            except Exception as e:
                error_msg = f"❌ Error generating response: {str(e)}"
                self.root.after(0, lambda: self.chat.add_bubble(error_msg, "system"))

        threading.Thread(target=generate, daemon=True).start()

    def _translate_hindi(self, text: str) -> str:
        """Translate text to Hindi"""
        if not Translator:
            return "\n\n🌐 (Hindi translation unavailable: googletrans not installed)"
        
        try:
            translator = Translator()
            result = translator.translate(text, dest="hi")
            return f"\n\n🌐 हिंदी अनुवाद:\n{result.text}"
        except Exception:
            return "\n\n🌐 (Translation failed)"

    # ---------------------- Emotion Detection ----------------------
    def simulate_emotion_detection(self):
        """Simulate emotion detection"""
        self.emotion_display.config(text="🔄 Analyzing...", bg="#2a1a00", fg=NEON_COLORS["warning"])
        self.root.update()

        def detect():
            time.sleep(1.5)
            emotions = ["happy", "sad", "angry", "surprise", "neutral", "fear"]
            try:
                emotion = np.random_choice(emotions) if hasattr(np, "random") else emotions[0]
            except Exception:
                emotion = emotions[0]

            self._update_emotion_display(emotion)
            self.detected_emotion.set(emotion)
            
            # Add to emotion history
            self.emotion_history.append((emotion, datetime.now()))
            
            self.chat.add_bubble(f"😊 Simulated emotion detected: {emotion.title()}. I'll adapt my responses accordingly.", "system")

        threading.Thread(target=detect, daemon=True).start()

    def real_emotion_detection(self):
        """Real camera-based emotion detection"""
        if cv2 is None or DeepFace is None:
            messagebox.showerror("Emotion Detection", 
                               "Real emotion detection requires OpenCV and DeepFace libraries.\n\n" +
                               "Install with: pip install opencv-python deepface")
            return

        self.emotion_display.config(text="📷 Accessing camera...", bg="#1a0d26", fg=NEON_COLORS["accent"])
        self.chat.add_bubble("📷 Analyzing your emotion using camera... Please look at the camera.", "system")

        def detect():
            try:
                emotion = capture_and_analyze_emotion()
                
                if emotion:
                    self._update_emotion_display(emotion)
                    self.detected_emotion.set(emotion)
                    self.emotion_history.append((emotion, datetime.now()))
                    
                    emotion_responses = {
                        'happy': "😊 Wonderful! Your positive energy is contagious!",
                        'sad': "💙 I can see you might be feeling down. I'm here to help brighten your day.",
                        'angry': "🕊️ I notice some frustration. Let's work through this together calmly.",
                        'surprise': "😲 You look surprised! Ready to explore something new?",
                        'fear': "🛡️ I can sense some anxiety. Remember, this is a safe space to learn and grow.",
                        'neutral': "😐 You seem focused and ready to learn. Perfect!",
                        'disgust': "😖 Let's find a better approach that works for you."
                    }
                    
                    response = emotion_responses.get(emotion, f"I detected that you're feeling {emotion}.")
                    self.root.after(0, lambda: self.chat.add_bubble(f"📊 {response}", "system"))
                else:
                    self.root.after(0, lambda: [
                        self.emotion_display.config(text="❌ Detection failed", bg="#2a1515", fg=NEON_COLORS["danger"]),
                        self.chat.add_bubble("❌ Couldn't detect emotion. Please ensure good lighting and look at the camera.", "system")
                    ])
                    
            except Exception as e:
                self.root.after(0, lambda: [
                    self.emotion_display.config(text="❌ Camera error", bg="#2a1515", fg=NEON_COLORS["danger"]),
                    self.chat.add_bubble(f"❌ Camera error: {str(e)}", "system")
                ])

        threading.Thread(target=detect, daemon=True).start()

    def _update_emotion_display(self, emotion: str):
        """Update emotion display with colors"""
        emotion_configs = {
            "happy": ("😊 Feeling Happy", "#052018", NEON_COLORS["success"]),
            "sad": ("😢 Feeling Sad", "#181c2a", "#8aa0ff"),
            "angry": ("😠 Feeling Frustrated", "#2a1515", NEON_COLORS["danger"]),
            "surprise": ("😲 Feeling Surprised", "#1a1a2a", "#b19cff"),
            "neutral": ("😐 Neutral", "#0e162a", NEON_COLORS["muted"]),
            "fear": ("😨 Feeling Anxious", "#1a0f1a", "#ff9bf2"),
            "disgust": ("😖 Feeling Uncomfortable", "#1a1a0f", "#ffcc99")
        }
        
        config = emotion_configs.get(emotion, ("😐 Unknown", NEON_COLORS["surface"], NEON_COLORS["muted"]))
        self.emotion_display.config(text=config[0], bg=config[1], fg=config[2])

    # ---------------------- Audio Features ----------------------
    def speak_response(self):
        """Enhanced text-to-speech"""
        if pyttsx3 is None:
            messagebox.showerror("Text-to-Speech", "TTS not available. Please install pyttsx3 library.")
            return

        last_text = self.chat.get_last_assistant_message()
        if not last_text:
            messagebox.showwarning("TTS", "No assistant message to speak.")
            return

        self.chat.add_bubble("🔊 Reading response aloud...", "system")

        def speak():
            try:
                engine = pyttsx3.init()
                
                # Enhanced voice settings for accessibility
                voices = engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break

                # Adjust rate based on controls
                rate = 140 if self.controls["speak_slowly"].get() else 165
                engine.setProperty("rate", rate)
                engine.setProperty("volume", 0.9)
                
                engine.say(last_text)
                engine.runAndWait()
                
                self.root.after(0, lambda: self.chat.add_bubble("✅ Finished reading response.", "system"))
                
            except Exception as e:
                self.root.after(0, lambda: self.chat.add_bubble(f"❌ TTS error: {str(e)}", "system"))

        threading.Thread(target=speak, daemon=True).start()

    # ---------------------- Visual Aids ----------------------
    def show_visual_aid(self):
        """Enhanced visual aid with real images"""
        topic = self.entry.get("1.0", tk.END).strip() or "learning"
        
        # Create visual aid window
        visual_window = tk.Toplevel(self.root)
        visual_window.title(f"🖼️ Visual Learning Aid - {topic.title()}")
        visual_window.configure(bg=NEON_COLORS["bg"])
        visual_window.geometry("900x700")
        
        # Center window
        visual_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 900) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 700) // 2
        visual_window.geometry(f"900x700+{x}+{y}")

        # Header
        header = tk.Frame(visual_window, bg=NEON_COLORS["panel"])
        header.pack(fill="x", padx=15, pady=15)

        title_glow = neon_glow_label(header, f"🖼️ Visual Aid - {topic.title()}", 
                                   fg=NEON_COLORS["accent"], font=("Segoe UI", 18, "bold"))
        title_glow.pack()

        # Content area
        content = tk.Frame(visual_window, bg=NEON_COLORS["panel"])
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Check if we have a specific visual for this topic
        visual_url = None
        topic_lower = topic.lower()
        for key, url in ENHANCED_VISUALS.items():
            if key in topic_lower or topic_lower in key:
                visual_url = url
                break

        if visual_url and requests:
            # Load real image
            loading_label = tk.Label(content, text="🔄 Loading visual aid...",
                                   bg=NEON_COLORS["panel"], fg=NEON_COLORS["primary"],
                                   font=("Segoe UI", 14))
            loading_label.pack(expand=True)

            def load_image():
                try:
                    response = requests.get(visual_url, timeout=10)
                    response.raise_for_status()
                    
                    if PIL_OK:
                        img = Image.open(io.BytesIO(response.content)).convert("RGB")
                        img.thumbnail((850, 500))
                        photo = ImageTk.PhotoImage(img)
                        
                        visual_window.after(0, lambda: [
                            loading_label.destroy(),
                            self._show_image_content(content, photo, topic, visual_window)
                        ])
                    else:
                        visual_window.after(0, lambda: [
                            loading_label.destroy(),
                            self._show_fallback_visual(content, topic, visual_window)
                        ])
                        
                except Exception as e:
                    visual_window.after(0, lambda: [
                        loading_label.destroy(),
                        self._show_error_visual(content, str(e), visual_window)
                    ])

            threading.Thread(target=load_image, daemon=True).start()
        else:
            # Show interactive diagram
            self._show_fallback_visual(content, topic, visual_window)

        # Close button
        ttk.Button(visual_window, text="❌ Close", style="NeonDanger.TButton", 
                   command=visual_window.destroy).pack(pady=15)

    def _show_image_content(self, parent, photo, topic, window):
        """Display loaded image"""
        image_label = tk.Label(parent, image=photo, bg=NEON_COLORS["panel"])
        image_label.image = photo  # Keep reference
        image_label.pack(expand=True, pady=20)

        info_label = tk.Label(parent, text=f"📊 Visual learning aid for: {topic.title()}",
                             bg=NEON_COLORS["panel"], fg=NEON_COLORS["muted"],
                             font=("Segoe UI", 12))
        info_label.pack(pady=10)

    def _show_fallback_visual(self, parent, topic, window):
        """Show interactive diagram fallback"""
        canvas = tk.Canvas(parent, bg=NEON_COLORS["surface"], highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # Draw interactive concept map
        self._draw_concept_map(canvas, topic)

        instruction = tk.Label(parent, 
                             text="💡 Interactive concept visualization. Click elements for more details!",
                             bg=NEON_COLORS["panel"], fg=NEON_COLORS["info"],
                             font=("Segoe UI", 11))
        instruction.pack(pady=10)

    def _show_error_visual(self, parent, error, window):
        """Show error message"""
        error_label = tk.Label(parent, 
                              text=f"❌ Failed to load visual aid:\n{error}\n\nShowing fallback diagram instead...",
                              bg=NEON_COLORS["panel"], fg=NEON_COLORS["danger"],
                              font=("Segoe UI", 12), justify="center")
        error_label.pack(expand=True)

    def _draw_concept_map(self, canvas, topic):
        """Draw an interactive concept map"""
        # Main concept
        rounded_rect_on_canvas(canvas, 350, 50, 550, 120, r=20, 
                              fill=NEON_COLORS["surface"], outline=NEON_COLORS["primary"], width=3)
        canvas.create_text(450, 85, text=topic.title(), fill=NEON_COLORS["text"], 
                          font=("Segoe UI", 14, "bold"))

        # Related concepts
        concepts = [
            ("Understanding", 100, 200, NEON_COLORS["secondary"]),
            ("Practice", 300, 300, NEON_COLORS["accent"]),
            ("Application", 600, 300, NEON_COLORS["warning"]),
            ("Mastery", 800, 200, NEON_COLORS["success"])
        ]

        for concept, x, y, color in concepts:
            # Draw concept bubble
            rounded_rect_on_canvas(canvas, x-60, y-25, x+60, y+25, r=15,
                                  fill=NEON_COLORS["surface"], outline=color, width=2)
            canvas.create_text(x, y, text=concept, fill=NEON_COLORS["text"], 
                              font=("Segoe UI", 11, "bold"))
            
            # Draw connection line
            canvas.create_line(450, 120, x, y-25, fill=color, width=2, arrow=tk.LAST)

        # Add click bindings for interactivity
        def on_click(event):
            item = canvas.find_closest(event.x, event.y)[0]
            canvas.create_text(event.x, event.y-30, text="💡 Click!", 
                              fill=NEON_COLORS["info"], font=("Segoe UI", 10))
            canvas.after(2000, lambda: canvas.delete(item))

        canvas.bind("<Button-1>", on_click)

    # ---------------------- File Operations ----------------------
    def export_conversation(self):
        """Enhanced conversation export"""
        if not self.history:
            messagebox.showinfo("Export", "No conversation history to export.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Conversation History"
            )
            
            if not filename:
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if filename.endswith('.json'):
                # Export as JSON
                export_data = {
                    "export_info": {
                        "timestamp": timestamp,
                        "mode": self.current_mode.get(),
                        "emotion": self.detected_emotion.get(),
                        "total_conversations": len(self.history)
                    },
                    "conversations": [
                        {"question": q, "answer": a, "index": i+1} 
                        for i, (q, a) in enumerate(self.history)
                    ],
                    "emotion_history": [
                        {"emotion": e, "timestamp": t.isoformat()} 
                        for e, t in self.emotion_history
                    ]
                }
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                # Export as text
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("🧠 NeuroBridge AI - Enhanced Conversation Export\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Export Date: {timestamp}\n")
                    f.write(f"Support Mode: {self.current_mode.get()}\n")
                    f.write(f"Current Emotion: {self.detected_emotion.get()}\n")
                    f.write(f"Total Conversations: {len(self.history)}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for i, (question, answer) in enumerate(self.history, 1):
                        f.write(f"Conversation {i}:\n")
                        f.write(f"👤 You: {question}\n")
                        f.write(f"🤖 NeuroBridge: {answer}\n")
                        f.write("-" * 40 + "\n\n")
                    
                    if self.emotion_history:
                        f.write("\n📊 Emotion History:\n")
                        f.write("-" * 20 + "\n")
                        for emotion, timestamp in self.emotion_history:
                            f.write(f"• {emotion.title()} - {timestamp.strftime('%H:%M:%S')}\n")

            messagebox.showinfo("Export Complete", f"Conversation exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export conversation:\n{str(e)}")

    def load_profile(self):
        """Enhanced profile loading"""
        try:
            filename = filedialog.askopenfilename(
                title="Load NeuroBridge Profile",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not filename:
                return

            with open(filename, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            # Load settings
            if "mode" in profile_data:
                self.current_mode.set(profile_data["mode"])
            
            if "last_emotion" in profile_data:
                emotion = profile_data["last_emotion"]
                self.detected_emotion.set(emotion)
                self._update_emotion_display(emotion.lower())
            
            if "font_size" in profile_data:
                self.font_size.set(profile_data["font_size"])
            
            if "show_translation" in profile_data:
                self.show_translation.set(profile_data["show_translation"])

            # Load control states if available
            if "controls" in profile_data:
                for key, value in profile_data["controls"].items():
                    if key in self.controls:
                        self.controls[key].set(value)

            messagebox.showinfo("Profile Loaded", f"Successfully loaded profile from:\n{os.path.basename(filename)}")
            self.chat.add_bubble(f"📁 Profile loaded: {os.path.basename(filename)}", "system")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load profile:\n{str(e)}")

    def show_settings(self):
        """Enhanced settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ NeuroBridge Settings")
        settings_window.configure(bg=NEON_COLORS["bg"])
        settings_window.geometry("700x600")
        
        # Center window
        settings_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 700) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 600) // 2
        settings_window.geometry(f"700x600+{x}+{y}")

        # Header
        header = tk.Frame(settings_window, bg=NEON_COLORS["panel"])
        header.pack(fill="x", padx=20, pady=20)

        title_glow = neon_glow_label(header, "⚙️ Settings & System Info", 
                                   fg=NEON_COLORS["warning"], font=("Segoe UI", 18, "bold"))
        title_glow.pack()

        # Content with scrollbar
        content_frame = tk.Frame(settings_window, bg=NEON_COLORS["bg"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Settings sections
        sections = [
            ("🔑 API Configuration", self._get_api_info()),
            ("📊 Session Statistics", self._get_session_stats()),
            ("🔧 System Dependencies", self._get_dependency_info()),
            ("🎨 Theme Information", self._get_theme_info()),
            ("💡 Usage Tips", self._get_usage_tips())
        ]

        for title, items in sections:
            section = ttk.LabelFrame(content_frame, text=title, style="Neon.TLabelframe", padding=15)
            section.pack(fill="x", pady=10)

            for item in items:
                tk.Label(section, text=f"• {item}", bg=NEON_COLORS["panel"], 
                        fg=NEON_COLORS["text"], font=("Segoe UI", 10), 
                        wraplength=600, justify="left").pack(anchor="w", pady=2)

        # Close button
        ttk.Button(settings_window, text="✅ Close Settings", style="NeonPrimary.TButton",
                   command=settings_window.destroy).pack(pady=20)

    def _get_api_info(self):
        """Get API configuration info"""
        info = []
        if GOOGLE_API_KEY:
            info.append(f"✅ Google Gemini API: Connected ({GEMINI_MODEL_NAME})")
        else:
            info.append("❌ Google Gemini API: Not configured")
        
        if OPENAI_API_KEY:
            info.append(f"✅ OpenAI API: Connected ({OPENAI_MODEL})")
        else:
            info.append("❌ OpenAI API: Not configured")
        
        if not GOOGLE_API_KEY and not OPENAI_API_KEY:
            info.append("⚠️ No AI APIs configured - limited functionality")
        
        return info

    def _get_session_stats(self):
        """Get session statistics"""
        return [
            f"Total Conversations: {len(self.history)}",
            f"Current Mode: {self.current_mode.get()}",
            f"Detected Emotion: {self.detected_emotion.get()}",
            f"Emotion History: {len(self.emotion_history)} detections",
            f"Font Size: {self.font_size.get()}pt",
            f"Translation: {'Enabled' if self.show_translation.get() else 'Disabled'}",
            f"Active Controls: {sum(1 for v in self.controls.values() if v.get())}/4"
        ]

    def _get_dependency_info(self):
        """Get dependency information"""
        deps = [
            ("OpenCV (Real emotion detection)", cv2),
            ("DeepFace (Emotion analysis)", DeepFace),
            ("Speech Recognition (Voice input)", sr),
            ("pyttsx3 (Text-to-speech)", pyttsx3),
            ("PIL/Pillow (Image processing)", PIL_OK),
            ("requests (Image loading)", requests),
            ("googletrans (Translation)", Translator),
            ("numpy (Enhanced features)", np)
        ]
        
        return [f"{'✅' if available else '❌'} {name}" for name, available in deps]

    def _get_theme_info(self):
        """Get theme information"""
        return [
            "Current Theme: Enhanced Neon Edition",
            f"Primary Color: {NEON_COLORS['primary']} (Cyan)",
            f"Secondary Color: {NEON_COLORS['secondary']} (Green)", 
            f"Accent Color: {NEON_COLORS['accent']} (Magenta)",
            "Supports: Glow effects, animated bubbles, responsive design",
            "Accessibility: High contrast, dyslexia-friendly fonts available"
        ]

    def _get_usage_tips(self):
        """Get usage tips"""
        return [
            "Use Ctrl+Enter to send messages quickly",
            "Try different support modes for specialized assistance",
            "Enable emotion detection for personalized responses",
            "Use voice input for hands-free interaction",
            "Export conversations to save your progress",
            "Load profiles to resume previous sessions",
            "Visual aids help with complex topics",
            "Advanced controls customize the AI's behavior"
        ]

    def show_emotion_history(self):
        """Show detailed emotion history"""
        if not self.emotion_history:
            messagebox.showinfo("Emotion History", "No emotion data recorded yet.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("📊 Emotion History")
        history_window.configure(bg=NEON_COLORS["bg"])
        history_window.geometry("600x500")

        # Center window
        history_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 600) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 500) // 2
        history_window.geometry(f"600x500+{x}+{y}")

        # Header
        header = tk.Frame(history_window, bg=NEON_COLORS["panel"])
        header.pack(fill="x", padx=20, pady=20)

        title_glow = neon_glow_label(header, "📊 Emotion History", 
                                   fg=NEON_COLORS["info"], font=("Segoe UI", 16, "bold"))
        title_glow.pack()

        # Stats
        stats = tk.Frame(history_window, bg=NEON_COLORS["panel"])
        stats.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(stats, text=f"Total Detections: {len(self.emotion_history)}", 
                bg=NEON_COLORS["panel"], fg=NEON_COLORS["text"], 
                font=("Segoe UI", 12)).pack(side="left")

        if self.emotion_history:
            latest = self.emotion_history[-1][0].title()
            tk.Label(stats, text=f"Latest: {latest}", 
                    bg=NEON_COLORS["panel"], fg=NEON_COLORS["primary"], 
                    font=("Segoe UI", 12)).pack(side="right")

        # History list
        list_frame = tk.Frame(history_window, bg=NEON_COLORS["bg"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Scrollable listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        history_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                 bg=NEON_COLORS["surface"], fg=NEON_COLORS["text"],
                                 font=("Segoe UI", 11), selectbackground=NEON_COLORS["primary"])
        history_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=history_list.yview)

        # Populate list
        emotion_icons = {
            'happy': '😊', 'sad': '😢', 'angry': '😠', 
            'surprise': '😲', 'fear': '😨', 'neutral': '😐', 'disgust': '😖'
        }

        for i, (emotion, timestamp) in enumerate(reversed(self.emotion_history), 1):
            icon = emotion_icons.get(emotion, '😐')
            time_str = timestamp.strftime("%H:%M:%S")
            history_list.insert(0, f"{i:2d}. {icon} {emotion.title()} - {time_str}")

        # Close button
        ttk.Button(history_window, text="✅ Close", style="NeonPrimary.TButton",
                   command=history_window.destroy).pack(pady=20)

    def clear_chat(self):
        """Clear chat with confirmation"""
        if not self.history and not self.chat.message_history:
            messagebox.showinfo("Clear Chat", "Chat is already empty.")
            return

        result = messagebox.askyesno("Clear Chat", 
                                   f"Clear all chat messages and conversation history?\n\n" +
                                   f"This will remove {len(self.history)} conversations.\n\n" +
                                   "This action cannot be undone.")
        
        if result:
            self.chat.clear_messages()
            self.history.clear()
            # Reset controls
            for control in self.controls.values():
                control.set(False)
            
            self.chat.add_bubble("🗑️ Chat cleared. Ready for a fresh start! Ask me anything.", "assistant")


# ---------------------- Main Application ----------------------
def main():
    """Enhanced main function with better error handling"""
    print("🧠 NeuroBridge AI - Enhanced Neon Edition")
    print("=" * 50)
    
    # Check API keys
    if not GOOGLE_API_KEY and not OPENAI_API_KEY:
        print("⚠️  WARNING: No AI API keys configured!")
        print("   Set GOOGLE_API_KEY or OPENAI_API_KEY in your .env file")
        print("   The app will run with limited functionality.\n")
    elif GOOGLE_API_KEY:
        print(f"✅ Google Gemini API configured ({GEMINI_MODEL_NAME})")
    elif OPENAI_API_KEY:
        print(f"✅ OpenAI API configured ({OPENAI_MODEL})")
    
    # Check optional dependencies
    optional_deps = [
        ("OpenCV", cv2),
        ("DeepFace", DeepFace), 
        ("SpeechRecognition", sr),
        ("pyttsx3", pyttsx3),
        ("PIL/Pillow", PIL_OK),
        ("requests", requests),
        ("googletrans", Translator)
    ]
    
    missing_deps = [name for name, available in optional_deps if not available]
    if missing_deps:
        print(f"\n📦 Optional dependencies missing: {', '.join(missing_deps)}")
        print("   Install for full functionality:")
        print("   pip install opencv-python deepface speechrecognition pyttsx3 pillow requests googletrans==4.0.0rc1")
    
    print("\n🚀 Starting NeuroBridge AI...")
    
    try:
        # Create and run application
        root = tk.Tk()
        app = NeuroBridgeGUI(root)
        
        # Show welcome message
        print("✅ Application started successfully!")
        print("🎨 Neon theme loaded")
        print("🧠 Enhanced features available")
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()