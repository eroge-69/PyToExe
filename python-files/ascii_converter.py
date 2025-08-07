import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import argparse

# کاراکترهای ASCII برای سطوح مختلف روشنایی
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100):
    """تغییر اندازه تصویر با حفظ نسبت ابعاد"""
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def grayscale_image(image):
    """تبدیل تصویر به مقیاس خاکستری"""
    return image.convert("L")

def pixels_to_ascii(image, colored=False):
    """تبدیل پیکسل‌ها به کاراکترهای ASCII"""
    pixels = image.getdata()
    ascii_str = ""
    
    if colored:
        colored_pixels = []
        for pixel in pixels:
            brightness = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
            char = ASCII_CHARS[int(brightness / 255 * (len(ASCII_CHARS) - 1))]
            ascii_str += char
            colored_pixels.append(pixel)
        return ascii_str, colored_pixels
    else:
        for pixel in pixels:
            char = ASCII_CHARS[int(pixel / 255 * (len(ASCII_CHARS) - 1))]
            ascii_str += char
        return ascii_str, None

def ascii_to_image(ascii_str, width, original_image=None, colored=False, font_size=10):
    """تبدیل متن ASCII به تصویر"""
    lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
    height = len(lines)
    
    if colored and original_image:
        img = Image.new("RGB", (width * font_size, height * font_size), "black")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        
        original_pixels = original_image.getdata()
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if y * width + x < len(original_pixels):
                    color = original_pixels[y * width + x]
                    draw.text((x * font_size, y * font_size), char, fill=color, font=font)
    else:
        img = Image.new("RGB", (width * font_size, height * font_size), "black")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                draw.text((x * font_size, y * font_size), char, fill="white", font=font)
    
    return img

def process_image(image_path, output_dir, width=100):
    """پردازش یک تصویر و ذخیره نتایج"""
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"خطا در باز کردن تصویر {image_path}: {e}")
        return
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    image = resize_image(image, width)
    gray_image = grayscale_image(image)
    
    ascii_str, _ = pixels_to_ascii(gray_image)
    
    txt_output = os.path.join(output_dir, f"{base_name}_ascii.txt")
    with open(txt_output, "w", encoding="utf-8") as f:
        f.write(ascii_str)
    
    bw_image = ascii_to_image(ascii_str, width)
    bw_output = os.path.join(output_dir, f"{base_name}_ascii_bw.png")
    bw_image.save(bw_output)
    
    ascii_str_colored, colored_pixels = pixels_to_ascii(image, colored=True)
    color_image = ascii_to_image(ascii_str_colored, width, image, colored=True)
    color_output = os.path.join(output_dir, f"{base_name}_ascii_color.png")
    color_image.save(color_output)
    
    print(f"فایل‌های خروجی برای {base_name} ذخیره شدند:")
    print(f"- متن ASCII: {txt_output}")
    print(f"- تصویر سیاه و سفید: {bw_output}")
    print(f"- تصویر رنگی: {color_output}")

def process_video(video_path, output_dir, width=100, frame_skip=5):
    """پردازش یک ویدیو و ذخیره فریم‌های ASCII"""
    try:
        cap = cv2.VideoCapture(video_path)
    except Exception as e:
        print(f"خطا در باز کردن ویدیو {video_path}: {e}")
        return
    
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_dir = os.path.join(output_dir, base_name)
    os.makedirs(video_output_dir, exist_ok=True)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"پردازش ویدیو: {base_name}")
    print(f"تعداد کل فریم‌ها: {total_frames}, نرخ فریم: {fps:.2f}")
    print(f"هر {frame_skip} فریم یک بار پردازش می‌شود")
    
    frame_count = 0
    processed_count = 0
    
    with tqdm(total=total_frames, desc="پردازش ویدیو") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                resized_image = resize_image(pil_image, width)
                gray_image = grayscale_image(resized_image)
                
                ascii_str, _ = pixels_to_ascii(gray_image)
                
                txt_output = os.path.join(video_output_dir, f"frame_{frame_count:06d}_ascii.txt")
                with open(txt_output, "w", encoding="utf-8") as f:
                    f.write(ascii_str)
                
                bw_image = ascii_to_image(ascii_str, width)
                bw_output = os.path.join(video_output_dir, f"frame_{frame_count:06d}_ascii_bw.png")
                bw_image.save(bw_output)
                
                ascii_str_colored, colored_pixels = pixels_to_ascii(resized_image, colored=True)
                color_image = ascii_to_image(ascii_str_colored, width, resized_image, colored=True)
                color_output = os.path.join(video_output_dir, f"frame_{frame_count:06d}_ascii_color.png")
                color_image.save(color_output)
                
                processed_count += 1
            
            frame_count += 1
            pbar.update(1)
    
    cap.release()
    print(f"پردازش ویدیو کامل شد. {processed_count} فریم پردازش و ذخیره شدند در: {video_output_dir}")

def main():
    parser = argparse.ArgumentParser(description="تبدیل عکس و ویدیو به ASCII Art")
    parser.add_argument("inputs", nargs="+", help="مسیر فایل‌های عکس یا ویدیو برای پردازش")
    parser.add_argument("-o", "--output", required=True, help="مسیر دایرکتوری خروجی برای ذخیره نتایج")
    parser.add_argument("-w", "--width", type=int, default=100, help="عرض خروجی ASCII (پیش‌فرض: 100)")
    parser.add_argument("-s", "--skip", type=int, default=5, help="تعداد فریم‌های ویدیو که بین هر پردازش رد می‌شوند (پیش‌فرض: 5)")
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    for input_path in args.inputs:
        if not os.path.exists(input_path):
            print(f"خطا: فایل {input_path} یافت نشد!")
            continue
        
        if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            print(f"\nپردازش تصویر: {input_path}")
            process_image(input_path, args.output, args.width)
        elif input_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            print(f"\nپردازش ویدیو: {input_path}")
            process_video(input_path, args.output, args.width, args.skip)
        else:
            print(f"خطا: فرمت فایل {input_path} پشتیبانی نمی‌شود!")

if __name__ == "__main__":
    main()