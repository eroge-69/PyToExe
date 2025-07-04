import argparse
import os
import glob # Para buscar archivos dentro de subcarpetas

import music21
import torch
import soundfile as sf
import numpy as np
import librosa
import rvc_python
from pyutau import UTAUVoiceEngine

# --- NOTA IMPORTANTE ---
# La implementación completa de RVC o UTAU requiere modelos pre-entrenados y lógica de inferencia
# que va más allá del alcance de este script. Los siguientes comentarios te guiarán
# sobre dónde integrar tu código específico para estas librerías.
# -----------------------

def parse_musicxml_for_tones(musicxml_path):
    """
    Analiza un archivo MusicXML y extrae información de tonos y duraciones.
    Utiliza la biblioteca 'music21'.
    Devuelve una lista de diccionarios con 'note' (ej. 'C4') y 'duration' (en cuartos).
    """
    print(f"Analizando MusicXML: '{musicxml_path}' para tonos...")
    try:
        score = music21.converter.parse(musicxml_path)
        tones_data = []
        for part in score.parts:
            for element in part.flat.notesAndRests:
                if isinstance(element, music21.note.Note):
                    tones_data.append({
                        "note": element.nameWithOctave,
                        "duration": element.quarterLength,
                        "is_rest": False
                    })
                elif isinstance(element, music21.note.Rest):
                    tones_data.append({
                        "note": "Rest",
                        "duration": element.quarterLength,
                        "is_rest": True
                    })
        print(f"MusicXML analizado. Se encontraron {len(tones_data)} elementos musicales.")
        return tones_data
    except Exception as e:
        print(f"Error al analizar MusicXML '{musicxml_path}': {e}")
        return None

def analyze_audio_for_tones(audio_path):
    """
    Analiza un archivo de audio y extrae información de tono (F0) usando librosa.yin.
    Devuelve una lista de diccionarios con 'time' (en segundos) y 'frequency' (en Hz).
    """
    print(f"Analizando audio: '{audio_path}' para tonos usando librosa.yin...")
    try:
        y, sr = librosa.load(audio_path, sr=None) # sr=None para mantener la frecuencia de muestreo original

        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            frame_length=2048,
            hop_length=512
        )

        tones_data = []
        times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=512)

        for i, freq in enumerate(f0):
            tones_data.append({
                "time": times[i],
                "frequency": freq if voiced_flag[i] else 0.0, # 0.0 para indicar silencio/no-voz
                "is_voiced": bool(voiced_flag[i])
            })

        print(f"Audio analizado. Se encontraron {len(tones_data)} puntos de tono/silencio.")
        return tones_data
    except Exception as e:
        print(f"Error al analizar audio '{audio_path}' con librosa: {e}")
        return None

def load_voice_model(model_subfolder_path):
    """
    Carga un modelo RVC (archivo .pth) o identifica un voicebank UTAU dentro de la subcarpeta.
    La lógica de carga real para RVC asume un archivo .pth.
    Para UTAU, verifica la presencia de 'character.txt'.
    """
    print(f"Cargando modelo de voz desde la subcarpeta: '{model_subfolder_path}'...")
    if not os.path.isdir(model_subfolder_path):
        raise FileNotFoundError(f"Error: La subcarpeta del modelo no se encontró en: '{model_subfolder_path}'")
    
    voice_model_info = {
        "name": os.path.basename(model_subfolder_path),
        "type": "Unknown",
        "path": model_subfolder_path,
        "model_object": None,
        "sample_rate": None # RVC models often have a specific sample rate
    }

    # --- Intentar cargar como modelo RVC (.pth) ---
    # Busca archivos .pth dentro de la subcarpeta
    pth_files = glob.glob(os.path.join(model_subfolder_path, "*.pth"))
    if pth_files and RVC_AVAILABLE:
        # Asume el primer archivo .pth encontrado como el modelo principal.
        # En un escenario real, podrías tener una convención de nombres (ej. G_latest.pth).
        pth_file_path = pth_files[0]
        print(f"Intentando cargar archivo RVC .pth: {pth_file_path}")
        try:
            # Carga el diccionario de estado del modelo PyTorch.
            # Necesitarás la arquitectura del modelo (la clase Python) para instanciarlo completamente.
            loaded_state_dict = torch.load(pth_file_path, map_location='cpu')
            voice_model_info["model_object"] = loaded_state_dict # Almacena el diccionario de estado
            voice_model_info["type"] = "RVC_MODEL"
            print(f"Modelo RVC '{os.path.basename(pth_file_path)}' cargado (diccionario de estado).")
            print("Nota: La arquitectura del modelo (clase Python) es aún necesaria para la inferencia real.")
            
            # Intenta determinar el sample_rate del modelo RVC si está en el nombre del archivo o en los metadatos
            # Esto es una heurística y puede no ser precisa para todos los modelos RVC.
            if "40k" in os.path.basename(pth_file_path).lower():
                voice_model_info["sample_rate"] = 40000
            elif "48k" in os.path.basename(pth_file_path).lower():
                voice_model_info["sample_rate"] = 48000
            else:
                voice_model_info["sample_rate"] = 44100 # Por defecto
            
        except Exception as e:
            print(f"Error al cargar el modelo PyTorch .pth '{pth_file_path}': {e}")
            voice_model_info["type"] = "Unknown"
            voice_model_info["model_object"] = None
    
    # --- Intentar identificar como voicebank UTAU ---
    # Un voicebank UTAU típicamente contiene un archivo 'character.txt'
    character_txt_path = os.path.join(model_subfolder_path, "character.txt")
    if os.path.exists(character_txt_path) and UTAU_AVAILABLE:
        if voice_model_info["type"] == "Unknown": # Solo si no se identificó ya como RVC
            voice_model_info["type"] = "UTAU_VOICEBANK"
            print(f"Voicebank UTAU identificado en: {model_subfolder_path}")
            # Para UTAU, el 'model_object' podría ser la ruta a la carpeta.
            voice_model_info["model_object"] = model_subfolder_path 
            # UTAU suele usar 44100 Hz, pero puede variar.
            voice_model_info["sample_rate"] = 44100 

    if voice_model_info["type"] == "Unknown":
        print(f"Advertencia: No se pudo identificar el tipo de modelo en '{model_subfolder_path}'. Asegúrese de que contenga un archivo .pth (RVC) o character.txt (UTAU).")

    return voice_model_info

def synthesize_audio(tones_data, voice_model, output_path):
    """
    Sintetiza audio usando datos de tono y un modelo de voz.
    Este es el punto de integración para RVC o UTAU.
    Utiliza soundfile para escribir el archivo WAV.
    """
    print(f"Sintetizando audio con '{voice_model['name']}' (Tipo: {voice_model['type']}) y datos de tonos...")
    print(f"Guardando salida en: '{output_path}'")

    synthesized_audio_data = np.array([], dtype=np.float32)
    output_sample_rate = voice_model.get("sample_rate", 44100) # Usar sample rate del modelo si está disponible

    # --- PUNTO DE INTEGRACIÓN PARA LA SÍNTESIS DE VOZ REAL (RVC/UTAU) ---
    # Aquí es donde integrarías tu lógica de síntesis de voz compleja.
    #
    # 1. Preparar los datos de 'tones_data' para tu motor de síntesis.
    # 2. Invocar la función/clase de inferencia de tu librería RVC/UTAU.
    # 3. El resultado debe ser un array NumPy de audio (float32).

    if voice_model["type"] == "RVC_MODEL" and RVC_AVAILABLE:
        print("\n--- Intentando síntesis RVC ---")
        # --- PSEUDOCÓDIGO DE INTEGRACIÓN RVC ---
        # Necesitarás:
        # a) La definición de la arquitectura de tu modelo RVC (ej. de rvc_project.models import Generator)
        # b) Un objeto de inferencia RVC que maneje la conversión.
        #
        # Ejemplo conceptual:
        # try:
        #     from rvc_python.vc_infer import VCInfer # Esto es un ejemplo, la ruta real puede variar
        #     # Instancia el modelo RVC. Esto es MUY dependiente de tu modelo y su arquitectura.
        #     # rvc_model_architecture = YourRVCModelClass() # ¡Necesitas definir esta clase!
        #     # rvc_model_architecture.load_state_dict(voice_model["model_object"])
        #     # rvc_model_architecture.eval()
        #
        #     # Aquí, necesitarías convertir tones_data (notas o F0) al formato que RVC espera.
        #     # RVC a menudo toma un audio de entrada (para extraer características) y un contorno de F0 objetivo.
        #     # Si la entrada es MusicXML, necesitarías convertir notas a un contorno de F0.
        #     # Si la entrada es audio, ya tienes el contorno de F0.
        #
        #     # Ejemplo muy simplificado:
        #     # target_f0 = convert_tones_data_to_f0_contour(tones_data, output_sample_rate)
        #     # rvc_inferer = VCInfer(model=rvc_model_architecture, device='cuda' if torch.cuda.is_available() else 'cpu')
        #     # synthesized_audio_data = rvc_inferer.infer(
        #     #     target_f0=target_f0,
        #     #     source_audio=np.zeros(10000, dtype=np.float32), # RVC a menudo necesita un audio de referencia dummy
        #     #     sid=0, # Speaker ID
        #     #     f0_up_key=0, # Pitch shift
        #     #     # ... otros parámetros de RVC
        #     # )
        #     print("Lógica de síntesis RVC placeholder ejecutada. ¡Integra tu código RVC aquí!")
        #     # Por ahora, se usará el generador de audio de ejemplo.
        # except Exception as e:
        #     print(f"Error durante la integración RVC: {e}")
        #     print("Volviendo a la generación de audio de ejemplo.")
        
        print("rvc_python está disponible, pero la lógica de inferencia RVC debe ser implementada aquí.")
        print("Generando audio de ejemplo como fallback.")
        synthesized_audio_data, output_sample_rate = _generate_placeholder_audio(tones_data, output_sample_rate)

    elif voice_model["type"] == "UTAU_VOICEBANK" and UTAU_AVAILABLE:
        print("\n--- Intentando síntesis UTAU ---")
        # --- PSEUDOCÓDIGO DE INTEGRACIÓN UTAU ---
        # Necesitarás:
        # a) Una clase o función de motor UTAU (ej. de pyutau import UTAUVoiceEngine)
        # b) Convertir los datos de MusicXML (o F0 de audio) a un formato que UTAU entienda (ej. UST-like).
        #
        # Ejemplo conceptual:
        # try:
        #     from pyutau import UTAUVoiceEngine # Esto es un ejemplo, la ruta real puede variar
        #     utau_engine = UTAUVoiceEngine(voice_model["model_object"]) # 'model_object' es la ruta a la carpeta del voicebank
        #
        #     # Convertir tones_data a un formato de notas/eventos que pyutau pueda renderizar.
        #     # Por ejemplo, una lista de objetos de nota UTAU o un archivo UST en memoria.
        #     # utau_notes = convert_tones_data_to_utau_notes(tones_data)
        #     # synthesized_audio_data = utau_engine.render(utau_notes)
        #     print("Lógica de síntesis UTAU placeholder ejecutada. ¡Integra tu código UTAU aquí!")
        #     # Por ahora, se usará el generador de audio de ejemplo.
        # except Exception as e:
        #     print(f"Error durante la integración UTAU: {e}")
        #     print("Volviendo a la generación de audio de ejemplo.")

        print("pyutau está disponible, pero la lógica de inferencia UTAU debe ser implementada aquí.")
        print("Generando audio de ejemplo como fallback.")
        synthesized_audio_data, output_sample_rate = _generate_placeholder_audio(tones_data, output_sample_rate)

    else:
        print("\n--- Usando generador de audio de ejemplo (sin integración RVC/UTAU real) ---")
        synthesized_audio_data, output_sample_rate = _generate_placeholder_audio(tones_data, output_sample_rate)

    if len(synthesized_audio_data) == 0:
        print("No se generó audio. Verifique los datos de tonos o la integración del motor de síntesis.")
        return False

    try:
        sf.write(output_path, synthesized_audio_data, output_sample_rate)
        print(f"Audio sintetizado y guardado en: '{output_path}'.")
        return True
    except Exception as e:
        print(f"Error al escribir el archivo de audio con soundfile: {e}")
        return False

def _generate_placeholder_audio(tones_data, sample_rate=44100):
    """
    Genera un audio de ejemplo simple (ondas sinusoidales) basado en los datos de tono.
    Utilizado como fallback si la síntesis RVC/UTAU real no está integrada o falla.
    """
    audio_output = np.array([], dtype=np.float32)
    total_duration_seconds = 0

    note_frequencies = {
        "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13, "E4": 329.63,
        "F4": 349.23, "F#4": 369.99, "G4": 392.00, "G#4": 415.30, "A4": 440.00,
        "A#4": 466.16, "B4": 493.88, "C5": 523.25
    }

    if tones_data and "note" in tones_data[0]: # Formato MusicXML
        for item in tones_data:
            note_name = item.get("note")
            duration_quarters = item.get("duration", 1.0)
            duration_seconds = duration_quarters * (60 / 120) * 0.5 # Asumiendo 120 BPM

            num_samples = int(sample_rate * duration_seconds)
            segment = np.zeros(num_samples, dtype=np.float32)

            if not item.get("is_rest", False) and note_name != "Rest":
                frequency = note_frequencies.get(note_name, 440.0)
                t = np.linspace(0, duration_seconds, num_samples, endpoint=False)
                amplitude = 0.6
                segment = amplitude * np.sin(2 * np.pi * frequency * t).astype(np.float32)
            
            audio_output = np.concatenate((audio_output, segment))
            total_duration_seconds += duration_seconds
    elif tones_data and "frequency" in tones_data[0]: # Formato de análisis de audio (F0)
        total_duration_seconds = tones_data[-1]["time"] if tones_data else 0
        num_total_samples = int(total_duration_seconds * sample_rate)
        audio_output = np.zeros(num_total_samples, dtype=np.float32)

        for i in range(len(tones_data) - 1):
            current_point = tones_data[i]
            next_point = tones_data[i+1] if (i+1) < len(tones_data) else None

            start_time = current_point["time"]
            frequency = current_point["frequency"]
            
            if next_point:
                segment_duration = next_point["time"] - start_time
            else:
                segment_duration = (1.0 / sample_rate) * 512 # Default to hop_length duration

            start_sample = int(start_time * sample_rate)
            num_samples = int(segment_duration * sample_rate)
            end_sample = start_sample + num_samples

            if frequency > 0 and current_point.get("is_voiced", True):
                t = np.linspace(0, segment_duration, num_samples, endpoint=False)
                amplitude = 0.6
                segment = amplitude * np.sin(2 * np.pi * frequency * t).astype(np.float32)
                audio_output[start_sample:min(end_sample, num_total_samples)] += segment[:min(num_samples, num_total_samples - start_sample)]
            
    return audio_output, sample_rate

def main():
    parser = argparse.ArgumentParser(description="Sintetizador de voz basado en MusicXML/Audio y modelos RVC/UTAU.")
    parser.add_argument("--input", required=True, help="Ruta al archivo .musicxml o de audio (.wav, .mp3, etc.).")
    parser.add_argument("--model", required=True, help="Nombre de la subcarpeta del modelo RVC o voicebank UTAU (debe estar en la subcarpeta 'model').")
    parser.add_argument("--output", default="output.wav", help="Ruta del archivo de salida de audio (.wav).")

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    model_dir = os.path.join(script_dir, "model")
    # model_full_path ahora es la ruta a la subcarpeta del modelo
    model_subfolder_path = os.path.join(model_dir, args.model) 

    output_path = os.path.abspath(args.output)

    print(f"Ruta de entrada: {input_path}")
    print(f"Ruta de la subcarpeta del modelo: {model_subfolder_path}")
    print(f"Ruta de salida: {output_path}")

    if not os.path.exists(model_dir):
        print(f"Error: La subcarpeta 'model' no se encontró en: '{model_dir}'")
        print("Por favor, asegúrese de que su modelo RVC o voicebank UTAU esté dentro de esta carpeta.")
        return

    if not os.path.exists(input_path):
        print(f"Error: El archivo de entrada no se encontró en: '{input_path}'")
        return

    input_ext = os.path.splitext(input_path)[1].lower()
    tones_data = None

    if input_ext == ".musicxml":
        tones_data = parse_musicxml_for_tones(input_path)
    elif input_ext in [".wav", ".mp3", ".flac", ".ogg"]:
        tones_data = analyze_audio_for_tones(input_path)
    else:
        print(f"Error: Tipo de archivo de entrada no compatible: '{input_ext}'. Solo se admiten .musicxml y formatos de audio comunes.")
        return

    if tones_data is None:
        print("Error: No se pudieron obtener datos de tonos del archivo de entrada.")
        return

    try:
        voice_model = load_voice_model(model_subfolder_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error al cargar el modelo de voz: {e}")
        return

    success = synthesize_audio(tones_data, voice_model, output_path)

    if success:
        print("\nProceso de síntesis completado. ¡Disfrute de su audio sintetizado!")
    else:
        print("\nEl proceso de síntesis falló.")

if __name__ == "__main__":
    import sys
