#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json
import os
import sys
import time
import datetime
import math
import struct
import base64

# Optional dependencies
USE_TTKBOOTSTRAP = False
try:
    import ttkbootstrap as tb
    from ttkbootstrap import Style
    USE_TTKBOOTSTRAP = True
except Exception:
    USE_TTKBOOTSTRAP = False

USE_FERNET = False
try:
    from cryptography.fernet import Fernet
    USE_FERNET = True
except Exception:
    USE_FERNET = False

IS_WINDOWS = sys.platform.startswith('win')
if IS_WINDOWS:
    import winsound

# Settings
LOG_FILE = "test_logs.json"
KEY_XOR = 123  # fallback XOR key
APP_VERSION = "v2.1.1"
APP_AUTHOR = "Хутченко Данііл"

# --- Sound generation (small WAV buffers) ---
def make_wav_bytes(freq=440.0, duration=0.18, volume=0.3, samplerate=44100):
    n_samples = int(duration * samplerate)
    max_amp = int(32767 * volume)
    data = bytearray()
    for i in range(n_samples):
        t = i / samplerate
        sample = int(max_amp * math.sin(2 * math.pi * freq * t))
        data += struct.pack('<h', sample)
    num_channels = 1
    bytes_per_sample = 2
    byte_rate = samplerate * num_channels * bytes_per_sample
    block_align = num_channels * bytes_per_sample
    wav = bytearray()
    wav += b'RIFF'
    wav += struct.pack('<I', 36 + len(data))
    wav += b'WAVEfmt '
    wav += struct.pack('<I', 16)
    wav += struct.pack('<H', 1)
    wav += struct.pack('<H', num_channels)
    wav += struct.pack('<I', samplerate)
    wav += struct.pack('<I', byte_rate)
    wav += struct.pack('<H', block_align)
    wav += struct.pack('<H', bytes_per_sample * 8)
    wav += b'data'
    wav += struct.pack('<I', len(data))
    wav += data
    return bytes(wav)

SOUND_CORRECT = make_wav_bytes(freq=920.0, duration=0.12, volume=0.16)
SOUND_WRONG = make_wav_bytes(freq=440.0, duration=0.18, volume=0.14)
SOUND_TIMEOUT = make_wav_bytes(freq=330.0, duration=0.28, volume=0.12)

def play_sound_buf(buf):
    if not IS_WINDOWS:
        return
    try:
        winsound.PlaySound(buf, winsound.SND_MEMORY | winsound.SND_ASYNC)
    except Exception:
        pass

# --- Encryption helpers ---
def xor_decrypt_text(text: str, key=KEY_XOR) -> str:
    return ''.join(chr(ord(c) ^ key) for c in text)

def xor_encrypt_text(text: str, key=KEY_XOR) -> str:
    return ''.join(chr(ord(c) ^ key) for c in text)

def load_plain_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# New: support .test files that are self-contained (no separate .key)
# Expected wrapper JSON inside .test (text):
# { "type":"fernet", "key":"<base64>", "payload":"<base64>" }
# or { "type":"xor", "key":123, "payload":"<xor-string>" }
# or { "type":"plain", "payload":"<json-string>" }

def load_selfcontained_test(path):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            wrapper = json.load(f)
        except Exception as e:
            raise ValueError('Not a JSON wrapper (.test self-contained)') from e
    if not isinstance(wrapper, dict):
        raise ValueError('Invalid wrapper format')
    t = wrapper.get('type')
    if t == 'fernet':
        if 'key' not in wrapper or 'payload' not in wrapper:
            raise ValueError('Missing key/payload for fernet')
        if not USE_FERNET:
            raise RuntimeError('cryptography.Fernet required to decrypt this .test (embedded key)')
        key_b64 = wrapper['key']
        payload_b64 = wrapper['payload']
        try:
            key = base64.b64decode(key_b64)
            payload = base64.b64decode(payload_b64)
        except Exception as e:
            raise ValueError('Invalid base64 in wrapper') from e
        try:
            dec = Fernet(key).decrypt(payload).decode('utf-8')
            return json.loads(dec)
        except Exception as e:
            raise ValueError('Fernet decryption failed') from e
    elif t == 'xor':
        if 'payload' not in wrapper:
            raise ValueError('Missing payload for xor')
        payload = wrapper['payload']
        key = wrapper.get('key', KEY_XOR)
        try:
            dec_text = xor_decrypt_text(payload, key)
            return json.loads(dec_text)
        except Exception as e:
            raise ValueError('XOR decryption failed') from e
    elif t == 'plain':
        if 'payload' not in wrapper:
            raise ValueError('Missing payload for plain')
        payload = wrapper['payload']
        try:
            return json.loads(payload)
        except Exception as e:
            raise ValueError('Parsing payload failed') from e
    else:
        raise ValueError('Unknown wrapper type')

# Backwards-compatible loaders

def load_xor_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    dec = xor_decrypt_text(raw)
    return json.loads(dec)

def load_fernet_external_key(path):
    key_path = path + '.key'
    if not os.path.exists(key_path):
        raise FileNotFoundError("Key (.key) not found")
    with open(key_path, 'rb') as kf:
        key = kf.read()
    with open(path, 'rb') as f:
        raw = f.read()
    dec = Fernet(key).decrypt(raw).decode('utf-8')
    return json.loads(dec)

# --- Logging ---
def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def append_log(entry: dict):
    ensure_log_file()
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except Exception:
        logs = []
    logs.append(entry)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def read_logs():
    ensure_log_file()
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- UI utilities: rounded rectangle on Canvas as button ---
def rounded_rect(canvas, x1, y1, x2, y2, r=12, **kwargs):
    return canvas.create_polygon(
        [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2 - r,
            x1, y1 + r
        ],
        smooth=True, **kwargs
    )

class AnswerButton:
    def __init__(self, parent, width=900, height=72, radius=14,
                 base_color='#ffd9cc', hover_color='#ffe6e0', text_color='#063047', callback=None):
        self.parent = parent
        self.width = width
        self.height = height
        self.radius = radius
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.callback = callback
        self.visible = False
        self.frame = tk.Frame(parent, bg=parent['bg'])
        self.canvas = tk.Canvas(self.frame, width=width, height=height, highlightthickness=0, bg=parent['bg'])
        self.canvas.pack()
        self.rect = rounded_rect(self.canvas, 6, 6, width - 6, height - 6, r=radius, fill=self.base_color, outline='')
        self.text_id = self.canvas.create_text(width // 2, height // 2, text='', font=('Segoe UI', 14), fill=self.text_color, width=width - 40)
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Enter>', self._on_enter)
        self.canvas.bind('<Leave>', self._on_leave)
        self.opt_index = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        self.visible = True

    def pack_forget(self):
        self.frame.pack_forget()
        self.visible = False
        self.opt_index = None

    def set_text(self, text):
        self.canvas.itemconfigure(self.text_id, text=text)

    def set_colors(self, base=None, hover=None, text_color=None):
        if base:
            self.base_color = base
            self.canvas.itemconfigure(self.rect, fill=self.base_color)
        if hover:
            self.hover_color = hover
        if text_color:
            self.text_color = text_color
            self.canvas.itemconfigure(self.text_id, fill=self.text_color)

    def set_callback(self, cb):
        self.callback = cb

    def _on_click(self, _e):
        if self.callback:
            try:
                self.callback(self.opt_index, self)
            except Exception:
                self.callback(self.opt_index)

    def _on_enter(self, _e):
        try:
            self.canvas.itemconfigure(self.rect, fill=self.hover_color)
        except Exception:
            pass

    def _on_leave(self, _e):
        try:
            self.canvas.itemconfigure(self.rect, fill=self.base_color)
        except Exception:
            pass

    def set_feedback(self, correct=False, wrong=False):
        if correct:
            self.canvas.itemconfigure(self.rect, fill='#bff3c6')
        elif wrong:
            self.canvas.itemconfigure(self.rect, fill='#ffc4c4')
        else:
            self.canvas.itemconfigure(self.rect, fill=self.base_color)

# --- Main application ---
class TestApp:
    def __init__(self, root):
        self.root = root
        self.tb_style = None
        if USE_TTKBOOTSTRAP:
            try:
                self.tb_style = Style()
                self.root.destroy()
                self.root = tb.Window(themename='flatly')
            except Exception:
                self.root = root
        self.root.title("Quiz Tester")
        self.root.geometry("1020x780")
        self.root.resizable(False, False)
        self.bg = '#f7fcff'
        self.root.configure(bg=self.bg)

        # state
        self.user_name = ""
        self.current_test_path = None
        self.test_data = []
        self.q_index = 0
        self.correct_count = 0
        self.remaining = 0
        self.timer_job = None

        # colors brighter pool
        self.colors = ['#ffcccc', '#cce5ff', '#fff2b3', '#ccffd9', '#f0d6ff', '#ffd9b3']

        # frames
        self.frame_start = tk.Frame(self.root, bg=self.bg)
        self.frame_about = tk.Frame(self.root, bg=self.bg)
        self.frame_quiz = tk.Frame(self.root, bg=self.bg)
        self.frame_logs = tk.Frame(self.root, bg=self.bg)
        for f in (self.frame_start, self.frame_about, self.frame_quiz, self.frame_logs):
            f.place(relwidth=1, relheight=1)

        self.build_start()
        self.build_about()
        self.build_quiz()
        self.build_logs()

        self.show_frame('start')

    # ---------- Start ----------
    def build_start(self):
        f = self.frame_start
        for w in f.winfo_children(): w.destroy()
        tk.Label(f, text="Тестування студентів", font=('Segoe UI', 26, 'bold'), bg=self.bg, fg='#063047').pack(pady=(30,6))
        # name
        nf = tk.Frame(f, bg=self.bg)
        nf.pack(pady=8)
        tk.Label(nf, text="Ім'я:", font=('Segoe UI', 12), bg=self.bg).pack(side=tk.LEFT, padx=(0,8))
        self.name_entry = tk.Entry(nf, font=('Segoe UI', 12), width=36)
        self.name_entry.pack(side=tk.LEFT)

        # theme selector
        if USE_TTKBOOTSTRAP:
            tf = tk.Frame(f, bg=self.bg)
            tf.pack(pady=8)
            tk.Label(tf, text="Тема:", font=('Segoe UI', 11), bg=self.bg).pack(side=tk.LEFT, padx=(0,8))
            themes = ['flatly', 'litera', 'pulse', 'cyborg', 'solar']
            self.theme_var = tk.StringVar(value=themes[0])
            theme_menu = tk.OptionMenu(tf, self.theme_var, *themes)
            theme_menu.config(width=18)
            theme_menu.pack(side=tk.LEFT)
            tk.Button(tf, text="Застосувати", command=self.apply_theme).pack(side=tk.LEFT, padx=8)

        sf = tk.Frame(f, bg=self.bg)
        sf.pack(pady=12)
        tk.Label(sf, text="Виберіть тест:", font=('Segoe UI', 12), bg=self.bg).pack(side=tk.LEFT, padx=(0,8))
        self.test_var = tk.StringVar()
        tests = self.find_tests()
        if tests:
            self.test_var.set(tests[0])
        else:
            self.test_var.set('')
        self.tests_menu = tk.OptionMenu(sf, self.test_var, *tests)
        self.tests_menu.config(width=60)
        self.tests_menu.pack(side=tk.LEFT)

        bf = tk.Frame(f, bg=self.bg)
        bf.pack(pady=18)
        tk.Button(bf, text="Почати тест", font=('Segoe UI', 12), bg='#66b8ff', fg='white', command=self.start_pressed).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text="О программе", font=('Segoe UI', 12), command=lambda: self.show_frame('about')).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text="Логи (admin)", font=('Segoe UI', 12), command=self.prompt_logs_login).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text="Оновити список", font=('Segoe UI', 11), command=self.refresh_tests).pack(side=tk.LEFT, padx=6)

        tk.Label(f, text="Файли: .json, .test (+.key), XOR-text .test", font=('Segoe UI', 10), bg=self.bg).pack(pady=(10,0))

    def apply_theme(self):
        if not USE_TTKBOOTSTRAP:
            messagebox.showinfo("Тема", "ttkbootstrap не встановлено")
            return
        theme = self.theme_var.get()
        try:
            if self.tb_style:
                self.tb_style.theme_use(theme)
                messagebox.showinfo("Тема", f"Тему '{theme}' застосовано")
        except Exception as e:
            messagebox.showerror("Тема", f"Не вдалось застосувати тему: {e}")

    def refresh_tests(self):
        lst = self.find_tests()
        menu = self.tests_menu['menu']
        menu.delete(0, 'end')
        for t in lst:
            menu.add_command(label=t, command=lambda v=t: self.test_var.set(v))
        if lst:
            self.test_var.set(lst[0])
        else:
            self.test_var.set('')

    def find_tests(self):
        files = [f for f in os.listdir() if os.path.isfile(f)]
        tests = [f for f in files if f.endswith('.test') or f.endswith('.json')]
        tests.sort()
        return tests

    def start_pressed(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Ім'я", "Введіть ім'я")
            return
        if not self.test_var.get():
            messagebox.showwarning("Тест", "Виберіть тест")
            return
        self.user_name = name
        self.load_test(self.test_var.get())

    # ---------- About ----------
    def build_about(self):
        f = self.frame_about
        for w in f.winfo_children(): w.destroy()
        tk.Label(f, text="О програмі", font=('Segoe UI', 20, 'bold'), bg=self.bg).pack(pady=(30,10))
        about = (
            f"Версія: {APP_VERSION}\n"
            f"Автор: {APP_AUTHOR}\n"
            "Мова: Python 3\n\n"
            "Підтримка: .json, .test (Fernet + .key), XOR-text .test"
        )
        tk.Label(f, text=about, font=('Segoe UI', 12), bg=self.bg, justify=tk.LEFT).pack(padx=24, pady=6)
        tk.Button(f, text="Назад", font=('Segoe UI', 12), command=lambda: self.show_frame('start')).pack(pady=12)

    # ---------- Logs ----------
    def build_logs(self):
        f = self.frame_logs
        for w in f.winfo_children(): w.destroy()
        tk.Label(f, text="Логи", font=('Segoe UI', 18, 'bold'), bg=self.bg).pack(pady=(18,8))
        self.logs_text = tk.Text(f, width=110, height=25, font=('Segoe UI', 10))
        self.logs_text.pack(padx=12, pady=6)
        bf = tk.Frame(f, bg=self.bg)
        bf.pack(pady=8)
        tk.Button(bf, text="Оновити", command=self.populate_logs).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text="Очистити", command=self.clear_logs).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text="Назад", command=lambda: self.show_frame('start')).pack(side=tk.LEFT, padx=6)

    def prompt_logs_login(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Логи — пароль')
        dlg.geometry('360x140')
        dlg.resizable(False, False)
        tk.Label(dlg, text='Введіть пароль:', font=('Segoe UI', 12)).pack(pady=(12,6))
        pw_entry = tk.Entry(dlg, show='*', font=('Segoe UI', 12))
        pw_entry.pack(pady=6)
        def on_ok():
            val = pw_entry.get() or ''
            if val.lower() == 'admin':
                dlg.destroy()
                self.populate_logs()
                self.show_frame('logs')
            else:
                messagebox.showerror('Пароль', 'Невірний пароль')
                dlg.lift()
        def on_cancel():
            dlg.destroy()
        btnf = tk.Frame(dlg)
        btnf.pack(pady=8)
        tk.Button(btnf, text='OK', width=10, command=on_ok).pack(side=tk.LEFT, padx=6)
        tk.Button(btnf, text='Відмінити', width=10, command=on_cancel).pack(side=tk.LEFT, padx=6)
        pw_entry.focus_set()

    def populate_logs(self):
        logs = read_logs()
        self.logs_text.delete('1.0', tk.END)
        if not logs:
            self.logs_text.insert(tk.END, 'Логи відсутні.\n')
            return
        for e in logs:
            line = (f"{e.get('timestamp','')} | {e.get('name','')} | {e.get('test','')} | "
                    f"{e.get('correct','0')}/{e.get('total','0')} | {e.get('percent','0')}% | {e.get('score','0')}\n")
            self.logs_text.insert(tk.END, line)

    def clear_logs(self):
        if messagebox.askyesno('Очистити', 'Очистити всі логи?'):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.populate_logs()

    # ---------- Quiz ----------
    def build_quiz(self):
        f = self.frame_quiz
        for w in f.winfo_children(): w.destroy()
        top = tk.Frame(f, bg=self.bg)
        top.pack(fill=tk.X, pady=(12,6))
        self.lbl_testname = tk.Label(top, text='', font=('Segoe UI', 12), bg=self.bg)
        self.lbl_testname.pack(side=tk.LEFT, padx=12)
        self.lbl_timer = tk.Label(top, text='', font=('Segoe UI', 12, 'bold'), bg=self.bg, fg='#b02a2a')
        self.lbl_timer.pack(side=tk.RIGHT, padx=18)

        self.lbl_question = tk.Label(f, text='', font=('Segoe UI', 18, 'bold'), bg=self.bg, wraplength=920, justify=tk.LEFT)
        self.lbl_question.pack(padx=18, pady=(8,14))

        self.answers_container = tk.Frame(f, bg=self.bg)
        self.answers_container.pack(pady=(6,12))

        self.answer_buttons = []
        for i in range(6):
            ab = AnswerButton(self.answers_container, width=920, height=72,
                              base_color=self.colors[i % len(self.colors)], hover_color='#ffe6e0', text_color='#063047', callback=self.on_answer_clicked)
            self.answer_buttons.append(ab)

        bottom = tk.Frame(f, bg=self.bg)
        bottom.pack(fill=tk.X, pady=(6,18))
        self.lbl_progress = tk.Label(bottom, text='', font=('Segoe UI', 12), bg=self.bg)
        self.lbl_progress.pack(side=tk.LEFT, padx=16)
        tk.Button(bottom, text='Завершити тест', font=('Segoe UI', 12), bg='#ff7b7b', command=self.end_quiz_early).pack(side=tk.RIGHT, padx=14)
        tk.Button(bottom, text='Назад', font=('Segoe UI', 12), command=self.end_and_back).pack(side=tk.RIGHT, padx=6)

    def load_test(self, filename):
        path = filename if os.path.isabs(filename) else os.path.abspath(filename)
        self.current_test_path = path
        data = None
        try:
            # first: try self-contained .test (JSON wrapper with embedded key/payload)
            if path.endswith('.test'):
                try:
                    data = load_selfcontained_test(path)
                except Exception:
                    data = None
            # if no data yet, try other loaders
            if data is None:
                if path.endswith('.json'):
                    data = load_plain_json(path)
                else:
                    if USE_FERNET:
                        try:
                            data = load_fernet_external_key(path)
                        except Exception:
                            data = None
                    if data is None:
                        try:
                            data = load_xor_text(path)
                        except Exception:
                            data = None
                    if data is None:
                        data = load_plain_json(path)
            if not isinstance(data, list):
                raise ValueError('Формат тесту неправильний (очікується список).')
            for q in data:
                if 'question' not in q or 'options' not in q or 'answer' not in q:
                    raise ValueError('Кожне питання має містити поля question/options/answer')
                opts = q['options']
                a = q['answer']
                try:
                    ai = int(a)
                except Exception:
                    try:
                        ai = opts.index(str(a))
                    except Exception:
                        ai = None
                q['_answer_index'] = ai
            self.test_data = data
            self.start_quiz()
        except Exception as e:
            messagebox.showerror('Помилка', f'Не вдалось завантажити тест:\n{e}')

    def start_quiz(self):
        self.q_index = 0
        self.correct_count = 0
        self.show_frame('quiz')
        self.show_question()

    def show_question(self):
        self.cancel_timer()
        if self.q_index >= len(self.test_data):
            self.finish_quiz()
            return
        q = self.test_data[self.q_index]
        self.lbl_testname.config(text=f"Тест: {os.path.basename(self.current_test_path)}")
        self.lbl_question.config(text=f"Питання {self.q_index+1}: {q.get('question','')}")
        opts = q.get('options', [])
        for i, ab in enumerate(self.answer_buttons):
            if i < len(opts):
                ab.set_text(opts[i])
                ab.set_colors(base=self.colors[i % len(self.colors)], hover='#ffe6e0', text_color='#063047')
                ab.opt_index = i
                if not ab.visible:
                    ab.pack(pady=8)
            else:
                if ab.visible:
                    ab.pack_forget()
        self.lbl_progress.config(text=f"Пройдено: {self.q_index} / {len(self.test_data)}")
        self.remaining = 60
        self.update_timer_label()
        self.schedule_timer()

    def schedule_timer(self):
        self.cancel_timer()
        def tick():
            self.remaining -= 1
            self.update_timer_label()
            if self.remaining <= 0:
                play_sound_buf(SOUND_TIMEOUT)
                self.on_time_out()
            else:
                self.timer_job = self.root.after(1000, tick)
        self.timer_job = self.root.after(1000, tick)

    def update_timer_label(self):
        mins = self.remaining // 60
        secs = self.remaining % 60
        self.lbl_timer.config(text=f"Залишилось: {mins:02d}:{secs:02d}")

    def cancel_timer(self):
        if self.timer_job:
            try:
                self.root.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

    def on_time_out(self):
        for ab in self.answer_buttons:
            if ab.visible:
                ab.set_feedback(wrong=True)
        self.root.after(500, self._advance_after_feedback_time)

    def _advance_after_feedback_time(self):
        self.cancel_timer()
        self.q_index += 1
        self.show_question()

    def on_answer_clicked(self, opt_index, widget):
        self.cancel_timer()
        q = self.test_data[self.q_index]
        correct_idx = q.get('_answer_index')
        if correct_idx is not None and opt_index == correct_idx:
            widget.set_feedback(correct=True)
            play_sound_buf(SOUND_CORRECT)
            self.correct_count += 1
        else:
            widget.set_feedback(wrong=True)
            # highlight correct among visible
            visible = [ab for ab in self.answer_buttons if ab.visible]
            if correct_idx is not None and 0 <= correct_idx < len(visible):
                visible[correct_idx].set_feedback(correct=True)
            play_sound_buf(SOUND_WRONG)
        self.root.after(500, self._advance_after_feedback)

    def _advance_after_feedback(self):
        self.q_index += 1
        self.show_question()

    def finish_quiz(self):
        self.cancel_timer()
        total = len(self.test_data)
        correct = self.correct_count
        scaled = round((correct / total) * 12) if total > 0 else 0
        percent = round((correct / total) * 100, 1) if total > 0 else 0
        # result window with return button
        res = tk.Toplevel(self.root)
        res.title('Результат')
        res.geometry('560x260')
        res.resizable(False, False)
        tk.Label(res, text='Результат тесту', font=('Segoe UI', 16, 'bold')).pack(pady=(12,8))
        txt = (
            f"Ім'я: {self.user_name}\n"
            f"Тест: {os.path.basename(self.current_test_path) if self.current_test_path else ''}\n"
            f"Правильних: {correct} з {total}\n"
            f"Процент: {percent}%\n"
            f"Оцінка (0-12): {scaled}"
        )
        tk.Label(res, text=txt, font=('Segoe UI', 12), justify=tk.LEFT).pack(padx=12, pady=8)
        btnf = tk.Frame(res)
        btnf.pack(pady=12)
        tk.Button(btnf, text='Повернутися на початок', width=20, command=lambda: self._return_to_start(res)).pack(side=tk.LEFT, padx=8)
        tk.Button(btnf, text='Закрити', width=12, command=res.destroy).pack(side=tk.LEFT, padx=8)
        # log
        entry = {
            'timestamp': datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
            'name': self.user_name,
            'test': os.path.basename(self.current_test_path) if self.current_test_path else '',
            'correct': correct,
            'total': total,
            'percent': percent,
            'score': scaled
        }
        append_log(entry)

    def _return_to_start(self, res_window):
        try:
            res_window.destroy()
        except Exception:
            pass
        self.show_frame('start')

    def end_quiz_early(self):
        if messagebox.askyesno('Завершити', 'Закінчити тест достроково?'):
            self.finish_quiz()

    def end_and_back(self):
        if messagebox.askyesno('Вихід', 'Завершити тест і повернутися на початок?'):
            self.cancel_timer()
            self.show_frame('start')

    # ---------- Frame control ----------
    def show_frame(self, name):
        frames = {
            'start': self.frame_start,
            'about': self.frame_about,
            'quiz': self.frame_quiz,
            'logs': self.frame_logs
        }
        for k, fr in frames.items():
            if k == name:
                fr.lift()
            else:
                fr.lower()

# --- Run ---
def main():
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
