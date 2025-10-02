from PIL import Image
import random
import base64
import binascii

bin_repr = lambda s, coding="ascii": ' '.join('{0:08b}'.format(c) for c in s.encode(coding))


image = Image.open('image.png')
pixel = image.load()
longueur = image.size[0]-1
largeur = image.size[1]-1

message = 'flag'
messageBinaire = bin_repr(message).replace(' ', '')

key = []

for bits in messageBinaire:
	randomLongueur = random.randint(0, longueur) #x
	randomLargeur = random.randint(0, largeur) #y
	print("Writing in pixel", randomLongueur, "x", randomLargeur)
	quelRgb = random.randint(0,2)
	print("Pixel was : " + str(pixel[randomLongueur, randomLargeur]))
	if quelRgb == 0:
		if bits == '1':
			r = (pixel[randomLongueur, randomLargeur][0])+1
			g = pixel[randomLongueur, randomLargeur][1]
			b = pixel[randomLongueur, randomLargeur][2]

			pixel[randomLongueur, randomLargeur] = (r,g,b,255)
			print("Pixel is now : " + str(pixel[randomLongueur, randomLargeur]))
			key.append(str(randomLongueur) + "x" + str(randomLargeur))
		else:
			r = (pixel[randomLongueur, randomLargeur][0])-1
			g = pixel[randomLongueur, randomLargeur][1]
			b = pixel[randomLongueur, randomLargeur][2]

			pixel[randomLongueur, randomLargeur] = (r,g,b,255)
			print("Pixel is now : " + str(pixel[randomLongueur, randomLargeur]))
			key.append(str(randomLongueur) + "x" + str(randomLargeur))

	elif quelRgb == 1:
		if bits == '1':
			r = pixel[randomLongueur, randomLargeur][0]
			g = (pixel[randomLongueur, randomLargeur][1])+1
			b = pixel[randomLongueur, randomLargeur][2]

			pixel[randomLongueur, randomLargeur] = (r,g,b,255)
			print("Pixel is now : " + str(pixel[randomLongueur, randomLargeur]))
			key.append(str(randomLongueur) + "x" + str(randomLargeur))
		else:
			r = pixel[randomLongueur, randomLargeur][0]
			g = (pixel[randomLongueur, randomLargeur][1])-1
			b = pixel[randomLongueur, randomLargeur][2]

			pixel[randomLongueur, randomLargeur] = (r,g,b,255)
			print("Pixel is now : " + str(pixel[randomLongueur, randomLargeur]))
			key.append(str(randomLongueur) + "x" + str(randomLargeur))
	else:
		if bits == '1':
			r = pixel[randomLongueur, randomLargeur][0]
			g = pixel[randomLongueur, randomLargeur][1]
			b = (pixel[randomLongueur, randomLargeur][2])+1

			pixel[randomLongueur, randomLargeur] = (r,g,b,255)
			print("Pixel is now : " + str(pixel[randomLongueur, randomLargeur]))
			key.append(str(randomLongueur) + "x" + str(randomLargeur))
		else:
			r = pixel[randomLongueur, randomLargeur][0]
			g = pixel[randomLongueur, randomLargeur][1]
			b = (pixel[randomLongueur, randomLargeur][2])-1

			pixel[randomLongueur, randomLargeur] = (r,g,b,255)
			print("Pixel is now : " + str(pixel[randomLongueur, randomLargeur]))
			key.append(str(randomLongueur) + "x" + str(randomLargeur))


print("Key : " + str(key))
print(messageBinaire)
image.save('image_stega.png')