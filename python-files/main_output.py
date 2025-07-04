import time

wait = .03

def start_sequence(string):
    # define word and set to default letter
    # starting string will convert letters to a's 
    # nums to 1's, and all else will stay the same
    
    word = "" # define empty
    # loop through and set to defaults
    for char in string:
        if char.isalpha():
            if char.isupper():
                word += "A"
            else:
                word += "a"
        elif char.isdigit():
            word += "0"
        elif char == " ":
            word += " "
        else:
            word += char
    
    print(word)
    
    # do effect idk
    word_index = 0
    for char in word:
        # get the goal character from string provided
        goal_char = string[word_index]
        char_code = ord(char)
        
        # if char is not already the correct one continue
        if char != goal_char:
            # if its a letter then loop through until match
            if char.isalpha():
                # set number for loop logic
                current_code = char_code
                while chr(current_code) != goal_char:
                    word = word[:word_index] + chr(current_code+1) + word[word_index + 1:]
                    current_code += 1
                    print(word)
                    time.sleep(wait)
            # if its a nuber increase until match
            if char.isdigit():
                # set number for loop logic
                current_code = 0
                while str(current_code) != goal_char:
                    word = word[:word_index] + str(current_code+1) + word[word_index + 1:]
                    current_code += 1
                    print(word)
                    time.sleep(wait)
        
        word_index += 1
    
    print(word) 

def main():
    while True:
        # console stuff
        print("\n")
        print("="*100)
        # get word from
        word = input("Input something for the effect: \n")
        # more console stuff
        print("="*25, end="")
        print(" Input: " + word, end=" ")
        print("="*25)
        # do text effect
        start_sequence(word)
        

    
main()
