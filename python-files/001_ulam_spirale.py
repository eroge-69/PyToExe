# -*- coding: utf-8 -*-
"""
Created on Wed May  3 13:43:40 2023

@author: tilob
"""

import pgzrun
import random
from pgzero.builtins import Actor, animate, keyboard, Rect



WIDTH=800
HEIGHT=800
TITLE='Ulam-Spirale'
def draw():
    screen.draw.text(str(counter), (pos_x,pos_y),color='white',fontsize=15)
    

def update():
    
    global delay
    global counter
    if delay>100:
        neu_pos(counter)
        counter+=1
        delay=0
    else:
        delay+=1
        
def drehen():
    pass

def laufen():
    pass
        
def neu_pos(n):
    global pos_x
    global pos_y
    drehen()
    laufen()
    pos_x+=15
    
    
    pass
pos_x=0
pos_y=400
counter=1
size_x=10
size_y=10

delay=0            
schrittlaenge=1

pgzrun.go()
