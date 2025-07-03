from PIL import Image
import math

# define the corresponding path of the image
image_path = input("Please input the path of the image:")
image_name = input("Please input the generated name:")

# define the resized size
resize_width = int(input("Please input the resized width:"))
resize_height = int(input("Please input the resized height:"))

# Define a threshold value for black & white
threshold = 128

# reverse = False
# reverse = True
reverse = int(input("Please input whether the image are reversed (1 for yes, 0 for no): "))

try:
    img = Image.open(image_path)
    print("Image loaded successfully!")
    print("Image format:", img.format)
    print("Image size:", img.size)
    print("Image mode:", img.mode)

    img = img.resize((resize_width, resize_height))

    # Convert to grayscale
    img = img.convert("L")

    print("============================")
    print("modified Image size:", img.size)

    if reverse:
        pixel = [0 if i > threshold else 1 for i in list(img.getdata())]
    else:
        pixel = [1 if i > threshold else 0 for i in list(img.getdata())]

    print("============================")
    print(f"printing image {image_name}:")
    for p in range(len(pixel)):
        if pixel[p]: print("1", end="")
        else: print(" ", end="")
        if p % resize_width == resize_width-1: print()

    c_code = f"""#include <stdint.h>

#pragma section PIXEL_FLASH
volatile uint8_t {image_name}[] = """

    c_code += '{'

    for paging in range(math.ceil(resize_height / 8)):
        for x in range(resize_width):
            if x % 16 == 0: c_code += '\n'
            val = 0
            for y in range(8):
                val *= 2
                current_i = (paging * 8 + y) * resize_width + x
                if current_i >= resize_width * resize_height:
                    val += 0
                else:
                    val += pixel[current_i]
            c_code += f"\t0x{val:02X}, "
        c_code += '\n'

    c_code += '};\n#pragma section default\n'
    with open("output_picture.c", "w") as f:
        f.write(c_code)

except FileNotFoundError:
    print("Error: The specified image file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")