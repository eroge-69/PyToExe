import random

score = 0 
enscore = 0
match = 0
cardbackupop = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 50, 50, 50, 50]
cardbackup = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 50, 50, 50, 50]
cardlistpl = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 50, 50, 50, 50]
cardlistop = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 50, 50, 50, 50]


def playgame():
    global match
    global enscore
    global score
    global cardlistpl
    global cardlistop
    plcard = random.choice(cardlistpl)
    opcard = random.choice(cardlistop)
    print(f'\nopponent card: {opcard}')
    cardflip = input('reveal your card? (y/n): ')
    if cardflip == 'y':
        print(f'your card: {plcard}')
        if plcard > opcard:
            print('\nYOU WIN (+1 point)\n')
            score = score + 1 
            enscore = enscore
        elif plcard < opcard:
            print('\nyou lost... (+1 enemy point)\n')
            score = score
            enscore = enscore + 1
        elif plcard == opcard:
            print('\nit was a tie (+0 point)\n')
            score = score
            enscore = enscore
    else:
        print('\n<returning to menu>')
    cardlistpl.remove(plcard)
    cardlistop.remove(opcard)
    match = match + 1
    if match == 52:
        print(f'\n@@@@@@@@@@@@@@@\nthat is the end of this game\nyour points: {score}\nopponent points: {enscore}\n@@@@@@@@@@@@@@@')
        exit()
    elif len(cardlistpl) == 0 or len(cardlistop) == 0:
        print(f'\n@@@@@@@@@@@@@@@\nthat is the end of this game\nyour points: {score}\nopponent points: {enscore}\n@@@@@@@@@@@@@@@')
        exit()


    menu()
    return match

def menu():
    global enscore
    global score
    global cardlistpl
    global cardlistop
    choice = input('<><><><><>\nWhat is your action?\n1: play match\n2: view remaining cards\n3: reset\n<><><><><>\n')
    if choice == '1':
        playgame()
    elif choice == '2':
        print(cardlistpl)
        menu()
    elif choice == '3':
        print('\nresetting...')
        cardlistpl = cardbackup
        cardlistop = cardbackupop
        score = 0
        enscore = 0
        menu()
    return choice




menu()