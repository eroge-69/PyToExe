import nltk
from nltk.corpus import wordnet
import random

# Download WordNet
nltk.download('wordnet')
nltk.download('omw-1.4')

def get_random_word_and_meaning():
    words = list(wordnet.words())
    while True:
        word = random.choice(words)
        synsets = wordnet.synsets(word)
        if synsets:
            definition = synsets[0].definition()
            return word, definition

word, meaning = get_random_word_and_meaning()
print(f"Word: {word}
Meaning: {meaning}")
