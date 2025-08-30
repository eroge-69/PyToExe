from PIL import Image
from sys import argv
import struct
import os

def convert_etc2_2_img(etc2_file_path,width,height,show_flag=False):
    outname = os.path.basename(etc2_file_path)
    extension = os.path.splitext(etc2_file_path)[1]
    outname = outname.replace(extension,'.png')

    with open(etc2_file_path, 'rb') as f:
        f.seek(0x20)
        etc2_data = f.read()

    image = Image.new('RGBA', (width, height))
    block_size = 8
    offset = 0
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            for block_y in range(block_size):
                for block_x in range(block_size):
                    if offset + 4 <= len(etc2_data):
                        a, b, g, r = struct.unpack_from('BBBB', etc2_data, offset)
                        if a == 0:
                            r,g,b = 0,0,0
                        image.putpixel((x + block_x, y + block_y), (r, g, b, a))
                        offset += 4

    if show_flag == True:
        image.show()
    
    image.save(outname)
    return image,outname

def get_demesions(png_path):
    with Image.open(png_path) as image:
        w,h = image.size
        return w,h

def convert_img_2_etc2(png_file_path):
    outname = os.path.basename(png_file_path)
    extension = os.path.splitext(png_file_path)[1]
    outname = outname.replace(extension,'.3dst')

    with Image.open(png_file_path) as image:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        width, height = image.size
        etc2_data = bytearray()
        for y in range(0, height, 8):
            for x in range(0, width, 8):
                block_data = b''
                for block_y in range(8):
                    for block_x in range(8):
                        pixel = image.getpixel((x + block_x, y + block_y))
                        r, g, b, a = pixel
                        block_data += struct.pack('BBBB', a, b, g, r)

                etc2_data += block_data

        return bytes(etc2_data),outname

raw_list = ['--convert2image','-c2i']
raw_type = '.3dst'
show_false = ["--show-false","-sf"]
show_true = ["--show-true","-st"]
img_list = ['--image2raw','-i2r']
img_type = ['.png','.jpg','.jpeg','.gif','.jfif','.bmp','.tiff','.tif','.ico','.icon','.webp','jp2','j2k']

try:
    image = argv[1]
    flag = argv[2]
except:
    flag = None

try:
    show_flag = argv[3]
except:
    show_flag = False

if '"' in image:
    image = image.replace('"','')

if "\\" in image:
    image = image.replace("\\","/")

if show_flag in show_false:
    show_flag = False
elif show_flag in show_true:
    show_flag = True
else:
    show_flag = False

if raw_type in image:
    with open(image,'rb+') as of:
        of.seek(0x0C)
        width_b = of.read(0x04)
        of.seek(0x10)
        height_b = of.read(0x04)
    
        width = int.from_bytes(width_b, byteorder='little')
        height = int.from_bytes(height_b, byteorder='little')
        print(f"\nImage Demesions: {width}x{height}\n")
        of.close()
    
    if flag in raw_list:
        convert_etc2_2_img(image,width,height,show_flag)
    elif flag == None:
        print(f"\nFlag Provided: '{flag}' isn't recognized.\n")
    else:
        print(f"\nFlag Provided: '{flag}' isn't recognized.\n")
    
extension = os.path.splitext(image)[1]
if extension in img_type:
    if flag in img_list:
        width,height = get_demesions(image)
        width = width.to_bytes(4, byteorder='little')
        height = height.to_bytes(4, byteorder='little')
        etc2_data,outname = convert_img_2_etc2(image)

        with open(outname,'wb+') as f:
            f.write(b'3DST\x03\x00\x00\x00\x00\x00\x00\x00'),f.write(width),f.write(height),f.write(width),f.write(height),f.write(b'\x01\x00\x00\x00')
            f.write(etc2_data)
    elif flag == None:
        print(f"\nFlag Provided: '{flag}' isn't recognized.\n")
    else:
        print(f"\nFlag Provided: '{flag}' isn't recognized.\n")