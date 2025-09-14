#!/usr/bin/env python3
"""
Hacker-style green terminal with "word upar aur niche".
Save as hacker_terminal.py and run with: python3 hacker_terminal.py
Works on Unix terminals and Windows (if ANSI supported). Use Ctrl-C to exit.
"""
import os
import sys
import time
import random
import shutil
import math

# Optional: try to enable ANSI on Windows (modern Windows terminals support it)
if os.name == "nt":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# ANSI color codes
GREEN = "\033[92m"      # bright green
DIM_GREEN = "\033[2;32m"  # dim green (if supported)
RESET = "\033[0m"
CLEAR = "\033[2J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
MOVE = lambda r, c: f"\033[{r};{c}H"

# Characters for the rain
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()[]{}<>?/|\\-+=~"

def get_size():
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines

def build_rain_state(width, height):
    # Each column has a "drop" y position and a speed
    drops = []
    for _ in range(width):
        # -1 means no active drop currently
        drops.append({
            "y": random.randint(-height, 0),
            "speed": random.choice([1,1,1,2]),  # mostly slow, some faster
            "length": random.randint(3, height//2 or 3)
        })
    return drops

def render_frame(width, height, drops, target_word, t):
    # Create blank frame (list of list of chars)
    frame = [[" " for _ in range(width)] for _ in range(height)]

    # Draw rain
    for x in range(width):
        d = drops[x]
        d["y"] += d["speed"]
        # reset occasionally
        if d["y"] - d["length"] > height or random.random() < 0.005:
            d["y"] = random.randint(-height//3, 0)
            d["length"] = random.randint(3, max(3, height//2))
            d["speed"] = random.choice([1,1,1,2])

        # draw the column: from y-length..y
        for i in range(d["length"]):
            yy = d["y"] - i
            if 0 <= yy < height:
                frame[yy][x] = random.choice(CHARS)

    # compute center and oscillating offset for "upar/niche" effect
    center_row = height // 2
    # offset oscillates between -4 and +4
    offset = int(round(4 * math.sin(t/6.0)))
    top_row = max(1, center_row - 3 + offset)       # ensure within bounds
    bottom_row = min(height - 2, center_row + 3 - offset)

    # overlay the target_word centered horizontally at top_row and bottom_row
    w = target_word
    start_col = max(0, (width - len(w)) // 2)
    for i, ch in enumerate(w):
        c = start_col + i
        if 0 <= c < width:
            frame[top_row][c] = ch
            frame[bottom_row][c] = ch

    # convert to strings with coloring: make letters from rain dim green, overlay word bright green
    lines = []
    for r, row in enumerate(frame):
        line_chars = []
        for c, ch in enumerate(row):
            if ch == " ":
                line_chars.append(" ")
            else:
                # If this position coincides with target word, use bright green
                if (r == top_row or r == bottom_row) and start_col <= c < start_col + len(w):
                    line_chars.append(f"{GREEN}{ch}{RESET}")
                else:
                    # dim or normal green for rain; make head slightly brighter randomly
                    if random.random() < 0.02:
                        line_chars.append(f"{GREEN}{ch}{RESET}")
                    else:
                        line_chars.append(f"{DIM_GREEN}{ch}{RESET}")
        lines.append("".join(line_chars))
    return lines

def main():
    # Read target word from CLI args or ask input
    if len(sys.argv) >= 2:
        target_word = " ".join(sys.argv[1:])
    else:
        target_word = input("Enter the word to show (appears upar & niche): ").strip() or "HACKER"

    try:
        print(CLEAR + HIDE_CURSOR, end="")
        sys.stdout.flush()
        cols, rows = get_size()
        drops = build_rain_state(cols, rows)
        t = 0.0
        while True:
            # check terminal resize
            new_cols, new_rows = get_size()
            if new_cols != cols or new_rows != rows:
                cols, rows = new_cols, new_rows
                drops = build_rain_state(cols, rows)

            frame_lines = render_frame(cols, rows, drops, target_word, t)
            # move cursor to top-left and print
            print(MOVE(1, 1), end="")
            for ln in frame_lines:
                # truncate/pad to width
                raw = ln
                # remove ANSI resets for length calculation: crude approach by slicing to cols characters
                # Simpler: print then newline; if longer than terminal it will wrap — acceptable.
                print(raw)
            t += 1
            time.sleep(0.07)
    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR + RESET)
        sys.exit(0)

if __name__ == "__main__":
    main()
