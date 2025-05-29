import random
import os

with open('usa.txt') as file:
    lst = [line.strip() for line in file]


char_len = int(input("Enter length of word (3-12): "))
while char_len not in range(3, 13):
    char_len = int(input("Enter length of word (3-12): "))
    
word = lst[random.randint(0,len(lst))]
while len(word) != char_len:
    word = lst[random.randint(0,len(lst))]


pattern = list('-' * char_len)

def indexes(s, c):
    ins = []
    for i in range(len(s)):
        if s[i] == c:
            ins.append(i)
    return ins

def insert_ins(p, ins, c):
    for i in ins:
        p[i] = c
    return p

#GAME_LOOP
tries_count = 0
while pattern != list(word):
    os.system('cls')
    print(''.join(pattern))
    char = input("Enter char to guess: ")
    while len(char) != 1:
        char = input("Pleaser enter 1 valid character: ")
            
    ins = indexes(word, char)
    pattern = insert_ins(pattern, ins, char)
    
    tries_count += 1
    
os.system('cls')
print(f"Congrats, you did this at {tries_count}'s try")
print(word)

