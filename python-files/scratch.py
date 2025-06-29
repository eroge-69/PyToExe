import requests
import os
import glob

# --- Configuration ---
API_KEY = "sk_188936c21cffc2bbfaf78bd9b21958bd56af2c7f4e59fb2c"
VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"  # Josh – deep and motivational
CHUNK_SIZE = 1024
OUTPUT_BASE_NAME = "output"
SCRIPT_PATTERN = "looksmaxxing_script*.txt"

# --- Functions ---

def get_latest_script_file():
    script_files = glob.glob(SCRIPT_PATTERN)
    if not script_files:
        raise FileNotFoundError(f"No files matching pattern '{SCRIPT_PATTERN}' found.")
    return max(script_files, key=os.path.getmtime)

def read_file_text(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_unique_filename(base_name="output", extension=".mp3"):
    filename = f"{base_name}{extension}"
    counter = 1
    while os.path.exists(filename):
        filename = f"{base_name}_{counter}{extension}"
        counter += 1
    return filename

# --- Main Execution ---

try:
    script_file = get_latest_script_file()
    print(f"✅ Using script file: {script_file}")
    script_text = read_file_text(script_file)

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    payload = {
        "text": script_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8,
            "speed": 1.15  # a bit faster to sound more assertive
        }
    }

    response = requests.post(tts_url, headers=headers, json=payload)
    response.raise_for_status()

    output_file = get_unique_filename(OUTPUT_BASE_NAME)
    with open(output_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    print(f"✅ Motivational male voice saved as '{output_file}'")

except Exception as e:
    print(f"❌ Error: {e}")
