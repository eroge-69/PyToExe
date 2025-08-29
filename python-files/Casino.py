import random
import time

cash = float(100)
print(f'Your balance: ${cash:.2f}')

colours = ['black', 'red', 'green']
rarity = [0.47, 0.47, 0.06]

def shuffle(cash):

    try:
        bet = float(input('How much you want to bet ?\n'))
    except ValueError:
        print('Only Numbers Please!')
        shuffle(cash)
        return

    while True:
        
        if bet <= 0:
            bet = float(input('You can not bet less than $1\n'))
        elif bet > cash:
            bet = float(input('You can not afford that much, bet lower.\n'))
        elif bet > 0 and bet <= cash:
            break

    choice = input('Which color do you choose ?\n').lower()
    while choice not in colours:
        choice = input('Choose one of colors:\nBlack, red, Green.\n')
        if choice in colours:
            break

    if choice in colours:
        print('Okay, Let the game begin!\n')
        countdown = 3
        while countdown != 0:
            print(countdown)
            countdown -= 1
            time.sleep(1)

        x = random.choices(colours, rarity)[0]
        print('\n' + x)

    if (choice == 'black' or choice == 'red') and choice == x:
        print(f'\nYou Won ${bet:.2f}, Congrats!')
        cash += bet
        print(f'Your balance: ${cash:.2f}') 
    elif choice == 'green' and choice == x:
        print(f'\nYou Won ${bet*35:.2f}, Congrats!')
        cash += bet*35
        print(f'Your balance: ${cash:.2f}')
    else:
        print(f'\nUnfortunetly You Lost ${bet:.2f}.')
        cash -= bet
        print(f'Your balance: ${cash:.2f}')
    
    if cash >= float(5000):
        print('\nYou made $5000! You won the game!\n')
        quit()
    
    if cash < 1:
        print('\nYou are poor, You lost.\n')
        quit()

    again = input('\nDo you want to play again ?\n').lower()
    def yes_or_no(again):
        if again == 'yes':
            shuffle(cash)
        elif again == 'no':
            print('Thank for playing! Bye!')
        else:
            again = input('I dont uderstand. Do you want to play again ?\n')
            yes_or_no(again)
    yes_or_no(again)
        


shuffle(cash)