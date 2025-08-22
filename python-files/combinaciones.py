import itertools

# Conjunto de caracteres permitidos (sin 0 ni O)
chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def hex_value(c):
    if c.isdigit():
        return int(c)
    elif c.upper() in "ABCDEF":
        return 10 + ord(c.upper()) - ord('A')
    else:
        return 0

def hex_sum(s):
    return sum(hex_value(c) for c in s[:7])

def no_tres_consecutivos(s):
    for i in range(len(s) - 2):
        tipo1 = s[i].isalpha()
        tipo2 = s[i+1].isalpha()
        tipo3 = s[i+2].isalpha()
        if tipo1 == tipo2 == tipo3:
            return False
    return True

def pares_validos(s):
    if s[0] == s[-1]:
        return False
    pares = 0
    i = 0
    while i < 7:
        if s[i] == s[i+1]:
            pares += 1
            i += 1  # saltar siguiente para no contar pegado
        i += 1
    return pares >= 2

def ultimo_valido(c):
    return c.islower() or c.isdigit()

# Archivo de salida
with open("combinaciones.txt", "w") as f:
    total = 0
    for s in itertools.product(chars, repeat=8):
        s = ''.join(s)
        if not (700 <= hex_sum(s) <= 799):
            continue
        if not ultimo_valido(s[-1]):
            continue
        if not no_tres_consecutivos(s):
            continue
        if not pares_validos(s):
            continue
        f.write(s + "\n")
        total += 1
    print(f"Combinaciones válidas generadas: {total}")