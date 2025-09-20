import pgzrun
HEIGHT = 500
WIDTH = 500
TITLE = "to move"
x = 225
y = 225
def draw():
    screen.fill("green")
    screen.draw.filled_rect(Rect(x, y, 50, 50), "pink")
def update():
    global x
    global y
    if keyboard.left:
        x -= 10
    if keyboard.right:
        x += 10
    if keyboard.up:
        y -= 10
    if keyboard.down:
        y += 10
pgzrun.go()
