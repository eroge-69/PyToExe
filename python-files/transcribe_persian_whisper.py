import whisper
import os
from pathlib import Path

def transcribe_persian_audio(mp3_file_path, model_name="base", output_file="transcription.txt"):
    """
    Transcribe a Persian language MP3 file to Persian text using Whisper.
    
    Args:
        mp3_file_path (str): Path to the input MP3 file
        model_name (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        output_file (str): Path to save the transcription text
    """
    try:
        # Check if file exists and is an MP3
        if not os.path.exists(mp3_file_path):
            raise FileNotFoundError(f"MP3 file not found: {mp3_file_path}")
        if not mp3_file_path.lower().endswith('.mp3'):
            raise ValueError("File must be an MP3 file")

        # Load the Whisper model
        print(f"Loading Whisper model '{model_name}'...")
        model = whisper.load_model(model_name)

        # Transcribe the audio file
        print(f"Transcribing {mp3_file_path}...")
        result = model.transcribe(mp3_file_path, language="fa")  # 'fa' for Persian

        # Extract the transcribed text
        transcribed_text = result["text"]
        print("\nTranscription:")
        print(transcribed_text)

        # Save the transcription to a file
        output_path = os.path.join(os.path.dirname(mp3_file_path), output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcribed_text)
        print(f"\nTranscription saved to {output_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    # Prompt user for MP3 file path
    mp3_path = input("Enter the path to the MP3 file (e.g., C:\\path\\to\\audio.mp3): ").strip()
    transcribe_persian_audio(mp3_path, model_name="base", output_file="persian_transcription.txt")

if __name__ == "__main__":
    main()