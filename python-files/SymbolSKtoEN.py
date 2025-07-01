import sys
import csv

def convert_char(char):
    match char:
        case 'á' | 'ä': return 'a'
        case 'č': return 'c'
        case 'ď': return 'd'
        case 'é': return 'e'
        case 'í': return 'i'
        case 'ĺ' | 'ľ': return 'l'
        case 'ň': return 'n'
        case 'ó' | 'ô': return 'o'
        case 'ŕ': return 'r'
        case 'š': return 's'
        case 'ť': return 't'
        case 'ú': return 'u'
        case 'ý': return 'y'
        case 'ž': return 'z'
        case 'Á' | 'Ä': return 'A'
        case 'Č': return 'C'
        case 'Ď': return 'D'
        case 'É': return 'E'
        case 'Í': return 'I'
        case 'Ĺ' | 'Ľ': return 'L'
        case 'Ň': return 'N'
        case 'Ó' | 'Ô': return 'O'
        case 'Ŕ': return 'R'
        case 'Š': return 'S'
        case 'Ť': return 'T'
        case 'Ú': return 'U'
        case 'Ý': return 'Y'
        case 'Ž': return 'Z'
        case _: return char  # default: return unchanged character

def convert_slovak_to_english(text):
    return ''.join(convert_char(char) for char in text)



file_path = ""
file_text = ""
result = []


if __name__ == "__main__":

    file_path = sys.argv[1]

    file_text = open(file_path, "r")


    for line in file_text.readlines():
        result.append(convert_slovak_to_english(line))


    file_text = open(file_path, "w")


    for line in result:
        file_text.write(line)
            