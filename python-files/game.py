import random

def guess_number():
    print("be bazie hads adad khosh amadid!")
    number_to_guess = random.randint(1, 100)
    attempts = 0

    while True:
        guess = input("adad ro beyne 1 ta 100 entekhab namaeid:")
        
        # بررسی اینکه ورودی عددی باشد
        if not guess.isdigit():
            print("lotfan, yek adad vared konid.")
            continue
        
        guess = int(guess)
        attempts += 1

        if guess < number_to_guess:
            print("adad bozorg tar ast")
        elif guess > number_to_guess:
            print("adad kochak tar ast.")
        else:
            print(f"tabrik! adade dorost ro yafti!{attempts} تلاش حدس زدی!")
            break

if __name__ == "__main__":
    guess_number()
    