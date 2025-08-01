# Pentachlorobezene.exe
# Start development on 7/302025 4:39pm

import win32gui
import win32con
import ctypes
import time
from tkinter import messagebox
from threading import Thread
from winsound import *
from tempfile import *
import struct
import win32api
import random
import colorsys
import os

# TUNNEL

def tunnel_screen():
    hdc = win32gui.GetDC(0)
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [sw, sh] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    start_time = time.time()
    delay = 0.1
    size = 100
    while time.time() - start_time < 30:
        hdc = win32gui.GetDC(0)
        win32gui.StretchBlt(
            hdc,
            int(size / 2),
            int(size / 2),
            sw - size,
            sh - size,
            hdc,
            0,
            0,
            sw,
            sh,
            win32con.SRCCOPY,
        )
        time.sleep(delay)

# Restore/Erase the drawing function
def erase_screen():
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, None, 3)

def bytebeat_formula(t):
    # This formula can produce values outside 0-255.
    # We will use modulo 256 to keep it within the 8-bit unsigned range.
    # ORIGINAL: return 2*t^2*t+(t>>7)&t>>12|t>>4-(1^7&t>>19)|t>>7
    # FIX: 2*t^2*t was problematic due to operator precedence (resulted in 0).
    # Replaced with a common bytebeat pattern for illustration.
    # The (t % 256) is applied implicitly by Python's byte conversion if value
    # is out of range when appending to bytearray, but it's good practice for clarity.
    val = (2 * (t ^ (t >> 2))) + ((t >> 7) & (t >> 12)) | (t >> 4) - ((1 ^ 7) & (t >> 19)) | (t >> 7)
    return val & 255 # Ensure it stays within 0-255 range explicitly

def generate_and_play_bytebeat(duration_seconds=30, sample_rate=8000): # Removed unused 'amplitude'
    num_samples = duration_seconds * sample_rate
    raw_samples = bytearray()

    for t in range(num_samples):
        # Get the sample value from the bytebeat formula
        val = bytebeat_formula(t)
        # Append to raw samples. For 8-bit unsigned PCM, values are 0-255.
        raw_samples.append(val)

    # WAV header construction
    # RIFF header
    chunk_id = b'RIFF'
    chunk_size = 36 + len(raw_samples) # 36 bytes for header + data size
    format_tag = b'WAVE'

    # FMT sub-chunk
    subchunk1_id = b'fmt '
    subchunk1_size = 16 # For PCM
    audio_format = 1 # PCM = 1
    num_channels = 1 # Mono
    byte_rate = sample_rate * num_channels * 1 # Bytes per second (8-bit = 1 byte per sample)
    block_align = num_channels * 1 # Bytes per sample (8-bit = 1 byte)
    bits_per_sample = 8 # 8-bit audio

    # DATA sub-chunk
    subchunk2_id = b'data'
    subchunk2_size = len(raw_samples)

    wav_header = b''
    wav_header += chunk_id
    wav_header += struct.pack('<I', chunk_size)
    wav_header += format_tag
    wav_header += subchunk1_id
    wav_header += struct.pack('<I', subchunk1_size)
    wav_header += struct.pack('<H', audio_format)
    wav_header += struct.pack('<H', num_channels)
    wav_header += struct.pack('<I', sample_rate)
    wav_header += struct.pack('<I', byte_rate)
    wav_header += struct.pack('<H', block_align)
    wav_header += struct.pack('<H', bits_per_sample)
    wav_header += subchunk2_id
    wav_header += struct.pack('<I', subchunk2_size)

    full_wav_data = wav_header + raw_samples

    # Use NamedTemporaryFile to handle temporary file creation and cleanup
    temp_wav_file = None
    try:
        # delete=False means the file won't be deleted automatically when closed.
        # We'll explicitly delete it after playback.
        temp_wav_file = NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav_file.write(full_wav_data)
        temp_wav_file.close() # Close the file so winsound can access it

        # Play the sound asynchronously
        PlaySound(temp_wav_file.name, SND_FILENAME | SND_ASYNC)
        
        # Keep the thread alive for the duration of the sound to prevent file deletion
        # before playback finishes.
        time.sleep(duration_seconds + 1) # Add a small buffer

    except Exception as e:
        pass
    finally:
        if temp_wav_file and temp_wav_file.name:
            try:
                os.unlink(temp_wav_file.name) # Explicitly delete the temporary file
            except OSError as e:
                pass


def bytebeat2(t):
    return ((t // 2 * (4 | 7 & (t >> 13)) >> (~t >> 11 & 1) & 127)
            + (t * (t >> 11 & t >> 13) * (~t >> 9 & 3) & 127)) & 255

          
def rainbow_hell_stretch():
    duration_seconds = 30
    sample_rate = 8000
    num_samples = duration_seconds * sample_rate
    raw_samples = bytearray()

    # Generate audio samples
    for t in range(num_samples):
        raw_samples.append(bytebeat2(t))

    # Build WAV header
    chunk_id = b'RIFF'
    chunk_size = 36 + len(raw_samples)
    format_tag = b'WAVE'

    subchunk1_id = b'fmt '
    subchunk1_size = 16
    audio_format = 1
    num_channels = 1
    byte_rate = sample_rate
    block_align = 1
    bits_per_sample = 8

    subchunk2_id = b'data'
    subchunk2_size = len(raw_samples)

    wav_header = b''.join([
        chunk_id,
        struct.pack('<I', chunk_size),
        format_tag,
        subchunk1_id,
        struct.pack('<I', subchunk1_size),
        struct.pack('<H', audio_format),
        struct.pack('<H', num_channels),
        struct.pack('<I', sample_rate),
        struct.pack('<I', byte_rate),
        struct.pack('<H', block_align),
        struct.pack('<H', bits_per_sample),
        subchunk2_id,
        struct.pack('<I', subchunk2_size)
    ])

    full_wav_data = wav_header + raw_samples

    # Write to temp file
    temp_wav_file = NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav_file.write(full_wav_data)
    temp_wav_file.close()

    # Begin visual + audio playback
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [sw, sh] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    color = 0.0
    start_time = time.time()

    PlaySound(temp_wav_file.name, SND_FILENAME | SND_ASYNC)

    while time.time() - start_time < duration_seconds:
        hdc = win32gui.GetDC(0)

        # Rainbow Hell visuals
        rgb_color = colorsys.hsv_to_rgb(color % 1.0, 1.0, 1.0)
        brush = win32gui.CreateSolidBrush(
            win32api.RGB(
                int(rgb_color[0] * 255),
                int(rgb_color[1] * 255),
                int(rgb_color[2] * 255)
            )
        )
        win32gui.SelectObject(hdc, brush)
        win32gui.BitBlt(
            hdc,
            random.randint(-10, 10),
            random.randint(-10, 10),
            sw,
            sh,
            hdc,
            0,
            0,
            win32con.SRCCOPY
        )
        win32gui.BitBlt(
            hdc,
            random.randint(-10, 10),
            random.randint(-10, 10),
            sw,
            sh,
            hdc,
            0,
            0,
            win32con.PATINVERT
        )

        # Stretch effect
        win32gui.StretchBlt(
            hdc,
            0,
            -20,
            sw,
            sh + 40,
            hdc,
            0,
            0,
            sw,
            sh,
            win32con.SRCCOPY
        )

        win32gui.ReleaseDC(0, hdc)
        color += 0.05
        time.sleep(0.01)

    PlaySound(None, SND_PURGE)  # Stop playback
    try:
        os.unlink(temp_wav_file.name)  # Clean up
    except OSError:
        pass





def bytebeat3(t):
    return (
        ((t >> 10 ^ t >> 11) % 5)
        * ((t >> 14 & 3 ^ t >> 15 & 1) + 1)
        * t % 99
        + (int(((3 + (t >> 14 & 3) - (t >> 16 & 1)) / 3 * t % 99)) & 64)
    ) & 255



def scribble_void():
    """
    Combined Rotate Tunnel + Void visuals with synchronized custom bytebeat audio.
    Runs for 30 seconds at 8000 Hz. No threading.
    """
    duration_seconds = 30
    sample_rate = 8000
    num_samples = duration_seconds * sample_rate
    raw_samples = bytearray()

    for t in range(num_samples):
        raw_samples.append(bytebeat3(t))

    # Build WAV header
    chunk_id = b'RIFF'
    chunk_size = 36 + len(raw_samples)
    format_tag = b'WAVE'

    subchunk1_id = b'fmt '
    subchunk1_size = 16
    audio_format = 1
    num_channels = 1
    byte_rate = sample_rate
    block_align = 1
    bits_per_sample = 8

    subchunk2_id = b'data'
    subchunk2_size = len(raw_samples)

    wav_header = b''.join([
        chunk_id,
        struct.pack('<I', chunk_size),
        format_tag,
        subchunk1_id,
        struct.pack('<I', subchunk1_size),
        struct.pack('<H', audio_format),
        struct.pack('<H', num_channels),
        struct.pack('<I', sample_rate),
        struct.pack('<I', byte_rate),
        struct.pack('<H', block_align),
        struct.pack('<H', bits_per_sample),
        subchunk2_id,
        struct.pack('<I', subchunk2_size)
    ])

    full_wav_data = wav_header + raw_samples

    temp_wav_file = NamedTemporaryFile(suffix=".wav", delete=False)
    temp_wav_file.write(full_wav_data)
    temp_wav_file.close()

    # Visual setup
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    color = 0.0
    start_time = time.time()

    PlaySound(temp_wav_file.name, SND_FILENAME | SND_ASYNC)

    while time.time() - start_time < duration_seconds:
        hdc = win32gui.GetDC(0)

        # --- Rotate Tunnel (Bezier Rainbow Lines) ---
        color = (color + 0.02) % 1.0
        rgb = colorsys.hsv_to_rgb(color, 1.0, 1.0)
        bezier_points = [(random.randint(0, w), random.randint(0, h)) for _ in range(4)]
        hPen = win32gui.CreatePen(
            win32con.PS_SOLID,
            5,
            win32api.RGB(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        )
        win32gui.SelectObject(hdc, hPen)
        win32gui.PolyBezier(hdc, bezier_points)
        win32gui.DeleteObject(hPen)

        # --- Void distortion (bit-level glitch) ---
        win32gui.BitBlt(
            hdc,
            random.randint(1, 10) % 2,
            random.randint(1, 10) % 2,
            w,
            h,
            hdc,
            random.randint(1, 1000) % 2,
            random.randint(1, 1000) % 2,
            win32con.SRCAND
        )

        win32gui.ReleaseDC(0, hdc)
        time.sleep(0.01)

    PlaySound(None, SND_PURGE)
    try:
        os.unlink(temp_wav_file.name)
    except OSError:
        pass


def rotate_tunnel_with_triangles(duration_seconds=30):
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    
    hdc = win32gui.GetDC(0)
    color = 0.0
    start_time = time.time()

    def draw_gradient_triangle(hdc):
        # Draw several random colored gradient triangles
        for _ in range(25):
            # Get desktop rect (l,t,r,b)
            l, t, r, b = win32gui.GetClientRect(win32gui.GetDesktopWindow())
            vertices = (
                {
                    "x": int(random.random() * r),
                    "y": int(random.random() * b),
                    "Red": int(random.random() * 0xFF00),
                    "Green": 0,
                    "Blue": 0,
                    "Alpha": 0,
                },
                {
                    "x": int(random.random() * r),
                    "y": int(random.random() * b),
                    "Red": 0,
                    "Green": int(random.random() * 0xFF00),
                    "Blue": 0,
                    "Alpha": 0,
                },
                {
                    "x": int(random.random() * r),
                    "y": int(random.random() * b),
                    "Red": 0,
                    "Green": 0,
                    "Blue": int(random.random() * 0xFF00),
                    "Alpha": 0,
                },
            )
            mesh = ((0, 1, 2),)
            try:
                win32gui.GradientFill(hdc, vertices, mesh, win32con.GRADIENT_FILL_TRIANGLE)
            except Exception:
                # Sometimes GradientFill can fail on certain windows - ignore errors
                pass

    try:
        while time.time() - start_time < duration_seconds:
            # Increment and wrap the hue value for rotating color
            color = (color + 0.02) % 1.0

            # Calculate a bright RGB color from HSV
            rgb_color = colorsys.hsv_to_rgb(color, 1.0, 1.0)

            # Create a random polybezier shape with 4 points
            points = [(random.randint(0, w), random.randint(0, h)) for _ in range(4)]

            # Create a pen with the rotating color, width 5
            pen = win32gui.CreatePen(
                win32con.PS_SOLID,
                5,
                win32api.RGB(
                    int(rgb_color[0] * 255),
                    int(rgb_color[1] * 255),
                    int(rgb_color[2] * 255),
                ),
            )
            win32gui.SelectObject(hdc, pen)

            # Draw the polybezier curve
            win32gui.PolyBezier(hdc, points)

            # Cleanup pen object
            win32gui.DeleteObject(pen)

            # Draw random colored gradient triangles over the screen
            draw_gradient_triangle(hdc)

            # Small sleep for smooth effect
            time.sleep(0.01)
    finally:
        # Release device context on exit
        win32gui.ReleaseDC(0, hdc)

def bytebeat4(t):
    cond = (t >> 18) & 1
    part1 = t >> (13 if cond else 12)
    part1 &= 3 if cond else 0
    part2 = t >> (14 if cond else 13)
    part3_cond = (- (t >> (15 if cond else 14)) & 3)
    part3 = 1 if part3_cond else 2
    inner_xor = (part1 ^ part2) + 3 & 3
    val = (
        t * (6 + (inner_xor) / 8 % 128)
        + (t * (6 + ((t >> 16) & 3)) / 16 | (t >> 7) ^ (t >> 9)) % 128
    )
    # val can be float, convert to int and mod 256 for 8-bit audio
    return int(val) & 255

def generate_and_play_bytebeat_custom(duration_seconds=30, sample_rate=32000):
    num_samples = duration_seconds * sample_rate
    raw_samples = bytearray()

    for t in range(num_samples):
        val = bytebeat_formula_custom(t)
        raw_samples.append(val)

    # WAV header as before, just updating sample_rate
    chunk_id = b'RIFF'
    chunk_size = 36 + len(raw_samples)
    format_tag = b'WAVE'

    subchunk1_id = b'fmt '
    subchunk1_size = 16
    audio_format = 1
    num_channels = 1
    byte_rate = sample_rate * num_channels * 1
    block_align = num_channels * 1
    bits_per_sample = 8

    subchunk2_id = b'data'
    subchunk2_size = len(raw_samples)

    wav_header = b''.join([
        chunk_id,
        struct.pack('<I', chunk_size),
        format_tag,
        subchunk1_id,
        struct.pack('<I', subchunk1_size),
        struct.pack('<H', audio_format),
        struct.pack('<H', num_channels),
        struct.pack('<I', sample_rate),
        struct.pack('<I', byte_rate),
        struct.pack('<H', block_align),
        struct.pack('<H', bits_per_sample),
        subchunk2_id,
        struct.pack('<I', subchunk2_size)
    ])

    full_wav_data = wav_header + raw_samples

    temp_wav_file = None
    try:
        temp_wav_file = NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav_file.write(full_wav_data)
        temp_wav_file.close()

        PlaySound(temp_wav_file.name, SND_FILENAME | SND_ASYNC)
        time.sleep(duration_seconds + 1)

    except Exception:
        pass
    finally:
        if temp_wav_file and temp_wav_file.name:
            try:
                os.unlink(temp_wav_file.name)
            except OSError:
                pass

      
if __name__ == "__main__":
    ans1 = messagebox.askyesno("Pentachlorobezene.exe", "Run Harmless Malware?")
    if ans1:
        ans2 = messagebox.askyesno("Pentachlorobezene.exe", "Are you sure? It would not write the boot sector but this application will make loud noise.")
        if ans2:
            ans3 = messagebox.askyesno("Pentachlorobezene", "LAST WARNING!\nDO YOU WANT TO EXECUTE THIS APPLICATION? \nPRESS NO IF YOU HAVE EPILEPSY/PHOTOSENSITIVE.")
            if ans3:
                time.sleep(3)

                # First payload is tunnel like screen effect
                thread1 = Thread(target=tunnel_screen)
                thread1.start()
                generate_and_play_bytebeat()
                erase_screen()
                time.sleep(2)

                # Second payload, Rainbowhell/Rainbow Blink + stretch !
                rainbow_hell_stretch()
                erase_screen()
                time.sleep(2)

                # Third payload, Scribble Effect + void :D!
                scribble_void()
                erase_screen()
                time.sleep(2)

                # Fourth payload, Rotate tunnel + Triangle
                thread2 = Thread(target=generate_and_play_bytebeat_custom)
                thread2.start()
                rotate_tunnel_with_triangles(30)
    else:
        messagebox.showinfo("Pentachlorobezene.exe", "Ok I will quit. (Press ok to disappear this message)")
