#x=int(input())
f=int(input("이차함수 일반형 식의 우변을 입력해주세요."))
#x값 입력
import turtle
t=turtle.Turtle()
t.shape("turtle")
t.penup()
t.goto(0,-200)
t.pendown()
t.left(90)
t.forward(400)
t.write("x")
t.penup()
t.goto(-400,0)
t.pendown()
t.goto(400,0)
t.pu()

#좌표평면 그리기
def f(x):
    global y
    y=(x+2)**2+5
    return(y)

for x in range(-150,150):
    f(x)
    print(y)
    t.goto(x,y/50)
    t.pd()
while True:
    user_input = input("Enter q to quit: ")
    if user_input.lower() == "q":
        break

