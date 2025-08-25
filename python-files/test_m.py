# benign_emulator.py  (for an isolated lab)
# Behaviors: creates temp file, spawns cmd that echoes a marker, and exits.

import os, subprocess, tempfile, time, base64

# Obfuscate the MARKER
MARKER = base64.b64decode("QkVOUklOX1RFU1RfVFRQXzEyMzQ1").decode('utf-8')

# Get the temporary directory
tmp = tempfile.gettempdir()

# Create a temporary file and write the MARKER to it
temp_file_path = os.path.join(tmp, "benign_drop.txt")
with open(temp_file_path, "w", encoding="utf-8") as f:
    f.write(MARKER)

# Simulate "suspicious" parent/child (python -> cmd)
subprocess.run(["cmd.exe", "/c", f"echo {MARKER} > {os.environ['TEMP']}\\benign_echo.txt"], shell=False)

# Optional small sleep to show runtime in EDR timelines
time.sleep(2)
print("Done.")