import turtle 
    
t = turtle.Turtle()
t.hideturtle() #this hides the arrow
t.speed(0) #turn off animation

#This function draw a circle in x,y of radius r zoomed by a n factor
def drawZoomedCircle(x,y,r,n):
    t.pu()
    t.goto(x*n,(y-r)*n) #-r because we want xy as center and Turtles starts from border
    t.pd()
    t.circle(r*n)

n=1

drawZoomedCircle(5,3,1,n)
drawZoomedCircle(2,5,3,n)
drawZoomedCircle(0,0,0.2,n)