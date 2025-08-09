Python 3.13.6 (tags/v3.13.6:4e66535, Aug  6 2025, 14:36:00) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
Automatic Audio Beat Maker Software Coding use it python 

#!/usr/bin/env python3
"""
Simple Automatic Audio Beat Maker
Save as beatmaker.py

Dependencies:
  pip install numpy simpleaudio

To build an exe:
  pip install pyinstaller
  pyinstaller --onefile beatmaker.py
  -> dist/beatmaker.exe
"""

import sys
import struct
import wave
import math
import random
import argparse
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import numpy as np
except Exception:
    print("Missing dependency: numpy. Install with: pip install numpy")
    sys.exit(1)

PLAYBACK_AVAILABLE = True
try:
    import simpleaudio as sa
except Exception:
    PLAYBACK_AVAILABLE = False

SAMPLE_RATE = 44100  # CD quality


# -------------------------
# Sound generators
# -------------------------
def sine(frequency, length_secs, amp=1.0):
    t = np.linspace(0, length_secs, int(SAMPLE_RATE * length_secs), False)
    return amp * np.sin(2 * np.pi * frequency * t)


def exponential_decay_envelope(length_samples, attack=0.001, decay=0.5):
    # quick attack then exponential decay
    env = np.ones(length_samples)
    attack_samples = max(1, int(attack * SAMPLE_RATE))
    env[:attack_samples] = np.linspace(0, 1, attack_samples)
    tail = np.arange(length_samples - attack_samples)
    # normalize tail to start at 1 and decay to near 0
    env[attack_samples:] = np.exp(-tail / (decay * SAMPLE_RATE))
    return env


def kick(length_secs=0.25):
    # Kick: pitch drop sine + envelope
    length = length_secs
    n = int(SAMPLE_RATE * length)
    t = np.linspace(0, length, n, False)
    # pitch falls from about 120Hz to 40Hz
    freqs = np.linspace(120, 40, n)
    wave_data = np.sin(2 * np.pi * freqs * t)
    env = exponential_decay_envelope(n, attack=0.001, decay=0.08)
    return (wave_data * env * 1.0).astype(np.float32)


def snare(length_secs=0.18):
    # Snare: noisy + short oscillator
    n = int(SAMPLE_RATE * length_secs)
    noise = np.random.normal(0, 1, n)
    tone = sine(1800, length_secs, amp=0.2)
    env = exponential_decay_envelope(n, attack=0.001, decay=0.06)
    out = (noise * 0.6 + tone * 0.6) * env
    # small highpass-ish by subtracting moving average
    kernel = 3
    out = out - np.convolve(out, np.ones(kernel) / kernel, mode='same')
    return out.astype(np.float32)

... 
... def hihat(length_secs=0.06):
...     n = int(SAMPLE_RATE * length_secs)
...     noise = np.random.normal(0, 1, n)
...     env = exponential_decay_envelope(n, attack=0.0005, decay=0.02)
...     # bright thin sound
...     out = noise * env * 0.6
...     # quick highpass effect
...     out = out - np.convolve(out, np.ones(2) / 2, mode='same')
...     return out.astype(np.float32)
... 
... 
... # -------------------------
... # Pattern / sequencing
... # -------------------------
... DEFAULT_INSTRUMENTS = ['kick', 'snare', 'hihat']
... 
... 
... def create_pattern(steps=16, prob_kick=0.8, prob_snare=0.35, prob_hihat=0.7, variation=0.2):
...     """
...     Creates a pattern dictionary with booleans for each step for each instrument.
...     variation adjusts randomness per step.
...     """
...     pattern = {'kick': [False] * steps, 'snare': [False] * steps, 'hihat': [False] * steps}
...     for i in range(steps):
...         # Kick often on step 0 and 8 for 4/4 feel, plus randomness
...         base_k = (i % 4 == 0)
...         pattern['kick'][i] = base_k or (random.random() < prob_kick * (1 - variation + random.random() * variation))
...         pattern['snare'][i] = (i % 8 == 4) or (random.random() < prob_snare * (1 - variation + random.random() * variation))
...         pattern['hihat'][i] = (random.random() < prob_hihat * (1 - variation + random.random() * variation))
...     # Clean: ensure at least 1 kick and 1 snare
...     if not any(pattern['kick']): pattern['kick'][0] = True
...     if not any(pattern['snare']): pattern['snare'][4] = True
