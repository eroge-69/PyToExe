from random import random
from re import L
from telnetlib import NOP
import keyboard
import mouse
import pygame
import random
from PIL import Image, ImageGrab
import time

#https://www.youtube.com/watch?v=6At79Lt7SXQ&t=6s

from sqlalchemy import false, true


def Main():

    #chrome
    time.sleep(1)
    mouse.move(2190, 1060)
    mouse.click()

    #profile
    time.sleep(1)
    mouse.move(2880, 560)
    mouse.click()

    #website
    time.sleep(1)
    keyboard.write("https://sudoku.com/sudoku-printable")

    #website cont.
    time.sleep(1)
    keyboard.press("Enter")

    #website print button 
    time.sleep(5)
    mouse.move(2900, 600)
    mouse.click()

    #print page print button
    time.sleep(2)
    mouse.move(3770, 150)
    mouse.click()

    #printer print button
    time.sleep(5)
    mouse.move(3400, 900)
    mouse.click()

    #printer print button
    time.sleep(2)
    mouse.move(3820, 15)
    mouse.click()


if __name__ == "__main__":
    Main()
