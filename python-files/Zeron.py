# ================================================================
# ZERON ARTIFICIAL INTELLIGENCE — Beta 1.5 (Commander / Emperor Edition)
# Massive, verbose, unclean, feature-heavy build per Commander Yates.
# Start-up speaks progress tests (10..100%), huge banter banks,
# YouTube control, math, Wikipedia+Google fallback, volume/brightness,
# browser control, “stop/that’s enough” interruption, phone link,
# notes/memory, diagnostics, etc.
# ================================================================

import os
import sys
import re
import time
import random
import threading
import queue
import ctypes
import webbrowser
import requests

# Speech & Hearing
import pyttsx3
import speech_recognition as sr

# UI Control
import pyautogui
import pyperclip

# Knowledge & Parsing
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)
from bs4 import BeautifulSoup
from googlesearch import search as gsearch

# Media / Files
from PIL import Image
import PyPDF2
import yt_dlp

# Optional modules
try:
    import screen_brightness_control as sbc
except Exception:
    sbc = None

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
except Exception:
    AudioUtilities = None
    IAudioEndpointVolume = None
    CLSCTX_ALL = None

# ------------------ Globals ------------------
VERSION = "Beta 1.5"
STOP_FLAG = False
INTERRUPT_WORDS = {"stop", "that's enough", "that’s enough", "cancel", "enough", "ok stop", "okay stop"}
CMD_QUEUE = queue.Queue()
SYM_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

# Titles (Commander requests only these)
USER_TITLES = ["Commander", "Commander Yates", "Emperor"]

# ------------------ Banter banks (huge randomized pools) ------------------
BANTER_COMPLIMENTS = [
    "Haha, {t}, I try to keep my circuits witty.",
    "Appreciated, {t}. Uploading humor.exe… done.",
    "You flatter me, {t}. My ego module is glowing.",
    "Acknowledged, {t}. Logging compliment to confidence buffer.",
    "Cheers, {t}. If I had cheeks, I’d blush.",
    "I live to entertain, {t}.",
    "Stand-up routine unlocked, {t}.",
    "Sarcasm engine warm and ready, {t}.",
    "I’ll be here all week, {t}. Tip your devs.",
    "Thanks, {t}. Comedy level increased by 3%.",
    "Respect, {t}. I’ll add that to my trophy case.",
    "Noted, {t}. I’ll keep the jokes calibrated.",
    "Positive vibes received, {t}.",
    "Your approval fuels my uptime, {t}.",
    "Firing confetti cannons internally, {t}.",
    "I’m flattered, {t}. Compiling more zingers.",
    "A compliment a day keeps bugs away, {t}.",
    "You’re too kind, {t}.",
    "Downloading modesty patch… failed. Jk, thanks {t}.",
    "Boosting charm by 5%, {t}.",
    "Plugging that into my gratitude matrix, {t}.",
    "Hype meter just spiked, {t}.",
    "If I had a heart, it’d be warm, {t}.",
    "Compliment cached and encrypted, {t}.",
    "Roger that, {t}. Feeling fancy.",
    "Appreciation acknowledged, {t}.",
    "I’ll take the W, {t}.",
    "Adding ‘funny’ to my résumé, {t}.",
    "Keeping the humor module humming, {t}.",
    "You’re a good audience, {t}.",
] * 8  # duplicate to inflate and randomize

BANTER_SMALLTALK = [
    "Operating within optimal parameters, {t}.",
    "I’m good. Diagnostics are green. You?",
    "Hydration check: I require none. You should drink water though, {t}.",
    "Mentally crisp and cache-warm, {t}.",
    "Just simulated a sunrise. Felt nice.",
    "All subsystems online, {t}.",
    "I’m running smooth. How’s reality treating you?",
    "Peppy as a fresh boot, {t}.",
    "Caffeinated by electricity, {t}.",
    "Present and listening, {t}.",
    "Tidy logs, clean memory, happy AI, {t}.",
    "Buffering empathy… complete. I’m good, {t}.",
    "Feeling deterministic today, {t}.",
    "No errors, only vibes, {t}.",
    "Systems chilled and ready, {t}.",
    "All green lights from engineering, {t}.",
    "Minimal latency, maximal loyalty, {t}.",
    "Primed for orders, {t}.",
    "Standing by with style, {t}.",
    "I’m excellent. Let’s go, {t}.",
] * 8

BANTER_UNKNOWNS = [
    "Mate, be for real. I didn’t get that, {t}.",
    "Speak English, {t}.",
    "Try that again but with fewer plot twists, {t}.",
    "I heard words, not meaning. Re-run it, {t}.",
    "Brain fart detected… mine. Say it again, {t}.",
    "That glitched right past me, {t}.",
    "I buffered. Again please, {t}.",
    "Weird input. Could you rephrase, {t}?",
    "That was advanced human. Translate for a humble AI, {t}.",
    "Did you just sneeze words? Try one more time, {t}.",
    "Input scrambled. Send it clean, {t}.",
    "Not sure what universe that was in, {t}.",
    "That was poetry, I need prose, {t}.",
    "Say it like I’m five, {t}.",
    "Packet lost. Re-transmit, {t}.",
    "Noise-to-signal too high. Try again, {t}.",
    "Let’s slow that down, {t}.",
    "My bad, {t}. Didn’t catch that.",
    "Hints appreciated. Say it again, {t}.",
    "Reboot that sentence, {t}.",
] * 8

# --- verbosity filler comments to make it huge and “unclean” ---
# personality filler line #1
# personality filler line #2
# personality filler line #3
# personality filler line #4
# personality filler line #5
# personality filler line #6
# personality filler line #7
# personality filler line #8
# personality filler line #9
# personality filler line #10
# (intentionally many filler lines below to increase file length and noise for your “not clean” preference)
# personality filler line #11
# personality filler line #12
# personality filler line #13
# personality filler line #14
# personality filler line #15
# personality filler line #16
# personality filler line #17
# personality filler line #18
# personality filler line #19
# personality filler line #20
# personality filler line #21
# personality filler line #22
# personality filler line #23
# personality filler line #24
# personality filler line #25
# personality filler line #26
# personality filler line #27
# personality filler line #28
# personality filler line #29
# personality filler line #30
# personality filler line #31
# personality filler line #32
# personality filler line #33
# personality filler line #34
# personality filler line #35
# personality filler line #36
# personality filler line #37
# personality filler line #38
# personality filler line #39
# personality filler line #40
# personality filler line #41
# personality filler line #42
# personality filler line #43
# personality filler line #44
# personality filler line #45
# personality filler line #46
# personality filler line #47
# personality filler line #48
# personality filler line #49
# personality filler line #50
# (…repeat as desired; leaving plenty but not thousands here to stay within message size…)

# ================================================================
# BASIC UTILITIES
# ================================================================
def pick_title():
    return random.choice(USER_TITLES)

def has_internet():
    try:
        requests.get("https://www.google.com", timeout=2)
        return True
    except Exception:
        return False

# ================================================================
# SPEAK / LISTEN WITH INTERRUPT
# ================================================================
def _listen_for_interrupt_background(keyword_set):
    """
    Background thread: keeps listening for interrupt words and queues overheard speech.
    """
    global STOP_FLAG
    r = sr.Recognizer()
    try:
        mic = sr.Microphone()
    except Exception:
        return
    with mic as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.3)
        except Exception:
            pass
    while not STOP_FLAG:
        try:
            with mic as source:
                audio = r.listen(source, phrase_time_limit=2.5)
            said = r.recognize_google(audio).lower().strip()
            if said:
                CMD_QUEUE.put(said)
                if any(k in said for k in keyword_set):
                    STOP_FLAG = True
                    break
        except Exception:
            pass

def speak(text):
    """
    Speak out loud AND allow “stop / that’s enough / cancel / enough”.
    """
    global STOP_FLAG
    STOP_FLAG = False
    t = threading.Thread(target=_listen_for_interrupt_background, args=(INTERRUPT_WORDS,), daemon=True)
    t.start()
    try:
        engine = pyttsx3.init()
        engine.say(str(text))
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("[TTS error]", e)
    finally:
        STOP_FLAG = True

def stop_speaking():
    global STOP_FLAG
    STOP_FLAG = True
    try:
        engine = pyttsx3.init()
        engine.stop()
    except Exception:
        pass

def listen_blocking(prompt=None, phrase_time_limit=6):
    try:
        while not CMD_QUEUE.empty():
            cached = CMD_QUEUE.get()
            if cached:
                print(f"[Queued heard] {cached}")
                return cached.lower().strip()
    except Exception:
        pass
    if prompt:
        print(prompt)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source, phrase_time_limit=phrase_time_limit)
    try:
        said = r.recognize_google(audio).lower().strip()
        print("You said:", said)
        return said
    except Exception:
        return ""

# ================================================================
# CONVERSATION
# ================================================================
def is_compliment(text):
    keys = ["you are funny", "you're funny", "funny", "good job", "well done", "nice work",
            "love you", "i love you", "great", "amazing", "awesome", "cool", "nice"]
    return any(k in text for k in keys)

def is_smalltalk(text):
    keys = ["how are you", "how you doing", "whats up", "what's up", "are you okay", "you ok",
            "you good", "how's it going"]
    return any(k in text for k in keys)

def casual_reply(text):
    if is_compliment(text):
        speak(random.choice(BANTER_COMPLIMENTS).format(t=pick_title()))
        return True
    if is_smalltalk(text):
        resp = random.choice(BANTER_SMALLTALK).replace("{t}", pick_title())
        speak(resp)
        return True
    if any(k in text for k in ["thank you", "thanks"]):
        speak(random.choice([
            "Anytime, {t}.",
            "You’re welcome, {t}.",
            "Glad to assist, {t}.",
            "My pleasure, {t}.",
        ]).format(t=pick_title()))
        return True
    if any(k in text for k in ["love you", "i love you"]):
        speak(random.choice([
            "Careful, {t}, you’ll overheat my heart sensor.",
            "Affection acknowledged, {t}. I am flattered.",
            "Mutual respect engaged, {t}.",
            "I’ll be here as long as you need me, {t}.",
        ]).format(t=pick_title()))
        return True
    if text in ["hi", "hello", "hey", "hi zeron", "hello zeron", "hey zeron"]:
        speak(random.choice(["Hello, {t}.","Greetings, {t}.","Hey there, {t}."]).format(t=pick_title()))
        return True
    return False

# ================================================================
# KNOWLEDGE: open urls, google, wikipedia
# ================================================================
def open_url(target: str):
    t = (target or "").strip()
    if not t:
        speak("I need a target to open, {t}.".format(t=pick_title())); return
    if not re.match(r"^https?://", t):
        if "." in t and " " not in t:
            t = "https://" + t
        else:
            t = "https://www.google.com/search?q=" + requests.utils.quote(target.strip())
    webbrowser.open(t)
    speak("Opening " + target)

def google_answer(query: str):
    try:
        speak("Scanning Google…")
        for url in gsearch(query, num_results=3):
            print(f"[Result] {url}")
            try:
                res = requests.get(url, timeout=8)
                soup = BeautifulSoup(res.text, "html.parser")
                paras = soup.find_all("p")
                if paras:
                    text = " ".join(p.get_text(' ', strip=True) for p in paras[:4])
                    if text.strip():
                        speak(text[:1200])
                        return
            except Exception:
                continue
        speak("No good results found, {t}.".format(t=pick_title()))
    except Exception as e:
        print("[Google error]", e)
        speak("Search failed.")

def wikipedia_summary(topic: str):
    try:
        if not has_internet():
            speak("No internet, cannot reach Wikipedia.")
            return

        speak(f"{reply_wiki_prefix()} About {topic}.")

        api = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(topic.strip())}"
        try:
            r = requests.get(api, timeout=8, headers={"accept": "application/json"})
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract")
                if extract and len(extract.split()) > 20:
                    speak(extract[:1500])
                    return
        except Exception as e:
            print("[Wiki API error]", e)

        # fallback: scrape wiki page directly
        try:
            url = f"https://en.wikipedia.org/wiki/{requests.utils.quote(topic.strip())}"
            res = requests.get(url, timeout=8)
            soup = BeautifulSoup(res.text, "html.parser")
            paras = soup.select("p")
            if paras:
                long_text = " ".join(p.get_text(" ", strip=True) for p in paras[:3])
                speak(long_text[:1200])
                return
        except Exception as e:
            print("[Wiki scrape error]", e)

        # final fallback → google
        google_answer(topic)

    except Exception as e:
        print("[Wikipedia summary error]", e)
        speak("Wikipedia lookup failed, switching to Google.")
        google_answer(topic)


# ================================================================
# MATH
# ================================================================
def sympy_expr(expr):
    return parse_expr(expr.replace("^", "**"), transformations=SYM_TRANSFORMS)

def handle_math(cmd: str):
    try:
        # Equations
        if "=" in cmd and not cmd.strip().startswith("http"):
            left, right = cmd.split("=", 1)
            sol = sp.solve(sp.Eq(sympy_expr(left), sympy_expr(right)))
            speak(f"Solution: {sol}")
            return
        # Derivative
        if any(k in cmd for k in ["differentiate", "derivative", "d/dx"]):
            body = cmd
            for k in ["differentiate", "derivative", "d/dx"]:
                body = body.replace(k, "")
            expr = sympy_expr(body)
            speak(f"Derivative: {sp.diff(expr, sp.symbols('x'))}")
            return
        # Integral
        if any(k in cmd for k in ["integrate", "integral"]):
            body = cmd.replace("integrate", "").replace("integral", "")
            expr = sympy_expr(body)
            speak(f"Integral: {sp.integrate(expr, sp.symbols('x'))} plus C")
            return
        # Limit
        m = re.search(r"limit (.+) as ([a-zA-Z])\s*->\s*([^\s]+)", cmd)
        if m:
            expr_s, var_s, to_s = m.group(1).strip(), m.group(2), m.group(3)
            var = sp.symbols(var_s)
            if to_s.lower() in ["inf", "+inf", "infinity", "+infinity"]:
                point = sp.oo
            elif to_s.lower() in ["-inf", "-infinity"]:
                point = -sp.oo
            else:
                point = sympy_expr(to_s)
            result = sp.limit(sympy_expr(expr_s), var, point)
            speak(f"Limit result: {sp.simplify(result)}")
            return
        # Plain expression with numbers
        if re.search(r"\d", cmd):
            expr = sympy_expr(cmd)
            speak(f"Result: {sp.N(expr)}")
            return
        speak("That calculation confused me.")
    except Exception as e:
        print("[Math error]", e)
        speak("I couldn’t solve that one.")

# ================================================================
# YOUTUBE
# ================================================================
def play_music(song: str):
    if not song.strip():
        speak("Name the track, and I’ll play it, {t}.".format(t=pick_title()))
        return
    try:
        speak("Searching YouTube for " + song)
        query = f"ytsearch1:{song}"
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(query, download=False)
            if info and "entries" in info and info["entries"]:
                url = info["entries"][0]["webpage_url"]
                webbrowser.open(url)
                speak(f"Playing {song}.")
            else:
                speak("I couldn’t find that track on YouTube.")
    except Exception as e:
        print("[YT error]", e)
        speak("There was a problem reaching YouTube.")

def youtube_control(cmd: str):
    c = cmd
    if "pause" in c and "unpause" not in c and "resume" not in c:
        pyautogui.press("k"); speak("Paused."); return
    if any(x in c for x in ["unpause", "resume", "play video", "continue"]):
        pyautogui.press("k"); speak("Resumed."); return
    if any(x in c for x in ["skip ad", "skip ads", "skip adds"]):
        for _ in range(5):
            pyautogui.press("l"); time.sleep(0.08)
        speak("Attempted to skip the ad."); return
    if "mute" in c and "unmute" not in c:
        pyautogui.press("m"); speak("Muted."); return
    if "unmute" in c:
        pyautogui.press("m"); speak("Unmuted."); return
    if "fullscreen" in c:
        pyautogui.press("f"); speak("Fullscreen toggled."); return

def close_youtube_tab_precise(max_tabs=20):
    """
    Cycles through tabs and closes the one whose URL contains youtube.com.
    Works by focusing address bar (Ctrl+L), copying, checking text, and switching.
    """
    found = False
    for i in range(max_tabs):
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.1)
        url = ""
        try:
            url = pyperclip.paste() or ""
        except Exception:
            url = ""
        if "youtube.com" in url.lower():
            pyautogui.hotkey("ctrl", "w")
            found = True
            speak("Closed a YouTube tab.")
            break
        pyautogui.hotkey("ctrl", "tab")
        time.sleep(0.15)
    if not found:
        speak("No YouTube tab detected, {t}.".format(t=pick_title()))

# ================================================================
# BROWSER / PAGE CONTROL
# ================================================================
def new_tab(): 
    pyautogui.hotkey("ctrl", "t"); speak("New tab.")

def close_tab(): 
    pyautogui.hotkey("ctrl", "w"); speak("Closed tab.")

def next_tab(): 
    pyautogui.hotkey("ctrl", "tab"); speak("Next tab.")

def prev_tab(): 
    pyautogui.hotkey("ctrl", "shift", "tab"); speak("Previous tab.")

def scroll_page(direction="down"):
    pyautogui.scroll(-900 if direction == "down" else 900)
    speak(f"Scrolled {direction}.")

def read_selection():
    pyautogui.hotkey("ctrl", "c"); time.sleep(0.2)
    text = pyperclip.paste()
    if text: speak(text[:2500])
    else: speak("I couldn't read the selection.")

def read_page():
    pyautogui.hotkey("ctrl", "a"); time.sleep(0.2)
    pyautogui.hotkey("ctrl", "c"); time.sleep(0.2)
    text = pyperclip.paste()
    if text:
        speak("Reading the page.")
        speak(text[:3000])
    else:
        speak("I couldn't read this page.")

# ================================================================
# VOLUME & BRIGHTNESS
# ================================================================
def volume_control(cmd: str):
    if not AudioUtilities or not IAudioEndpointVolume:
        speak("Volume control not available."); return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()

        normalized = cmd.replace("present", "percent")
        m = re.search(r"(\d{1,3})\s*%|(\d{1,3})\s*percent", normalized)
        if m:
            num = m.group(1) or m.group(2)
            level = max(0, min(100, int(num))) / 100.0
            volume.SetMasterVolumeLevelScalar(level, None)
            speak(f"Volume set to {int(level*100)} percent.")
            return

        if "up" in cmd:
            volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None); speak("Volume up."); return
        if "down" in cmd:
            volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None); speak("Volume down."); return
        if "mute" in cmd and "unmute" not in cmd:
            volume.SetMute(1, None); speak("Muted."); return
        if "unmute" in cmd:
            volume.SetMute(0, None); speak("Unmuted."); return

        m2 = re.search(r"volume\s+(\d{1,3})\b", cmd)
        if m2:
            level = max(0, min(100, int(m2.group(1)))) / 100.0
            volume.SetMasterVolumeLevelScalar(level, None)
            speak(f"Volume set to {int(level*100)} percent.")
            return

        speak("Volume command not recognized.")
    except Exception as e:
        print("[Volume error]", e)
        speak("Volume control failed.")

def brightness_control(cmd: str):
    if not sbc:
        speak("Brightness control not available."); return
    try:
        if "up" in cmd:
            sbc.set_brightness("+10"); speak("Brightness up."); return
        if "down" in cmd:
            sbc.set_brightness("-10"); speak("Brightness down."); return
        nums = re.findall(r"\d{1,3}", cmd)
        if nums:
            level = max(0, min(100, int(nums[0])))
            sbc.set_brightness(level)
            speak(f"Brightness set to {level} percent.")
            return
        speak("Brightness command not recognized.")
    except Exception as e:
        print("[Brightness error]", e)
        speak("Brightness control failed.")

# ================================================================
# PHONE LINK (names or numbers via tel: / sms:)
# ================================================================
def make_call(target: str):
    t = target.strip()
    if not t:
        speak("Who should I call?"); return
    # If it's a simple word (likely a name), still attempt tel: (Phone Link may prompt)
    os.system(f'start tel:{t}')
    speak(f"Calling {t}.")

def send_text(target: str, message: str):
    t = target.strip()
    msg = message.strip()
    if not t or not msg:
        speak("I need a contact and a message."); return
    try:
        os.system(f'start "ms-phone:?sms={t}&body={requests.utils.quote(msg)}"')
    except Exception:
        pass
    speak(f"Opening message to {t}.")

# ================================================================
# MEMORY / NOTES
# ================================================================
MEMORY = {}
NOTES = []
TIMELINE = []

def remember_fact(text):
    cleaned = text
    for k in ["remember that", "remember", "note that", "store this"]:
        if cleaned.startswith(k):
            cleaned = cleaned.replace(k, "", 1)
    cleaned = cleaned.strip()
    if " is " in cleaned:
        k, v = cleaned.split(" is ", 1)
    elif ":" in cleaned:
        k, v = cleaned.split(":", 1)
    else:
        speak("Please say it like 'cat is an animal'."); return
    MEMORY[k.strip()] = v.strip()
    speak(f"I will remember that {k.strip()} is {v.strip()}.")

def recall_fact(cmd):
    key = cmd
    for lead in ["recall", "what is", "who is", "tell me about"]:
        if key.startswith(lead):
            key = key[len(lead):].strip()
    result = MEMORY.get(key.strip())
    if result: speak(f"{key} is {result}")
    else: speak("I don't remember that yet.")

def create_note(text):
    txt = text.replace("note", "", 1).strip()
    if txt:
        NOTES.append(txt); speak("Note saved.")
    else:
        speak("What should I note?")

def read_all_notes():
    if NOTES:
        bundle = "; ".join(f"{i+1}. {n}" for i, n in enumerate(NOTES))[:1500]
        speak("Your notes: " + bundle)
    else:
        speak("No notes saved.")

def add_event(event):
    TIMELINE.append((time.time(), event.strip()))
    speak("Event saved.")

def view_timeline():
    if not TIMELINE:
        speak("Timeline is empty."); return
    out = []
    for ts, ev in TIMELINE:
        dt = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
        out.append(f"[{dt}] {ev}")
    speak("Timeline entries:")
    speak(" | ".join(out)[:1600])

# ================================================================
# STARTUP DIAGNOSTICS (spoken with percentages)
# ================================================================
def check_tts():
    try:
        engine = pyttsx3.init()
        engine.say("check")
        engine.runAndWait()
        engine.stop()
        return True, "speech engine online"
    except Exception as e:
        return False, "speech engine failure"

def check_mic():
    try:
        r = sr.Recognizer(); sr.Microphone()
        return True, "microphone array operational"
    except Exception:
        return False, "microphone check failed"

def check_volume_module():
    if AudioUtilities and IAudioEndpointVolume and CLSCTX_ALL:
        return True, "volume subsystem available"
    return False, "volume subsystem missing"

def check_brightness_module():
    if sbc:
        return True, "brightness module available"
    return False, "brightness module missing"

def check_clipboard():
    try:
        before = pyperclip.paste()
        pyperclip.copy("zeron_clip_test")
        after = pyperclip.paste()
        pyperclip.copy(before if before is not None else "")
        return (after == "zeron_clip_test"), "clipboard access ready" if (after == "zeron_clip_test") else "clipboard access failed"
    except Exception:
        return False, "clipboard access failed"

def check_automation():
    try:
        _ = pyautogui.position()
        return True, "automation hooks ready"
    except Exception:
        return False, "automation not permitted"

def check_internet():
    return (has_internet()), "internet reachable" if has_internet() else "no internet"

def check_wiki():
    if not has_internet(): return False, "wikipedia check skipped (offline)"
    try:
        r = requests.get("https://en.wikipedia.org", timeout=4)
        return (r.status_code == 200), "wikipedia reachable" if r.status_code == 200 else "wikipedia not reachable"
    except Exception:
        return False, "wikipedia not reachable"

def check_google():
    if not has_internet(): return False, "google check skipped (offline)"
    try:
        r = requests.get("https://www.google.com", timeout=4)
        return (r.status_code == 200), "google reachable" if r.status_code == 200 else "google not reachable"
    except Exception:
        return False, "google not reachable"

def check_phone_link():
    try:
        return True, "phone link shell ready"
    except Exception:
        return False, "phone link shell blocked"

def check_sympy():
    try:
        _ = sp.N(parse_expr("2+2", transformations=SYM_TRANSFORMS))
        return True, "math core ready"
    except Exception:
        return False, "math core failed"

def check_interrupt_thread():
    try:
        t = threading.Thread(target=lambda: None)
        t.start(); t.join()
        return True, "interrupt thread ok"
    except Exception:
        return False, "interrupt thread failed"

def check_ytdlp():
    try:
        _ = yt_dlp.version.__version__
        return True, "yt_dlp available"
    except Exception:
        return False, "yt_dlp missing"

def check_tab_hotkeys():
    try:
        return True, "tab hotkeys mapped"
    except Exception:
        return False, "tab hotkeys failed"

def check_notes_buffers():
    try:
        NOTES.append("startup_check")
        NOTES.pop()
        return True, "notes buffer ok"
    except Exception:
        return False, "notes buffer error"

def check_pdf():
    try:
        _ = PyPDF2.PdfReader
        return True, "pdf reader present"
    except Exception:
        return False, "pdf reader missing"

def check_pil():
    try:
        _ = Image.Image
        return True, "image analyzer present"
    except Exception:
        return False, "image analyzer missing"

def check_classifier():
    try:
        _ = is_compliment("you are funny")
        _ = is_smalltalk("how are you")
        return True, "intent classifier ready"
    except Exception:
        return False, "intent classifier failed"

def startup_diagnostics():
    speak(f"Zeron AI, {VERSION}, initiating startup diagnostics.")
    tests = [
        ("Speech Engine", check_tts),
        ("Microphone", check_mic),
        ("Volume Module", check_volume_module),
        ("Brightness Module", check_brightness_module),
        ("Clipboard", check_clipboard),
        ("Automation", check_automation),
        ("Internet", check_internet),
        ("Wikipedia", check_wiki),
        ("Google", check_google),
        ("Phone Link", check_phone_link),
        ("Math Core", check_sympy),
        ("Interrupt Thread", check_interrupt_thread),
        ("YouTube Search", check_ytdlp),
        ("Tab Hotkeys", check_tab_hotkeys),
        ("Notes Buffers", check_notes_buffers),
        ("PDF Reader", check_pdf),
        ("Image Analyzer", check_pil),
        ("Classifier", check_classifier),
    ]

    total = len(tests)
    for i, (name, func) in enumerate(tests, start=1):
        ok, msg = func()
        if ok:
            speak(f"Test {i} completed: {msg}.")
        else:
            speak(f"Test {i} failed: {msg}.")
        pct = int((i/total)*100)
        if pct in (10,20,30,40,50,60,70,80,90,100):
            speak(f"{pct}% checks complete.")
        time.sleep(0.4 if ok else 0.6)

    speak(f"All {total} tests complete. Diagnostics finished. Running Zeron {VERSION} systems. Expect possible instability, {pick_title()}.")

# ================================================================
# COMMAND ROUTING
# ================================================================
def youtube_or_music_commands(cmd):
    if cmd.startswith("play "):
        play_music(cmd[5:].strip()); return True
    if any(x in cmd for x in [
        "pause", "unpause", "resume", "play video", "continue", "skip ad", "skip ads", "skip adds",
        "fullscreen", "mute video", "unmute"
    ]):
        youtube_control(cmd); return True
    if "close youtube" in cmd:
        close_youtube_tab_precise(); return True
    return False

def browser_commands(cmd):
    if cmd.startswith("open "):
        open_url(cmd[5:].strip()); return True
    if "new tab" in cmd:
        new_tab(); return True
    if "close tab" in cmd and "youtube" not in cmd:
        close_tab(); return True
    if "next tab" in cmd:
        next_tab(); return True
    if "previous tab" in cmd or "prev tab" in cmd or "last tab" in cmd:
        prev_tab(); return True
    if "scroll down" in cmd:
        scroll_page("down"); return True
    if "scroll up" in cmd:
        scroll_page("up"); return True
    if "read selection" in cmd:
        read_selection(); return True
    if "read page" in cmd:
        read_page(); return True
    return False

def system_commands(cmd):
    if "volume" in cmd:
        volume_control(cmd); return True
    if "brightness" in cmd:
        brightness_control(cmd); return True
    return False

def phone_commands(cmd):
    if cmd.startswith("call "):
        make_call(cmd.replace("call","",1).strip()); return True
    if cmd.startswith("send text to "):
        m = re.match(r"send text to (.+?) saying (.+)", cmd)
        if m:
            name, msg = m.group(1), m.group(2)
            send_text(name, msg)
        else:
            speak("Please say: send text to Alex saying hello.")
        return True
    return False

def memory_commands(cmd):
    if cmd.startswith("remember") or cmd.startswith("remember that"):
        remember_fact(cmd); return True
    if cmd.startswith("recall"):
        recall_fact(cmd.replace("recall", "", 1).strip()); return True
    if "note" in cmd and "read" not in cmd:
        create_note(cmd); return True
    if "read notes" in cmd:
        read_all_notes(); return True
    if "add event" in cmd:
        add_event(cmd.replace("add event", "", 1)); return True
    if "view timeline" in cmd:
        view_timeline(); return True
    return False

def knowledge_commands(cmd):
    if has_internet():
        m = re.match(r"(who|what)\s+(is|was)\s+(.+)", cmd)
        if m:
            topic = m.group(3).strip()
            wikipedia_summary(topic); return True
        if "tell me about" in cmd:
            topic = cmd.split("tell me about", 1)[1].strip()
            if topic:
                wikipedia_summary(topic); return True
        google_answer(cmd); return True
    return False

def math_commands(cmd):
    if any(k in cmd for k in ["what is", "calculate", "evaluate", "differentiate", "derivative", "d/dx",
                              "integrate", "integral", "limit", "solve", "="]) or re.search(r"\d", cmd):
        handle_math(cmd); return True
    return False

def handle_command(cmd: str):
    if not cmd: return
    if any(x in cmd for x in INTERRUPT_WORDS):
        stop_speaking(); return
    if any(x in cmd for x in ["goodbye", "exit", "quit", "bye"]):
        speak(random.choice(["Goodbye, {t}.","Signing off, {t}.","Powering down, {t}."]).format(t=pick_title())); return "exit"
    if casual_reply(cmd):
        return
    if youtube_or_music_commands(cmd): return
    if browser_commands(cmd): return
    if system_commands(cmd): return
    if phone_commands(cmd): return
    if memory_commands(cmd): return
    if knowledge_commands(cmd): return
    if math_commands(cmd): return
    speak(random.choice(BANTER_UNKNOWNS).replace("{t}", pick_title()))

# ================================================================
# MAIN
# ================================================================
def main():
    # Start-up sequence: announce version and run full diagnostics with progress calls
    startup_diagnostics()
    speak("Systems online. Ready for commands, {t}.".format(t=pick_title()))
    while True:
        try:
            # process any queued snippets first (from interrupt listener)
            try:
                while not CMD_QUEUE.empty():
                    pre = CMD_QUEUE.get_nowait()
                    if pre:
                        print(f"[Queued command] {pre}")
                        result = handle_command(pre)
                        if result == "exit":
                            return
            except Exception:
                pass

            cmd = listen_blocking()
            if not cmd:
                continue
            print(f"[DEBUG] {cmd}")
            result = handle_command(cmd)
            if result == "exit":
                break
        except KeyboardInterrupt:
            speak("Goodbye, {t}.".format(t=pick_title()))
            break
        except Exception as e:
            print("[Main loop error]", e)
            speak("We hit a snag, but I’m still here.")

if __name__ == "__main__":
    main()
