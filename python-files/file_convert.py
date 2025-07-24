import os
import subprocess
import logging
import threading
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, StringVar, OptionMenu, Checkbutton, IntVar, Frame, Scrollbar, Listbox

class VideoConverterApp:
    def __init__(self, root):
        """Initialize the application with default settings and GUI elements."""
        self.root = root
        self.root.title("Advanced Video Converter")

        # Configure logging
        self.setup_logging()

        # Default settings
        self.settings = {
            'output_format': '.mkv',
            'codec': 'libx264',
            'crf': '23',
            'preset': 'slow',
            'copy_audio': True,
            'copy_subtitles': True,
            'output_dir': os.path.join(os.path.dirname(__file__), "output"),
            'parallel_processes': 4
        }

        # Supported video extensions
        self.supported_extensions = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".m2ts", ".ts", ".vob", ".webm", ".ogv"}

        # Thread for running conversions in background
        self.conversion_thread = None

        # Create GUI
        self.create_widgets()

        # Check for FFmpeg
        self.check_ffmpeg()

    def setup_logging(self):
        """Configure logging to file and console."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('video_converter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_ffmpeg(self):
        """Check if FFmpeg exists and is accessible."""
        self.ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
        if not os.path.exists(self.ffmpeg_path):
            messagebox.showerror("Error", "ffmpeg.exe not found next to the script.")
            self.logger.error("FFmpeg executable not found")
            return False
        return True

    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main frame
        main_frame = Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Input section
        input_frame = Frame(main_frame)
        input_frame.pack(fill='x', pady=5)

        Label(input_frame, text="Input:").pack(side='left')
        self.input_entry = Entry(input_frame, width=50)
        self.input_entry.pack(side='left', padx=5)
        Button(input_frame, text="Browse...", command=self.browse).pack(side='left')

        # Settings section
        settings_frame = Frame(main_frame)
        settings_frame.pack(fill='x', pady=5)

        # Output format
        Label(settings_frame, text="Output Format:").grid(row=0, column=0, sticky='w')
        self.output_format_var = StringVar(value=self.settings['output_format'])
        OptionMenu(settings_frame, self.output_format_var, *['.mkv', '.mp4']).grid(row=0, column=1, sticky='w')

        # Codec settings
        Label(settings_frame, text="Codec:").grid(row=1, column=0, sticky='w')
        self.codec_var = StringVar(value=self.settings['codec'])
        OptionMenu(settings_frame, self.codec_var, *['libx264', 'libx265']).grid(row=1, column=1, sticky='w')

        Label(settings_frame, text="CRF:").grid(row=1, column=2, sticky='w')
        self.crf_entry = Entry(settings_frame, width=5)
        self.crf_entry.insert(0, self.settings['crf'])
        self.crf_entry.grid(row=1, column=3, sticky='w')

        Label(settings_frame, text="Preset:").grid(row=1, column=4, sticky='w')
        self.preset_var = StringVar(value=self.settings['preset'])
        OptionMenu(settings_frame, self.preset_var, *['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']).grid(row=1, column=5, sticky='w')

        # Audio/Subtitle options
        self.copy_audio_var = IntVar(value=int(self.settings['copy_audio']))
        Checkbutton(settings_frame, text="Copy Audio", variable=self.copy_audio_var).grid(row=2, column=0, sticky='w')

        self.copy_subtitles_var = IntVar(value=int(self.settings['copy_subtitles']))
        Checkbutton(settings_frame, text="Copy Subtitles", variable=self.copy_subtitles_var).grid(row=2, column=1, sticky='w')

        # Parallel processes
        Label(settings_frame, text="Parallel Processes:").grid(row=2, column=2, sticky='w')
        self.parallel_processes_entry = Entry(settings_frame, width=5)
        self.parallel_processes_entry.insert(0, self.settings['parallel_processes'])
        self.parallel_processes_entry.grid(row=2, column=3, sticky='w')

        # Output directory
        Label(settings_frame, text="Output Directory:").grid(row=3, column=0, sticky='w')
        self.output_dir_entry = Entry(settings_frame, width=50)
        self.output_dir_entry.insert(0, self.settings['output_dir'])
        self.output_dir_entry.grid(row=3, column=1, columnspan=4, sticky='w')
        Button(settings_frame, text="Browse...", command=self.browse_output_dir).grid(row=3, column=5, sticky='w')

        # Action buttons
        button_frame = Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        Button(button_frame, text="Convert", command=self.start_conversion).pack(side='left', padx=5)
        Button(button_frame, text="Clear Log", command=self.clear_log).pack(side='left', padx=5)

        # Log display
        log_frame = Frame(main_frame)
        log_frame.pack(fill='both', expand=True)

        Label(log_frame, text="Log:").pack(anchor='w')
        self.log_text = Listbox(log_frame, height=15, width=100)
        self.log_text.pack(fill='both', expand=True)

        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # Redirect stdout and stderr to log
        self.redirect_output()

    def redirect_output(self):
        """Redirect stdout and stderr to the log display."""
        class StreamToWidget:
            def __init__(self, widget, logger):
                self.widget = widget
                self.logger = logger

            def write(self, string):
                self.widget.insert('end', string)
                self.widget.see('end')
                self.logger.info(string.strip())

            def flush(self):
                pass

        sys.stdout = StreamToWidget(self.log_text, self.logger)
        sys.stderr = StreamToWidget(self.log_text, self.logger)

    def browse(self):
        """Open file dialog to select input file or folder."""
        file_or_folder = filedialog.askopenfilename() or filedialog.askdirectory()
        if file_or_folder:
            self.input_entry.delete(0, 'end')
            self.input_entry.insert(0, file_or_folder)

    def browse_output_dir(self):
        """Open directory dialog to select output directory."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir_entry.delete(0, 'end')
            self.output_dir_entry.insert(0, dir_path)
            self.settings['output_dir'] = dir_path

    def update_settings(self):
        """Update settings from GUI inputs."""
        self.settings.update({
            'output_format': self.output_format_var.get(),
            'codec': self.codec_var.get(),
            'crf': self.crf_entry.get(),
            'preset': self.preset_var.get(),
            'copy_audio': bool(self.copy_audio_var.get()),
            'copy_subtitles': bool(self.copy_subtitles_var.get()),
            'output_dir': self.output_dir_entry.get(),
            'parallel_processes': int(self.parallel_processes_entry.get())
        })

    def validate_settings(self):
        """Validate user settings before conversion."""
        try:
            crf = int(self.settings['crf'])
            if not 0 <= crf <= 51:
                raise ValueError("CRF must be between 0 and 51")

            processes = int(self.settings['parallel_processes'])
            if processes < 1:
                raise ValueError("Number of parallel processes must be at least 1")

            if not os.path.exists(self.settings['output_dir']):
                os.makedirs(self.settings['output_dir'])

            return True
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid setting: {str(e)}")
            self.logger.error(f"Invalid setting: {str(e)}")
            return False

    def convert_file(self, file_path):
        """Convert a single file using FFmpeg."""
        try:
            # Create output file path
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            output_file = os.path.join(
                self.settings['output_dir'],
                f"{name_without_ext}{self.settings['output_format']}"
            )

            # Build FFmpeg command
            cmd = [
                self.ffmpeg_path, "-hide_banner", "-loglevel", "error", "-stats",
                "-i", file_path,
                "-map", "0:v?",
                "-map", "0:a?" if self.settings['copy_audio'] else None,
                "-map", "0:s?" if self.settings['copy_subtitles'] else None,
                "-map", "0:t?",
                "-c:v", self.settings['codec'],
                "-crf", self.settings['crf'],
                "-preset", self.settings['preset']
            ]

            # Filter out None values
            cmd = [x for x in cmd if x is not None]

            # Add audio and subtitle copying options
            if self.settings['copy_audio']:
                cmd.extend(["-c:a", "copy"])
            if self.settings['copy_subtitles']:
                cmd.extend(["-c:s", "copy"])

            # Add output file
            cmd.append(output_file)

            # Run FFmpeg command
            self.logger.info(f"Converting: {file_path}")
            subprocess.run(cmd, check=True)
            self.logger.info(f"Successfully converted to: {output_file}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Conversion failed for {file_path}: {str(e)}")
            return False

    def process_files(self, file_paths):
        """Process multiple files with parallel processing."""
        from concurrent.futures import ThreadPoolExecutor

        max_workers = min(len(file_paths), self.settings['parallel_processes'])
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.convert_file, file_paths))

        success_count = sum(results)
        failure_count = len(results) - success_count

        self.logger.info(f"\nConversion complete. Success: {success_count}, Failed: {failure_count}")

        if failure_count > 0:
            messagebox.showwarning(
                "Conversion Complete",
                f"Conversion complete. {success_count} files succeeded, {failure_count} failed. See log for details."
            )
        else:
            messagebox.showinfo("Conversion Complete", "All files converted successfully!")

    def start_conversion(self):
        """Start the conversion process in a separate thread."""
        self.update_settings()

        if not self.validate_settings():
            return

        input_path = self.input_entry.get()
        if not input_path:
            messagebox.showwarning("Warning", "Please select a file or folder.")
            return

        # Disable convert button during conversion
        self.root.nametowidget("convert").config(state='disabled')

        # Start conversion in a separate thread
        self.conversion_thread = threading.Thread(
            target=self.handle_conversion,
            args=(input_path,),
            daemon=True
        )
        self.conversion_thread.start()

    def handle_conversion(self, input_path):
        """Handle the conversion process based on input type."""
        try:
            if os.path.isdir(input_path):
                self.process_folder(input_path)
            elif os.path.isfile(input_path):
                self.process_single_file(input_path)
            else:
                self.logger.error("Invalid input path")
                messagebox.showerror("Error", "Invalid input path.")

        finally:
            # Re-enable convert button
            self.root.after(0, lambda: self.root.nametowidget("convert").config(state='normal'))

    def process_folder(self, folder_path):
        """Process all supported files in a folder and its subfolders."""
        file_paths = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file_path.lower().endswith(ext.lower()) for ext in self.supported_extensions):
                    file_paths.append(file_path)

        if not file_paths:
            self.logger.info("No supported files found in the selected folder.")
            messagebox.showinfo("Information", "No supported files found in the selected folder.")
            return

        self.logger.info(f"Found {len(file_paths)} files to convert.")
        self.process_files(file_paths)

    def process_single_file(self, file_path):
        """Process a single file."""
        if any(file_path.lower().endswith(ext.lower()) for ext in self.supported_extensions):
            self.process_files([file_path])
        else:
            self.logger.error(f"Unsupported file type: {file_path}")
            messagebox.showerror("Error", "Unsupported file type.")

    def clear_log(self):
        """Clear the log display."""
        self.log_text.delete(0, 'end')

if __name__ == "__main__":
    import sys
    root = Tk()
    app = VideoConverterApp(root)
    root.mainloop()