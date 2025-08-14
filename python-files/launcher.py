#!/usr/bin/env python3
import os
import subprocess
import stat
import sys

scriptdir = os.path.dirname(os.path.realpath(__file__))

# Go to game folder
game_dir = os.path.join(scriptdir, "game")
try:
    os.chdir(game_dir)
except FileNotFoundError:
    sys.exit(1)

# Set permissions to 0700
for root, dirs, files in os.walk(game_dir):
    for d in dirs:
        os.chmod(os.path.join(root, d), 0o700)
    for f in files:
        os.chmod(os.path.join(root, f), 0o700)

# Run setup if pinned_libs_64 is missing
pinned_libs = os.path.join(game_dir, "steam-runtime", "pinned_libs_64")
if not os.path.isdir(pinned_libs):
    subprocess.run([os.path.join(game_dir, "steam-runtime", "setup.sh")])

# Run the game
subprocess.run([os.path.join(game_dir, "steam-runtime", "run.sh"), "./dowser"])
