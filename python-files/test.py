from PIL import Image

def is_near_black(r, g, b, threshold=0.95):
    """Trả về True nếu màu gần như đen (dưới 5% độ sáng)"""
    brightness = (r + g + b) / 3 / 255
    return brightness < (1 - threshold)

def convert_black_to_transparent(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        r, g, b, a = item
        if is_near_black(r, g, b):
            new_data.append((r, g, b, 0))  # Transparent
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    img.save(output_path)
    print(f"Đã lưu ảnh mới vào: {output_path}")

# Ví dụ sử dụng:
if __name__ == "__main__":
    input_image = "input.png"
    output_image = "output.png"
    convert_black_to_transparent(input_image, output_image)
