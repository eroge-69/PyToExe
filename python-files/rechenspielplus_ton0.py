# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 10:42:25 2025

@author: yvonn
"""

import random as rand

maxzahl=10
z1=rand.randint(1,maxzahl)
z2=rand.randint(1,maxzahl)

z3=z1+z2
  
#from playsound import playsound


while True:
    try:
        if z3==int(input(f'{z1} + {z2} = ')):
            print("Richtig!")
            #playsound('F:/Pythonspiel/richtig.mp3')
            z1=rand.randint(1,maxzahl)
            z2=rand.randint(1,maxzahl)
            z3=z1+z2
            
       # elif z3 != int(input(f'{z1} + {z2} = ')):
        else:
            print("Falsch! Versuche es noch einmal!")
            #playsound('F:/Pythonspiel/falsch.wav')
            z1=z1
            z2=z2
            z3=z1+z2
    except:
        print("Gib eine Zahl ein!")
        
    
    
