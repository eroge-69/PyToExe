import random

words = ['Teacher', 'doctor', 'chef', 'student', 'pilot', 'firefighter', 'school', 'restaurant', 'hospital', 'library', 'forest', 'theater', 'phone', 'pencil', 'computer', 'chair', 'table', 'carpet', 'bookshelf', 'window', 'clock', 'horse', 'fish', 'rabbit', 'elephant', 'squirrel', 'freedom', 'confidence', 'honesty', 'intelligence', 'loyalty', 'happiness', 'peace', 'patience', 'classroom', 'deadline', 'hairbrush']
word = random.choice(words)
guessed = set()
tries = 6
while tries > 0:
    display = [letter if letter in guessed else '-' for letter in word]
    print('word:', ' '.join(display))
    guess = input('guess a letter: ').lower()
    if len(guess) != 1 or not guess.isalpha():
        print('please enter a single letter.')
        continue
    if guess in guessed:
        print('you already guessed that letter.')
        continue
    guessed.add(guess)
    if guess in word:
        print('good guess!')
        if all(letter in guessed for letter in word):
            print(f'congratulations! you guessed the word: {word}')
            break
    else:
        print('wrong guess.')
        tries -= 1
        print(f'tries left: {tries}')
else:
    print(f'game over! the word was: {word}')