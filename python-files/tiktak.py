# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 09:24:13 2025

@author: A143VU03
"""

from pgzero.builtins import Actor
import pgzrun

WIDTH = 500
HEIGHT = 400

felder = []

def draw():
    screen.clear()
    screen.fill('white')
    for a in felder:
        a.draw()
def on_mouse_down(pos):
    global akt_spieler
    for i in range(len(felder)):
    
        if felder[i].collidepoint(pos) and belegung[i]=='-':
            if akt_spieler=='x':
                felder[i].image='kreuz.png'
                belegung[i]='x'                
                akt_spieler='o'
            elif akt_spieler=='o':
                felder[i].image='kreis.png'
                belegung[i]='o'   
                akt_spieler='x'
    print(belegung)
    test()
    
def test():
    global sieger
    
    if belegung[0]==belegung[1] and belegung[0]==belegung[2] and belegung[0]!='-':
        sieger=belegung[0]
        
    if belegung[3]==belegung[4] and belegung[3]==belegung[5] and belegung[3]!='-':
        sieger=belegung[3]
        
    if belegung[6]==belegung[7] and belegung[6]==belegung[8] and belegung[6]!='-':
        sieger=belegung[6]
    
    if belegung[0]==belegung[3] and belegung[0]==belegung[6] and belegung[0]!='-':
        sieger=belegung[0]
    
    if belegung[1]==belegung[4] and belegung[1]==belegung[7] and belegung[1]!='-':
        sieger=belegung[1]
        
    if belegung[3]==belegung[5] and belegung[3]==belegung[8] and belegung[3]!='-':
        sieger=belegung[3]
        
    if belegung[0]==belegung[4] and belegung[0]==belegung[8] and belegung[0]!='-':
        sieger=belegung[0]
    
    if belegung[2]==belegung[4] and belegung[2]==belegung[6] and belegung[2]!='-':
        sieger=belegung[2]
    
  
    print('Sieger ist:',sieger)
    

sieger='-'
akt_spieler='x'
felder=[]
belegung=[]

for i in range(9):
    belegung.append('-')   
    
for i in range(9):
    a = Actor('leeresfeld.png')
    a.x = 100 + 100 * (i % 3) #Rest der Division
    a.y = 100 + 100 * (i // 3) #ganzzahliger Anteil
    felder.append(a)

pgzrun.go()
