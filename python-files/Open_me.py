# файл guess_number.py
# импортируем модуль для работы со случайными числами
import random

# число попыток угадать
guesses_made = 0

# получаем имя пользователя из консольного ввода
name = input('Hello.What is your name?\n')
# получаем случайное число в диапазоне от 1 до 30
number = random.randint(1, 30)

if name =='Tarakan':
   print("Wh-hat?That's MY name! How do you know it?!")
elif name =='Zalgo':
   print("Are you kidding me?!Thats MY name!Not your!")
elif name =='Руби':
   print("Привет, Кексик!")
elif name =='Данрив':
   print("Привет, Мандаринка!")
elif name =='Денис':
   print("Привет, Кроличка!")
elif name =='Ruby':
   print("Hi,little cupcake")
elif name =='Denis':
   print("Hi,bunny!")
else:
   print(name+"?Nice name:D")
  

print ('Well,' + name+ ',i wanna play one little game.I shoose number from 1 to 30.Can you guess it?'.format(name))

# пока пользователь не превысил число разрешенных попыток - 6
while guesses_made < 6:
    
    # получаем число от пользователя
    guess = int(input('Your answer?: '))
    
    # увеличиваем счетчик числа попыток
    guesses_made += 1

    if guess < number:
        print ('Your number is less than i shoose.')

    if guess > number:
        print ('Your number is more than i shoose.')

    if guess == number:
        break

if guess == number:
    print ('Wow, {0}! You guessed my number and used only {1} attemps.Good Job!'.format(name, guesses_made))
else:
    print ('You have exhausted my patience, mortal! I shoose a number {0},silly!'.format(number))
    
    