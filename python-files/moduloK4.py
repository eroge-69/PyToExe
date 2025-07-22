#!/usr/bin/env python3

#*************************************************************
#-- Aufteilung eines Geldbetrags in Scheine u. Münzen --
#-- unter Verwendung von Modulo --
#*************************************************************

geld = input("Geldbetrag in Euro: ")
geld = int(geld)
zehner = geld // 10
geld = geld % 10
fuenfer = geld // 5
geld = geld % 5
zweier = geld // 2
geld = geld % 2
einer = geld // 1
geld = geld % 1
print("Der Geldbetrag teilt sich wie folgt auf:")
print(str(zehner) + "-mal Zehner")
print(str(fuenfer) + "-mal Fünfer")
print(str(zweier) + "-mal Zweier\n" + str(einer) + "-mal Einer")

input()
