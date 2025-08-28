Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import mss
import numpy as np
import mido
import time

# --------------------------
# Launchpad X MIDI setup
# --------------------------
outport = mido.open_output("Launchpad X MIDI 1")  # Adjust if needed

def set_pad_rgb(x, y, r, g, b):
    """
    Send RGB SysEx to Launchpad X pad (x,y) with colour (r,g,b).
    Grid: x=0..7, y=0..7
    """
    # Launchpad pad indexing (0–99 range depending on mode)
    pad_index = y * 10 + x  # Simplified mapping
    sysex = [
        0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x03,
        pad_index,
        r, g, b,
        0xF7
    ]
    msg = mido.Message('sysex', data=sysex)
    outport.send(msg)

# --------------------------
# Screen capture setup
# --------------------------
sct = mss.mss()
monitor = sct.monitors[1]  # primary screen

# Keep track of current colours for fading
current_colors = np.zeros((8, 8, 3), dtype=int)

def get_grid_colors():
    """
    Divide screen into 8x8 grid, compute average colour for each cell.
...     Returns 8x8x3 array.
...     """
...     img = np.array(sct.grab(monitor))
...     h, w, _ = img.shape
...     cell_h, cell_w = h // 8, w // 8
...     grid_colors = np.zeros((8, 8, 3), dtype=int)
... 
...     for y in range(8):
...         for x in range(8):
...             region = img[y*cell_h:(y+1)*cell_h, x*cell_w:(x+1)*cell_w, :3]
...             avg = region.mean(axis=(0,1))
...             grid_colors[y, x] = avg
...     return grid_colors
... 
... def fade_step(current, target, speed=0.2):
...     """
...     Smooth fade: move current towards target.
...     speed = 0..1 (higher = faster change)
...     """
...     return current + (target - current) * speed
... 
... # --------------------------
... # Main Loop
... # --------------------------
... try:
...     while True:
...         target_colors = get_grid_colors()
...         global current_colors
...         current_colors = fade_step(current_colors, target_colors)
... 
...         # Send to Launchpad
...         for y in range(8):
...             for x in range(8):
...                 r, g, b = current_colors[y, x].astype(int)
...                 set_pad_rgb(x, y, r, g, b)
... 
...         time.sleep(0.05)  # ~20 FPS
... except KeyboardInterrupt:
...     print("Stopped")
