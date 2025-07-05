import os
import random
import tkinter as tk
from tkinter import ttk
from transformers import pipeline
import torch
from tkinter import messagebox, scrolledtext
import os
import traceback
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import praw
import soundfile as sf
import platform
from glob import glob
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import random
from multiprocessing import Process
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
import re
import time
from typing import List, Dict, Tuple, Optional
import json
import threading
from pydub import AudioSegment
from pydub.playback import play
import subprocess
import sys
import string  # Moved to top
import praw
import os
import os
import sys
import tempfile

# Dynamically find the path to praw.ini
config_path = os.path.join(os.path.dirname(__file__), "praw.ini")

# Load the 'bot' section from praw.ini using custom path
reddit = praw.Reddit(client_id="EDiwAN4bbujuFOCB3U6izw",
client_secret="hLwlViTKBIo3Mu9IWioM_utcCc9qVA",
password="COol24@@",
user_agent="testscript by u/fakebot3",
username="Immediate_Flight2215",
config_interpolation="basic", config_path=config_path)
# ✅ 1. Set critical environment variables FIRST
os.environ["IMAGEMAGICK_BINARY"] = "magick.exe"

# ✅ 2. Ensure sys.stderr exists before kokoro import
if sys.stderr is None:
    # Create a fallback stderr stream
    stderr_path = os.path.join(tempfile.gettempdir(), "kokoro_stderr.log")
    sys.stderr = open(stderr_path, "w", encoding="utf-8")
    print(f"Created fallback stderr at: {stderr_path}", file=sys.stderr)

# ✅ 3. Now set KOKORO_LOG_PATH with robust handling
if getattr(sys, 'frozen', False):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(sys.executable)

    log_path = os.path.join(base_path, "kokoro.log")

    # Fallback to temp directory if needed
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a"):
            pass  # Test file creation
    except Exception:
        log_path = os.path.join(tempfile.gettempdir(), "kokoro.log")
else:
    log_path = os.path.abspath("kokoro.log")

os.environ["KOKORO_LOG_PATH"] = log_path
print(f"KOKORO_LOG_PATH set to: {log_path}", file=sys.stderr)

# ✅ 4. Import kokoro AFTER ensuring stderr exists
try:
    if getattr(sys, 'frozen', False):
        # In frozen executable
        from kokoro.pipeline import KPipeline
    else:
        # In development
        from kokoro import KPipeline
except Exception as e:
    print(f"Kokoro import failed: {e}", file=sys.stderr)


# 🔊 Voice mapping
voices = {
    "af_heart": 1, "af_alloy": 2, "af_aoede": 3, "af_bella": 4, "af_jessica": 5,
    "af_kore": 6, "af_santa": 7, "af_nova": 8, "af_river": 9, "af_sarah": 10,
    "af_sky": 11, "am_adam": 12, "am_echo": 13, "am_eric": 14, "am_fenrir": 15,
    "am_liam": 16, "am_michael": 17, "am_onyx": 18, "am_puck": 19
}
voice_by_number = {v: k for k, v in voices.items()}

try:
    pipeline = KPipeline(lang_code='a')
except Exception as e:
    print(f"Warning: Could not initialize Kokoro pipeline: {e}")
    pipeline = None


# Fixed timing parameters
WORD_DURATION = 0.2  # Each word displayed for 0.2 seconds
WORDS_PER_SUBTITLE = 10  # Show 7 words at a time
WORDS_PER_SECOND = 2.6  # adjust this per your voice


def _create_word_aligned_subtitle_chunks(word_timings, chunk_size=3, overlap=0):
    EoS_PUNCT = {".", "!", "?"}
    PUNCTUATION = set(string.punctuation)
    chunks = []

    sentence = []
    sentences = []

    # Step 1: Split word timings into sentences
    for word, start, end in word_timings:
        sentence.append((word, start, end))
        if word in EoS_PUNCT:
            sentences.append(sentence)
            sentence = []
    if sentence:
        sentences.append(sentence)

    # Step 2: Chunk each sentence
    for sentence in sentences:
        j = 0
        while j < len(sentence):
            chunk = []

            # Build a chunk while skipping punctuation
            while len(chunk) < chunk_size and j < len(sentence):
                word, start, end = sentence[j]
                if word not in PUNCTUATION:
                    # Clean word from punctuation characters
                    cleaned_word = ''.join(char for char in word if char not in PUNCTUATION)
                    if cleaned_word:  # Only add if not empty after cleaning
                        chunk.append((cleaned_word, start, end))
                j += 1

            if not chunk:
                continue

            start_time = chunk[0][1]
            end_time = chunk[-1][2]
            text = " ".join(word for word, _, _ in chunk)
            chunks.append((start_time, end_time, text))

            # Handle overlap if needed
            j -= max(0, overlap)

    return chunks


class SubtitleTracker:
    def __init__(self, root):
        self.root = root
        self.current_subtitle = tk.StringVar()
        self.current_subtitle.set("Subtitle will appear here")
        self.is_playing = False
        self.playback_thread = None
        self.audio_process = None
        self.subtitle_chunks = []

    def update_subtitle(self, text):
        """Thread-safe subtitle update"""
        if self.root.winfo_exists():
            self.current_subtitle.set(text)

    def play_audio_with_subs(self, audio_path, word_timings, chunk_size=7, overlap=0):
        """
        Play audio while displaying accurate word-aligned subtitles.

        :param audio_path: Path to the generated TTS audio file.
        :param word_timings: List of tuples (word, start_ts, end_ts) from Kokoro tokens.
        :param chunk_size: Number of words per subtitle.
        :param overlap: Number of overlapping words between chunks.
        """
        if self.is_playing:
            self.stop_playback()
            time.sleep(0.5)  # Brief pause to avoid threading race

        # Create subtitle chunks from real word timings
        self.subtitle_chunks = _create_word_aligned_subtitle_chunks(
            word_timings, chunk_size=chunk_size, overlap=overlap
        )

        self.is_playing = True
        self.playback_thread = threading.Thread(
            target=self._play_audio_with_fixed_subs,
            args=(audio_path,),
            daemon=True
        )
        self.playback_thread.start()

    def _play_audio_with_fixed_subs(self, audio_path):
        import simpleaudio as sa  # simpleaudio is cross-platform lightweight playback

        # Load audio file
        try:
            wave_obj = sa.WaveObject.from_wave_file(audio_path)
            play_obj = wave_obj.play()
        except Exception as e:
            print(f"Failed to play audio: {e}")
            self.is_playing = False
            return

        start_time = time.time()

        for start, end, subtitle_text in self.subtitle_chunks:
            if not self.is_playing:
                break

            # Wait until subtitle start time
            while time.time() - start_time < start:
                if not self.is_playing:
                    break
                time.sleep(0.01)

            # Update subtitle text on the main thread
            self.root.after(0, self.update_subtitle, subtitle_text)

            # Wait until subtitle end time
            while time.time() - start_time < end:
                if not self.is_playing:
                    break
                time.sleep(0.01)

        # Clear subtitle after playback
        self.root.after(0, self.update_subtitle, "")
        self.is_playing = False

    def _safe_audio_play(self, audio):
        """Safely play audio with error handling"""
        try:
            play(audio)
        except Exception as e:
            print(f"Audio playback error: {e}")
            # Alternative playback method using system commands
            try:
                self._system_audio_play("output.wav")
            except Exception as e2:
                print(f"System audio playback also failed: {e2}")

    def _system_audio_play(self, audio_path):
        """System-level audio playback as fallback"""
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound(audio_path, winsound.SND_FILENAME)
        elif platform.system() == "Darwin":
            subprocess.run(["afplay", audio_path], check=True)
        else:
            subprocess.run(["aplay", audio_path], check=True)

    def stop_playback(self):
        """Stop current playback"""
        self.is_playing = False
        if self.audio_process:
            try:
                self.audio_process.terminate()
            except:
                pass
        self.root.after(0, self.update_subtitle, "Playback stopped")


def generate_audio():
    """Generate audio with fixed-timing subtitles using real word timings"""
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("No Input", "Please paste a Reddit story.")
        return

    if pipeline is None:
        messagebox.showerror("Error", "Kokoro TTS pipeline not available. Please check your installation.")
        return

    num = random.randint(1, 19)
    voice = voice_by_number[num]
    voice_label.config(text=f"Selected Voice: {voice}")
    status_var.set("Generating audio...")
    root.update()

    try:
        all_word_timings = []  # Renamed for clarity

        try:
            generator = pipeline(text, voice=voice)

            cumulative_offset = 0.0
            audio_chunks = []
            all_word_timings = []

            for item in generator:
                # Collect audio
                if hasattr(item, 'output') and hasattr(item.output, 'audio'):
                    audio_np = item.output.audio.cpu().numpy()
                    duration = len(audio_np) / 24000  # Duration in seconds
                    audio_chunks.append(audio_np)
                else:
                    duration = 0.0

                # Collect word timings with offset
                if hasattr(item, 'tokens'):
                    for token in item.tokens:
                        if hasattr(token, 'start_ts') and hasattr(token, 'end_ts'):
                            adjusted_start = token.start_ts + cumulative_offset
                            adjusted_end = token.end_ts + cumulative_offset
                            all_word_timings.append((token.text, adjusted_start, adjusted_end))

                # Add to cumulative offset
                cumulative_offset += duration

        except Exception as e:
            print(f"Error during audio generation: {e}")
            # Fallback if Kokoro fails
            words = text.split()
            audio_duration = len(words) * WORD_DURATION
            audio_chunks = [np.zeros(int(24000 * audio_duration))]
            # Create dummy timings
            for i, word in enumerate(words):
                start = i * WORD_DURATION
                end = start + WORD_DURATION
                all_word_timings.append((word, start, end))

        if not audio_chunks:
            raise Exception("No audio chunks generated")

        # Save full audio
        full_audio = np.concatenate(audio_chunks)
        audio_path = "output.wav"
        sf.write(audio_path, full_audio, 24000)

        # Get audio duration
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        audio_clip.close()

        status_var.set("Audio generated. Ready to play with subtitles")

        # ✅ Send token timings
        subtitle_tracker.play_audio_with_subs(audio_path, all_word_timings)

    except Exception as e:
        messagebox.showerror("Error", f"Audio generation failed: {str(e)}")
        status_var.set("Error occurred")
        import traceback
        traceback.print_exc()


def get_recommended_thread_count(cpu_heavy=True):
    cores = os.cpu_count()
    if cores is None:
        return 4  # Default fallback
    return max(1, cores // 2) if cpu_heavy else min(cores * 4, 100)

import re

def sanitize_filename(filename):
    # Remove invalid Windows filename characters
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def create_video(name=None):
    """Create video with subtitles synced to Kokoro timing and live progress"""
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("No Input", "Please paste a Reddit story.")
        return

    if pipeline is None:
        messagebox.showerror("Error", "Kokoro TTS pipeline not available.")
        return

    num = random.randint(1, 19)
    voice = voice_by_number[num]
    voice_label.config(text=f"Selected Voice: {voice}")
    status_var.set("Generating audio for video...")
    root.update()

    def update_timer(start_time):
        while timer_running:
            elapsed = int(time.time() - start_time)
            status_var.set(f"Processing... {elapsed}s elapsed")
            time.sleep(1)

    try:
        start_time = time.time()
        timer_running = True
        threading.Thread(target=update_timer, args=(start_time,), daemon=True).start()
        progress_bar.start()

        cumulative_offset = 0.0
        audio_chunks = []
        all_word_timings = []

        generator = pipeline(text, voice=voice)
        for item in generator:
            if hasattr(item, 'output') and hasattr(item.output, 'audio'):
                audio_np = item.output.audio.cpu().numpy()
                duration = len(audio_np) / 24000
                audio_chunks.append(audio_np)
            else:
                duration = 0.0

            if hasattr(item, 'tokens'):
                for token in item.tokens:
                    if token.start_ts is not None and token.end_ts is not None:
                        adjusted_start = token.start_ts + cumulative_offset
                        adjusted_end = token.end_ts + cumulative_offset
                        all_word_timings.append((token.text, adjusted_start, adjusted_end))

            cumulative_offset += duration

        if not audio_chunks:
            raise Exception("No audio chunks generated")

        # Save full audio
        full_audio = np.concatenate(audio_chunks)
        audio_path = "output.wav"
        sf.write(audio_path, full_audio, 24000)
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration

        # Check if audio needs segmentation (over 2 minutes)
        if audio_duration > 120:
            segment_duration = 60.0  # 1 minute segments
            segment_count = int(np.ceil(audio_duration / segment_duration))
            status_var.set(f"Splitting into {segment_count} parts...")
            root.update()

            # Generate TTS for "Part X" intro
            part_intros = []
            for i in range(segment_count):
                # Generate TTS for "Part X"
                part_text = f"Part {i + 1} from {name}"
                intro_audio = []
                intro_timings = []
                intro_offset = 0.0

                # Generate audio and timings for intro
                intro_gen = pipeline(part_text, voice=voice)
                for item in intro_gen:
                    if hasattr(item, 'output') and hasattr(item.output, 'audio'):
                        audio_np = item.output.audio.cpu().numpy()
                        duration = len(audio_np) / 24000
                        intro_audio.append(audio_np)
                    if hasattr(item, 'tokens'):
                        for token in item.tokens:
                            if token.start_ts is not None and token.end_ts is not None:
                                adjusted_start = token.start_ts + intro_offset
                                adjusted_end = token.end_ts + intro_offset
                                intro_timings.append((token.text, adjusted_start, adjusted_end))
                    if hasattr(item, 'output') and hasattr(item.output, 'audio'):
                        intro_offset += duration

                part_intros.append((
                    np.concatenate(intro_audio) if intro_audio else np.array([]),
                    intro_timings,
                    intro_offset
                ))

            for segment_index in range(segment_count):
                part_start = segment_index * segment_duration
                part_end = min((segment_index + 1) * segment_duration, audio_duration)

                # Extract audio segment
                segment_audio = full_audio[int(part_start * 24000):int(part_end * 24000)]

                # Get intro for this segment
                intro_audio, intro_timings, intro_duration = part_intros[segment_index]

                # Combine intro + segment audio
                combined_audio = np.concatenate([intro_audio, segment_audio])
                segment_audio_path = f"output_part_{segment_index}.wav"
                sf.write(segment_audio_path, combined_audio, 24000)
                segment_audio_clip = AudioFileClip(segment_audio_path)

                # Filter word timings for this segment and adjust for intro
                segment_word_timings = [
                    (word, start - part_start + intro_duration, end - part_start + intro_duration)
                    for word, start, end in all_word_timings
                    if start < part_end and end > part_start
                ]

                # Combine intro timings with segment timings
                combined_timings = intro_timings + segment_word_timings

                # Create video segment
                segment_name = f"{name}_Part{segment_index + 1}" if name else f"reddit_video_Part{segment_index + 1}"
                _create_video_segment(
                    segment_audio_clip,  # AudioFileClip object
                    combined_timings,
                    num,
                    segment_name,
                    segment_index + 1,
                    segment_count,
                    pipeline  # Pass pipeline for outro TTS
                )

                # Clean up audio segment
                segment_audio_clip.close()
                os.remove(segment_audio_path)

            # Clean up full audio
            audio_clip.close()
            os.remove(audio_path)

            timer_running = False
            progress_bar.stop()
            total_time = time.time() - start_time
            status_var.set(f"Ready | Created {segment_count} parts in {total_time:.1f}s")
            return
        else:
            # For videos under 2 minutes - create single video with voiced outro
            segment_name = name if name else "reddit_video"
            output_file = _create_video_segment(
                audio_clip,
                all_word_timings,
                num,
                segment_name,
                1,  # part number
                1,  # total parts
                pipeline  # Pass pipeline for outro TTS
            )

            timer_running = False
            progress_bar.stop()
            total_time = time.time() - start_time

            if output_file:
                # Get the current user's Videos folder path dynamically
                folder_path = Path.home() / "Videos" / "Reddit Videos"
                folder_path.mkdir(parents=True, exist_ok=True)

                # Get the base file name (e.g., "output.mp4")
                filename = os.path.basename(output_file)

                # Full path where the file should be saved
                destination_path = folder_path / filename

                # Move or save the file to the new folder
                shutil.move(output_file, str(destination_path))

                # Update status
                status_var.set(f"Ready | Completed in {total_time:.1f}s")
            else:
                status_var.set("Error creating video")
    except Exception as e:
        timer_running = False
        progress_bar.stop()
        status_var.set("Error occurred")
        messagebox.showerror("Error", str(e))
        import traceback
        traceback.print_exc()
import shutil
from pathlib import Path
def create_outro_clip(text="Next part is out on the channel", duration=3, video_clip=None, color='white',
                      color_bg='black'):
    """Creates a custom outro with background matching video dimensions"""
    from moviepy.editor import TextClip, ColorClip, CompositeVideoClip

    # Use video_clip dimensions or default vertical size
    width = video_clip.w if video_clip else 1080
    height = video_clip.h if video_clip else 1920

    # Create background matching main video
    background = ColorClip((width, height), color=(0, 0, 0), duration=duration)

    # Create text clip
    txt_clip = TextClip(
        text,
        fontsize=72,
        font='Times New Roman-Bold',
        color=color,
        stroke_color=color_bg,
        stroke_width=1,
        size=(background.w * 0.92, None),
        method='caption',
        align='center',
        kerning=2
    ).set_duration(duration).set_position("center")

    # Combine text with background
    return CompositeVideoClip([background, txt_clip])


def _create_video_segment(audio_clip, word_timings, voice_num, name, part, total_parts, pipeline):
    """Create a video segment with background, subtitles, and voiced outro"""
    try:
        from moviepy.editor import ImageClip, CompositeVideoClip, TextClip, ColorClip, concatenate_videoclips, \
            VideoFileClip, AudioFileClip
        import soundfile as sf
        import numpy as np
        import os
        import random
        import time
        import tempfile

        # Variables for cleanup
        temp_audio_paths = []  # To track all temporary audio files
        cleanup_main_audio = False
        main_audio_path = None

        # Handle different audio clip types
        if not hasattr(audio_clip, 'duration'):
            if isinstance(audio_clip, (list, np.ndarray)):
                main_audio_path = f"temp_audio_{int(time.time())}.wav"
                sf.write(main_audio_path, np.concatenate(audio_clip), 24000)
                audio_clip = AudioFileClip(main_audio_path)
                cleanup_main_audio = True
                temp_audio_paths.append(main_audio_path)
            elif isinstance(audio_clip, str):
                audio_clip = AudioFileClip(audio_clip)
            else:
                raise ValueError("Unsupported audio format")

        # Create background
        width, height = 1080, 1920  # Vertical format
        audio_duration = audio_clip.duration

        # Get background clips
        clip_folder = "clips"
        clip_files = sorted([f for f in os.listdir(clip_folder)
                             if f.startswith("clip_") and f.endswith(".mp4")])
        clip_files = [os.path.join(clip_folder, f) for f in clip_files]

        if not clip_files:
            background = ColorClip((width, height), color=(0, 0, 0), duration=audio_duration)
        else:
            total_duration = 0
            selected_clips = []
            random.shuffle(clip_files)
            while total_duration < audio_duration:
                if not clip_files:
                    # Reset if we run out
                    clip_files = sorted([f for f in os.listdir(clip_folder)
                                         if f.startswith("clip_") and f.endswith(".mp4")])
                    clip_files = [os.path.join(clip_folder, f) for f in clip_files]
                    random.shuffle(clip_files)
                clip_path = clip_files.pop()
                clip = VideoFileClip(clip_path).without_audio()
                selected_clips.append(clip)
                total_duration += clip.duration
            background = concatenate_videoclips(selected_clips).subclip(0, audio_duration)

        # Precompute colors for consistency
        colors = ['white', 'blue', 'red', 'green', 'orange']
        color_idx = ((voice_num - 1) // 4) % len(colors)
        segment_color = colors[color_idx]
        segment_color_bg = 'black' if segment_color == 'white' else 'black'

        # Create subtitle clips
        subtitle_clips = []
        subtitle_chunks = _create_word_aligned_subtitle_chunks(word_timings)

        for start, end, text in subtitle_chunks:
            if start < audio_duration:
                end = min(end, audio_duration)
                duration = end - start
                if duration <= 0:
                    continue

                txt_clip = TextClip(
                    text,
                    fontsize=72,
                    font='Times New Roman-Bold',
                    color=segment_color,
                    stroke_color=segment_color_bg,
                    stroke_width=2,
                    size=(background.w * 0.92, None),
                    method='caption',
                    align='center',
                    kerning=2
                ).set_duration(duration).set_start(start)
                txt_clip = txt_clip.set_position('center')
                subtitle_clips.append(txt_clip)

        # Create main video
        main_video = CompositeVideoClip([background] + subtitle_clips)
        main_video = main_video.set_audio(audio_clip)
        main_video = main_video.set_duration(audio_duration)

        # Generate outro message
        if part < total_parts:
            outro_text = "Next part is out on the channel"
        else:
            outro_text = "Like and follow for more content"

        # Generate TTS audio for outro
        voice_name = voice_by_number[voice_num]
        outro_audio_chunks = []
        for item in pipeline(outro_text, voice=voice_name):
            if hasattr(item, 'output') and hasattr(item.output, 'audio'):
                audio_np = item.output.audio.cpu().numpy()
                outro_audio_chunks.append(audio_np)

        # Create outro audio clip
        outro_audio_clip = None
        outro_audio_path = None

        if outro_audio_chunks:
            outro_audio = np.concatenate(outro_audio_chunks)
            outro_duration = len(outro_audio) / 24000.0

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                sf.write(tmpfile.name, outro_audio, 24000)
                outro_audio_path = tmpfile.name
            outro_audio_clip = AudioFileClip(outro_audio_path)
            temp_audio_paths.append(outro_audio_path)
        else:
            # Create silent audio clip as fallback
            outro_duration = 3.0
            silent_audio = np.zeros(int(24000 * outro_duration), dtype=np.float32)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                sf.write(tmpfile.name, silent_audio, 24000)
                outro_audio_path = tmpfile.name
            outro_audio_clip = AudioFileClip(outro_audio_path)
            temp_audio_paths.append(outro_audio_path)

        # Create outro video clip with background
        outro_background = _create_background_clip(outro_duration, clip_folder)
        outro_txt = TextClip(
            outro_text,
            fontsize=72,
            font='Times New Roman-Bold',
            color=segment_color,
            stroke_color=segment_color_bg,
            stroke_width=2,
            size=(background.w * 0.92, None),
            method='caption',
            align='center',
        ).set_duration(outro_duration).set_position('center')

        outro_clip = CompositeVideoClip([outro_background, outro_txt])
        outro_clip = outro_clip.set_audio(outro_audio_clip)

        # Combine main video with outro
        final_video = concatenate_videoclips([main_video, outro_clip])
        final_duration = main_video.duration + outro_duration
        final_video = final_video.set_duration(final_duration)

        # Generate output filename
        if total_parts > 1:
            output_name_raw = f"{name}_Part{part}"
        else:
            output_name_raw = name if name else f"reddit_video_{int(time.time())}"

        output_name_safe = sanitize_filename(output_name_raw)
        output_file = f"{output_name_safe}.mp4"

        # Write final video
        final_video.write_videofile(
            output_file,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            threads=get_recommended_thread_count(cpu_heavy=True),
            preset='ultrafast'
        )

        # Clean up resources - close clips first
        final_video.close()
        main_video.close()
        background.close()
        outro_background.close()
        outro_clip.close()

        # Clean up audio files after closing clips
        for path in temp_audio_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Warning: Could not remove temp file {path}: {str(e)}")

        return output_file

    except Exception as e:
        # Cleanup even in case of error
        for path in temp_audio_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        messagebox.showerror("Video Creation Error", str(e))
        import traceback
        traceback.print_exc()
        return None

def _create_background_clip(duration, clip_folder):
    """Create background video clip of specified duration"""
    from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips
    import os
    import random

    width, height = 1080, 1920
    clip_files = sorted([f for f in os.listdir(clip_folder)
                         if f.startswith("clip_") and f.endswith(".mp4")])
    clip_files = [os.path.join(clip_folder, f) for f in clip_files]

    if not clip_files:
        return ColorClip((width, height), color=(0, 0, 0), duration=duration)

    total_duration = 0
    selected_clips = []
    random.shuffle(clip_files)

    while total_duration < duration:
        if not clip_files:
            clip_files = sorted([f for f in os.listdir(clip_folder)
                                 if f.startswith("clip_") and f.endswith(".mp4")])
            clip_files = [os.path.join(clip_folder, f) for f in clip_files]
            random.shuffle(clip_files)

        clip_path = clip_files.pop()
        clip = VideoFileClip(clip_path).without_audio()
        selected_clips.append(clip)
        total_duration += clip.duration

    return concatenate_videoclips(selected_clips).subclip(0, duration)
def _open_file(path):
    """Open file using platform-specific methods"""
    if not os.path.exists(path):
        messagebox.showerror("Error", f"File not found: {path}")
        return

    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {str(e)}")


def save_progress(subreddit_name, post_number):
    progress_file = f"progress_{subreddit_name}.txt"
    with open(progress_file, "w") as f:
        f.write(str(post_number))


def Automated_Reddit_Player(text_box):
    popup_root = tk.Tk()
    popup_root.withdraw()

    try:
        # Get subreddit name from user
        subreddit_name = simpledialog.askstring("Subreddit Input", "Enter the subreddit name:").strip()
        if not subreddit_name:
            messagebox.showinfo("Cancelled", "Operation cancelled by user.")
            return

        # Get number of videos to generate
        num_trials = simpledialog.askinteger(
            "Automated Reddit Player",
            "How many videos do you want to generate?",
            minvalue=1
        )
        if num_trials is None:
            messagebox.showinfo("Cancelled", "Operation cancelled by user.")
            return

        # Initialize Reddit progress only if file exists
        progress_file = f"progress_{subreddit_name}.txt"
        if os.path.exists(progress_file):
            current_index = load_progress(progress_file)
        else:
            current_index = 2  # or your default starting index

        # Process videos
        created_count = 0
        for i in range(num_trials):
            # Get next Reddit post
            post, name = get_reddit_post(subreddit_name, current_index)
            if not post:
                messagebox.showinfo("No More Posts", "No more valid posts available or rate limit reached")
                break

            # Update GUI
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, post)
            text_box.update_idletasks()  # Force GUI update

            # Create video
            try:
                create_video(name)  # Your video creation function
                created_count += 1
            except Exception as e:
                messagebox.showerror("Video Error", f"Failed to create video: {e}")
                break

            # Save progress and move to next post
            save_progress(progress_file, current_index + 1)
            current_index += 1

            # Add delay between requests to avoid rate limits
            time.sleep(2)

        # Final status
        messagebox.showinfo("Complete", f"Created {created_count}/{num_trials} videos")

    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        traceback.print_exc()
    finally:
        popup_root.destroy()


def get_reddit_post(subreddit_name, post_index):
    """Fetch a Reddit post with error handling and rate limit protection"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = list(subreddit.hot(limit=post_index + 1))  # +1 to account for 0-index

        if post_index >= len(posts):
            return None  # End of available posts

        post = posts[post_index]
        if not post.selftext.strip():
            return None  # Skip posts without content

        return f"{post.title}\n\n{post.selftext}", f"{post.title}"

    except praw.exceptions.APIException as e:
        if e.error_type == "RATELIMIT":
            time.sleep(60)  # Wait 1 minute for rate limit reset
            return get_reddit_post(subreddit_name, post_index)  # Retry
        messagebox.showerror("API Error", f"Reddit API error: {e}")
        return None
    except Exception as e:
        messagebox.showerror("Fetch Error", f"Failed to fetch post: {e}")
        return None


def load_progress(progress_file):
    """Load progress index from file"""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r") as f:
                return int(f.read().strip())
        except:
            return 1
    return 1  # Default starting index



# Initialize Reddit instance (should be configured elsewhere)

# 🖼 GUI Setup
root = tk.Tk()
root.title("Fixed-Timing Subtitle Generator")
root.geometry("900x750")
root.configure(bg="#2c3e50")

# Create subtitle tracker
subtitle_tracker = SubtitleTracker(root)

# Custom styling
btn_style = {
    "font": ("Arial", 12),
    "bg": "#3498db",
    "fg": "white",
    "padx": 12,
    "pady": 6,
    "borderwidth": 0,
    "relief": "flat",
    "activebackground": "#2980b9"
}
sample_btn_style = {
    "font": ("Arial", 11),
    "bg": "#9b59b6",
    "fg": "white",
    "padx": 8,
    "pady": 4,
    "borderwidth": 0,
    "relief": "flat",
    "activebackground": "#8e44ad"
}
video_btn_style = {
    "font": ("Arial", 12),
    "bg": "#e74c3c",
    "fg": "white",
    "padx": 12,
    "pady": 6,
    "borderwidth": 0,
    "relief": "flat",
    "activebackground": "#c0392b"
}

# GUI elements
header_frame = tk.Frame(root, bg="#34495e")
header_frame.pack(fill=tk.X, padx=0, pady=0)

title_label = tk.Label(
    header_frame,
    text="Fixed-Timing Subtitle Generator",
    font=("Arial", 24, "bold"),
    bg="#34495e",
    fg="#1abc9c",
    pady=10
)
title_label.pack(pady=(10, 0))

subtitle_label = tk.Label(
    header_frame,
    text=f"Subtitles change every {WORD_DURATION}s per word, showing {WORDS_PER_SUBTITLE} words at a time",
    font=("Arial", 12),
    bg="#34495e",
    fg="#bdc3c7",
    pady=5
)
subtitle_label.pack(pady=(0, 10))

# Main content frame
content_frame = tk.Frame(root, bg="#2c3e50")
content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

# Text input area
text_frame = tk.LabelFrame(
    content_frame,
    text=" Paste Your Story ",
    font=("Arial", 12, "bold"),
    bg="#34495e",
    fg="#ecf0f1",
    padx=10,
    pady=10,
    relief="flat",
    borderwidth=0
)
text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

text_box = scrolledtext.ScrolledText(
    text_frame,
    wrap=tk.WORD,
    font=("Arial", 12),
    height=15,
    bg="#34495e",
    fg="#ecf0f1",
    insertbackground="white",
    highlightthickness=0,
    relief="flat"
)
text_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Subtitle preview area
preview_frame = tk.LabelFrame(
    content_frame,
    text=" Live Subtitle Preview ",
    font=("Arial", 12, "bold"),
    bg="#34495e",
    fg="#ecf0f1",
    padx=10,
    pady=10,
    relief="flat"
)
preview_frame.pack(fill=tk.BOTH, pady=(10, 15))

def create_video_button_only():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    title = simpledialog.askstring("Enter Title", "What should the video title be?")
    create_video(title.strip())

subtitle_preview = tk.Label(
    preview_frame,
    textvariable=subtitle_tracker.current_subtitle,
    font=("Arial", 16, "bold"),
    wraplength=800,
    bg="#2c3e50",
    fg="#f1c40f",
    height=4,
    justify="center"
)
subtitle_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Button area
button_frame = tk.Frame(content_frame, bg="#2c3e50")
button_frame.pack(fill=tk.X, pady=10)

# Create buttons
generate_btn = tk.Button(
    button_frame,
    text="🔊 Play Audio with Live Subtitles",
    command=generate_audio,
    **btn_style,
    cursor="hand2"
)
generate_btn.pack(side=tk.LEFT, padx=5, ipadx=5)

video_btn = tk.Button(
    button_frame,
    text="🎬 Create Video with Fixed Subtitles",
    command=create_video_button_only,
    **video_btn_style,
    cursor="hand2"
)
video_btn.pack(side=tk.LEFT, padx=5, ipadx=5)

stop_btn = tk.Button(
    button_frame,
    text="⏹ Stop Playback",
    command=subtitle_tracker.stop_playback,
    **sample_btn_style,
    cursor="hand2"
)
stop_btn.pack(side=tk.LEFT, padx=5, ipadx=5)

# Right side buttons
right_btn_frame = tk.Frame(button_frame, bg="#2c3e50")
right_btn_frame.pack(side=tk.RIGHT, padx=10)

audio_btn = tk.Button(
    right_btn_frame,
    text="Automate Reddit Video Stories",
    command=lambda: Automated_Reddit_Player(text_box),
    **sample_btn_style,
    cursor="hand2"
)
audio_btn.pack(side=tk.LEFT, padx=5, ipadx=5)
# Voice display
voice_frame = tk.Frame(button_frame, bg="#2c3e50")
voice_frame.pack(side=tk.RIGHT, padx=10)

voice_label = tk.Label(
    voice_frame,
    text="Selected Voice: (random)",
    font=("Arial", 11, "italic"),
    bg="#2c3e50",
    fg="#f1c40f"
)
voice_label.pack()

# Status bar
status_frame = tk.Frame(root, bg="#34495e", height=25)
status_frame.pack(fill=tk.X, side=tk.BOTTOM)

status_var = tk.StringVar()
status_var.set("Ready - Kokoro TTS " + ("Available" if pipeline else "Not Available"))
status_bar = tk.Label(
    status_frame,
    textvariable=status_var,
    bd=1,
    relief=tk.SUNKEN,
    anchor=tk.W,
    bg="#34495e",
    fg="#ecf0f1",
    font=("Arial", 10),
    padx=10
)
status_bar.pack(fill=tk.X)

# Tips area
tips_frame = tk.Frame(content_frame, bg="#2c3e50")
tips_frame.pack(fill=tk.X, pady=(5, 0))

progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300)
progress_bar.pack(pady=10)

timer_label = tk.Label(root, text="Elapsed Time: 0.0s")
timer_label.pack()

tips_label = tk.Label(
    tips_frame,
    text=f"💡 Each word is displayed for {WORD_DURATION} seconds. Subtitles show {WORDS_PER_SUBTITLE} words at a time.",
    font=("Arial", 10),
    fg="#bdc3c7",
    bg="#2c3e50",
    justify=tk.LEFT,
    wraplength=800
)
tips_label.pack(anchor=tk.W)

progress_bar = ttk.Progressbar(root, mode='indeterminate', length=300)
progress_bar.pack(pady=10)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var)
status_label.pack()

# Set dark theme for text widget
text_box.configure(
    selectbackground="#3498db",
    inactiveselectbackground="#3498db"
)

# Cleanup on window close
def on_closing():
    if subtitle_tracker.is_playing:
        subtitle_tracker.stop_playback()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()