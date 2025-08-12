import numpy as np
from scipy import signal
from pydub import AudioSegment
import random

# ------------------------------
# PARAMETERS
# ------------------------------
song_length_seconds = 60    # Length in seconds
bpm = 60                    # Beats per minute
key = "C"                   # Musical key (C, D, E, etc.)
scale_type = "major"        # major or minor
sample_rate = 44100         # Audio sample rate
bitcrush_bits = 8           # Bit depth for bitcrush

# ------------------------------
# NOTE FREQUENCIES
# ------------------------------
NOTE_FREQS = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
    'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
    'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
}

# ------------------------------
# SCALE GENERATION
# ------------------------------
def generate_scale(root, scale_type):
    major_intervals = [0, 2, 4, 5, 7, 9, 11]
    minor_intervals = [0, 2, 3, 5, 7, 8, 10]
    intervals = major_intervals if scale_type == "major" else minor_intervals
    notes = list(NOTE_FREQS.keys())
    root_index = notes.index(root)
    return [notes[(root_index + i) % 12] for i in intervals]

scale_notes = generate_scale(key, scale_type)

# ------------------------------
# GUITAR-LIKE NOTE GENERATOR
# ------------------------------
def generate_guitar_note(note, duration, sr=44100):
    freq = NOTE_FREQS[note]
    t = np.linspace(0, duration, int(sr * duration), False)
    
    # Triangle wave for plucked tone
    wave = signal.sawtooth(2 * np.pi * freq * t, width=0.5)
    
    # Low-pass filter for warmth
    b, a = signal.butter(4, 2000 / (sr / 2), btype='low')
    wave = signal.lfilter(b, a, wave)
    
    # Slow attack + decay for ambient
    envelope = np.exp(-t * 3) * np.clip(t * 5, 0, 1)
    wave *= envelope
    
    # Bitcrush
    wave = np.round(wave * (2**(bitcrush_bits-1))) / (2**(bitcrush_bits-1))
    
    return wave

# ------------------------------
# SONG GENERATION
# ------------------------------
beats_per_second = bpm / 60
total_beats = int(song_length_seconds * beats_per_second)

song = np.array([], dtype=np.float32)

for _ in range(total_beats):
    note = random.choice(scale_notes)
    duration = 60 / bpm  # 1 beat
    note_wave = generate_guitar_note(note, duration)
    
    # Add some silence between notes for space
    silence = np.zeros(int(sample_rate * 0.05))
    song = np.concatenate((song, note_wave, silence))

# Normalize
song /= np.max(np.abs(song))

# ------------------------------
# EXPORT AS WAV
# ------------------------------
song_int16 = np.int16(song * 32767)
AudioSegment(
    song_int16.tobytes(),
    frame_rate=sample_rate,
    sample_width=2,
    channels=1
).export("ambient_bitcrushed_guitar.wav", format="wav")

print("generated: ambient_bitcrushed_guitar.wav")
