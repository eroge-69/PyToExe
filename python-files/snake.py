from gturtle import *
from random import randint
import sys

wait_counter = 0
counter = 0
max_lenght = 2
points = 0
highscore = 0

positions = []
red_points = []

running = True
player = None
eraser = None
draw = None

def is_collision(p1, p2, radius=15):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dist = (dx*dx + dy*dy)**0.5
    return dist < radius

# Runden auf Vielfaches von 15
def round_to_step(value, step=15):
    return round(value / step) * step

def onKeyPressed(key):
    global running, player
    current_heading = player.heading()

    if key == "ArrowLeft":
        if current_heading != 90:
            player.setHeading(270)
    elif key == "ArrowRight":
        if current_heading != 270:
            player.setHeading(90)
    elif key == "ArrowUp":
        if current_heading != 180:
            player.setHeading(0)
    elif key == "ArrowDown":
        if current_heading != 0:
            player.setHeading(180)
    elif key == "Escape":
        global running,points,highscore
        running = False
        points = 0
        setStatusText(f"Du hast das Spiel beendet. | Punkte: {points}")
        print("Spiel beendet | Highscore: ",highscore)
        sys.exit()
    elif key == "Enter":
        speed(0)
        player.clear()
        eraser.clear()
        player.home()
        eraser.home()
        player.showTurtle()
        positions.clear()
        red_points.clear()
        points = 0
        running = True
        game()
        setStatusText("Pfeiltasten zum Steuern.")

def game():
    global running,counter,points,highscore,wait_counter
    addStatusBar(20)
    setStatusText("Pfeiltasten zum Steuern.")
    wait_counter = randint(10, 50)
    while running:
        player.forward(15)
        player.setPenColor("green")
        player.dot(20)
        player.setPenColor("orange")
        player.dot(8)
        counter = counter + 1
        max_lenght = 2 + points
        if counter == wait_counter:
            counter = 0
            # Generiere roten Punkt sicher ohne Kollision mit Schlange
            while True:
                x = randint(-200, 200)
                y = randint(-200, 200)
                x = round_to_step(x, 15)
                y = round_to_step(y, 15)
                conflict = False
                for p in positions:
                    if is_collision((x, y), p, radius=15):
                        conflict = True
                        break
                if not conflict:
                    break
            draw.setPos(x, y)
            draw.dot(10)
            red_points.append((x, y))
            wait_counter = randint(10, 50)

        pos = player.getPos()
        if pos != None:
            # Check Kollision mit eigenem Körper
            for p in positions[:-2]:
                if is_collision(pos, p, radius=15):
                    running = False
                    playTone(100, 75)
                    delay(10)
                    playTone(75, 10)
                    delay(150)
                    playTone(45, 100)
                    delay(25)
                    playTone(40, 150)
                    setStatusText(f"Game Over | Punkte: {points} | Drücke Enter zum neustarten.")
                    print("Game over | Punkte: ",points)
                    if points > highscore:
                        highscore = points
                        print(f"Neuer Highscore! ({highscore})")
                    break
            
            # Check Kollision mit roten Punkten
            for rp in red_points:
                if is_collision(pos, rp, radius=10):
                    points += 1
                    playTone(450, 10)
                    delay(25)
                    playTone(1000, 100)
                    setStatusText(f"Punkte: {points}")
                    red_points.remove(rp)
                    break
        else:
            print("ERROR: pos = None")

        positions.append(pos)
        if len(positions) > max_lenght:
            oldest = positions.pop(0)
            eraser.setPos(oldest)
            eraser.dot(20)
    
        delay(50)

makeTurtle(keyPressed=onKeyPressed)
speed(0)
player = Turtle()
eraser = Turtle()
draw = Turtle()
player.setPenColor("green")
eraser.setPenColor("white")
eraser.setFillColor("white")
draw.setPenColor("red")

eraser.hideTurtle()
draw.hideTurtle()
player.clear()
eraser.clear()
player.home()
eraser.home()
player.showTurtle()
positions.clear()
game()
