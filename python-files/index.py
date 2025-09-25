import pygetwindow
from pynput.keyboard import Controller
from multiprocessing import Process
import math
import time
import json
import os

# detect Sky window
windows = pygetwindow.getWindowsWithTitle("Sky")
sky = None
for window in windows:
    if window.title == "Sky":
        sky = window

if sky is None:
    print("Sky was not detected, please open Sky before running this script.")
    quit()

def focusWindow():
    try:
        sky.activate()
    except:
        sky.minimize()
        sky.restore()

keyboard = Controller()

# sky instrument mappings
key_maps = {
    '1Key0': 'y', '1Key1': 'u', '1Key2': 'i', '1Key3': 'o', '1Key4': 'p',
    '1Key5': 'h', '1Key6': 'j', '1Key7': 'k', '1Key8': 'l', '1Key9': ';',
    '1Key10': 'n', '1Key11': 'm', '1Key12': ',', '1Key13': '.', '1Key14': '/',
    '2Key0': 'y', '2Key1': 'u', '2Key2': 'i', '2Key3': 'o', '2Key4': 'p',
    '2Key5': 'h', '2Key6': 'j', '2Key7': 'k', '2Key8': 'l', '2Key9': ';',
    '2Key10': 'n', '2Key11': 'm', '2Key12': ',', '2Key13': '.', '2Key14': '/'
}

# progress bar display
def progress_bar(current, total, song_name, replace_line, bar_length=40):
    fraction = current / total
    current = round(current)
    total = round(total)

    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current >= total else '\r'

    msg = f'Now Playing: {song_name} [{arrow}{padding}] {math.floor(current/60)}:{math.floor(current%60):02}/{math.floor(total/60)}:{math.floor(total%60):02}'
    if replace_line == 0:
        print(msg)
    else:
        print(msg, end=ending)

# progress loop (runs in separate process)
def progress_loop(data):
    start_time = time.perf_counter()
    pause_time = 0
    elapsed_time = 0
    total = data[0]['songNotes'][-1]["time"] / 1000
    name = data[0]["name"]
    paused = 1
    while elapsed_time < total:
        if sky.isActive:
            elapsed_time = time.perf_counter() - start_time - pause_time
            progress_bar(elapsed_time, total, name, paused)
            paused = 1
            time.sleep(1)
        else:
            pause_start = time.perf_counter()
            while not sky.isActive:
                time.sleep(1)
            pause_time += time.perf_counter() - pause_start
            paused = 2

# play music function
def play_music(song_data):
    song_notes = song_data[0]['songNotes']
    song_notes.sort(key=lambda n: n["time"])  # safety sort

    start_time = time.perf_counter()
    pause_time = 0

    # start progress bar process
    p_loop = Process(target=progress_loop, args=(song_data,))
    p_loop.start()

    i = 0
    while i < len(song_notes):
        if sky.isActive:
            note_time = song_notes[i]['time']
            # group all notes with same timestamp
            same_time_notes = []
            while i < len(song_notes) and song_notes[i]['time'] == note_time:
                same_time_notes.append(song_notes[i])
                i += 1

            # wait until this note time
            elapsed = time.perf_counter() - start_time - pause_time
            wait_time = max(0, note_time / 1000 - elapsed)
            if wait_time > 0:
                time.sleep(wait_time)

            # press all notes
            for note in same_time_notes:
                if note['key'] in key_maps:
                    keyboard.press(key_maps[note['key']])
            time.sleep(0.02)  # small press duration
            for note in same_time_notes:
                if note['key'] in key_maps:
                    keyboard.release(key_maps[note['key']])
        else:
            print("Sky not focused, pausing...")
            pause_start = time.perf_counter()
            while not sky.isActive:
                time.sleep(1)
            pause_time += time.perf_counter() - pause_start
            print("Resuming...")

    p_loop.terminate()
    print(f"Finished playing {song_data[0]['name']}")

# main
if __name__ == '__main__':
    print("Please select a song with the corresponding number.")
    song_list = os.listdir("./songs/")

    for no, name in enumerate(song_list):
        if name.endswith(".json") or name.endswith(".skysheet"):
            print(f"{no+1}) {name.split('.')[0]}")

    selection = int(input("Please select a song: "))
    folder_name = "songs"

    if selection-1 in range(len(song_list)):
        try:
            with open(f'{folder_name}/{song_list[selection-1]}', 'r', encoding="utf-8") as file:
                song_data = json.load(file)
        except FileNotFoundError:
            print("Song not found.")
            quit()

        for i in range(3, 0, -1):
            print(f"Playing song in {i}")
            time.sleep(1)

        focusWindow()
        play_music(song_data)
    else:
        print("Invalid selection, exiting")
