import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import subprocess
import threading
import time
import urllib.parse
import shlex
import sys
import queue # For thread-safe communication

# Attempt to import ttkbootstrap for modern styling
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    USE_TTK_BOOTSTRAP = True
except ImportError:
    # Fallback to standard tkinter if ttkbootstrap is not available
    import tkinter as tk
    from tkinter import ttk
    USE_TTK_BOOTSTRAP = False
    print("ttkbootstrap not found. Using standard tkinter. Run 'pip install ttkbootstrap' for a modern look.")

# --- Global Variables ---
# Threading events and references
stop_ffmpeg_flag = threading.Event()
ffmpeg_process_ref = None
log_queue = queue.Queue() # Thread-safe queue for log messages

# --- FFmpeg Logic ---

def validate_inputs(m3u8_url, subscriber_id, subscriber_code, rtmp_output):
    """Validates user inputs."""
    errors = []
    warnings = []

    if not all([m3u8_url, subscriber_id, subscriber_code, rtmp_output]):
        errors.append("All fields are required!")

    def is_valid_url(url_string, schemes=['http', 'https']):
        try:
            result = urllib.parse.urlparse(url_string)
            return all([result.scheme, result.netloc]) and result.scheme in schemes
        except Exception:
            return False

    if m3u8_url and not is_valid_url(m3u8_url, schemes=['http', 'https']):
        warnings.append("M3U8 URL might not be valid.")
    if rtmp_output and not is_valid_url(rtmp_output, schemes=['rtmp']):
        warnings.append("RTMP Output URL might not be valid.")

    return errors, warnings

def build_ffmpeg_command(m3u8_url, subscriber_id, subscriber_code, rtmp_output):
    """Constructs the FFmpeg command as a list of arguments."""
    m3u8_url = m3u8_url.strip()
    subscriber_id = subscriber_id.strip()
    subscriber_code = subscriber_code.strip()
    rtmp_output = rtmp_output.strip()

    input_url = f"{m3u8_url}?subscriberId={subscriber_id}&subscriberCode={subscriber_code}"

    # Match the command from the provided .bat file exactly
    command = [
        "ffmpeg", # Assumes ffmpeg is in PATH
        "-user_agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "-referer", "https://sgmc6.live/",
        "-i", input_url,
        "-c:v", "copy", "-c:a", "copy",
        "-f", "flv",
        "-flvflags", "no_duration_filesize",
        "-strict", "experimental",
        rtmp_output
    ]
    return command

def log_message(message, level="INFO"):
    """Thread-safe way to add messages to the log queue."""
    timestamp = time.strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] [{level}] {message}\n"
    log_queue.put(formatted_message)

def process_log_queue(text_widget):
    """Processes messages in the log queue and updates the text widget."""
    try:
        while True: # Process all available messages
            message = log_queue.get_nowait()
            text_widget.config(state=tk.NORMAL) # Enable editing
            text_widget.insert(tk.END, message)
            text_widget.see(tk.END) # Auto-scroll to the end
            text_widget.config(state=tk.DISABLED) # Disable editing
    except queue.Empty:
        pass
    # Schedule the next check
    text_widget.after(100, process_log_queue, text_widget)


def run_ffmpeg_loop(m3u8_url, subscriber_id, subscriber_code, rtmp_output, log_text_widget):
    """Runs the FFmpeg command in a loop directly from Python."""
    global ffmpeg_process_ref
    errors, warnings = validate_inputs(m3u8_url, subscriber_id, subscriber_code, rtmp_output)

    if errors:
        messagebox.showerror("Input Error", "\n".join(errors))
        return

    for warning in warnings:
        messagebox.showwarning("Input Warning", warning)

    def ffmpeg_loop_thread():
        global ffmpeg_process_ref
        cmd = build_ffmpeg_command(m3u8_url, subscriber_id, subscriber_code, rtmp_output)

        log_message("Starting FFmpeg loop...", "INFO")

        while not stop_ffmpeg_flag.is_set():
            try:
                log_message(f"Executing: {' '.join(shlex.quote(arg) for arg in cmd)}", "CMD")
                # Start FFmpeg process
                ffmpeg_process_ref = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )

                # Read output line by line
                for line in iter(ffmpeg_process_ref.stdout.readline, ''):
                    if line.strip():
                        log_message(line.strip(), "FFMPEG")

                # Wait for process to finish
                return_code = ffmpeg_process_ref.wait()
                ffmpeg_process_ref = None

                if return_code != 0:
                    log_message(f"FFmpeg exited with code {return_code}.", "ERROR")
                    log_message("Retrying in 5 seconds...", "INFO")
                    for _ in range(5):
                        if stop_ffmpeg_flag.is_set():
                            log_message("FFmpeg loop stopped by user.", "INFO")
                            return
                        time.sleep(1)
                else:
                    log_message("Stream ended cleanly. Restarting...", "INFO")

                if not stop_ffmpeg_flag.is_set():
                    time.sleep(1) # Small delay before restart

            except FileNotFoundError:
                error_msg = "FFmpeg not found. Please ensure 'ffmpeg' is installed and in your system's PATH."
                log_message(error_msg, "CRITICAL")
                messagebox.showerror("Error", error_msg)
                break
            except Exception as e:
                error_msg = f"Failed to start/run FFmpeg: {type(e).__name__}: {e}"
                log_message(error_msg, "ERROR")
                log_message("Retrying in 5 seconds...", "INFO")
                for _ in range(5):
                    if stop_ffmpeg_flag.is_set():
                        log_message("FFmpeg loop stopped by user.", "INFO")
                        return
                    time.sleep(1)

        log_message("FFmpeg loop thread finished.", "INFO")

    # Reset the stop flag before starting
    stop_ffmpeg_flag.clear()
    # Run the loop in a separate thread
    thread = threading.Thread(target=ffmpeg_loop_thread, name="FFmpegLoopThread")
    thread.daemon = True
    thread.start()
    messagebox.showinfo("FFmpeg Started", "FFmpeg loop has started. Check the log area for details.")

def stop_ffmpeg():
    """Signals the FFmpeg loop to stop."""
    global ffmpeg_process_ref
    if stop_ffmpeg_flag.is_set(): # Already stopping/ stopped
         log_message("Stop signal already sent or FFmpeg is not running.", "INFO")
         return

    stop_ffmpeg_flag.set()
    log_message("Sending stop signal to FFmpeg loop...", "INFO")
    if ffmpeg_process_ref and ffmpeg_process_ref.poll() is None:
        try:
            ffmpeg_process_ref.terminate()
            log_message("Sent terminate signal to FFmpeg process.", "INFO")
            # Optionally wait for a short time for graceful termination
            # try:
            #     ffmpeg_process_ref.wait(timeout=2)
            # except subprocess.TimeoutExpired:
            #     ffmpeg_process_ref.kill()
            #     ffmpeg_process_ref.wait()
            # log_message("FFmpeg process terminated/killed.", "INFO")
        except Exception as e:
            log_message(f"Could not send terminate signal: {e}", "WARNING")
    # messagebox.showinfo("FFmpeg Stop", "Stop signal sent. FFmpeg loop should terminate shortly.")

# --- GUI Setup ---
def create_gui():
    # Initialize the main window
    if USE_TTK_BOOTSTRAP:
        # Use ttkbootstrap with a modern theme
        root = ttk.Window(themename="darkly") # Try themes like 'cosmo', 'flatly', 'journal', 'darkly', 'superhero'
        style = ttk.Style()
        # You can configure specific styles if needed
        # style.configure('TButton', foreground='white', background='blue')
    else:
        root = tk.Tk()
        root.configure(bg='gray85') # Basic background color fallback

    root.title("FFmpeg Stream Relay")
    root.geometry("900x600") # Set a larger initial size
    root.minsize(700, 500) # Allow resizing but set minimum size

    # --- Input Frame ---
    input_frame = ttk.LabelFrame(root, text="Configuration", padding=(10, 5))
    input_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

    # Store entry widgets
    entries = {}

    # M3U8 URL
    ttk.Label(input_frame, text="Base M3U8 URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
    entries['m3u8'] = ttk.Entry(input_frame)
    entries['m3u8'].grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2, columnspan=3)
    entries['m3u8'].insert(0, "https://swarm.lucky23s.com/mechveil/streams/aztaroth14.m3u8")

    # Subscriber ID
    ttk.Label(input_frame, text="Subscriber ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
    entries['subscriber_id'] = ttk.Entry(input_frame)
    entries['subscriber_id'].grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
    entries['subscriber_id'].insert(0, "s60A10176749")

    # Subscriber Code
    ttk.Label(input_frame, text="Subscriber Code:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
    entries['subscriber_code'] = ttk.Entry(input_frame)
    entries['subscriber_code'].grid(row=1, column=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)

    # RTMP Output URL
    ttk.Label(input_frame, text="RTMP Output URL:").grid(row=2, column=0, sticky=tk.W, pady=2)
    entries['rtmp'] = ttk.Entry(input_frame)
    entries['rtmp'].grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2, columnspan=3)
    entries['rtmp'].insert(0, "rtmp://127.0.0.1/live/stream")

    # Configure grid weights for resizing within the frame
    input_frame.columnconfigure(1, weight=1)
    input_frame.columnconfigure(3, weight=1)

    # --- Buttons Frame ---
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    def on_start():
        run_ffmpeg_loop(
            entries['m3u8'].get(),
            entries['subscriber_id'].get(),
            entries['subscriber_code'].get(),
            entries['rtmp'].get(),
            log_text # Pass the log text widget
        )

    def on_stop():
        stop_ffmpeg()

    # Start Button
    start_button = ttk.Button(button_frame, text="Start FFmpeg Loop", command=on_start, bootstyle="SUCCESS")
    start_button.pack(side=tk.LEFT, padx=(0, 5))

    # Stop Button
    stop_button = ttk.Button(button_frame, text="Stop FFmpeg", command=on_stop, bootstyle="DANGER")
    stop_button.pack(side=tk.LEFT, padx=(5, 0))

    # Spacer to push notes to the right or center if desired
    # button_frame.columnconfigure(2, weight=1)
    # ttk.Label(button_frame, text=" ").grid(row=0, column=2, padx=20) # Invisible spacer

    # --- Log Frame ---
    log_frame = ttk.LabelFrame(root, text="Logs", padding=(5, 5))
    log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

    # Create a ScrolledText widget for logs
    log_text = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True)

    # Configure tags for different log levels (optional, for color coding)
    # This requires more setup and might conflict with ttkbootstrap themes
    # log_text.tag_config("INFO", foreground="blue")
    # log_text.tag_config("ERROR", foreground="red")
    # log_text.tag_config("CMD", foreground="green")

    # Start the log processing loop
    process_log_queue(log_text)

    # --- Notes ---
    note_frame = ttk.Frame(root)
    note_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    note_text = (
        "Notes: Ensure 'ffmpeg' is in PATH. Source might block automated access. "
        "Check logs for FFmpeg output/status. The 'sgmc6.live' example often blocks."
    )
    # Use a smaller label or adjust font if needed
    note_label = ttk.Label(note_frame, text=note_text, foreground='gray50', font=('Arial', 8))
    note_label.pack(side=tk.LEFT)

    # Handle window closing
    def on_closing():
        if not stop_ffmpeg_flag.is_set():
             if messagebox.askokcancel("Quit", "Stop FFmpeg and quit?"):
                 stop_ffmpeg()
                 root.destroy()
        else:
             root.destroy() # If already stopping, just close

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

if __name__ == "__main__":
    print("Starting FFmpeg Stream Relay GUI...")
    create_gui()
