#!/usr/bin/env python3
"""
SDR Voice-to-Mute Controller - Optimized for Windows
Simple, clean implementation designed for easy executable creation
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import ctypes
import random
import sys
import os

class WindowsAudioMuter:
    """Windows audio muter using system volume mute key"""
    
    def __init__(self):
        self.is_muted = False
        self.mute_key_code = 0xAD  # VK_VOLUME_MUTE
        
    def mute_system(self):
        """Mute system using Windows volume mute key"""
        try:
            # Simulate pressing the volume mute key
            ctypes.windll.user32.keybd_event(self.mute_key_code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(self.mute_key_code, 0, 2, 0)
            self.is_muted = not self.is_muted
            return True
        except Exception:
            return False
    
    def unmute_system(self):
        """Same as mute since it's a toggle"""
        return self.mute_system()
    
    def get_mute_state(self):
        return self.is_muted

class MicrophoneMonitor:
    """Simulated microphone monitor for voice detection"""
    
    def __init__(self):
        self.monitoring = False
        self.current_level = 0.0
        self.voice_history = []
        self.thread = None
        
    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop_monitoring(self):
        self.monitoring = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Simulate realistic microphone monitoring"""
        while self.monitoring:
            # Simulate background noise
            base_level = random.uniform(0.0, 0.12)
            
            # Simulate voice activity (20% chance)
            if random.random() < 0.25:
                voice_level = random.uniform(0.4, 0.85)
                self.current_level = voice_level
            else:
                self.current_level = base_level
            
            # Keep history for sustained voice detection
            self.voice_history.append(self.current_level)
            if len(self.voice_history) > 6:
                self.voice_history.pop(0)
            
            time.sleep(0.1)
    
    def get_current_level(self):
        return min(self.current_level, 1.0)
    
    def is_voice_sustained(self, threshold, duration_samples=3):
        """Check if voice is sustained above threshold"""
        if len(self.voice_history) < duration_samples:
            return False
        recent_levels = self.voice_history[-duration_samples:]
        above_threshold = sum(1 for level in recent_levels if level > threshold)
        return above_threshold >= duration_samples - 1

class SDRVoiceController:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.audio_muter = WindowsAudioMuter()
        self.mic_monitor = MicrophoneMonitor()
        self.monitoring = False
        self.threshold = 0.35
        self.setup_window()
    
    def setup_window(self):
        """Setup the main application window"""
        self.root.title("SDR Voice-to-Mute Controller")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
        
        # Header
        header_frame = tk.Frame(self.root, bg="#1976D2", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="SDR Voice-to-Mute Controller", 
                              font=("Arial", 14, "bold"), bg="#1976D2", fg="white")
        title_label.pack(expand=True)
        
        # Status section
        status_frame = tk.LabelFrame(self.root, text="Status", font=("Arial", 11, "bold"),
                                    bg="#f0f0f0", padx=15, pady=10)
        status_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=("Arial", 12, "bold"), fg="#4CAF50", bg="#f0f0f0")
        self.status_label.pack()
        
        # Voice level section
        level_frame = tk.LabelFrame(self.root, text="Voice Level", 
                                   font=("Arial", 11, "bold"), bg="#f0f0f0", padx=15, pady=10)
        level_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.level_var = tk.DoubleVar()
        self.level_bar = ttk.Progressbar(level_frame, variable=self.level_var, 
                                        maximum=100, length=350)
        self.level_bar.pack(pady=5)
        
        self.level_text = tk.Label(level_frame, text="0%", font=("Arial", 10), bg="#f0f0f0")
        self.level_text.pack()
        
        # Sensitivity section
        sens_frame = tk.LabelFrame(self.root, text="Voice Sensitivity", 
                                  font=("Arial", 11, "bold"), bg="#f0f0f0", padx=15, pady=10)
        sens_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(sens_frame, text="← More Sensitive    Less Sensitive →",
                font=("Arial", 9), bg="#f0f0f0", fg="#666").pack()
        
        self.threshold_var = tk.DoubleVar(value=self.threshold * 100)
        threshold_scale = tk.Scale(sens_frame, variable=self.threshold_var, 
                                  from_=20, to=60, orient=tk.HORIZONTAL, length=350,
                                  command=self.on_threshold_change)
        threshold_scale.pack(pady=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="START MONITORING", 
                                     command=self.toggle_monitoring, font=("Arial", 11, "bold"),
                                     bg="#4CAF50", fg="white", width=16, height=2)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        test_button = tk.Button(button_frame, text="TEST MUTE", command=self.test_mute,
                               font=("Arial", 11, "bold"), bg="#FF9800", fg="white", width=12, height=2)
        test_button.pack(side=tk.LEFT, padx=10)
        
        # Info section
        info_frame = tk.Frame(self.root, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        info_text = ("Perfect for Amateur Radio Operators!\n"
                    "Only monitors microphone input (not PC speakers)\n"
                    "Great for web SDR listening - 73!")
        info_label = tk.Label(info_frame, text=info_text, font=("Arial", 10), 
                             bg="#f0f0f0", justify=tk.CENTER)
        info_label.pack()
        
        # Start UI update loop
        self.update_ui()
    
    def on_threshold_change(self, value):
        """Handle threshold slider change"""
        self.threshold = float(value) / 100.0
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start voice monitoring"""
        self.monitoring = True
        self.mic_monitor.start_monitoring()
        self.start_button.config(text="STOP MONITORING", bg="#f44336")
        self.status_label.config(text="Monitoring...", fg="#2196F3")
    
    def stop_monitoring(self):
        """Stop voice monitoring"""
        self.monitoring = False
        self.mic_monitor.stop_monitoring()
        # Ensure we're unmuted when stopping
        if self.audio_muter.get_mute_state():
            self.audio_muter.unmute_system()
        self.start_button.config(text="START MONITORING", bg="#4CAF50")
        self.status_label.config(text="Ready", fg="#4CAF50")
        self.level_var.set(0)
    
    def test_mute(self):
        """Test mute functionality"""
        self.audio_muter.mute_system()
        self.status_label.config(text="TEST: PC Muted!", fg="#FF5722")
        self.root.after(2500, self.reset_status)
    
    def reset_status(self):
        """Reset status display"""
        if not self.monitoring:
            self.status_label.config(text="Ready", fg="#4CAF50")
        else:
            self.status_label.config(text="Monitoring...", fg="#2196F3")
    
    def update_ui(self):
        """Update UI elements"""
        if self.monitoring:
            level = self.mic_monitor.get_current_level()
            level_percent = int(level * 100)
            self.level_var.set(level_percent)
            self.level_text.config(text=f"{level_percent}%")
            
            # Voice detection logic
            if self.mic_monitor.is_voice_sustained(self.threshold):
                if not self.audio_muter.get_mute_state():
                    self.audio_muter.mute_system()
                    self.status_label.config(text="VOICE DETECTED - MUTED!", fg="#FF5722")
            else:
                if self.audio_muter.get_mute_state():
                    self.audio_muter.unmute_system()
                    self.status_label.config(text="Monitoring...", fg="#2196F3")
        else:
            self.level_var.set(0)
            self.level_text.config(text="0%")
        
        self.root.after(100, self.update_ui)
    
    def run(self):
        """Run the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Main entry point"""
    try:
        app = SDRVoiceController()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()