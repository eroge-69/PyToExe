import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
import threading
import time
import requests
import io
import pyaudio
import wave
import speech_recognition as sr
import base64
from collections import deque

# -------- CONFIG --------
GEMINI_API_KEY = "AIzaSyD-iFJ-zQm3rOwlHBWS81tAsnJxjAYuS7A"
GEMINI_API_ENDPOINT = "https://api.gemini2.flash/v1/chat"  # Replace with real Gemini 2.0 chat+voice endpoint

# -----------------------

mp_pose = mp.solutions.pose

class SmartFootballAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Energy Football Assistant")

        self.label = tk.Label(root, text="Waiting for your move or voice command...", font=("Arial", 20), width=50, height=6)
        self.label.pack(padx=20, pady=20)

        # MediaPipe pose and webcam
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.prev_landmarks = None

        # Energy detection variables
        self.energy_history = deque(maxlen=30)  # ~3 seconds smoothing
        self.baseline_energy = None
        self.energy_std = None

        self.active = False
        self.cooldown_active = False
        self.cooldown_start = 0
        self.burst_start = None

        # Energy thresholds and timing
        self.burst_min_duration = 1.0  # seconds
        self.energy_multiplier = 2.0

        # Speech recognizer
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        # Thread flags
        self.listening = True
        self.processing_voice = False

        # Start threads
        threading.Thread(target=self.detect_energy_loop, daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def calc_energy(self, landmarks1, landmarks2):
        if landmarks1 is None or landmarks2 is None:
            return 0
        energy = 0
        for lm1, lm2 in zip(landmarks1.landmark, landmarks2.landmark):
            energy += np.linalg.norm(
                np.array([lm1.x, lm1.y, lm1.z]) - np.array([lm2.x, lm2.y, lm2.z])
            )
        return energy

    def detect_energy_loop(self):
        frame_duration = 0.1
        while True:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(frame_duration)
                continue

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)

            if results.pose_landmarks:
                if self.prev_landmarks:
                    energy = self.calc_energy(results.pose_landmarks, self.prev_landmarks)
                    self.energy_history.append(energy)

                    if len(self.energy_history) >= 20 and self.baseline_energy is None:
                        energies = list(self.energy_history)
                        self.baseline_energy = np.mean(energies)
                        self.energy_std = np.std(energies)
                        print(f"Baseline energy set: {self.baseline_energy:.5f}, std: {self.energy_std:.5f}")

                    if self.baseline_energy is not None:
                        threshold = self.baseline_energy + self.energy_multiplier * self.energy_std
                        now = time.time()

                        if energy > threshold:
                            if self.burst_start is None:
                                self.burst_start = now
                            if (now - self.burst_start) >= self.burst_min_duration and not self.active and not self.cooldown_active:
                                self.active = True
                                self.cooldown_active = False
                                self.burst_start = None
                                print(f"Energy burst detected at {now}")
                                self.root.after(0, self.on_active_detected)
                        else:
                            self.burst_start = None
                            if self.active:
                                self.active = False
                                self.cooldown_active = True
                                self.cooldown_start = now
                                print(f"Cooldown started at {now}")

                        # Adaptive cooldown calculation
                        if self.cooldown_active:
                            elapsed_cooldown = now - self.cooldown_start
                            cooldown_length = max(5, 15 - elapsed_cooldown)  # smart cooldown decreases as you rest longer
                            if elapsed_cooldown > cooldown_length:
                                self.cooldown_active = False
                                self.root.after(0, lambda: self.label.config(text="Waiting for your move or voice command..."))
                                print("Cooldown ended")

                self.prev_landmarks = results.pose_landmarks

            time.sleep(frame_duration)

    def listen_loop(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
        while self.listening:
            if not self.processing_voice:
                try:
                    with self.mic as source:
                        print("Listening for voice command...")
                        audio = self.recognizer.listen(source, timeout=5)
                        user_text = self.recognizer.recognize_google(audio)
                        print(f"You said: {user_text}")
                        self.processing_voice = True
                        self.process_voice_command(user_text)
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    print("Voice recognition error:", e)

    def process_voice_command(self, text):
        # Send user text to Gemini 2.0 Flash API for smart response
        response_text, response_audio = self.query_gemini(text)
        if response_text:
            self.root.after(0, lambda: self.label.config(text=response_text))
        if response_audio:
            self.play_audio(response_audio)
        self.processing_voice = False

    def query_gemini(self, text):
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": text,
            "response_format": "audio_wav",
            "voice": "default"
        }
        try:
            response = requests.post(GEMINI_API_ENDPOINT, json=data, headers=headers)
            if response.status_code == 200:
                json_resp = response.json()
                response_text = json_resp.get("text", "")
                audio_b64 = json_resp.get("audio", None)
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    return response_text, audio_bytes
                else:
                    return response_text, None
            else:
                print("Gemini API error:", response.status_code, response.text)
                return None, None
        except Exception as e:
            print("Gemini request failed:", e)
            return None, None

    def on_active_detected(self):
        # When energy burst detected, send a proactive smart request to Gemini for advice
        prompt = "I am active and ready. What should I do now for football practice, food, or rest?"
        print("Sending proactive prompt to Gemini...")
        response_text, response_audio = self.query_gemini(prompt)
        if response_text:
            self.label.config(text=response_text)
        if response_audio:
            self.play_audio(response_audio)

    def play_audio(self, audio_bytes):
        p = pyaudio.PyAudio()
        wf = wave.open(io.BytesIO(audio_bytes), 'rb')
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartFootballAssistant(root)
    root.mainloop()
