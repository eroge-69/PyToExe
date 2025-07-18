from PIL import Image
import pillow_heif
 
# Ouvre le fichier HEIC
heif_file = pillow_heif.open_heif('image.HEIC')
 
# Convertit en objet PIL
image = Image.frombytes(
    heif_file.mode,
    heif_file.size,
    heif_file.data,
    "raw"
)
 
# Sauvegarde au format JPEG
image.save('image_convertie.jpg', "JPEG")
