import mido
import os
import sys

def ticks_to_beats(ticks, ticks_per_beat):
    return ticks / ticks_per_beat

def extract_sheet_from_midi(file_path):
    mid = mido.MidiFile(file_path)
    ticks_per_beat = mid.ticks_per_beat
    current_tempo = 500000  # Default tempo
    sheet_lines = []
    time_in_beats = 0
    last_abs_tick = 0

    merged_tracks = mido.merge_tracks(mid.tracks)

    for msg in merged_tracks:
        last_abs_tick += msg.time
        time_in_beats += ticks_to_beats(msg.time, ticks_per_beat)

        if msg.type == 'set_tempo':
            current_tempo = msg.tempo
            bpm = int(mido.tempo2bpm(current_tempo))
            sheet_lines.append(f"tempo= {bpm}")

        elif msg.type == 'note_on' and msg.velocity > 0:
            beat_time = round(time_in_beats, 2)
            sheet_lines.append(f"{beat_time} {msg.note}")

    return sheet_lines

def list_midi_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith(".mid")]

def main():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    midi_files = list_midi_files(base_dir)

    if not midi_files:
        print("No MIDI files found in the current directory.")
        return

    print("Available MIDI files:")
    for idx, filename in enumerate(midi_files):
        print(f"[{idx}] {filename}")

    while True:
        try:
            choice = int(input("Select a MIDI file by number: "))
            if 0 <= choice < len(midi_files):
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")

    selected_file = midi_files[choice]
    file_path = os.path.join(base_dir, selected_file)
    print(f"Processing: {selected_file}")

    sheet = extract_sheet_from_midi(file_path)

    with open("sheet_output.txt", "w") as f:
        f.write("\n".join(sheet))

    print("✅ Sheet music saved to 'sheet_output.txt'.")

if __name__ == "__main__":
    main()
