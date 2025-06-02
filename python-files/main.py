# Rock Paper Scissor
import random

score = 0
def play():
    global score
    print(f'Score: {score}')
    print('\n-O  O-\n')
    p = input('rock (r), paper (p) or scissor (s):')
    opt = ['r', 'p', 's']

    ai = opt[random.randint(0, 2)]

    if ai == 'r' and p == 's':
        print('\n-<  o-')
        print('\nLost')
        res = input('Want To Restart (y/n):')
    if ai == 'r' and p == 'p':
        print('\n-#  o-')
        print('\nNice!')
        score += 1
        play()
    if ai == 'p' and p == 's':
        print('\n-<  O-')
        print('\nNice!')
        score += 1
        play()
    if ai == 'p' and p == 'r':
        print('\n-O  #-')
        print('\nLost')
        res = input('Want To Restart (y/n):')
    if ai == 's' and p == 'p':
        print('\n-#  >-')
        print('\nLost')
        res = input('Want To Restart (y/n):')
    if ai == 's' and p == 'r':
        print('\n-O  >-')
        print('\nNice!')
        score += 1
        play()

    if ai == 's' and p == 's':
        print('\n-<  >-')
        print('\nOh! Same')
        play()
    if ai == 'r' and p == 'r':
        print('\n-O  O-')
        print('\nOh! Same')
        play()
    if ai == 's' and p == 's':
        print('\n-#  #-')
        print('\nOh! Same')
        play()
    
    if res == 'y':
        score = 0
        print('\nStarting Game...\n')
        play()
    else:
        pass

def menu():
    print('Welcome To Terminal RockPaperScissor\n\n1.Play\n2.Exit\n')
    i = input('[1 to play, 2 to exit]:')
    if i == '1':
        print('\nStarting Game...\n')
        play()
    if i == '2':
        pass

menu()