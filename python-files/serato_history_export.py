import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import csv

# Pot do tvoje Serato History mape
HISTORY_DIR = r"G:\untitled folder\_Serato_\History"

def parse_session_file(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        return [song.attrib.get('Name') for song in root.iter('Song') if song.attrib.get('Name')]
    except Exception as e:
        print(f"Napaka pri branju {filepath}: {e}")
        return []

track_counter = defaultdict(int)

for file in os.listdir(HISTORY_DIR):
    if file.endswith('.session'):
        full_path = os.path.join(HISTORY_DIR, file)
        tracks = parse_session_file(full_path)
        for track in tracks:
            track_counter[track] += 1

output_file = 'serato_history_top_tracks.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Število predvajanj', 'Naziv skladbe'])
    for track, count in sorted(track_counter.items(), key=lambda x: x[1], reverse=True):
        writer.writerow([count, track])

print(f"Izvoz končan! CSV je shranjen kot: {output_file}")
input("Pritisni Enter za izhod...")
