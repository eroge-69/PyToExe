import os
import datetime
import re
import subprocess
import shutil
import tarfile

def get_user_input():
    # Ask if there's a new file in the syslogs folder
    option2 = input("Have you just downloaded a compressed log file from Garage? y/n: ")
    
    if option2.lower()!= 'y':
        return None
    
    # Get the last 6 digits of the VIN from the user
    vin = input("Enter the last 6 digits of the VIN: ")
    
    return vin

def identify_file(vin):
    # Iterate through files in the syslogs folder
    for filename in os.listdir('/mnt/c/Users/$USER/syslogs'):
        # Check if the VIN is present in the filename
        if vin in filename:
            return filename
    
    return None

def unpack_file(filename, vin):
    # Rename the file
    os.rename(os.path.join('/mnt/c/Users/$USER/syslogs', filename), os.path.join('/mnt/c/Users/$USER/syslogs', f'{vin}.tgz'))
    
    # Extract the file
    with tarfile.open(os.path.join('/mnt/c/Users/$USER/syslogs', f'{vin}.tgz'), 'r') as tar_ref:
        tar_ref.extractall(path=os.path.join('/mnt/c/Users/$USER/syslogs', vin))
    
    # Remove the extracted archive
    os.remove(os.path.join('/mnt/c/Users/$USER/syslogs', f'{vin}.tgz'))

def welcome():
    options = "-ia"
    print("\n\nYou are here:", os.getcwd())
    print("\n\nExample for how to write the time, 2023-04-13_00:00 IN PACIFIC time (-8 hours from Universal Time)")
    
    word = input("What is the timestamp? (even just year or year and month) ")
    word_zzz(word, options)

def word_zzz(word, options):
    print("When the output is displayed, press q to return to the search")
    print("----------------------------------------------------------------")
    print("if you want to add multiple words please use '|' after phrase. example (remote request|spotify|error)")

    if options == "-ia":
        word_2 = input("what word(s) are you searching?  ")
        exclu1 = input("do you want to exclude any words? y/n   ").lower()
        
        if exclu1 == 'y':
            exclu2 = input("what words are we excluding?   ")
            search_and_display(word, word_2, exclu2, options)
        else:
            search_and_display(word, word_2, None, options)
    else:
        word_2 = input("what word(s) are you searching?  ")
        search_and_display(word, word_2, None, options)

def search_and_display(word, word_2, exclu2=None, options=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if options == "-ia":
        pattern = f"{word_2}|alsettesla"
        if exclu2:
            command = f"zcat -rf * | sort | grep {options} '{pattern}' | grep '{word}' | grep -iv '{exclu2}|\\.txt'"
        else:
            command = f"zcat -rf * | sort | grep {options} '{pattern}' | grep '{word}'"

        result = os.popen(command).read()

        save_to_file(result, now, word, word_2)
        display_result(result)
    else:
        pattern = f"{word_2}|alsettesla"
        if exclu2:
            command = f"zgrep {options} '{pattern}' */*/* | grep '{word}' | grep -iv '{exclu2}'"
        else:
            command = f"zgrep {options} '{pattern}' */*/* | grep '{word}'"

        result = os.popen(command).read()

        save_to_file(result, now, word, word_2)
        display_result(result)

def save_to_file(result, now, word, word_2):
    save_choice = input("Would you like to output the results to a text file? y/n    ").lower()
    if save_choice == 'y':
        filename = f"{now}_{word}_{word_2}.txt"
        with open(filename, 'w') as file:
            file.write(re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', result))
        print(f"Results saved to {filename}")

def display_result(result):
    print