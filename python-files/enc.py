def xorbytes(abytes, bbytes):
    return bytes([a ^ b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])


text = input('Please enter the text sent by parsa: ')
key = input('Please call parsa and receive the key: ')

print(xorbytes((key*15).encode(),bytes(bytearray.fromhex(text))).decode())