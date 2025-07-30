from PIL import Image, ImageDraw, ImageFont

# Tekst użytkownika
text = input("Wpisz tekst, który ma być wyświetlony na obrazku: ")

# Parametry obrazka
width = 600
height = 100

# Tworzenie czarnego tła
image = Image.new('RGB', (width, height), color='black')
draw = ImageDraw.Draw(image)

# Czcionka
try:
    font = ImageFont.truetype("arial.ttf", 24)
except:
    font = ImageFont.load_default()

# Pozycja tekstu
text_position = (10, 30)

# Rysowanie czerwonego tekstu
draw.text(text_position, text, fill='red', font=font)

# Zapis
image.save('tekst_na_obrazku.png')
print("Obrazek został zapisany jako 'tekst_na_obrazku.png'")
