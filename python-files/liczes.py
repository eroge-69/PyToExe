liczby=[
	{
		"licz": 0,
		"es": "cero"
	},
	{
		"licz": 1,
		"es": "uno"
	},
	{
		"licz": 2,
		"es": "dos"
	},
	{
		"licz": 3,
		"es": "tres"
	},
	{
		"licz": 4,
		"es": "cuatro"
	},
	{
		"licz": 5,
		"es": "cinco"
	},
	{
		"licz": 6,
		"es": "seis"
	},
	{
		"licz": 7,
		"es": "siete"
	},
	{
		"licz": 8,
		"es": "ocho"
	},
	{
		"licz": 9,
		"es": "nueve"
	},
	{
		"licz": 10,
		"es": "diez"
	},
	{
		"licz": 11,
		"es": "once"
	},
	{
		"licz": 12,
		"es": "doce"
	},
	{
		"licz": 13,
		"es": "trece"
	},
	{
		"licz": 14,
		"es": "catorce"
	},
	{
		"licz": 15,
		"es": "quince"
	},
	{
		"licz": 16,
		"es": "diecise`is"
	},
	{
		"licz": 17,
		"es": "diecisiete"
	},
	{
		"licz": 18,
		"es": "dieciocho"
	},
	{
		"licz": 19,
		"es": "diecinueve"
	},
	{
		"licz": 20,
		"es": "veinte"
	},
	{
		"licz": 21,
		"es": "veintiuno"
	},
	{
		"licz": 22,
		"es": "veintido`s"
	},
	{
		"licz": 23,
		"es": "veintitre`s"
	},
	{
		"licz": 24,
		"es": "veinticuatro"
	},
	{
		"licz": 25,
		"es": "veinticinco"
	},
	{
		"licz": 26,
		"es": "veintise`is"
	},
	{
		"licz": 27,
		"es": "veintisiete"
	},
	{
		"licz": 28,
		"es": "veintiocho"
	},
	{
		"licz": 29,
		"es": "veintinueve"
	},
	{
		"licz": 30,
		"es": "treinta"
	},
	{
		"licz": 40,
		"es": "cuarenta"
	},
	{
		"licz": 50,
		"es": "cincuenta"
	},
	{
		"licz": 60,
		"es": "sesenta"
	},
	{
		"licz": 70,
		"es": "setenta"
	},
	{
		"licz": 80,
		"es": "ochenta"
	},
	{
		"licz": 90,
		"es": "noventa"
	},
	{
		"licz": 100,
		"es": "cien"
	},
	{
		"licz": 1000,
		"es": "mil"
	}
]

def znajdz(liczba):
	odp=list(filter(lambda x: x["licz"]==liczba, liczby))
	if len(odp)==0:
		return ""
	return odp[0]["es"]

def tysiac(liczba):
	if liczba==1:
		return "mil"
	return znajdz(liczba)+" "+"mil"

def setka(liczba, codalej=0):
	if liczba==0:
		return ""
	elif liczba==1:
		if codalej!=0:
			return "ciento"
		else:
			return "cien"
	elif liczba==5:
		return "quinientos"
	elif liczba==7:
		return "setecientos"
	elif liczba==9:
		return "novecientos"
	else:
		return znajdz(liczba)+"cientos"
		
def dzesiecjeden(liczba):
	if liczba==0:
		return ""
	if liczba%10==0:
		return znajdz(liczba)
	if liczba<30:
		return znajdz(liczba)
	else:
		return znajdz(liczba//10*10)+" y "+znajdz(liczba%10)


def calaliczba(liczba):
	if liczba==0:
		return "cero"
	else:
		tys=liczba//1000
		set=(liczba//100)%10
		dziesij=liczba%100
		tysiacSTR=tysiac(tys)
		setkaSTR=setka(set, dziesij)
		dziesjSTR=dzesiecjeden(dziesij)
		
		odp=tysiacSTR
		if setkaSTR!="":
			odp=odp+" "+setkaSTR
		if dziesjSTR!="":
			odp=odp+" "+dziesjSTR
		return odp


import random

while True:
	l=random.randint(1000,9999)
	es=calaliczba(l)
	odp=input("Podaj liczbę po hiszpańsku " + '\x1b[38;2;5;86;243m' + str(l) + '\x1b[0m')
	if odp==es:
		print('\x1b[38;2;0;255;0m' + 'DOBRZE' + '\x1b[0m')
	else:
		i=0
		while i<len(es):
			if i>=len(odp):
				print('\x1b[38;2;255;0;0m' + es[i::] + '\x1b[0m', end="")
				break
			if es[i]==odp[i]:
				print('\x1b[38;2;0;255;0m' + es[i] + '\x1b[0m', end="")
			else:
				print('\x1b[38;2;255;0;0m' + es[i] + '\x1b[0m', end="")
			i+=1
		print('\x1b[38;2;255;0;0m' + '\nŹLE' + '\x1b[0m')

