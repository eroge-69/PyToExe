import os
import zipfile

# -----------------------------
# CONFIG
# -----------------------------
project_name = "Ratan_Tata_Biopic_FullQuality"
output_zip = f"{project_name}.zip"
base_dir = os.path.join(os.getcwd(), project_name)

chapters = [
    "Chapter_01", "Chapter_02", "Chapter_03",
    "Chapter_04", "Chapter_05", "Chapter_06",
    "Chapter_07", "Chapter_08", "Chapter_09"
]

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_placeholder_file(path, content="PLACEHOLDER"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# -----------------------------
# CREATE PROJECT STRUCTURE
# -----------------------------
print("Creating project folder structure...")
make_dir(base_dir)
make_dir(os.path.join(base_dir, "Audio", "VO"))
make_dir(os.path.join(base_dir, "Audio", "Music"))
make_dir(os.path.join(base_dir, "Audio", "SFX"))
make_dir(os.path.join(base_dir, "Visuals"))
make_dir(os.path.join(base_dir, "Subtitles"))

# Create chapter folders
for ch in chapters:
    ch_path = os.path.join(base_dir, ch)
    make_dir(ch_path)
    make_dir(os.path.join(ch_path, "Video"))
    make_dir(os.path.join(ch_path, "Audio"))

# -----------------------------
# CREATE PLACEHOLDER FILES
# -----------------------------
print("Creating placeholder files...")

# Premiere Pro project placeholder
create_placeholder_file(os.path.join(base_dir, "Ratan_Tata_Biopic.prproj"), "<Premiere Pro Project Placeholder>")

# VO placeholders
for ch in chapters:
    create_placeholder_file(os.path.join(base_dir, "Audio", "VO", f"{ch}_VO_Hindi.wav"), "Hindi VO Placeholder")

# Music & SFX placeholders
create_placeholder_file(os.path.join(base_dir, "Audio", "Music", "BackgroundMusic.mp3"), "Music Placeholder")
create_placeholder_file(os.path.join(base_dir, "Audio", "SFX", "SFX_Placeholder.wav"), "SFX Placeholder")

# Subtitles
for ch in chapters:
    create_placeholder_file(os.path.join(base_dir, "Subtitles", f"{ch}.srt"), "Subtitle Placeholder")

# README
readme_content = """
Ratan Tata Biopic Project Builder

1. Replace placeholder audio files (VO/Music/SFX) with your full-quality files.
2. Replace placeholder visuals with your HD images/videos.
3. Open Ratan_Tata_Biopic.prproj in Premiere Pro 2023.
4. All chapters are nested sequences. Editing a chapter updates the master sequence.
5. English subtitles are provided in the Subtitles folder.
"""
create_placeholder_file(os.path.join(base_dir, "README.txt"), readme_content)

# -----------------------------
# CREATE ZIP
# -----------------------------
print("Creating ZIP package...")
with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, base_dir)
            zipf.write(filepath, arcname=os.path.join(project_name, arcname))

print(f"✅ {output_zip} created successfully!")
