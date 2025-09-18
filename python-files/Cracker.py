import random

ways = True

a = "07"
b = "ik"
c = "iippa"
d = "2007"
e = "iivari"
f = "22"
g = "11"
h = "hibeer"



info = [a, b, c, d, e, f, g, h]

while ways:

parts = info.copy()
random.shuffle(parts)# randomize the variable order
guess = ''.join(parts) 

if guess in info:
    continue
else:
    print(guess)
    info.append(guess)
    tries = tries + 1
    
if tries == 100:
    ways = False