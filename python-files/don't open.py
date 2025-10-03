import tkinter as tk
import subprocess
import random
import sys

def close_lively():
    """Close Lively Wallpaper"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'lively.exe'], 
                      capture_output=True, check=False)
        subprocess.run(['taskkill', '/F', '/IM', 'Lively.exe'], 
                      capture_output=True, check=False)
        subprocess.run(['taskkill', '/F', '/IM', 'LivelyWallpaper.exe'], 
                      capture_output=True, check=False)
    except Exception as e:
        print(f"Error closing Lively: {e}")

def flash_colors():
    """Create fullscreen window that flashes colors"""
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.configure(cursor='none')
    
    # Color list
    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', 
              '#FF00FF', '#00FFFF', '#FFA500', '#800080',
              '#FF1493', '#00FF7F', '#FFD700', '#FF4500']
    

    
    def change_color():
        color = random.choice(colors)
        root.configure(bg=color)
        label.configure(bg=color)
        root.after(50, change_color)  # Flash every 50ms
    
    def exit_program(event=None):
        root.destroy()
        sys.exit()
    
    root.bind('<Escape>', exit_program)
    root.bind('<q>', exit_program)
    
    change_color()
    root.mainloop()

if __name__ == "__main__":
    print("Closing Lively Wallpaper...")
    close_lively()
    print("Starting color flash... Press ESC to exit")
    flash_colors()
