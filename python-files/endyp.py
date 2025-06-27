encrypt_map = {
    'a': 'Q', 'b': 'P', 'c': 'W', 'd': 'O', 'e': 'E', 'f': 'I',
    'g': 'R', 'h': 'U', 'i': 'T', 'j': 'Y', 'k': 'A', 'l': 'L',
    'm': 'S', 'n': 'K', 'o': 'D', 'p': 'J', 'q': 'F', 'r': 'H',
    's': 'G', 't': 'Z', 'u': 'M', 'v': 'X', 'w': 'N', 'x': 'C',
    'y': 'B', 'z': 'V', '1': '$', '2': '!', '3': '%', '4': '@',
     '5': '?',
}

decrypt_map = {v: k for k, v in encrypt_map.items()}

extra_vars = {'0': '-'}
extra_vars = {'1': '!'}
extra_vars = {'2': '@'}
extra_vars = {'3': '#'}

text = input("Enter your code: ")

result = []
for ch in text:
    if ch in encrypt_map:
        result.append(encrypt_map[ch])
    elif ch in decrypt_map:
        result.append(decrypt_map[ch])
    elif ch in extra_vars:
        result.append(extra_vars[ch])
    else:
        result.append(ch)

print(''.join(result) + "\npowered by Mamun")
