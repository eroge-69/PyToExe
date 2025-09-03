#!/usr/bin/env python3

import sys

#declare band variables
global band1, band2, band3, band4
band1 = 0
band2 = 0
band3 = 0
band4 = 0

#Checks for when to trigger query again
queryComplete = True

print("[]------------------------------[]")
print("Welcome to the Resistor Calculator")
print("This program will calculate the resistance value and tolerance of a resistor given the band colors")
print("Type \"Exit\" to close the program")
print("[]------------------------------[]")

#Dictionary associating band colors and band numbers with their values
bandOptions = {
    "black" : {
        1-2 : 0,
        3 : 1,
        4 : "ERROR"
    },
    "brown" : {
        1-2 : 1,
        3 : 10,
        4 : .01
    },
    "red" : {
        1-2 : 2,
        3 : 100,
        4 : .02
    },
    "orange" : {
        1-2 : 3,
        3 : 1000,
        4 : "ERROR"
    },
    "yellow" : {
        1-2 : 4,
        3 : 10000,
        4 : "ERROR"
    },
    "green" : {
        1-2 : 5,
        3 : 100000,
        4 : .005
    },
    "blue" : {
        1-2 : 6,
        3 : 1000000,
        4 : .0025
    },
    "violet" : {
        1-2 : 7,
        3 : 10000000,
        4 : .001
    },
    "voilet" : {
        1-2 : 7,
        3 : 10000000,
        4 : .001
    },
    "gray" : {
        1-2 : 8,
        3 : 100000000,
        4 : "ERROR"
    },
    "grey" : {
        1-2 : 8,
        3 : 100000000,
        4 : "ERROR"
    },
    "white" : {
        1-2 : 9,
        3 : 1000000000,
        4 : "ERROR"
    },
    #Below are 4th band exclusive colors
    "gold" : {
        1-2 : "ERROR",
        3 : "ERROR",
        4 : .05
    },
    "silver" : {
        1-2 : "ERROR",
        3 : "ERROR",
        4 : .10
    },
    "none" : {
        1-2 : "ERROR",
        3 : "ERROR",
        4 : .20
    },
    "no" : {
        1-2 : "ERROR",
        3 : "ERROR",
        4 : .20
    },
    
}

global errored
errored = False

# Error handler for colorCheck
def colorErrorCheck(band, color):
    global errored  # Declare errored as global
    if band == "ERROR":
        print("ERROR CODE 1\nReason: \"" + color + "\" is an invalid color for the selected band")
        errored = True

# Matches the input string to a color and band value
def colorCheck(color, bandNumber):
    global errored, band1, band2, band3, band4  # Declare all as global

    if color.lower() == "exit":
        sys.exit("\n[Exiting program...]")

    if color in bandOptions:
        if bandNumber == 1:
            band1 = bandOptions[color.lower()][1-2]
            colorErrorCheck(band1, color)
        elif bandNumber == 2:
            band2 = bandOptions[color.lower()][1-2]
            colorErrorCheck(band2, color)
        elif bandNumber == 3:
            band3 = bandOptions[color.lower()][3]
            colorErrorCheck(band3, color)
        elif bandNumber == 4:
            band4 = bandOptions[color.lower()][4]
            colorErrorCheck(band4, color)  # Corrected to use band4
        else:
            print("ERROR CODE 2\nReason: invalid band number")
            errored = True
    else:
        print("ERROR CODE 3\nReason: \"" + color + "\" is an invalid color")
        errored = True
    #abort function if error occurs
    if errored:
        return        

#Takes user inputs, requests calculations, and returns results
def query():
    queryComplete = False
    print("\n\n")

    ask1 = input("Band 1 color: ")
    colorCheck(ask1, 1)
    if errored == True:
        return
    ask2 = input("Band 2 color: ")
    colorCheck(ask2, 2)
    if errored == True:
        return
    ask3 = input("Band 3 color: ")
    colorCheck(ask3, 3)
    if errored == True:
        return
    ask4 = input("Band 4 color: ")
    colorCheck(ask4, 4)
    if errored == True:
        return
    print("------------------------------")

    withoutTolerance = (int(str(band1) + str(band2)) * band3)
    toleranceCeiling = (withoutTolerance * (band4 + 1))
    toleranceFloor =  (withoutTolerance * (1 - band4))

    print(str('{:,}'.format(withoutTolerance)) + "Ω ± " + str(band4 * 100) + "%")
    print(str('{:,}'.format(round(toleranceFloor, 2))) + "Ω - " + str('{:,}'.format(round(toleranceCeiling, 2))) + "Ω")

    queryComplete = True

#Keeps program repeating until closed
while queryComplete == True:
    query()
    errored = False
