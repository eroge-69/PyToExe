
from turtle import *

dick_length_str = input("Enter dick length: ")
dick = int(dick_length_str)

color("pink")
pensize(9)
pu()
fd(60)
pd()
for n in range(270):
    fd(1)
    rt(1)
for n in range(270):
    back(1)
    rt(1)
rt(90)
fd(dick)
for n in range(90):
    fd(1)
    rt(1)
fd(0)
for n in range(90):
    fd(1)
    rt(1)

fd(dick)
done()