#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import wave
import struct
import numpy as np
from scipy.fftpack import fft
from pydub import AudioSegment
from colorama import init, Fore, Back, Style

# Inicializácia colorama pre Windows
init()

# ASCII art "Apple" logo s dvoma malými odhryzkami na pravej strane
APPLE_LOGO = r"""
      ,--./,-.
     / #      \
    |          |
     \        /
  ,--./\__/\./\--.
 /                 \
|   \   \__/   /    |
 \    \      /     /
  `\            ,'
     `-._____.-'
"""

# Mapa znak → frekvencia
CHAR_FREQ = {
    **{ch: 400 + i*10 for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")},
    ' ': 660, '.': 670, ',': 680, '-': 690, '+': 700, '_': 710, '=': 720,
    '#': 730, '%': 740, '?': 750, '!': 760, '&': 770, '/': 780, '\\': 790,
    '|': 800, '*': 810, '~': 820, '×': 830, '@': 840,
    **{str(i): 850 + i*10 for i in range(1, 10)}, '0': 940
}
# Invertovaná mapa
FREQ_CHAR = {v: k for k, v in CHAR_FREQ.items()}

# Parametre
DURATION = 0.5   # sekundy
SAMPLE_RATE = 44100
TOLERANCE = 5    # Hz tolerancia pri detekcii

def print_ui():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Back.GREEN + Fore.BLACK + APPLE_LOGO + Style.RESET_ALL)
    print(Back.GREEN + Fore.BLACK + "  S I N G A L   E N C O D E R / D E C O D E R  " + Style.RESET_ALL)
    print()

def generate_tone(freq, duration=DURATION):
    """Vygeneruje sinový signál danej frekvencie."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave_data = 0.5 * np.sin(2 * np.pi * freq * t)
    return wave_data

def save_wave(data, filename):
    """Uloží numpy pole float [-1..1] do WAV súboru 16‑bit."""
    scaled = np.int16(data * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(scaled.tobytes())

def load_audio(path):
    """Načíta audio a vráti numpy pole float [-1..1]."""
    audio = AudioSegment.from_file(path)
    audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(1)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    return samples / 32768.0

def chunkify(data, chunk_size):
    """Rozdelí pole na bloky po chunk_size vzorkách."""
    n = len(data)
    for i in range(0, n, chunk_size):
        yield data[i:i+chunk_size]

def detect_freq(block):
    """Detekuje dominantnú frekvenciu v danom bloku."""
    # FFT
    N = len(block)
    windowed = block * np.hanning(N)
    spectrum = np.abs(fft(windowed))[:N//2]
    freqs = np.fft.fftfreq(N, 1/SAMPLE_RATE)[:N//2]
    peak = freqs[np.argmax(spectrum)]
    return peak

def encode_table(text, out_file):
    """Enkóduje text podľa CHAR_FREQ tabulky do WAV."""
    signal = np.array([], dtype=np.float32)
    for ch in text.upper():
        f = CHAR_FREQ.get(ch)
        if f is None:
            print(f"Neznak '{ch}', preskakujem.")
            continue
        tone = generate_tone(f)
        signal = np.concatenate([signal, tone])
    save_wave(signal, out_file)
    print(f"Ulozené do {out_file}")

def decode_table(path):
    """Načíta a dekóduje WAV podľa CHAR_FREQ tabulky."""
    data = load_audio(path)
    chunk_size = int(SAMPLE_RATE * DURATION)
    result = []
    for block in chunkify(data, chunk_size):
        if len(block) < chunk_size:
            break
        peak = detect_freq(block)
        # nájdi najbližšiu frekvenciu v tabuľke
        diffs = {abs(peak - f): f for f in FREQ_CHAR}
        closest = diffs[min(diffs)]
        if abs(peak - closest) > TOLERANCE:
            raise ValueError(f"Chybná frekvencia: {peak:.1f} Hz")
        result.append(FREQ_CHAR[closest])
    return ''.join(result)

def encode_binary(text, out_file):
    """Enkóduje text ako binárny reťazec do WAV (0→500 Hz, 1→950 Hz)."""
    bits = ''.join(f"{ord(c):08b}" for c in text)
    signal = np.array([], dtype=np.float32)
    for b in bits:
        f = 500 if b=='0' else 950
        signal = np.concatenate([signal, generate_tone(f)])
    save_wave(signal, out_file)
    print(f"Ulozené do {out_file}")

def decode_binary(path):
    """Dekóduje WAV ako binárny reťazec podľa 0/1 frekvencií."""
    data = load_audio(path)
    chunk_size = int(SAMPLE_RATE * DURATION)
    bits = []
    for block in chunkify(data, chunk_size):
        if len(block) < chunk_size:
            break
        peak = detect_freq(block)
        if abs(peak - 500) < abs(peak - 950):
            bits.append('0')
        else:
            bits.append('1')
    # po 8 bitoch -> znak
    text = ''
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte)<8: break
        text += chr(int(''.join(byte), 2))
    return text

def robust_decode(func, path):
    """Pokusí sa trikrát dekódovať, inak vyhodí chybu."""
    for attempt in range(3):
        try:
            return func(path)
        except Exception as e:
            print(f"Chyba dekódu (pokus {attempt+1}/3): {e}")
    print("Súbor pravdepodobne poškodený alebo zlý formát.")
    return None

def main():
    print_ui()
    print("1) Enkódovať  2) Dekódovať")
    choice = input("> ").strip()
    print("Metóda: 1) Tabuľka  2) Binárne")
    method = input("> ").strip()

    if choice == '1':  # encoder
        txt = input("Zadaj text: ")
        path = input("Uložiť ako (napr. out.wav): ").strip()
        if method == '1':
            encode_table(txt, path)
        else:
            encode_binary(txt, path)

    else:  # decoder
        path = input("Cesta k audio súboru: ").strip()
        if method == '1':
            res = robust_decode(decode_table, path)
        else:
            res = robust_decode(decode_binary, path)
        if res is not None:
            print("Decoded text:\n", res)

if __name__ == "__main__":
    main()