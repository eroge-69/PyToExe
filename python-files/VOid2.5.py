import soundfile as sf
import numpy as np
from scipy.signal import resample
import os

def pitch_shift_void2style(input_path, output_path, semitones):
    """
    Pitch-shifts a WAV file like VOid2.5:
    - semitones > 0 = chipmunk effect
    - semitones < 0 = demon effect
    """
    data, sr = sf.read(input_path)
    
    # Calculate pitch ratio
    pitch_ratio = 2 ** (semitones / 12)
    
    # Resample to shift pitch
    new_length = int(len(data) / pitch_ratio)
    shifted = resample(data, new_length)
    
    sf.write(output_path, shifted, sr)
    print(f"Processed {input_path} → {output_path}")

def batch_process(folder_path, semitones):
    for file in os.listdir(folder_path):
        if file.lower().endswith(".wav"):
            input_path = os.path.join(folder_path, file)
            output_file = f"shifted_{file}"
            output_path = os.path.join(folder_path, output_file)
            pitch_shift_void2style(input_path, output_path, semitones)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VOid2.5-style pitch shifter (chipmunk/demon)")
    parser.add_argument("input", help="Path to input WAV file or folder")
    parser.add_argument("semitones", type=float, help="Number of semitones to shift (+ high, - low)")
    parser.add_argument("--batch", action="store_true", help="Process a whole folder")
    args = parser.parse_args()

    if args.batch:
        batch_process(args.input, args.semitones)
    else:
        output_file = "shifted_" + os.path.basename(args.input)
        pitch_shift_void2style(args.input, output_file, args.semitones)
