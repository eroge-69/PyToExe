import math


# ======================
# 1. 镜像加密/解密
# ======================
def mirror_encrypt(text):
    return text[::-1]


def mirror_decrypt(text):
    return text[::-1]


# ======================
# 2. 栅栏加密/解密 (高度2)
# ======================
def fence_encrypt(text):
    n = len(text)
    part1 = text[0::2]  # 奇数位字符
    part2 = text[1::2]  # 偶数位字符
    return part1 + part2


def fence_decrypt(text):
    n = len(text)
    len1 = (n + 1) // 2  # 第一部分长度
    part1 = text[:len1]
    part2 = text[len1:]
    result = []
    for i in range(len1):
        result.append(part1[i])
        if i < len(part2):
            result.append(part2[i])
    return ''.join(result)


# ======================
# 3. 电脑键盘替代加密/解密
# ======================
def create_keyboard_map():
    rows = [
        "`1234567890-=",
        "qwertyuiop[]\\",
        "asdfghjkl;'",
        "zxcvbnm,./",
        "~!@#$%^&*()_+",
        "QWERTYUIOP{}|",
        "ASDFGHJKL:\"",
        "ZXCVBNM<>?"
    ]
    mapping = {}
    for row in rows:
        for i in range(1, len(row)):
            mapping[row[i]] = row[i - 1]
        mapping[row[0]] = row[-1]  # 第一个字符映射到最后一个
    return mapping


keyboard_map = create_keyboard_map()
reverse_keyboard_map = {v: k for k, v in keyboard_map.items()}


def keyboard_encrypt(text):
    return ''.join(keyboard_map.get(c, c) for c in text)


def keyboard_decrypt(text):
    return ''.join(reverse_keyboard_map.get(c, c) for c in text)


# ======================
# 4. 九宫格手机键盘加密/解密
# ======================
phone_map = {
    'a': '2', 'b': '2', 'c': '2',
    'd': '3', 'e': '3', 'f': '3',
    'g': '4', 'h': '4', 'i': '4',
    'j': '5', 'k': '5', 'l': '5',
    'm': '6', 'n': '6', 'o': '6',
    'p': '7', 'q': '7', 'r': '7', 's': '7',
    't': '8', 'u': '8', 'v': '8',
    'w': '9', 'x': '9', 'y': '9', 'z': '9',
    'A': '2', 'B': '2', 'C': '2',
    'D': '3', 'E': '3', 'F': '3',
    'G': '4', 'H': '4', 'I': '4',
    'J': '5', 'K': '5', 'L': '5',
    'M': '6', 'N': '6', 'O': '6',
    'P': '7', 'Q': '7', 'R': '7', 'S': '7',
    'T': '8', 'U': '8', 'V': '8',
    'W': '9', 'X': '9', 'Y': '9', 'Z': '9'
}
reverse_phone_map = {
    '2': 'a', '3': 'd', '4': 'g', '5': 'j',
    '6': 'm', '7': 'p', '8': 't', '9': 'w'
}


def phone_encrypt(text):
    return ''.join(phone_map.get(c, c) for c in text)


def phone_decrypt(text):
    return ''.join(reverse_phone_map.get(c, c) for c in text)


# ======================
# 5. 摩斯密码加密/解密
# ======================
morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...',
    ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-',
    '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
}
reverse_morse_dict = {v: k for k, v in morse_dict.items()}


def morse_encrypt(text):
    morse_list = []
    for char in text.upper():
        if char in morse_dict:
            morse_list.append(morse_dict[char])
        else:
            morse_list.append(char)  # 未知字符保留原样
    return ' '.join(morse_list)


def morse_decrypt(text):
    words = text.split(' ')
    result = []
    for code in words:
        if code in reverse_morse_dict:
            result.append(reverse_morse_dict[code])
        else:
            result.append(code)  # 未知代码保留原样
    return ''.join(result)


# ======================
# 复合加密/解密
# ======================
def composite_encrypt(text):
    text = mirror_encrypt(text)
    text = fence_encrypt(text)
    text = keyboard_encrypt(text)
    text = phone_encrypt(text)
    text = morse_encrypt(text)
    return text


def composite_decrypt(text):
    text = morse_decrypt(text)
    text = phone_decrypt(text)
    text = keyboard_decrypt(text)
    text = fence_decrypt(text)
    text = mirror_decrypt(text)
    return text


# ======================
# 用户界面
# ======================
def main():
    while True:
        print("\n===== 五层复合加密/解密器 =====")
        print("1. 加密文本")
        print("2. 解密文本")
        print("3. 退出程序")
        choice = input("请选择操作 (1/2/3): ")

        if choice == '1':
            text = input("请输入要加密的文本: ")
            encrypted = composite_encrypt(text)
            print("\n加密结果:", encrypted)

        elif choice == '2':
            text = input("请输入要解密的文本: ")
            decrypted = composite_decrypt(text)
            print("\n解密结果:", decrypted)

        elif choice == '3':
            print("感谢使用，再见！")
            break

        else:
            print("无效选择，请重新输入！")


if __name__ == "__main__":
    main()