import codecs

def read_character_mapping(file_path):
    mapping = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                chinese_char, replacement = line.split('\t')
                mapping[chinese_char] = swap_and_decode(replacement)
    return mapping


def swap_and_decode(text):
    try:
        decoded_text = chr(int(text, 16))
        return decoded_text
    except ValueError:
        return text  # If decoding fails, return the original content


def replace_characters(input_file, output_file, mapping):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    for chinese_char, replacement in mapping.items():
        content = content.replace(chinese_char, replacement)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)


# Read the character mapping
character_mapping = read_character_mapping('手机hex对照表.txt')

# Replace characters and write to the output file
replace_characters('gtavc.txt', 'temp.txt', character_mapping)
