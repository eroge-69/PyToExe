import random

while True:
    passl = input("how many digits do you want your password to be?")
    try:
        e = int(passl)
    except ValueError:
        print("That's not a number.")
        continue

    if e >= 26 or e <= 0:
        print("password does not fit the requirements of 1-25 digits please try again")
        continue
    else:
        break


password = "".join(random.choice("qwertyuiopåasdfghjklæøzxcvbnm,.-'¨´+!@£$€&/[{]}0123456789") for x in range(e))

print(f"your password is {password}")