"""
===============================================================================
Advanced Voice Changer with Recording
===============================================================================
Description:
    This is an advanced desktop application for recording voice and applying
    voice effects including pitch shifting, tempo alteration, and reverb. The 
    app also provides functionality to overlay processed base audio (selected 
    by the user) onto the recorded voice for unique voice-changing effects.
    
Features:
    - Select a base audio file (WAV or MP3) that serves as an overlay effect.
    - Start and manually stop live voice recording using the microphone.
    - Playback the original, unmodified recording.
    - Apply voice effects (pitch shift, speed alteration, reverb) to the recording.
    - Overlay processed base audio on the recording if available.
    - Playback the modified recording.
    - Exit the application via a simple GUI.
    
Libraries Used:
    - Tkinter: For GUI creation and interactive dialogs.
    - Pydub: For audio processing and playback.
    - Sounddevice: For real-time audio recording.
    - Wave: For saving recorded audio into WAV format.
    - NumPy and SciPy: For numerical operations and audio resampling.
    - Pygame: For enhanced audio playback functionality.
    
Usage:
    Run the script to launch the GUI. Follow the interface steps:
        1. (Optional) Select a Base Audio file.
        2. Click "Start Recording" to begin recording your voice.
        3. Click "Stop Recording" to end the recording and save the file.
        4. Click "Play Original Recording" to hear your raw recording.
        5. Click "Apply Voice Effects & Play Modified" to process and listen 
           to your voice with effects.
        6. Click "Exit" to close the application.
    
Author: Ahmad Abid
Date: 2025-06-05
Version: 1.5
===============================================================================
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import sounddevice as sd
import wave

from scipy.signal import resample
from pydub import AudioSegment
from pydub.playback import play
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Global variables
base_audio = None              # The selected base audio file (for additional effects)
file_path = None               # The file path of the selected base audio
recording_file = "user_recording.wav"  # File where the user's recording will be saved
recording_stream = None        # The sounddevice.InputStream instance
audio_frames = []              # List to store recorded audio chunks

# Create the main window
root = tk.Tk()
root.title("Advanced Voice Changer with Recording")
root.geometry("500x600")

# Status label to show realtime updates
status_label = tk.Label(root, text="Welcome to the Voice Changer!", wraplength=480)
status_label.pack(pady=10)

# Label to show base audio details
audio_info_label = tk.Label(root, text="No audio file selected.", wraplength=480)
audio_info_label.pack(pady=10)


def select_file():
    """
    Open a file dialog for selecting a base audio file (WAV or MP3).
    The selected file is loaded for processing to be later overlaid on the recording.
    """
    global base_audio, file_path
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")]
    )
    if file_path:
        try:
            base_audio = AudioSegment.from_file(file_path)
            info = (f"Selected file: {os.path.basename(file_path)}\n"
                    f"Sample Rate: {base_audio.frame_rate} Hz\n"
                    f"Channels: {base_audio.channels}")
            audio_info_label.config(text=info)
            status_label.config(text="Audio file loaded successfully!", fg="black")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load audio file:\n{e}")
    else:
        status_label.config(text="No file selected.", fg="red")


def start_recording():
    """
    Start recording audio using sounddevice.InputStream.
    Records are stored into a global list (audio_frames) until the user stops the recording.
    """
    global recording_stream, audio_frames
    audio_frames = []  # Reset frames for a new recording

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        # Append a copy of the current block of data
        audio_frames.append(indata.copy())

    try:
        recording_stream = sd.InputStream(samplerate=44100, channels=1, dtype="int16", callback=callback)
        recording_stream.start()
        status_label.config(text="Recording... Press 'Stop Recording' to finish", fg="blue")
    except Exception as e:
        messagebox.showerror("Error", f"Recording failed:\n{e}")


def stop_recording():
    """
    Stop the live recording, concatenate recorded frames, and write the audio data to disk.
    """
    global recording_stream, audio_frames
    if recording_stream is None:
        messagebox.showerror("Error", "Recording has not been started.")
        return

    try:
        recording_stream.stop()
        recording_stream.close()
        recording_stream = None

        # Combine recorded frames to make a full array
        audio_data = np.concatenate(audio_frames, axis=0)
        sample_rate = 44100

        # Save the recorded data to a WAV file
        with wave.open(recording_file, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio (2 bytes per sample)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

        status_label.config(text="Recording complete!", fg="green")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving recording:\n{e}")


def play_original_recording():
    """
    Plays back the original (raw) recorded audio.
    """
    if not os.path.exists(recording_file):
        messagebox.showerror("Error", "No recording found! Please record your voice first.")
        return

    status_label.config(text="Playing original recording...", fg="blue")
    try:
        recorded_audio = AudioSegment.from_file(recording_file, format="wav")
        play(recorded_audio)
        status_label.config(text="Original recording playback complete.", fg="green")
    except Exception as e:
        messagebox.showerror("Error", f"Playback error:\n{e}")


def change_pitch(audio, semitones):
    """
    Change the pitch of the audio by a number of semitones.
    Resamples the audio and adjusts its frame rate.
    """
    factor = 2 ** (semitones / 12)
    samples = np.array(audio.get_array_of_samples())
    resampled = resample(samples, int(len(samples) / factor))
    return audio._spawn(resampled.astype(np.int16).tobytes()).set_frame_rate(int(audio.frame_rate * factor))


def change_speed(audio, speed_factor):
    """
    Change the speed (tempo) of the audio by adjusting the frame_rate.
    """
    return audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed_factor)}).set_frame_rate(audio.frame_rate)


def add_reverb(audio):
    """
    Add a simple reverb effect by overlaying the audio with a slightly attenuated version.
    """
    return audio.overlay(audio - 10, gain_during_overlay=-10)


def apply_voice_effects():
    """
    Applies voice-changing effects on the user's recording.
    If a base audio file is selected, its processed version (pitch, speed, reverb adjusted)
    is overlaid on top of the recording.
    Otherwise, the effects are applied directly to the recording.
    The result is saved and played back.
    """
    if not os.path.exists(recording_file):
        messagebox.showerror("Error", "No recording found! Please record your voice first.")
        return

    status_label.config(text="Applying effects to your voice...", fg="blue")
    try:
        recorded_audio = AudioSegment.from_file(recording_file, format="wav")
        if base_audio is not None:
            # Process the base audio to create an effect
            modified_base = change_pitch(base_audio, 5)     # Increase pitch by 5 semitones
            modified_base = change_speed(modified_base, 1.2)  # Speed up by 20%
            modified_base = add_reverb(modified_base)         # Add reverb effect
            modified_base = modified_base - 5  # Lower volume for better blending
            # Overlay the processed base audio on top of the recorded audio
            combined = recorded_audio.overlay(modified_base)
        else:
            # Apply effects directly to the recorded audio
            combined = change_pitch(recorded_audio, 5)
            combined = change_speed(combined, 1.2)
            combined = add_reverb(combined)

        output_file = "modified_voice.wav"
        combined.export(output_file, format="wav")
        status_label.config(text="Effects applied! Playing modified voice...", fg="green")
        threading.Thread(target=play_audio, args=(output_file,), daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", f"Error during processing:\n{e}")


def play_audio(file_to_play):
    """
    Play the specified audio file using pydub, in a separate thread.
    """
    try:
        playback_audio = AudioSegment.from_file(file_to_play, format="wav")
        play(playback_audio)
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Playback error:\n{e}"))


def exit_app():
    """Exit the application."""
    root.quit()


# -------------------------------
# Create the buttons and pack them into the window
# -------------------------------
select_button = tk.Button(root, text="Select Base Audio (for effects)", command=select_file, width=30)
select_button.pack(pady=5)

start_record_button = tk.Button(root, text="Start Recording", command=start_recording, width=30)
start_record_button.pack(pady=5)

stop_record_button = tk.Button(root, text="Stop Recording", command=stop_recording, width=30)
stop_record_button.pack(pady=5)

play_original_button = tk.Button(root, text="Play Original Recording", command=play_original_recording, width=30)
play_original_button.pack(pady=5)

apply_effects_button = tk.Button(root, text="Apply Voice Effects & Play Modified", command=apply_voice_effects, width=30)
apply_effects_button.pack(pady=5)

exit_button = tk.Button(root, text="Exit", command=exit_app, width=30)
exit_button.pack(pady=20)

# -------------------------------
# Start the GUI event loop
# -------------------------------
root.mainloop()