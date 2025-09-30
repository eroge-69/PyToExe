import os
from mutagen.wave import WAVE
import argparse
import struct
import pandas
from tkinter import Tk,filedialog

# -----------------------
# Parse command-line argument
# -----------------------
'''
parser = argparse.ArgumentParser(description="Extract info from WAV files in folder")
parser.add_argument("foldername", help="Path to the folder containing WAV files")
args = parser.parse_args()
folderName = args.foldername
'''


def extract_description(filename):
    with open(filename, "rb") as f:
        riff, size, ftype = struct.unpack("<4sI4s", f.read(12))
        if riff != b"RIFF" or ftype != b"WAVE":
            raise ValueError("Not a valid WAV file")

        while f.tell() < size + 8:
            header = f.read(8)
            if len(header) < 8:
                break
            chunk_id, chunk_size = struct.unpack("<4sI", header)
            chunk_id = chunk_id.decode(errors="ignore")
            data = f.read(chunk_size)

            if chunk_id == "bext":
                raw = data[:256].split(b"\x00", 1)[0]
                return raw.decode("cp1256", errors="ignore").strip()

            elif chunk_id == "DISP":
                raw = data[4:].split(b"\x00", 1)[0]
                return raw.decode("cp1256", errors="ignore").strip()

            if chunk_size % 2 == 1:
                f.seek(1, 1)

    return None

def extract_time_info(seconds: float) -> str:
    ms_total = int(round(seconds * 1000))         # total milliseconds (rounded)
    hours = ms_total // 3_600_000
    rem = ms_total % 3_600_000
    minutes = rem // 60_000
    rem = rem % 60_000
    secs = rem // 1000
    millis = rem % 1000
    return [f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}", hours, minutes, secs]


def main():
    # Hide Tkinter root window
    root = Tk()
    root.withdraw()

    # Ask user to pick a folder
    folderName = filedialog.askdirectory(title="Select folder with WAV files")
    if not folderName:
        print("No folder selected. Exiting.")
        return

    fnamesArray, authorsArray, descsArray, lengthsArray, hoursArray, minutesArray, secsArray, cd_numsArray, tracksArray = [], [], [], [], [], [], [], [], []

    for filename in os.listdir(folderName):
        if filename.endswith(".wav"):
            full_path = os.path.abspath(os.path.join(folderName, filename))
            audio = WAVE(full_path)
            tags = audio.tags or {}

            # Author (TPE1)
            author = ""
            if "TPE1" in tags:
                raw = tags["TPE1"].text[0]
                try:
                    author = raw.encode("latin1").decode("windows-1256")
                except:
                    author = raw

            desc = extract_description(full_path)
            audio_length = round(audio.info.length, 2)
            length, hours, minutes, secs = extract_time_info(audio_length)

            cd_num, track = filename[:-4].split("-")
            track = int(track)
            if track < 10:
                track = f"0{track}"

            fnamesArray.append(filename)
            authorsArray.append(author)
            descsArray.append(desc)
            lengthsArray.append(length)
            hoursArray.append(hours)
            minutesArray.append(minutes)
            secsArray.append(secs)
            cd_numsArray.append(cd_num)
            tracksArray.append(track)

    df = pandas.DataFrame({
        "Filename": fnamesArray,
        "Author": authorsArray,
        "Description": descsArray,
        "Length": lengthsArray,
        "Hours": hoursArray,
        "Minutes": minutesArray,
        "Seconds": secsArray,
        "CD_Num": cd_numsArray,
        "Track": tracksArray
    })

    df.to_csv("output_wav.txt", index=False)
    print("Data extracted and saved to output_wav.txt")

if __name__ == "__main__":
    main()