from PIL import Image
import imageio

static_img = Image.open("girl_static.png")
frames = []

for i in range(10):
    frame = static_img.rotate(i*2, resample=Image.BICUBIC)
    frames.append(frame)

frames[0].save('girl_animation.gif', save_all=True, append_images=frames[1:], duration=150, loop=0)