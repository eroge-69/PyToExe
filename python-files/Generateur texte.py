from random import *
import time
print("Ceci est un générateur de texte aléatoire, t'as une petite chance d'avoir du texte clair!")
alphabet=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
while True:
    text=""
    for i in range(randint(1,1000)):
        text+=alphabet[randint(0,25)]
    print(text)
    time.sleep(1)