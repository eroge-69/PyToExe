marks=int(input("enter your marks"))
if (marks>100):
  print("error: please enter marks out of 100")
elif(marks>=90):
  print("A+")
elif(marks>=80):
  print("B+")
elif(marks>=60):
  print("B")
elif(marks<=60):
  print("fail")
