import configparser
import struct
import csv
from pathlib import Path

# === SETTINGS ===
FOLDER = Path(".")        # Folder containing all DATA_174.* files
INI_FILE = FOLDER / "DATA_174.INI"
OUTPUT_CSV = FOLDER / "output.csv"

# === STEP 1: Parse INI file ===
config = configparser.ConfigParser()
config.optionxform = str  # preserve case
config.read(INI_FILE)

channels = []
for key in config:
    if key.startswith("Chan"):
        ch = config[key]
        channels.append({
            "name": ch["Name"],
            "bit": int(ch["Bit"]),
            "freq": int(ch["Freq"]),
            "unit": ch["Unit"],
            "file": FOLDER / f"DATA_174.{ch['Name']}"
        })

# === STEP 2: Read binary data ===
channel_data = {}
max_samples = 0

for ch in channels:
    filename = ch["file"]
    if not filename.exists():
        continue
    with open(filename, "rb") as f:
        data = f.read()
        # 8-bit or 16-bit values
        if ch["bit"] == 8:
            values = list(struct.unpack(f"{len(data)}B", data))
        elif ch["bit"] == 16:
            count = len(data) // 2
            values = list(struct.unpack(f"<{count}H", data))
        else:
            continue

    channel_data[ch["name"]] = values
    if len(values) > max_samples:
        max_samples = len(values)

# === STEP 3: Write to CSV ===
with open(OUTPUT_CSV, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Header
    writer.writerow(["Time(s)"] + [f"{c['name']} ({c['unit']})" for c in channels if c["name"] in channel_data])

    # Determine max frequency (to create common time axis)
    max_freq = max(c["freq"] for c in channels if c["name"] in channel_data)
    
    for i in range(max_samples):
        t = i / max_freq
        row = [f"{t:.3f}"]
        for c in channels:
            vals = channel_data.get(c["name"], [])
            if i < len(vals):
                row.append(vals[i])
            else:
                row.append("")
        writer.writerow(row)

print(f"✅ Done. CSV created at: {OUTPUT_CSV}")
s