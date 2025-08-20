import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
import re
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

# ------------------------------
# Helper functions
# ------------------------------

def safe_rename(f: Path, new_name: str):
    try:
        new_path = f.parent / (new_name + f.suffix)
        if new_path.exists():
            new_path = f.parent / (new_name + "_1" + f.suffix)
        f.rename(new_path)
        return new_path
    except Exception as e:
        print(f"Rename error: {e}")
        return None

def read_id3_quiet(f: Path):
    try:
        tags = EasyID3(f)
        artist = tags.get("artist", ["UnknownArtist"])[0]
        title = tags.get("title", [f.stem])[0]
        genre = tags.get("genre", ["UnknownGenre"])[0]
        bpm = tags.get("bpm", [None])[0]
        return artist, genre, bpm
    except Exception:
        return "UnknownArtist", "UnknownGenre", None

def parse_filename_to_tags(f: Path, pattern: str):
    # Simple example: split by ' - ' -> artist - title
    if ' - ' in f.stem:
        artist, title = f.stem.split(' - ', 1)
    else:
        artist, title = "UnknownArtist", f.stem
    try:
        tags = EasyID3(f)
        tags['artist'] = artist
        tags['title'] = title
        tags.save()
    except Exception:
        pass

def tags_to_filename(f: Path, pattern: str):
    artist, genre, bpm = read_id3_quiet(f)
    title = EasyID3(f).get('title', [f.stem])[0]
    new_name = pattern.replace("%artist%", artist).replace("%title%", title)
    return safe_rename(f, new_name) or f

def bpm_bucket(bpm):
    try:
        bpm = int(bpm)
        return f"{(bpm//10)*10}-{(bpm//10)*10+9}"
    except:
        return "Unknown"

# ------------------------------
# Core processing function
# ------------------------------

def process_files(root_folder: Path, mode: str, bpm_only: bool,
                  fname_pattern: str, tag_pattern: str,
                  do_fname2tag: bool, do_tag2fname: bool, do_sort: bool,
                  do_cleanup: bool, cleanup_patterns: str, cleanup_replacement: str,
                  preview: bool = False, log: list[str] = None):

    mp3s = list(root_folder.rglob("*.mp3"))
    if not mp3s:
        return ["No MP3 files found."]
    patterns = [p.strip() for p in cleanup_patterns.split(",") if p.strip()]
    log = log or []

    for f in mp3s:
        try:
            original_name = f.name
            actions = []

            # Regex cleanup
            if do_cleanup and patterns:
                new_name = f.stem
                for pat in patterns:
                    try:
                        new_name = re.sub(pat, cleanup_replacement, new_name, flags=re.IGNORECASE)
                    except re.error:
                        continue
                new_name = re.sub(r"\s+", " ", new_name).strip()
                if not new_name:
                    new_name = "untitled"
                if new_name != f.stem:
                    actions.append(f"Regex cleanup: {f.name} → {new_name}")
                    if not preview:
                        f = safe_rename(f, new_name) or f

            # Filename → Tag
            if do_fname2tag and fname_pattern:
                actions.append(f"Filename → Tag: {f.name}")
                if not preview:
                    parse_filename_to_tags(f, fname_pattern)

            # Tag → Filename
            if do_tag2fname and tag_pattern:
                actions.append(f"Tag → Filename: {f.name}")
                if not preview:
                    f = tags_to_filename(f, tag_pattern) or f

            # Sorting
            if do_sort:
                artist, genre, bpm_tag = read_id3_quiet(f)
                bpm = bpm_tag if bpm_tag else None
                if mode == "BPM":
                    target_dir = root_folder / "Sorted" / "BPM" / (bpm_bucket(bpm) if bpm else "Unknown")
                elif mode == "Artist":
                    target_dir = root_folder / "Sorted" / "Artist" / artist
                elif mode == "Genre":
                    target_dir = root_folder / "Sorted" / "Genre" / genre
                else:
                    target_dir = root_folder / "Sorted" / "Unsorted"
                actions.append(f"Would move {f.name} → {target_dir}")
                if not preview:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    f.rename(target_dir / f.name)

            if actions:
                log.append(f"{original_name}:\n  " + "\n  ".join(actions))

        except Exception as e:
            log.append(f"Error processing {f.name}: {e}")
            continue

    return log

# ------------------------------
# GUI App
# ------------------------------

class MP3SorterApp:
    def __init__(self, root):
        self.root = root
        root.title("MP3 Sorter")
        frm = ttk.Frame(root, padding=10)
        frm.grid()

        # Folder
        ttk.Label(frm, text="Root Folder").grid(row=0, column=0, sticky="w")
        self.folder_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.folder_var, width=50).grid(row=1, column=0, sticky="we")
        ttk.Button(frm, text="Browse", command=self.browse_folder).grid(row=1, column=1)

        # Mode
        ttk.Label(frm, text="Sort Mode").grid(row=2, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="BPM")
        ttk.Combobox(frm, textvariable=self.mode_var, values=["BPM", "Artist", "Genre"]).grid(row=3, column=0, sticky="we")

        # Cleanup
        ttk.Label(frm, text="Regex Cleanup Patterns (comma-separated)").grid(row=4, column=0, sticky="w")
        self.cleanup_words = tk.StringVar()
        ttk.Entry(frm, textvariable=self.cleanup_words, width=50).grid(row=5, column=0, sticky="we")

        ttk.Label(frm, text="Replacement").grid(row=6, column=0, sticky="w")
        self.cleanup_replacement = tk.StringVar()
        ttk.Entry(frm, textvariable=self.cleanup_replacement, width=50).grid(row=7, column=0, sticky="we")

        ttk.Label(frm, text="Filename → Tag Pattern").grid(row=8, column=0, sticky="w")
        self.fname_pattern = tk.StringVar(value="%artist% - %title%")
        ttk.Entry(frm, textvariable=self.fname_pattern, width=50).grid(row=9, column=0, sticky="we")

        ttk.Label(frm, text="Tag → Filename Pattern").grid(row=10, column=0, sticky="w")
        self.tag_pattern = tk.StringVar(value="%artist% - %title%")
        ttk.Entry(frm, textvariable=self.tag_pattern, width=50).grid(row=11, column=0, sticky="we")

        # Options
        self.do_fname2tag = tk.BooleanVar(value=True)
        self.do_tag2fname = tk.BooleanVar(value=True)
        self.do_sort = tk.BooleanVar(value=True)
        self.do_cleanup = tk.BooleanVar(value=True)
        self.preview = tk.BooleanVar(value=True)

        ttk.Checkbutton(frm, text="Filename → Tag", variable=self.do_fname2tag).grid(row=12, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Tag → Filename", variable=self.do_tag2fname).grid(row=13, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Regex Cleanup", variable=self.do_cleanup).grid(row=14, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Sorting", variable=self.do_sort).grid(row=15, column=0, sticky="w")
        ttk.Checkbutton(frm, text="Preview Mode", variable=self.preview).grid(row=16, column=0, sticky="w")

        # Test Regex
        ttk.Label(frm, text="Sample filename for regex test").grid(row=17, column=0, sticky="w")
        self.sample_input = tk.StringVar()
        ttk.Entry(frm, textvariable=self.sample_input, width=44).grid(row=18, column=0, sticky="we")
        self.test_output = tk.StringVar()
        ttk.Button(frm, text="Test Regex", command=self.test_regex).grid(row=19, column=0, sticky="w", pady=(5,0))
        ttk.Label(frm, textvariable=self.test_output, foreground="blue").grid(row=20, column=0, sticky="w", pady=(5,0))

        # Run Button
        ttk.Button(frm, text="Run", command=self.run).grid(row=21, column=0, sticky="we", pady=(10,0))

        # Preview Log
        self.preview_log = tk.Text(frm, height=15, width=70)
        self.preview_log.grid(row=22, column=0, columnspan=2, sticky="we", pady=(10,0))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def test_regex(self):
        sample = self.sample_input.get().strip()
        patterns = [p.strip() for p in self.cleanup_words.get().split(",") if p.strip()]
        replacement = self.cleanup_replacement.get().strip()
        if not sample:
            self.test_output.set("⚠️ Enter a sample filename first.")
            return
        result = sample
        for pat in patterns:
            try:
                result = re.sub(pat, replacement, result, flags=re.IGNORECASE)
            except re.error as e:
                self.test_output.set(f"❌ Invalid regex: {pat} ({e})")
                return
        result = re.sub(r"\s+", " ", result).strip()
        if not result:
            result = "untitled"
        self.test_output.set(f"✅ Result: {result}")

    def run(self):
        folder = Path(self.folder_var.get())
        if not folder.exists():
            self.preview_log.insert(tk.END, "❌ Folder does not exist.\n")
            return
        self.preview_log.delete("1.0", tk.END)
        log = process_files(
            root_folder=folder,
            mode=self.mode_var.get(),
            bpm_only=False,
            fname_pattern=self.fname_pattern.get(),
            tag_pattern=self.tag_pattern.get(),
            do_fname2tag=self.do_fname2tag.get(),
            do_tag2fname=self.do_tag2fname.get(),
            do_sort=self.do_sort.get(),
            do_cleanup=self.do_cleanup.get(),
            cleanup_patterns=self.cleanup_words.get(),
            cleanup_replacement=self.cleanup_replacement.get(),
            preview=self.preview.get()
        )
        self.preview_log.insert(tk.END, "\n".join(log))
        self.preview_log.see(tk.END)

# ------------------------------
# Run the GUI
# ------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3SorterApp(root)
    root.mainloop()
