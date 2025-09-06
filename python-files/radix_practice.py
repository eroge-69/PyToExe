import random
import os
import time


def main():
    while True:
        clear("=========================================")
        print("        Radix Conversion Practice        ")
        print("=========================================")
        print("A. Practice Mode")
        print("B. Timed Mode (20 Questions)\n")
        while True:
            option = input("Please input your option: ").strip().lower()
            if option in ['a', 'b']:
                print("=========================================")
                break
            else:
                print("Invalid option")
        r1 = check("Convert from base: ", 2, 20)
        r2 = check("To base: ", 2, 20)
        digits = check("How many digits: ", 1, 20)
        print(practice(option == 'b', r1, r2, digits))
        print("=========================================")
        exit = input("Do you want to play again? (y/n):").strip().lower()
        if exit != 'y':
            break


def practice(is_timed, r1, r2, digits):
    clear(f"Convert base-{r1} to base-{r2}.\nEnter x to stop.")
    print("=========================================")
    print("Good Luck!\n")
    score, i, start = 0, 0, time.time()

    while i < 20:
        n = random.randint(r1**(digits-1), (r1**digits)-1)
        q, a = dec_to_base(n, r1), dec_to_base(n, r2)

        while True:
            ans = input(f"{padding(q)} = ").strip().upper()
            if ans == 'X':  # user wants to quit
                return f"Congrats! you got {score} correct!"
            if ans == a or ans == a.zfill((len(a) + 3) // 4 * 4):  # correct
                score += 1
                clear(f"Convert base-{r1} to base-{r2}.\nEnter x to stop.")
                print("=========================================")
                print("Correct!\n")
                if is_timed:  # advance only if timed
                    i += 1
                break
            else:
                clear(f"Convert base-{r1} to base-{r2}.\nEnter x to stop.")
                print("=========================================")
                print("Wrong" + (", try again\n" if not is_timed else "\n"))
    return f"Congrats! you got {score} correct in {time.time()-start} seconds!"


def padding(q):
    if len(q) >= 4:
        q = q.zfill((len(q) + 3) // 4 * 4)  # pad to multiple of 4
        return " ".join(q[i:i+4] for i in range(0, len(q), 4))
    else:
        return q


def dec_to_base(n, b):
    digits = "0123456789ABCDEFGHIJ"
    if n == 0:
        return "0"
    s = ""
    while n:
        s = digits[n % b]+s
        n //= b
    return s


def check(msg, minn, maxx):
    while True:
        n = input(msg)
        if n.isdigit() and minn <= int(n) <= maxx:
            return int(n)
        print("Invalid input")


def clear(msg=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(msg) if msg else None


if __name__ == '__main__':
    main()
