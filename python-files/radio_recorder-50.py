import os
import threading
import subprocess
import time

# Lijst van radiostations (Nederland & België) - stream URL's
radio_streams = {
    "NPO Radio 1": "http://icecast.omroep.nl/radio1-bb-mp3",
    "NPO Radio 2": "http://icecast.omroep.nl/radio2-bb-mp3",
    "NPO 3FM": "http://icecast.omroep.nl/3fm-bb-mp3",
    "Qmusic NL": "http://icecast-qmusic.cdp.triple-it.nl/Qmusic_nl_live_96.mp3",
    "Qmusic BE": "http://icecast.qmusic.be/Qmusic_be_live_96.mp3",
    "Studio Brussel": "http://icecast.vrtcdn.be/stubru-high.mp3",
    "MNM": "http://icecast.vrtcdn.be/mnm-high.mp3",
    "Joe BE": "http://icecast.qmusic.be/Joe_be_live_96.mp3",
    # Voeg tot 50 stations toe
}

output_dir = "recordings"
os.makedirs(output_dir, exist_ok=True)

# Gebruik FFmpeg om de stream op te nemen
def record_stream(name, url, duration=3600):  # standaard: 1 uur
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(output_dir, f"{name}_{timestamp}.mp3")
    command = [
        "ffmpeg",
        "-y",
        "-i", url,
        "-t", str(duration),
        "-acodec", "copy",
        filename
    ]
    print(f"Opname gestart voor: {name}")
    subprocess.run(command)
    print(f"Opname voltooid voor: {name}")

# Start opname voor alle streams
def start_recordings():
    threads = []
    for name, url in radio_streams.items():
        t = threading.Thread(target=record_stream, args=(name, url))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    start_recordings()
