import pyaudio
import wave
import argparse
import configparser
import keyboard
import os
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Argument parser
parser = argparse.ArgumentParser(description='Robust Sound Recorder')
parser.add_argument('-c', '--config', help='Path to configuration file')
parser.add_argument('-f', '--filename', help='Output filename (without .wav extension)')
parser.add_argument('-o', '--output-dir', default='.', help='Directory to save the recording')
parser.add_argument('--duration', type=int, help='Maximum recording duration in seconds (optional)')
args = parser.parse_args()

# Load config
config = configparser.ConfigParser()
default_config = {
    'format': '16bit',
    'channels': '2',
    'rate': '44100'
}

if args.config and os.path.isfile(args.config):
    config.read(args.config)
    if 'RECORDING' not in config:
        config['RECORDING'] = default_config
else:
    config['RECORDING'] = default_config

# Validate format
format_map = {
    '16bit': pyaudio.paInt16,
    '24bit': pyaudio.paInt24,
    '32bit': pyaudio.paInt32
}
fmt_str = config['RECORDING'].get('format', '16bit').lower()
if fmt_str not in format_map:
    logging.warning(f"Invalid format '{fmt_str}'. Defaulting to 16bit.")
    fmt_str = '16bit'
FORMAT = format_map[fmt_str]

# Validate channels and rate
try:
    CHANNELS = int(config['RECORDING'].get('channels', 2))
    RATE = int(config['RECORDING'].get('rate', 44100))
except ValueError:
    logging.warning("Invalid channels or rate in config. Using defaults.")
    CHANNELS = 2
    RATE = 44100

# Prepare output filename
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

if args.filename:
    base_name = args.filename.strip()
else:
    base_name = input("Enter a file name for your recording (without extension): ").strip()

def get_unique_filename(name, directory):
    full_path = os.path.join(directory, name + '.wav')
    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(directory, f"{name}_{counter}.wav")
        counter += 1
    return full_path

WAVE_OUTPUT_FILENAME = get_unique_filename(base_name, args.output_dir)

# Initialize PyAudio
audio = pyaudio.PyAudio()
try:
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=1024)
except Exception as e:
    logging.error(f"Failed to open audio stream: {e}")
    audio.terminate()
    exit(1)

# Open output WAV file
wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)

print("Recording... Press 'Esc' or use --duration to stop.")
start_time = time.time()

try:
    while True:
        if keyboard.is_pressed('esc'):
            print("Stopping recording...")
            break
        if args.duration and (time.time() - start_time) > args.duration:
            print("Duration limit reached.")
            break
        data = stream.read(1024, exception_on_overflow=False)
        wave_file.writeframes(data)
except KeyboardInterrupt:
    print("Recording interrupted by user.")
except Exception as e:
    logging.error(f"Recording error: {e}")

# Cleanup
stream.stop_stream()
stream.close()
audio.terminate()
wave_file.close()

duration_secs = time.time() - start_time
print(f"Recording complete. Saved to '{WAVE_OUTPUT_FILENAME}'")
print(f"Duration: {duration_secs:.2f} seconds ({duration_secs / 60:.2f} minutes)")
