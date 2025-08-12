import re
import json
import os
from tkinter import Tk, filedialog

def srt_time_to_seconds(time_str):
    """Convert SRT time format (HH:MM:SS,mmm) to seconds (float)."""
    hours, minutes, seconds = re.split('[:,]', time_str)
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds + '.' + time_str.split(',')[1])

def srt_to_json(srt_path, json_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    pattern = re.compile(
        r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.+?)(?=\n\n|\Z)',
        re.DOTALL
    )
    results = []

    for match in pattern.finditer(srt_content):
        start_time = srt_time_to_seconds(match.group(2))
        end_time = srt_time_to_seconds(match.group(3))
        text = match.group(4).replace('\n', ' ').strip()
        results.append({
            "start": start_time,
            "end": end_time,
            "translation": text
        })

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# Hide the root Tkinter window
Tk().withdraw()

# Ask the user to select an SRT file
srt_file = filedialog.askopenfilename(
    title="Select SRT file",
    filetypes=[("SRT files", "*.srt")]
)

if srt_file:
    json_file = os.path.splitext(srt_file)[0] + ".json"
    srt_to_json(srt_file, json_file)
