import random
import time

print('sud\'s (painfully realistic) case opening simulator v 1.0')

def timer(): #note: it's best to print(timer()), since 'flush=True' causes next line to show on same line as timer

    timer_length = 3

    while True:

        if timer_length >= 1:
            print(timer_length, end=' ', flush=True)
            timer_length -= 1
            time.sleep(1)
        else:
            return ''
            break

def loading_dots():

    print('.', end='', flush=True)
    time.sleep(0.35)
    print('.', end='', flush=True)
    time.sleep(0.35)
    print('.')

ESC = '\x1b'
BLUE = ESC + '[36m'
PURPLE = ESC + '[34m'
PINK = ESC + '[35m'
RED = ESC + '[31m'
GOLD = ESC + '[33m'
reset_txt_color = ESC + '[m'

while True:

    possible_items = range(1, 386)
    list_items = list(possible_items)
    item_unboxed = random.choice(list_items)
    txt_color = ()

    if 1 <= int(item_unboxed) <= 307:
        item_unboxed = 'mil-spec (blue)'
        txt_color = BLUE
    elif 308 <= int(item_unboxed) <= 369:
        item_unboxed = 'restricted (purple)'
        txt_color = PURPLE
    elif 370 <= int(item_unboxed) <= 381:
        item_unboxed = 'classified (pink)'
        txt_color = PINK
    elif 382 <= int(item_unboxed) <= 384:
        item_unboxed = 'covert (red)'
        txt_color = RED
    elif int(item_unboxed) == 385:
        item_unboxed = 'knife!! (gold)!'
        txt_color = GOLD

    is_statty = False
    determine_statty = range(1, 11)
    list_statty = list(determine_statty)
    statty = random.choice(list_statty)

    if 1 <= statty <= 9:
        is_statty = False
    elif statty == 10:
        is_statty = True


    if input(reset_txt_color + '\nPress \'Enter\' to open a case, or type anything else to quit: ') == '':
        print('\nOpening case in...', end=' ', flush=True)
        time.sleep(1)
        print(timer())
        time.sleep(1)
        loading_dots()
        time.sleep(3)
        if is_statty == False:
            print(txt_color + '\nYou unboxed a ' + item_unboxed + '!')
        elif is_statty == True:
            print(txt_color + '\nYou unboxed a StatTrak ' + item_unboxed + '!')
    else:
        break