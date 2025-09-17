# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: QrKode-Inator5000.py
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import csv
from PIL import Image, ImageDraw, ImageFont
import segno
import os
with open('qr.csv', 'r') as f:
    reader = csv.reader(f)
    your_list = list(reader)
    images = []
    for i in your_list:
        codefromcsv = i[0]
        print(codefromcsv)
        qrcode = segno.make(codefromcsv, micro=False)
        qrcode.save(str(codefromcsv) + '.png', scale=10)
        font = ImageFont.truetype('C:\Windows\Fonts\DejaVuSans.ttf', 25)
        img = Image.open(str(codefromcsv) + '.png')
        draw = ImageDraw.Draw(img)
        draw.text((145.0, 290), str(codefromcsv), font=font, align='center', bold=True, size=100, anchor='ms')
        img.save('a_' + str(codefromcsv) + '.png')
        images.append(Image.open('a_' + str(codefromcsv) + '.png').convert('RGB'))
    if images:
        images[0].save('all_codes.pdf', save_all=True, append_images=images[1:])
    for i in your_list:
        os.remove(str(i[0]) + '.png')
        os.remove('a_' + str(i[0]) + '.png')