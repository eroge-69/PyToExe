from datetime import datetime
import time
import os

'''Heat Seal Cleaning Tool 0.1

Overview:
    Run as a shortcut to writing CMMS entries for trivial tasks such as heat seal cleaning. This 
    is only meant to replace the word document full of templates that many techs use daily.

How to Use This Thing:
    Running this script will prompt "Lot Number: J003" and "TS: " which are not case sensitive. 
    Type these in and press <ENTER>. The entry, along with the correct hour, is scrolled out on 
    the screen. It is immediatly added to your clipboard ready to be pasted in where needed.
    For the sake of simplicity, Edits CANNOT be made here.

Release Notes:
    0.1
        Bare bones just to get the thing working. Python with default libraries used only.
        os, time, datetime used to write to command line and find the time of day.
        tkinter gui in the works but not currently utilized.
    0.2
        TBA
'''

#window = tk.Tk()
#window.title('CMMS Entry Tool')

def scroll(text, delay=0.01):
    x = 0
    for i in text:
        # Prints single letter, doesn't create a newline, and automatically updates line instead of waiting for function to finish
        print(i, end='', flush=True)
        if(x%4==0):
            time.sleep(delay)
        x = x + 1
		
def hsclean():
    hr = datetime.now()
    hr = hr.hour - 5
    print("  Heat Seal Cleaning Tool v0.1")
    print("================================")
    print()
    lot = input('Lot Number: J003')
    ts = input('TS: ')
    text = f"Hour {hr}: Cleaned heat seal dies per cycle. Inspected toggle assemblies, cleaned lasers, and inspected sample arrays. Foil placement, perforation, and seals all in compliance according to TM-0276. Lot J003{lot.upper()}. Time stamp {ts.upper()}."
    scroll(text)
    #pyperclip.copy(text)
    os.system('echo ' + text + '|clip')
    input()
    #os.system('echo ' + password + '|clip')

os.system('color 06')
os.system('cls')
hsclean()

