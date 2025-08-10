def install_package(package):
   
    try:
        __import__(package)  # Attempt to import the module
        print(f"{package} is already installed.")
    except ImportError:
        print(f"Installing {package}...")
        try:
            # Run pip as a subprocess to install the package
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1) 


install_package("turtle")
import turtle
install_package("random")
import random
install_package("time")
import time

install_package("sys")
import sys 
install_package("subprocess")
import subprocess 



install_package("pygame")
import pygame # pyright: ignore[reportMissingImports]

pygame.mixer.init()
try:
    pygame.mixer.music.load("BDsong.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play()

finally:

    screen = turtle.Screen()
    screen.bgcolor("black")
    screen.title("Happy Birthday Nabanita!")


    pen = turtle.Turtle()
    pen.speed(-15)
    pen.hideturtle()


    def firework_burst(x, y):
        colors = ["red", "green", "blue", "yellow", "purple", "cyan"]
        pen.penup()
        pen.goto(x, y)
        pen.pendown()
        for _ in range(36):
            pen.color(random.choice(colors))
            pen.forward(300)
            pen.right(300)


    def display_name():
   
        pen.penup()
        pen.goto(-400,400)
        pen.pendown()
    
        pen.color("cyan")
        name = "Happy Birthday NABANITA [sleeping angel] 😂 😂 😂 😂 ❤️ ❤️ ❤️ "
   
        for char in name:
            pen.write(char, font=("Arial", 24, "normal"))
            time.sleep(0.01)
            pen.forward(25)


    for _ in range(5):
     x = random.randint(-600, 400)
     y = random.randint(-600, 50)
     firework_burst(x, y)


    display_name()

    def firework_b(x, y):
     colors = ["red", "green", "blue", "yellow", "purple", "cyan"]
     pen.penup()
     pen.goto(x, y)
     pen.pendown()
     for _ in range(200):
         pen.color(random.choice(colors))
         time.sleep(0)
         pen.forward(500)
         pen.right(179)

    for _ in range(9):
     x = random.randint(-800,400)
     y = random.randint(-500,50)
     firework_b(x, y)


    pen.hideturtle()
    screen.mainloop()



pygame.mixer.music.stop()


