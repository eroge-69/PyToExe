pip install pynput
from pynput.keyboard import Key, Controller
from datetime import datetime
import time, sys, pyautogui, os
import keyboard as keyboardlistenerDEBUGMODEDEBUGMODE
from threading import Thread
from tkinter import Label, PhotoImage, Button
import tkinter as tk
from win32gui import GetWindowText, GetForegroundWindow
from win32api import GetSystemMetrics

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Stop the print command from showing up in the console
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("logfile.log", "a")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
          
    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()

def closeprog():
    consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nClosing Program")
    time.sleep(1)
    sys.exit()

# Activates the print block function
#blockPrint()

global DEBUGMODE
DEBUGMODE = True

import mss

def getpixelcolour(x,y):
    with mss.mss() as sct:
        pic = sct.grab({'mon':1, 'top':y, 'left':x, 'width':1, 'height':1})
        g = pic.pixel(0,0)
        return(g)


def sniperscript():
    
    def enterauctionhouse():
        # Search and enter the auction house
        global start

        loop1 = True
        while loop1 == True: # Allows the program to loop
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEntering search")
            print("Entering search")
            #time.sleep(.9)
            ahsearch = getpixelcolour(ahsearchx, ahsearchy)
            while ahsearch != (255,0,134):
                ahsearch = getpixelcolour(ahsearchx, ahsearchy)
            ahsearch = getpixelcolour(ahsearchx, ahsearchy)
            while ahsearch == (255,0,134):
                #searchah = getpixelcolour(searchahx, searchahy)
                #while searchah != (255, 0, 134):
                #    print("Make sure you have the search auction house selected")
                #    searchah = getpixelcolour(searchahx, searchahy)
                #    time.sleep(.5)
                start = time.time()
                keyboard.press(Key.enter) # Enters auction house menu
                keyboard.release(Key.enter)
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEntering Auction House")
                print("Entering Auction House")
                ahsearch = getpixelcolour(ahsearchx, ahsearchy)
                #time.sleep(.1)
            #time.sleep(.5)
            searchloading = getpixelcolour(searchloadingx, searchloadingy)
            while searchloading != (247,247,247):
                searchloading = getpixelcolour(searchloadingx, searchloadingy)
                print("Waiting for search")
            loop2 = True
            while loop2 == True:
                print("Line: 66")
                sconfirm = getpixelcolour(sconfirmx, sconfirmy)
                if sconfirm == (255,0,134):     # Confirms if you are in ah search menu
                    print("Checking if you are currently in ah")
                    keyboard.press(Key.enter) # Searches the auction house
                    keyboard.release(Key.enter)
                    if DEBUGMODE == True:
                        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEnter pressed")
                    loop2 = False
                    break
                loop1 = False
                break
            break
    
        checkforauction()
    
    def checkforauction():
        # Checks the auction house for an available auction
        auctionavailable = False

        printer = True
        Rear_Window = getpixelcolour(Rear_Windowx, Rear_Windowy)
        while Rear_Window != (255,222,57):
            if printer == True:
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nChecking for any auctions")                
                print("Checking if there are any cars up for auction")
                printer = False
            Rear_Window = getpixelcolour(Rear_Windowx, Rear_Windowy) # Checks to see if you are in the auction house - viewing the cars up for auction
        #if Rear_Window == (255,222,57):
        #time.sleep(.52)
        car = getpixelcolour(carx, cary) # Search for the image of the auctionhouse details of the desired car on your screen
        if car == (52,23,53):
            auctionavailable = True
            #time.sleep(0.1)
            px = getpixelcolour(pxx, pxy)
            if px == (247,247,247):
                listingloading = 1
                printer = True
                while listingloading == 1:
                    if printer == True:
                        print("Line: 84")
                        printer = False
                    David_Joseph = getpixelcolour(David_Josephx, David_Josephy) # Gets the RGB Values for the pixel at the location X:873 Y:234
                    print(David_Joseph) # Prints the RGB Values for the pixel at the location X:873 Y:234
                    if David_Joseph != (247,247,247): # Checks if the RGB values are not equal to RGB(247,247,247)
                        auctionavailable = True
                        listingloading = 0
                        break
        else: # If there is no car avaliable for purchase on the auction house
            auctionavailable = False
       
        if auctionavailable == True:
            attemptbuyout()
        else:
            returntostart()
    
    def attemptbuyout():
        # Attempts to buyout the car

        keyboard.press(keyy) # Auction house options
        keyboard.release(keyy)
        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nBringing up shortcut menu")
        print("Bringing up shortcut menu to purchase the car")
        time.sleep(.25)
        loop3 = True
        while loop3 == True:
            print("loop3")
            auctionoptions = getpixelcolour(auctionoptionsx, auctionoptionsy) # Confirms that the butout option is selected
            auctionoptions1 = getpixelcolour(auctionoptions1x, auctionoptions1y) # Confirms that the butout option is selected
            if auctionoptions == (52, 23, 53):
                print("BuyoutOption2")
                x,y = BuyoutOption2x, BuyoutOption2y
                loop3 = False
            elif auctionoptions1 == (52, 23, 53):
                print("BuyoutOption1")
                x,y = BuyoutOptionx, BuyoutOptiony
                loop3 = False
        BuyoutOption = getpixelcolour(x, y) # Confirms that the butout option is selected
        while BuyoutOption != (255,0,134):
            BuyoutOption = getpixelcolour(x, y) # Confirms that the butout option is selected
            keyboard.press(Key.down) # Move to Buy-out
            keyboard.release(Key.down)
            print("Moved to Buy-Out Button")
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nMoved to Buy-Out Button")
            time.sleep(.05)
            BuyoutOption = getpixelcolour(x, y) # Confirms that the butout option is selected
        keyboard.press(Key.enter) # Selects Buy-out
        keyboard.release(Key.enter)
        if DEBUGMODE == True:
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEnter pressed")
        print("Line: 98")
        time.sleep(0.5)
        Budget_Shaeden = getpixelcolour(Budget_Shaedenx, Budget_Shaedeny) # Search for the image 'placebid.png' on your screen
        if Budget_Shaeden == (255,0,134):
            keyboard.press(Key.enter) # Buys the car
            keyboard.release(Key.enter)
            print("Car Purchased") 
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nCar Purchased")
        buyoutoutcome()
    
    def buyoutoutcome():
        # Waits and checks for the buyout outcome
        print("buyoutoutcome")
        time.sleep(.5)
        printer = True
        buyoutoutcomewait = getpixelcolour(buyoutoutcomex, buyoutoutcomey) # Checks to see if the buyout outcome is still loading
        while buyoutoutcomewait != (52,23,53):
            buyoutoutcomewait = getpixelcolour(buyoutoutcomex, buyoutoutcomey) # Checks to see if the buyout outcome is still loading
            if printer == True:
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nWaiting for buyout outcome loading poput")
                print("Waiting for buyout outcome loading popup")
                printer = False
        printer = True
        buyoutoutcomewait = getpixelcolour(buyoutoutcomex, buyoutoutcomey) # Checks to see if the buyout outcome is still loading
        while buyoutoutcomewait == (52,23,53):
            buyoutoutcomewait = getpixelcolour(buyoutoutcomex, buyoutoutcomey) # Checks to see if the buyout outcome is still loading
            if printer == True:
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nWaiting for buyout outcome")
                print("Waiting for buyout outcome")
                printer = False
        buyoutoutcomewait = getpixelcolour(buyoutoutcomex, buyoutoutcomey) # Checks to see if the buyout outcome is still loading
        buyoutoutcomecheck = getpixelcolour(buyoutoutcomecheckx, buyoutoutcomechecky)
        while buyoutoutcomecheck != (52,23,53):
            buyoutoutcomecheck = getpixelcolour(buyoutoutcomecheckx, buyoutoutcomechecky)
        #time.sleep(.5)
        buyoutfailed = getpixelcolour(buyoutfailedx, buyoutfailedy) # Checks if the buyout failed
        buyoutsuccessful = getpixelcolour(buyoutx, buyouty) # Checks if the buyout was successful
        if buyoutsuccessful == (52,23,53):
            buyoutoutcomesuccessful()
        else:
            buyoutoutcomefailed()

    def buyoutoutcomesuccessful():
        # Collects car and returns to auction house

        #   Buyout Successful
        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nBuyout Siccessful")
        print("Buyout Successful")
        keyboard.press(Key.enter) # Backs out of the successful buy-out screen
        keyboard.release(Key.enter)
        if DEBUGMODE == True:
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEnter pressed")
        printer = True
        loop4 = True
        while loop4 == True:
            collectcar = getpixelcolour(collectcarx, collectcary) # Checks if collect car is currently selected
            if collectcar == (255,0,134):
                loop4 = False
            collectcar = getpixelcolour(collectcar1x, collectcar1y) # Checks if collect car is currently selected
            if collectcar == (255,0,134):
                loop4 = False
            collectcar = getpixelcolour(collectcar2x, collectcar2y) # Checks if collect car is currently selected
            if collectcar == (255,0,134):
                loop4 = False
            if printer == True:
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nCollect car not selected")
                print("Car collect option not selected")
                printer = False
            time.sleep(.01)
        #if collectcar == (255,0,134):
        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nCollect car selected")
        print("Collect car is selected")
        time.sleep(.1)
        keyboard.press(Key.enter) # Collects the car
        keyboard.release(Key.enter)
        if DEBUGMODE == True:
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEnter pressed")
        time.sleep(.5)
        printer = True
        collectcar = getpixelcolour(collectcarx, collectcary) # Checks if collect car is currently selected
        while collectcar == (255,0,134):
            collectcar = getpixelcolour(collectcarx, collectcary) # Checks if collect car is currently selected
            collectcar = getpixelcolour(collectcar1x, collectcar1y) # Checks if collect car is currently selected
            collectcar = getpixelcolour(collectcar2x, collectcar2y) # Checks if collect car is currently selected
            keyboard.press(Key.enter) # Collects the car
            keyboard.release(Key.enter)
            if printer == True:
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nAttempting to collect car")
                print("Attempting to collect the car")
                printer = False
        printer = True
        carcollected = getpixelcolour(carcollectedx, carcollectedy) # Checks if collect car is currently selected
        while carcollected != (52, 23, 53):
            carcollected = getpixelcolour(carcollectedx, carcollectedy) # Checks if collect car is currently selected
            if printer == True:
                consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nWaiting for car to be collected")
                print("Waiting for car to be collected")
                printer = False
        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nCar collected")
        print("Car has been collected")
        time.sleep(.1)
        keyboard.press(Key.enter) # Collects the car
        keyboard.release(Key.enter)
        #else:
        #    print("Car collect option not selected")
        #print("Line: 159")
        #sellerdetails = getpixelcolour(sellerdetailsx, sellerdetailsy) # Search for the image of the seller details of the desired car on your screen
        #while sellerdetails != (255,0,134):
        #    sellerdetails = getpixelcolour(sellerdetailsx, sellerdetailsy) # Search for the image of the seller details of the desired car on your screen
        #    sellerdetails = getpixelcolour(sellerdetails2x, sellerdetails2y) # Search for the image of the seller details of the desired car on your screen
        #    sellerdetails = getpixelcolour(sellerdetails3x, sellerdetails3y) # Search for the image of the seller details of the desired car on your screen
        #time.sleep(.2)

        time.sleep(.7)
        keyboard.press(Key.esc) # Backs out of the auction house shortcut menu
        keyboard.release(Key.esc)
        print("Line: 277")

        returntostart()
    
    def buyoutoutcomefailed():
        # Exits back to auction house shortcut menu

        #   Buyout Failed
        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nBuyout Failed")
        print("Buyout Failed")
        buyoutfailed = getpixelcolour(buyoutfailedx, buyoutfailedy) # Checks if the buyout failed
        while buyoutfailed != (52,23,53):
            buyoutfailed = getpixelcolour(buyoutfailedx, buyoutfailedy) # Checks if the buyout failed
        keyboard.press(Key.enter) # Backs out of the successful buy-out screen
        keyboard.release(Key.enter)
        print("Line: 272")
        if DEBUGMODE == True:
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEnter Pressed")
        time.sleep(.7)

        time.sleep(.7)
        print("Line: 274")
        keyboard.press(Key.esc) # Backs out of the auction house shortcut menu
        keyboard.release(Key.esc)
        print("Line: 277")
        if DEBUGMODE == True:
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nESC Pressed")

        returntostart()

    def returntostart():
        global count
        # Returns from the auction house to the start
        consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nReturning to start")
        print("Line: 163")
        #time.sleep(.1)
        printer = True
        Rear_Window = getpixelcolour(Rear_Windowx, Rear_Windowy)
        while Rear_Window != (255,222,57):
            if printer == True:                
                print("Checking if there are any cars up for auction")
                printer = False
            Rear_Window = getpixelcolour(Rear_Windowx, Rear_Windowy) # Checks to see if you are in the auction house - viewing the cars up for auction
        print("Line: 165")
        keyboard.press(Key.esc) # Returns to start location, before entering the search for the desired car
        keyboard.release(Key.esc)
        print("Line: 169")
        if DEBUGMODE == True:
            consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nEnter pressed")

        end = time.time()
        print("loop time:", end-start)

        #count += 1
        #if count <= 100:
           #Script.stop()
        #enterauctionhouse()

    

    # Start of Code
    print("Welcome to the Forza Auction House Sniper Bot")
    consoleoutput.set("Welcome to the Forza Auction House Sniper Bot")
    time.sleep(2)
    print("Starting program")
    consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nStarting program")
    time.sleep(2)
    activewin = 0
    while activewin == 0:
        print(GetWindowText(GetForegroundWindow()))
        if GetWindowText(GetForegroundWindow()) == "Forza Horizon 5":
            activewin = 1

    consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nGetting Monitor info")

    keyboard = Controller()

    keyy = "y" # Used to press down and release the 'y' key

    #global count
    #count = 0

    MonitorWidth = GetSystemMetrics(0)
    MonitorHeight = GetSystemMetrics(1)

    ahsearchx = int(0.4 * MonitorWidth)
    ahsearchy = int(0.2305555556 * MonitorHeight)
    sconfirmx = int(0.3171875 * MonitorWidth)
    sconfirmy = int(0.677777778 * MonitorHeight)
    Rear_Windowx = int(0.2140625 * MonitorWidth)
    Rear_Windowy = int(0.159259259 * MonitorHeight)
    carx = int(0.515625 * MonitorWidth)
    cary = int(0.213888889 * MonitorHeight)
    pxx = int(0.4546875 * MonitorWidth)
    pxy = int(0.216666667 * MonitorHeight)
    David_Josephx = int(0.4546875 * MonitorWidth)
    David_Josephy = int(0.216666667 * MonitorHeight)
    BuyoutOptionx = int(0.329166667 * MonitorWidth)
    BuyoutOptiony = int(0.492592593 * MonitorHeight)
    Budget_Shaedenx = int(0.3265625 * MonitorWidth)
    Budget_Shaedeny = int(0.52962963 * MonitorHeight)
    buyoutoutcomex = int(0.33489583333 * MonitorWidth)        #w:643 h:442
    buyoutoutcomey = int(0.40925925925 * MonitorHeight)
    buyoutx = int(0.3328125 * MonitorWidth)               #w:639 h:460
    buyouty = int(0.42592592592 * MonitorHeight)
    collectcar1x = int(0.32291666666 * MonitorWidth)
    collectcar1y = int(0.46481481481 * MonitorHeight)
    collectcarx = int(0.328645833 * MonitorWidth)
    collectcary = int(0.490740741 * MonitorHeight)
    carcollectedx = int(0.3296875 * MonitorWidth)
    carcollectedy = int(0.47685185185 * MonitorHeight)
    sellerdetailsx = int(0.327604167 * MonitorWidth)
    sellerdetailsy = int(0.489814815 * MonitorHeight)
    sellerdetails2x = int(0.327604167 * MonitorWidth)
    sellerdetails2y = int(0.514814815 * MonitorHeight)
    buyoutfailedx = int(0.33020833333 * MonitorWidth)             #w:634 h:532
    buyoutfailedy = int(0.49259259259 * MonitorHeight)

    collectcar2x = int(0.31818181818 * MonitorWidth)
    collectcar2y = int(0.46666666666 * MonitorHeight)
    sellerdetails3x = int(0.31818181818 * MonitorWidth)
    sellerdetails3y = int(0.46666666666 * MonitorHeight)
    BuyoutOption2x = int(0.32916666666 * MonitorWidth)
    BuyoutOption2y = int(0.47592592592 * MonitorHeight)
    auctionoptionsx = int(0.32864583333 * MonitorWidth)
    auctionoptionsy = int(0.3537037037 * MonitorHeight)
    auctionoptions1x = int(0.33020833333 * MonitorWidth)
    auctionoptions1y = int(0.41944444444 * MonitorHeight)

    searchloadingx = int(0.4703125 * MonitorWidth)
    searchloadingy = int(0.52962962963 * MonitorHeight)

    buyoutoutcomecheckx = int(0.33020833333 * MonitorWidth)
    buyoutoutcomechecky = int(0.47685185185 * MonitorHeight)

    time.sleep(2)

    consoleoutput.set("Welcome to the Forza Auction House Sniper Bot\nProgram Running")
    while True:
        enterauctionhouse()
    #while True: # remove enterauctionhouse from returntostart
    #enterauctionhouse()
    
root = tk.Tk()
consoleoutput = tk.StringVar()
consoleoutput.set("")
lastoutput = tk.StringVar()
lastoutput.set("")

width, height= pyautogui.size()

root.title("Forza Horizon 5 Sniper") # names the Tk root window  
root.overrideredirect(1) # removes title bar from window
root.geometry(("%dx%d" % (width, height)))
root.configure(bg='grey')
root.wm_attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "grey")

ConsoleOutput=Label(textvariable=consoleoutput, fg='#ffffff', bg='grey')
ConsoleOutput.grid(sticky="NE")
LastOutput=Label(textvariable=lastoutput, fg='#ffffff', bg='grey')
LastOutput.grid()
overlayimg=PhotoImage(file=resource_path('overlay.png'))
overlay=Button(root, image=overlayimg, bg='grey', highlightbackground = "grey", highlightthickness = 0, bd=0, activebackground = "grey", command = closeprog)
X=width-120
Y=height-31
overlay.place(x=X, y=Y)

Script = Thread(target=sniperscript)
Script.setDaemon(True)
Script.start()

root.mainloop()
