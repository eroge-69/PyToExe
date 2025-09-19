import pygame
import tempfile
import os
import base64
from tkinter import Tk, Button, Label, messagebox

class AudioHiderPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Hider Player")
        self.root.geometry("400x200")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create a temporary audio file
        self.create_audio_file()
        
        # Create UI
        self.label = Label(root, text="Click 'Play Audio' to hear the sound\nClick 'Hide Audio' to make the audio file disappear", 
                          wraplength=300, justify="center")
        self.label.pack(pady=20)
        
        self.play_button = Button(root, text="Play Audio", command=self.play_audio, height=2, width=15)
        self.play_button.pack(pady=5)
        
        self.hide_button = Button(root, text="Hide Audio", command=self.hide_audio, height=2, width=15)
        self.hide_button.pack(pady=5)
        
        self.audio_file_path = None
        self.audio_hidden = False

    def create_audio_file(self):
        """Create a temporary audio file with beep sounds"""
        try:
            # Create a temporary file
            self.audio_file_path = os.path.join(tempfile.gettempdir(), "hidden_audio.wav")
            
            # Generate a simple beep sound using pygame
            sample_rate = 44100
            duration = 0.1  # seconds
            frequency = 880  # Hz (A5 note)
            
            # Generate array of samples for the beep sound
            samples = []
            for i in range(int(duration * sample_rate)):
                sample = int(32767 * 0.5 * pygame.math.sin(2 * pygame.math.pi * frequency * i / sample_rate))
                samples.append(sample)
            
            # Create a sound from the samples
            sound = pygame.mixer.Sound(buffer=bytearray(samples))
            
            # Save the sound to a file
            pygame.mixer.Sound.save(sound, self.audio_file_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create audio file: {e}")

    def play_audio(self):
        """Play the audio file"""
        try:
            if self.audio_hidden:
                messagebox.showinfo("Info", "Audio is currently hidden. It will be recreated.")
                self.create_audio_file()
                self.audio_hidden = False
                
            if self.audio_file_path and os.path.exists(self.audio_file_path):
                pygame.mixer.music.load(self.audio_file_path)
                pygame.mixer.music.play()
                self.label.config(text="Playing audio...")
                # Schedule a check to update the label when audio stops
                self.root.after(1000, self.check_audio_status)
            else:
                messagebox.showerror("Error", "Audio file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio: {e}")

    def check_audio_status(self):
        """Check if audio is still playing and update the label"""
        if pygame.mixer.music.get_busy():
            self.root.after(100, self.check_audio_status)
        else:
            self.label.config(text="Audio finished playing")

    def hide_audio(self):
        """Hide the audio file from the user"""
        try:
            if self.audio_file_path and os.path.exists(self.audio_file_path):
                os.remove(self.audio_file_path)
                self.audio_hidden = True
                self.label.config(text="Audio file has been hidden!\nClick 'Play Audio' to recreate and play it.")
                messagebox.showinfo("Success", "Audio file has been hidden!")
            else:
                messagebox.showinfo("Info", "Audio file is already hidden")
        except Exception as e:
            messagebox.showerror("Error", f"Could not hide audio: {e}")

    def on_closing(self):
        """Cleanup when closing the application"""
        try:
            if self.audio_file_path and os.path.exists(self.audio_file_path):
                os.remove(self.audio_file_path)
        except:
            pass  # Ignore errors during cleanup
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = AudioHiderPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()