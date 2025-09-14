import subprocess
import re

# Your koboldcpp command (you can edit if needed)
command = [
    "koboldcpp.exe",
    "--hordekey", "00hiFGa_XGO2CCPD0UCxuw",
    "--hordeworkername", "Model",
    "--hordemodelname", "L3-8B-Stheno-v3.2",
    "--hordegenlen", "1024",
    "--debugmode"
]

# Regex patterns to catch messages
user_pattern = re.compile(r"User:\s*(.*)", re.IGNORECASE)
ai_pattern = re.compile(r"Response:\s*(.*)", re.IGNORECASE)

# Run koboldcpp and capture stdout in real time
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

print("=== Clean KoboldCPP Horde Viewer ===")
print("Capturing only User Inputs and AI Outputs...\n")

for line in process.stdout:
    line = line.strip()

    # Match user messages
    user_match = user_pattern.search(line)
    if user_match:
        print(f"\n[User] {user_match.group(1)}")
        continue

    # Match AI responses
    ai_match = ai_pattern.search(line)
    if ai_match:
        print(f"[AI] {ai_match.group(1)}")
        continue

# If process exits
process.wait()
