import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment
from pathlib import Path
from PIL import Image, ImageTk
import json
import tempfile
import os
import random
import math

# Constants
FADE_DURATION = 3000  # 3 seconds
SUPPORTED_FORMATS = (".mp3", ".wav", ".flac", ".ogg", ".m4a")
SETTINGS_FILE = "settings.json"
LOGO_FILE = "logo.png"

# Modern compact color scheme
COLORS = {
    'bg_primary': '#0d1117',      # GitHub dark background
    'bg_secondary': '#161b22',     # Slightly lighter
    'bg_tertiary': '#21262d',     # Card background
    'accent': '#238636',          # GitHub green
    'accent_hover': '#2ea043',    # Lighter green
    'danger': '#da3633',          # Red
    'warning': '#fb8500',         # Orange
    'text_primary': '#f0f6fc',    # Light text
    'text_secondary': '#8b949e',  # Muted text
    'border': '#30363d',          # Subtle border
    'button_bg': '#21262d',       # Button background
    'button_hover': '#30363d',    # Button hover
}

# Load/save settings
def load_settings():
    if Path(SETTINGS_FILE).exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except:
        pass

settings = load_settings()
last_output_folder = settings.get("last_output", "")
last_duration = settings.get("last_duration", 2)

# Generate a unique file path
def get_unique_path(filepath):
    counter = 1
    original_path = filepath
    while filepath.exists():
        filepath = original_path.with_name(f"{original_path.stem} ({counter}){original_path.suffix}")
        counter += 1
    return filepath

# Audio processing - extract middle segment
def extract_middle_segment(file_path, duration_minutes):
    """Extract middle segment from audio file and return the processed audio"""
    try:
        # Load audio file
        audio = AudioSegment.from_file(file_path)
        
        # Calculate durations in milliseconds
        total_duration_needed = duration_minutes * 60000 + 2 * FADE_DURATION
        main_segment_duration = duration_minutes * 60000
        
        # Check if audio is long enough
        if len(audio) < total_duration_needed:
            raise ValueError(f"Audio file is too short. Need at least {total_duration_needed/1000:.1f} seconds, but file is only {len(audio)/1000:.1f} seconds.")
        
        # Calculate start position for middle segment
        start_pos = (len(audio) - main_segment_duration) // 2
        end_pos = start_pos + main_segment_duration
        
        # Extract middle segment
        segment = audio[start_pos:end_pos]
        
        # Apply fade in/out
        segment = segment.fade_in(FADE_DURATION).fade_out(FADE_DURATION)
        
        return segment
        
    except Exception as e:
        raise Exception(f"Error processing audio: {str(e)}")

# Export audio only
def export_audio_only(audio_segment, original_file_path, output_folder, duration_minutes):
    """Export just the audio segment"""
    try:
        # Create output filename
        original_name = Path(original_file_path).stem
        original_ext = Path(original_file_path).suffix
        output_filename = f"{original_name}_{duration_minutes}min_cut{original_ext}"
        output_path = Path(output_folder) / output_filename
        output_path = get_unique_path(output_path)
        
        # Export audio
        format_name = original_ext.lower().replace('.', '')
        if format_name == 'm4a':
            format_name = 'mp4'  # pydub uses mp4 for m4a
        
        audio_segment.export(str(output_path), format=format_name)
        
        return f"✅ Audio exported successfully to: {output_path.name}"
        
    except Exception as e:
        return f"❌ Audio export failed: {str(e)}"

# Generate complex video filter for motion graphics
def generate_motion_filter(duration_seconds, motion_type="dynamic"):
    """Generate FFmpeg filter for dynamic motion graphics"""
    
    if motion_type == "zoom_pulse":
        # Smooth zoom in/out with pulse effect
        return f"""
        [0:v]scale=1920:1080:force_original_aspect_ratio=increase,
        crop=1920:1080,
        zoompan=z='min(zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720,
        format=yuv420p[v1];
        [v1]scale=1280:720,
        eq=brightness=0.05*sin(2*PI*t/3):contrast=1+0.1*sin(2*PI*t/4)[v2]
        """
    
    elif motion_type == "glitch_zoom":
        # Glitch effect with zoom
        return f"""
        [0:v]scale=1920:1080:force_original_aspect_ratio=increase,
        crop=1920:1080,
        zoompan=z='1+0.3*sin(2*PI*t/8)':d=1:x='iw/2-(iw/zoom/2)+20*sin(2*PI*t/2)':y='ih/2-(ih/zoom/2)+15*cos(2*PI*t/3)':s=1280x720,
        noise=alls=10:allf=t+u:c0f=t:c1f=t:c2f=t,
        format=yuv420p[v1];
        [v1]datascope=s=1280x720:mode=color2:axis=1:opacity=0.1[v2];
        [v1][v2]blend=all_mode=overlay:all_opacity=0.1[v3];
        [v3]eq=brightness=0.1*sin(20*PI*t):contrast=1+0.2*random(0)[v4]
        """
    
    elif motion_type == "smooth_orbit":
        # Smooth orbital motion with scaling
        return f"""
        [0:v]scale=1600:1600:force_original_aspect_ratio=increase,
        crop=1600:1600,
        zoompan=z='1+0.2*sin(2*PI*t/10)':d=1:
        x='iw/2-(iw/zoom/2)+100*sin(2*PI*t/15)':
        y='ih/2-(ih/zoom/2)+100*cos(2*PI*t/15)':s=1280x720,
        format=yuv420p[v1];
        [v1]eq=brightness=0.05*sin(2*PI*t/5):saturation=1+0.1*sin(2*PI*t/7)[v2]
        """
    
    elif motion_type == "cyberpunk":
        # Cyberpunk-style glitch with RGB split
        return f"""
        [0:v]scale=1920:1080:force_original_aspect_ratio=increase,
        crop=1920:1080,
        zoompan=z='1.2+0.3*sin(2*PI*t/6)':d=1:
        x='iw/2-(iw/zoom/2)+30*sin(4*PI*t)':
        y='ih/2-(ih/zoom/2)':s=1280x720[v1];
        [v1]split=3[r][g][b];
        [r]lutrgb=r=val:g=0:b=0,pad=1285:720:5[r2];
        [g]lutrgb=r=0:g=val:b=0,pad=1285:720:0[g2];
        [b]lutrgb=r=0:g=0:b=val,pad=1285:720:-5[b2];
        [r2][g2]blend=all_mode=addition[rg];
        [rg][b2]blend=all_mode=addition,
        eq=brightness=0.1*sin(10*PI*t):contrast=1+0.3*random(0),
        format=yuv420p[v2]
        """
    
    else:  # dynamic (default)
        # Complex dynamic motion with multiple effects
        return f"""
        [0:v]scale=1920:1080:force_original_aspect_ratio=increase,
        crop=1920:1080,
        zoompan=z='1.1+0.4*sin(2*PI*t/12)+0.1*sin(8*PI*t)':d=1:
        x='iw/2-(iw/zoom/2)+50*sin(2*PI*t/8)+20*sin(6*PI*t)':
        y='ih/2-(ih/zoom/2)+50*cos(2*PI*t/10)+15*cos(4*PI*t)':s=1280x720,
        format=yuv420p[v1];
        [v1]eq=brightness=0.08*sin(2*PI*t/3)+0.03*sin(12*PI*t):
        contrast=1+0.15*sin(2*PI*t/5)+0.05*sin(16*PI*t):
        saturation=1+0.1*sin(2*PI*t/7)[v2]
        """

# Video export function using FFmpeg with motion graphics
def create_video_with_artwork(audio_segment, image_path, output_path, motion_type="dynamic", progress_callback=None):
    """Create video from audio segment and static image with motion graphics using FFmpeg"""
    try:
        import subprocess
        import shutil
        
        # Check if FFmpeg is available
        if not shutil.which("ffmpeg"):
            return create_video_with_moviepy_motion(audio_segment, image_path, output_path, motion_type, progress_callback)
        
        # Create temporary audio file
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        try:
            # Export audio segment to temporary file
            audio_segment.export(temp_audio_path, format="wav")
            
            if progress_callback:
                progress_callback(20)
            
            # Get audio duration
            duration = len(audio_segment) / 1000.0  # Convert to seconds
            
            if progress_callback:
                progress_callback(40)
            
            # Generate motion filter
            filter_complex = generate_motion_filter(duration, motion_type)
            
            # Use FFmpeg to create video with motion graphics
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file
                "-loop", "1",  # Loop the image
                "-i", image_path,  # Input image
                "-i", temp_audio_path,  # Input audio
                "-filter_complex", filter_complex,
                "-map", "[v2]" if motion_type != "cyberpunk" else "[v2]",  # Map the final video
                "-map", "1:a",  # Map the audio
                "-c:v", "libx264",  # Video codec
                "-c:a", "aac",  # Audio codec
                "-preset", "medium",  # Encoding preset
                "-crf", "23",  # Quality
                "-t", str(duration),  # Duration
                "-r", "30",  # Frame rate
                "-shortest",  # Stop when shortest input ends
                output_path
            ]
            
            if progress_callback:
                progress_callback(60)
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Fallback to simpler motion if complex filter fails
                return create_simple_motion_video(audio_segment, image_path, output_path, progress_callback)
            
            if progress_callback:
                progress_callback(100)
            
            return "✅ Video with motion graphics exported successfully!"
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        
    except Exception as e:
        # Try simpler motion as fallback
        return create_simple_motion_video(audio_segment, image_path, output_path, progress_callback)

# Simplified motion video creation as fallback
def create_simple_motion_video(audio_segment, image_path, output_path, progress_callback=None):
    """Create video with simple zoom motion as fallback"""
    try:
        import subprocess
        import shutil
        
        # Create temporary audio file
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        try:
            audio_segment.export(temp_audio_path, format="wav")
            duration = len(audio_segment) / 1000.0
            
            if progress_callback:
                progress_callback(70)
            
            # Simple zoom effect
            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-i", image_path,
                "-i", temp_audio_path,
                "-vf", f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.001,1.3)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720,format=yuv420p",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-t", str(duration),
                "-r", "24",
                "-shortest",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return create_video_with_moviepy_motion(audio_segment, image_path, output_path, "simple", progress_callback)
            
            if progress_callback:
                progress_callback(100)
            
            return "✅ Video with motion graphics exported successfully!"
            
        finally:
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        
    except Exception as e:
        return create_video_with_moviepy_motion(audio_segment, image_path, output_path, "simple", progress_callback)

# MoviePy fallback with motion graphics
def create_video_with_moviepy_motion(audio_segment, image_path, output_path, motion_type="simple", progress_callback=None):
    """Create video using MoviePy with motion effects as fallback"""
    try:
        # Try different import methods for MoviePy
        try:
            from moviepy import ImageClip, AudioFileClip
            from moviepy.video.fx import resize
        except ImportError:
            try:
                from moviepy.editor import ImageClip, AudioFileClip
                from moviepy.video.fx.all import resize
            except ImportError:
                raise Exception("MoviePy is not installed. Please install with: pip install moviepy")
        
        # Create temporary audio file
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        try:
            # Export audio segment to temporary file
            audio_segment.export(temp_audio_path, format="wav")
            
            if progress_callback:
                progress_callback(30)
            
            # Load audio clip
            audio_clip = AudioFileClip(temp_audio_path)
            duration = audio_clip.duration
            
            if progress_callback:
                progress_callback(50)
            
            # Create image clip with motion
            image_clip = ImageClip(image_path, duration=duration)
            
            # Apply motion effects based on type
            if motion_type == "zoom_pulse":
                # Zoom with pulse effect
                def zoom_pulse(get_frame, t):
                    zoom = 1.0 + 0.2 * math.sin(2 * math.pi * t / 8)
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h * zoom), int(w * zoom)
                    if new_h > h and new_w > w:
                        # Crop to original size from center
                        y_start = (new_h - h) // 2
                        x_start = (new_w - w) // 2
                        return frame[y_start:y_start+h, x_start:x_start+w]
                    return frame
                
                image_clip = image_clip.fl(zoom_pulse)
            
            # Resize to 720p
            image_clip = image_clip.resize(height=720)
            
            if progress_callback:
                progress_callback(75)
            
            # Set audio to image clip
            video_clip = image_clip.set_audio(audio_clip)
            
            # Write video file
            video_clip.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            if progress_callback:
                progress_callback(100)
            
            # Clean up
            audio_clip.close()
            video_clip.close()
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        
        return "✅ Video with motion graphics exported successfully!"
        
    except Exception as e:
        return f"❌ Video export failed: {str(e)}\n\nTry installing MoviePy with: pip install moviepy"

# Modern Compact GUI App with Motion Controls
class GrooveCutrApp:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("GrooveCutr Pro")
        self.app.geometry("520x850")  # Increased height for motion controls
        self.app.resizable(False, False)
        self.app.configure(bg=COLORS['bg_primary'])
        
        # Configure modern style
        self.setup_styles()
        
        # Variables
        self.selected_audio = tk.StringVar()
        self.selected_artwork = tk.StringVar()
        self.output_path_var = tk.StringVar(value=last_output_folder)
        self.duration_var = tk.IntVar(value=last_duration)
        self.motion_var = tk.StringVar(value="dynamic")
        
        self.create_widgets()
        
    def setup_styles(self):
        """Configure modern compact styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure main frame
        self.style.configure("Main.TFrame",
                           background=COLORS['bg_primary'],
                           relief="flat")
        
        # Configure section frames
        self.style.configure("Section.TFrame",
                           background=COLORS['bg_tertiary'],
                           relief="flat",
                           borderwidth=1)
        
        # Configure labels
        self.style.configure("Title.TLabel",
                           background=COLORS['bg_primary'],
                           foreground=COLORS['text_primary'],
                           font=("Inter", 18, "bold"))
        
        self.style.configure("Heading.TLabel",
                           background=COLORS['bg_tertiary'],
                           foreground=COLORS['text_primary'],
                           font=("Inter", 10, "bold"))
        
        self.style.configure("Body.TLabel",
                           background=COLORS['bg_primary'],
                           foreground=COLORS['text_secondary'],
                           font=("Inter", 9))
        
        self.style.configure("Status.TLabel",
                           background=COLORS['bg_primary'],
                           foreground=COLORS['text_secondary'],
                           font=("SF Pro Text", 9))
        
        # Configure buttons
        self.style.configure("Primary.TButton",
                           background=COLORS['accent'],
                           foreground="white",
                           font=("Inter", 9, "bold"),
                           padding=(12, 8),
                           relief="flat")
        
        self.style.map("Primary.TButton",
                      background=[("active", COLORS['accent_hover']),
                                ("pressed", COLORS['accent_hover'])])
        
        self.style.configure("Secondary.TButton",
                           background=COLORS['button_bg'],
                           foreground=COLORS['text_primary'],
                           font=("Inter", 9),
                           padding=(10, 6),
                           relief="flat")
        
        self.style.map("Secondary.TButton",
                      background=[("active", COLORS['button_hover']),
                                ("pressed", COLORS['button_hover'])])
        
        # Configure entries
        self.style.configure("Modern.TEntry",
                           font=("SF Mono", 9),
                           padding=6,
                           relief="flat")
        
        # Configure radiobuttons
        self.style.configure("Modern.TRadiobutton",
                           background=COLORS['bg_tertiary'],
                           foreground=COLORS['text_primary'],
                           font=("Inter", 9),
                           focuscolor='none')
        
        self.style.map("Modern.TRadiobutton",
                      background=[("active", COLORS['bg_secondary'])],
                      foreground=[("active", COLORS['text_primary'])])
        
        # Configure progress bar
        self.style.configure("Modern.Horizontal.TProgressbar",
                           background=COLORS['accent'],
                           troughcolor=COLORS['bg_secondary'],
                           borderwidth=0,
                           lightcolor=COLORS['accent'],
                           darkcolor=COLORS['accent'])
        
    def create_section(self, parent, title, compact=True):
        """Create a compact section"""
        section_frame = ttk.Frame(parent, style="Section.TFrame", padding=(15, 10))
        section_frame.pack(padx=15, pady=6, fill="x")
        
        if title:
            title_label = ttk.Label(section_frame, text=title, style="Heading.TLabel")
            title_label.pack(anchor="w", pady=(0, 8))
        
        return section_frame
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.app, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header - compact
        header_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        header_frame.pack(fill="x", pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="GrooveCutr Pro", style="Title.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Extract perfect audio segments with motion graphics", style="Body.TLabel")
        subtitle_label.pack(pady=(2, 0))
        
        # Audio file selection
        audio_section = self.create_section(main_frame, "🎵 Audio File")
        
        audio_frame = tk.Frame(audio_section, bg=COLORS['bg_tertiary'])
        audio_frame.pack(fill="x")
        
        audio_entry = ttk.Entry(audio_frame, textvariable=self.selected_audio, 
                               style="Modern.TEntry")
        audio_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ttk.Button(audio_frame, text="Browse", style="Secondary.TButton",
                  command=self.browse_audio).pack(side="right")
        
        # Duration selection - more compact
        duration_section = self.create_section(main_frame, "⏱️ Duration")
        
        ttk.Radiobutton(duration_section, 
                       text="1 min (Hip-Hop, Pop, Country)", 
                       variable=self.duration_var, 
                       value=1,
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        ttk.Radiobutton(duration_section, 
                       text="2 min (EDM, Electronic, House)", 
                       variable=self.duration_var, 
                       value=2,
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        # Artwork selection - compact
        artwork_section = self.create_section(main_frame, "🎨 Artwork")
        
        artwork_frame = tk.Frame(artwork_section, bg=COLORS['bg_tertiary'])
        artwork_frame.pack(fill="x")
        
        artwork_entry = ttk.Entry(artwork_frame, textvariable=self.selected_artwork, 
                                 style="Modern.TEntry")
        artwork_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ttk.Button(artwork_frame, text="Browse", style="Secondary.TButton",
                  command=self.browse_artwork).pack(side="right")
        
        # NEW: Motion Graphics Selection
        motion_section = self.create_section(main_frame, "🎬 Motion Graphics")
        
        ttk.Radiobutton(motion_section, 
                       text="Dynamic Motion (Recommended)", 
                       variable=self.motion_var, 
                       value="dynamic",
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        ttk.Radiobutton(motion_section, 
                       text="Smooth Zoom Pulse", 
                       variable=self.motion_var, 
                       value="zoom_pulse",
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        ttk.Radiobutton(motion_section, 
                       text="Glitch + Zoom", 
                       variable=self.motion_var, 
                       value="glitch_zoom",
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        ttk.Radiobutton(motion_section, 
                       text="Smooth Orbit", 
                       variable=self.motion_var, 
                       value="smooth_orbit",
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        ttk.Radiobutton(motion_section, 
                       text="Cyberpunk Style", 
                       variable=self.motion_var, 
                       value="cyberpunk",
                       style="Modern.TRadiobutton").pack(anchor='w', pady=2)
        
        # Output folder - compact
        folder_section = self.create_section(main_frame, "📁 Output Folder")
        
        folder_frame = tk.Frame(folder_section, bg=COLORS['bg_tertiary'])
        folder_frame.pack(fill="x")
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.output_path_var, 
                                style="Modern.TEntry")
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ttk.Button(folder_frame, text="Browse", style="Secondary.TButton",
                  command=self.select_output_folder).pack(side="right")
        
        # Progress section - compact
        progress_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        progress_frame.pack(pady=15, fill="x")
        
        self.progress = ttk.Progressbar(progress_frame, 
                                       orient="horizontal", 
                                       length=480, 
                                       mode="determinate",
                                       style="Modern.Horizontal.TProgressbar")
        self.progress.pack(pady=8)
        
        self.status_label = ttk.Label(progress_frame, 
                                     text="Ready to process audio", 
                                     style="Status.TLabel")
        self.status_label.pack()
        
        # Action buttons - compact layout
        button_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        button_frame.pack(pady=20)
        
        # Stack buttons vertically for better compact layout
        audio_btn = ttk.Button(button_frame, 
                              text="🎵 Export Audio Only", 
                              style="Primary.TButton",
                              width=25,
                              command=self.export_audio_only)
        audio_btn.pack(pady=4)
        
        video_btn = ttk.Button(button_frame, 
                              text="🎬 Export Video + Motion", 
                              style="Primary.TButton",
                              width=25,
                              command=self.export_video)
        video_btn.pack(pady=4)
        
        # Compact footer
        footer_frame = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        footer_frame.pack(side="bottom", pady=8)
        
        footer_text = ttk.Label(footer_frame, 
                               text="Extracts perfect middle segments with dynamic motion graphics",
                               style="Body.TLabel")
        footer_text.pack()
    
    def browse_audio(self):
        file = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.selected_audio.set(file)
    
    def browse_artwork(self):
        file = filedialog.askopenfilename(
            title="Select Artwork Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.selected_artwork.set(file)
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.output_path_var.get() or ".",
            title="Select Output Folder"
        )
        if folder:
            self.output_path_var.set(folder)
            settings["last_output"] = folder
            save_settings(settings)
    
    def update_progress(self, value):
        self.progress["value"] = value
        self.app.update_idletasks()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.app.update_idletasks()
    
    def validate_common_inputs(self):
        """Validate inputs common to both export modes"""
        audio_file = self.selected_audio.get()
        output_folder = self.output_path_var.get()
        
        if not audio_file:
            messagebox.showwarning("Missing Input", "Please select an audio file.")
            return None
        
        if not output_folder:
            messagebox.showwarning("Missing Input", "Please select an output folder.")
            return None
        
        if not Path(audio_file).exists():
            messagebox.showerror("File Error", "Selected audio file does not exist.")
            return None
        
        if not Path(output_folder).exists():
            messagebox.showerror("Folder Error", "Selected output folder does not exist.")
            return None
        
        return audio_file, output_folder
    
    def export_audio_only(self):
        """Export only the audio cut"""
        validation = self.validate_common_inputs()
        if not validation:
            return
        
        audio_file, output_folder = validation
        
        # Save settings
        duration_minutes = self.duration_var.get()
        settings["last_duration"] = duration_minutes
        save_settings(settings)
        
        # Reset progress
        self.progress["maximum"] = 100
        self.progress["value"] = 0
        
        try:
            # Extract middle segment from audio
            self.update_status("Processing audio file...")
            self.update_progress(30)
            
            audio_segment = extract_middle_segment(Path(audio_file), duration_minutes)
            
            self.update_status("Exporting audio file...")
            self.update_progress(70)
            
            # Export audio
            result = export_audio_only(audio_segment, audio_file, output_folder, duration_minutes)
            
            self.update_progress(100)
            
            if result.startswith("✅"):
                self.update_status("Audio exported successfully!")
                messagebox.showinfo("Success", result)
                self.selected_audio.set("")
            else:
                self.update_status("Failed to export audio.")
                messagebox.showerror("Error", result)
                self.progress["value"] = 0
                
        except Exception as e:
            self.update_status("Error occurred during processing.")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.progress["value"] = 0
    
    def export_video(self):
        """Export video with motion graphics"""
        validation = self.validate_common_inputs()
        if not validation:
            return
        
        audio_file, output_folder = validation
        artwork_file = self.selected_artwork.get()
        
        if not artwork_file:
            messagebox.showwarning("Missing Input", "Please select an artwork image for video export.")
            return
        
        if not Path(artwork_file).exists():
            messagebox.showerror("File Error", "Selected artwork file does not exist.")
            return
        
        # Save settings
        duration_minutes = self.duration_var.get()
        motion_type = self.motion_var.get()
        settings["last_duration"] = duration_minutes
        settings["last_motion"] = motion_type
        save_settings(settings)
        
        # Reset progress
        self.progress["maximum"] = 100
        self.progress["value"] = 0
        
        try:
            # Extract middle segment from audio
            self.update_status("Processing audio file...")
            self.update_progress(10)
            
            audio_segment = extract_middle_segment(Path(audio_file), duration_minutes)
            
            # Create output filename
            self.update_status("Preparing video export...")
            audio_name = Path(audio_file).stem
            motion_suffix = f"_{motion_type}" if motion_type != "dynamic" else ""
            output_filename = f"{audio_name}_{duration_minutes}min{motion_suffix}_video.mp4"
            output_path = Path(output_folder) / output_filename
            output_path = get_unique_path(output_path)
            
            # Create video with motion graphics
            self.update_status(f"Creating video with {motion_type} motion... This may take a while...")
            self.update_progress(20)
            
            result = create_video_with_artwork(
                audio_segment, 
                artwork_file, 
                str(output_path),
                motion_type,
                self.update_progress
            )
            
            if result.startswith("✅"):
                self.update_status("Video created successfully!")
                messagebox.showinfo("Success", f"Video created successfully!\n\nSaved to:\n{output_path}")
                
                # Clear inputs
                self.selected_audio.set("")
                self.selected_artwork.set("")
            else:
                self.update_status("Failed to create video.")
                messagebox.showerror("Error", result)
                self.progress["value"] = 0
                
        except Exception as e:
            self.update_status("Error occurred during processing.")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.progress["value"] = 0
    
    def run(self):
        self.app.mainloop()

# Run the application
if __name__ == "__main__":
    app = GrooveCutrApp()
    app.run()
