import re

class UnicodeDecoder:
    def __init__(self):
        self.supported_formats = [
            "\\uXXXX (16-битный Unicode)",
            "\\UXXXXXXXX (32-битный Unicode)", 
            "\\xXX (hex escape)",
            "Кодовые точки (U+XXXX)"
        ]
    
    def decode_unicode(self, text):
        """Основная функция декодирования"""
        try:
            # Если это список кодовых точек
            if re.match(r'^[0-9A-Fa-f+\s,]+$', text.strip()):
                return self._decode_from_codepoints(text)
            
            # Если это escape-последовательности
            return text.encode('utf-8').decode('unicode-escape')
            
        except Exception as e:
            return f"Ошибка декодирования: {e}"
    
    def _decode_from_codepoints(self, text):
        """Декодирование из кодовых точек"""
        # Извлекаем кодовые точки вида U+XXXX или просто XXXX
        codepoints = re.findall(r'[Uu]\+?([0-9A-Fa-f]{4,6})|\b([0-9A-Fa-f]{4,6})\b', text)
        
        # Преобразуем найденные точки
        chars = []
        for cp in codepoints:
            # Выбираем непустую группу
            cp_hex = cp[0] if cp[0] else cp[1]
            if cp_hex:
                try:
                    chars.append(chr(int(cp_hex, 16)))
                except ValueError:
                    continue
        
        return ''.join(chars)
    
    def show_supported_formats(self):
        """Показать поддерживаемые форматы"""
        print("Поддерживаемые форматы:")
        for fmt in self.supported_formats:
            print(f"  - {fmt}")

def main():
    decoder = UnicodeDecoder()
    
    print("=== Unicode Decoder ===")
    decoder.show_supported_formats()
    print("\nПримеры ввода:")
    print('  - "\\u041f\\u0440\\u0438\\u0432\\u0435\\u0442"')
    print('  - "U+4F60 U+597D"')
    print('  - "1F600 1F601 1F602"')
    print("\nВведите 'quit' для выхода")
    
    while True:
        user_input = input("\nВведите текст для декодирования: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'выход']:
            break
        
        if not user_input:
            continue
        
        result = decoder.decode_unicode(user_input)
        print(f"Результат: {result}")

if __name__ == "__main__":
    main()