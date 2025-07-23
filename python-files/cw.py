import time
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.playback import play

# Morse code mapping
MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.', 
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---', 
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---', 
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-', 
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--', 
    'Z': '--..',  '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', 
    '0': '-----', ' ': '/'
}

# Function to convert text to Morse code
def text_to_morse(text):
    return ' '.join(MORSE_CODE.get(char.upper(), '') for char in text)

# Function to generate sound for Morse code
def morse_to_sound(morse_code, dot_freq=300, dash_freq=800, unit_duration=1200):
    audio = AudioSegment.silent(duration=0)
    
    for symbol in morse_code:
        if symbol == '.':
            tone = Sine(dot_freq).to_audio_segment(duration=unit_duration)
            audio += tone
        elif symbol == '-':
            tone = Sine(dash_freq).to_audio_segment(duration=unit_duration * 3)
            audio += tone
        elif symbol == ' ':
            audio += AudioSegment.silent(duration=unit_duration)  # Space between letters
        audio += AudioSegment.silent(duration=unit_duration)  # Space between dots and dashes

    return audio

# Main function
def main():
    text = input("Enter text to convert to Morse code: ")
    morse_code = text_to_morse(text)
    print(f"Morse Code: {morse_code}")

    # Generate sound
    audio = morse_to_sound(morse_code)
    
    # Play the sound
    print("Playing Morse code sound...")
    play(audio)

if __name__ == "__main__":
    main()
