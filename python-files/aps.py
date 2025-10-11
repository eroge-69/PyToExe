import random
import string

an = []
pan = []
for i in range(12):
    random_number = random.randint(0, 9)
    an.append(str(random_number))
 
adn = "".join(an);
print(f"Aadhar No - {adn}")

for i in range(5):
    random_letter = random.choice(string.ascii_letters).upper()
    pan.append(random_letter)
    
for i in range(4):
    pan.append(str(random.randint(0, 9)))

pan.append(random.choice(string.ascii_letters).upper())
print(f"PAN - {"".join(pan)}")