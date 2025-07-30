import panda3d.core
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
player = FirstPersonController()
Sky()

# نوع فعلی بلاک انتخاب‌شده
current_texture = 'grass.png'

boxes = []

# ساخت زمین
for y in [0, -1, -2]:
    for i in range(20):
        for j in range(20):
            tex = 'grass.png' if y == 0 else 'dirt.png' if y == -1 else 'stone.png'   # بالا چمن، پایین سنگ
            box = Button(
                color=color.white,
                model='cube',
                position=(j, y, i),
                texture=tex,
                parent=scene,
                origin_y=0.5
            )
            boxes.append(box)

# انتخاب نوع بلاک
def input(key):
    global current_texture

    # تغییر نوع بلوک
    if key == '1':
        current_texture = 'grass.png'
    elif key == '2':
        current_texture = 'dirt.png'
    elif key == '3':
        current_texture = 'stone.png'


    # اضافه کردن یا حذف کردن بلوک
    for box in boxes:
        if box.hovered:
            if key == 'right mouse down':
                new = Button(
                    color=color.white,
                    model='cube',
                    position=box.position + mouse.normal,
                    texture=current_texture,
                    parent=scene,
                    origin_y=0.5
                )
                boxes.append(new)
            if key == 'left mouse down':
                boxes.remove(box)
                destroy(box)

def update():
      if held_keys["escape"]:
        application.quit()


  
app.run()
