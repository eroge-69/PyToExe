
print('введи сумму ') 
a=int(input())
b=(a-((a/100)*12))
print('введи курс ')
usd= int(input())
c= b*usd
c2= c- ((c/100)*2)
print('введи комсу ')
komsa = int(input())
c3= c2 - komsa
print (c3)