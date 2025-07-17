print("Welcome to marco the searcher....")

print("""
   
     .-----.
    /  (o o)  \\   
   |   `---'   |
   '-----------'
     /| | | |\\
    | |=====| |           
    | |`---'| |          
    \\_|_____|_/          
       / \\ / \\         
      /   Y   \\        
     (_/ \\_/ \\_)     

        /\\_/\\
       ( ^.^ )     
        > Q <
       /  ___ \\
      /  /   \\ \\
     (__/     \\__)
     
""")



introduction = ("Marco is a teenboy from Georgia. He has a pet goat named COCO. One day his pet goat COCO suddenly lost..... There was a giant fire dragon\n"
"named Drago Fizz... Let's find out Marcos goat")

print(f"Story: {introduction.title()}")


#Marcos understand....

print(f"Marco: Oh, its evening i should go home. Where is COCO??")
print(f"\nMarco shouted ,,,,, COCO COCO")

print(f"\nI think COCO is lost... I should search him.")

search = input("Do you think Marco should search? ")

if search == 'yes' :
    print("\nLets go..")
elif search == 'no':
    print("\nOkey, lets play another one.")

print(f"\nMarco is walking .. suddenly he saw a board which shows two path.. Left and Right...Which path is correct one you think?")

path = input("Left or Right? ")

if path == 'left':
    print(f'After walking 2 minutes you saw a big empty field...Now can shout..')
    shout = input("Shout? ")

    if shout == 'yes':
        print('COOCOOOOOO!, COCOOOO!')
    else :
        print('I lost my friend COCO..')

elif path == 'right':
    print(f'After 6 mintes of walking.. marco found a giant mountain.. and its the Mountain of Drago fizz...')
    print(f'\n There is a Cave of the Drago Mountain....')

    cave = input('Do you want to enter the cave?:')
    if cave== 'yes':
        print(f'Damn its big and the light is so little.\n\tAfter two minutes of walking there are 2 path of this cave..')

        print(f"Should i enter the path??")

        cave_path = input('Decide Left of Right: ')
        if cave_path == 'left':
            print(f"Marco is walking. after 3 minutes of walking he found COCO.. \n\t He go to the COCO and take it. Then he saw the giant DRAGO FIZZ.\n\t It seam very angry. Drago FIZZ lay down and bring it's face to Marco.")
            marcos=input("What should Marco do now, run or stand: ")
            
            if marcos == 'run':
                print('Run COCO run')
            elif marcos == 'stand':
                print('Marco touch the Dragon and the dragon is peted.... ')
                print('I Am MD.Shariar Hassan Shanto..Thanking for playing this game ... ')
            else:
                print("Game over!")
        elif cave_path == 'right':
            print("Oh there is nothing....")







else:
    print('Game Over!!')

