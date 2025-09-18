#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual MIDI Keyboard + 16‑Step Sequencer

Dependencies (install first):
    pip install mido python-rtmidi

Optional EXE (Windows):
    pip install pyinstaller
    pyinstaller -F -w --name VirtualMIDIKeyboard midi_keyboard_sequencer.py

Tested backends: python-rtmidi (works with USB-MIDI devices)

Notes:
- Click the piano keys or use your computer keyboard to play notes.
- Select your USB-MIDI output from the dropdown (⚠ change while stopped for safety).
- Use the 16-step grid to program patterns. Press ▶ Play to start.
- Tempo, swing, channel, velocity, and root note are adjustable.
- Close the app safely to send note-off and stop the sequencer.
"""

import sys
import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional

import mido
import tkinter as tk
from tkinter import ttk, messagebox

############################################################
# MIDI UTILITIES
############################################################

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
PENTATONIC_MAJOR = [0, 2, 4, 7, 9]
PENTATONIC_MINOR = [0, 3, 5, 7, 10]

SCALES = {
    'Major (Ionian)': MAJOR_SCALE,
    'Minor (Aeolian)': MINOR_SCALE,
    'Pentatonic Major': PENTATONIC_MAJOR,
    'Pentatonic Minor': PENTATONIC_MINOR,
}

COMPUTER_KEYS = "zsxcfvgbnjmk,./"  # map to white/black combo starting C


def note_number(name: str, octave: int) -> int:
    """Convert note name and octave (e.g., ('C#', 4)) to MIDI note number."""
    return NOTE_NAMES.index(name) + (octave + 1) * 12


############################################################
# DATA CLASSES
############################################################

@dataclass
class SequencerState:
    steps: int = 16
    rows: int = 8
    pattern: List[List[bool]] = field(default_factory=lambda: [[False]*16 for _ in range(8)])
    root_note: int = note_number('C', 4)  # C4
    scale_name: str = 'Major (Ionian)'
    channel: int = 1  # 1-16 (MIDI channels are 0-15 internally)
    velocity: int = 100
    tempo_bpm: int = 120
    swing_percent: int = 0  # 0..100
    length_ratio: float = 0.9  # note length as ratio of step duration


############################################################
# MAIN APP
############################################################

class MidiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtual MIDI Keyboard + Sequencer")
        self.geometry("1000x680")
        self.minsize(900, 620)

        self.midi_out: Optional[mido.ports.BaseOutput] = None
        self.midi_port_name: Optional[str] = None
        self._active_notes = set()  # to send proper note_off on quit

        self.seq_state = SequencerState()
        self.seq_thread: Optional[threading.Thread] = None
        self.seq_running = threading.Event()
        self.seq_lock = threading.Lock()
        self.current_step = 0

        self._build_ui()
        self._bind_keys()
        self.after(200, self._auto_open_first_port)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    ########################################################
    # UI
    ########################################################
    def _build_ui(self):
        # Top bar: MIDI port, channel, velocity
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        ttk.Label(top, text="MIDI Output:").pack(side="left")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top, textvariable=self.port_var, width=45, state="readonly")
        self._refresh_ports()
        self.port_combo.pack(side="left", padx=6)
        ttk.Button(top, text="Refresh", command=self._refresh_ports).pack(side="left")
        ttk.Button(top, text="Open", command=self._open_selected_port).pack(side="left", padx=6)
        ttk.Button(top, text="Close", command=self._close_port).pack(side="left")

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=6)

        # Piano frame
        piano_frame = ttk.LabelFrame(self, text="Virtual Piano")
        piano_frame.pack(fill="x", padx=10, pady=6)

        ctrl = ttk.Frame(piano_frame)
        ctrl.pack(fill="x", pady=6)
        ttk.Label(ctrl, text="Octave:").pack(side="left")
        self.octave_var = tk.IntVar(value=4)
        ttk.Spinbox(ctrl, from_=0, to=8, width=4, textvariable=self.octave_var).pack(side="left", padx=6)

        ttk.Label(ctrl, text="Velocity:").pack(side="left")
        self.vel_var = tk.IntVar(value=self.seq_state.velocity)
        ttk.Scale(ctrl, from_=1, to=127, orient="horizontal", variable=self.vel_var, length=200).pack(side="left", padx=6)

        ttk.Label(ctrl, text="Channel:").pack(side="left")
        self.chan_var = tk.IntVar(value=self.seq_state.channel)
        ttk.Spinbox(ctrl, from_=1, to=16, width=4, textvariable=self.chan_var).pack(side="left", padx=6)

        self.sustain_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(ctrl, text="Sustain", variable=self.sustain_var).pack(side="left", padx=6)

        # Draw simple 2-octave piano (24 notes) starting from chosen octave
        self.piano_canvas = tk.Canvas(piano_frame, height=160, bg="#222")
        self.piano_canvas.pack(fill="x", padx=8, pady=8)
        self._draw_piano()
        self.piano_canvas.bind("<ButtonPress-1>", self._on_piano_press)
        self.piano_canvas.bind("<ButtonRelease-1>", self._on_piano_release)

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=6)

        # Sequencer
        seq_box = ttk.LabelFrame(self, text="16‑Step Sequencer")
        seq_box.pack(fill="both", expand=True, padx=10, pady=6)

        seq_ctrl = ttk.Frame(seq_box)
        seq_ctrl.pack(fill="x", pady=6)

        ttk.Label(seq_ctrl, text="Root:").pack(side="left")
        self.root_note_var = tk.StringVar(value="C4")
        self.root_entry = ttk.Entry(seq_ctrl, width=4, textvariable=self.root_note_var)
        self.root_entry.pack(side="left", padx=4)

        ttk.Label(seq_ctrl, text="Scale:").pack(side="left")
        self.scale_var = tk.StringVar(value=self.seq_state.scale_name)
        self.scale_combo = ttk.Combobox(seq_ctrl, textvariable=self.scale_var, values=list(SCALES.keys()), width=20, state="readonly")
        self.scale_combo.pack(side="left", padx=4)

        ttk.Label(seq_ctrl, text="Tempo (BPM):").pack(side="left")
        self.tempo_var = tk.IntVar(value=self.seq_state.tempo_bpm)
        ttk.Spinbox(seq_ctrl, from_=20, to=300, textvariable=self.tempo_var, width=5).pack(side="left", padx=4)

        ttk.Label(seq_ctrl, text="Swing %:").pack(side="left")
        self.swing_var = tk.IntVar(value=self.seq_state.swing_percent)
        ttk.Spinbox(seq_ctrl, from_=0, to=75, textvariable=self.swing_var, width=4).pack(side="left", padx=4)

        ttk.Label(seq_ctrl, text="Gate (0.1–1.0):").pack(side="left")
        self.gate_var = tk.DoubleVar(value=self.seq_state.length_ratio)
        ttk.Spinbox(seq_ctrl, from_=0.1, to=1.0, increment=0.05, textvariable=self.gate_var, width=5).pack(side="left", padx=4)

        ttk.Button(seq_ctrl, text="Clear", command=self._clear_pattern).pack(side="right", padx=6)
        self.play_btn = ttk.Button(seq_ctrl, text="▶ Play", command=self.toggle_play)
        self.play_btn.pack(side="right", padx=6)

        # Grid
        self.grid_frame = ttk.Frame(seq_box)
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_buttons: List[List[ttk.Checkbutton]] = []
        self.step_vars: List[List[tk.BooleanVar]] = []

        for r in range(self.seq_state.rows):
            row_vars = []
            row_buttons = []
            ttk.Label(self.grid_frame, text=f"Row {r+1}").grid(row=r+1, column=0, padx=4, pady=2, sticky="w")
            for c in range(self.seq_state.steps):
                v = tk.BooleanVar(value=False)
                btn = ttk.Checkbutton(self.grid_frame, variable=v)
                btn.grid(row=r+1, column=c+1, padx=2, pady=2)
                row_vars.append(v)
                row_buttons.append(btn)
            self.step_vars.append(row_vars)
            self.grid_buttons.append(row_buttons)

        # Column headers
        ttk.Label(self.grid_frame, text="").grid(row=0, column=0)
        for c in range(self.seq_state.steps):
            ttk.Label(self.grid_frame, text=f"{c+1}").grid(row=0, column=c+1)

        # Current step indicator
        self.step_highlights = []
        for c in range(self.seq_state.steps):
            lbl = tk.Label(self.grid_frame, text=" ", width=2, bg=self._step_bg(False))
            lbl.grid(row=self.seq_state.rows+2, column=c+1, pady=(6, 0))
            self.step_highlights.append(lbl)

        info = ttk.Label(seq_box, text=(
            "Tip: Each row is a scale degree (1..8) starting from Root. "
            "Click boxes to enable notes per step."
        ))
        info.pack(anchor="w", padx=6, pady=4)

    def _step_bg(self, active: bool) -> str:
        return "#4caf50" if active else self.cget("bg")

    def _refresh_ports(self):
        ports = mido.get_output_names()
        if not ports:
            ports = ["<no MIDI outputs found>"]
        self.port_combo["values"] = ports
        if ports:
            self.port_var.set(ports[0])

    def _open_selected_port(self):
        name = self.port_var.get()
        if not name or name.startswith("<no "):
            messagebox.showwarning("MIDI", "No MIDI output selected/found.")
            return
        try:
            self._close_port()
            self.midi_out = mido.open_output(name)
            self.midi_port_name = name
        except Exception as e:
            messagebox.showerror("MIDI", f"Failed to open port:\n{e}")

    def _auto_open_first_port(self):
        if self.midi_out is None:
            ports = mido.get_output_names()
            if ports:
                try:
                    self.midi_out = mido.open_output(ports[0])
                    self.midi_port_name = ports[0]
                except Exception:
                    pass

    def _close_port(self):
        if self.midi_out is not None:
            try:
                self._all_notes_off()
                self.midi_out.close()
            except Exception:
                pass
        self.midi_out = None
        self.midi_port_name = None

    ########################################################
    # PIANO RENDERING & INTERACTION
    ########################################################
    def _draw_piano(self):
        self.piano_canvas.delete("all")
        width = self.piano_canvas.winfo_width() or self.piano_canvas.winfo_reqwidth()
        white_keys = 14  # two octaves C..B
        white_w = max(20, int(width / white_keys))
        height = 160
        black_h = int(height * 0.6)
        # Layout pattern for black keys across two octaves starting at C
        black_pattern = [1, 1, 0, 1, 1, 1, 0] * 2  # 14 white keys -> 14 entries with zeros where E/B
        self._white_rects = []
        self._black_rects = []
        start_oct = self.octave_var.get()
        # Draw white keys first
        for i in range(white_keys):
            x0 = i * white_w
            x1 = x0 + white_w - 1
            note_idx = i * 2 - (i//7)  # map white index to semitone index in octave
            # Calculate note for the white key
            n_in_octave = [0,2,4,5,7,9,11]
            degree = i % 7
            oct_off = i // 7
            semitone = n_in_octave[degree] + 12*oct_off
            midi_note = note_number('C', start_oct) + semitone

            rect = self.piano_canvas.create_rectangle(x0, 0, x1, height, fill="white", outline="black", tags=("white", f"note_{midi_note}"))
            self._white_rects.append((rect, midi_note))
            label = NOTE_NAMES[midi_note % 12]
            self.piano_canvas.create_text((x0+x1)//2, height-12, text=f"{label}")
        # Draw black keys
        for i in range(white_keys):
            degree = i % 7
            if degree in (2, 6):
                # No black key after E (degree 2) and B (degree 6)
                continue
            # Position black key between this white and next
            x0 = i * white_w + int(white_w*0.65)
            x1 = x0 + int(white_w*0.7)
            # Compute midi note between white keys
            # Figure semitone of this white key
            n_in_octave = [0,2,4,5,7,9,11]
            oct_off = i // 7
            semitone_base = n_in_octave[degree] + 12*oct_off
            midi_note = note_number('C', start_oct) + semitone_base + 1
            rect = self.piano_canvas.create_rectangle(x0, 0, x1, black_h, fill="black", outline="black", tags=("black", f"note_{midi_note}"))
            self._black_rects.append((rect, midi_note))

    def _find_note_from_xy(self, event) -> Optional[int]:
        # Prefer black keys (drawn last, on top)
        items = self.piano_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in items[::-1]:  # topmost first
            tags = self.piano_canvas.gettags(item)
            for t in tags:
                if t.startswith("note_"):
                    return int(t.split("_")[1])
        return None

    def _on_piano_press(self, event):
        midi_note = self._find_note_from_xy(event)
        if midi_note is not None:
            self._note_on(midi_note, self.vel_var.get(), self.chan_var.get())

    def _on_piano_release(self, event):
        midi_note = self._find_note_from_xy(event)
        if midi_note is not None and not self.sustain_var.get():
            self._note_off(midi_note, self.chan_var.get())

    def _bind_keys(self):
        # Map QWERTY area to scale starting from C in selected octave (white-ish)
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        self._pressed_keys = {}

    def _on_key_press(self, event):
        key = event.keysym.lower()
        if key in self._pressed_keys:
            return
        # Map a simple chromatic starting C
        try:
            idx = "zsxcfvgbnjmk,./".index(event.char)
        except Exception:
            return
        base = note_number('C', self.octave_var.get())
        midi_note = base + idx
        self._pressed_keys[key] = midi_note
        self._note_on(midi_note, self.vel_var.get(), self.chan_var.get())

    def _on_key_release(self, event):
        key = event.keysym.lower()
        midi_note = self._pressed_keys.pop(key, None)
        if midi_note is not None and not self.sustain_var.get():
            self._note_off(midi_note, self.chan_var.get())

    ########################################################
    # MIDI SEND
    ########################################################
    def _note_on(self, midi_note: int, velocity: int, channel_ui: int):
        if self.midi_out is None:
            return
        channel = max(0, min(15, channel_ui - 1))
        velocity = max(1, min(127, int(velocity)))
        msg = mido.Message('note_on', note=midi_note, velocity=velocity, channel=channel)
        try:
            self.midi_out.send(msg)
            self._active_notes.add((midi_note, channel))
        except Exception:
            pass

    def _note_off(self, midi_note: int, channel_ui: int):
        if self.midi_out is None:
            return
        channel = max(0, min(15, channel_ui - 1))
        msg = mido.Message('note_off', note=midi_note, velocity=0, channel=channel)
        try:
            self.midi_out.send(msg)
            self._active_notes.discard((midi_note, channel))
        except Exception:
            pass

    def _all_notes_off(self):
        if self.midi_out is None:
            return
        for (n, ch) in list(self._active_notes):
            try:
                self.midi_out.send(mido.Message('note_off', note=n, velocity=0, channel=ch))
            except Exception:
                pass
        self._active_notes.clear()

    ########################################################
    # SEQUENCER
    ########################################################
    def _parse_root(self) -> int:
        txt = self.root_note_var.get().strip().upper()
        # expected like C4 or F#3
        try:
            if len(txt) >= 2 and txt[1] == '#':
                name = txt[:2]
                octv = int(txt[2:])
            else:
                name = txt[0]
                octv = int(txt[1:])
            if name not in NOTE_NAMES:
                raise ValueError
            return note_number(name, octv)
        except Exception:
            messagebox.showwarning("Root note", "Enter like C4, F#3, etc. Defaulting to C4.")
            return note_number('C', 4)

    def _gather_pattern(self) -> List[List[bool]]:
        patt = []
        for r in range(self.seq_state.rows):
            row = [self.step_vars[r][c].get() for c in range(self.seq_state.steps)]
            patt.append(row)
        return patt

    def _clear_pattern(self):
        for r in range(self.seq_state.rows):
            for c in range(self.seq_state.steps):
                self.step_vars[r][c].set(False)

    def toggle_play(self):
        if self.seq_running.is_set():
            self._stop_seq()
        else:
            self._start_seq()

    def _start_seq(self):
        if self.midi_out is None:
            messagebox.showwarning("MIDI", "Open a MIDI output first.")
            return
        with self.seq_lock:
            self.seq_state.pattern = self._gather_pattern()
            self.seq_state.root_note = self._parse_root()
            self.seq_state.scale_name = self.scale_var.get()
            self.seq_state.channel = int(self.chan_var.get())
            self.seq_state.velocity = int(self.vel_var.get())
            self.seq_state.tempo_bpm = int(self.tempo_var.get())
            self.seq_state.swing_percent = int(self.swing_var.get())
            self.seq_state.length_ratio = float(self.gate_var.get())
        self.seq_running.set()
        self.play_btn.configure(text="■ Stop")
        self.seq_thread = threading.Thread(target=self._seq_loop, daemon=True)
        self.seq_thread.start()

    def _stop_seq(self):
        self.seq_running.clear()
        self.play_btn.configure(text="▶ Play")
        self._all_notes_off()

    def _seq_loop(self):
        steps = self.seq_state.steps
        rows = self.seq_state.rows
        scale = SCALES.get(self.seq_state.scale_name, MAJOR_SCALE)
        channel = max(0, min(15, self.seq_state.channel - 1))
        velocity = max(1, min(127, self.seq_state.velocity))

        # Precompute row -> midi note mapping (scale degrees 1..8)
        degrees = [scale[i % len(scale)] + 12 * (i // len(scale)) for i in range(rows)]
        notes_map = [self.seq_state.root_note + d for d in degrees]

        swing = max(0, min(100, self.seq_state.swing_percent)) / 100.0
        base_step_dur = 60.0 / max(20, self.seq_state.tempo_bpm) / 2  # 8th notes default
        # swing alternates long-short: long = base*(1+swing*0.5), short = base*(1-swing*0.5)
        long = base_step_dur * (1.0 + swing * 0.5)
        short = base_step_dur * (1.0 - swing * 0.5)

        step = 0
        last_sent: List[int] = []  # notes currently on this step
        while self.seq_running.is_set():
            # Visual highlight
            self._highlight_step(step)

            # Gather which rows are active on this step
            with self.seq_lock:
                pattern = self.seq_state.pattern
                gate = max(0.05, min(1.0, self.seq_state.length_ratio))

            # Turn off notes from previous step
            for n in last_sent:
                try:
                    self.midi_out.send(mido.Message('note_off', note=n, velocity=0, channel=channel))
                    self._active_notes.discard((n, channel))
                except Exception:
                    pass
            last_sent = []

            # Send new notes for this step
            for r in range(rows):
                if pattern[r][step]:
                    n = notes_map[r]
                    try:
                        self.midi_out.send(mido.Message('note_on', note=n, velocity=velocity, channel=channel))
                        self._active_notes.add((n, channel))
                        last_sent.append(n)
                    except Exception:
                        pass

            # Sleep for step duration and schedule note-off halfway according to gate
            dur = long if (step % 2 == 0) else short
            note_len = dur * gate
            t0 = time.perf_counter()
            while True:
                if not self.seq_running.is_set():
                    break
                elapsed = time.perf_counter() - t0
                if elapsed >= note_len:
                    # early note-off (gate) for this step
                    for n in list(last_sent):
                        try:
                            self.midi_out.send(mido.Message('note_off', note=n, velocity=0, channel=channel))
                            self._active_notes.discard((n, channel))
                        except Exception:
                            pass
                    last_sent.clear()
                    break
                time.sleep(0.001)
            # Finish rest of step time
            t1 = time.perf_counter()
            while self.seq_running.is_set() and (time.perf_counter() - t0) < dur:
                time.sleep(0.001)

            step = (step + 1) % steps
        # Ensure all notes are off at the end
        for n in list(last_sent):
            try:
                self.midi_out.send(mido.Message('note_off', note=n, velocity=0, channel=channel))
            except Exception:
                pass
        self._highlight_step(None)

    def _highlight_step(self, step: Optional[int]):
        # Called from seq thread; marshal to UI thread
        def apply():
            for i, lbl in enumerate(self.step_highlights):
                lbl.configure(bg=self._step_bg(i == step))
        self.after(0, apply)

    ########################################################
    # LIFECYCLE
    ########################################################
    def on_close(self):
        try:
            self._stop_seq()
        except Exception:
            pass
        try:
            if self.sustain_var.get():
                # All Notes Off CC 123
                if self.midi_out is not None:
                    ch = max(0, min(15, self.chan_var.get()-1))
                    self.midi_out.send(mido.Message('control_change', control=123, value=0, channel=ch))
        except Exception:
            pass
        try:
            self._all_notes_off()
        finally:
            self._close_port()
            self.destroy()


if __name__ == "__main__":
    # Ensure RtMidi backend is used
    mido.set_backend('mido.backends.rtmidi')
    app = MidiApp()
    # Keep piano responsive on resize
    def _on_resize(event):
        app._draw_piano()
    app.piano_canvas.bind("<Configure>", _on_resize)
    app.mainloop()

