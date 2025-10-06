import sys
import subprocess
import os
import platform
import zipfile
import urllib.request
import shutil
import json

# Funzione per installare pacchetti Python
def install_package(package):
    try:
        __import__(package)
        return True
    except ImportError:
        print(f"Installazione del pacchetto {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            return True
        except subprocess.CalledProcessError:
            print(f"Errore nell'installazione di {package}")
            return False

# Funzione per verificare se ffmpeg è installato
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Funzione per installare ffmpeg automaticamente su Windows
def install_ffmpeg_windows():
    print("\n" + "="*60)
    print("INSTALLAZIONE FFMPEG")
    print("="*60)
    
    install_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ffmpeg')
    ffmpeg_bin = os.path.join(install_dir, 'bin')
    
    if os.path.exists(os.path.join(ffmpeg_bin, 'ffmpeg.exe')):
        print(f"✓ ffmpeg trovato in: {ffmpeg_bin}")
        return ffmpeg_bin
    
    print("ffmpeg non trovato. Installazione automatica in corso...")
    print("Questo richiederà qualche minuto...\n")
    
    try:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(os.environ.get('TEMP', ''), 'ffmpeg.zip')
        
        print("1/4 Download ffmpeg...")
        urllib.request.urlretrieve(url, zip_path)
        print("✓ Download completato")
        
        print("2/4 Estrazione file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.environ.get('TEMP', ''))
        print("✓ Estrazione completata")
        
        print("3/4 Installazione...")
        temp_dir = os.environ.get('TEMP', '')
        extracted_folder = None
        for item in os.listdir(temp_dir):
            if item.startswith('ffmpeg-') and os.path.isdir(os.path.join(temp_dir, item)):
                extracted_folder = os.path.join(temp_dir, item)
                break
        
        if extracted_folder:
            os.makedirs(install_dir, exist_ok=True)
            src_bin = os.path.join(extracted_folder, 'bin')
            if os.path.exists(src_bin):
                if os.path.exists(ffmpeg_bin):
                    shutil.rmtree(ffmpeg_bin)
                shutil.copytree(src_bin, ffmpeg_bin)
                print(f"✓ ffmpeg installato in: {install_dir}")
            shutil.rmtree(extracted_folder)
        
        os.remove(zip_path)
        
        print("4/4 Configurazione PATH...")
        os.environ['PATH'] = ffmpeg_bin + os.pathsep + os.environ['PATH']
        print("✓ PATH configurato per questa sessione")
        
        print("\n" + "="*60)
        print("✓ INSTALLAZIONE COMPLETATA!")
        print("="*60)
        
        return ffmpeg_bin
        
    except Exception as e:
        print(f"\n✗ Errore durante l'installazione: {e}")
        return None

# Funzione per scaricare il modello Vosk italiano
def download_vosk_model():
    model_dir = os.path.join(os.path.dirname(__file__), 'vosk-model-small-it-0.22')
    
    if os.path.exists(model_dir):
        print(f"✓ Modello Vosk trovato in: {model_dir}")
        return model_dir
    
    print("\n" + "="*60)
    print("DOWNLOAD MODELLO ITALIANO VOSK")
    print("="*60)
    print("Download del modello di riconoscimento vocale italiano...")
    print("Dimensione: ~40MB - Richiederà qualche minuto...\n")
    
    try:
        # URL del modello italiano piccolo (più veloce da scaricare)
        url = "https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip"
        zip_path = os.path.join(os.environ.get('TEMP', ''), 'vosk-model.zip')
        
        print("Download in corso...")
        
        # Download con progress bar
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, downloaded * 100 / total_size)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f'\r[{bar}] {percent:.1f}%', end='', flush=True)
        
        urllib.request.urlretrieve(url, zip_path, show_progress)
        print("\n✓ Download completato")
        
        print("Estrazione modello...")
        extract_dir = os.path.dirname(__file__)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("✓ Estrazione completata")
        
        os.remove(zip_path)
        
        print("\n" + "="*60)
        print("✓ MODELLO INSTALLATO!")
        print("="*60)
        
        return model_dir
        
    except Exception as e:
        print(f"\n✗ Errore durante il download: {e}")
        print("\nScarica manualmente:")
        print("1. Vai su: https://alphacephei.com/vosk/models")
        print("2. Scarica 'vosk-model-small-it-0.22.zip'")
        print("3. Estrai nella stessa cartella dello script")
        return None

# Setup automatico
print("="*60)
print("SETUP TRASCRITTORE OFFLINE")
print("="*60)

print("\nVerifica dipendenze Python...")
if not install_package("vosk"):
    sys.exit(1)
if not install_package("pydub"):
    sys.exit(1)

print("\nVerifica ffmpeg...")
if not check_ffmpeg():
    if platform.system() == "Windows":
        if not install_ffmpeg_windows():
            print("\n⚠ Impossibile installare ffmpeg.")
            sys.exit(1)
    else:
        print("Installa ffmpeg manualmente per supportare MP3")

print("\nVerifica modello vocale...")
model_path = download_vosk_model()
if not model_path:
    print("\n⚠ Impossibile scaricare il modello vocale.")
    sys.exit(1)

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import wave

# Funzione per convertire audio in formato WAV 16kHz mono
def convert_to_wav_16k(audio_file):
    wav_file = audio_file.rsplit(".", 1)[0] + "_16k.wav"
    
    try:
        print(f"\nCaricamento audio: {os.path.basename(audio_file)}")
        
        # Carica audio (supporta MP3, WAV, etc.)
        if audio_file.lower().endswith('.wav'):
            audio = AudioSegment.from_wav(audio_file)
        elif audio_file.lower().endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_file)
        else:
            audio = AudioSegment.from_file(audio_file)
        
        print(f"Durata: {len(audio) / 1000:.1f} secondi")
        
        # Converti a formato ottimale: mono, 16kHz, 16-bit
        print("Conversione audio...")
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_sample_width(2)
        
        audio.export(wav_file, format="wav")
        print(f"✓ Audio preparato: {wav_file}")
        
        return wav_file
        
    except Exception as e:
        print(f"✗ Errore conversione: {e}")
        return None

# Funzione di trascrizione offline
def transcribe_offline(audio_file, model_path):
    try:
        # Converti audio
        wav_file = convert_to_wav_16k(audio_file)
        if not wav_file:
            return
        
        # Carica modello Vosk
        print("\nCaricamento modello di riconoscimento vocale...")
        model = Model(model_path)
        
        # Apri file audio
        wf = wave.open(wav_file, "rb")
        
        # Verifica formato
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            print("✗ Formato audio non corretto")
            return
        
        # Crea recognizer
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        print("Trascrizione in corso (OFFLINE - nessuna connessione richiesta)...")
        print("Questo potrebbe richiedere qualche minuto...\n")
        
        # Trascrivi
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'text' in result and result['text']:
                    results.append(result['text'])
                    # Mostra progresso
                    print('.', end='', flush=True)
        
        # Risultato finale
        final_result = json.loads(rec.FinalResult())
        if 'text' in final_result and final_result['text']:
            results.append(final_result['text'])
        
        # Combina risultati
        full_text = ' '.join(results)
        
        print("\n\n" + "="*60)
        print("TESTO TRASCRITTO:")
        print("="*60)
        print(full_text)
        print("="*60)
        
        # Salva trascrizione
        output_file = audio_file.rsplit(".", 1)[0] + "_trascrizione.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"\n✓ Trascrizione salvata in: {output_file}")
        
        # Pulisci file temporaneo
        if wav_file != audio_file and os.path.exists(wav_file):
            os.remove(wav_file)
        
    except Exception as e:
        print(f"\n✗ Errore trascrizione: {e}")
        import traceback
        traceback.print_exc()

# Main
def main():
    print("\n" + "="*60)
    print("TRASCRITTORE AUDIO OFFLINE")
    print("="*60)
    print("\n✓ Funziona SENZA connessione internet")
    print("✓ Nessuna API richiesta")
    print("✓ Privacy totale - tutto elaborato localmente")
    print("\nFormati supportati: WAV, MP3, OGG, FLAC, etc.")
    print("\nTrascina il file audio qui e premi Invio:")
    
    audio_file = input().strip().strip("'\"")
    
    if not os.path.exists(audio_file):
        print(f"\n⚠ File non trovato: {audio_file}")
        sys.exit(1)
    
    transcribe_offline(audio_file, model_path)
    
    print("\n✓ Operazione completata!")

if __name__ == "__main__":
    main()