# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
# Get started with interactive Python!
# Supports Python Modules: builtins, math,pandas, scipy 
# matplotlib.pyplot, numpy, operator, processing, pygal, random, 
# re, string, time, turtle, urllib.request
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp
import tkinter as tk

class FlashingApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)  # Make full screen
        self.colors = ['green', 'red']
        self.current = 0
        self.flash()

    def flash(self):
        self.root.configure(bg=self.colors[self.current])
        self.current = (self.current + 1) % 2
        self.root.after(500, self.flash)  # Change color every 500ms

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashingApp(root)
    root.mainloop()
