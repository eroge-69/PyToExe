import math

a = "<"
b = ">"
c = "0"
d = "9"
e = "/"
f = "X"
g = "|"
h = "#"
i = "!"
j = "@"
k = "3"
l = "\/"
m = "1"
n = "10"
o = "7"
p = "!!"
q = "aA"
r = "Qr"
s = "rQ"
t = "$"
u = "%"
v = "*"
x = "-+"
y = "!."
z = "(!RS)"


def encpro(sent):
    encoded = ""
    for char in sent:
        if char == "a" or char == "A":
            encoded += a
        elif char == "b" or char == "B":
            encoded += b
        elif char == "c" or char == "C":
            encoded += c
        elif char == "d" or char == "D":
            encoded += d
        elif char == "e" or char == "E":
            encoded += e
        elif char == "f" or char == "F":
            encoded += f
        elif char == "g" or char == "G":
            encoded += g
        elif char == "h" or char == "H":
            encoded += h
        elif char == "i" or char == "I":
            encoded += i
        elif char == "j" or char == "J":
            encoded += j
        elif char == "k" or char == "K":
            encoded += k
        elif char == "l" or char == "L":
            encoded += l
        elif char == "m" or char == "M":
            encoded += m
        elif char == "n" or char == "N":
            encoded += n
        elif char == "o" or char == "O":
            encoded += o
        elif char == "p" or char == "P":
            encoded += p
        elif char == "q" or char == "Q":
            encoded += q
        elif char == "r" or char == "R":
            encoded += r
        elif char == "s" or char == "S":
            encoded += s
        elif char == "t" or char == "T":
            encoded += t
        elif char == "u" or char == "U":
            encoded += u
        elif char == "v" or char == "V":
            encoded += v
        elif char == "x" or char == "X":
            encoded += x
        elif char == "y" or char == "Y":
            encoded += y
        elif char == "z" or char == "Z":
            encoded += z
        else:
            encoded += char  # Non-alphabetic characters remain unchanged
    return encoded


def decpro(encoded):
    decoded = ""
    i = 0
    while i < len(encoded):
        if encoded[i:i+1] == a:
            decoded += "a"
            i += 1
        elif encoded[i:i+1] == b:
            decoded += "b"
            i += 1
        elif encoded[i:i+1] == c:
            decoded += "c"
            i += 1
        elif encoded[i:i+1] == d:
            decoded += "d"
            i += 1
        elif encoded[i:i+1] == e:
            decoded += "e"
            i += 1
        elif encoded[i:i+1] == f:
            decoded += "f"
            i += 1
        elif encoded[i:i+1] == g:
            decoded += "g"
            i += 1
        elif encoded[i:i+1] == h:
            decoded += "h"
            i += 1
        elif encoded[i:i+1] == i:
            decoded += "i"
            i += 1
        elif encoded[i:i+1] == j:
            decoded += "j"
            i += 1
        elif encoded[i:i+1] == k:
            decoded += "k"
            i += 1
        elif encoded[i:i+2] == l:
            decoded += "l"
            i += 2
        elif encoded[i:i+1] == m:
            decoded += "m"
            i += 1
        elif encoded[i:i+2] == n:
            decoded += "n"
            i += 2
        elif encoded[i:i+1] == o:
            decoded += "o"
            i += 1
        elif encoded[i:i+2] == p:
            decoded += "p"
            i += 2
        elif encoded[i:i+2] == q:
            decoded += "q"
            i += 2
        elif encoded[i:i+2] == r:
            decoded += "r"
            i += 2
        elif encoded[i:i+2] == s:
            decoded += "s"
            i += 2
        elif encoded[i:i+1] == t:
            decoded += "t"
            i += 1
        elif encoded[i:i+1] == u:
            decoded += "u"
            i += 1
        elif encoded[i:i+1] == v:
            decoded += "v"
            i += 1
        
        elif encoded[i:i+1] == x:
            decoded += "x"
            i += 1
        elif encoded[i:i+1] == y:
            decoded += "y"
            i += 1
        elif encoded[i:i+1] == z:
            decoded += "z"
            i += 1
        else:
            decoded += encoded[i:i+1]
            i += 1
    return decoded

quiery = input("Encode or Decode? (e/d): ").lower()
if quiery == "d":
    sent = input("Enter text to decode: ")
    print(decpro(sent))
elif quiery == "e":
    sent = input("Enter text to encode: ")
    print(encpro(sent))
else:
    print("Invalid option. Please enter 'e' to encode or 'd' to decode.")