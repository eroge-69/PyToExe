import os
import subprocess
import shutil

# Crear carpetas necesarias
os.makedirs("tmp", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Limpiar carpeta temporal
for f in os.listdir("tmp"):
    os.remove(os.path.join("tmp", f))

lopus_files = []

# Procesar archivos .wav en la carpeta ./input
for filename in os.listdir("./input"):
    if not filename.lower().endswith(".wav"):
        continue

    base = os.path.splitext(filename)[0]
    input_path = os.path.join("input", filename)
    tmp_wav_path = os.path.join("tmp", f"{base}_48k_12db.wav")
    tmp_lopus_path = os.path.join("tmp", f"{base}.lopus")

    print(f"Convirtiendo {filename}...")

    # 1. WAV → WAV 48kHz con +12 dB
    subprocess.call([
        "./tools/sox/sox.exe", input_path, "-r", "48000",
        tmp_wav_path, "gain", "+12"
    ])

    # 2. WAV → LOPUS (CBR 64kbps, cabecera Namco)
    subprocess.call([
        "./tools/VGAudioCli.exe", tmp_wav_path, tmp_lopus_path,
        "--bitrate", "64000", "--CBR", "--opusheader", "namco"
    ])

    lopus_files.append(tmp_lopus_path)

# 3. Crear archivo NUS3AUDIO (playlist)
output_file = "./output/vc_ness_c03.nus3audio"
print(f"Generando archivo NUS3AUDIO: {output_file}")

subprocess.call([
    "./tools/nus3audio.exe", "-n", "-A", "vc_ness_c03"
] + lopus_files + ["-w", output_file])

print("✅ Proceso completado.")
