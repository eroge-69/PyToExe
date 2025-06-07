import subprocess

def extract_chords(audio_path):
    """Uses Chordino plugin via Sonic Annotator to extract chords."""
    vamp_command = [
        "sonic-annotator",
        "-d", "vamp:nnls-chroma:chordino:chordino",
        audio_path,
        "-w", "csv",
        "--csv-stdout"
    ]
    result = subprocess.run(vamp_command, stdout=subprocess.PIPE, text=True)
    chords = []

    for line in result.stdout.strip().split("\n"):
        if line and not line.startswith("#"):
            parts = line.split(",")
            start_time = float(parts[0])
            chord = parts[2]
            chords.append((start_time, chord))

    return chords
