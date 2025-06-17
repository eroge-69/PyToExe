#Autor: Moritz Wilhelm
#Datum: 27.03.2025-12.06.2025
#Zweck: Game of life
#
#Logik: 1. Lebt bei 2 oder 3 Nachbarn
#       2. Geburt bei 3 lebendigen Zellen
#       (3.) Tod bei <2, >3
#
#Spielfeld: 87X49
#
#... 3 2 1 0
#           0
#           1
#           2
#           3
# Mitte [43, 24]
#
#Zustand ~ lebendig/tot

from turtle import * #Modul zur Grafikausgabe
from time import * #Modul für die Begrenzung der Aktualisierungsrate
from random import * #Modul für Zufallsereignisse
global spielfeld 



class Spielfeld: #Spielfeld, für die Zuordnung aller Zellen 
    def __init__(self):
        self.__ZellenListe=[ [],[],[],[],[] ,[],[],[],[],[], #Spielfeld (Liste von Listen) 
                             [],[],[],[],[] ,[],[],[],[],[],
                             [],[],[],[],[] ,[],[],[],[],[],
                             [],[],[],[],[] ,[],[],[],[],[],
                             [],[],[],[],[] ,[],[],[],[]    ]
        self.__yPositionListegrau=[]
        self.__xPositionListegrau=[]
        self.__yPositionListeweiß=[]
        self.__xPositionListeweiß=[]

        
        
    def überprüfen(self): #Aufruf führt einen "Lebenszyklus" gemäß der Regeln durch
        
        for i in range (49):
            for j in range(87):
                AnzahllebendeZellen=0

                #Die Nachfolgenden 8 if Bedingungen zählen die Anzahl der lebendigen Nachbarn.
                #Nachbarn außerhalb des Spielfelds werden als tot gewertet
                if i+1<=48 and j+1<=86: #unten links
                    if self.__ZellenListe[i+1][j+1].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if i+1<=48:             #unten Mitte
                    if self.__ZellenListe[i+1][j].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if i+1<=48 and j-1>=0:  #unten rechts
                    if self.__ZellenListe[i+1][j-1].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if j+1<=86:             #Mitte links
                    if self.__ZellenListe[i][j+1].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if j-1>=0:              #Mitte rechts
                    if self.__ZellenListe[i][j-1].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if i-1>=0 and j+1<=86:  #oben links
                    if self.__ZellenListe[i-1][j+1].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if i-1>=0:              #oben Mitte
                    if self.__ZellenListe[i-1][j].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1
                if i-1>=0 and j-1>=0:   #oben rechts
                    if self.__ZellenListe[i-1][j-1].gibFarbe()=="white":
                        AnzahllebendeZellen=AnzahllebendeZellen+1

                #(Nachfolgenden 2 if Bedingungen) Merkt sich die Änderungen des Lebendigkeitsstatus der Zellen vor
                # um eine falsche Aktualisierung von rechts nach links und von oben nach unten zu verhindern
                # Das gesamte Spielfeld wird gleichzeitig aktualisiert (keine Zwischenzustände)
                if self.__ZellenListe[i][j].gibFarbe()=="white": # Fall Zelle überlebt (wenn sie lebt und sie 2 oder 3 lebendige Nachbarn hat)
                    if AnzahllebendeZellen<2 or AnzahllebendeZellen>3:
                        self.__yPositionListegrau.append(i)
                        self.__xPositionListegrau.append(j)

                if self.__ZellenListe[i][j].gibFarbe()=="grey":# Fall Zelle wird geboren (wenn sie tot ist und 3 lebendige Nachbarn hat)
                    if AnzahllebendeZellen==3:
                        self.__yPositionListeweiß.append(i)
                        self.__xPositionListeweiß.append(j)
        tracer(False)
        
        #(Nächsten 2 Schleifen) Alle Zellen die "neutot" oder "neulebendig" sind, erhalten eine Umfärbung
        for i in range (len(self.__yPositionListegrau)):
            self.__ZellenListe[self.__yPositionListegrau[0]][self.__xPositionListegrau[0]].Zellefärben("grey")
            self.__yPositionListegrau.pop(0)
            self.__xPositionListegrau.pop(0)

        for i in range (len(self.__yPositionListeweiß)):
            self.__ZellenListe[self.__yPositionListeweiß[0]][self.__xPositionListeweiß[0]].Zellefärben("white")
            self.__yPositionListeweiß.pop(0)
            self.__xPositionListeweiß.pop(0)
        tracer(True)


    def einfügen(self,x,y,Objekt):#Funktion zum einfügen von Zellen ins Spielfeld
        self.__ZellenListe[y].append(Objekt)
    
    def färben(self,x,y,farbe):#Funktion zum Umfärben einer Zelle (Zustandsänderung)
        self.__ZellenListe[y][x].Zellefärben(farbe)
        
    def gibFarbe(self,x,y):#Abfrage der Farbe einer Zelle (Zustand)
        return self.__ZellenListe[y][x].gibFarbe()
        
        

class Zelle: #Klasse Zelle enthält Informationen über den Zustand
    def __init__(self,xpos,ypos,wahrscheinlichkeit):
        self.__xpos=xpos
        self.__ypos=ypos
        self.__screen=Turtle()
        self.__screen.penup()
        self.__screen.goto(self.__xpos,self.__ypos)
        self.__screen.shape("square")

        #Je nach voreingestellter wahrscheinlichkeit, dass eine Zelle lebendig ist, wird sie mit dieser
        # "Lebendigkeitswahrscheinlichkeit" erzeugt
        if wahrscheinlichkeit==10:
            if randint(1,10)>1:
                self.__screen.color("grey")
                self.__Farbe="grey"
            else:
                self.__screen.color("white")
                self.__Farbe="white"
        elif wahrscheinlichkeit==25:
            if randint(1,4)>1:
                self.__screen.color("grey")
                self.__Farbe="grey"
            else:
                self.__screen.color("white")
                self.__Farbe="white"
        elif wahrscheinlichkeit==50:
            if randint(1,2)==1:
                self.__screen.color("grey")
                self.__Farbe="grey"
            else:
                self.__screen.color("white")
                self.__Farbe="white"
        elif wahrscheinlichkeit==75:
            if randint(1,100)>=75:
                self.__screen.color("grey")
                self.__Farbe="grey"
            else:
                self.__screen.color("white")
                self.__Farbe="white"

        else:
            self.__screen.color("grey")
            self.__Farbe="grey"
        
        
        
    def Zellefärben(self,farbe): #Funktion zum Umfärben einer Zelle (Zustandsänderung)
        self.__screen.color(farbe)
        self.__Farbe=farbe

    def gibFarbe(self): #Abfrage der Farbe einer Zelle (Zustand)
        return self.__Farbe

def leer():#Funktion zum Anhalten/ Fortsetzen der Aktualisierungszyklen mit der Leertaste(space)
            # nur für den selber platzieren Modus
    global pause
    if pause==True:
        pause=False
    else:
        pause=True

def warteaufstart():
    if temp=="Starten":
        tracer(False)
        ht()
        penup()
        
        #Modusauswahlseite
        goto(-350,200)
        pencolor("white")
        write("Game of Life", font=("Elephant", 80, "normal"))#Titel
        
        Höhe1=50
        Höhe2=-150
        
        goto(-600,Höhe1)
        write("Modus: Selber platzieren", font=("Calibri", 40, "normal"))#Modus selber platzieren
        Viereck(50,50,00,Höhe1)#Modus 1 Auswahlfeld


        goto(-600,Höhe2)
        write("Modus: Zufall", font=("Calibri", 40, "normal"))#Modi Zufall 
        Viereck(50,60,-250,Höhe2)
        goto(-243,Höhe2+10)
        write("10%", font=("Calibri", 20, "normal"))#Modus 2 Auswahlfeld
        
        Viereck(50,60,-100,Höhe2)
        goto(-93,Höhe2+10)
        write("25%", font=("Calibri", 20, "normal"))#Modus 3 Auswahlfeld
        
        Viereck(50,60,50,Höhe2)
        goto(58,Höhe2+10)
        write("50%", font=("Calibri", 20, "normal"))#Modus 4 Auswahlfeld
        
        Viereck(50,60,200,Höhe2)
        goto(208,Höhe2+10)
        write("75%", font=("Calibri", 20, "normal"))#Modus 5 Auswahlfeld

        
        
    else:
        Screen.ontimer(warteaufstart, 100)  # prüft alle 0.1s erneut, ob Eingabe erfolgt ist
   
#Funktion ist für den Startknopf zuständig 
def Startgedrückt(x,y):
    global temp
    if 200>=x>=-200 and 50>=y>=-50: #Bereich vom Startknopf
        Screen.onclick(None)
        tracer(False)
        Screen.clearscreen()
        Screen.bgcolor("grey")
        tracer(True)
        temp="Starten"
        Screen.onclick(Modusauswahl) #Weiter zur Modusauswahlseite


def Modusauswahl(x,y):
    
    if 50>=x>=0 and 100>=y>=50: #Bereich vom Selber platzieren Knopf
        temp="Selber platzieren"
        Spielstart(0)
    if -190>=x>=-250 and -100>=y>=-150: #Bereich vom 10% lebendige Zellen Knopf
        temp="10%"
        Spielstart(10)
    if -40>=x>=-100 and -100>=y>=-150: #Bereich vom 25% lebendige Zellen Knopf
        temp="25%"
        Spielstart(25)
    if 110>=x>=50 and -100>=y>=-150: #Bereich vom 50% lebendige Zellen Knopf
        temp="50%"
        Spielstart(50)
    if 260>=x>=200 and -100>=y>=-150: #Bereich vom 75% lebendige Zellen Knopf
        temp="75%"
        Spielstart(75)
        
def Viereck(Höhe,Breite,x,y):#Funktion zum Zeichnen von Vierecken
    tracer(False)
    ht()
    penup()
    goto(x,y)
    pendown()
    fd(Breite)
    lt(90)
    fd(Höhe)
    lt(90)
    fd(Breite)
    lt(90)
    fd(Höhe)
    lt(90)
    penup()

def pos(x,y):#Funktion zum Auswerten der  Zeigerposition wenn ein Linksklick ausgeführt wird
    for höhe in range(49):
        for breite in range(87):
            if x>=957-(22*breite)-11 and x<=957-(22*breite)+11 and y>=539-(22*höhe)-11 and y<=539-(22*höhe)+11:#Ermittelt das angeklickte Feld
                if spielfeld.gibFarbe(breite,höhe)=="grey":#Wenn tot
                    spielfeld.färben(breite,höhe,"white")#wird sie lebendig
                else:
                    spielfeld.färben(breite,höhe,"grey")#Gegenteilig zur vorherigen Ausführung


def Spielstart(wahrscheinlichkeit):#Funktion bestückt das Spielfeld mit lebendigen Zellen und startet den "Lebenszyklus"
                                   #Wenn selber platzieren gewählt wurde wird ein Spielfeld mit ausschließlich toten Zellen erzeugt
                                   #und der "Lebenszyklus" ist zunächst pausiert
    
    Screen.clearscreen()   #Löscht vorherige Seite
    Screen.bgcolor("black")
    tracer(False)#Pausiert Aktualisierung nach jedem Schritt
    
    for i in range(49):#y 
        for j in range(87):#x
            
            spielfeld.einfügen(j,i,Zelle(957-22*j,539-22*i,wahrscheinlichkeit)) #~Hd Bildschirmgröße 1914-   1078 |
                                                                                # Erstellt Zellen mit der angebenen Lebendigkeitswahrscheinlichkeit
    tracer(True)
  
    if wahrscheinlichkeit!=0:  #Alle Modi ausser selber platzieren
        while True:
            spielfeld.überprüfen()
            sleep(0.15)

            
    else:                      #selber platzieren Modus   
        global pause            
        pause=True
        screen=turtle.Screen()      #Erstellt Fenster mit Bezug zur Eingabe
        Screen.onclick(pos)         #bei einem Linksklick wird die Funktion pos Ausgeführt
        Screen.onkey(leer,"space")  #Wenn space (Leertaste) gedrückt wird, wird die Funktion leer ausgeführt
        Screen.listen()             #Prüft ob Eingabe erfolgt
        while True:                     #Endlosschleife zum Pausieren/Fortsetzen des "Lebenszykluses" 
            if pause==False:            
                spielfeld.überprüfen()  # "Lebenszyklus" wird einmalig ausgeführt
            sleep(0.15)                 
            update()

               
        
#--------Hauptprogramm----------

#Startbildschirm
screensize(canvwidth=1920, canvheight=1080, bg=None)
bgcolor("black")
tracer(False)

#Grafikfenster, Basis für alles grafische
import turtle
temp=False
Screen=turtle.Screen()
turtle.ht()
    
#Titel
bgcolor("grey")#Farbe und Aufbau vom Fenster
penup()
tracer(False)
ht()
goto(-350,200)
pencolor("white")
write("Game of Life", font=("Elephant", 80, "normal"))

#Startknopf
Viereck(100,400,-200,-50)
tracer(False)
fd(70)
write("Starten", font=("Calibri", 60, "normal"))


spielfeld=Spielfeld()
Screen.onclick(Startgedrückt)

warteaufstart()


#-----------------------


