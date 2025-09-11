from PIL import Image, ImageSequence
import os

# Nome file immagine di partenza
input_file = "Image20.png"

# Nome file gif di uscita
output_file = "personaggio_animato.gif"

# Carico immagine base
img = Image.open(input_file).convert("RGBA")

# Creiamo più fotogrammi con piccoli movimenti (simulazione canto e movimento naturale)
frames = []
for i in range(10):
    # Copia immagine
    frame = img.copy()

    # Leggera traslazione su/giù
    offset = (i % 2) * 2  
    new_frame = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    new_frame.paste(frame, (0, offset))

    # Salvo frame
    frames.append(new_frame)

# Salvo come GIF animata in loop infinito
frames[0].save(
    output_file,
    save_all=True,
    append_images=frames[1:],
    duration=150,  # Velocità animazione (ms)
    loop=0  # 0 = infinito
)

print(f"Animazione salvata come {output_file}")
