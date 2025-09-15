
def decrypt_text_fixed(encrypted_text, alphabet_map):
    """
    Расшифровывает текст, используя заданный алфавит, с исправлением неоднозначности.
    """
    decrypted_result = []    
    
    
    reverse_alphabet_map = {}
    
    for original, encrypted in alphabet_map.items():
        reverse_alphabet_map[encrypted] = original
           
    
    if 'р' in alphabet_map.values(): # Проверяем, есть ли 'р' среди зашифрованных символов
        reverse_alphabet_map['р'] = 'т' # Устанавливаем, что 'р' расшифровывается в 'т'
       
           
    temp_reverse_map = {}
    for original, encrypted in alphabet_map.items():
        
        temp_reverse_map[encrypted] = original

    if 'р' in temp_reverse_map:
        temp_reverse_map['р'] = 'т' 
        
    reverse_alphabet_map = temp_reverse_map

    for char in encrypted_text:
        if char in reverse_alphabet_map:
            decrypted_result.append(reverse_alphabet_map[char])
        else:
            decrypted_result.append(char)
            
    return "".join(decrypted_result)

def main():
    alphabet_map = {
        'а': '>', 'б': 'и', 'в': 'ж', 'г': 'у', 'д': 'л', 'е': '¿', 'ё': 'ю',
        'ж': '#', 'з': '!', 'и': '^', 'й': '•', 'к': '|', 'л': '+', 'м': '&',
        'н': '$', 'о': '¡', 'п': '=', 'р': 'т', 'с': 'щ', 'т': 'р', 'у': 'б',
        'ф': 'й', 'х': 'я', 'ц': 'ы', 'ч': 'г', 'ш': 'н', 'щ': 'м', 'ъ': 'ё',
        'ы': 'ш', 'ь': 'о', 'э': 'ф', 'ю': 'з', 'я': 'в',
        ' ': '/', '.': '@', ',': '%', ':': '?', '-': '*', '(': '₽', ')': '£'
    }

    print("Введите текст для расшифровки:")
    user_input = input()

    decrypted_text = decrypt_text_fixed(user_input, alphabet_map)
    print("\nРасшифрованный текст:")
    print(decrypted_text)

if __name__ == "__main__":
    main()
