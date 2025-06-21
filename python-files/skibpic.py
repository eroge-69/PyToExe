import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image
from scipy.io import wavfile
import os
import re
import random
import string
import base64
import struct

# --- Palette Setup ---
STEPS = [0, 85, 170, 255]
PALETTE = [(r, g, b) for r in STEPS for g in STEPS for b in STEPS]
PALETTE_NP = np.array(PALETTE, dtype=np.int32)
INDEX_TO_COLOR = {i: c for i, c in enumerate(PALETTE)}

def quantize_image_to_palette(img_array: np.ndarray, palette_np: np.ndarray) -> np.ndarray:
    """Quantizes an entire image to the given palette using NumPy for performance."""
    h, w, _ = img_array.shape
    pixels = img_array.astype(np.int32).reshape(-1, 3)
    distances = np.sum((pixels[:, np.newaxis, :] - palette_np[np.newaxis, :, :])**2, axis=2)
    indices = np.argmin(distances, axis=1)
    return indices.reshape(h, w)

# Chinese characters for digits encoding
CHINESE_DIGITS = {
    '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
    '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
}
CHINESE_CHAR_TO_NUM = {v: k for k, v in CHINESE_DIGITS.items()}

# Build a regex pattern to match two Chinese characters from our set
chinese_char_set = "".join(CHINESE_DIGITS.values())
# Using re.escape to ensure any special regex characters in the set are handled, though not strictly needed for these specific chars.
TOKEN_RE = re.compile(f"[{re.escape(chinese_char_set)}]{{2}}")
NOISE_RE = re.compile(r"\*+[\da-z]+\*+", re.IGNORECASE)

def generate_key_bytes(length=16):
    return bytes(random.choices(string.ascii_letters.encode('ascii') + string.digits.encode('ascii'), k=length))

def xor_encrypt_bytes(data_bytes: bytes, key: bytes) -> bytes:
    # Ensure key is not empty to prevent IndexError
    if not key:
        raise ValueError("Encryption key cannot be empty.")
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data_bytes)])

def analyze_audio(wav_path):
    rate, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data[:, 0]

    n = len(data)
    window = np.hanning(n)
    fft = np.fft.fft(data * window)
    freq = np.fft.fftfreq(n, 1 / rate)

    mask = freq > 0
    fft = fft[mask]
    freq = freq[mask]

    indices = np.argsort(np.abs(fft))[-512:]
    sines = []

    for i in sorted(indices, key=lambda x: freq[x]):
        amplitude = int(np.abs(fft[i]) / n * 1000)
        frequency = int(freq[i])
        phase = int(np.angle(fft[i]) * 100)
        sines.append((amplitude, frequency, phase))
    return sines

def encode_audio_bin(sines):
    buf = bytearray()
    for amp, freq, phase in sines:
        amp = max(0, min(65535, amp))
        freq = max(0, min(65535, freq))
        phase = max(-32768, min(32767, phase))
        buf += struct.pack(">HHh", amp, freq, phase)
    return base64.b64encode(buf).decode()

def decode_audio_bin(b64data):
    buf = base64.b64decode(b64data)
    sines = []
    for i in range(0, len(buf), 6):
        amp, freq, phase = struct.unpack(">HHh", buf[i:i+6])
        sines.append((amp, freq, phase))
    return sines

def generate_audio_from_sines(sines, output_path):
    duration = 3
    rate = 44100
    t = np.linspace(0, duration, int(rate * duration), False)
    signal = np.zeros_like(t)

    for amp, freq, phase in sines:
        signal += amp * np.sin(2 * np.pi * freq * t + (phase / 100))

    if np.max(np.abs(signal)) == 0:
        signal_out = np.zeros_like(signal, dtype=np.int16)
    else:
        signal_out = np.int16(signal / np.max(np.abs(signal)) * 32767)

    wavfile.write(output_path, rate, signal_out)

def num_to_word(num):
    # This function is no longer directly used for encoding, as we use CHINESE_DIGITS directly.
    # Keeping it for now, but it could be removed if not used elsewhere.
    return str(num) # Fallback, though it won't be called for Chinese encoding.

def encode_color_index(idx):
    """Encodes a color index (0-63) into a two-character Chinese token."""
    s_idx = f"{idx:02d}" # Convert to two-digit string (e.g., 5 -> "05", 12 -> "12")
    encoded_chars = [CHINESE_DIGITS[digit] for digit in s_idx]
    return "".join(encoded_chars)

def decode_color_token(token):
    """Decodes a two-character Chinese token back to a color index string (e.g., '01', '15')."""
    if len(token) == 2:
        digit1 = CHINESE_CHAR_TO_NUM.get(token[0])
        digit2 = CHINESE_CHAR_TO_NUM.get(token[1])
        if digit1 is not None and digit2 is not None:
            return digit1 + digit2
    return None

def tokenize_skibpic_data(data):
    """Removes noise and splits the data string into color tokens."""
    data = NOISE_RE.sub("", data)
    return TOKEN_RE.findall(data)

def image_to_skibpic(image_path, audio_path=None):
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)
    indices = quantize_image_to_palette(pixels, PALETTE_NP)
    h, w = indices.shape

    skib_data = ""
    for y in range(h):
        for x in range(w):
            idx = indices[y, x]
            if random.random() < 0.2:
                noise_num = random.randint(1, 9999)
                noise_str = str(noise_num)
                stars = "*" * len(noise_str)
                skib_data += f"{stars}{noise_str}{stars}"
            skib_data += encode_color_index(idx)
        skib_data += "\n"  # End of row marker

    if audio_path:
        sines = analyze_audio(audio_path)
        audio_bin = encode_audio_bin(sines)
        skib_data += "\n##AUDIOBIN##\n"
        skib_data += audio_bin

    key = generate_key_bytes()
    encrypted = xor_encrypt_bytes(skib_data.encode('utf-8'), key)

    out_path = os.path.splitext(image_path)[0] + ".skibpic"
    with open(out_path, "wb") as f:
        f.write(encrypted)
        f.write(b"\n##ENCRYPTION_KEY##\n")
        f.write(key)

    messagebox.showinfo("Done", f"Saved encrypted .skibpic to {out_path}")

def skibpic_to_image(skibpic_path):
    with open(skibpic_path, "rb") as f:
        raw = f.read()

    parts = raw.rsplit(b"##ENCRYPTION_KEY##", 1)
    if len(parts) != 2:
        messagebox.showerror("Error", "Encryption key missing in file!")
        return
    encrypted_data, key = parts[0].strip(), parts[1].strip()

    decrypted_bytes = xor_encrypt_bytes(encrypted_data, key)
    try:
        decrypted = decrypted_bytes.decode('utf-8')
    except UnicodeDecodeError:
        messagebox.showerror("Error", "Failed to decode decrypted content.")
        return

    if "##AUDIOBIN##" in decrypted:
        pixel_data, audio_bin = decrypted.split("##AUDIOBIN##", 1)
        audio_bin = audio_bin.strip()
    else:
        pixel_data = decrypted
        audio_bin = None

    rows = []
    pixel_data_rows = pixel_data.strip().split('\n')

    for row_str in pixel_data_rows:
        if not row_str:
            continue
        tokens = tokenize_skibpic_data(row_str)
        current_row = []
        for token in tokens:
            decoded_token = decode_color_token(token)
            if decoded_token is None:
                continue
            idx = int(decoded_token)
            color = INDEX_TO_COLOR.get(idx, (0, 0, 0))
            current_row.append(color)
        if current_row:
            rows.append(current_row)

    height = len(rows)
    width = max(len(r) for r in rows) if rows else 0

    if width == 0 or height == 0:
        messagebox.showinfo("Done", "Converted to an empty image.")
        return

    img = Image.new("RGB", (width, height))
    for y, row in enumerate(rows):
        row.extend([(0, 0, 0)] * (width - len(row)))  # Pad short rows
        for x, col in enumerate(row):
            img.putpixel((x, y), col)

    base_path, _ = os.path.splitext(skibpic_path)
    out_img_path = base_path + "_output.png"
    img.save(out_img_path)

    if audio_bin:
        sines = decode_audio_bin(audio_bin)
        out_audio_path = base_path + "_audio.wav"
        generate_audio_from_sines(sines, out_audio_path)
        messagebox.showinfo("Done", f"Converted to image and audio:\n{out_img_path}\n{out_audio_path}")
    else:
        messagebox.showinfo("Done", f"Converted to image:\n{out_img_path}")

def choose_file():
    path = filedialog.askopenfilename(filetypes=[
        ("Images", "*.png;*.jpg;*.jpeg;*.bmp"),
        ("WAV Audio", "*.wav"),
        ("Skibpic Files", "*.skibpic")
    ])
    if not path:
        return

    if path.endswith(".skibpic"):
        skibpic_to_image(path)
    else:
        audio = filedialog.askopenfilename(title="Optional: choose .wav audio to embed", filetypes=[("WAV Audio", "*.wav")])
        image_to_skibpic(path, audio if audio else None)

root = tk.Tk()
root.title("Skibpic Converter")
root.geometry("400x200")

label = tk.Label(root, text="Choose an image or skibpic file")
label.pack(pady=20)

btn = tk.Button(root, text="Select File", command=choose_file)
btn.pack()

root.mainloop()
