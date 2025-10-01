import random

n = random.randint(1,10)
g = int(input("enter number between 1 and 10: "))
while g != n:
  if g > n:
    print("less")
    g = int(input("enter number between 1 and 10: "))
  elif g < n:
    print("more")
    g = int(input("enter number between 1 and 10: "))
  else:
      print('enter a number between 1 and 10')
print("got it")