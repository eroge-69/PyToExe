"""
Nova Assistant (Windows) - All-in-One with Settings (API + UI + optional wake word)
- UI has a Settings panel to save/update your OpenAI API key and select TTS voice.
- Settings are stored at: %APPDATA%\NovaAssistant\config.json

Run examples:
  python nova_all_in_one_with_settings.py --mode both    # API + UI (default)
  python nova_all_in_one_with_settings.py --mode server  # API only
  python nova_all_in_one_with_settings.py --mode ui      # UI only

Build .exe:
  pyinstaller --onefile --noconsole nova_all_in_one_with_settings.py
"""

import os, sys, io, wave, threading, time, base64, json, argparse
from typing import Optional

# ---------- Config paths ----------
APP_NAME = "NovaAssistant"
APPDATA = os.getenv("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
CONFIG_DIR = os.path.join(APPDATA, APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "OPENAI_API_KEY": "",
    "LLM_MODEL": "gpt-4o-mini",
    "STT_MODEL": "whisper-1",
    "TTS_MODEL": "tts-1",
    "TTS_VOICE": "alloy",
    "SYSTEM_PROMPT": "You are a concise, friendly home assistant named Nova. Reply briefly unless asked for detail.",
    "ASSIST_API_URL": "http://127.0.0.1:8000"
}

def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(data or {})
        return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(cfg: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

CFG = load_config()

# =================== OpenAI + FastAPI Server ===================
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

def get_openai_client():
    key = CFG.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OpenAI API key not set. Open Settings in the app and save your key.")
    return OpenAI(api_key=key)

app = FastAPI(title="Nova Laptop Assistant API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssistIn(BaseModel):
    text: str
    tts: bool = True

class AssistOut(BaseModel):
    reply_text: str
    audio_b64: Optional[str] = None

client = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/assist", response_model=AssistOut)
def assist(body: AssistIn):
    global client, CFG
    if client is None:
        client = get_openai_client()

    LLM_MODEL = CFG.get("LLM_MODEL", DEFAULT_CONFIG["LLM_MODEL"])
    SYSTEM_PROMPT = CFG.get("SYSTEM_PROMPT", DEFAULT_CONFIG["SYSTEM_PROMPT"])

    resp = client.responses.create(
        model=LLM_MODEL,
        input=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": body.text}
        ],
        temperature=0.6,
        max_output_tokens=600
    )

    reply_text = ""
    if hasattr(resp, "output") and resp.output:
        for part in resp.output:
            if getattr(part, "type", "") == "message":
                for c in getattr(part.message, "content", []):
                    if getattr(c, "type", "") == "output_text":
                        reply_text += c.text
    if not reply_text:
        reply_text = getattr(resp, "output_text", "") or ""

    out = AssistOut(reply_text=reply_text, audio_b64=None)

    if body.tts:
        TTS_MODEL = CFG.get("TTS_MODEL", DEFAULT_CONFIG["TTS_MODEL"])
        TTS_VOICE = CFG.get("TTS_VOICE", DEFAULT_CONFIG["TTS_VOICE"])
        speech = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=reply_text,
            format="wav",
        )
        audio_bytes = speech.read()
        out.audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    return out

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    global client, CFG
    if client is None:
        client = get_openai_client()

    STT_MODEL = CFG.get("STT_MODEL", DEFAULT_CONFIG["STT_MODEL"])
    data = await file.read()
    r = client.audio.transcriptions.create(
        model=STT_MODEL,
        file=(file.filename or "audio.wav", data, file.content_type or "audio/wav"),
    )
    return {"text": (r.text or "").strip()}

# =================== Desktop UI (PySide6) ===================
import numpy as np
import sounddevice as sd
import soundfile as sf
import requests
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QCheckBox, QSpinBox, QLineEdit, QComboBox, QGroupBox
)

OWW_AVAILABLE = True
try:
    from openwakeword.model import Model as OWWModel
except Exception:
    OWW_AVAILABLE = False

SAMPLE_RATE = 16000
CHANNELS = 1

def list_devices_str():
    lines = []
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        flags = []
        if dev["max_input_channels"] > 0: flags.append("IN")
        if dev["max_output_channels"] > 0: flags.append("OUT")
        rate = int(dev.get("default_samplerate", 0) or 0)
        lines.append(f"{idx:2d}: {dev['name']}  [{' '.join(flags) or '-'}]  default_rate={rate}")
    return "\n".join(lines)

def record_fixed(seconds: int, mic_index: int | None) -> bytes | None:
    sd.default.samplerate = SAMPLE_RATE
    if mic_index is not None:
        sd.default.device = (mic_index, None)
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32")
    sd.wait()
    if float(np.max(np.abs(audio))) < 0.02:
        return None
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()

def play_wav_bytes(wav_bytes: bytes, out_index: int | None):
    if out_index is not None:
        sd.default.device = (None, out_index)
    data, rate = sf.read(io.BytesIO(wav_bytes), dtype="float32", always_2d=True)
    if data.shape[1] > 1:
        data = np.mean(data, axis=1, keepdims=True)
    sd.play(data, rate)
    sd.wait()

class AssistWorker(QThread):
    result = Signal(str, bytes)
    error = Signal(str)

    def __init__(self, api_url: str, text: str, tts: bool):
        super().__init__()
        self.api_url = api_url
        self.text = text
        self.tts = tts

    def run(self):
        try:
            r = requests.post(f"{self.api_url}/assist", json={"text": self.text, "tts": self.tts}, timeout=120)
            r.raise_for_status()
            data = r.json()
            reply = data.get("reply_text", "")
            audio_b64 = data.get("audio_b64")
            audio = base64.b64decode(audio_b64) if (audio_b64 and self.tts) else b""
            self.result.emit(reply, audio)
        except Exception as e:
            self.error.emit(str(e))

class WakeWordThread(QThread):
    wake = Signal()
    def __init__(self, mic_index: int | None, keyword: str = "ok_nova"):
        super().__init__()
        self.mic_index = mic_index
        self.keyword = keyword
        self._running = True
        self.model = None
    def stop(self):
        self._running = False
    def run(self):
        if not OWW_AVAILABLE: return
        sd.default.samplerate = SAMPLE_RATE
        if self.mic_index is not None:
            sd.default.device = (self.mic_index, None)
        self.model = OWWModel(multiplier=1.0)
        frame_len = 512
        with sd.InputStream(channels=1, samplerate=SAMPLE_RATE, blocksize=frame_len, dtype="float32") as stream:
            while self._running:
                audio, _ = stream.read(frame_len)
                scores = self.model.predict(audio.flatten())
                for k, v in scores.items():
                    if self.keyword in k and v > 0.5:
                        self.wake.emit()
                        time.sleep(1.0)
                        break

class SettingsPanel(QGroupBox):
    saved = Signal(dict)
    def __init__(self, cfg: dict):
        super().__init__("Settings")
        self.cfg = cfg.copy()
        layout = QVBoxLayout(self)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("OpenAI API key:"))
        self.keyEdit = QLineEdit()
        self.keyEdit.setEchoMode(QLineEdit.Password)
        self.keyEdit.setText(self.cfg.get("OPENAI_API_KEY", ""))
        row1.addWidget(self.keyEdit)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Voice:"))
        self.voiceBox = QComboBox()
        self.voiceBox.addItems(["alloy", "aria", "verse", "coral", "amber", "sage"])
        current_voice = self.cfg.get("TTS_VOICE", "alloy")
        idx = max(0, self.voiceBox.findText(current_voice))
        self.voiceBox.setCurrentIndex(idx)
        row2.addWidget(self.voiceBox)
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Model:"))
        self.modelEdit = QLineEdit(self.cfg.get("LLM_MODEL", "gpt-4o-mini"))
        row3.addWidget(self.modelEdit)
        layout.addLayout(row3)

        btnRow = QHBoxLayout()
        self.saveBtn = QPushButton("Save Settings")
        btnRow.addStretch(1)
        btnRow.addWidget(self.saveBtn)
        layout.addLayout(btnRow)

        self.saveBtn.clicked.connect(self.on_save)

    @Slot()
    def on_save(self):
        new_cfg = load_config()
        new_cfg["OPENAI_API_KEY"] = self.keyEdit.text().strip()
        new_cfg["TTS_VOICE"] = self.voiceBox.currentText().strip()
        new_cfg["LLM_MODEL"] = self.modelEdit.text().strip() or "gpt-4o-mini"
        save_config(new_cfg)
        self.saved.emit(new_cfg)

class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nova Assistant (Windows)")
        self.resize(780, 620)
        self.cfg = load_config()

        self.mic_index = None
        self.out_index = None

        layout = QVBoxLayout(self)

        self.status = QLabel(f"Ready. API: {self.cfg.get('ASSIST_API_URL')}")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.settings = SettingsPanel(self.cfg)
        self.settings.saved.connect(self.on_settings_saved)
        layout.addWidget(self.settings)

        self.devicesBtn = QPushButton("List Audio Devices")
        self.devicesText = QTextEdit(); self.devicesText.setReadOnly(True)
        layout.addWidget(self.devicesBtn); layout.addWidget(self.devicesText)

        row = QHBoxLayout()
        row.addWidget(QLabel("Mic index:"))
        self.micBox = QSpinBox(); self.micBox.setRange(-1, 128); self.micBox.setValue(-1)
        row.addWidget(self.micBox)
        row.addWidget(QLabel("Out index:"))
        self.outBox = QSpinBox(); self.outBox.setRange(-1, 128); self.outBox.setValue(-1)
        row.addWidget(self.outBox)
        row.addWidget(QLabel("Record secs:"))
        self.secsBox = QSpinBox(); self.secsBox.setRange(2, 15); self.secsBox.setValue(6)
        row.addWidget(self.secsBox)
        layout.addLayout(row)

        self.inputText = QLineEdit(); self.inputText.setPlaceholderText("Type text or use 🎤 Talk...")
        layout.addWidget(self.inputText)

        buttons = QHBoxLayout()
        self.talkBtn = QPushButton("🎤 Talk")
        self.sendBtn = QPushButton("Send Text")
        self.speakChk = QCheckBox("Speak replies"); self.speakChk.setChecked(True)
        buttons.addWidget(self.talkBtn); buttons.addWidget(self.sendBtn); buttons.addWidget(self.speakChk)
        layout.addLayout(buttons)

        self.wakeChk = QCheckBox("Enable wake word (say: 'ok nova')"); self.wakeChk.setChecked(False)
        self.wakeLbl = QLabel("(openWakeWord installed: %s)" % ("yes" if OWW_AVAILABLE else "no"))
        layout.addWidget(self.wakeChk); layout.addWidget(self.wakeLbl)

        self.log = QTextEdit(); self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.devicesBtn.clicked.connect(self.on_list_devices)
        self.talkBtn.clicked.connect(self.on_talk)
        self.sendBtn.clicked.connect(self.on_send_text)
        self.wakeChk.stateChanged.connect(self.on_toggle_wake)

        self.wakeThread = None

    @Slot(dict)
    def on_settings_saved(self, new_cfg: dict):
        self.cfg = new_cfg
        self.status.setText(f"Settings saved. API: {self.cfg.get('ASSIST_API_URL')}")

    @Slot()
    def on_list_devices(self):
        self.devicesText.setPlainText(list_devices_str())

    @Slot()
    def on_talk(self):
        self.mic_index = self.micBox.value() if self.micBox.value() >= 0 else None
        self.out_index = self.outBox.value() if self.outBox.value() >= 0 else None
        secs = int(self.secsBox.value())
        self.status.setText("Recording...")
        wav_bytes = record_fixed(secs, self.mic_index)
        if not wav_bytes:
            self.status.setText("Heard nothing."); return
        self.status.setText("Transcribing...")
        try:
            files = {"file": ("speech.wav", wav_bytes, "audio/wav")}
            r = requests.post(f"{self.cfg.get('ASSIST_API_URL')}/stt", files=files, timeout=60)
            r.raise_for_status()
            user_text = r.json().get("text", "")
        except Exception as e:
            self.log.append(f"[error] STT failed: {e}"); self.status.setText("STT failed."); return
        if not user_text:
            self.status.setText("Empty transcription."); return
        self.log.append(f"You: {user_text}")
        self.status.setText("Thinking...")
        worker = AssistWorker(self.cfg.get("ASSIST_API_URL"), user_text, self.speakChk.isChecked())
        worker.result.connect(self.on_assist_done)
        worker.error.connect(self.on_assist_err)
        worker.start()

    @Slot()
    def on_send_text(self):
        text = self.inputText.text().strip()
        if not text: return
        self.log.append(f"You: {text}")
        self.status.setText("Thinking...")
        worker = AssistWorker(self.cfg.get("ASSIST_API_URL"), text, self.speakChk.isChecked())
        worker.result.connect(self.on_assist_done)
        worker.error.connect(self.on_assist_err)
        worker.start()

    @Slot(int)
    def on_toggle_wake(self, state):
        if state == Qt.Checked:
            if not OWW_AVAILABLE:
                self.log.append("[warn] openWakeWord not installed. Disable or install."); self.wakeChk.setChecked(False); return
            self.mic_index = self.micBox.value() if self.micBox.value() >= 0 else None
            self.wakeThread = WakeWordThread(self.mic_index, "ok_nova")
            self.wakeThread.wake.connect(self.on_wake_detected)
            self.wakeThread.start()
            self.log.append("Wake word listening... say 'ok nova'")
        else:
            if self.wakeThread:
                self.wakeThread.stop(); self.wakeThread.wait(1000); self.wakeThread = None
                self.log.append("Wake word disabled.")

    @Slot()
    def on_wake_detected(self):
        self.log.append("[wake] Detected 'ok nova'. Recording...")
        self.on_talk()

    @Slot(str, bytes)
    def on_assist_done(self, reply_text: str, audio_bytes: bytes):
        self.log.append(f"Nova: {reply_text}\n")
        self.status.setText("Ready")
        try:
            if audio_bytes and self.speakChk.isChecked():
                play_wav_bytes(audio_bytes, self.out_index if hasattr(self, 'out_index') else None)
        except Exception as e:
            self.log.append(f"[error] Playback failed: {e}")

    @Slot(str)
    def on_assist_err(self, msg: str):
        self.log.append(f"[error] {msg}")
        self.status.setText("Error")

def start_server_background(host="127.0.0.1", port=8000):
    import uvicorn
    def _run():
        global client, CFG
        client = get_openai_client()
        uvicorn.run(app, host=host, port=port, log_level="info")
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t

def run_ui():
    app_qt = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    sys.exit(app_qt.exec())

def main():
    parser = argparse.ArgumentParser(description="Nova Assistant - All-in-One with Settings")
    parser.add_argument("--mode", choices=["both", "server", "ui"], default="both")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.mode in ("both", "server"):
        start_server_background(host=args.host, port=args.port)

    if args.mode in ("both", "ui"):
        run_ui()
    elif args.mode == "server":
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()