import random
run = True
person = 1
reply = ""
print("welcome to where's waldo")
print("you have to find waldo")
print("type in y or n depending if it is or is not waldo")

while run == True:
  person = random.randint(0,40)
  if person == 0:
    print("waldo")
    reply = input("")
    if reply == "y":
      print("you found waldo")
      run = False
    elif reply == "n":
      print ("wrong answer")
      run = False
    else:
      print("invalid answer")
      run = False
  else:
    print("not waldo")
    reply = input("")
    if reply == "n":
      run = True
    elif reply == "y":
      print ("wrong answer")
      run = False
    else:
      print("invalid answer")
      run = False


    
    