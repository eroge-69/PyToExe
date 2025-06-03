import pyaudio
import wave
import argparse
import configparser
import keyboard
import os

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Sound Recorder')
parser.add_argument('-c', '--config', help='Path to configuration file')
args = parser.parse_args()

# Load configuration file
config = configparser.ConfigParser()
if args.config:
    config.read(args.config)
else:
    config['RECORDING'] = {
        'format': '16bit',
        'channels': '2',
        'rate': '44100'
    }

# Set parameters
FORMAT = pyaudio.paInt16 if config['RECORDING']['format'] == '16bit' else pyaudio.paInt32
CHANNELS = int(config['RECORDING']['channels'])
RATE = int(config['RECORDING']['rate'])

# Get file name from user
while True:
    WAVE_OUTPUT_FILENAME = input("Enter a file name for your recording (without extension): ")
    if not WAVE_OUTPUT_FILENAME.endswith('.wav'):
        WAVE_OUTPUT_FILENAME += '.wav'
    if os.path.exists(WAVE_OUTPUT_FILENAME):
        print("A file with this name already exists. Please choose a different name.")
    else:
        break

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=1024)

print("Press 'esc' to stop recording...")
frames = []

try:
    while True:
        if keyboard.is_pressed('esc'):
            print("Stopping recording...")
            break
        data = stream.read(1024)
        frames.append(data)
except Exception as e:
    print(f"Error: {e}")

# Close and terminate everything
stream.stop_stream()
stream.close()
audio.terminate()

# Save to file
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

print(f"Recording saved to {WAVE_OUTPUT_FILENAME}")
