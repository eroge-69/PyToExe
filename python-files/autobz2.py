Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import bz2
import sys

def convert_to_bz2(input_file):
    """
    تبدیل ساده یک فایل به فرمت BZ2
    """
    output_file = input_file + '.bz2'
    
    with open(input_file, 'rb') as f_in:
        with bz2.open(output_file, 'wb') as f_out:
            f_out.write(f_in.read())
    
    print(f'تغییر فرمت انجام شد: {output_file}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('لطفا آدرس فایل را وارد کنید')
        print('مثال: python convert.py file.txt')
    else:
        convert_to_bz2(sys.argv[1])