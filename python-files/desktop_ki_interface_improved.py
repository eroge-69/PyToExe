#!/usr/bin/env python3
\"\"\"Desktop KI Interface - Improved prototype
- GUI: Tkinter with two tabs
- Speech: speech_recognition (optional; program runs without it)
- TTS: pyttsx3 (optional; program runs without it)
- REST client: requests (with simple retry/backoff)
Save as desktop_ki_interface_improved.py and convert to .exe with PyInstaller if needed.

Note: This is a prototype. Adjust REST endpoints, NPC IDs, and integration details
to match your Minecraft mod and network setup.
\"\"\"

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
import json

# Optional libs - handled with lazy imports to allow running even if some packages missing
try:
    import requests
except Exception:
    requests = None

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

# ---------- Configuration ----------
REST_ENDPOINT = \"http://localhost:5000/npc\"  # default mod REST endpoint
NPC_ID = \"npc_01\"

# ---------- Utility: Thread-safe TTS ----------
class TTS:
    def __init__(self):
        self.engine = None
        self.queue = queue.Queue()
        self.thread = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                # start worker thread
                self.thread = threading.Thread(target=self._worker, daemon=True)
                self.thread.start()
            except Exception as e:
                print(\"TTS init failed:\", e)
                self.engine = None

    def _worker(self):
        while True:
            text = self.queue.get()
            try:
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                print(\"TTS speak error:\", e)

    def speak(self, text):
        if self.engine:
            self.queue.put(text)
        else:
            # fallback printing
            print(\"TTS fallback:\", text)

tts = TTS()

# ---------- REST client with retry/backoff ----------
def send_to_mod(payload, max_retries=3, backoff=1.0):
    if requests is None:
        print(\"requests not available - cannot send to mod.\")
        return {\"status\": \"requests_missing\"}
    headers = {\"Content-Type\": \"application/json\"}
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(REST_ENDPOINT, json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                try:
                    return resp.json()
                except Exception:
                    return {\"status\": \"ok\"}
            else:
                print(f\"REST returned {resp.status_code}: {resp.text}\")
        except Exception as e:
            print(f\"REST attempt {attempt} failed:\", e)
        time.sleep(backoff * attempt)
    return {\"status\": \"failed\"}

# ---------- Speech recognition loop (runs in background thread) ----------
class SpeechWorker:
    def __init__(self, on_command_callback, device_index=None):
        self.on_command = on_command_callback
        self._stop = threading.Event()
        self.device_index = device_index
        self.thread = None
        self.recognizer = None
        if sr:
            try:
                self.recognizer = sr.Recognizer()
            except Exception as e:
                print(\"SR init error:\", e)
                self.recognizer = None

    def start(self):
        if not sr or not self.recognizer:
            print(\"Speech recognition not available on this machine.\")
            return False
        self._stop.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self._stop.set()

    def _run(self):
        mic = None
        try:
            if self.device_index is None:
                mic = sr.Microphone()
            else:
                mic = sr.Microphone(device_index=self.device_index)
        except Exception as e:
            print(\"Microphone error:\", e)
            return

        with mic as source:
            # initial calibration
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            except Exception:
                pass

        while not self._stop.is_set():
            try:
                with mic as source:
                    print(\"Listening... (speak clearly)\")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                try:
                    cmd = self.recognizer.recognize_google(audio, language='de-DE')
                    print(\"Heard:\", cmd)
                    self.on_command(cmd)
                except sr.UnknownValueError:
                    # couldn't understand
                    pass
                except sr.RequestError as e:
                    print(\"Speech API error:\", e)
                    time.sleep(1.0)
            except sr.WaitTimeoutError:
                # no speech detected within timeout
                continue
            except Exception as e:
                print(\"Speech loop error:\", e)
                time.sleep(1.0)

# ---------- Command processing ----------
def process_command_text(command_text, update_chat_fn=None, speak_result=True):
    # Basic normalization and simple intent parsing
    text = command_text.strip().lower()
    if update_chat_fn:
        update_chat_fn(f\"Du: {command_text}\")
    payload = None

    # Example command mapping (expandable)
    if any(kw in text for kw in [\"folge mir\", \"follow me\", \"komm mit\"]):
        payload = {\"npcId\": NPC_ID, \"response\": \"Ich folge dir jetzt!\", \"action\": \"follow\"}
        result_text = \"Ich folge dir jetzt!\"
    elif any(kw in text for kw in [\"rüstung anziehen\", \"anziehen rüstung\", \"equip armor\", \"anlege rüstung\"]):
        payload = {\"npcId\": NPC_ID, \"response\": \"Rüstung angelegt.\", \"action\": \"equip_armor\"}
        result_text = \"Rüstung angelegt.\"
    elif any(kw in text for kw in [\"schwert nehmen\", \"nimm schwert\", \"equip sword\"]):
        payload = {\"npcId\": NPC_ID, \"response\": \"Schwert ausgerüstet.\", \"action\": \"equip_sword\"}
        result_text = \"Schwert ausgerüstet.\"
    elif any(kw in text for kw in [\"axt nehmen\", \"nimm axt\", \"equip axe\"]):
        payload = {\"npcId\": NPC_ID, \"response\": \"Axt ausgerüstet.\", \"action\": \"equip_axe\"}
        result_text = \"Axt ausgerüstet.\"
    else:
        # Fallback: send to ChatGPT-5.0 (placeholder) or echo
        result_text = f\"Verstanden: {command_text}\"
        payload = {\"npcId\": NPC_ID, \"response\": result_text, \"action\": \"speak\"}

    # send to mod if available
    send_result = send_to_mod(payload)
    if update_chat_fn:
        update_chat_fn(f\"Mod: {json.dumps(send_result)}\")
        update_chat_fn(f\"NPC: {result_text}\")
    if speak_result:
        tts.speak(result_text)

# ---------- GUI ----------
class App:
    def __init__(self, root):
        self.root = root
        root.title(\"Minecraft KI-Interface - Verbesserte Version\")
        root.geometry('720x480')

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Tab Minecraft status
        self.tab_status = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_status, text='Minecraft-Spieler')
        self._build_status_tab(self.tab_status)

        # Tab KI Interface
        self.tab_ki = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ki, text='KI-Interface')
        self._build_ki_tab(self.tab_ki)

        # Friend network tab
        self.tab_friends = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_friends, text='Freunde')
        self._build_friends_tab(self.tab_friends)

        # Speech worker
        self.speech_worker = None

    def _build_status_tab(self, parent):
        lbl = ttk.Label(parent, text='Spielerstatus (Platzhalter)', font=('Arial', 14))
        lbl.pack(pady=12)
        self.status_text = tk.Text(parent, height=12)
        self.status_text.pack(fill='x', padx=12, pady=6)
        # Example controls
        frame = ttk.Frame(parent)
        frame.pack(pady=6)
        ttk.Button(frame, text='Refresh Status', command=self._refresh_status).pack(side='left', padx=6)
        ttk.Label(frame, text='REST Endpoint:').pack(side='left', padx=6)
        self.endpoint_entry = ttk.Entry(frame, width=30)
        self.endpoint_entry.insert(0, REST_ENDPOINT)
        self.endpoint_entry.pack(side='left', padx=6)
        ttk.Button(frame, text='Set', command=self._set_endpoint).pack(side='left', padx=6)

    def _build_ki_tab(self, parent):
        # Chat box
        self.chat_box = tk.Text(parent, height=14)
        self.chat_box.pack(padx=10, pady=8, fill='x')
        # input area
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill='x', padx=10, pady=6)
        self.user_input = ttk.Entry(input_frame)
        self.user_input.pack(side='left', expand=True, fill='x', padx=6)
        ttk.Button(input_frame, text='Senden', command=self._on_send_text).pack(side='left', padx=6)
        ttk.Button(input_frame, text='Sprache Start', command=self._on_start_speech).pack(side='left', padx=6)
        ttk.Button(input_frame, text='Sprache Stop', command=self._on_stop_speech).pack(side='left', padx=6)

        # device selection if available
        if sr:
            dev_frame = ttk.Frame(parent)
            dev_frame.pack(fill='x', padx=10, pady=6)
            ttk.Label(dev_frame, text='Mikrofon Device Index (optional):').pack(side='left')
            self.device_var = tk.StringVar()
            self.device_entry = ttk.Entry(dev_frame, width=6, textvariable=self.device_var)
            self.device_entry.pack(side='left', padx=6)
            ttk.Button(dev_frame, text='Liste Geräte', command=self._list_mic_devices).pack(side='left', padx=6)

    def _build_friends_tab(self, parent):
        ttk.Label(parent, text='Freundesnetzwerk (Prototyp)', font=('Arial', 14)).pack(pady=8)
        self.friends_listbox = tk.Listbox(parent, height=10)
        self.friends_listbox.pack(fill='both', padx=12, pady=6, expand=True)
        friend_frame = ttk.Frame(parent)
        friend_frame.pack(pady=6)
        ttk.Entry(friend_frame, width=30).pack(side='left', padx=6)
        ttk.Button(friend_frame, text='Hinzufügen (Platzhalter)', command=lambda: messagebox.showinfo('Info', 'Freund hinzufügen ist noch nicht implementiert')).pack(side='left', padx=6)
        ttk.Button(friend_frame, text='Verbinden (Platzhalter)', command=lambda: messagebox.showinfo('Info', 'Verbinden ist noch nicht implementiert')).pack(side='left', padx=6)

    # ---------- GUI actions ----------
    def _refresh_status(self):
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert(tk.END, 'Keine Live-Daten - Mod muss Events senden.\\n')
        self.status_text.insert(tk.END, f'REST Endpoint: {REST_ENDPOINT}\\n')

    def _set_endpoint(self):
        global REST_ENDPOINT
        val = self.endpoint_entry.get().strip()
        if val:
            REST_ENDPOINT = val
            messagebox.showinfo('Gespeichert', f'Endpoint gesetzt auf: {REST_ENDPOINT}')

    def _on_send_text(self):
        txt = self.user_input.get().strip()
        if not txt:
            return
        process_command_text(txt, update_chat_fn=self._append_chat)
        self.user_input.delete(0, tk.END)

    def _append_chat(self, text):
        self.chat_box.insert(tk.END, text + '\\n')
        self.chat_box.see(tk.END)

    def _on_start_speech(self):
        if not sr:
            messagebox.showwarning('Fehler', 'speech_recognition nicht installiert.')
            return
        device_index = None
        try:
            di = int(self.device_var.get())
            device_index = di
        except Exception:
            device_index = None
        if self.speech_worker and self.speech_worker.thread and self.speech_worker.thread.is_alive():
            messagebox.showinfo('Info', 'Spracherkennung läuft bereits.')
            return
        self.speech_worker = SpeechWorker(on_command_callback=lambda c: process_command_text(c, update_chat_fn=self._append_chat), device_index=device_index)
        started = self.speech_worker.start()
        if started:
            self._append_chat('Spracherkennung gestartet.')
        else:
            self._append_chat('Spracherkennung konnte nicht gestartet werden.')

    def _on_stop_speech(self):
        if self.speech_worker:
            self.speech_worker.stop()
            self._append_chat('Spracherkennung gestoppt.')

    def _list_mic_devices(self):
        if not sr:
            messagebox.showwarning('Fehler', 'speech_recognition nicht installiert.')
            return
        try:
            mics = sr.Microphone.list_microphone_names()
            msg = '\\n'.join(f\"{i}: {name}\" for i, name in enumerate(mics))
            messagebox.showinfo('Mikrofone', msg)
        except Exception as e:
            messagebox.showerror('Fehler', f'Konnte Geräte nicht listen: {e}')

# ---------- Main ----------
def main():
    root = tk.Tk()
    app = App(root)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()

if __name__ == '__main__':
    main()
