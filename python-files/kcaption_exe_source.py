"""
KCaption_ExeSource.pyw — Windows 시스템 오디오(스피커 출력) → 한글 텍스트 실시간 자막, 단일 소스

• 이 파일 하나만 업로드해서 온라인 EXE 빌더(파이썬→EXE)로 빌드해 사용하세요.
• 최초 실행 시 음성모델/번역모델을 자동 다운로드(인터넷 1회 필요) 후 캐시에 저장, 이후 오프라인 동작.
• GUI(Tkinter) 기본 제공: 시작/정지, 진행상태, 실시간 자막, SRT/TXT 저장.
• 핵심 의존성: sounddevice(Wasapi loopback), numpy, faster-whisper(ctranslate2 포함), argostranslate, sentencepiece
  ※ 온라인 빌더에서 pip 종속성 포함 옵션을 켜세요. PyInstaller 사용 시 --collect-all 스위치 권장.

작성일: 2025-08-24
"""
from __future__ import annotations
import os, sys, time, threading, queue
from collections import deque
from typing import Optional, Tuple, Deque

# --------- 안전한 임포트 및 오류 안내 ---------
missing: list[str] = []
try:
    import numpy as np
except Exception:
    missing.append("numpy")
try:
    import sounddevice as sd
except Exception:
    missing.append("sounddevice")
try:
    from faster_whisper import WhisperModel
except Exception:
    missing.append("faster-whisper")
try:
    import argostranslate.package as argos_pkg
    import argostranslate.translate as argos_tr
except Exception:
    missing.append("argostranslate (and sentencepiece)")

if missing:
    msg = (
        "필수 패키지 미설치: " + ", ".join(missing) + "\n"
        "온라인 EXE 빌더에서 pip 종속성을 포함하도록 설정하거나,\n"
        "로컬에서는 다음을 설치하세요:\n"
        "  pip install numpy sounddevice faster-whisper argostranslate sentencepiece\n"
    )
    raise SystemExit(msg)

# --------- 설정 ---------
APP_NAME = "KCaption"
SAMPLE_RATE = 16000
CHANNELS = 2
BLOCK_SEC = 0.25    # 오디오 콜백 주기
CHUNK_SEC = 5.0     # 인식 청크 길이
OVERLAP_SEC = 1.0   # 오버랩(중복 억제)
BEAM_SIZE = 5
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", APP_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)

# --------- 유틸 ---------
def srt_ts(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    ms = int((secs - int(secs)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# --------- 번역기 ---------
class Translator:
    def __init__(self, target_lang: str = "ko"):
        self.target = target_lang
        self.cache = {}
        try:
            argos_pkg.update_package_index()
        except Exception:
            pass

    def _installed(self):
        try:
            return argos_tr.get_installed_languages()
        except Exception:
            return []

    def _ensure(self, src: str, dst: str):
        key = f"{src}->{dst}"
        if key in self.cache:
            return self.cache[key]
        langs = self._installed()
        a = next((l for l in langs if l.code == src or src == "auto", None), None)
        b = next((l for l in langs if l.code == dst), None)
        if a and b:
            try:
                t = a.get_translation(b)
                self.cache[key] = t
                return t
            except Exception:
                pass
        # 다운로드 시도
        try:
            av = argos_pkg.get_available_packages()
            cand = [p for p in av if (p.from_code == src or src == "auto") and p.to_code == dst]
            if not cand and src != "en":
                # pivot 대비: src->en, en->dst 두 단계가 더 흔함
                cand = [p for p in av if p.from_code == "en" and p.to_code == dst]
            if cand:
                path = argos_pkg.download_package(cand[0])
                argos_pkg.install_from_path(path)
                return self._ensure(src, dst)
        except Exception:
            pass
        return None

    def translate(self, text: str, src: Optional[str]) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        src = src or "auto"
        # 1) 직행
        pair = self._ensure(src, self.target)
        if pair:
            return pair.translate(t)
        # 2) pivot src->en->ko
        if src != "en":
            to_en = self._ensure(src, "en")
            en_ko = self._ensure("en", self.target)
            if to_en and en_ko:
                return en_ko.translate(to_en.translate(t))
        # 3) en->ko만
        en_ko = self._ensure("en", self.target)
        if en_ko:
            return en_ko.translate(t)
        # 최종 실패 시 원문 반환
        return t

# --------- ASR ---------
class ASR:
    def __init__(self):
        dev, compute = self._pick_dev()
        # GPU면 large-v3, CPU면 medium 권장(정확/속도 균형)
        model_name = "large-v3" if dev == "cuda" else "medium"
        self.model = WhisperModel(model_name, device=dev, compute_type=compute, num_workers=4)
        self.detected_lang: Optional[str] = None

    def _pick_dev(self) -> Tuple[str, str]:
        device = "cpu"; compute = "int8"
        try:
            import ctranslate2
            if getattr(ctranslate2, "get_cuda_device_count", lambda: 0)() > 0:
                device = "cuda"; compute = "float16"
        except Exception:
            pass
        return device, compute

    def transcribe(self, mono: 'np.ndarray') -> Tuple[str, Optional[str]]:
        segs, info = self.model.transcribe(
            mono,
            task="transcribe",
            beam_size=BEAM_SIZE,
            temperature=0.0,
            no_speech_threshold=0.45,
            vad_filter=False,
            condition_on_previous_text=True,
        )
        text = "".join(s.text for s in segs).strip()
        lang = getattr(info, "language", None)
        if self.detected_lang is None and lang:
            self.detected_lang = lang
        return text, self.detected_lang or lang

    def translate_en(self, mono: 'np.ndarray') -> str:
        segs, _ = self.model.transcribe(mono, task="translate", beam_size=BEAM_SIZE, temperature=0.0)
        return "".join(s.text for s in segs).strip()

# --------- 파이프라인 ---------
class Pipeline:
    def __init__(self, on_text, on_status, on_level):
        self.on_text = on_text
        self.on_status = on_status
        self.on_level = on_level
        self.q: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=80)
        self.running = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.total_t0 = 0.0
        self.srt: list[tuple[int,float,float,str]] = []
        self.tail: Deque[str] = deque(maxlen=4)
        self.asr = ASR()
        self.trans = Translator("ko")
        self.stream = None

    def start(self):
        if self.running.is_set():
            return
        self.running.set()
        self.total_t0 = time.time()
        self._start_audio()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        self.on_status(f"시작 — 모델:{self.asr.model._model_name}")

    def stop(self):
        self.running.clear()
        try:
            if self.stream:
                self.stream.stop(); self.stream.close()
        except Exception:
            pass
        self.on_status("정지")

    def _start_audio(self):
        block = int(SAMPLE_RATE * BLOCK_SEC)
        wasapi = sd.WasapiSettings(loopback=True)
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            blocksize=block,
            extra_settings=wasapi,
            callback=self._on_audio,
        )
        self.stream.start()

    def _on_audio(self, indata, frames, time_info, status):
        mono = indata.mean(axis=1).astype('float32')
        # 레벨(시각화)
        try:
            import numpy as _np
            level = float((_np.sqrt((_np.mean(mono**2))) if mono.size else 0.0))
        except Exception:
            level = 0.0
        self.on_level(level)
        try:
            self.q.put_nowait(mono)
        except queue.Full:
            try:
                _ = self.q.get_nowait(); self.q.put_nowait(mono)
            except Exception:
                pass

    def _worker(self):
        import numpy as _np
        buf = _np.zeros(0, dtype='float32')
        chunk = int(SAMPLE_RATE * CHUNK_SEC)
        step = int(SAMPLE_RATE * (CHUNK_SEC - OVERLAP_SEC))
        next_cut = chunk
        idx = 1
        while self.running.is_set():
            try:
                mono = self.q.get(timeout=0.2)
                buf = _np.concatenate([buf, mono])
                if buf.size >= next_cut:
                    start_idx = max(0, buf.size - chunk)
                    clip = buf[start_idx:]
                    start_ts = (time.time() - self.total_t0) - (clip.size / SAMPLE_RATE)
                    t0 = time.time()

                    text, lang = self.asr.transcribe(clip)
                    if lang and lang != 'ko':
                        ko = self.trans.translate(text, lang)
                        if not ko or ko.strip() == text.strip():
                            en = self.asr.translate_en(clip)
                            ko = self.trans.translate(en, 'en')
                    else:
                        ko = text
                    ko = self._dedup(ko)
                    if ko:
                        dur = (time.time() - t0) * 1000
                        end_ts = start_ts + (clip.size / SAMPLE_RATE)
                        self.srt.append((idx, max(0.0, start_ts), max(start_ts, end_ts), ko))
                        idx += 1
                        self.on_text(ko)
                        self.on_status(f"언어:{lang or 'auto'} | 지연:{dur:.0f}ms | 라인:{len(self.srt)}")
                    next_cut = buf.size - step + chunk
            except queue.Empty:
                continue
            except Exception as e:
                self.on_status(f"오류:{e}")
                time.sleep(0.2)

    def _dedup(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        tail = " ".join(list(self.tail)[-2:])
        if t and (t in tail or tail.endswith(t)):
            return ""
        self.tail.append(t)
        return t

    def save_txt(self, path: Optional[str] = None) -> str:
        if path is None:
            path = os.path.join(SAVE_DIR, time.strftime("%Y%m%d_%H%M%S") + ".txt")
        with open(path, "w", encoding="utf-8") as f:
            for _, _, _, t in self.srt:
                f.write(t + "\n")
        return path

    def save_srt(self, path: Optional[str] = None) -> str:
        if path is None:
            path = os.path.join(SAVE_DIR, time.strftime("%Y%m%d_%H%M%S") + ".srt")
        with open(path, "w", encoding="utf-8") as f:
            for i, s, e, t in self.srt:
                f.write(f"{i}\n{srt_ts(s)} --> {srt_ts(e)}\n{t}\n\n")
        return path

# --------- Tkinter GUI ---------
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — 실시간 자막")
        self.geometry("900x520")
        self.minsize(760, 420)
        try:
            self.iconbitmap(default=None)
        except Exception:
            pass
        self._build()
        self.pipeline = Pipeline(self._append_text, self._set_status, self._set_level)

    def _build(self):
        s = ttk.Style()
        s.theme_use("clam")

        top = ttk.Frame(self); top.pack(fill="x", padx=10, pady=8)
        self.btn_start = ttk.Button(top, text="▶ 시작", command=self.on_start)
        self.btn_stop  = ttk.Button(top, text="⏸ 정지", command=self.on_stop)
        self.btn_srt   = ttk.Button(top, text="💾 SRT 저장", command=self.on_save_srt)
        self.btn_txt   = ttk.Button(top, text="📝 TXT 저장", command=self.on_save_txt)
        for w in (self.btn_start, self.btn_stop, self.btn_srt, self.btn_txt):
            w.pack(side="left", padx=6)

        self.level_var = tk.DoubleVar(value=0.0)
        self.pb = ttk.Progressbar(top, orient="horizontal", length=240, mode="determinate", maximum=1000, variable=self.level_var)
        self.pb.pack(side="right", padx=6)

        mid = ttk.Frame(self); mid.pack(fill="both", expand=True, padx=10, pady=6)
        self.text = tk.Text(mid, wrap="word", font=("Malgun Gothic", 16), bg="#0f172a", fg="#e5e7eb")
        self.text.pack(fill="both", expand=True)

        bottom = ttk.Frame(self); bottom.pack(fill="x", padx=10, pady=4)
        self.stat = ttk.Label(bottom, text="대기")
        self.stat.pack(side="left")

    # ---- Callbacks ----
    def on_start(self):
        try:
            self.pipeline.start()
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def on_stop(self):
        self.pipeline.stop()

    def on_save_srt(self):
        p = self.pipeline.save_srt()
        messagebox.showinfo("저장", f"SRT 저장: {p}")

    def on_save_txt(self):
        p = self.pipeline.save_txt()
        messagebox.showinfo("저장", f"TXT 저장: {p}")

    def _append_text(self, t: str):
        self.text.insert("end", ("\n" if self.text.index('end-1c') != '1.0' else "") + t)
        self.text.see("end")

    def _set_status(self, s: str):
        self.stat.config(text=s)

    def _set_level(self, v: float):
        # 0..1 -> 0..1000
        val = max(0, min(1000, int(v * 2000)))
        self.level_var.set(val)

    def destroy(self):
        try:
            self.pipeline.stop()
        except Exception:
            pass
        super().destroy()

if __name__ == "__main__":
    # 고DPI 선명도
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    App().mainloop()
