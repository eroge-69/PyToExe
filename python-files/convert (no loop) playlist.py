import os, subprocess, shutil

# Preparar carpetas
os.makedirs("tmp", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Limpiar carpeta temporal
for f in os.listdir("tmp"):
    os.remove(os.path.join("tmp", f))

lopus_files = []

# Convertir todos los .wav de ./input a .lopus con +12 dB
for x in os.listdir("./input"):
    if not x.lower().endswith(".wav"):
        continue

    base = os.path.splitext(x)[0]
    print(f"Convirtiendo {x}...")

    # WAV -> WAV (+12dB, 48kHz)
    subprocess.call([
        "./tools/sox/sox.exe", f"./input/{x}", "-r", "48000",
        f"./tmp/{base}_48k_12db.wav", "gain", "+12"
    ])

    # WAV -> LOPUS
    subprocess.call([
        "./tools/VGAudioCli.exe", f"./tmp/{base}_48k_12db.wav",
        f"./tmp/{base}.lopus",
        "--bitrate", "64000", "--CBR", "--opusheader", "namco"
    ])
    lopus_files.append(f"./tmp/{base}.lopus")

# Crear playlist NUS3AUDIO
output_file = "./output/vc_ness_c03.nus3audio"
subprocess.call([
    "./tools/nus3audio.exe", "-n", "-A", "vc_ness_c03"
] + lopus_files + ["-w", output_file])

print(f"Playlist NUS3AUDIO generada: {output_file}")
