import os
import sys
import threading
import queue
import logging
import json
from pathlib import Path
from tkinter import Tk, filedialog, ttk, scrolledtext, messagebox
import tkinter as tk
import subprocess
from datetime import datetime
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configure logging
if RICH_AVAILABLE:
    console = Console()
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RichHandler(console=console, show_time=True, show_level=False, rich_tracebacks=False),
            logging.FileHandler('media_processor.log', mode='a', encoding='utf-8')
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('media_processor.log', mode='a', encoding='utf-8')
        ]
    )
logger = logging.getLogger(__name__)

class MediaProcessor:
    """Process media files with GPU-accelerated FFmpeg."""

    SUPPORTED_VIDEO_EXT = ('.mp4', '.mkv', '.avi')
    SUPPORTED_AUDIO_EXT = ('.mp3', '.wav', '.flac')

    def __init__(self, input_paths=None, output_dir=None, gui_log_callback=None):
        self.input_paths = [Path(p) for p in input_paths] if input_paths else [Path.cwd()]
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / f"{self.input_paths[0].name}_output"
        self.output_dir.mkdir(exist_ok=True)
        self.queue = queue.Queue()
        self.running = False
        self.gpu_available = False
        self.gpu_name = "Unknown"
        self.video_encoder = 'libx264'
        self.decoder = 'auto'
        self.cuda_filters_available = False
        self.gui_log_callback = gui_log_callback
        self.detect_gpu()
        self.check_ffmpeg_support()

    def detect_gpu(self):
        """Detect NVIDIA GPU and set encoder/decoder."""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv'], capture_output=True, text=True)
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split('\n')
                if len(gpu_info) > 1:
                    self.gpu_name = gpu_info[1].strip()
                    self.gpu_available = True
                    self.video_encoder = 'h264_nvenc'
                    self.decoder = 'h264_cuvid'
                    log_msg = f"🖥️ GPU: {self.gpu_name} (NVENC, CUDA decoding)"
                    logger.info(log_msg)
                    if self.gui_log_callback:
                        self.gui_log_callback(log_msg)
                    return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        self.gpu_available = False
        self.video_encoder = 'libx264'
        self.decoder = 'auto'
        log_msg = "⚠️ No GPU detected, using CPU (libx264)"
        logger.info(log_msg)
        if self.gui_log_callback:
            self.gui_log_callback(log_msg)

    def check_ffmpeg_support(self):
        """Verify FFmpeg NVENC and CUDA filter support."""
        if not FFMPEG_AVAILABLE:
            log_msg = "❌ FFmpeg not installed"
            logger.error(log_msg)
            if self.gui_log_callback:
                self.gui_log_callback(log_msg)
            return
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
            if 'h264_nvenc' in result.stdout:
                log_msg = "✅ FFmpeg supports h264_nvenc"
                logger.info(log_msg)
                if self.gui_log_callback:
                    self.gui_log_callback(log_msg)
            else:
                self.gpu_available = False
                self.video_encoder = 'libx264'
                log_msg = "⚠️ FFmpeg lacks h264_nvenc, using CPU"
                logger.warning(log_msg)
                if self.gui_log_callback:
                    self.gui_log_callback(log_msg)

            result = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True)
            if 'unsharp_cuda' in result.stdout:
                self.cuda_filters_available = True
                log_msg = "✅ FFmpeg supports CUDA filters"
                logger.info(log_msg)
                if self.gui_log_callback:
                    self.gui_log_callback(log_msg)
        except Exception as e:
            log_msg = f"❌ FFmpeg check failed: {str(e)}"
            logger.error(log_msg)
            if self.gui_log_callback:
                self.gui_log_callback(log_msg)

    def get_media_files(self):
        """Retrieve supported media files from input paths."""
        media_files = []
        try:
            for path in self.input_paths:
                if path.is_file() and path.suffix.lower() in (self.SUPPORTED_VIDEO_EXT + self.SUPPORTED_AUDIO_EXT):
                    media_files.append(path)
                elif path.is_dir():
                    for ext in self.SUPPORTED_VIDEO_EXT + self.SUPPORTED_AUDIO_EXT:
                        media_files.extend(path.rglob(f'*{ext}'))
            log_msg = f"📁 Found {len(media_files)} media files"
            logger.info(log_msg)
            if self.gui_log_callback:
                self.gui_log_callback(log_msg)
            return media_files
        except Exception as e:
            log_msg = f"❌ Error accessing paths: {str(e)}"
            logger.error(log_msg)
            if self.gui_log_callback:
                self.gui_log_callback(log_msg)
            return []

    def validate_settings(self, settings, is_video):
        """Validate settings for acceptable ranges."""
        validated = settings.copy()
        validated['speed'] = max(0.5, min(2.0, settings['speed']))
        validated['volume'] = max(0.0, min(200.0, settings['volume']))
        validated['trim_start'] = max(0.0, settings['trim_start'])
        if is_video:
            validated['frame_rate'] = max(10, min(60, settings['frame_rate']))
            validated['vibrancy'] = max(0.5, min(2.0, settings['vibrancy']))
            validated['sharpness'] = max(0.0, min(2.0, settings['sharpness']))
        return validated

    def get_video_info(self, file_path):
        """Extract bitrate and FPS from video file."""
        try:
            probe = ffmpeg.probe(str(file_path))
            video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            bitrate = float(probe['format'].get('bit_rate', 0)) / 1000  # kb/s
            fps = eval(video_stream.get('r_frame_rate', '0/1'))  # Convert fraction to float
            return bitrate, fps
        except Exception:
            return 0, 0

    def process_file(self, file_path, settings, progress_callback=None):
        """Process a media file with FFmpeg."""
        if not FFMPEG_AVAILABLE:
            log_msg = "❌ FFmpeg not installed"
            logger.error(log_msg)
            if progress_callback:
                progress_callback(log_msg)
            return False

        try:
            file_path = Path(file_path)
            output_path = self.output_dir / f"processed_{file_path.name}"
            is_video = file_path.suffix.lower() in self.SUPPORTED_VIDEO_EXT
            start_time = datetime.now()

            # Validate settings
            settings = self.validate_settings(settings, is_video)

            # Probe input file
            probe = ffmpeg.probe(str(file_path))
            duration = float(probe['format']['duration'])
            bitrate, fps = self.get_video_info(file_path) if is_video else (0, 0)
            info = f"Bitrate: {bitrate:.0f} kb/s, FPS: {fps:.2f}" if is_video else "Audio only"
            log_msg = f"🎥 Processing {file_path.name} ({info}, Duration: {duration:.2f}s)"
            logger.info(log_msg)
            if progress_callback:
                progress_callback(log_msg)

            # Initialize input
            input_kwargs = {'hwaccel': 'cuda', 'c:v': self.decoder} if self.gpu_available and is_video else {}
            stream = ffmpeg.input(str(file_path), **input_kwargs)
            video_stream = stream.video if is_video else None
            audio_stream = stream.audio if is_video else stream

            # Apply trimming
            trim_args = {'start': settings['trim_start']}
            if settings['trim_end'] != float('inf') and settings['trim_end'] <= duration:
                trim_args['duration'] = settings['trim_end'] - settings['trim_start']
            if trim_args:
                if is_video:
                    video_stream = video_stream.filter('trim', **trim_args).filter('setpts', 'PTS-STARTPTS')
                audio_stream = audio_stream.filter('atrim', **trim_args).filter('asetpts', 'PTS-STARTPTS')

            # Apply speed change
            if settings['speed'] != 1.0:
                speed_factor = 1.0 / settings['speed']
                if is_video:
                    video_stream = video_stream.filter('setpts', f"{speed_factor}*PTS")
                audio_stream = audio_stream.filter('atempo', settings['speed'])

            # Apply volume change
            if settings['volume'] != 100.0:
                audio_stream = audio_stream.filter('volume', settings['volume'] / 100.0)

            # Apply frame rate change
            if is_video and settings['frame_rate']:
                if self.gpu_available and self.cuda_filters_available:
                    video_stream = video_stream.filter('scale_cuda', format='yuv420p', fps=settings['frame_rate'])
                else:
                    video_stream = video_stream.filter('fps', settings['frame_rate'])

            # Apply vibrancy
            if is_video and settings['vibrancy'] != 1.0:
                video_stream = video_stream.filter('eq', saturation=settings['vibrancy'])

            # Apply sharpness
            if is_video and settings['sharpness'] != 1.0:
                if self.gpu_available and self.cuda_filters_available:
                    video_stream = video_stream.filter('unsharp_cuda', luma_amount=settings['sharpness'])
                else:
                    video_stream = video_stream.filter('unsharp', lx=5, ly=5, la=settings['sharpness'])

            # Combine streams and output
            kwargs = {'c:a': 'aac', 'preset': 'fast'} if is_video else {'c:a': 'mp3'}
            if is_video:
                kwargs['c:v'] = self.video_encoder
                kwargs['rc'] = 'vbr'
                kwargs['b:v'] = '5000k'
                output = ffmpeg.output(video_stream, audio_stream, str(output_path), **kwargs)
            else:
                output = ffmpeg.output(audio_stream, str(output_path), **kwargs)

            # Run FFmpeg
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            elapsed = (datetime.now() - start_time).total_seconds()
            log_msg = f"✔️ Processed {file_path.name} in {elapsed:.2f}s"
            logger.info(log_msg)
            if progress_callback:
                progress_callback(log_msg)
            return True
        except ffmpeg.Error as e:
            log_msg = f"❌ FFmpeg error: {file_path.name} ({e.stderr.decode()[:100]})"
            logger.error(log_msg)
            if progress_callback:
                progress_callback(log_msg)
            return False
        except Exception as e:
            log_msg = f"❌ Error: {file_path.name} ({str(e)})"
            logger.error(log_msg)
            if progress_callback:
                progress_callback(log_msg)
            return False

    def process_batch(self, settings, progress_callback=None):
        """Process media files with progress bar."""
        media_files = self.get_media_files()
        if not media_files:
            log_msg = "⚠️ No media files found"
            logger.warning(log_msg)
            if progress_callback:
                progress_callback(log_msg)
            return

        total_files = len(media_files)
        processed = 0
        log_msg = f"🚀 Starting batch of {total_files} files"
        logger.info(log_msg)
        if progress_callback:
            progress_callback(log_msg)

        if RICH_AVAILABLE:
            with Progress(
                TextColumn("{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Processing...", total=total_files)
                for file in media_files:
                    if not self.running:
                        log_msg = "🛑 Batch stopped by user"
                        logger.info(log_msg)
                        if progress_callback:
                            progress_callback(log_msg)
                        break
                    success = self.process_file(file, settings, progress_callback)
                    if success:
                        processed += 1
                    progress.update(task, advance=1)
                    progress_msg = f"📊 {processed}/{total_files} files done"
                    if progress_callback:
                        progress_callback(progress_msg)
        else:
            for file in media_files:
                if not self.running:
                    log_msg = "🛑 Batch stopped by user"
                    logger.info(log_msg)
                    if progress_callback:
                        progress_callback(log_msg)
                    break
                success = self.process_file(file, settings, progress_callback)
                if success:
                    processed += 1
                progress_msg = f"📊 {processed}/{total_files} files done"
                logger.info(progress_msg)
                if progress_callback:
                    progress_callback(progress_msg)

        log_msg = f"🏁 Batch complete: {processed}/{total_files} files"
        logger.info(log_msg)
        if progress_callback:
            progress_callback(log_msg)

class MediaProcessorGUI:
    """Tkinter GUI for media processor."""

    def __init__(self, root):
        self.root = root
        self.root.title("Media Processor")
        self.root.geometry("600x600")
        self.config_file = Path('config.json')
        self.load_config()
        self.processor = MediaProcessor(self.input_paths, self.output_dir, self.log_message)
        self.settings = {
            'speed': 1.0,
            'frame_rate': 30,
            'vibrancy': 1.0,
            'sharpness': 1.0,
            'trim_start': 0.0,
            'trim_end': float('inf'),
            'volume': 100.0
        }
        self.running = False
        self.setup_gui()

    def load_config(self):
        """Load input/output paths from config."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.input_paths = [Path(p) for p in config.get('input_paths', [str(Path.cwd())])]
                self.output_dir = Path(config.get('output_dir', str(Path.cwd() / f"{self.input_paths[0].name}_output")))
            else:
                self.input_paths = [Path.cwd()]
                self.output_dir = None
        except Exception as e:
            logger.error(f"❌ Config load error: {str(e)}")
            self.input_paths = [Path.cwd()]
            self.output_dir = None

    def save_config(self):
        """Save input/output paths to config."""
        try:
            config = {
                'input_paths': [str(p) for p in self.input_paths],
                'output_dir': str(self.output_dir) if self.output_dir else str(self.processor.output_dir)
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Config save error: {str(e)}")

    def setup_gui(self):
        """Set up Tkinter GUI components."""
        io_frame = ttk.LabelFrame(self.root, text="Input/Output", padding=10)
        io_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(io_frame, text="Input (Folder/Files):").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.input_label = ttk.Label(io_frame, text=", ".join([str(p) for p in self.input_paths])[:300], wraplength=300)
        self.input_label.grid(row=0, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        ttk.Button(io_frame, text="Browse Folder", command=self.browse_input_folder).grid(row=0, column=3, padx=5, pady=2)
        ttk.Button(io_frame, text="Browse Files", command=self.browse_input_files).grid(row=0, column=4, padx=5, pady=2)

        ttk.Label(io_frame, text="Output Folder:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.output_label = ttk.Label(io_frame, text=str(self.output_dir or self.processor.output_dir), wraplength=300)
        self.output_label.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        ttk.Button(io_frame, text="Browse", command=self.browse_output).grid(row=1, column=3, padx=5, pady=2)

        settings_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)

        gpu_status = f"GPU: {self.processor.gpu_name}" if self.processor.gpu_available else "GPU: None (CPU mode)"
        self.gpu_label = ttk.Label(settings_frame, text=gpu_status)
        self.gpu_label.grid(row=0, column=0, columnspan=3, sticky='w', padx=5, pady=2)

        ttk.Label(settings_frame, text="Speed (0.5x-2x):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(settings_frame, from_=0.5, to=2.0, variable=self.speed_var, orient='horizontal').grid(row=1, column=1, padx=5, pady=2)
        self.speed_entry = ttk.Entry(settings_frame, textvariable=self.speed_var, width=6)
        self.speed_entry.grid(row=1, column=2, padx=5, pady=2)
        self.speed_entry.bind('<Return>', lambda e: self.validate_entry(self.speed_entry, self.speed_var, 0.5, 2.0))

        ttk.Label(settings_frame, text="Frame Rate (10-60):").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.fps_var = tk.DoubleVar(value=30)
        ttk.Scale(settings_frame, from_=10, to=60, variable=self.fps_var, orient='horizontal').grid(row=2, column=1, padx=5, pady=2)
        self.fps_entry = ttk.Entry(settings_frame, textvariable=self.fps_var, width=6)
        self.fps_entry.grid(row=2, column=2, padx=5, pady=2)
        self.fps_entry.bind('<Return>', lambda e: self.validate_entry(self.fps_entry, self.fps_var, 10, 60))

        ttk.Label(settings_frame, text="Vibrancy (0.5-2):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.vibrancy_var = tk.DoubleVar(value=1.0)
        ttk.Scale(settings_frame, from_=0.5, to=2.0, variable=self.vibrancy_var, orient='horizontal').grid(row=3, column=1, padx=5, pady=2)
        self.vibrancy_entry = ttk.Entry(settings_frame, textvariable=self.vibrancy_var, width=6)
        self.vibrancy_entry.grid(row=3, column=2, padx=5, pady=2)
        self.vibrancy_entry.bind('<Return>', lambda e: self.validate_entry(self.vibrancy_entry, self.vibrancy_var, 0.5, 2.0))

        ttk.Label(settings_frame, text="Sharpness (0-2):").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.sharpness_var = tk.DoubleVar(value=1.0)
        self.sharpness_scale = ttk.Scale(settings_frame, from_=0.0, to=2.0, variable=self.sharpness_var, orient='horizontal')
        self.sharpness_scale.grid(row=4, column=1, padx=5, pady=2)
        self.sharpness_entry = ttk.Entry(settings_frame, textvariable=self.sharpness_var, width=6)
        self.sharpness_entry.grid(row=4, column=2, padx=5, pady=2)
        self.sharpness_entry.bind('<Return>', lambda e: self.validate_entry(self.sharpness_entry, self.sharpness_var, 0.0, 2.0))

        ttk.Label(settings_frame, text="Volume (0-200%):").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        self.volume_var = tk.DoubleVar(value=100.0)
        ttk.Scale(settings_frame, from_=0.0, to=200.0, variable=self.volume_var, orient='horizontal').grid(row=5, column=1, padx=5, pady=2)
        self.volume_entry = ttk.Entry(settings_frame, textvariable=self.volume_var, width=6)
        self.volume_entry.grid(row=5, column=2, padx=5, pady=2)
        self.volume_entry.bind('<Return>', lambda e: self.validate_entry(self.volume_entry, self.volume_var, 0, 200))

        ttk.Label(settings_frame, text="Trim Start (s):").grid(row=6, column=0, sticky='w', padx=5, pady=2)
        self.trim_start_var = tk.DoubleVar(value=0.0)
        self.trim_start_entry = ttk.Entry(settings_frame, textvariable=self.trim_start_var, width=10)
        self.trim_start_entry.grid(row=6, column=1, padx=5, pady=2)
        self.trim_start_entry.bind('<Return>', lambda e: self.validate_entry(self.trim_start_entry, self.trim_start_var, 0, float('inf')))

        ttk.Label(settings_frame, text="Trim End (s):").grid(row=7, column=0, sticky='w', padx=5, pady=2)
        self.trim_end_var = tk.DoubleVar(value=float('inf'))
        self.trim_end_entry = ttk.Entry(settings_frame, textvariable=self.trim_end_var, width=10)
        self.trim_end_entry.grid(row=7, column=1, padx=5, pady=2)
        self.trim_end_entry.bind('<Return>', lambda e: self.validate_entry(self.trim_end_entry, self.trim_end_var, 0, float('inf')))

        self.start_button = ttk.Button(self.root, text="Start Processing", command=self.start_processing)
        self.start_button.pack(pady=10)

        self.log_text = scrolledtext.ScrolledText(self.root, height=10, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w').pack(fill='x', padx=10, pady=5)

    def validate_entry(self, entry, var, min_val, max_val):
        """Validate entry input."""
        try:
            value = float(entry.get())
            if min_val <= value <= max_val:
                var.set(value)
            else:
                var.set(max(min_val, min(max_val, value)))
                entry.delete(0, tk.END)
                entry.insert(0, var.get())
                messagebox.showwarning("Invalid Input", f"Value must be between {min_val} and {max_val}.")
        except ValueError:
            var.set(min_val)
            entry.delete(0, tk.END)
            entry.insert(0, var.get())
            messagebox.showerror("Invalid Input", "Please enter a number.")

    def browse_input_folder(self):
        """Select input folder."""
        directory = filedialog.askdirectory()
        if directory:
            self.input_paths = [Path(directory)]
            self.processor.input_paths = self.input_paths
            self.update_output_dir()
            self.input_label.config(text=str(self.input_paths[0]))
            self.output_label.config(text=str(self.processor.output_dir))
            self.save_config()

    def browse_input_files(self):
        """Select input files."""
        files = filedialog.askopenfilenames(
            filetypes=[("Media Files", "*.mp4 *.mkv *.avi *.mp3 *.wav *.flac"), ("All Files", "*.*")]
        )
        if files:
            self.input_paths = [Path(f) for f in files]
            self.processor.input_paths = self.input_paths
            self.update_output_dir()
            self.input_label.config(text=", ".join([str(p) for p in self.input_paths])[:300])
            self.output_label.config(text=str(self.processor.output_dir))
            self.save_config()

    def browse_output(self):
        """Select output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir = Path(directory)
            self.processor.output_dir = self.output_dir
            self.output_label.config(text=str(self.output_dir))
            self.save_config()

    def update_output_dir(self):
        """Update output directory."""
        self.output_dir = self.input_paths[0].parent / f"{self.input_paths[0].name}_output"
        self.processor.output_dir = self.output_dir
        self.save_config()

    def log_message(self, message):
        """Log to GUI."""
        self.root.after(0, lambda: self._update_log_text(message))

    def _update_log_text(self, message):
        """Thread-safe GUI log update."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_processing(self):
        """Start processing in a thread."""
        if self.running:
            self.running = False
            self.processor.running = False
            self.start_button.config(text="Start Processing")
            self.status_var.set("Stopped")
            return

        if not self.input_paths:
            messagebox.showerror("Error", "No input paths selected.")
            return

        self.running = True
        self.processor.running = True
        self.start_button.config(text="Stop Processing")
        self.status_var.set("Processing...")
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

        self.settings.update({
            'speed': self.speed_var.get(),
            'frame_rate': self.fps_var.get(),
            'vibrancy': self.vibrancy_var.get(),
            'sharpness': self.sharpness_var.get(),
            'trim_start': self.trim_start_var.get(),
            'trim_end': self.trim_end_var.get(),
            'volume': self.volume_var.get()
        })

        threading.Thread(target=self.process_thread, daemon=True).start()

    def process_thread(self):
        """Run batch processing."""
        try:
            self.processor.process_batch(self.settings, self.log_message)
        except Exception as e:
            log_msg = f"❌ Processing error: {str(e)}"
            self.log_message(log_msg)
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.running = False
            self.processor.running = False
            self.root.after(0, lambda: self.start_button.config(text="Start Processing"))
            self.root.after(0, lambda: self.status_var.set("Ready"))

def main():
    """Main entry point."""
    root = Tk()
    app = MediaProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()