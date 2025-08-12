#!/usr/bin/env python3
"""
Headset Audio Controller with GUI
Provides volume control and audio enhancement features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import subprocess
import platform

# Try to import audio libraries
try:
    import pycaw
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import pyaudio
    import numpy as np
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

class AudioController:
    def __init__(self):
        self.volume_interface = None
        self.current_volume = 0.5
        self.enhancement_enabled = False
        self.compressor_enabled = True
        self.limiter_enabled = True
        self.eq_enabled = False
        
        # Audio enhancement parameters
        self.compressor_threshold = 0.7
        self.compressor_ratio = 3.0
        self.limiter_threshold = 0.9
        self.bass_boost = 1.2
        self.treble_boost = 1.1
        
        self.setup_audio_interface()
    
    def setup_audio_interface(self):
        """Initialize audio interface based on platform"""
        if platform.system() == "Windows" and PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = interface.QueryInterface(IAudioEndpointVolume)
                return True
            except Exception as e:
                print(f"Windows audio setup failed: {e}")
                return False
        return False
    
    def set_system_volume(self, volume):
        """Set system volume (0.0 to 1.0)"""
        try:
            if platform.system() == "Windows" and self.volume_interface:
                self.volume_interface.SetMasterScalarVolume(volume, None)
                return True
            elif platform.system() == "Darwin":  # macOS
                # Use osascript to control volume
                volume_percent = int(volume * 100)
                subprocess.run(['osascript', '-e', f'set volume output volume {volume_percent}'])
                return True
            elif platform.system() == "Linux":
                # Use amixer to control volume
                volume_percent = int(volume * 100)
                subprocess.run(['amixer', 'sset', 'Master', f'{volume_percent}%'])
                return True
        except Exception as e:
            print(f"Volume control error: {e}")
            return False
        return False
    
    def get_system_volume(self):
        """Get current system volume"""
        try:
            if platform.system() == "Windows" and self.volume_interface:
                return self.volume_interface.GetMasterScalarVolume()
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(['osascript', '-e', 'output volume of (get volume settings)'], 
                                      capture_output=True, text=True)
                return float(result.stdout.strip()) / 100.0
            elif platform.system() == "Linux":
                result = subprocess.run(['amixer', 'get', 'Master'], capture_output=True, text=True)
                # Parse amixer output for volume percentage
                for line in result.stdout.split('\n'):
                    if 'Playback' in line and '[' in line:
                        start = line.find('[') + 1
                        end = line.find('%]')
                        if start > 0 and end > start:
                            return float(line[start:end]) / 100.0
        except Exception as e:
            print(f"Get volume error: {e}")
        return 0.5
    
    def apply_audio_enhancement(self, audio_data):
        """Apply audio enhancements to prevent distortion at high volumes"""
        if not isinstance(audio_data, np.ndarray):
            return audio_data
            
        enhanced_audio = audio_data.copy()
        
        # Dynamic Range Compression
        if self.compressor_enabled:
            enhanced_audio = self.apply_compressor(enhanced_audio)
        
        # Limiting to prevent clipping
        if self.limiter_enabled:
            enhanced_audio = self.apply_limiter(enhanced_audio)
        
        # EQ adjustments
        if self.eq_enabled:
            enhanced_audio = self.apply_eq(enhanced_audio)
        
        return enhanced_audio
    
    def apply_compressor(self, audio_data):
        """Apply dynamic range compression"""
        threshold = self.compressor_threshold
        ratio = self.compressor_ratio
        
        # Simple compression algorithm
        compressed = np.copy(audio_data)
        mask = np.abs(compressed) > threshold
        
        excess = np.abs(compressed[mask]) - threshold
        compressed[mask] = np.sign(compressed[mask]) * (threshold + excess / ratio)
        
        return compressed
    
    def apply_limiter(self, audio_data):
        """Apply limiting to prevent clipping"""
        threshold = self.limiter_threshold
        
        # Hard limiting
        limited = np.clip(audio_data, -threshold, threshold)
        return limited
    
    def apply_eq(self, audio_data):
        """Apply basic EQ (simplified)"""
        # This is a simplified EQ - in practice you'd use proper DSP
        # Boost bass and treble slightly
        eq_audio = audio_data * self.bass_boost * 0.3 + audio_data * self.treble_boost * 0.3 + audio_data * 0.4
        return np.clip(eq_audio, -1.0, 1.0)

class AudioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Headset Audio Controller")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.audio_controller = AudioController()
        self.create_widgets()
        self.update_current_volume()
        
        # Start volume monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_volume, daemon=True)
        self.monitor_thread.start()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10, fill='x')
        
        title_label = ttk.Label(title_frame, text="🎧 Headset Audio Controller", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Volume Control Section
        volume_frame = ttk.LabelFrame(self.root, text="Volume Control", padding=10)
        volume_frame.pack(pady=10, padx=20, fill='x')
        
        # Current volume display
        self.volume_var = tk.StringVar(value="Current Volume: 50%")
        volume_display = ttk.Label(volume_frame, textvariable=self.volume_var, 
                                  font=('Arial', 12))
        volume_display.pack(pady=5)
        
        # Volume slider
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=100, 
                                     orient='horizontal', length=400,
                                     command=self.on_volume_change)
        self.volume_scale.pack(pady=10, fill='x')
        
        # Quick volume buttons
        button_frame = ttk.Frame(volume_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="25%", width=8,
                  command=lambda: self.set_volume_percent(25)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="50%", width=8,
                  command=lambda: self.set_volume_percent(50)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="75%", width=8,
                  command=lambda: self.set_volume_percent(75)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="MAX", width=8,
                  command=lambda: self.set_volume_percent(100)).pack(side='left', padx=2)
        
        # Audio Enhancement Section
        enhance_frame = ttk.LabelFrame(self.root, text="Audio Enhancement", padding=10)
        enhance_frame.pack(pady=10, padx=20, fill='x')
        
        # Enable enhancement checkbox
        self.enhancement_var = tk.BooleanVar(value=True)
        enhance_check = ttk.Checkbutton(enhance_frame, text="Enable Audio Enhancement",
                                       variable=self.enhancement_var,
                                       command=self.toggle_enhancement)
        enhance_check.pack(anchor='w', pady=5)
        
        # Enhancement options
        options_frame = ttk.Frame(enhance_frame)
        options_frame.pack(fill='x', pady=5)
        
        # Compressor
        self.compressor_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Dynamic Compression",
                       variable=self.compressor_var,
                       command=self.update_compressor).pack(anchor='w')
        
        # Limiter
        self.limiter_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Audio Limiter",
                       variable=self.limiter_var,
                       command=self.update_limiter).pack(anchor='w')
        
        # EQ
        self.eq_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Bass/Treble Boost",
                       variable=self.eq_var,
                       command=self.update_eq).pack(anchor='w')
        
        # Advanced Settings
        advanced_frame = ttk.LabelFrame(self.root, text="Advanced Settings", padding=10)
        advanced_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Compressor threshold
        ttk.Label(advanced_frame, text="Compression Threshold:").pack(anchor='w')
        self.comp_threshold_var = tk.DoubleVar(value=70)
        comp_scale = ttk.Scale(advanced_frame, from_=50, to=90, 
                              orient='horizontal', variable=self.comp_threshold_var,
                              command=self.update_comp_threshold)
        comp_scale.pack(fill='x', pady=2)
        
        # Compressor ratio
        ttk.Label(advanced_frame, text="Compression Ratio:").pack(anchor='w')
        self.comp_ratio_var = tk.DoubleVar(value=3.0)
        ratio_scale = ttk.Scale(advanced_frame, from_=1.0, to=10.0, 
                               orient='horizontal', variable=self.comp_ratio_var,
                               command=self.update_comp_ratio)
        ratio_scale.pack(fill='x', pady=2)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x', padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
        
        # Check system compatibility
        if not self.check_compatibility():
            self.status_var.set("⚠️ Limited functionality - install pycaw (Windows) for full features")
    
    def check_compatibility(self):
        """Check if audio libraries are available"""
        system = platform.system()
        if system == "Windows" and not PYCAW_AVAILABLE:
            messagebox.showwarning("Missing Dependency", 
                                 "For full Windows functionality, install: pip install pycaw")
            return False
        elif system in ["Darwin", "Linux"]:
            self.status_var.set("Using system audio controls")
            return True
        return True
    
    def on_volume_change(self, value):
        """Handle volume slider changes"""
        volume_percent = float(value)
        self.set_volume_percent(volume_percent)
    
    def set_volume_percent(self, percent):
        """Set volume by percentage"""
        volume = percent / 100.0
        if self.audio_controller.set_system_volume(volume):
            self.volume_var.set(f"Current Volume: {int(percent)}%")
            self.status_var.set(f"Volume set to {int(percent)}%")
        else:
            self.status_var.set("Failed to set volume")
    
    def update_current_volume(self):
        """Update the volume display with current system volume"""
        current_vol = self.audio_controller.get_system_volume()
        percent = int(current_vol * 100)
        self.volume_scale.set(percent)
        self.volume_var.set(f"Current Volume: {percent}%")
    
    def monitor_volume(self):
        """Monitor volume changes in background"""
        while self.monitoring:
            try:
                current_vol = self.audio_controller.get_system_volume()
                percent = int(current_vol * 100)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.volume_scale.set(percent))
                self.root.after(0, lambda: self.volume_var.set(f"Current Volume: {percent}%"))
                
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
    
    def toggle_enhancement(self):
        """Toggle audio enhancement"""
        self.audio_controller.enhancement_enabled = self.enhancement_var.get()
        status = "enabled" if self.enhancement_var.get() else "disabled"
        self.status_var.set(f"Audio enhancement {status}")
    
    def update_compressor(self):
        """Update compressor setting"""
        self.audio_controller.compressor_enabled = self.compressor_var.get()
    
    def update_limiter(self):
        """Update limiter setting"""
        self.audio_controller.limiter_enabled = self.limiter_var.get()
    
    def update_eq(self):
        """Update EQ setting"""
        self.audio_controller.eq_enabled = self.eq_var.get()
    
    def update_comp_threshold(self, value):
        """Update compression threshold"""
        self.audio_controller.compressor_threshold = float(value) / 100.0
    
    def update_comp_ratio(self, value):
        """Update compression ratio"""
        self.audio_controller.compressor_ratio = float(value)

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Set up the GUI
    app = AudioGUI(root)
    
    # Handle window closing
    def on_closing():
        app.monitoring = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        app.monitoring = False

if __name__ == "__main__":
    print("Headset Audio Controller")
    print("=" * 30)
    print("Requirements:")
    print("- Windows: pip install pycaw")
    print("- macOS/Linux: Built-in system commands")
    print("- Optional: pip install pyaudio numpy (for audio processing)")
    print()
    
    main()
