import random
from english_words import get_english_words_set
import os
import time
from datetime import date
import sqlite3

conn = sqlite3.connect('highscores.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS highscores (score INTEGER NOT NULL, date TEXT NOT NULL, name TEXT NOT NULL, time TEXT NOT NULL)')
english_words=get_english_words_set(['web2'], lower=True)

def clear_terminal():
    #Clear the terminal.
    os.system('cls' if os.name == 'nt' else 'clear')   

def is_lose(number):
    #Check if the player has lost.
    if number==12:
        return "You loose."

def random_element(item_set):
    #Return a random element from a set.
    return random.choice(list(item_set))

def underscores(word_input):
    #Replace each letter in a word with an underscore.
    blank_word=""
    for char in word_input:
        blank_word+="_"
    return blank_word

def hangman(player_name):
    #Function of the game.
    word=random_element(english_words)
    penalty=0
    list_word=underscores(word)
    already_guessed=[]
    
    while penalty<12:
        list_word=list(list_word)
        list_word=''.join(list_word)        
        clear_terminal()
        #print(word) #Remove "#" for debugging.
        print(list_word, " | ", penalty, " / 12 penalties. Letters already guessed:", str(already_guessed).strip('[]').replace("'", ""))
        start_time=time.time()
        letter=input("Enter a letter: ").lower()
        if len (letter)!=1:
            clear_terminal()
            print("Enter only one letter.")
            time.sleep(1)
            continue
        if letter in already_guessed:
            clear_terminal()
            print("You already guessed that letter.")
            time.sleep(1)
            continue

        if letter in word:
            for i in range(len(word)):
                if word[i]==letter:
                    list_word=list(list_word)
                    list_word[i]=letter
        else:
            if not letter in already_guessed and len(letter)==1:
                penalty+=1
        if not letter in already_guessed:
            already_guessed+=letter
        
        if "_" not in list_word:
            clear_terminal()
            end_time=time.time()
            elapsed_time=end_time-start_time
            elapsed_time=round(elapsed_time, 2)
            print("You win. Word was:", word)
            break
    if penalty==12:
        clear_terminal()
        print(is_lose(penalty), "Word was:", word)
    cursor.execute('SELECT * FROM highscores ORDER BY score DESC')
    high=cursor.fetchone()
    if high!=None:
        print("Current high score:", high[0], "penalties on", high[1], "in", high[3])
        time.sleep(2)
        clear_terminal()
        if high==[] or penalty<high[0]:
            print("New high score!")
            print("Score:", penalty, "penalties on", date.today())
            cursor.execute('INSERT INTO highscores (score, date, name, time) VALUES (?, ?, ?, ?)', (penalty, str(date.today()), player_name, str(elapsed_time)))
            input("Press Enter to return to the main menu.")   
    else:
        clear_terminal()
        print("New high score!")
        print("Score:", penalty, "penalties on", date.today(), "in", str(elapsed_time))
        cursor.execute('INSERT INTO highscores (score, date, name, time) VALUES (?, ?, ?, ?)', (penalty, str(date.today()), player_name, str(elapsed_time)))
        input("Press Enter to return to the main menu.")
    conn.commit()
    menu()

def leaderboard():
    #Display leaderboard.
    sort_by=input("Sort by (1) penalties, (2) time: ")
    if sort_by=="1":
        cursor.execute('SELECT * FROM highscores ORDER BY score ASC')
    elif sort_by=="2":
        cursor.execute('SELECT * FROM highscores ORDER BY time ASC')
    else:
        clear_terminal()
        print("Invalid choice.")
        time.sleep(1)
        leaderboard()
    highscores=cursor.fetchall()
    clear_terminal()
    print("Leaderboard:")
    for score in highscores:
        print(score[2], " - ", score[0], "penalties on", score[1], "in", score[3])
    input("Press Enter to return to the main menu.")
    menu()

def menu():
    #Display main menu.
    clear_terminal()
    print("Welcome to Hangman!")
    print("1. Start Game")
    print("2. Leaderboard")
    print("3. Quit")
    choice=input("Enter your choice: ")
    if choice=="1":
        player_name=input("Enter your name: ")
        clear_terminal()
        hangman(player_name)
    elif choice=="2":
        leaderboard()
    elif choice=="3":
        clear_terminal()
        print("Goodbye!")
        time.sleep(1)
        clear_terminal()
        conn.close()
        exit()
    else:
        clear_terminal()
        print("Invalid choice.")
        time.sleep(1)
        menu()



menu()