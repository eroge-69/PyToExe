import random
import re

# Global değişkenleri ve fonksiyon isimlerini rastgele değiştirme
def obfuscate_globals(code):
    globals = {}
    
    # Global değişkenleri ve fonksiyonları bul
    tokens = re.findall(r'\b\w+\b', code)

    # Her bir unique token için rastgele isimler oluştur
    for word in tokens:
        if word not in globals and word not in ['local', 'function', 'end', 'print', 'return']:  # bazı LUA anahtar kelimelerini atla
            globals[word] = "var" + str(random.randint(1000, 9999))  # Rastgele isim oluştur

    # Yeni isimleri koda yerleştir
    for old, new in globals.items():
        code = code.replace(old, new)
    
    return code

# String şifreleme
def obfuscate_string(s):
    encoded = ''.join([f"\\{ord(c)}" for c in s])  # String'in her karakterinin ASCII değerini al
    return encoded

# Tüm metindeki string'leri obfuscate et
def obfuscate_code(code):
    # String'leri bul ve şifrele
    code = re.sub(r'"([^"]*)"', lambda m: f'"{obfuscate_string(m.group(1))}"', code)
    code = re.sub(r"'([^']*)'", lambda m: f"'{obfuscate_string(m.group(1))}'", code)
    
    # Global değişkenleri obfuscate et
    code = obfuscate_globals(code)
    
    return code

# Obfuscate edilecek örnek LUA kodu
lua_code = """
local x = 5
print(x)
function say_hello()
    print("Hello World")
end
"""

# Obfuscate edilen kodu al
obfuscated_code = obfuscate_code(lua_code)

# Sonucu yazdır
print("Obfuscated Code:")
print(obfuscated_code)
