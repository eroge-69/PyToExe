#!/usr/bin/env python3

import os
import random

keyboardDict = {
    2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
    16: 'q', 17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o', 25: 'p',
    30: 'a', 31: 's', 32: 'd', 33: 'f', 34: 'g', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
    44: 'z', 45: 'x', 46: 'c', 47: 'v', 48: 'b', 49: 'n', 50: 'm'
}

def keyboardEncToAscii(inKey):
    out = ""
    for c in inKey:
        if c != 0:
            out += keyboardDict[c]
    return out

def asciiToKeyboardenc(inAscii):
    out = []
    asciiDict = {a: k for k, a in keyboardDict.items()}
    for c in inAscii:
        if c != 0:
            out.append(asciiDict[c])
    return out

def badCRC16(pwd, salt=0):
    hash = salt
    for c in pwd:
        hash ^= c
        for i in range(8):
            if (hash & 1):
                hash = (hash >> 1) ^ 0x2001
            else:
                hash = (hash >> 1)
    return hash

def bruteForce(hash, salt=0, digitsOnly=False, charsOnly=True, minLen=3, maxLen=8):
    global keyboardDict
    keyboardDictOrig = keyboardDict
    if digitsOnly:
        keyboardDict = dict(zip(list(keyboardDict.keys())[0:9], list(keyboardDict.values())[0:9]))
    elif charsOnly:
        keyboardDict = dict(zip(list(keyboardDict.keys())[10:36], list(keyboardDict.values())[10:36]))

    encodedPwd = [list(keyboardDict.keys())[0] for _ in range(7)]
    random.seed()
    if hash > 0x3FFF:
        return "invalid hash code"
    while True:
        rndVal = random.random() * len(keyboardDict)
        for i in range(len(encodedPwd)):
            value = int(rndVal % len(keyboardDict))
            encodedPwd[i] = list(keyboardDict.keys())[value]
            rndVal *= len(keyboardDict)
        for i in range(minLen, maxLen + 1):
            if badCRC16(encodedPwd[0:i], salt) == hash:
                keyboardDict = keyboardDictOrig
                encodedPwd = encodedPwd[0:i]
                return keyboardEncToAscii(encodedPwd)

print("Master Password Generator for Phoenix BIOS (five decimal digits version)")
print("Copyright (C) 2009 dogbert <dogber1@gmail.com>")
print("")
print("After entering the wrong password for the third time, you will receive a")
print("decimal number from which the master password can be calculated,")
print("e.g. 12345")
print("")
code = input("Please enter the number: ").replace('[', '').replace(']', '')
hash = int(code)
print("
Brute forcing passwords...")
print("Generic Phoenix BIOS:          " + bruteForce(hash, 0))
print("HP/Compaq Phoenix BIOS:        " + bruteForce(hash, salt=17232))
print("FSI Phoenix BIOS (generic):    " + bruteForce(hash, salt=65, minLen=3, maxLen=7, digitsOnly=True))
print("FSI Phoenix BIOS ('L' model):  " + bruteForce(hash + 1, salt=ord('L'), minLen=3, maxLen=7, digitsOnly=True))
print("FSI Phoenix BIOS ('P' model):  " + bruteForce(hash + 1, salt=ord('P'), minLen=3, maxLen=7, digitsOnly=True))
print("FSI Phoenix BIOS ('S' model):  " + bruteForce(hash + 1, salt=ord('S'), minLen=3, maxLen=7, digitsOnly=True))
print("FSI Phoenix BIOS ('X' model):  " + bruteForce(hash + 1, salt=ord('X'), minLen=3, maxLen=7, digitsOnly=True))
print("
done.
")
print("Please note that the password has been encoded for the standard US keyboard layout (QWERTY).")
input("Press Enter to exit...")
