# # import turtle
# # import random
# # import time
# # # from pygame import mixer

# # # mixer.init()
# # # mixer.music.load("Sidna - Happy Birthday (320).mp3")  

# # bg = turtle.Screen()
# # bg.bgcolor("black")
# # # mixer.music.play()
# # Name = "Sana"
# # turtle.penup()
# # turtle.goto(-170, -180)
# # turtle.color("white")
# # turtle.pendown()
# # turtle.forward(350)

# # turtle.penup()
# # turtle.goto(-160, -150)
# # turtle.color("white")
# # turtle.pendown()
# # turtle.forward(300)

# # turtle.penup()
# # turtle.goto(-150, -120)
# # turtle.color("white")
# # turtle.pendown()
# # turtle.forward(250)
# # bg.bgcolor("lightgreen")

# # turtle.penup()
# # turtle.goto(-100, -100)
# # turtle.color("white")
# # turtle.begin_fill()
# # turtle.pendown()
# # turtle.forward(140)
# # turtle.left(90)
# # turtle.forward(95)
# # turtle.left(90)
# # turtle.forward(140)
# # turtle.left(90)
# # turtle.forward(95)
# # turtle.end_fill()
# # bg.bgcolor("lightblue")


# # turtle.penup()
# # turtle.goto(-90, 0)
# # turtle.color("red")
# # turtle.left(180)
# # turtle.pendown()
# # turtle.forward(20)
# # turtle.penup()
# # turtle.goto(-60, 0)
# # turtle.color("blue")
# # turtle.pendown()
# # turtle.forward(20)
# # turtle.penup()
# # turtle.goto(-30, 0)
# # turtle.color("yellow")
# # turtle.pendown()
# # turtle.forward(20)
# # turtle.penup()
# # turtle.goto(0, 0)
# # turtle.color("green")
# # turtle.pendown()
# # turtle.forward(20)
# # turtle.penup()
# # turtle.goto(30, 0)
# # turtle.color("purple")
# # turtle.pendown()
# # turtle.forward(20)
# # bg.bgcolor("orange")


# # colors = ["red", "orange", "yellow", "green", "blue", "purple", "black"]
# # turtle.penup()
# # turtle.goto(-40, -50)
# # turtle.pendown()
# # for each_color in colors:
# #     angle = 360 / len(colors)
# #     turtle.color(each_color)
# #     turtle.circle(10)
# #     turtle.right(angle)
# #     turtle.forward(10)
# # bg.bgcolor("purple")
# # turtle.penup()
# # turtle.goto(-150, 50)
# # turtle.color("#5CB65B")
# # turtle.pendown()
# # turtle.write(arg=f"Happy Birthday {Name} jon :) !", align="center", font=("jokerman", 20, "normal"))
# # time.sleep(1.5)

# # # Bouncing Animation
# # for _ in range(20):
# #     turtle.penup()
# #     turtle.goto(-150, 50)
# #     turtle.pendown()
# #     turtle.clear()
# #     turtle.penup()
# #     turtle.goto(-150, 50 - _ * 10)
# #     turtle.pendown()
# #     turtle.write(arg=f"Happy Birthday {Name} jon :) !", align="left", font=("jokerman", 20, "normal"))
# #     time.sleep(0.5)

# # turtle.done()
# # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# # import turtle
# # import random
# # import time
# # # from pygame import mixer

# # # تنظیمات اولیه
# # # mixer.init()
# # # mixer.music.load("happy_birthday_song.mp3")  # نیاز به فایل صوتی
# # # mixer.music.play(-1)

# # # تنظیمات صفحه
# # bg = turtle.Screen()
# # bg.bgcolor("black")
# # bg.title("Happy Birthday!")
# # bg.setup(width=800, height=600)

# # # تنظیمات عمومی
# # turtle.speed(0)
# # turtle.hideturtle()

# # # ستارههای پسزمینه
# # def stars():
# #     star = turtle.Turtle()
# #     star.hideturtle()
# #     star.speed(0)
# #     for _ in range(100):
# #         star.penup()
# #         star.goto(random.randint(-380, 380), random.randint(-280, 280))
# #         star.color(random.choice(["gold", "white", "silver"]))
# #         star.pendown()
# #         star.dot(random.randint(2, 5))

# # # رسم کیک
# # def draw_cake():
# #     # لایه پایینی
# #     turtle.penup()
# #     turtle.goto(-120, -250)
# #     turtle.color("#FFD700")
# #     turtle.begin_fill()
# #     turtle.pendown()
# #     for _ in range(2):
# #         turtle.forward(240)
# #         turtle.left(90)
# #         turtle.forward(120)
# #         turtle.left(90)
# #     turtle.end_fill()

# #     # لایه بالایی
# #     turtle.penup()
# #     turtle.goto(-90, -130)
# #     turtle.color("#FF6347")
# #     turtle.begin_fill()
# #     turtle.pendown()
# #     for _ in range(2):
# #         turtle.forward(180)
# #         turtle.left(90)
# #         turtle.forward(90)
# #         turtle.left(90)
# #     turtle.end_fill()

# #     # شمعها
# #     candle_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
# #     for x in [-80, -40, 0, 40, 80]:
# #         turtle.penup()
# #         turtle.goto(x, -80)
# #         turtle.color(random.choice(candle_colors))
# #         turtle.begin_fill()
# #         turtle.pendown()
# #         for _ in range(2):
# #             turtle.forward(8)
# #             turtle.left(90)
# #             turtle.forward(40)
# #             turtle.left(90)
# #         turtle.end_fill()

# # # انیمیشن شعله
# # def animate_flames():
# #     flames = []
# #     for x in [-80, -40, 0, 40, 80]:
# #         f = turtle.Turtle()
# #         f.hideturtle()
# #         f.penup()
# #         f.goto(x + 4, -40)
# #         f.color("#FFA500")
# #         flames.append(f)
    
# #     for _ in range(30):
# #         for f in flames:
# #             f.clear()
# #             f.color(random.choice(["#FF4500", "#FFD700", "#FF0000"]))
# #             f.shapesize(0.5)
# #             f.dot(random.randint(8, 12))
# #             f.sety(f.ycor() + random.uniform(-2, 2))
# #         time.sleep(0.1)

# # # بادکنکها
# # def balloons():
# #     colors = ["red", "blue", "green", "purple", "orange", "pink"]
# #     balloons = []
# #     for _ in range(12):
# #         b = turtle.Turtle()
# #         b.shape("circle")
# #         b.color(random.choice(colors))
# #         b.shapesize(1.5, 3.0)
# #         b.speed(0)
# #         b.penup()
# #         b.goto(random.randint(-300, 300), random.randint(-400, -200))
# #         b.setheading(90)
# #         balloons.append(b)
    
# #     for _ in range(150):
# #         for b in balloons:
# #             b.forward(3)
# #             b.left(random.randint(-5, 5))
# #             if b.ycor() > 280:
# #                 b.goto(random.randint(-300, 300), random.randint(-400, -200))

# # # متن رنگینکمانی
# # def rainbow_text():
# #     text = turtle.Turtle()
# #     text.hideturtle()
# #     text.penup()
# #     text.goto(-200, 200)
# #     colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    
# #     for i, char in enumerate("Happy Birthday Sana!"):
# #         text.color(colors[i % len(colors)])
# #         text.write(char, align="center", font=("Comic Sans MS", 32, "bold"))
# #         text.forward(32)
# #         time.sleep(0.1)

# # # کنفتی
# # def confetti():
# #     pieces = []
# #     for _ in range(100):
# #         p = turtle.Turtle()
# #         p.shape("circle")
# #         p.shapesize(0.3)
# #         p.color(random.choice(["red", "blue", "gold", "green", "purple"]))
# #         p.speed(0)
# #         p.penup()
# #         p.goto(0, 0)
# #         pieces.append(p)
    
# #     for _ in range(50):
# #         for p in pieces:
# #             p.setx(p.xcor() + random.randint(-15, 15))
# #             p.sety(p.ycor() + random.randint(0, 20))
# #             p.right(random.randint(0, 360))
# #         time.sleep(0.05)

# # # اجرای مراحل
# # stars()
# # draw_cake()
# # animate_flames()
# # balloons()
# # rainbow_text()
# # confetti()

# # # پاکسازی و پیام نهایی
# # turtle.clear()
# # bg.bgcolor("black")
# # turtle.penup()
# # turtle.goto(0, 0)
# # turtle.color("gold")
# # turtle.write("Click to Exit", align="center", font=("Arial", 24, "normal"))

# # # انتظار برای کلیک
# # bg.exitonclick()
# # mixer.music.stop()
# # turtle.done()
# # ////////////////////////////////////////////////////////////////////////////////////////////////////


# import turtle
# import random
# import time
# import winsound
# import threading

# # تنظیمات صفحه
# bg = turtle.Screen()
# bg.bgcolor("black")
# bg.title("Happy Birthday!")
# bg.setup(width=800, height=600)

# # فرکانسهای نتهای موسیقی تولدت مبارک
# MELODY = [
#     # جمله اول: "Happy birthday to you"
#     (261, 400), (261, 400), (293, 800), (261, 800), (349, 800), (329, 1200),
    
#     # جمله دوم: "Happy birthday to you"
#     (261, 400), (261, 400), (293, 800), (261, 800), (392, 800), (349, 1200),
    
#     # جمله سوم: "Happy birthday dear Sana"
#     (261, 400), (261, 400), (523, 400), (440, 400),  # Happy birthday
#     (349, 800), (349, 400), (392, 400),  # dear Sa-
#     (440, 1600),  # -na
    
#     # جمله چهارم: "Happy birthday to you"
#     (466, 400), (466, 400), (440, 800), (349, 800), (392, 800), (349, 1600)
# ]

# def play_music():
#     while True:
#         for freq, duration in MELODY:
#             winsound.Beep(freq, duration)

# # شروع موسیقی در یک نخ جداگانه
# music_thread = threading.Thread(target=play_music)
# music_thread.daemon = True
# music_thread.start()

# # بقیه کدهای گرافیکی شما...
# # ---------------------------
# turtle.speed(0)
# turtle.hideturtle()

# bg = turtle.Screen()
# bg.bgcolor("black")
# bg.title("Happy Birthday!")
# bg.setup(width=800, height=600)

# # تنظیمات عمومی
# turtle.speed(0)
# turtle.hideturtle()

# # ستارههای پسزمینه
# def stars():
#     star = turtle.Turtle()
#     star.hideturtle()
#     star.speed(0)
#     for _ in range(100):
#         star.penup()
#         star.goto(random.randint(-380, 380), random.randint(-280, 280))
#         star.color(random.choice(["gold", "white", "silver"]))
#         star.pendown()
#         star.dot(random.randint(2, 5))

# # رسم کیک
# def draw_cake():
#     # لایه پایینی
#     turtle.penup()
#     turtle.goto(-120, -250)
#     turtle.color("#FFD700")
#     turtle.begin_fill()
#     turtle.pendown()
#     for _ in range(2):
#         turtle.forward(240)
#         turtle.left(90)
#         turtle.forward(120)
#         turtle.left(90)
#     turtle.end_fill()

#     # لایه بالایی
#     turtle.penup()
#     turtle.goto(-90, -130)
#     turtle.color("#FF6347")
#     turtle.begin_fill()
#     turtle.pendown()
#     for _ in range(2):
#         turtle.forward(180)
#         turtle.left(90)
#         turtle.forward(90)
#         turtle.left(90)
#     turtle.end_fill()

#     # شمعها
#     candle_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
#     for x in [-80, -40, 0, 40, 80]:
#         turtle.penup()
#         turtle.goto(x, -60)
#         turtle.color(random.choice(candle_colors))
#         turtle.begin_fill()
#         turtle.pendown()
#         for _ in range(2):
#             turtle.forward(8)
#             turtle.left(90)
#             turtle.forward(40)
#             turtle.left(90)
#         turtle.end_fill()
#         # قلب پایین متن
#     heart = turtle.Turtle()
#     heart.hideturtle()
#     heart.color("red")
#     heart.penup()
#     heart.goto(57, -235)
#     heart.write("❤️", align="center", font=("Arial", 58, "normal"))
# # انیمیشن شعله
# def animate_flames():
#     flames = []
#     for x in [-80, -40, 0, 40, 80]:
#         f = turtle.Turtle()
#         f.hideturtle()
#         f.penup()
#         f.goto(x + 4, -20)
#         f.color("#FFA500")
#         flames.append(f)
    
#     for _ in range(30):
#         for f in flames:
#             f.clear()
#             f.color(random.choice(["#FF4500", "#FFD700", "#FF0000"]))
#             f.shapesize(0.5)
#             f.dot(random.randint(8, 12))
#             f.sety(f.ycor() + random.uniform(-2, 2))
#         time.sleep(0.1)


# # متن رنگینکمانی
# def rainbow_text():
#     text = turtle.Turtle()
#     text.hideturtle()
#     text.penup()
#     text.goto(-280, 200)
#     colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    
#     for i, char in enumerate("Happy Birthday Sana!"):
#         text.color(colors[i % len(colors)])
#         text.write(char, align="center", font=("Comic Sans MS", 32, "bold"))
#         text.forward(32)
#         time.sleep(0.1)


# stars()
# draw_cake()
# rainbow_text()
# animate_flames()

# bg.exitonclick()
# turtle.done()


import turtle
import random
import time
import winsound
import threading
import math

# تنظیمات صفحه
bg = turtle.Screen()
bg.bgcolor("black")
bg.title("🎉 Happy Birthday! 🎉")
bg.setup(width=1000, height=700)
bg.tracer(0)  # برای انیمیشن‌های نرم‌تر

# نام شخص - قابل تغییر
BIRTHDAY_NAME = "Farnia"

# ملودی تولدت مبارک فرنیا (نت‌ها و مدت زمان)
MELODY = [
    (261, 400), (261, 400), (293, 800), (261, 800), (349, 800), (329, 1200),
    (261, 400), (261, 400), (293, 800), (261, 800), (392, 800), (349, 1200),
    (261, 400), (261, 400), (523, 400), (440, 400),
    (349, 800), (349, 400), (392, 400),
    (440, 800), (392, 400), (349, 400), (329, 400), (293, 1200), # Happy birthday dear Fer-
    (466, 400), (466, 400), (440, 800), (349, 800), (392, 800), (349, 1600)
]

def play_music():
    """پخش موسیقی تولدت مبارک"""
    try:
        for freq, duration in MELODY:
            winsound.Beep(freq, duration)
            time.sleep(duration/1000 * 0.1)
    except:
        pass  # اگر صدا کار نکرد، ادامه بده

def play_firework_sound():
    """صدای آتش‌بازی"""
    try:
        for i in range(5):
            winsound.Beep(800 + i*100, 200)
            time.sleep(0.1)
    except:
        pass

# شروع موسیقی در یک نخ جداگانه
music_thread = threading.Thread(target=play_music)
music_thread.daemon = True
music_thread.start()

# تنظیمات عمومی
turtle.speed(0)
turtle.hideturtle()

# لیست برای نگهداری اشیاء انیمیشن
animated_objects = []

# ستاره‌های پس‌زمینه با انیمیشن چشمک‌زن
def create_stars():
    stars = []
    for _ in range(150):
        star = turtle.Turtle()
        star.hideturtle()
        star.speed(0)
        star.penup()
        star.goto(random.randint(-480, 480), random.randint(-340, 340))
        star.color(random.choice(["gold", "white", "silver", "lightblue", "pink"]))
        star.dot(random.randint(1, 4))
        stars.append(star)
    return stars

# انیمیشن ستاره‌های چشمک‌زن
def animate_stars(stars):
    for star in stars:
        if random.random() < 0.1:  # 10% احتمال تغییر رنگ
            star.color(random.choice(["gold", "white", "silver", "lightblue", "pink"]))
            star.dot(random.randint(1, 4))

# رسم کیک با جزئیات بیشتر
def draw_cake():
    # سایه کیک
    turtle.penup()
    turtle.goto(-125, -255)
    turtle.color("gray")
    turtle.begin_fill()
    turtle.pendown()
    for _ in range(2):
        turtle.forward(250)
        turtle.left(90)
        turtle.forward(125)
        turtle.left(90)
    turtle.end_fill()
    
    # لایه پایینی
    turtle.penup()
    turtle.goto(-120, -250)
    turtle.color("#FFD700")
    turtle.begin_fill()
    turtle.pendown()
    for _ in range(2):
        turtle.forward(240)
        turtle.left(90)
        turtle.forward(120)
        turtle.left(90)
    turtle.end_fill()

    # تزئینات لایه پایینی
    turtle.penup()
    turtle.goto(-110, -200)
    turtle.color("#FFA500")
    for i in range(12):
        turtle.goto(-110 + i*20, -200)
        turtle.dot(8)

    # لایه بالایی
    turtle.penup()
    turtle.goto(-90, -130)
    turtle.color("#FF6347")
    turtle.begin_fill()
    turtle.pendown()
    for _ in range(2):
        turtle.forward(180)
        turtle.left(90)
        turtle.forward(90)
        turtle.left(90)
    turtle.end_fill()

    # تزئینات لایه بالایی
    turtle.penup()
    turtle.goto(-80, -80)
    turtle.color("#FF4500")
    for i in range(9):
        turtle.goto(-80 + i*20, -80)
        turtle.dot(6)

# شمع‌های رنگی با شعله و قابلیت خاموش شدن
class Candle:
    def __init__(self, x, color):
        self.body = turtle.Turtle()
        self.body.hideturtle()
        self.body.speed(0)
        self.body.penup()
        self.body.goto(x, -60)
        self.body.color(color)
        self.body.begin_fill()
        self.body.pendown()
        for _ in range(2):
            self.body.forward(8)
            self.body.left(90)
            self.body.forward(40)
            self.body.left(90)
        self.body.end_fill()
        self.body.penup()
        self.body.showturtle()
        # شعله
        self.flame = turtle.Turtle()
        self.flame.hideturtle()
        self.flame.speed(0)
        self.flame.penup()
        self.flame.goto(x+4, -20)
        self.flame.color("#FFA500")
        self.flame_on = True
    def animate_flame(self):
        if self.flame_on:
            self.flame.clear()
            self.flame.color(random.choice(["#FF4500", "#FFD700", "#FF0000", "#FF69B4"]))
            self.flame.dot(random.randint(8, 14))
            self.flame.sety(self.flame.ycor() + random.uniform(-2, 2))
    def blow_out(self):
        self.flame.clear()
        self.flame_on = False

candles = []
def create_candles():
    global candles
    candles = []
    candle_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#FF69B4"]
    for i, x in enumerate([-80, -50, -20, 10, 40, 70]):
        candles.append(Candle(x, candle_colors[i % len(candle_colors)]))

def animate_flames():
    for _ in range(50):
        for candle in candles:
            candle.animate_flame()
        bg.update()
        time.sleep(0.1)

# صدای فوت
import platform
if platform.system() == "Windows":
    def play_blow_sound():
        try:
            winsound.Beep(300, 100)
            winsound.Beep(200, 100)
        except:
            pass
else:
    def play_blow_sound():
        pass

# دکمه فوت
def blow_out_candles(x=None, y=None):
    for candle in candles:
        candle.blow_out()
    play_blow_sound()
    # پیام خاموش شدن
    msg = turtle.Turtle()
    msg.hideturtle()
    msg.penup()
    msg.goto(0, 0)
    msg.color("#00CED1")
    msg.write("شمع‌ها خاموش شدند! 🎉", align="center", font=("B Nazanin", 28, "bold"))
    bg.update()
    time.sleep(2)
    msg.clear()

# دکمه گرافیکی فوت
def draw_blow_button():
    btn = turtle.Turtle()
    btn.hideturtle()
    btn.penup()
    btn.goto(350, -300)
    btn.shape("square")
    btn.shapesize(2, 6)
    btn.color("#2222FF")
    btn.fillcolor("#AADDFF")
    btn.pendown()
    btn.begin_fill()
    for _ in range(2):
        btn.forward(120)
        btn.left(90)
        btn.forward(40)
        btn.left(90)
    btn.end_fill()
    btn.penup()
    btn.goto(410, -295)
    btn.color("#2222FF")
    btn.write(" فوت کن! ", align="center", font=("B Nazanin", 18, "bold"))
    btn.penup()
    btn.goto(350, -300)
    btn.showturtle()
    # ثبت کلیک روی دکمه
    def on_click(x, y):
        if 350 <= x <= 470 and -300 <= y <= -260:
            blow_out_candles()
    bg.onclick(on_click)

# بادکنک‌های شناور
def create_balloons():
    balloons = []
    colors = ["red", "blue", "green", "purple", "orange", "pink", "yellow", "cyan"]
    for _ in range(20):
        balloon = turtle.Turtle()
        balloon.shape("circle")
        balloon.color(random.choice(colors))
        balloon.shapesize(1.5, 3.0)
        balloon.speed(0)
        balloon.penup()
        balloon.goto(random.randint(-400, 400), random.randint(-500, -200))
        balloon.setheading(90)
        balloons.append(balloon)
    return balloons

# انیمیشن بادکنک‌ها
def animate_balloons(balloons):
    for _ in range(200):
        for balloon in balloons:
            balloon.forward(random.randint(1, 4))
            balloon.left(random.randint(-5, 5))
            if balloon.ycor() > 350:
                balloon.goto(random.randint(-400, 400), random.randint(-500, -200))
        bg.update()
        time.sleep(0.05)

# کنفتی رنگی
def create_confetti():
    confetti_pieces = []
    colors = ["red", "blue", "gold", "green", "purple", "orange", "pink", "cyan"]
    for _ in range(100):
        piece = turtle.Turtle()
        piece.shape("circle")
        piece.shapesize(0.3)
        piece.color(random.choice(colors))
        piece.speed(0)
        piece.penup()
        piece.goto(random.randint(-400, 400), random.randint(200, 400))
        confetti_pieces.append(piece)
    return confetti_pieces

# انیمیشن کنفتی
def animate_confetti(confetti_pieces):
    for _ in range(100):
        for piece in confetti_pieces:
            piece.setx(piece.xcor() + random.randint(-20, 20))
            piece.sety(piece.ycor() + random.randint(-30, -5))
            piece.right(random.randint(0, 360))
            if piece.ycor() < -350:
                piece.goto(random.randint(-400, 400), random.randint(200, 400))
        bg.update()
        time.sleep(0.05)

# متن رنگین‌کمانی با انیمیشن
def rainbow_text():
    text = turtle.Turtle()
    text.hideturtle()
    text.penup()
    text.goto(-350, 250)
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "cyan"]
    
    # انیمیشن تایپ کردن متن
    message = f"Happy Birthday {BIRTHDAY_NAME}! 🎉"
    for i, char in enumerate(message):
        text.color(colors[i % len(colors)])
        text.write(char, align="center", font=("Comic Sans MS", 28, "bold"))
        text.forward(25)
        bg.update()
        time.sleep(0.1)

# قلب‌های شناور
def create_hearts():
    hearts = []
    for _ in range(15):
        heart = turtle.Turtle()
        heart.hideturtle()
        heart.speed(0)
        heart.penup()
        heart.goto(random.randint(-400, 400), random.randint(-300, 300))
        heart.color(random.choice(["red", "pink", "magenta"]))
        heart.write("❤️", align="center", font=("Arial", random.randint(20, 40), "normal"))
        hearts.append(heart)
    return hearts

# انیمیشن قلب‌ها
def animate_hearts(hearts):
    for _ in range(100):
        for heart in hearts:
            heart.sety(heart.ycor() + random.randint(1, 3))
            heart.setx(heart.xcor() + random.randint(-2, 2))
            if heart.ycor() > 350:
                heart.goto(random.randint(-400, 400), random.randint(-400, -200))
        bg.update()
        time.sleep(0.1)

# کیک با انیمیشن چرخش
def spinning_cake():
    cake = turtle.Turtle()
    cake.hideturtle()
    cake.speed(0)
    cake.penup()
    cake.goto(0, 0)
    
    for _ in range(36):
        cake.clear()
        cake.color("#FFD700")
        cake.begin_fill()
        cake.pendown()
        for _ in range(4):
            cake.forward(100)
            cake.left(90)
        cake.end_fill()
        cake.right(10)
        bg.update()
        time.sleep(0.1)

# آتش‌بازی
def create_fireworks():
    """ایجاد آتش‌بازی در نقاط مختلف صفحه"""
    firework_positions = [(0, 200), (-200, 150), (200, 150), (-100, 100), (100, 100)]
    
    for x, y in firework_positions:
        play_firework_sound()
        firework = turtle.Turtle()
        firework.hideturtle()
        firework.speed(0)
        firework.penup()
        firework.goto(x, y)
        
        colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"]
        for _ in range(20):
            firework.color(random.choice(colors))
            firework.dot(random.randint(3, 8))
            firework.goto(x + random.randint(-80, 80), y + random.randint(-80, 80))
            bg.update()
            time.sleep(0.05)
        firework.clear()

# اجرای مراحل با انیمیشن‌های پیشرفته
def main_animation():
    # ایجاد ستاره‌ها
    stars = create_stars()
    
    # رسم کیک
    draw_cake()
    
    # ایجاد شمع‌ها
    create_candles()
    
    # متن رنگین‌کمانی
    rainbow_text()
    
    # انیمیشن ستاره‌ها
    for _ in range(20):
        animate_stars(stars)
        bg.update()
        time.sleep(0.2)
    
    # انیمیشن شعله‌ها
    animate_flames()
    
    # ایجاد بادکنک‌ها
    balloons = create_balloons()
    
    # انیمیشن بادکنک‌ها
    animate_balloons(balloons)
    
    # ایجاد کنفتی
    confetti_pieces = create_confetti()
    
    # انیمیشن کنفتی
    animate_confetti(confetti_pieces)
    
    # ایجاد قلب‌ها
    hearts = create_hearts()
    
    # انیمیشن قلب‌ها
    animate_hearts(hearts)
    
    # کیک چرخان
    spinning_cake()
    
    # آتش‌بازی
    create_fireworks()
    
    # پیام نهایی
    final_message = turtle.Turtle()
    final_message.hideturtle()
    final_message.penup()
    final_message.goto(0, -100)
    final_message.color("gold")
    final_message.write("Click anywhere to exit! 🎂", align="center", font=("Arial", 24, "bold"))
    bg.update()
    time.sleep(5)
    bg.bye()

# اثرات کلیک
def create_click_effect(x, y):
    """ایجاد اثرات رنگی در محل کلیک"""
    effect = turtle.Turtle()
    effect.hideturtle()
    effect.speed(0)
    effect.penup()
    effect.goto(x, y)
    
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink"]
    for i in range(10):
        effect.color(random.choice(colors))
        effect.dot(random.randint(5, 20))
        effect.goto(x + random.randint(-50, 50), y + random.randint(-50, 50))
        bg.update()
        time.sleep(0.05)
    effect.clear()

# تنظیم کلیک
bg.onclick(create_click_effect)

# اجرای انیمیشن اصلی
main_animation()

# پیام تعاملی
interactive_message = turtle.Turtle()
interactive_message.hideturtle()
interactive_message.penup()
interactive_message.goto(0, -150)
interactive_message.color("lightblue")
interactive_message.write("Click anywhere for surprise effects! 🎊", align="center", font=("Arial", 20, "bold"))

# انتظار برای کلیک
bg.exitonclick()
turtle.done()