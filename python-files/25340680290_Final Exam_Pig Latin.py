import sys
import re

vowels = set('aeiouAEIOU')

def pig_latin(word):
    if word[0] in vowels:
        return word + 'ay'
    else:
        return word[1:] + word[0] + 'ay'

for line in sys.stdin:
    # Use regex to split into words and non-words
    parts = re.findall(r'[A-Za-z]+|[^A-Za-z]+', line)
    result = []
    for part in parts:
        if part.isalpha():
            result.append(pig_latin(part))
        else:
            result.append(part)
    print(''.join(result), end='')