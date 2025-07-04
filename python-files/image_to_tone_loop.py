#!/usr/bin/env python3
PK     v��Z�c�@       image_to_tone_loop.pyfrom __future__ import annotations

import argparse
import io
import wave
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

SAMPLE_RATE = 44_100
NOTE_LENGTH = 0.12
AMPLITUDE = 0.25
START_MIDI = 48
END_MIDI = 84

def note_from_luma(luma: float) -> int:
    return int(round(START_MIDI + luma * (END_MIDI - START_MIDI)))

def midi_to_freq(midi_note: int) -> float:
    return 440.0 * 2 ** ((midi_note - 69) / 12)

def sine_wave(freq: float, length: float, sample_rate: int) -> np.ndarray:
    import numpy as np
    t = np.linspace(0, length, int(sample_rate * length), endpoint=False)
    return np.sin(2 * np.pi * freq * t)

def image_to_notes(img: Image.Image) -> list[int]:
    import numpy as np
    luminance = np.asarray(img.convert("L"), dtype=np.uint8).flatten() / 255.0
    return [note_from_luma(v) for v in luminance]

def render_notes(notes: Sequence[int], fname: Path, note_len: float):
    import numpy as np, wave
    if not notes:
        raise ValueError("No notes to render – is the image empty?")
    samples_per_note = int(note_len * SAMPLE_RATE)
    audio = np.zeros(samples_per_note * len(notes), dtype=np.float32)
    for i, n in enumerate(notes):
        audio[i * samples_per_note:(i + 1) * samples_per_note] = sine_wave(
            midi_to_freq(n), note_len, SAMPLE_RATE
        )
    peak = np.max(np.abs(audio)) or 1.0
    audio = (audio / peak) * AMPLITUDE
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(str(fname), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_int16.tobytes())
    print(f"WAV written → {fname}")

def parse_args(argv: Optional[Iterable[str]] = None) -> Optional[Tuple[Path, Path, float, bool]]:
    p = argparse.ArgumentParser(description="Convert an image to a looping sine‑tone melody.")
    p.add_argument("-i", "--image", metavar="IMG", help="Input image (png/jpg/etc.)")
    p.add_argument("-o", "--out", metavar="WAV", help="Output WAV file")
    p.add_argument("-l", "--length", type=float, default=NOTE_LENGTH, metavar="SEC",
                   help="Seconds per note (default: %(default)s)")
    p.add_argument("--preview", action="store_true",
                   help="Play the first bar (requires simpleaudio)")
    args = p.parse_args(list(argv) if argv is not None else None)
    if not args.image:
        p.print_help()
        return None
    in_path = Path(args.image)
    if not in_path.is_file():
        print(f"File not found: {in_path}")
        return None
    out_path = Path(args.out) if args.out else in_path.with_stem(in_path.stem + "_loop").with_suffix(".wav")
    return in_path, out_path, args.length, args.preview

def main(argv: Optional[Iterable[str]] = None):
    config = parse_args(argv)
    if config is None:
        return
    img_path, wav_path, note_len, preview = config
    img = Image.open(img_path)
    notes = image_to_notes(img)
    render_notes(notes, wav_path, note_len)
    if preview:
        try:
            import simpleaudio as sa
            sa.WaveObject.from_wave_file(str(wav_path)).play()
        except ImportError:
            print("simpleaudio not installed; skipping preview")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
PK     v��Z�JXPB   B      __main__.pyfrom image_to_tone_loop import main
import sys
main(sys.argv[1:])
PK     v��Z�c�@               ��   image_to_tone_loop.pyPK     v��Z�JXPB   B              ��[  __main__.pyPK      |   �    