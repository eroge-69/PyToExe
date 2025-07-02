# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:40:47 2024

@author: A143VU03
"""

import turtle as t
import random

def haus_nikolaus(laenge):
    t.penup()
    t.goto(0,0)
    t.pendown()
    t.goto(0,laenge)
    t.goto(laenge,0)
    t.goto(laenge,laenge)
    t.goto(0,laenge)
    t.goto(laenge/2,laenge*1.5)
    t.goto(laenge,laenge)
    t.goto(0,0)
    t.goto(laenge,0)
    
for i in range(5):        
    haus_nikolaus(40*i)

t.done()