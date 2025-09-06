# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 19:14:23 2025

@author: straj
"""
from tkinter import Tk, Canvas
from PIL import Image, ImageTk
# Initialize the Tkinter window
root = Tk()
# Create a canvas object
canvas = Canvas(root, width=400, height=400)
canvas.pack()
# Open an image using PIL
image = Image.open('darow.png')
photo = ImageTk.PhotoImage(image)
# Draw the image on the canvas
canvas.create_image(20, 20, anchor='nw', image=photo)
# Start the Tkinter event loop
root.mainloop()