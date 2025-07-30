# Créé par nebuleuse, le 27/07/2025 en Python 3.7
#http://sdz.tdct.org/sdz/interface-graphique-pygame-pour-python.html#Lesinterfacesgraphiques
from pygame import*
from pygame.locals import*
import pygame
import sys
from random import *
from pygame import event
from math import*


class BoutonRadio:
    def __init__(self,nom,coord):
        self.nom=nom   # Le nom de la case, par exemple "A1"
        self.coord=coord   # [centre,rayon]
        self.etat=0   # L'état de la case (0 = vide, 1 = activée, 2 = une autre activation)
        self.passage=0   # Indicateur pour savoir si la souris est passée dessus
        self.color0=pygame.Color(235,235,255)
        self.color1=pygame.Color(70,70,255)
        self.colorOutside=(0,0,0)
        self.Hitbox=pygame.Rect(coord[0][0]-coord[1],coord[0][1]-coord[1],coord[1]*2,coord[1]*2)

    def activation(self):
        if self.etat==0:
            self.etat=1
        else:
            self.etat=0


    def Apassage(self,a):
        if a=="1":
            self.passage="1"
        else:
            self.passage=0


    def affichage(self):
        if self.etat==1:
            c=self.color1
        else:
            c=self.color0
        pygame.draw.circle(screen,c,self.coord[0],self.coord[1])

        coord2=(self.coord[0][0]-1,self.coord[0][1])

        ep=round(0.3*self.coord[1])
        if self.passage=="1":
            pygame.draw.circle(screen,self.colorOutside,coord2,self.coord[1]+1,round(ep/1.55))
        else:
            pygame.draw.circle(screen,self.colorOutside,coord2,self.coord[1]+1,ep+2)

class CaseInput:

    def __init__(self,coord,nom):
        self.coord=pygame.Rect(coord[0],coord[1],coord[2],coord[3])
        self.initial=coord[2]
        self.nom=nom
        self.etat=False
        self.contenu=""
        self.colorON=[(0,210,0),(250,250,250)]  # [contour,fond]
        self.colorOFF=[(232,112,12),(250,250,250)]  # [contour,fond]
        self.blocage=False

    def activation(self):
        if self.etat==False:
            self.etat=True
        else:
            self.etat=False


    def affichage(self, font):
        if self.etat==False:
            pygame.draw.rect(screen,self.colorOFF[1],self.coord)
            pygame.draw.rect(screen,self.colorOFF[0],self.coord,4)
        else:
            pygame.draw.rect(screen,self.colorON[1],self.coord)
            pygame.draw.rect(screen,self.colorON[0],self.coord,4)

        text_surface = font.render(self.contenu,True,(0,0,0))
        h1=text_surface.get_height()
        h2=(self.coord.h-h1)//2
        screen.blit(text_surface,(self.coord.x+8, self.coord.y + round(h2*1.5)))

    def ajustement(self, mod, font):
        if self.blocage==False:
            text_surface = font.render(self.contenu,True,(0,0,0))
            if mod==1:
                self.coord.w=max(self.coord.w,text_surface.get_width() + 15)
            else:
                pygame.draw.rect(screen,(255,255,255),self.coord)     # (255,255,255) correspond à la couleur de screen (fond de la fenêtre)
                pygame.draw.rect(screen,(255,255,255),self.coord,4)
                self.coord.w=max(self.initial,text_surface.get_width() + 15)

class Bouton:
    def __init__(self,nom,coord,font):
        self.nom=nom   # Le nom de la case, par exemple "A1"
        self.coord=coord   # Les coordonnées de la case, sous forme de rectangle pygame.Rect
        self.passage=0   # Indicateur pour savoir si la souris est passée dessus
        self.color0=pygame.Color(110,110,110)
        self.color1=pygame.Color(170,170,170)
        self.Hitbox=coord
        self.texte=Texte("Valider",(500,390),font)
        self.texte.mode="M"
        self.texte.color=(255,255,255)

    def activation(self):
        if self.etat==0:
            self.etat=1
        else:
            self.etat=0
        self.affichage()

    def Apassage(self,a):
        if a=="1":
            self.passage="1"
        else:
            self.passage=0

    def affichage(self):
        if self.passage=="1":
            pygame.draw.rect(screen,self.color1,self.coord)
        else:
            pygame.draw.rect(screen,self.color0,self.coord)
        pygame.draw.rect(screen,(0,0,0),self.coord,4)
        self.texte.affichage()

class Texte:
    def __init__(self,texte,coord,font):
        self.texte=texte
        self.font=font
        self.mode="D"    # Début  /  Fin  /  Milieu
        self.coord=coord   # point eu centre du texte (horizontal)
        self.color=(0,0,0)


    def affichage(self):
        taille=self.font.size(self.texte)
        if self.mode=="D":
            coord2=(self.coord[0],self.coord[1]-(taille[1]//2))
        elif self.mode=="M":
            coord2=(self.coord[0]-(taille[0]//2),self.coord[1]-(taille[1]//2))
        else:
            coord2=(self.coord[0]-taille[0],self.coord[1]-(taille[1]//2))
        rendu = self.font.render(self.texte,True,self.color)
        screen.blit(rendu,coord2)


def liste_texte(l):
    texte=l[0]
    for y in range(1,len(l)):
        texte=texte+l[y]
    return texte

def floatNB(a):
    if "," in a:
        i=a.index(",")
        a=a[:i]+"."+a[i+1:]
    try:
        float(a)
    except ValueError:
        return "Error"
    a=float(a)
    if a==0:
        return "Error"
    return abs(a)

pygame.init()
clock = pygame.time.Clock()
s_width=1000
s_height=600
screen= pygame.display.set_mode((s_width,s_height))
pygame.display.set_caption('Convertisseur tartelettes/tarte')
smallfont = pygame.font.SysFont('Arial',30)
font = pygame.font.SysFont(None,36)
font2 = pygame.font.SysFont(None,48)
font3 = pygame.font.SysFont(None,12)
fontInput = pygame.font.SysFont(None,42)

screen.fill((255,255,255))
liste_boutonsR=[]

## Bouton Mode 1
Tartelettes_Tarte=Texte("Tartelettes → Tarte",(470,60),smallfont)  #(247, 35)
Tartelettes_Tarte.mode="F"
Tartelettes_Tarte.affichage()

BR1=BoutonRadio("BR1",[(193,60),20])
liste_boutonsR.append(BR1)

BR1.activation()
BR1.affichage()

## Bouton Mode 2
Tarte_Tartelettes=Texte("Tarte → Tartelettes",(580,60),smallfont)
Tarte_Tartelettes.affichage()

BR2=BoutonRadio("BR2",[(550,60),20])
liste_boutonsR.append(BR2)


## Input Y
InputY=Texte("Diamètre des tartelettes :",(480,200),font)
InputY.mode="F"
InputY.affichage()

CaseInputY=CaseInput((520,180,140,40),"InY")

CaseInputY.affichage(fontInput)

## Input X
InputX=Texte("Nombres de tartelettes :",(480,280),font)
InputX.mode="F"

CaseInputX=CaseInput((520,260,140,40),"InX")

CaseInputX.affichage(fontInput)
InputX.affichage()

## Input Z
InputZ=Texte("Diamètre de la tarte :",(480,280),font)
InputZ.mode="F"

CaseInputZ=CaseInput((520,260,140,40),"InY")
CaseInputZ.blocage==True

## Valider
BValider=Bouton("V",pygame.Rect(420,360,160,50),font2)
BValider.affichage()

liste_boutonsR.append(BValider)

valider=False
result=""

## Texte résultat 1
TRes1=Texte("Diamètre de la tarte :",(490,500),font2)
TRes1.mode="F"
TRes1.affichage()

## Texte résultat 2
TRes2=Texte("Nombre de tartelettes :",(490,500),font2)
TRes2.mode="F"



Consignes=Texte("*Les  dimensions  doivent  être  dans  la  même  unité",(2,594),font3)
Consignes.affichage()

while True:

# ---------- Permet de fermer la fenêtre sans crash ---------- #
    for events in pygame.event.get():
        if events.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
# ------------------------------------------------------------ #

# ------ Color/décolore la case si un clique de la souris est effectué dessus ------ #
        if events.type==pygame.MOUSEBUTTONDOWN:
            if BR1.Hitbox.collidepoint(events.pos) and BR1.etat==0:
                BR1.activation()
                BR1.affichage()

                pygame.draw.rect(screen,(255,255,255),(0,250,1000,320))
                InputX.affichage()
                CaseInputX.affichage(fontInput)
                CaseInputZ.etat=False
                CaseInputZ.blocage==True
                CaseInputX.blocage==False

                pygame.draw.rect(screen,(255,255,255),(0,410,1000,150))
                TRes1.affichage()

                if BR2.etat==1:
                    BR2.activation()
                    BR2.affichage()
            elif BR2.Hitbox.collidepoint(events.pos) and BR2.etat==0:
                BR2.activation()
                BR2.affichage()

                pygame.draw.rect(screen,(255,255,255),(0,250,1000,320))
                InputZ.affichage()
                CaseInputZ.affichage(fontInput)
                CaseInputX.etat=False
                CaseInputX.blocage==True
                CaseInputZ.blocage==False

                pygame.draw.rect(screen,(255,255,255),(0,410,1000,150))
                TRes2.affichage()

                if BR1.etat==1:
                    BR1.activation()
                    BR1.affichage()

            elif  CaseInputY.coord.collidepoint(events.pos):
                CaseInputY.activation()
                CaseInputY.affichage(fontInput)
                if BR1.etat==1:
                    CaseInputX.etat=False
                    CaseInputX.affichage(fontInput)
                else:
                    CaseInputZ.etat=False
                    CaseInputZ.affichage(fontInput)

            elif  CaseInputX.coord.collidepoint(events.pos):
                if BR1.etat==1:
                    CaseInputX.activation()
                    CaseInputX.affichage(fontInput)
                    CaseInputY.etat=False
                    CaseInputY.affichage(fontInput)
                else:
                    CaseInputZ.activation()
                    CaseInputZ.affichage(fontInput)
                    CaseInputY.etat=False
                    CaseInputY.affichage(fontInput)

            elif  BValider.coord.collidepoint(events.pos):
                valider=True
                pygame.draw.rect(screen,(255,255,255),(500,410,1000,150))


        if events.type == pygame.KEYDOWN:

            if CaseInputY.etat == True:
                if events.key == pygame.K_BACKSPACE:
                   CaseInputY.contenu = CaseInputY.contenu[:-1]
                   CaseInputY.ajustement(0,fontInput)
                else:
                   CaseInputY.contenu+=events.unicode
                   CaseInputY.ajustement(1,fontInput)
                CaseInputY.affichage(fontInput)

            elif CaseInputX.etat == True:
                if events.key == pygame.K_BACKSPACE:
                   CaseInputX.contenu = CaseInputX.contenu[:-1]
                   CaseInputX.ajustement(0,fontInput)
                else:
                   CaseInputX.contenu+=events.unicode
                   CaseInputX.ajustement(1,fontInput)
                CaseInputX.affichage(fontInput)

            elif CaseInputZ.etat == True:
                if events.key == pygame.K_BACKSPACE:
                   CaseInputZ.contenu = CaseInputZ.contenu[:-1]
                   CaseInputZ.ajustement(0,fontInput)
                else:
                   CaseInputZ.contenu+=events.unicode
                   CaseInputZ.ajustement(1,fontInput)
                CaseInputZ.affichage(fontInput)

# --------------------------------------------------------------------------------- #

# ---------- Entoure le case en rouge si la souris est dessus ---------- #
    mouse_position = pygame.mouse.get_pos()
    for b in liste_boutonsR:
        if b.Hitbox.collidepoint(mouse_position):
            b.Apassage("1")
        else:
            b.Apassage("0")
        b.affichage()
# --------------------------------------------------------------------- #


    if valider:
        valider=False

        if BR1.etat==1:
            if CaseInputY.contenu=="" or CaseInputX.contenu=="":
                result="Formulaire incomplet"
            elif floatNB(CaseInputY.contenu)=="Error" or floatNB(CaseInputX.contenu)=="Error":
                result="Formulaire incorrect"
            else:
                result = str(round( floatNB(CaseInputY.contenu) * sqrt(floatNB(CaseInputX.contenu)) ,3))

        else:
            if CaseInputY.contenu=="" or CaseInputZ.contenu=="":
                result="Formulaire incomplet"
            elif floatNB(CaseInputY.contenu)=="Error" or floatNB(CaseInputZ.contenu)=="Error":
                result="Formulaire incorrect"
            else:
                result = str(round( (floatNB(CaseInputY.contenu) / floatNB(CaseInputZ.contenu))**2 ,3))

        TResult=Texte(result,(510,500),font2)
        if len(result)>2:
            if result[:3]=="For":
                TResult.color=(255,10,10)
            else:
                TResult.color=(0,0,0)

        TResult.affichage()













    pygame.display.flip()
    clock.tick(60)
