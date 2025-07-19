"""
PGenerator comprimido em um único arquivo !! Versão provisória
versão do Python 3.10.12
versão do PGenerator: 0.0.1
Por: Victor G. Ramos
Em: 5 de novembro de 2023
"""

def cls(): 
    import os, sys
    if "win" in sys.platform:
        os.system("cls")
    else:
        os.system("clear")


cls()
print(
"""
888  ,dP ,8b.      888  ,dP 888  ,d8 ,8b.     888888888 ,8b.
888o8P'  88'8o     888o8P'  888_dPY8 88'8o       '88d   88'8o
888 Y8L  88PPY8.   888 Y8L  8888' 88 88PPY8.    '888    88PPY8.
888  `8p 8b   `Y'  888  `8p Y8P   Y8 8b   `Y' '88p      8b   `Y'

app: PGenerator
version: 2.0.1

----------------------------------------------------------------
"""
)

class alphabet:
    alphabet = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "g": 7,
    "h": 8,
    "i": 9,
    "j": 10,
    "k": 11,
    "l": 12,
    "m": 13,
    "n": 14,
    "o": 15,
    "p": 16,
    "q": 17,
    "r": 18,
    "s": 19,
    "t": 20,
    "u": 21,
    "v": 22,
    "w": 23,
    "x": 24,
    "y": 25,
    "z": 26
    }

    alphabet_random = [
        {'a': 25, 'b': 1, 'c': 26, 'd': 4, 'e': 13, 'f': 9, 'g': 10, 'h': 3, 'i': 19, 'j': 8, 'k': 5, 'l': 17, 'm': 21, 'n': 6, 'o': 11, 'p': 20, 'q': 18, 'r': 2, 's': 23, 't': 16, 'u': 22, 'v': 7, 'w': 15, 'x': 24, 'y': 14, 'z': 12},
        {'a': 19, 'b': 2, 'c': 9, 'd': 12, 'e': 13, 'f': 3, 'g': 25, 'h': 23, 'i': 21, 'j': 7, 'k': 17, 'l': 26, 'm': 5, 'n': 10, 'o': 22, 'p': 14, 'q': 8, 'r': 4, 's': 1, 't': 16, 'u': 15, 'v': 20, 'w': 24, 'x': 6, 'y': 11, 'z': 18},
        {'a': 4, 'b': 18, 'c': 11, 'd': 25, 'e': 12, 'f': 17, 'g': 24, 'h': 8, 'i': 14, 'j': 1, 'k': 7, 'l': 9, 'm': 20, 'n': 13, 'o': 10, 'p': 19, 'q': 5, 'r': 26, 's': 15, 't': 22, 'u': 23, 'v': 2, 'w': 21, 'x': 6, 'y': 3, 'z': 16},
        {'a': 6, 'b': 24, 'c': 3, 'd': 25, 'e': 4, 'f': 16, 'g': 14, 'h': 18, 'i': 20, 'j': 15, 'k': 19, 'l': 26, 'm': 21, 'n': 5, 'o': 22, 'p': 23, 'q': 11, 'r': 12, 's': 7, 't': 8, 'u': 9, 'v': 17, 'w': 2, 'x': 10, 'y': 1, 'z': 13},
        {'a': 8, 'b': 6, 'c': 9, 'd': 17, 'e': 21, 'f': 13, 'g': 1, 'h': 2, 'i': 7, 'j': 23, 'k': 22, 'l': 24, 'm': 11, 'n': 20, 'o': 15, 'p': 4, 'q': 19, 'r': 26, 's': 25, 't': 5, 'u': 18, 'v': 16, 'w': 3, 'x': 12, 'y': 10, 'z': 14},
        {'a': 25, 'b': 1, 'c': 16, 'd': 12, 'e': 18, 'f': 21, 'g': 14, 'h': 3, 'i': 22, 'j': 4, 'k': 9, 'l': 17, 'm': 7, 'n': 23, 'o': 11, 'p': 15, 'q': 19, 'r': 20, 's': 13, 't': 26, 'u': 2, 'v': 10, 'w': 5, 'x': 6, 'y': 24, 'z': 8},
        {'a': 4, 'b': 16, 'c': 25, 'd': 17, 'e': 19, 'f': 1, 'g': 18, 'h': 13, 'i': 9, 'j': 20, 'k': 8, 'l': 23, 'm': 24, 'n': 15, 'o': 12, 'p': 14, 'q': 11, 'r': 2, 's': 21, 't': 7, 'u': 10, 'v': 22, 'w': 26, 'x': 3, 'y': 6, 'z': 5},
        {'a': 4, 'b': 6, 'c': 21, 'd': 15, 'e': 23, 'f': 12, 'g': 10, 'h': 1, 'i': 18, 'j': 8, 'k': 19, 'l': 22, 'm': 9, 'n': 2, 'o': 7, 'p': 3, 'q': 24, 'r': 14, 's': 25, 't': 13, 'u': 17, 'v': 20, 'w': 26, 'x': 5, 'y': 11, 'z': 16},
        {'a': 12, 'b': 23, 'c': 1, 'd': 15, 'e': 9, 'f': 25, 'g': 14, 'h': 16, 'i': 10, 'j': 7, 'k': 5, 'l': 24, 'm': 8, 'n': 17, 'o': 6, 'p': 4, 'q': 3, 'r': 21, 's': 19, 't': 13, 'u': 2, 'v': 26, 'w': 20, 'x': 18, 'y': 11, 'z': 22},
        {'a': 18, 'b': 12, 'c': 13, 'd': 14, 'e': 4, 'f': 6, 'g': 21, 'h': 11, 'i': 17, 'j': 25, 'k': 22, 'l': 19, 'm': 23, 'n': 2, 'o': 8, 'p': 9, 'q': 26, 'r': 10, 's': 16, 't': 5, 'u': 15, 'v': 7, 'w': 20, 'x': 1, 'y': 24, 'z': 3}
    ]

    symbols = [
        '&', 
        ':', 
        '#', 
        '(', 
        '>', 
        '-', 
        ')', 
        '.', 
        '}', 
        '/', 
        '*', 
        '<', 
        '{', 
        '+', 
        '!', 
        '?', 
        '[', 
        ';', 
        ']', 
        '$', 
        '%', 
        '@', 
        ','
    ]

    length = len(alphabet.values())
    length_symbols = len(symbols) -1
    length_unit = 9

    first = alphabet["a"]

    last = alphabet["z"]

    a = alphabet["a"]
    b = alphabet["b"]
    c = alphabet["c"]
    d = alphabet["d"]
    e = alphabet["e"]
    f = alphabet["f"]
    g = alphabet["g"]
    h = alphabet["h"]
    i = alphabet["i"]
    j = alphabet["j"]
    k = alphabet["k"]
    l = alphabet["l"]
    m = alphabet["m"]
    n = alphabet["n"]
    o = alphabet["o"]
    p = alphabet["p"]
    q = alphabet["q"]
    r = alphabet["r"]
    s = alphabet["s"]
    t = alphabet["t"]
    u = alphabet["u"]
    v = alphabet["v"]
    w = alphabet["w"]
    x = alphabet["x"]
    y = alphabet["y"]
    z = alphabet["z"]

    def letter(value: int, random: int = 0) -> str:
        """ Returns the letter by its equivalent value"""
        al = alphabet.alphabet
        if random > 0:
            al = alphabet.alphabet_random[random-1]
        
        for key in al.keys():
            if value == al[key]:
                return key
            
            
    def value(letter: str, random: int = 0) -> int:
        """ Returns the value by its equivalent letter"""
        al = alphabet.alphabet
        if random > 0:
            al = alphabet.alphabet_random[random-1]
            
        return al[letter]


    def symbol(index: int) -> str:
        """ Returns the symbol by its equivalent index"""
        return alphabet.symbols[index]


    def limit_length(value: int, limit: int = length) -> int:
        r = 0
        
        if value == 0:
            return 1
        
        if value < 0:
            value = value * -1
            
        for c in range(0, value):
            if r == limit:
                r = 1
            else:
                r += 1
            
        return r


    def minus_letter(letter: int, minus: int, limit: int = length) -> int:
        if letter == 0:
            return 1
        
        for c in range(0, minus):
            letter -= 1
            if letter == 0:
                letter = -1
                
        if letter < 0:
            letter *= -1
            
        return letter


    def decimal(value: str) -> str:
        v = int(value)
        if v < 0:
            v = v * -1
        
        if v < 10:
            return f"0{v}"
        elif v > 99:
            return str(v)[:2]
        else:
            return str(v)


    def unit(value: str) -> str:
        v = int(value)
        if v < 0:
            v = v * -1
            
        if v > 9:
            return str(v)[-1]
        else:
            return str(v)
    
import math

class EncodeTypes:
    O15C = "O15C"
    T6C = "T6C"
    T16C = "T16C"


class Encoder:
    def __init__(self) -> None:
        self.__secret_key = 11
        
        
    def encode(self, key_word: str, altt: int = 1, type: str = EncodeTypes.T16C, email: str = None) -> str:
        "Generate password here."
        
        var_x = self.__encode_with_secret_key(key_word[0])
        var_y = self.__encode_with_secret_key(key_word[-1])
        var_z = len(key_word)
        
        if type == EncodeTypes.T6C:
            return self.enT6C(var_x, var_y, var_z, altt)
        
        elif type == EncodeTypes.T16C:
            return self.enT16C(var_x, var_y, var_z, altt)
        
        elif type == EncodeTypes.O15C:
            return self.enO15C(key_word[0], key_word[-1], var_z, altt, email)
        
        else:
            raise Exception("Unknown Encode Type")
            
            
    def enT6C(self, var_x: str, var_y: str, var_z: int, altt: int) -> str:
        """
        uppercase: 2/2 
        lowercase: 2/2
        simbols: 1/1
        numbers: 1/1
        total: 6/6
        """
        password = ""
        vvar_x = alphabet.value(var_x)
        vvar_y = alphabet.value(var_y)
        
        # R1
        password += alphabet.letter(alphabet.limit_length(int((vvar_x*82 + vvar_y) / 83) - var_z + altt - self.secret_key + 2), random=1).lower()
        
        # R2
        password += alphabet.unit(int((vvar_x + vvar_y ** var_z - 23) / altt))
        
        # R3
        password += alphabet.symbol(alphabet.limit_length((vvar_x - (var_z * altt) - self.__secret_key), alphabet.length_symbols))
        
        # R4
        password += alphabet.letter(alphabet.limit_length(vvar_y + vvar_y + var_z + altt), random=2).upper()
        
        # R15
        password += alphabet.letter(alphabet.limit_length(vvar_x - 13 + altt + var_z), random=3).upper()
        
        # R14
        password += alphabet.letter(alphabet.limit_length(vvar_y + 90 - altt - var_z), random=4).lower()

        return password
            
            
    def enT16C(self, var_x: str, var_y: str, var_z: int, altt: int) -> str:
        """
        uppercase: 4/4 
        lowercase: 4/4
        simbols: 4/4
        numbers: 4/4
        total: 16/16
        """
        password = ""
        vvar_x = alphabet.value(var_x)
        vvar_y = alphabet.value(var_y)
        
        # R1
        password += alphabet.letter(alphabet.limit_length(vvar_x + vvar_y + var_z + altt), random=5).upper()
        
        # R2
        password += alphabet.letter(alphabet.limit_length(math.floor((vvar_x + vvar_y) / 2) * (altt + var_z)), random=6).lower()
        
        # R3
        password += alphabet.symbol(alphabet.limit_length(math.floor(math.sqrt((vvar_y + altt + var_z) ** 3)), alphabet.length_symbols))
         
        # R4
        password += alphabet.symbol(alphabet.limit_length(math.floor(math.sqrt(altt ** 3) + ((vvar_x + var_z) / 2)), alphabet.length_symbols))
         
        # R5
        password += str(alphabet.limit_length(math.floor((vvar_x * 10 + vvar_y + (var_z - altt)) / 11), alphabet.length_unit))
        
        # R6
        password += alphabet.letter(alphabet.limit_length(int(vvar_x - (vvar_y * 3.5) + var_z + altt), alphabet.length_unit), random=7).upper()
         
        # R7
        password += alphabet.decimal(alphabet.limit_length(math.floor(((vvar_x*260) + (vvar_y*171))/431 - (var_z + altt)), 99))
        
        # R8 
        password += alphabet.letter(alphabet.limit_length(vvar_x + vvar_y - var_z), random=8).lower()
        
        # R9 
        password += alphabet.symbol(alphabet.limit_length((vvar_y - (var_z * altt) - self.__secret_key), alphabet.length_symbols))
        
        # R10 
        password += alphabet.letter(alphabet.limit_length(int((vvar_x*27 + vvar_y) / 29) - var_z + altt - self.secret_key), random=9).lower()
        password += alphabet.letter(alphabet.limit_length(int((vvar_y*81 + vvar_y) / 38) - var_z + altt - self.secret_key), random=10).lower()
        
        # R11
        password += alphabet.letter(alphabet.limit_length(self.__secret_key + vvar_x - altt - var_z), random=5).upper()
        
        # R12
        password += alphabet.symbol(alphabet.limit_length(vvar_x + 77 - altt + var_z, alphabet.length_symbols))
        
        # R13
        password += alphabet.unit(int((vvar_x - vvar_y ** var_z) / altt))
        
        # R14
        password += alphabet.letter(alphabet.limit_length(vvar_y - 41 + altt + var_z), random=3).upper()
        
        return password
            
            
    def enO15C(self, var_x: str, var_y: str, var_z: int, altt: int, email: str) -> str:
        """
        uppercase: 2/2 
        lowercase: 5/5
        simbols: 3/3
        numbers: 5/5
        total: 15/15
        """
        password = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "] # 15 caracteres
        vvar_x = alphabet.value(var_x)
        vvar_y = alphabet.value(var_y)
        
        # R1
        password[0] = var_x.lower()
        password[-1] = var_y.lower()
        
        # R2
        add = str(313 + vvar_x + vvar_y)
        password[1] = add[0]
        password[2] = add[1]
        password[3] = add[2]
        
        # R3
        password[4] = alphabet.letter(alphabet.limit_length(vvar_x + 3)).upper()
        password[11] = alphabet.letter(alphabet.limit_length(vvar_y + 3)).upper()
        
        # R4
        password[5] = alphabet.letter(alphabet.minus_letter(vvar_x, 3)).lower()
        password[10] = alphabet.letter(alphabet.minus_letter(vvar_y, 3)).lower()
        
        # R5
        password[6] = alphabet.letter(alphabet.limit_length(altt))
        
        # R6
        calc = 20 - (vvar_x + vvar_y)
        add = calc if calc >= 0 else calc * -1
        add = alphabet.decimal(add)
        password[12] = add[0]
        password[13] = add[1]
        
        # R7
        calc = vvar_x + vvar_y
        if calc < 12:
            add = "@#$"
        elif calc < 22:
            add = "*()"
        elif calc < 32:
            add = "_&+"
        elif calc < 42:
            add = ";!?"
        else:
            add = "[]/"
        password[7] = add[0]
        password[8] = add[1]
        password[9] = add[2]
        
        # R8
        if email != None:
            password.append(str(10 + alphabet.value(email)))
        
        return "".join(password)
    
    
    def __encode_with_secret_key(self, letter: str) -> str:
        "Uses the secret_key to encode a letter."
        n_letter = alphabet.alphabet[letter.lower()]
        n_letter = alphabet.limit_length(n_letter + self.__secret_key)
        return alphabet.letter(n_letter)
        
        
    @property
    def secret_key(self) -> None:
        #raise Exception("You cannot access the secret_key")
        return self.__secret_key
    
    
    @secret_key.setter
    def secret_key(self, value: int) -> None:
        __sk = list(str(value))
        __sk = int(__sk[0]) + int(__sk[1]) + int(__sk[2]) + int(__sk[3])
        
        for c in range(0, value):
            __sk += 1
            if __sk == 99:
                __sk = 0
        
        self.__secret_key = __sk


if __name__ == "__main__":

    import sys
    debug = False
    if len(sys.argv) > 1:
        debug = True if sys.argv[1] == "--d" else False
    
    import getpass
    secret_key = None
    encoder = Encoder()
    while True:
        secret_key = getpass.getpass("SECRET_KEY (4 numbers or none): ")
        if secret_key == "":
            exit()
            
        try:
            if len(secret_key) >= 4:
                encoder.secret_key = int(secret_key)
                break
        except:
            pass
    
    while True:
        try: 
            plataform = input("PLATAFORM: ")
            if plataform == "":
                break
            elif len(plataform) >= 2:
                while True:
                    altt = input("ALTT: ")
                    if altt == "" or altt.isnumeric():
                        altt = int(altt) if altt.isnumeric() else 1
                        
                        cls()
                        
                        print("--------- Generated Passwords ---------")
                        print(f"=> {str(plataform).upper()} <=\n")
                        print(f"O15C:   {encoder.encode(plataform, altt, EncodeTypes.O15C, 'v')}")
                        print(f"T16C:   {encoder.encode(plataform, altt, EncodeTypes.T16C)}")
                        print(f"T6C:    {encoder.encode(plataform, altt, EncodeTypes.T6C)}\n")
                        break
        except Exception as error:
            if debug:
                raise error()
            else:
                cls()
                print(f"ERROR: {error}")
