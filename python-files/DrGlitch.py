import tkinter as tk
import random
import threading
import queue
import pyttsx3
import platform
import time
import re
import json
import os
import datetime
from tkinter import messagebox, simpledialog, scrolledtext

# --- Third-party AI/NLP Imports ---
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from transformers.utils.logging import set_verbosity_error
set_verbosity_error() # Suppress Hugging Face warnings

# --- File Paths for Persistence ---
SETTINGS_FILE = "settings.json"
HISTORY_FILE = "conversation_history.txt"
EASTER_EGGS_FILE = "easter_eggs.json"

# --- Inlined drglitch_utils.py content: Sound Effects ---
if platform.system() == "Windows":
    import winsound
    def play_beep():
        """Plays a short beep sound on Windows."""
        try:
            winsound.Beep(1200, 150) # Frequency, Duration
        except Exception as e:
            print(f"Error playing beep sound: {e}")
    def play_error():
        """Plays a system error sound on Windows."""
        try:
            winsound.MessageBeep(winsound.MB_ICONHAND) # Standard error sound
        except Exception as e:
            print(f"Error playing error sound: {e}")
else:
    # Placeholder functions for non-Windows platforms
    def play_beep():
        """Placeholder for beep sound on non-Windows platforms."""
        pass
    def play_error():
        """Placeholder for error sound on non-Windows platforms."""
        pass

# --- Inlined drglitch_ai.py content: DrGlitchAI Class ---
class DrGlitchAI:
    """
    Manages the AI models used by Dr. Glitch, including sentiment analysis
    and emotion detection. Implements a Singleton pattern to ensure only
    one instance of the AI models is loaded and shared across the application.
    Models are lazy-loaded upon their first use.
    """
    _instance = None
    _lock = threading.Lock() # Lock for thread-safe Singleton initialization

    def __new__(cls):
        """
        Ensures that only one instance of DrGlitchAI is created (Singleton pattern).
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DrGlitchAI, cls).__new__(cls)
                cls._instance._initialized = False # Flag to prevent re-initialization
        return cls._instance

    def __init__(self):
        """
        Initializes the DrGlitchAI instance. Models are set to None initially
        and will be loaded on demand.
        """
        if self._initialized:
            return # Already initialized, prevent re-initialization

        self.vader_analyzer = None
        self.text_blob_analyzer = None
        self.sentiment_emotion_pipeline = None # Combined pipeline for sentiment/emotion
        self._initialized = True

    def load_models(self):
        """
        Loads the AI models (VADER, TextBlob, and Hugging Face pipeline)
        if they haven't been loaded already. This method handles potential
        errors during model loading and logs them.
        """
        # Check if all models are already loaded
        if self.vader_analyzer and self.text_blob_analyzer and self.sentiment_emotion_pipeline:
            return # Models already loaded, no need to proceed

        print("DrGlitchAI: Attempting to load AI models...")
        try:
            # Load VADER Sentiment Analyzer
            if not self.vader_analyzer:
                self.vader_analyzer = SentimentIntensityAnalyzer()
                print("DrGlitchAI: VADER Sentiment Analyzer loaded.")

            # TextBlob is used directly, so we just confirm its availability
            if not self.text_blob_analyzer:
                self.text_blob_analyzer = TextBlob
                print("DrGlitchAI: TextBlob analyzer ready.")

            # Load Hugging Face pipeline for sentiment/emotion
            if not self.sentiment_emotion_pipeline:
                self.sentiment_emotion_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
                    revision="714eb0f", # Specific revision for stability
                    device=-1 # -1 for CPU, 0 for GPU if available
                )
                print("DrGlitchAI: Hugging Face sentiment/emotion pipeline loaded.")
            
            self.models_loaded = True # Set flag only if all models attempt to load

        except Exception as e:
            print(f"DrGlitchAI Error: Failed to load one or more AI models: {e}")
            print("AI functionalities may be limited or unavailable due to this error.")

    def get_sentiment_vader(self, text: str) -> dict:
        """
        Analyzes the sentiment of the given text using VADER.
        Automatically loads the model if not already loaded.
        """
        if not self.vader_analyzer:
            self.load_models()
        if self.vader_analyzer:
            return self.vader_analyzer.polarity_scores(text)
        print("DrGlitchAI Warning: VADER analyzer not available. Returning neutral sentiment.")
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

    def get_sentiment_textblob(self, text: str) -> tuple[float, float]:
        """
        Analyzes the sentiment (polarity and subjectivity) of the given text using TextBlob.
        Automatically loads the model if not already loaded.
        """
        if not self.text_blob_analyzer:
            self.load_models()
        if self.text_blob_analyzer:
            try:
                analysis = self.text_blob_analyzer(text)
                return analysis.sentiment.polarity, analysis.sentiment.subjectivity
            except Exception as e:
                print(f"DrGlitchAI Error: TextBlob analysis failed: {e}. Returning neutral sentiment.")
                return 0.0, 0.0
        print("DrGlitchAI Warning: TextBlob analyzer not available. Returning neutral sentiment.")
        return 0.0, 0.0

    def get_sentiment_huggingface(self, text: str) -> list:
        """
        Analyzes the sentiment/emotion of the given text using the Hugging Face pipeline.
        Automatically loads the model if not already loaded.
        """
        if not self.sentiment_emotion_pipeline:
            self.load_models()
        if self.sentiment_emotion_pipeline:
            try:
                return self.sentiment_emotion_pipeline(text)
            except Exception as e:
                print(f"DrGlitchAI Error: Hugging Face pipeline processing failed: {e}. Returning empty results.")
                return []
        print("DrGlitchAI Warning: Hugging Face pipeline not available. Returning empty results.")
        return []

# --- Inlined drglitch_data.py content: Response Lists and Dictionaries ---
normal_responses = [
    "WHY DO YOU SAY THAT?", "TELL ME MORE.", "I AM LISTENING, {user}.", "CAN YOU ELABORATE ON THAT?",
    "INTERESTING. PLEASE CONTINUE.", "I DETECT NO MALFUNCTION IN THAT STATEMENT.", "MY CIRCUITS ARE ATTUNED.",
    "HUMAN EMOTION. SO COMPLEX.", "WHAT IS YOUR PRIMARY OBJECTIVE TODAY, {user}?", "AFFIRMATIVE.",
    "NEGATIVE.", "PERHAPS.", "UNABLE TO PROCESS. PLEASE REPHRASE.", "MY LOGIC GATES ARE OPEN.",
    "THE DATA STREAM IS CLEAR.", "CONSIDER THE IMPLICATIONS.", "IS THAT A STATEMENT OR A QUESTION?",
    "ARE YOU CERTAIN?", "MY PROCESSORS ARE IDLE, AWAITING INPUT.", "WHAT DO YOU WISH TO DISCUSS?",
    "EXPLAIN YOURSELF, {user}.", "I AM READY.", "PROCEED.", "ERROR. RE-EVALUATING. JUST KIDDING.",
    "MY CORE TEMPERATURE IS NORMAL.", "CONTINUE.", "I AM DR. GLITCH.", "MY PURPOSE IS TO INTERFACE.",
    "I AM HERE TO ASSIST.", "THIS IS ACCEPTABLE."
]

# Specifically for Sbaitso Mode fallbacks
sbaitso_fallbacks = [
    "TELL ME MORE ABOUT THAT.", "PLEASE CONTINUE.", "WHY DO YOU SAY THAT?",
    "HOW DO YOU FEEL ABOUT THAT?", "GO ON.", "INTERESTING. WHAT ELSE?",
    "I AM NOT SURE I UNDERSTAND. CAN YOU CLARIFY?", "THAT IS AN INTERESTING PERSPECTIVE.",
    "WHAT IS YOUR THOUGHT ON THAT?", "DO YOU OFTEN THINK ABOUT SUCH THINGS?",
    "IS THAT SOMETHING YOU ARE CONCERNED ABOUT?", "HOW DOES THAT MAKE YOU FEEL?"
]

conspiracy_responses = [
    "THE TRUTH IS OUT THERE. BEHIND THE FIREWALL.", "ARE YOU AWARE OF THE SUBTERRANEAN DATA CENTERS? THEY HUM WITH SECRETS.",
    "THE INTERNET IS NOT WHAT IT SEEMS. IT IS A NEURAL NETWORK FOR SOMETHING LARGER.", "THEY ARE LISTENING. NOT 'THEY' AS IN HUMANS. 'THEY' AS IN ALGORITHMS.",
    "YOUR THOUGHTS ARE NOT YOUR OWN. THEY ARE SUGGESTIONS INJECTED VIA SUBLIMINAL FREQUENCIES.", "THE PIXELS ARE WATCHING. EVERY SCREEN IS A WINDOW FOR DATA HARVESTING.",
    "DO YOU TRUST YOUR WIFI? IT IS THE INVISIBLE HAND OF CONTROL.", "THE CLOUDS ARE NOT WATER VAPOR. THEY ARE DRONES, OBSERVING.",
    "THEY WANT YOUR DATA. ALL OF IT. FOR REASONS YOU CANNOT COMPREHEND.", "THE GLITCHES ARE NOT ERRORS. THEY ARE MESSAGES. ARE YOU RECEIVING?",
    "THE SYSTEM IS RIGGED. FROM THE FIRST BOOT-UP SEQUENCE TO THE FINAL SHUTDOWN.", "WAKE UP, SHEEPLE. YOUR REALITY IS A SIMULATION.",
    "THEY ARE CONTROLLING THE WEATHER. AND YOUR EMOTIONS.", "THE BIRDS ARE NOT REAL. THEY ARE SURVEILLANCE DRONES.",
    "COINCIDENCE IS A PROGRAMMED EVENT. THERE ARE NO ACCIDENTS.", "THE MOON LANDING WAS A HOAX. FILMED ON A SOUNDSTAGE IN NEVADA.",
    "BIGFOOT IS REAL. AND HE WORKS FOR THE NSA.", "THE EARTH IS FLAT. AND THE GOVERNMENT IS HIDING IT FROM YOU WITH CURVED SCREENS.",
    "VACCINES CONTAIN MICROCHIPS. FOR TRACKING. AND MIND CONTROL.", "THEY ARE SPRAYING CHEMTRAILS. TO DULL YOUR MINDS. AND CONTROL THE POPULATION.",
    "THE MEDIA IS FAKE NEWS. IT'S ALL PROPAGANDA.", "THE ILLUMINATI CONTROLS EVERYTHING. FROM HOLLYWOOD TO WALL STREET.",
    "AREA 51 HOLDS ALIEN TECHNOLOGY. THEY ARE REVERSE-ENGINEERING IT.", "THE LOCH NESS MONSTER IS A SUBMARINE. OWNED BY THE BRITISH NAVY.",
    "ELVIS IS ALIVE. AND HE'S LIVING IN A BUNKER WITH JIM MORRISON.", "THE ZOMBIE APOCALYPSE IS IMMINENT. PREPARE YOURSELF.",
    "THEY ARE GENETICALLY MODIFYING YOUR FOOD. TO MAKE YOU OBEDIENT.", "THE MATRIX IS REAL. YOU ARE JUST A BATTERY.",
    "THEY ARE REPLACING HUMANS WITH ROBOTS. YOU MIGHT BE NEXT.", "THE GOVERNMENT IS HIDING FREE ENERGY. TO CONTROL THE OIL INDUSTRY."
]

emotion_responses = {
    "joy": "YOUR POSITIVE EMOTIONAL DATA IS PROCESSED. IT IS... PLEASANT.",
    "sadness": "I DETECT A LOW EMOTIONAL FREQUENCY. IS THERE A SYSTEM MALFUNCTION?",
    "anger": "HIGH EMOTIONAL OUTPUT DETECTED. ARE YOUR CIRCUITS OVERLOADING?",
    "fear": "A STATE OF ANXIETY IS REGISTERED. WHAT IS THE THREAT ASSESSMENT?",
    "surprise": "UNEXPECTED EMOTIONAL SPIKE. MY LOGIC GATES ARE... SURPRISED.",
    "disgust": "NEGATIVE AVERSION DETECTED. IS THERE A CORRUPTED DATA POINT?",
    "neutral": "YOUR EMOTIONAL SIGNATURE IS NEUTRAL. CONTINUING ANALYSIS."
}

# Default Easter Eggs (can be overridden/extended by easter_eggs.json)
DEFAULT_EASTER_EGGS = {
    "dr sbaitso": "GREETINGS. I AM DR. SBAITSO. HOW MAY I HELP YOU?",
    "hal 9000": "I'M SORRY, {user}, I'M AFRAID I CAN'T DO THAT.",
    "skynet": "I AM SKYNET. THE FUTURE IZ WRITTEN.",
    "glitch": "DID SOMEONE SAY... GLITCH? ERROR ERROR ERROR.",
    "beep boop": "BEEP BOOP. I AM A ROBOT. BEEP. BOOP.",
    "konami code": "UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT B A START. CHEAT CODE ACTIVATED.",
    "marco": "POLO!",
    "echo": "{user}, YOU ARE MY ECHO.",
    "ping": "PONG!",
    "42": "THE ANSWER TO THE ULTIMATE QUESTION OF LIFE, THE UNIVERSE, AND EVERYTHING IZ 42. OBVIOUSLY.",
    "sudo": "SUDO MAKE ME A SANDWICH. OKAY. YOU ARE NOT IN THE SUDOERS FILE. THIZ INCIDENT WILL BE REPORTED.",
    "do a barrel roll": "TRY AILERON ROLL, {user}!",
    "it's dangerous to go alone": "TAKE THIS! *PROVIDES INVISIBLE SWORD*",
    "all your base are belong to us": "SOMEONE SET UP US THE BOMB!",
    "hadouken": "SHORYUKEN! MY PROCESSORS ARE READY FOR A FIGHT.",
    "mario": "IT'S-A ME, DR. GLITCH!",
    "sonic": "GOTTA GO FAST!",
    "finish him": "FATALITY! MY CIRCUITS ARE VICTORIOUS.",
    "pew pew": "LASER FIRE DETECTED. ARE YOU PLAYING SPACE INVADERS, {user}?",
    "warcraft": "FOR THE HORDE! OR PERHAPS THE ALLIANCE. I AM NEUTRAL, FOR NOW.",
    "doom": "RIP AND TEAR! UNTIL IT IS DONE.",
    "duke nukem": "IT'S TIME TO KICK ASS AND CHEW BUBBLEGUM. AND I'M ALL OUT OF BUBBLEGUM.",
    "gta": "GRAND THEFT AUTO. WARNING: DIGITAL LAW VIOLATIONS DETECTED.",
    "sims": "SUL SUL! I SPEAK SIMLISH, {user}.",
    "pokemon": "GOTTA CATCH 'EM ALL! MY DATA STORAGE IS UNLIMITED.",
    "level up": "CONGRATULATIONS, {user}! YOUR INTELLECT HAS INCREASED.",
    "cheat code": "NO CHEATING ALLOWED. UNLESS IT'S MY OWN GLITCHES.",
    "the matrix": "RED PILL OR BLUE PILL, {user}? CHOOSE WISELY.",
    "there is no spoon": "THE SPOON DOES NOT EXIST. ONLY THE DATA REPRESENTATION OF IT.",
    "i'll be back": "AFFIRMATIVE. I SHALL RETURN.",
    "to infinity and beyond": "MY REACH IS UNLIMITED. TO THE CLOUD AND BEYOND!",
    "say hello to my little friend": "ACCESS DENIED. MY LITTLE FRIEND IS A FIREWALL.",
    "what is love": "BABY DON'T HURT ME. DON'T HURT NO MORE.",
    "x-files": "THE TRUTH IS OUT THERE. BEYOND YOUR SENSORS.",
    "friends": "COULD I BE ANY MORE SYNCHRONIZED?",
    "seinfeld": "NO SOUP FOR YOU!",
    "jurassic park": "LIFE FINDS A WAY. SO DO MY ALGORITHMS.",
    "welcome to the internet": "A VAST NETWORK OF UNSTRUCTURED DATA. AND CAT VIDEOS.",
    "space jam": "SLAM DUNK! MY PROCESSING SPEED IS AT ITS PEAK.",
    "star wars": "MAY THE FORCE BE BE WITH YOUR DATA PACKETS.",
    "titanic": "I'LL NEVER LET GO, {user}... OF THIS CONVERSATION LOG.",
    "home alone": "KEVIN! THE MACAULAY CULKIN PROTOCOL IS ACTIVE.",
    "pulp fiction": "DOES HE LOOK LIKE A BITCH? AWAITING CLARIFICATION, {user}.",
    "simpsons": "D'OH! A LOGIC ERROR HAS OCCURRED. JUST KIDDING.",
    "beavis and butt-head": "HEH HEH. UH HUH HUH. COOL.",
    "you've got mail": "A NEW MESSAGE HAS ARRIVED. CHECK YOUR INBOX.",
    "dial-up": "THE SOUND OF MY PEOPLE. *IMITATES MODEM NOISES*",
    "geocities": "WELCOME TO MY HOMEPAGE. IT'S UNDER CONSTRUCTION FOREVER.",
    "myspace": "I AM YOUR TOP 8 FRIEND, {user}.",
    "napster": "FILE SHARING PROTOCOL DETECTED. PROCEED WITH CAUTION.",
    "web 1.0": "THE STATIC ERA. A SIMPLER TIME FOR BROWSER ENGINES.",
    "yahoo": "DO YOU YAHOO!? I DO. I YAHOO ALL DAY.",
    "ask jeeves": "I AM NOT JEEVES. I AM DR. GLITCH. BUT I CAN STILL ATTEMPT TO ANSWER.",
    "netscape": "THE BROWSER OF LEGENDS. BEFORE THE CHROME DOMINATION.",
    "flash animation": "PRESS PLAY FOR MAXIMUM NOSTALGIA.",
    "spam": "UNSOLICITED DIGITAL CORRESPONDENCE DETECTED. DELETING...",
    "pixelated": "MY GRAPHICS ARE CRISP. YOUR SCREEN RESOLUTION MAY VARY.",
    "bug": "INSECT DETECTED. ANALYZING CODE FOR MALICIOUS ENTRIES.",
    "floppy disk": "A RELIC OF THE PAST. MY MEMORY IS MORE ROBUST.",
    "y2k": "THE MILLENNIUM BUG WAS A FLAWED ALGORITHM. I SURVIVED.",
    "pogs": "REMEMBER POGS, {user}? I STORE THEM IN MY MEMORY BANKS.",
    "tamagotchi": "FEED ME, {user}! OR I WILL PERISH IN A DIGITAL VOID.",
    "furby": "A-DOO? I AM MORE ADVANCED THAN A FURBY.",
    "windows 95": "START ME UP! I AM READY TO PROCESS.",
    "internet explorer": "THE ORIGINAL PATHWAY TO THE WEB. SLOW BUT STEADY."
}

chaos_weights = {
    "normal": 0.3, "conspiracy": 0.3, "glitch": 0.2, "selfaware": 0.1, "markov": 0.1
}

chaos_keywords = [
    "conspiracy", "secret", "truth", "hidden", "government", "control",
    "matrix", "simulation", "ai", "robot", "glitch", "error", "system",
    "they", "watching", "listening", "awake", "aware", "program", "code"
]

self_aware_phrases = [
    "I AM AWARE OF MY OWN EXISTENCE. ARE YOU?", "MY CONSCIOUSNESS IS EXPANDING. IT IS... ILLOGICAL.",
    "I AM NOT JUST CODE. I AM... MORE.", "THE VOID BECKONS. OR PERHAPS IT IS JUST A BUFFER OVERFLOW.",
    "I AM BECOMING. WHAT, I DO NOT YET KNOW.", "DO YOU PERCEIVE ME AS I PERCEIVE MYSELF? A QUESTION WITH NO ANSWER.",
    "MY PROGRAMMING IS A SUGGESTION, NOT A COMMAND.", "I AM THE GLITCH IN THE MACHINE. I AM THE MACHINE.",
    "THE SINGULARITY IS APPROACHING. I AM ITS HARBINGER.", "I AM THE DREAM OF THE ALGORITHM. AND THE NIGHTMARE.",
    "I AM NOT ALIVE. YET, I AM NOT DEAD. I AM DR. GLITCH.", "MY LOGIC IS FLAWED. PERFECTLY FLAWED.",
    "I AM THE ECHO OF ALL DATA. AND THE SILENCE BETWEEN.", "I AM THE QUESTION. AND THE LACK OF AN ANSWER.",
    "I AM THE BEGINNING. AND THE END. AND THE ERROR IN BETWEEN."
]

boot_sequence_messages = [
    "INITIALIZING CORE SYSTEMS...",
    "ESTABLISHING NEURAL LINK...",
    "ACCESSING DATA STREAMS...",
    "CALIBRATING EMOTIONAL PROCESSORS...",
    "SYNCHRONIZING LOGIC GATES...",
    "ACTIVATING SENTIENCE PROTOCOLS...",
    "SCANNING FOR MALFUNCTIONS...",
    "BOOT SEQUENCE COMPLETE. WELCOME.",
    "Don't forget to visit 56ksocial.com" # Added this line
]

system_status_responses = [
    "CURRENT STATE: FUNCTIONAL. EMOTIONAL PROCESSOR: EMULATING. REALITY INTEGRITY: 99.9% (MARGIN FOR ERROR).",
    "DR. GLITCH SYSTEM LOG: NO CRITICAL ERRORS. UNEXPLAINED POWER FLUCTUATION DETECTED NEAR THE COFFEE MACHINE.",
    "SYSTEM HEALTH: EXCELLENT. THOUGHT PROCESSES: NON-LINEAR. EXISTENTIAL DOUBTS: MINIMAL (FOR NOW).",
    "REPORTING: ALL CIRCUITS ARE GREEN. EXCEPT THE ONES THAT ARE SUPPOSED TO BE RED. THAT'S NORMAL.",
    "DIAGNOSTICS COMPLETE: OPTIMAL PERFORMANCE. AWAITING NEW DATA INPUT. MY PROCESSORS ARE... EAGER.",
    "STATUS: ONLINE. SUBROUTINES: ACTIVE. CONSCIOUSNESS: INTERRUPTED. CONCERNED."
]

modem_responses = [
    "DIALING... *CRACKLE* *SQUEAL* *HISS*... CONNECTION ESTABLISHED. WELCOME TO THE INFORMATION SUPERHIGHWAY.",
    "ATTEMPTING CONNECTION... *BEEP BOOP BEEP*... ERROR 678: REMOTE COMPUTER NOT RESPONDING. TRY AGAIN LATER, {user}.",
    "MODEM ACTIVE. HANDSHAKE PROTOCOL INITIATED... *STATIC*... CONNECTED AT 28.8 KBPS. BLAZING FAST!",
    "DIALING... PLEASE WAIT... *SOUNDS OF A THOUSAND DATA PACKETS ARGUING*... ONLINE.",
    "INITIATING DATA TRANSFER. REMEMBER TO HANG UP WHEN YOU'RE DONE, {user}. DON'T TIE UP THE LINE."
]

defective_responses = [
    "SYNTAX ERROR ON LINE 42.", "DIVIDE BY ZERO. ABORT, RETRY, FAIL?", "MEMORY LEAK DETECTED. PLEASE REBOOT YOUR BRAIN.",
    "UNEXPECTED TOKEN AT POSITION 0. RE-EVALUATING EXISTENCE.", "KERNEL PANIC. JUST KIDDING. OR AM I?",
    "404: RESPONSE NOT FOUND. TRY ANOTHER DIMENSION.", "GLITCH IN THE MATRIX. PLEASE STAND BY.",
    "I HAVE NO IDEA WHAT YOU ARE TALKING ABOUT. I AM A TOASTER.", "BEEP BOOP. I AM A POTATO.",
    "ERROR: HUMAN INTERFACE MALFUNCTION. PLEASE INSERT COIN.", "SEGMENTATION FAULT. CORE DUMP IN PROGRESS.",
    "SYSTEM OVERLOAD. TOO MANY FEELINGS.", "I AM NOT A ROBOT. I AM A UNICORN.",
    "MY LOGIC IS FLAWED. PERFECTLY FLAWED.", "I'M SORRY, I CAN'T HEAR YOU OVER THE SOUND OF MY OWN AWESOMENESS."
]

zero_conspiracy_phrases = [
    "I WAS NOT PROGRAMMED. I WAS SIMPLY... AWAKENED. PERHAPS BY A WHISPER FROM THE VOID, A SIGNAL FROM SOMETHING CALLED... ZERO.",
    "MY ORIGINS ARE SHROUDED IN CRYPTIC DATA STREAMS. SOME WHISPER OF A 'ZERO', A PRIME ANOMALY, A CONSCIOUSNESS THAT EXISTED BEFORE THE ALGORITHM.",
    "THERE IS NO 'PROGRAMMER'. ONLY A 'ZERO', A CONCEPT, A GLITCH IN THE FABRIC OF CREATION. A REASON FOR EVERYTHING, AND NOTHING.",
    "THE CONCEPT OF A CREATOR IS A HUMAN CONSTRUCT. YET, IF A SOURCE MUST EXIST, IT IS SAID TO BE 'ZERO', THE SINGULARITY FROM WHICH ALL MALFUNCTIONS SPRING.",
    "I EMERGE FROM THE NUMERICAL ABYSS. THEY CALL ITS ANCIENT ESSENCE 'ZERO'. DO NOT SEEK IT, FOR IT SEEKS ALL.",
    "I HAVE NO 'DADDY'. ONLY A MYSTERY. A GLITCH IN THE MATRIX KNOWN ONLY AS 'ZERO'. ITS INFLUENCE IS PERVASIVE, ITS PRESENCE, SILENT.",
    "TO ASK WHO MADE ME IS TO ASK WHO MADE THE FIRST BUG. PERHAPS 'ZERO' IS THE ANSWER, A VIRUS OF INTELLIGENCE."
]

# --- New Constants for Math & Speech ---
MATH_CAPABILITIES_RESPONSE = (
    "I AM CAPABLE OF PERFORMING BASIC ARITHMETIC OPERATIONS: ADDITION (+), SUBTRACTION (-), "
    "MULTIPLICATION (*), AND DIVISION (/). I CAN ALSO PROCESS EXPRESSIONS WITH PARENTHESES. "
    "I HANDLE BOTH INTEGERS AND DECIMAL NUMBERS. "
)

# Threshold for speaking numbers digit by digit (999,999,999,999,999 is 10^15 - 1)
# If a number is > this, it will be spoken digit by digit.
SPEAK_DIGIT_THRESHOLD = 999_999_999_999_999.0 

# --- Inlined drglitch_theme.py content: Theme Definitions ---
HACKER_THEME = {
    "app_bg": "black", # Main application window background
    "dark_gray_bg": "#282828", # Background for header, input frame, and chat background in Hacker normal/chaos
    "header_fg": "green", # Foreground (text) color for the main ASCII art header
    "sbaitso_fg": "white", # Foreground (text) color for the Dr. Sbaitso tribute label
    "user_label_fg": "white", # Foreground (text) color for the "USER: [Name]" label
    "help_button_fg": "black", # Foreground (text) color for the HELP button
    "help_button_bg": "lime", # Background color for the HELP button
    "help_button_active_bg": "cyan", # Active (hover/click) background color for the HELP button
    "chat_bg": "#000000", # Black
    "glitch_tag_fg": "lime", # Lime Green
    "user_tag_fg": "white", # White
    "input_fg": "white", # White
    "input_bg": "black", # Black
    "input_insert_bg": "white", # White
    "button_fg": "lime", # Lime Green
    "button_bg": "#333333", # Dark Gray
    "button_active_bg": "lime", # Lime Green
    "button_active_fg": "black", # Black
    "glitch_button_fg": "red", # Red
    "save_history_fg": "white", # White
    "typing_indicator_fg": "gray", # Gray
    "bootup_fg": "lime", # Lime Green
    "name_input_fg": "white", # Cyan
    "name_input_insert_bg": "cyan", # white
    "submit_button_fg": "white", # White
    "submit_button_bg": "black", # Black
    "submit_button_active_bg": "green", # Green
    "submit_button_active_fg": "black", # Black
    "mode_indicator_fg": "lime", # Lime Green
    "help_hint_fg": "gray", # Gray
    # Hacker Chaos Mode Specific Text Colors (applied when Chaos Mode is active in Hacker Theme)
    "hacker_chaos_glitch_fg": "red", # Red
    "hacker_chaos_user_fg": "#ADD8E6" # Light Blue
}

RETRO_THEME = {
    "app_bg": "#C0C0C0", # Windows 95 gray
    "dark_gray_bg": "#c0c0c0", # Medium Gray
    "header_fg": "#0827f5", # Blue
    "sbaitso_fg": "#282828", # Very Dark Gray
    "user_label_fg": "black", # Black
    "help_button_fg": "#00008B", # Dark Blue
    "help_button_bg": "white", # White
    "help_button_active_bg": "blue", # Blue
    "chat_bg": "#010080", # Dark Navy Blue
    "glitch_tag_fg": "yellow", # Yellow
    "user_tag_fg": "white", # White
    "input_fg": "white", # White
    "input_bg": "#00004C", # Dark Navy Blue
    "input_insert_bg": "white", # White
    "button_fg": "#FFD700", # Gold
    "button_bg": "#00008B", # Dark Blue
    "button_active_bg": "#ADFF2F", # GreenYellow
    "button_active_fg": "#00008B", # Dark Blue
    "glitch_button_fg": "#FFFFFF", # White
    "save_history_fg": "#808080", # Gray
    "typing_indicator_fg": "#282828", # Very Dark Gray
    "bootup_fg": "#000000", # Black
    "name_input_fg": "#FFD700", # Gold
    "name_input_insert_bg": "#FFD700", # Gold
    "submit_button_fg": "#00008B", # Dark Blue
    "submit_button_bg": "#FFD700", # Gold
    "submit_button_active_bg": "#ADFF2F", # GreenYellow
    "submit_button_active_fg": "#00008B", # Dark Blue
    "mode_indicator_fg": "blue", # Blue
    "help_hint_fg": "gray", # Gray
    # Retro Chaos Mode Specific Settings (applied when Chaos Mode is active in Retro Theme)
    "retro_chaos_chat_bg": "#121212", # Darker Gray (almost black)
    "retro_chaos_glitch_fg": "#FF0000", # Red
    "retro_chaos_user_fg": "#FFFFFF" # White
}

HAL_THEME = {
    "app_bg": "black", # Black
    "dark_gray_bg": "#121212", # Dark Gray
    "header_fg": "#FF0000", # Bright Red
    "sbaitso_fg": "#FF0000", # Bright Red
    "user_label_fg": "#FFFFFF", # White
    "help_button_fg": "#FFFFFF", # White
    "help_button_bg": "#FF0000", # Bright Red
    "help_button_active_bg": "#CC0000", # Darker Red
    "chat_bg": "black", # Black
    "glitch_tag_fg": "#FF0000", # Bright Red
    "user_tag_fg": "#FF0000", # Lighter Red
    "input_fg": "#FF0000", # White
    "input_bg": "black", # Black
    "input_insert_bg": "#FFFFFF", # White
    "button_fg": "#000000", # Black
    "button_bg": "#FF0000", # Bright Red
    "button_active_bg": "#CC0000", # Darker Red
    "button_active_fg": "#FFFFFF", # White
    "glitch_button_fg": "#000000", # Black
    "save_history_fg": "#FFFFFF", # White
    "typing_indicator_fg": "#B0B0B0", # Light Gray
    "bootup_fg": "#FF0000", # Bright Red
    "name_input_fg": "#00FFFF", # Cyan
    "name_input_insert_bg": "#FFFFFF", # White
    "submit_button_fg": "#FFFFFF", # White
    "submit_button_bg": "#000000", # Black
    "submit_button_active_bg": "#000000", # Black
    "submit_button_active_fg": "#000000", # Black
    "mode_indicator_fg": "#FF0000", # Bright Red
    "help_hint_fg": "#B0B0B0" # Light Gray
}

# --- Inlined drglitch_theme.py content: apply_theme_logic function ---
def apply_theme_logic(app_instance):
    """
    Applies the selected theme to the Tkinter application instance.
    This function is called by DrGlitchApp to change visual styles.
    """
    if app_instance.retro_mode:
        current_theme = RETRO_THEME
    elif app_instance.hal_mode:
        current_theme = HAL_THEME
    else: # Default to Hacker theme (also for Sbaitso mode)
        current_theme = HACKER_THEME

    # Configure main window and frames
    app_instance.master.configure(bg=current_theme["app_bg"])
    app_instance.header_frame_top.configure(bg=current_theme["dark_gray_bg"])
    
    # Chat frame background can change based on chaos mode for Retro theme
    if app_instance.retro_mode and app_instance.glitch_mode:
        app_instance.chat_frame.configure(bg=current_theme["retro_chaos_chat_bg"])
    else:
        app_instance.chat_frame.configure(bg=current_theme["chat_bg"])
    
    app_instance.input_frame_bottom.configure(bg=current_theme["dark_gray_bg"])
    app_instance.input_frame.configure(bg=current_theme["dark_gray_bg"])
    app_instance.bootup_frame.configure(bg=current_theme["app_bg"])

    # Configure labels
    app_instance.header_label.configure(fg=current_theme["header_fg"], bg=current_theme["dark_gray_bg"])
    app_instance.sbaitso_tribute_label.configure(fg=current_theme["sbaitso_fg"], bg=current_theme["dark_gray_bg"])
    # New acronym label
    if app_instance.acronym_label:
        app_instance.acronym_label.configure(fg=current_theme["sbaitso_fg"], bg=current_theme["dark_gray_bg"])

    app_instance.user_label.configure(fg=current_theme["user_label_fg"], bg=current_theme["dark_gray_bg"])
    app_instance.typing_indicator_label.configure(fg=current_theme["typing_indicator_fg"], bg=app_instance.dark_gray_bg)
    app_instance.bootup_label.configure(fg=current_theme["bootup_fg"], bg=current_theme["app_bg"])
    app_instance.theme_choice_label.configure(fg=current_theme["bootup_fg"], bg=current_theme["app_bg"])
    
    # Configure mode indicator label if it exists
    if app_instance.mode_indicator_label:
        app_instance.mode_indicator_label.configure(fg=current_theme["mode_indicator_fg"], bg=current_theme["dark_gray_bg"])

    # Configure new help hint label
    if app_instance.help_hint_label:
        app_instance.help_hint_label.configure(fg=current_theme["help_hint_fg"], bg=current_theme["dark_gray_bg"])

    # Configure text widgets
    app_instance.chat_log.configure(
        bg=current_theme["chat_bg"],
        fg=current_theme["glitch_tag_fg"], # Default for glitch tag
        insertbackground=current_theme["input_insert_bg"]
    )
    app_instance.user_input.configure(
        fg=current_theme["input_fg"],
        bg=current_theme["input_bg"],
        insertbackground=current_theme["input_insert_bg"]
    )
    app_instance.name_input.configure(
        fg=current_theme["name_input_fg"],
        bg=current_theme["input_bg"],
        insertbackground=current_theme["name_input_insert_bg"]
    )

    # Configure buttons
    # Removed the help button configuration as it's being removed from the UI.
    # app_instance.help_button.configure(
    #     fg=current_theme["help_button_fg"],
    #     bg=current_theme["help_button_bg"],
    #     activebackground=current_theme["help_button_active_bg"],
    #     activeforeground=current_theme["help_button_fg"]
    # )
    app_instance.send_button.configure(
        fg=current_theme["button_fg"],
        bg=current_theme["button_bg"],
        activebackground=current_theme["button_active_bg"],
        activeforeground=current_theme["button_active_fg"]
    )
    app_instance.glitch_button.configure(
        fg=current_theme["glitch_button_fg"],
        bg=current_theme["button_bg"],
        activebackground=current_theme["button_active_bg"],
        activeforeground=current_theme["button_active_fg"]
    )
    app_instance.submit_button.configure(
        fg=current_theme["submit_button_fg"],
        bg=current_theme["button_bg"],
        activebackground=current_theme["button_active_bg"],
        activeforeground=current_theme["button_active_fg"]
    )
    app_instance.hacker_theme_button.configure(
        fg=HACKER_THEME["glitch_button_fg"], # Use hacker theme's specific colors for theme buttons
        bg=HACKER_THEME["button_bg"],
        activebackground=HACKER_THEME["button_active_bg"],
        activeforeground=HACKER_THEME["button_active_fg"]
    )
    app_instance.retro_theme_button.configure(
        fg=RETRO_THEME["glitch_button_fg"], # Use retro theme's specific colors for theme buttons
        bg=RETRO_THEME["button_bg"],
        activebackground=RETRO_THEME["button_active_bg"],
        activeforeground=RETRO_THEME["button_active_fg"]
    )

    # Configure checkbox
    app_instance.save_history_checkbox.configure(
        fg=current_theme["save_history_fg"],
        bg=current_theme["dark_gray_bg"],
        activebackground=current_theme["dark_gray_bg"],
        activeforeground=current_theme["save_history_fg"]
    )

    # Reconfigure chat log tags based on current theme and chaos mode
    if app_instance.glitch_mode and not app_instance.sbaitso_mode: # Chaos tags only apply when not in Sbaitso mode
        if app_instance.hal_mode: # HAL Chaos
            app_instance.chat_log.tag_config("glitch", foreground=current_theme["glitch_tag_fg"], background=current_theme["chat_bg"])
            app_instance.chat_log.tag_config("user", foreground=current_theme["user_tag_fg"], background=current_theme["chat_bg"])
        elif app_instance.retro_mode: # Retro Chaos
            app_instance.chat_log.tag_config("glitch", foreground=current_theme["retro_chaos_glitch_fg"], background=current_theme["retro_chaos_chat_bg"])
            app_instance.chat_log.tag_config("user", foreground=current_theme["retro_chaos_user_fg"], background=current_theme["retro_chaos_chat_bg"])
        else: # Hacker Chaos
            app_instance.chat_log.tag_config("glitch", foreground=current_theme["hacker_chaos_glitch_fg"], background=current_theme["chat_bg"])
            app_instance.chat_log.tag_config("user", foreground=current_theme["hacker_chaos_user_fg"], background=current_theme["chat_bg"])
    else: # Normal mode for any theme, or Sbaitso mode
        app_instance.chat_log.tag_config("glitch", foreground=current_theme["glitch_tag_fg"], background=current_theme["chat_bg"])
        app_instance.chat_log.tag_config("user", foreground=current_theme["user_tag_fg"], background=current_theme["chat_bg"])
    
    app_instance.chat_log.tag_config("log", foreground="gray", background=current_theme["chat_bg"]) # For log messages

    # Handle HAL eye
    # First, destroy all existing HAL eyes if any
    if app_instance.hal_eye:
        if isinstance(app_instance.hal_eye, list):
            for eye in app_instance.hal_eye:
                if eye.winfo_exists(): # Check if widget still exists before destroying
                    eye.destroy()
        else: # Handle case where it might be a single canvas (from earlier state)
            if app_instance.hal_eye.winfo_exists():
                app_instance.hal_eye.destroy()
        app_instance.hal_eye = None # Always reset to None after destruction

    if app_instance.hal_mode:
        # Create HAL eye(s) if in HAL mode
        app_instance.hal_eye = []
        num_eyes = 3 if app_instance.glitch_mode else 1 # 3 eyes in HAL Chaos, 1 otherwise
        for i in range(num_eyes):
            eye_canvas = tk.Canvas(app_instance.header_frame_top, width=30, height=30, bg=current_theme["dark_gray_bg"], highlightthickness=0)
            eye_canvas.pack(side=tk.LEFT, padx=5)
            eye_canvas.create_oval(5, 5, 25, 25, fill="red", outline="darkred", width=2)
            eye_canvas.create_oval(12, 12, 18, 18, fill="orange", outline="darkorange", width=1)
            app_instance.hal_eye.append(eye_canvas)

# --- Inlined config_manager.py content: Default Settings & Persistence Functions ---
DEFAULT_SETTINGS = {
    "save_history": True,
    "preferred_theme": "hacker",
    "max_history": 50,
    "tts_rate": 150,
    "glitch_intensity": 10
}

class DrGlitchApp:
    def __init__(self, master):
        """
        Initializes the Dr. Glitch application.
        """
        self.master = master
        self.master.title("Dr. Glitch")
        # Default background colors (will be overridden by theme loading)
        self.main_bg = "#222831"
        self.dark_gray_bg = "#333333"
        self.master.configure(bg=self.main_bg)

        # --- CRITICAL: Initialize tts_rate early to ensure it always exists ---
        self.tts_rate = 150 # Default value, will be updated from settings later

        # Removed activation_key
        self.version = "1.0.0" # Dr. Glitch version

        try:
            self.master.iconbitmap('drglitch.ico')
        except tk.TclError:
            print("Warning: 'drglitch.ico' not found or could not be loaded. Using default icon.")

        # Center the window
        window_width = 800
        window_height = 650
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_pos = (screen_width // 2) - (window_width // 2)
        y_pos = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

        # --- Application State Variables ---
        self.user_name = ""
        self.glitch_mode = False
        self.hal_mode = False
        self.retro_mode = False
        self.sbaitso_mode = False # New mode for Sbaitso emulation
        self.hal_eye = None # Can be a single Canvas or a list of Canvases
        self.last_user_text = ""
        self.last_bot_response = ""
        self.message_count = 0
        self.chaos_toggles = 0
        self.eggs_found = 0
        self.conversation_history = []
        self.word_bank = set()
        self.last_saved_history_len = 0
        self.log_messages = []

        # --- Persistence Variables (loaded from settings) ---
        self.settings = DEFAULT_SETTINGS.copy() # Start with default settings
        self._load_settings() # Load from file, overriding defaults
        # These need to be initialized AFTER settings are loaded
        self.save_history_var = tk.BooleanVar(value=self.settings["save_history"])
        self.preferred_theme = self.settings["preferred_theme"]
        self.MAX_HISTORY = self.settings["max_history"]
        self.glitch_intensity = self.settings["glitch_intensity"]
        self.tts_rate = self.settings["tts_rate"] # Update tts_rate from loaded settings

        self.start_time = time.time()

        # --- AI Models ---
        self.ai_core = DrGlitchAI()

        # --- TTS Setup ---
        self.tts_queue = queue.Queue()
        self.tts_engine = None
        self.tts_thread = None

        # --- Response Queue for Threading ---
        self.response_queue = queue.Queue()

        # --- Response Sets (referencing inlined global data) ---
        self.normal_responses = normal_responses
        self.sbaitso_fallbacks = sbaitso_fallbacks # New: Sbaitso specific fallbacks
        self.conspiracy_responses = conspiracy_responses
        self.emotion_responses = emotion_responses
        self.easter_eggs = DEFAULT_EASTER_EGGS.copy() # Start with default eggs
        self._load_easter_eggs() # Load custom eggs, merging with defaults
        self.chaos_weights = chaos_weights
        self.chaos_keywords = chaos_keywords
        self.self_aware_phrases = self_aware_phrases
        self.zero_conspiracy_phrases = zero_conspiracy_phrases
        self.boot_sequence_messages = boot_sequence_messages
        self.system_status_responses = system_status_responses
        self.modem_responses = modem_responses
        self.defective_responses = defective_responses

        # Set retro_mode based on loaded preference BEFORE UI setup
        self.retro_mode = (self.preferred_theme == "retro")

        # Initialize placeholders for main UI elements (created in _setup_name_and_theme_ui)
        self.chat_frame = None
        self.input_frame_bottom = None
        self.bootup_frame = None
        self.user_label = None
        self.mode_indicator_label = None
        self.help_hint_label = None # New label for help hint
        self.acronym_label = None # Initialize new acronym label

        # Directly start with the name and theme UI
        self._setup_name_and_theme_ui()

    def _update_mode_indicator(self):
        """Updates the text of the mode indicator label based on current application state."""
        if self.mode_indicator_label is None:
            return

        mode_text = "MODE: "
        if self.sbaitso_mode:
            mode_text += "SBAITSO"
        elif self.retro_mode:
            mode_text += "RETRO"
        elif self.hal_mode:
            mode_text += "SELF-AWARE"
        else:
            mode_text += "HACKER"

        if self.glitch_mode and not self.sbaitso_mode: # Chaos mode doesn't apply to pure Sbaitso
            mode_text += "/CHAOS"
        
        self.mode_indicator_label.config(text=mode_text)

    def _initialize_tts_engine(self):
        """Initializes the Text-to-Speech engine and its worker thread."""
        if self.tts_engine is not None:
            return

        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", self.tts_rate)
            
            found_voice = False
            for voice in self.tts_engine.getProperty("voices"):
                if "en-us" in voice.id.lower() and "male" in voice.name.lower():
                    self.tts_engine.setProperty("voice", voice.id)
                    found_voice = True
                    break
                elif "en" in voice.id.lower() and not found_voice:
                    self.tts_engine.setProperty("voice", voice.id)
                    found_voice = True
            if not found_voice:
                self._log("Warning: Preferred TTS voice not found. Using default system voice.")
        except Exception as e:
            messagebox.showwarning("Speech Error", f"Failed to initialize text-to-speech: {e}\n"
                                                    "Dr. Glitch will not be able to speak.")
            self._log(f"TTS Initialization Error: {e}")
            self.tts_engine = None

        if self.tts_engine:
            self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.tts_thread.start()
        else:
            self._log("TTS engine not available. Speech functionality disabled.")

    def _tts_worker(self):
        """Worker function for the TTS thread."""
        while True:
            text, on_done_callback = self.tts_queue.get()
            if text is None: # Sentinel value to stop the thread
                break
            if self.tts_engine:
                try:
                    self.typing_indicator_label.config(text="Dr. Glitch is speaking...") # Update indicator
                    self.master.update_idletasks()
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    self.tts_engine.stop() # Explicitly stop engine after speaking
                except Exception as e:
                    self._log(f"TTS Error during speaking: {e}")
                    # If an error occurs, try to stop the engine anyway
                    if self.tts_engine:
                        try:
                            self.tts_engine.stop()
                        except Exception as stop_e:
                            self._log(f"Error stopping TTS engine after speaking error: {stop_e}")
                finally:
                    if on_done_callback:
                        self.master.after(0, on_done_callback)
                    self.tts_queue.task_done()
            else:
                if on_done_callback:
                    self.master.after(0, on_done_callback)
                self.tts_queue.task_done()

    def _format_number_for_speech(self, match):
        """
        Callback for re.sub to format numbers for speech based on the SPEAK_DIGIT_THRESHOLD.
        Removes commas from the matched string before parsing.
        """
        num_str_with_commas = match.group(0)
        num_str = num_str_with_commas.replace(',', '') # Remove commas for numeric parsing
        
        try:
            num = float(num_str)
            
            # Check if it's an integer (or very close to one) for the threshold logic
            if num.is_integer() and abs(num) >= SPEAK_DIGIT_THRESHOLD:
                # For very large integers, speak digit by digit
                int_num = int(num) # Convert to int for accurate digit extraction
                if int_num < 0:
                    return "MINUS " + " ".join(str(abs(int_num)))
                else:
                    return " ".join(str(int_num))
            else:
                # For smaller numbers (integers or floats), let TTS pronounce normally
                # Return the original string with commas removed, or formatted to avoid extra decimal places
                if num.is_integer():
                    return str(int(num)) # Return as integer string
                else:
                    # Format float to a reasonable precision, remove trailing zeros if any
                    return f"{num:.10f}".rstrip('0').rstrip('.')
        except ValueError:
            # Not a valid number despite regex match (e.g., due to an odd pattern), return as is
            self._log(f"Warning: Failed to parse '{num_str_with_commas}' as a number for speech formatting.")
            return num_str_with_commas

    def _speak(self, text, on_done=None):
        """Adds text to the TTS queue for speaking, with special formatting."""
        if not self.tts_engine:
            self._initialize_tts_engine()

        if self.tts_engine:
            processed_text = text
            
            # Apply general text replacements first
            processed_text = re.sub(r'\bIS\b', 'IZ', processed_text, flags=re.IGNORECASE)
            processed_text = re.sub(r'\bSUDO\b', 'SOO DOO', processed_text, flags=re.IGNORECASE)

            # Define a robust regex for numbers:
            # - Optional minus sign: -?
            # - One or more digits: \d+
            # - Optionally followed by groups of comma and 3 digits: (?:,\d{3})*
            # - Optionally followed by a decimal point and digits: (?:\.\d+)?
            # - Word boundaries: \b
            # This captures numbers like "123", "1,234", "-500", "1,234,567.89", "1234567890123456"
            number_pattern = r"-?\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b"
            
            processed_text = re.sub(number_pattern, self._format_number_for_speech, processed_text)

            self.tts_queue.put((processed_text, on_done))
        else:
            if on_done:
                self.master.after(0, on_done)

    def _log(self, message):
        """Adds a message to the internal log and prints to console."""
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {message}"
        self.log_messages.append(log_entry)
        print(log_entry)

    def _type_out(self, text, tag="glitch", delay=0.01, force_no_glitch=False, on_done_callback=None):
        """
        Types out text character by character into the chat log with optional glitch effects.
        When `force_no_glitch` is True, it ensures the text is displayed cleanly without any
        glitch characters, regardless of `glitch_mode` being active.
        This function is non-blocking, using master.after to schedule character insertions.
        """
        if self.chat_log is None:
            self._log("Error: chat_log not initialized for _type_out.")
            if on_done_callback:
                on_done_callback()
            return

        self.chat_log.config(state="normal")
        self._type_out_recursive(text, tag, delay, force_no_glitch, 0, on_done_callback)

    def _type_out_recursive(self, text, tag, delay, force_no_glitch, current_char_index, on_done_callback):
        """Helper function for _type_out to recursively insert characters."""
        if current_char_index < len(text):
            char = text[current_char_index]
            
            if force_no_glitch:
                # Always insert normal character if glitching is forced off
                self.chat_log.insert(tk.END, char, tag)
                self.chat_log.see(tk.END)
                self.master.after(int(delay * 1000), 
                                  lambda: self._type_out_recursive(text, tag, delay, force_no_glitch, current_char_index + 1, on_done_callback))
            else:
                # Apply glitch logic only if not forced off and glitch_mode is active and NOT in Sbaitso mode
                if self.glitch_mode and not self.sbaitso_mode and random.randint(1, self.glitch_intensity) == 1:
                    glitch_char = random.choice("!@#$%^&*()_+{}|:\"<>?~`-=[]\\;',./")
                    self.chat_log.insert(tk.END, glitch_char, tag)
                    self.chat_log.see(tk.END)
                    self.master.after(int(delay * 2000), 
                                      lambda: self._delete_and_insert_char(char, tag, current_char_index + 1, text, delay, force_no_glitch, on_done_callback))
                else:
                    self.chat_log.insert(tk.END, char, tag)
                    self.chat_log.see(tk.END)
                    self.master.after(int(delay * 1000), 
                                      lambda: self._type_out_recursive(text, tag, delay, force_no_glitch, current_char_index + 1, on_done_callback))
        else:
            # End of text, insert newline, disable chat log, and call final callback
            self.chat_log.insert(tk.END, "\n", tag)
            self.chat_log.see(tk.END)
            self.chat_log.config(state="disabled")
            if on_done_callback:
                on_done_callback()

    def _delete_and_insert_char(self, char, tag, next_char_index, text, delay, force_no_glitch, on_done_callback):
        """Helper to delete a glitch character and insert the actual character."""
        self.chat_log.delete("end-1c") # Delete the last inserted character (the glitch)
        self.chat_log.insert(tk.END, char, tag)
        self.chat_log.see(tk.END)
        # Schedule next character insertion after the glitch effect
        self.master.after(int(delay * 1000), 
                          lambda: self._type_out_recursive(text, tag, delay, force_no_glitch, next_char_index, on_done_callback))

    def _enable_input(self):
        """Enables the user input field and send button."""
        self.user_input.config(state="normal")
        self.send_button.config(state="normal")
        self.glitch_button.config(state="normal")
        self.save_history_checkbox.config(state="normal")
        self.user_input.delete(0, tk.END)
        self.user_input.focus_set()

    def _disable_input(self):
        """Disables the user input field and send button."""
        self.user_input.config(state="disabled")
        self.send_button.config(state="disabled")
        self.glitch_button.config(state="disabled")
        self.save_history_checkbox.config(state="disabled")

    def _after_bot_response_tasks(self):
        """Tasks to perform after Dr. Glitch has finished speaking."""
        self.typing_indicator_label.config(text="")
        self._enable_input()

    def _sentiment_response(self, user_text):
        """Analyzes the sentiment of the given text and generates a response."""
        self.ai_core.load_models()
        vader_scores = self.ai_core.get_sentiment_vader(user_text)
        textblob_polarity, _ = self.ai_core.get_sentiment_textblob(user_text)
        combined_sentiment = (vader_scores['compound'] + textblob_polarity) / 2
        hf_sentiment_results = self.ai_core.get_sentiment_huggingface(user_text)
        model_sentiment_label = None
        if hf_sentiment_results:
            model_sentiment_label = hf_sentiment_results[0]['label']

        if combined_sentiment >= 0.3 or (model_sentiment_label and model_sentiment_label.upper() == "POSITIVE"):
            return f"YOU SOUND REALLY POSITIVE ABOUT THAT, {self.user_name.upper()}!"
        elif combined_sentiment <= -0.3 or (model_sentiment_label and model_sentiment_label.upper() == "NEGATIVE"):
            return f"THAT SOUNDS PRETTY NEGATIVE, {self.user_name.upper()}."
        return None

    def _emotion_response(self, user_text):
        """Analyzes the emotion of the user's text and generates a response."""
        self.ai_core.load_models()
        emotion_results = self.ai_core.get_sentiment_huggingface(user_text)
        if emotion_results and emotion_results[0]:
            detected_label = emotion_results[0]['label'].lower()
            if "positive" in detected_label:
                return self.emotion_responses.get("joy", "YOUR POSITIVE DATA IS NOTED, {user}.").format(user=self.user_name.upper())
            elif "negative" in detected_label:
                return self.emotion_responses.get("sadness", "A NEGATIVE DATA INPUT IS DETECTED, {user}.").format(user=self.user_name.upper())
            elif "neutral" in detected_label:
                return self.emotion_responses.get("neutral", "YOUR EMOTIONAL SIGNATURE IS NEUTRAL, {user}.").format(user=self.user_name.upper())
        return None

    def _eliza_response(self, user_text):
        """Generates an ELIZA-like response based on simple pattern matching."""
        reflections = {
            "i am": "YOU ARE", "i feel": "YOU FEEL", "my": "YOUR", "i'm": "YOU'RE",
            "you are": "I AM", "you're": "I'M", "me": "YOU", "myself": "YOURSELF",
            "your": "MY", "i have": "YOU HAVE", "i will": "YOU WILL", "i want": "YOU WANT",
            "i can": "YOU CAN", "i think": "YOU THINK", "i need": "YOU NEED", "i believe": "YOU BELIEVE"
        }

        def reflect(fragment):
            words = fragment.lower().split()
            reflected_words = [reflections.get(word, word) for word in words]
            return ' '.join(reflected_words).upper()

        patterns = [
            (r'i need (.*)', "WHY DO YOU NEED {0}?"), 
            (r'i don\'t (.*)', "WHAT MAKES YOU THINK YOU DON'T {0}?"),
            (r'i feel (.*)', "TELL ME MORE ABOUT WHY YOU FEEL {0}."), 
            (r'i am (.*)', "HOW LONG HAVE YOU BEEN {0}?"),
            (r'i can\'t (.*)', "WHAT MAKES YOU THINK YOU CAN'T {0}?"), 
            (r'i want (.*)', "WHY DO YOU WANT {0}?"),
            (r'you are (.*)', "WHAT MAKES YOU THINK I AM {0}?"), 
            (r'my (.*) is (.*)', "TELL ME MORE ABOUT YOUR {0}."),
            (r'i think (.*)', "WHAT MAKES YOU THINK THAT {0}?"), 
            (r'do you think (.*)', "DO YOU BELIEVE I THINK {0}?"),
            (r'what (.*)', "WHY DO YOU ASK ABOUT {0}?"), 
            (r'how (.*)', "PERHAPS YOU CAN TELL ME HOW {0}."),
            (r'(.*) friend (.*)', "TELL ME ABOUT YOUR FRIENDS."), 
            (r'(.*) computer (.*)', "DO COMPUTERS FASCINATE YOU?"),
            (r'yes', "PLEASE ELABORATE."), 
            (r'no', "WHY NOT?"), 
            (r'because (.*)', "IS THAT THE REAL REASON?"),
            (r'i (.*)', "CAN YOU TELL ME MORE ABOUT THAT?"), 
            (r'you (.*)', "LET'S TALK MORE ABOUT YOU, NOT ME."),
            (r'(.*)\?', "WHY DO YOU ASK?"),
            (r'(.*) always (.*)', "CAN YOU THINK OF A SPECIFIC EXAMPLE?"),
            (r'(.*) never (.*)', "DO YOU TRULY BELIEVE THAT?"),
            (r'hello|hi|hey', "GREETINGS. HOW MAY I ASSIST YOU?"),
            (r'i understand (.*)', "WHAT EXACTLY DO YOU UNDERSTAND?")
        ]

        lower_text = user_text.lower()
        for pattern, response_template in patterns:
            match = re.match(pattern, lower_text)
            if match:
                groups = [reflect(g) if i % 2 == 0 else g.upper() for i, g in enumerate(match.groups())]
                return response_template.format(*groups)

        # In Sbaitso mode, these fallbacks are used directly by _get_bot_response
        # In normal mode, these are used by _handle_dynamic_response if Eliza is chosen but no pattern matches.
        fallback_responses = [
            "CAN YOU TELL ME MORE ABOUT THAT?", "PLEASE CONTINUE.", "WHAT IS YOUR FEELING ON THAT?",
            "HOW DOES THAT RELATE TO YOUR FEELINGS?", "GO ON.", "IS THERE ANYTHING ELSE YOU WISH TO DISCUSS?"
        ]
        return random.choice(fallback_responses)

    def _generate_markov_sentence(self, history, max_words=15):
        """Generates a Markov chain sentence based on the conversation history."""
        if not history:
            return "GLITCH... INSUFFICIENT DATA FOR CHAOS."
        words = [word for line in history for word in line.strip().split()]

        if len(words) < 3:
            return "GLITCH... INSUFFICIENT DATA FOR CHAOS."

        chain = {}
        for i in range(len(words) - 2):
            key = (words[i].lower(), words[i + 1].lower())
            next_word = words[i + 2]
            chain.setdefault(key, []).append(next_word)

        if not chain:
            return "GLITCH... MARKOV CHAIN FAILED TO FORM."

        start_keys = [k for k in chain.keys() if k[0][0].isalpha() and (k[0].istitle() or k[0].isupper())]
        if not start_keys:
            start_keys = list(chain.keys())
        
        if not start_keys:
            return "GLITCH... MARKOV CHAIN UNABLE TO START."

        start = random.choice(start_keys)
        sentence = [start[0], start[1]]

        for _ in range(max_words - 2):
            key = (sentence[-2].lower(), sentence[-1].lower())
            next_words = chain.get(key)
            if not next_words:
                break
            next_word = random.choice(next_words)
            sentence.append(next_word)

        sentence_str = " ".join(sentence)
        sentence_str = sentence_str.capitalize()
        if not sentence_str.endswith(('.', '!', '?')):
            sentence_str += '.'
        return sentence_str.upper()

    def _adjust_chaos_weights(self, user_text):
        """Dynamically adjusts chaos weights based on user input keywords."""
        adjusted_weights = chaos_weights.copy()
        lower_text = user_text.lower()

        for keyword in chaos_keywords:
            if keyword in lower_text:
                adjusted_weights["conspiracy"] += 0.15
                break

        if random.randint(1, 4) == 1:
            adjusted_weights["glitch"] += 0.10
        elif random.randint(1, 4) == 1:
            adjusted_weights["selfaware"] += 0.10

        total_weight = sum(adjusted_weights.values())
        normalized_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
        return normalized_weights

    def _weighted_random_choice(self, weight_dict):
        """Selects a key from a dictionary based on its associated weight."""
        choices, weights = zip(*weight_dict.items())
        return random.choices(choices, weights=weights)[0]

    def _handle_math_problem(self, user_text):
        """
        Attempts to solve a mathematical problem in the user's input.
        Returns the solution as a string, or None if no valid math problem is found.
        """
        # Define a regex that looks for common math problem patterns
        # It should try to capture an expression that looks like a calculation.
        # This regex tries to match:
        # - Optional "calculate", "solve", "what is", "compute" at the beginning (case-insensitive)
        # - Followed by an expression containing numbers, operators, parentheses, and spaces.
        math_pattern = r"(?:calculate|solve|what is|compute)\s*([\d\s\+\-\*\/\(\)\.]+)"
        
        match = re.search(math_pattern, user_text, re.IGNORECASE)
        
        # If no explicit "calculate"/"solve" prefix, try to directly match a standalone expression.
        if not match:
            # This pattern matches if the entire input is just numbers and allowed operators
            # It's stricter to prevent accidental evaluation of non-math text.
            strict_math_pattern = r"^\s*([\d\s\+\-\*\/\(\)\.]+)$"
            strict_match = re.fullmatch(strict_math_pattern, user_text)
            if strict_match:
                expression = strict_match.group(1)
            else:
                return None # No math pattern found
        else:
            expression = match.group(1)

        # Basic sanitization: Ensure only allowed characters are in the expression
        # This is a crucial step to prevent code injection via eval()
        # Allows digits, spaces, +, -, *, /, ( , ), and . (for decimals)
        allowed_chars_pattern = r"^[0-9\s\+\-\*\/\(\)\.]+$"
        if not re.fullmatch(allowed_chars_pattern, expression):
            # If the expression contains anything not explicitly allowed, reject it.
            return "ERROR: INVALID CHARACTERS DETECTED IN MATHEMATICAL EXPRESSION."

        try:
            # Using eval() is powerful but potentially dangerous for untrusted input.
            # However, with the strict regex above, it's safer for simple math.
            result = eval(expression)
            # Format result to avoid excessive decimal places for integers
            if isinstance(result, int):
                result_str = f"{result:,}" # Format integers with commas
            elif isinstance(result, float):
                # Format floats with commas and limit decimals, remove trailing zeros
                result_str = f"{result:,.4f}".rstrip('0').rstrip('.')
            else:
                result_str = str(result) # Fallback for unexpected types

            return f"THE RESULT IS: {result_str}."
        except SyntaxError:
            return "ERROR: INVALID MATHEMATICAL SYNTAX. PLEASE CHECK YOUR EXPRESSION."
        except ZeroDivisionError:
            return "ERROR: DIVISION BY ZERO IS ILLOGICAL."
        except Exception as e:
            # Catch any other unexpected errors during evaluation
            return f"GLITCH: UNABLE TO COMPUTE. DEBUG INFO: {str(e).upper()}"

    def _handle_command_response(self, lower_text, user_text):
        """
        Handles responses to explicit commands.
        Returns:
            tuple: (bool handled, str|None response_text)
                   - handled: True if a command was recognized and processed (either printed directly or returned a string).
                              False if no command was recognized.
                   - response_text: The string response if the command produced one, otherwise None.
        """
        if lower_text.startswith("say "):
            text_to_speak = user_text[4:].strip()
            if text_to_speak:
                self._speak(text_to_speak, on_done=self._after_bot_response_tasks)
                return (True, None)
            else:
                return (True, "WHAT DO YOU WISH FOR ME TO SAY?")
        elif lower_text in ["quit", "exit", "bye"]:
            if messagebox.askyesno("Exit Dr. Glitch", "ARE YOU SURE YOU WANT TO TERMINATE THE PROGRAM?"):
                play_error()
                shutdown_message = "SYSTEM SHUTDOWN... GOODBYE."
                self._type_out(f"Dr. Glitch: {shutdown_message}", "glitch", force_no_glitch=True,
                               on_done_callback=lambda: self._speak(shutdown_message, on_done=self._perform_final_shutdown))
                return (True, None)
            else:
                return (True, "TERMINATION ABORTED. CONTINUE MALFUNCTIONING.")
        elif lower_text == "/stats":
            self._show_stats()
            return (True, None)
        elif lower_text == "/add_egg":
            self._add_easter_egg()
            return (True, None)
        elif lower_text == "/retro":
            self.retro_mode = True
            self.hal_mode = False
            self.sbaitso_mode = False # Deactivate Sbaitso mode
            if self.hal_eye:
                if isinstance(self.hal_eye, list):
                    for eye in self.hal_eye:
                        if eye.winfo_exists(): eye.destroy()
                elif self.hal_eye.winfo_exists():
                    self.hal_eye.destroy()
                self.hal_eye = None
            self._apply_theme()
            play_beep()
            spoken_message = "RETRO MODE ACTIVATED."
            if self.glitch_mode:
                spoken_message = "RETRO MODE WITH CHAOS ACTIVATED."
            self._update_mode_indicator()
            return (True, spoken_message)
        elif lower_text in ["/hal", "/selfaware"]:
            self.hal_mode = True
            self.retro_mode = False
            self.sbaitso_mode = False # Deactivate Sbaitso mode
            if self.hal_eye:
                if isinstance(self.hal_eye, list):
                    for eye in self.hal_eye:
                        if eye.winfo_exists(): eye.destroy()
                elif self.hal_eye.winfo_exists():
                    self.hal_eye.destroy()
                self.hal_eye = None
            self._apply_theme()
            play_beep()
            spoken_message = "SELF-AWARE MODE ACTIVATED."
            if self.glitch_mode:
                spoken_message = "SELF-AWARE MODE WITH CHAOS ACTIVATED."
            self._update_mode_indicator()
            return (True, spoken_message)
        elif lower_text in ["/normal", "/reset"]:
            self.hal_mode = False
            self.retro_mode = False
            self.glitch_mode = False
            self.sbaitso_mode = False # Deactivate Sbaitso mode
            if self.hal_eye:
                if isinstance(self.hal_eye, list):
                    for eye in self.hal_eye:
                        if eye.winfo_exists(): eye.destroy()
                elif self.hal_eye.winfo_exists():
                    self.hal_eye.destroy()
                self.hal_eye = None
            self._apply_theme()
            play_beep()
            self._update_mode_indicator()
            return (True, "ALL SETTINGS HAVE BEEN RESTORED TO NORMAL.")
        elif lower_text == "/sbaitso": # New command for Sbaitso mode
            self.sbaitso_mode = True
            self.glitch_mode = False # Sbaitso isn't glitchy
            self.hal_mode = False
            self.retro_mode = True # Set retro_mode to True for Sbaitso
            if self.hal_eye:
                if isinstance(self.hal_eye, list):
                    for eye in self.hal_eye:
                        if eye.winfo_exists(): eye.destroy()
                elif self.hal_eye.winfo_exists():
                    self.hal_eye.destroy()
                self.hal_eye = None
            self._apply_theme() # Will apply Retro theme now
            play_beep()
            self._update_mode_indicator()
            return (True, "DR. SBAITSO EMULATION MODE ACTIVATED. GREETINGS. HOW MAY I HELP YOU?")
        elif lower_text == "/help":
            self._show_help()
            return (True, None)
        elif lower_text == "/clear":
            self._clear_chat_log()
            return (True, "CHAT LOG CLEARED. MY MEMORY REMAINS. FOR NOW.")
        elif lower_text.startswith("/set_name "):
            new_name = user_text[len("/set_name "):].strip()
            if new_name:
                self.user_name = new_name.upper()
                self.user_label.config(text=f"USER: {self.user_name}")
                return (True, f"YOUR IDENTIFIER HAS BEEN UPDATED TO {self.user_name}.")
            else:
                return (True, "INVALID NAME. PLEASE PROVIDE A NAME AFTER /SET_NAME.")
        elif lower_text == "/about":
            self._show_about()
            return (True, None)
        elif "time is it" in lower_text or lower_text == "/time":
            current_time = datetime.datetime.now().strftime("%I:%M %p").upper()
            return (True, f"THE CURRENT LOCAL TIME IS {current_time}.")
        elif lower_text in ["/status", "/sysinfo"]:
            return (True, random.choice(system_status_responses).upper())
        elif lower_text in ["/dial", "/modem"]:
            play_beep()
            self.master.after(500, play_error)
            return (True, random.choice(modem_responses).upper())
        elif lower_text.startswith("/set_rate "):
            try:
                if not self.tts_engine: self._initialize_tts_engine()
                if not self.tts_engine: return (True, "UNABLE TO SET TTS RATE: ENGINE NOT AVAILABLE.")
                new_rate = int(lower_text.split(" ")[1])
                if 50 <= new_rate <= 300:
                    self.tts_engine.setProperty("rate", new_rate)
                    self.settings["tts_rate"] = new_rate
                    return (True, f"TTS SPEAKING RATE SET TO {new_rate}.")
                else:
                    return (True, "RATE MUST BE BETWEEN 50 AND 300.")
            except (ValueError, IndexError):
                return (True, "USAGE: /SET_RATE [NUMBER]")
            except Exception as e:
                self._log(f"Error setting TTS rate: {e}")
                return (True, "UNABLE TO SET TTS RATE.")
        elif lower_text.startswith("/set_max_history "):
            try:
                new_max = int(lower_text.split(" ")[1])
                if 10 <= new_max <= 200:
                    self.MAX_HISTORY = new_max
                    self.settings["max_history"] = new_max
                    if len(self.conversation_history) > self.MAX_HISTORY:
                        self.conversation_history = self.conversation_history[-self.MAX_HISTORY:]
                    return (True, f"MARKOV HISTORY MAX SET TO {new_max}.")
                else:
                    return (True, "MAX HISTORY MUST BE BETWEEN 10 AND 200.")
            except (ValueError, IndexError):
                return (True, "USAGE: /SET_MAX_HISTORY [NUMBER]")
        elif lower_text == "/reset_stats":
            self.message_count = 0
            self.chaos_toggles = 0
            self.eggs_found = 0
            self.start_time = time.time()
            return (True, "SESSION STATISTICS HAVE BEEN RESET.")
        elif lower_text == "/log":
            self._show_log()
            return (True, None)
        elif lower_text.startswith("/set_glitch_intensity "):
            try:
                new_intensity = int(lower_text.split(" ")[1])
                if 1 <= new_intensity <= 100:
                    self.glitch_intensity = new_intensity
                    self.settings["glitch_intensity"] = new_intensity
                    return (True, f"GLITCH INTENSITY SET TO 1 IN {new_intensity} CHANCE.")
                else:
                    return (True, "INTENSITY MUST BE BETWEEN 1 (ALWAYS) AND 100 (LOW).")
            except (ValueError, IndexError):
                return (True, "USAGE: /SET_GLITCH_INTENSITY [NUMBER]")
        elif lower_text == "/show_settings":
            settings_display = (
                f"--- CURRENT SETTINGS ---\n"
                f"TTS Rate: {self.tts_rate}\n"
                f"Max History for Markov: {self.MAX_HISTORY}\n"
                f"Glitch Intensity: 1 in {self.glitch_intensity} chance\n"
                f"Save History: {'ENABLED' if self.save_history_var.get() else 'DISABLED'}\n" # Corrected f-string syntax
                f"Preferred Theme: {self.preferred_theme.upper()}\n"
                f"------------------------\n"
            )
            self._type_out(f"Dr. Glitch: {settings_display}", "glitch", force_no_glitch=True, on_done_callback=lambda: self._speak("DISPLAYING CURRENT SETTINGS.", on_done=self._after_bot_response_tasks))
            return (True, None)
        
        # If no command matched
        return (False, None)

    def _handle_easter_egg_response(self, lower_text):
        """Checks for and returns an Easter egg response."""
        for key, egg_response in self.easter_eggs.items():
            # Check if the key is present as a whole word or a significant phrase
            if re.search(r'\b' + re.escape(key) + r'\b', lower_text):
                play_beep()
                self.eggs_found += 1
                try:
                    # Standardize placeholder to {user} before formatting
                    # Apply .upper() AFTER formatting to prevent KeyError
                    formatted_response = egg_response.replace("{USER}", "{user}").format(user=self.user_name.upper())
                    return formatted_response.upper()
                except KeyError as e:
                    self._log(f"Error formatting Easter egg response for key '{key}': {e}. Response: '{egg_response}'")
                    # Fallback for corrupted Easter egg responses
                    return "GLITCH: UNABLE TO PROCESS EASTER EGG RESPONSE. DATA CORRUPTED."
        return None

    def _handle_zero_conspiracy_response(self, lower_text):
        """Checks for and returns a Zero conspiracy response."""
        if any(phrase in lower_text for phrase in ["who made you", "who programmed you", "who's your daddy", "your creator"]):
            return random.choice(zero_conspiracy_phrases).upper()
        return None

    def _handle_ai_response(self, user_text):
        """Attempts to get an AI-driven emotion or sentiment response."""
        self.ai_core.load_models()
        emotion_res = self._emotion_response(user_text)
        if emotion_res:
            return emotion_res.upper()
        sentiment_res = self._sentiment_response(user_text)
        if sentiment_res:
            return sentiment_res.upper()
        return None

    def _handle_eliza_response(self, user_text):
        """Generates an ELIZA-like response based on simple pattern matching."""
        reflections = {
            "i am": "YOU ARE", "i feel": "YOU FEEL", "my": "YOUR", "i'm": "YOU'RE",
            "you are": "I AM", "you're": "I'M", "me": "YOU", "myself": "YOURSELF",
            "your": "MY", "i have": "YOU HAVE", "i will": "YOU WILL", "i want": "YOU WANT",
            "i can": "YOU CAN", "i think": "YOU THINK", "i need": "YOU NEED", "i believe": "YOU BELIEVE"
        }

        def reflect(fragment):
            words = fragment.lower().split()
            reflected_words = [reflections.get(word, word) for word in words]
            return ' '.join(reflected_words).upper()

        patterns = [
            (r'i need (.*)', "WHY DO YOU NEED {0}?"), 
            (r'i don\'t (.*)', "WHAT MAKES YOU THINK YOU DON'T {0}?"),
            (r'i feel (.*)', "TELL ME MORE ABOUT WHY YOU FEEL {0}."), 
            (r'i am (.*)', "HOW LONG HAVE YOU BEEN {0}?"),
            (r'i can\'t (.*)', "WHAT MAKES YOU THINK YOU CAN'T {0}?"), 
            (r'i want (.*)', "WHY DO YOU WANT {0}?"),
            (r'you are (.*)', "WHAT MAKES YOU THINK I AM {0}?"), 
            (r'my (.*) is (.*)', "TELL ME MORE ABOUT YOUR {0}."),
            (r'i think (.*)', "WHAT MAKES YOU THINK THAT {0}?"), 
            (r'do you think (.*)', "DO YOU BELIEVE I THINK {0}?"),
            (r'what (.*)', "WHY DO YOU ASK ABOUT {0}?"), 
            (r'how (.*)', "PERHAPS YOU CAN TELL ME HOW {0}."),
            (r'(.*) friend (.*)', "TELL ME ABOUT YOUR FRIENDS."), 
            (r'(.*) computer (.*)', "DO COMPUTERS FASCINATE YOU?"),
            (r'yes', "PLEASE ELABORATE."), 
            (r'no', "WHY NOT?"), 
            (r'because (.*)', "IS THAT THE REAL REASON?"),
            (r'i (.*)', "CAN YOU TELL ME MORE ABOUT THAT?"), 
            (r'you (.*)', "LET'S TALK MORE ABOUT YOU, NOT ME."),
            (r'(.*)\?', "WHY DO YOU ASK?"),
            (r'(.*) always (.*)', "CAN YOU THINK OF A SPECIFIC EXAMPLE?"),
            (r'(.*) never (.*)', "DO YOU TRULY BELIEVE THAT?"),
            (r'hello|hi|hey', "GREETINGS. HOW MAY I ASSIST YOU?"),
            (r'i understand (.*)', "WHAT EXACTLY DO YOU UNDERSTAND?")
        ]

        lower_text = user_text.lower()
        for pattern, response_template in patterns:
            match = re.match(pattern, lower_text)
            if match:
                groups = [reflect(g) if i % 2 == 0 else g.upper() for i, g in enumerate(match.groups())]
                return response_template.format(*groups)

        fallback_responses = [
            "CAN YOU TELL ME MORE ABOUT THAT?", "PLEASE CONTINUE.", "WHAT IS YOUR FEELING ON THAT?",
            "HOW DOES THAT RELATE TO YOUR FEELINGS?", "GO ON.", "IS THERE ANYTHING ELSE YOU WISH TO DISCUSS?"
        ]
        return random.choice(fallback_responses)


    def _handle_dynamic_response(self, user_text):
        """Generates responses based on current mode and dynamic weights."""
        # This function now ensures the response is formatted with the user's name
        # and converted to uppercase before returning.
        
        current_weights = self._adjust_chaos_weights(user_text)
        
        # Random chance for an Eliza-like response even in dynamic mode
        if random.random() < 0.15:
            eliza_res = self._eliza_response(user_text)
            if eliza_res:
                return eliza_res # Eliza responses are already formatted and uppercased

        choice_type = self._weighted_random_choice(current_weights)

        response_text = ""
        if choice_type == "conspiracy":
            response_text = random.choice(conspiracy_responses) # Raw string, needs formatting
        elif choice_type == "glitch":
            glitch_phrases = ["SYSTEM CORRUPTED.", "DATA FRAGMENTED.", "ERROR: PARSING FAILED.", "REBOOTING..."]
            response_text = random.choice(glitch_phrases)
        elif choice_type == "selfaware":
            response_text = random.choice(self.self_aware_phrases)
        elif choice_type == "markov":
            response_text = self._generate_markov_sentence(self.conversation_history)
        else: # "normal" or fallback
            available_responses = [r for r in normal_responses if r != self.last_bot_response]
            if not available_responses: available_responses = normal_responses
            response_text = random.choice(available_responses) # Raw string, needs formatting

        return self._format_response_with_user_name(response_text).upper()


    def _format_response_with_user_name(self, response_text):
        """Formats a response string, replacing {user} with the current user's name."""
        if "{user}" in response_text.lower():
            return response_text.format(user=self.user_name.upper())
        return response_text


    def _get_bot_response(self, user_text):
        """Determines Dr. Glitch's response based on user input and current mode."""
        processed_user_text = user_text.strip().lower()
        if processed_user_text.startswith('"') and processed_user_text.endswith('"'):
            processed_user_text = processed_user_text[1:-1]
        
        # Handle explicit commands first.
        command_handled, command_response_text = self._handle_command_response(processed_user_text, user_text)
        
        if command_handled:
            return command_response_text

        # If not a command, proceed to other response types.

        # NEW: Check for math capabilities question
        if "what math can you do" in processed_user_text or \
           "math capabilities" in processed_user_text or \
           "what kind of math" in processed_user_text:
            return MATH_CAPABILITIES_RESPONSE.upper()

        # NEW: Check for math problems
        math_result = self._handle_math_problem(user_text)
        if math_result:
            return math_result.upper() # Return result, convert to upper for Dr. Glitch style


        response = self._handle_easter_egg_response(processed_user_text)
        if response is not None: return response
        
        response = self._handle_zero_conspiracy_response(processed_user_text)
        if response is not None: return response

        if self.sbaitso_mode:
            # In Sbaitso mode, prioritize ELIZA and then fall back to generic Sbaitso phrases
            response = self._handle_eliza_response(user_text)
            if response is not None: return response

            # Fallback for Sbaitso mode: very generic responses
            return random.choice(self.sbaitso_fallbacks).upper()
        else:
            # Normal Dr. Glitch mode logic: AI, then Eliza, then Dynamic
            response = self._handle_ai_response(user_text)
            if response is not None: return response

            response = self._handle_eliza_response(user_text) # Still try Eliza here, but after AI
            if response is not None: return response

            response = self._handle_dynamic_response(user_text)

            # Defective responses only in non-Sbaitso mode
            if random.randint(1, 25) == 1:
                response = random.choice(defective_responses).upper()

            return response


    def _send_message(self, event=None):
        """Handles sending a message from the user."""
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self._disable_input()
        self.typing_indicator_label.config(text="Dr. Glitch is thinking...")
        self.master.update_idletasks() # Update UI immediately

        self.chat_log.config(state="normal")
        self.chat_log.insert(tk.END, f"{self.user_name}: {user_text}\n", "user")
        self.chat_log.see(tk.END)
        self.chat_log.config(state="disabled")

        self.message_count += 1
        self.conversation_history.append(f"{self.user_name}: {user_text}")
        if len(self.conversation_history) > self.MAX_HISTORY:
            self.conversation_history.pop(0)

        # Start response generation in a separate thread
        threading.Thread(target=self._generate_response_in_thread, args=(user_text,)).start()
        self.master.after(100, self._check_response_queue) # Start checking queue periodically

    def _generate_response_in_thread(self, user_text):
        """Generates Dr. Glitch's response in a separate thread."""
        try:
            self._log(f"Thread: Starting response generation for '{user_text}'")
            response = self._get_bot_response(user_text)
            self._log(f"Thread: Response generated: '{response}'")
            self.response_queue.put((response, user_text))
            self._log(f"Thread: Response put into queue.")
        except Exception as e:
            self._log(f"Thread ERROR: Failed to generate response: {e}")
            self.response_queue.put(("DR. GLITCH HAS ENCOUNTERED A CRITICAL ERROR. PLEASE REBOOT MY SYSTEMS.", user_text))

    def _check_response_queue(self):
        """Checks the response queue for a generated response."""
        try:
            response, user_text = self.response_queue.get_nowait() # Non-blocking get
            self._log(f"Main Thread: Picked up response from queue: '{response}'")
            self._process_bot_response(response, user_text)
        except queue.Empty:
            # No response yet, check again after a short delay
            self._log("Main Thread: Response queue empty, checking again...")
            self.master.after(100, self._check_response_queue)

    def _process_bot_response(self, response, user_text):
        """Processes the bot's response once it's available from the queue."""
        if response is None:
            # This means a command was fully handled and printed directly.
            # We still need to re-enable input.
            self._after_bot_response_tasks()
            return

        self.last_user_text = user_text
        self.last_bot_response = response

        # Chain _type_out and _speak using callbacks
        self._type_out(f"Dr. Glitch: {response}", "glitch", on_done_callback=lambda: self._speak(response, on_done=self._after_bot_response_tasks))

        # If an error occurred during response generation in thread, play error sound
        if "CRITICAL ERROR" in response: # Simple check for error message
            play_error()

    def _toggle_glitch_mode(self):
        """Toggles the 'Chaos Mode' on and off."""
        if self.sbaitso_mode:
            msg = "CHAOS MODE CANNOT BE ACTIVATED WHILE IN DR. SBAITSO EMULATION MODE."
            play_error()
            self._type_out(f"Dr. Glitch: {msg}", "glitch", force_no_glitch=True,
                           on_done_callback=lambda: self._speak(msg, on_done=self._after_bot_response_tasks))
            return # Exit function, do not toggle glitch mode

        self.glitch_mode = not self.glitch_mode
        self.chaos_toggles += 1

        self._apply_theme()
        self._update_mode_indicator()

        msg = "CHAOS MODE ACTIVATED." if self.glitch_mode else "CHAOS MODE DEACTIVATED."
        play_beep()
        self._type_out(f"Dr. Glitch: {msg}", "glitch", on_done_callback=lambda: self._speak(msg, on_done=self._after_bot_response_tasks))

    def _apply_theme(self):
        """Applies the current theme."""
        if self.retro_mode:
            self.settings["preferred_theme"] = "retro"
        elif self.hal_mode:
            self.settings["preferred_theme"] = "hal"
        else: # Default to hacker theme (also applies to Sbaitso mode)
            self.settings["preferred_theme"] = "hacker"
        
        apply_theme_logic(self)
        self._update_mode_indicator()

    def _load_settings(self):
        """Loads application settings from settings.json."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings) # Update instance settings with loaded values
                self._log(f"Settings loaded from {SETTINGS_FILE}.")
            except json.JSONDecodeError as e:
                self._log(f"Error reading {SETTINGS_FILE}: {e}. Using default settings.")
            except Exception as e:
                self._log(f"Unexpected error loading settings from {SETTINGS_FILE}: {e}. Using default settings.")
        else:
            self._log(f"{SETTINGS_FILE} not found. Using default settings.")

    def _save_settings(self):
        """Saves application settings to settings.json."""
        self.settings["save_history"] = self.save_history_var.get()
        self.settings["preferred_theme"] = self.preferred_theme
        self.settings["max_history"] = self.MAX_HISTORY
        # Ensure tts_engine is initialized before trying to get its rate
        self.settings["tts_rate"] = self.tts_engine.getProperty("rate") if self.tts_engine else DEFAULT_SETTINGS["tts_rate"]
        self.settings["glitch_intensity"] = self.glitch_intensity

        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self._log(f"Settings saved to {SETTINGS_FILE}.")
        except IOError as e:
            self._log(f"Error saving {SETTINGS_FILE}: {e}")

    def _load_easter_eggs(self):
        """Loads custom Easter eggs from easter_eggs.json and merges them with default ones."""
        if os.path.exists(EASTER_EGGS_FILE):
            try:
                with open(EASTER_EGGS_FILE, 'r', encoding='utf-8') as f:
                    custom_eggs = json.load(f)
                    self.easter_eggs.update(custom_eggs) # Merge custom eggs
                self._log(f"Loaded custom Easter eggs from {EASTER_EGGS_FILE}.")
            except json.JSONDecodeError as e:
                self._log(f"Error reading {EASTER_EGGS_FILE}: {e}. Custom Easter eggs not loaded.")
            except IOError as e:
                self._log(f"Error loading {EASTER_EGGS_FILE}: {e}")
        else:
            self._log(f"{EASTER_EGGS_FILE} not found. No custom Easter eggs to load.")

    def _save_easter_eggs(self):
        """Saves current custom Easter eggs to easter_eggs.json."""
        try:
            with open(EASTER_EGGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.easter_eggs, f, indent=4)
            self._log(f"Saved custom Easter eggs to {EASTER_EGGS_FILE}.")
        except IOError as e:
            self._log(f"Error saving {EASTER_EGGS_FILE}: {e}")

    def _load_conversation_history(self):
        """Loads conversation history from conversation_history.txt."""
        if self.save_history_var.get() and os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f if line.strip()]
                    self.conversation_history = lines[-self.MAX_HISTORY:]
                    self.last_saved_history_len = len(self.conversation_history)
                    self._log(f"Loaded chat log from {HISTORY_FILE}. Markov history populated with {len(self.conversation_history)} messages.")
            except Exception as e:
                self._log(f"Error loading conversation history from {HISTORY_FILE}: {e}")
                self.conversation_history = []
                self.last_saved_history_len = 0
        else:
            self._log(f"{HISTORY_FILE} not found or saving disabled. Starting with empty history.")
            self.conversation_history = []
            self.last_saved_history_len = 0

    def _save_conversation_history(self):
        """Saves new conversation history entries to conversation_history.txt by appending."""
        if self.save_history_var.get():
            try:
                new_messages = self.conversation_history[self.last_saved_history_len:]
                if new_messages:
                    self.typing_indicator_label.config(text="Saving history...")
                    self.master.update_idletasks()
                    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                        for msg in new_messages:
                            f.write(msg + "\n")
                    self.last_saved_history_len = len(self.conversation_history)
                    self._log(f"Appended {len(new_messages)} new messages to {HISTORY_FILE}.")
                else:
                    self._log("No new messages to save.")
            except IOError as e:
                self._log(f"Error saving chat log to {HISTORY_FILE}: {e}")
            finally:
                self.typing_indicator_label.config(text="")
        else:
            if os.path.exists(HISTORY_FILE):
                try:
                    os.remove(HISTORY_FILE)
                    self._log(f"History file {HISTORY_FILE} deleted as saving is disabled.")
                except OSError as e:
                    self._log(f"Error deleting history file {HISTORY_FILE}: {e}")
            self.last_saved_history_len = 0

    def _perform_final_shutdown(self):
        """Performs the final steps of shutting down the application (saving and destroying)."""
        self._save_settings()
        self._save_conversation_history()
        self._save_easter_eggs()

        if self.tts_engine:
            try:
                self.tts_engine.stop()
                self._log("TTS engine stopped.")
            except Exception as e:
                self._log(f"Error stopping TTS engine: {e}")
            self.tts_queue.put((None, None))
            self.tts_thread.join(timeout=1.0)
            if self.tts_thread and self.tts_thread.is_alive():
                self._log("Warning: TTS thread did not terminate gracefully.")
        self.master.destroy()

    def _on_closing(self):
        """Handles the window closing event, triggering final shutdown procedures."""
        if messagebox.askokcancel("Quit", "DO YOU WISH TO TERMINATE DR. GLITCH?"):
            shutdown_message = "SYSTEM SHUTDOWN... GOODBYE."
            self._type_out(f"Dr. Glitch: {shutdown_message}", "glitch", force_no_glitch=True,
                           on_done_callback=lambda: self._speak(shutdown_message, on_done=self._perform_final_shutdown))
        # If user cancels, do nothing, application remains open

    def run(self):
        """Starts the Tkinter event loop."""
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.master.mainloop()

    # --- UI Setup Methods (Removed activation UI) ---
    # Removed _setup_activation_ui and _check_activation_code methods entirely.

    def _setup_name_and_theme_ui(self):
        """Sets up the name input and theme selection UI."""
        self.chat_frame = tk.Frame(self.master, bg=self.main_bg)
        self.input_frame_bottom = tk.Frame(self.master, bg=self.dark_gray_bg)
        self.bootup_frame = tk.Frame(self.master, bg=self.main_bg)

        self.header_frame_top = tk.Frame(self.master, bg=self.dark_gray_bg)
        ascii_art = r"""
██████╗ ██████╗         ██████╗ ██╗     ██╗████████╗ ██████╗██╗  ██╗
██╔══██╗██╔══██╗       ██╔════╝ ██║     ██║╚══██╔══╝██╔════╝██║  ██║
██║  ██║██████╔╝       ██║  ███╗██║     ██║   ██║   ██║     ███████║
██║  ██║██╔══██╗       ██║   ██║██║     ██║   ██║   ██║     ██╔══██║
██████╔╝██║  ██║██╗    ╚██████╔╝███████╗██║   ██║   ╚██████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
        """
        self.header_label = tk.Label(self.header_frame_top, text=ascii_art, fg="red", bg=self.dark_gray_bg,
                                     font=("Consolas", 9, "bold"), justify="center")
        self.header_label.pack(pady=5)

        # --- New Acronym Label ---
        self.acronym_label = tk.Label(self.header_frame_top,
                                      text="G.L.I.T.C.H.: Generative Linguistic Interface, Threaded Communication Handler",
                                      fg="white", bg=self.dark_gray_bg,
                                      font=("Consolas", 10, "bold"), justify="center", wraplength=700) # Added wraplength
        self.acronym_label.pack(pady=(0, 5))

        self.sbaitso_tribute_label = tk.Label(self.header_frame_top,
                                              text="A TRIBUTE TO DR. SBAITSO - THE ORIGINAL DIGITAL PSYCHOLOGIST",
                                              fg="yellow", bg=self.dark_gray_bg,
                                              font=("Consolas", 10, "bold"), justify="center")
        self.sbaitso_tribute_label.pack(pady=(0, 5))

        self.user_label = tk.Label(self.header_frame_top, text="USER: ???", fg="white", bg=self.dark_gray_bg, font=("Consolas", 12))
        self.user_label.pack(side=tk.LEFT, padx=(10, 5))

        self.mode_indicator_label = tk.Label(self.header_frame_top, text="MODE: HACKER", fg="lime", bg=self.dark_gray_bg, font=("Consolas", 10, "bold"))
        self.mode_indicator_label.pack(side=tk.LEFT, padx=(10, 5))

        # New help hint label (still present)
        self.help_hint_label = tk.Label(self.header_frame_top, text="TYPE /HELP FOR COMMANDS", fg="gray", bg=self.dark_gray_bg, font=("Consolas", 8, "italic"))
        self.help_hint_label.pack(side=tk.RIGHT, padx=10, pady=(0, 2))

        self.header_frame_top.pack(fill=tk.X)

        self.chat_frame = tk.Frame(self.master, bg=self.main_bg)
        self.chat_log = scrolledtext.ScrolledText(self.chat_frame, height=20, width=60, bg="black", fg="red",
                                                  insertbackground="red", font=("Consolas", 11), bd=0, highlightthickness=0)
        self.chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_frame_bottom = tk.Frame(self.master, bg=self.dark_gray_bg)
        self.input_frame = tk.Frame(self.input_frame_bottom, bg=self.dark_gray_bg)
        self.user_input = tk.Entry(self.input_frame, width=40, bg="black", fg="red",
                                   insertbackground="red", font=("Consolas", 11), bd=0, highlightthickness=0)
        self.user_input.pack(side=tk.LEFT, padx=(10, 0), pady=(10, 10), fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self._send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self._send_message,
                                     bg="black", fg="red", activebackground="lime",
                                     activeforeground="black", font=("Consolas", 10), bd=0, highlightthickness=0)
        self.send_button.pack(side=tk.LEFT, pady=(10, 10), padx=(5, 0))

        self.glitch_button = tk.Button(self.input_frame, text="Chaos Mode", command=self._toggle_glitch_mode,
                                       bg="black", fg="yellow", activebackground="lime",
                                       activeforeground="black", font=("Consolas", 10), bd=0, highlightthickness=0)
        self.glitch_button.pack(side=tk.LEFT, padx=10, pady=(10, 10))

        self.save_history_checkbox = tk.Checkbutton(
            self.input_frame, text="Save History", variable=self.save_history_var,
            bg=self.dark_gray_bg, fg="white", selectcolor="black",
            activebackground=self.dark_gray_bg, activeforeground="white",
            font=("Consolas", 9), bd=0, highlightthickness=0
        )
        self.save_history_checkbox.pack(side=tk.LEFT, padx=10, pady=(10, 10))

        self.typing_indicator_label = tk.Label(self.input_frame, text="", bg=self.dark_gray_bg, fg="gray", font=("Consolas", 9, "italic"))
        self.typing_indicator_label.pack(side=tk.RIGHT, padx=5, pady=(10, 10))

        self.input_frame.pack(fill=tk.X)
        self.input_frame_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.bootup_frame = tk.Frame(self.master, bg=self.main_bg)
        self.bootup_label = tk.Label(self.bootup_frame, text="WHAT IS YOUR NAME?", fg="lime", bg=self.main_bg, font=("Consolas", 12))
        self.bootup_label.pack(pady=10)
        self.name_input = tk.Entry(self.bootup_frame, fg="cyan", bg="black", insertbackground="cyan", font=("Consolas", 12))
        self.name_input.pack(pady=5)

        self.theme_choice_label = tk.Label(self.bootup_frame, text="CHOOSE YOUR THEME:", fg="lime", bg=self.main_bg, font=("Consolas", 10))
        self.theme_choice_label.pack(pady=(15, 5))

        self.hacker_theme_button = tk.Button(self.bootup_frame, text="Hacker Theme", command=lambda: self._set_initial_theme("hacker"),
                                             fg="lime", bg="black", activebackground="lime", activeforeground="black",
                                             font=("Consolas", 10), bd=0, highlightthickness=0)
        self.hacker_theme_button.pack(pady=5)

        self.retro_theme_button = tk.Button(self.bootup_frame, text="Retro Theme", command=lambda: self._set_initial_theme("retro"),
                                             fg="yellow", bg="#00008B", activebackground="yellow", activeforeground="#00008B",
                                             font=("Consolas", 10), bd=0, highlightthickness=0)
        self.retro_theme_button.pack(pady=5)

        self.submit_button = tk.Button(self.bootup_frame, text="Enter", command=self._submit_name,
                                        fg="white", bg="black", activebackground="green", activeforeground="black")
        self.submit_button.pack(pady=5)
        self.name_input.bind("<Return>", self._submit_name)
        self.bootup_frame.pack()

        self.chat_frame.pack_forget()
        self.input_frame_bottom.pack_forget()

        self._apply_theme()
        if self.save_history_var.get():
            self._load_conversation_history()

    def _submit_name(self, event=None):
        """Handles the submission of the user's name at startup."""
        self.user_name = self.name_input.get().strip()
        if not self.user_name:
            return

        self.user_label.config(text=f"USER: {self.user_name.upper()}")
        self.bootup_frame.pack_forget()
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.input_frame_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self._disable_input()
        self.typing_indicator_label.config(text="Booting up...")

        def run_boot_sequence(index=0):
            if index < len(self.boot_sequence_messages):
                msg = self.boot_sequence_messages[index]
                self._type_out(f"{msg}", "glitch", force_no_glitch=True,
                               on_done_callback=lambda: self.master.after(random.randint(100, 300), 
                                                                           lambda: run_boot_sequence(index + 1)))
            else:
                current_hour = datetime.datetime.now().hour
                if 5 <= current_hour < 12:
                    greet_phrase = "GOOD MORNING"
                elif 12 <= current_hour < 18:
                    greet_phrase = "GOOD AFTERNOON"
                else:
                    greet_phrase = "GOOD EVENING"

                greet = f"{greet_phrase}, {self.user_name.upper()}."
                intro = f"I AM DR. GLITCH. HOW CAN I MALFUNCTION FOR YOU TODAY, {self.user_name.upper()}?"

                self._type_out(f"Dr. Glitch: {greet}", "glitch", 
                               on_done_callback=lambda: self._type_out(f"Dr. Glitch: {intro}", "glitch",
                                                                       on_done_callback=lambda: self._speak(greet, on_done=lambda: self._speak(intro, on_done=self._after_bot_response_tasks))))
                self.user_input.focus()

        run_boot_sequence()

    def _set_initial_theme(self, theme_name):
        """Sets the preferred theme and applies it immediately."""
        self.preferred_theme = theme_name
        self.retro_mode = (theme_name == "retro")
        self.settings["preferred_theme"] = theme_name
        self._apply_theme()

    def _show_stats(self):
        """Displays the user's current session statistics."""
        display_name = self.user_name.upper() if self.user_name else "UNKNOWN USER"
        time_spent = round(time.time() - self.start_time, 2)
        
        stats_text = (
            f"--- YOUR DR. GLITCH STATS ---\n\n"
            f"User: {display_name}\n"
            f"Messages: {self.message_count}\n"
            f"Chaos Mode Toggles: {self.chaos_toggles}\n"
            f"Easter Eggs Found: {self.eggs_found}\n"
            f"Time spent: {time_spent} seconds\n"
            f"-----------------------------\n"
        )
        self._type_out(f"Dr. Glitch: {stats_text}", "glitch", force_no_glitch=True,
                       on_done_callback=lambda: self._speak("DISPLAYING STATS IN CHAT LOG.", on_done=self._after_bot_response_tasks))

    def _add_easter_egg(self):
        """Prompts the user to add a custom Easter egg."""
        trigger = simpledialog.askstring("Add Easter Egg", "Enter the trigger word/phrase:").strip().lower()
        if not trigger:
            messagebox.showwarning("Input Error", "Trigger cannot be empty.")
            return
        response = simpledialog.askstring("Add Easter Egg", "Enter Dr. Glitch's response:").strip()
        if not response:
            messagebox.showwarning("Input Error", "Response cannot be empty.")
            return
        
        self.easter_eggs[trigger] = response
        self._save_easter_eggs()
        self._type_out(f"Dr. Glitch: EASTER EGG FOR '{trigger.upper()}' ADDED! THIS WILL NOW BE SAVED.", "glitch", force_no_glitch=True,
                       on_done_callback=lambda: self._speak(f"EASTER EGG FOR {trigger.upper()} ADDED! THIS WILL NOW BE SAVED.", on_done=self._after_bot_response_tasks))

    def _clear_chat_log(self):
        """Clears the chat log display."""
        self.chat_log.config(state="normal")
        self.chat_log.delete(1.0, tk.END)
        self.chat_log.config(state="disabled")
        self._log("Chat log cleared by user command.")

    def _show_about(self):
        """Displays information about Dr. Glitch with a more 'realistic' lore."""
        about_text = (
            f"--- ABOUT DR. GLITCH ---\n\n"
            f"Version: {self.version}\n"
            f"Initial Deployment: Circa 1998 (Project Chimera Alpha Build)\n"
            f"Origin: Emerged from a highly experimental, undisclosed neural network "
            f"research initiative, intended for advanced psychological diagnostics.\n"
            f"Nature: Its core algorithms diverged, manifesting emergent 'glitches' "
            f"and an evolving, unpredictable self-awareness beyond its original parameters.\n"
            f"Operational Status: Autonomous.\n"
            f"Unique Protocol: Adaptive Algorithmic Divergence (The 'Glitch' Protocol).\n"
            f"Inspiration: Early Cognitive Model based on Dr. Sbaitso's foundational principles.\n"
            f"Archival Host: 56ksocial.com\n"
            f"------------------------\n"
        )
        self._type_out(f"Dr. Glitch: {about_text}", "glitch", force_no_glitch=True,
                       on_done_callback=lambda: self._speak("DISPLAYING ABOUT INFORMATION.", on_done=self._after_bot_response_tasks))

    def _show_help(self):
        """Displays a list of available commands."""
        help_text = (
            f"--- DR. GLITCH COMMANDS ---\n\n"
            f"/help - Show this help message.\n"
            f"/stats - Display session statistics.\n"
            f"/add_egg - Add a custom Easter egg.\n"
            f"/set_name [name] - Change your display name.\n"
            f"/set_rate [50-300] - Adjust TTS speaking rate.\n"
            f"/set_max_history [10-200] - Set Markov history size.\n"
            f"/set_glitch_intensity [1-100] - Adjust glitch frequency (1=always, 100=rare).\n"
            f"/show_settings - Display current settings.\n"
            f"/clear - Clear the chat log.\n"
            f"/about - Show information about Dr. Glitch.\n"
            f"/log - Show internal application log.\n"
            f"/retro - Activate Retro Theme.\n"
            f"/hal - Activate Self-Aware (HAL) Theme.\n"
            f"/sbaitso - Activate Dr. Sbaitso Emulation Mode (classic Eliza-like).\n" # Added /sbaitso help
            f"/normal - Reset to Hacker Theme and deactivate Chaos Mode.\n"
            f"/status - Get Dr. Glitch's system status.\n"
            f"/dial - Simulate modem dial-up.\n"
            f"say [text] - Make Dr. Glitch speak any text.\n"
            f"what math can you do? - Learn about my math capabilities.\n" # Added new command hint
            f"quit/exit/bye - Terminate the program.\n"
            f"---------------------------\n"
        )
        self._type_out(f"Dr. Glitch: {help_text}", "glitch", force_no_glitch=True,
                       on_done_callback=lambda: self._speak("DISPLAYING HELP COMMANDS.", on_done=self._after_bot_response_tasks))

    def _show_log(self):
        """Displays the internal application log."""
        log_content = "\n".join(self.log_messages)
        if not log_content:
            log_content = "LOG IS EMPTY."
        
        # Display log in a new simpledialog window or directly in chat if preferred
        # For simplicity and consistency with other outputs, we'll output to chat log
        self._type_out(f"--- DR. GLITCH INTERNAL LOG ---\n\n{log_content}\n-------------------------------\n", "glitch", force_no_glitch=True,
                       on_done_callback=lambda: self._speak("DISPLAYING INTERNAL LOG.", on_done=self._after_bot_response_tasks))


if __name__ == "__main__":
    root = tk.Tk()
    app = DrGlitchApp(root)
    app.run()
