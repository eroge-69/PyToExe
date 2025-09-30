import turtle

# إعداد النافذة
window = turtle.Screen()
window.bgcolor("white")

# إنشاء السلحفاة
t = turtle.Turtle()
t.speed(10)

# رسم الزهرة
def draw_flower_simple():
    # رسم البتلات
    colors = ["red", "orange", "yellow", "pink", "purple"]
    
    for i in range(36):
        t.color(colors[i % 5])
        t.forward(100)
        t.right(45)
        t.forward(100)
        t.right(135)
        t.forward(100)
        t.right(45)
        t.forward(100)
        t.right(135)
        t.right(10)
    
    # رسم المركز
    t.color("brown")
    t.dot(50)

# رسم الزهرة البسيطة
draw_flower_simple()

# إخفاء السلحفاة
t.hideturtle()

# الانتظار حتى النقر لإغلاق النافذة
window.exitonclick()