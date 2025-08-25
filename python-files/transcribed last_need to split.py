import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
import os
import argparse
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator

# List of languages supported for transcription and translation
languages = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'ru': 'Russian',
    'pl': 'Polish',
    'hi': 'Hindi',
    'tr': 'Turkish',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'pa': 'Punjabi',
    'or': 'Odia (Oriya)',
    'ur': 'Urdu',
    'as': 'Assamese',
    'ma': 'Maithili',
    'bh': 'Bhojpuri',
    'sd': 'Sindhi',
    'ne': 'Nepali',
    'si': 'Sinhala'
}

def transcribe_audio(audio_path, src_lang='en', target_lang='en'):
    # Create recognizer instance
    recognizer = sr.Recognizer()

    # If the file is MP3, print message and return
    if audio_path.endswith(".mp3"):
        print(f"Error: {audio_path} is in MP3 format. Please convert it to WAV and rerun the script.")
        return

    with sr.AudioFile(audio_path) as source:
        print(f"Processing {audio_path}...")
        audio_data = recognizer.record(source)

        try:
            # Transcribe the audio
            transcription = recognizer.recognize_google(audio_data, language=src_lang)
            print(f"Transcription in {src_lang}: {transcription}")

            # Save the transcription to a text file
            transcribed_filename = os.path.basename(audio_path).replace('.wav',
                                                                        f'_{src_lang}_transcription.txt')
            transcribed_file_path = os.path.join('Transcribed_Data', transcribed_filename)

            if not os.path.exists('Transcribed_Data'):
                os.makedirs('Transcribed_Data')

            with open(transcribed_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Transcription ({src_lang}):\n{transcription}\n")

            print(f"Transcription saved to: {transcribed_file_path}")

            # Translate the transcription
            translator = Translator()
            translated_text = translator.translate(transcription, src=src_lang, dest=target_lang)
            print(f"Translated to {target_lang}: {translated_text.text}")

            # Save the translated text to a separate file
            translated_filename = os.path.basename(audio_path).replace('.wav',
                                                                       f'_{src_lang}_to_{target_lang}_translation.txt')
            translated_file_path = os.path.join('Transcribed_Data', translated_filename)

            with open(translated_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Translation ({target_lang}):\n{translated_text.text}\n")

            print(f"Translation saved to: {translated_file_path}")

            return transcription, translated_text.text

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def process_directory(directory, src_lang, target_lang, specific_file=None):
    if specific_file:
        file_path = os.path.join(directory, specific_file)
        if os.path.exists(file_path):
            print(f"\nProcessing specific file: {specific_file}")
            transcribe_audio(file_path, src_lang, target_lang)
        else:
            print(f"File {specific_file} not found in {directory}")
    else:
        for filename in os.listdir(directory):
            if filename.endswith(".wav"):  # Process only WAV files
                file_path = os.path.join(directory, filename)
                print(f"\nProcessing file: {filename}")
                transcribe_audio(file_path, src_lang, target_lang)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Transcribe and Translate Audio Files.")
    parser.add_argument("src_lang", help="Source language code (e.g., 'en', 'fr', 'hi')")
    parser.add_argument("dest_lang", help="Destination language code (e.g., 'en', 'fr', 'es')")
    parser.add_argument("action", help="Action: 'all' to process all files, 'file' to specify a file",
                        choices=['all', 'file'])
    parser.add_argument("--specific_file", help="Specify a particular file to process (only for action 'file')")
    args = parser.parse_args()

    # Audio folder
    audio_folder = 'Audio_Files'  # Fixed folder path
    if not os.path.exists(audio_folder):
        print(f"Folder '{audio_folder}' does not exist.")
        exit(1)

    # Get language codes from arguments
    src_lang = args.src_lang
    target_lang = args.dest_lang

    # Process based on action
    if args.action == 'all':
        process_directory(audio_folder, src_lang, target_lang)
    elif args.action == 'file':
        if args.specific_file:
            process_directory(audio_folder, src_lang, target_lang, args.specific_file)
        else:
            print("You must specify a file with --specific_file for action 'file'")
            exit(1)

if __name__ == "__main__":
    main()
