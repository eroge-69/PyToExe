import random
import string


length = 12

characters = string.ascii_letters + string.digits

password = ''.join(random.choice(characters) for _ in range(length))

print("Случайный пароль:", password)

print ("Вы хочите сгенирировать ещё один пароль, напишите Да")
word = input ()
if word == "Да":
    import random
import string


length = 12

characters = string.ascii_letters + string.digits

password = ''.join(random.choice(characters) for _ in range(length))

print("Случайный пароль:", password)
