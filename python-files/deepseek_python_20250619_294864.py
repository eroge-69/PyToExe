# Kyro_dtrc_Key Şifreleme Sistemi

class KyroCipher:
    def __init__(self):
        # Şifreleme kılavuzu (alfabe)
        self.kyro_alphabet = {
            'a': 'aaa', 'b': 'aa', 'c': 'k', 'd': 'dtrc', 'e': 'r', 'f': 'cc',
            'g': '5', 'h': 't', 'i': '9', 'j': 'jj', 'k': 'xx', 'l': 'll',
            'm': 'mm', 'n': 'nn', 'o': 'oo', 'p': 'pp', 'q': 'qq', 'r': 'rr',
            's': 'ss', 't': 'tt', 'u': 'uu', 'v': 'vv', 'w': 'ww', 'x': 'xy',
            'y': 'yy', 'z': 'zz', ' ': '___', '?': '???', '!': '!!!'
        }
        self.reverse_kyro = {v: k for k, v in self.kyro_alphabet.items()}

    def encrypt(self, text):
        """Metni Kyro_dtrc_Key ile şifreler"""
        text = text.lower()
        encrypted = []
        for char in text:
            encrypted.append(self.kyro_alphabet.get(char, f'[{char}]'))
        return ' '.join(encrypted)

    def decrypt(self, code):
        """Kyro_dtrc_Key şifresini çözer"""
        parts = code.split()
        decrypted = []
        for part in parts:
            decrypted.append(self.reverse_kyro.get(part, f'[{part}]'))
        return ''.join(decrypted)

    def show_guide(self):
        """Şifreleme kılavuzunu gösterir"""
        print("\n\033[1;36m🔐 Kyro_dtrc_Key Şifreleme Kılavuzu 🔐\033[0m")
        print("\033[1;34m{:<5} {:<10} {:<5} {:<10}\033[0m".format(
            "Harf", "Kod", "|", "Harf", "Kod"))
        print("-"*35)
        
        items = sorted(self.kyro_alphabet.items())
        half = len(items) // 2 + 1
        
        for i in range(half):
            left = items[i] if i < len(items) else ('', '')
            right = items[i+half] if i+half < len(items) else ('', '')
            
            print("\033[1;33m{:<1}\033[0m {:<10} {:<5} \033[1;33m{:<1}\033[0m {:<10}".format(
                left[0], left[1], "|", 
                right[0], right[1]))


def display_banner():
    """Program başlığını gösterir"""
    print("\033[1;35m" + "="*50 + "\033[0m")
    print("\033[1;32m{:^50}\033[0m".format("KYRO_DTRC_KEY ŞİFRELEME SİSTEMİ"))
    print("\033[1;35m" + "="*50 + "\033[0m")
    print("\033[3;36mGizli mesajlar oluşturmak için güçlü şifreleme\033[0m")
    print("\033[1;35m" + "-"*50 + "\033[0m")


def main():
    cipher = KyroCipher()
    display_banner()
    
    while True:
        print("\n\033[1;34mMENÜ:\033[0m")
        print("\033[1;32m1.\033[0m Metni Şifrele")
        print("\033[1;32m2.\033[0m Şifreyi Çöz")
        print("\033[1;32m3.\033[0m Şifreleme Kılavuzu")
        print("\033[1;32m4.\033[0m Çıkış")
        
        choice = input("\n\033[1;36mSeçiminiz (1-4): \033[0m")
        
        if choice == '1':
            text = input("\n\033[1;33mŞifrelenecek metin: \033[0m")
            encrypted = cipher.encrypt(text)
            print("\n\033[1;32mŞifreli Mesaj:\033[0m \033[3;34m" + encrypted + "\033[0m")
            
        elif choice == '2':
            code = input("\n\033[1;33mÇözülecek şifre: \033[0m")
            decrypted = cipher.decrypt(code)
            print("\n\033[1;32mÇözülmüş Mesaj:\033[0m \033[3;32m" + decrypted + "\033[0m")
            
        elif choice == '3':
            cipher.show_guide()
            
        elif choice == '4':
            print("\n\033[1;35mÇıkılıyor... Güle güle!\033[0m")
            break
            
        else:
            print("\n\033[1;31mGeçersiz seçim! Lütfen 1-4 arasında bir sayı girin.\033[0m")


if __name__ == "__main__":
    main()