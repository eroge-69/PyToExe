

def word_to_to_bits_stream(word: str):
    res = '0b'
    for encode_symbol in word.encode():
        byte = bin(encode_symbol)

        res += byte[2:]

    return res


def code_with_repetition(word: str, s: int):
    res = '0b'
    original_word = word_to_to_bits_stream(word)

    for bit in original_word[2:]:
        res += bit * (s + 1)
    return original_word, res


def code_with_one_parity_check(word: str, s: int):
    res = '0b'
    original_word = word_to_to_bits_stream(word)

    word_in_bits = original_word[2:]
    assert len(word_in_bits) % s == 0

    blocks_count = len(word_in_bits) // s
    for i in range(blocks_count):
        block = word_in_bits[i * s: (i + 1) * s]

        res += block
        res += str(checksum(block))
    return original_word, res



def checksum(bits: str):
    res = 0
    for bit in bits:
        res ^= int(bit)
    return res


def rectangular_iterative_codes(word: str, s: int, p: int):
    res = '0b'
    original_word = word_to_to_bits_stream(word)

    assert len(original_word[2:]) % (s * p) == 0

    blocks_count = len(original_word[2:]) // (s * p)

    for i in range(blocks_count):
        block = original_word[2:][p * s * i: p * s * (i + 1)]
        res += block

        for j in range(s):
            res += str(checksum(block[j * p: (j + 1) * p]))

        for j in range(p):
            res += str(checksum(block[j::p]))

    return original_word, res


def triangular_codes(word: str, s: int):
    res = '0b'
    original_word = word_to_to_bits_stream(word)

    assert len(original_word[2:]) % (s ** 2) == 0

    blocks_count = len(original_word[2:]) // (s ** 2)

    for i in range(blocks_count):
        block = original_word[2:][s * s * i: s * s * (i + 1)]
        res += block
        row_checksum = []
        for j in range(s):
            row_checksum.append(str(checksum(block[j * s: (j + 1) * s])))

        column_checksum = []
        for j in range(s):
            column_checksum.append(str(checksum(block[j::s])))

        for i in range(s):
            res += str(int(row_checksum[i]) ^ int(column_checksum[i]))
    return original_word, res


if __name__ == '__main__':
    num = int(input('Введите номер задания -> '))
    word = input('Введите слово -> ')
    match(num):
        case 1:
            s = int(input("Введите s -> "))
            original_word, encoding_word = code_with_repetition(word, s)
            print(f'Исходное слово: {original_word}')
            print(f'Зашифрованное слово: {encoding_word}')
        case 2:
            s = int(input("Введите s -> "))
            original_word, encoding_word = code_with_one_parity_check(word, s)
            print(f'Исходное слово: {original_word}')
            print(f'Зашифрованное слово: {encoding_word}')
            print(f'Выполнила Назарьева Елена, гр. КМА')
        case 3:
            s = int(input("Введите s -> "))
            p = int(input("Введите p -> "))
            original_word, encoding_word = rectangular_iterative_codes(word, s, p)
            print(f'Исходное слово: {original_word}')
            print(f'Зашифрованное слово: {encoding_word}')
        case 4:
            s = int(input("Введите s -> "))
            original_word, encoding_word = triangular_codes(word, s)
            print(f'Исходное слово: {original_word}')
            print(f'Зашифрованное слово: {encoding_word}')
            pass
        case _:
            assert False