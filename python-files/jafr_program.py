# -*- coding: utf-8 -*-
import random

# جدول ابجد فارسی
abjad = {
    'ا':1,'ب':2,'پ':3,'ت':400,'ث':500,'ج':3,'چ':3,'ح':8,'خ':600,
    'د':4,'ذ':700,'ر':200,'ز':7,'ژ':700,'س':60,'ش':300,'ص':90,'ض':800,
    'ط':9,'ظ':900,'ع':70,'غ':1000,'ف':80,'ق':100,'ک':20,'گ':3,'ل':30,
    'م':40,'ن':50,'و':6,'ه':5,'ی':10
}

# جدول نگاشت عدد -> حرف
num_to_char = {
    1:'م',2:'ه',3:'ر',4:'ب',5:'ا',6:'ن',7:'و',8:'س',9:'ت',10:'ی',
    11:'ک',12:'ل',13:'د',14:'ف',15:'ق',16:'ط',17:'ظ',18:'ش',19:'ج',20:'چ',
    21:'ح',22:'خ',23:'ع',24:'غ',25:'ث',26:'ذ',27:'ز',28:'ژ',29:'ص',30:'ض'
}

def text_to_abjad(text):
    """تبدیل حروف فارسی به اعداد ابجد"""
    numbers = []
    for ch in text:
        if ch in abjad:
            numbers.append(abjad[ch])
    return numbers

def build_matrix(numbers):
    """ساخت ماتریس مربعی از جمع اعداد"""
    L = len(numbers)
    matrix = []
    for i in range(L):
        row = []
        for j in range(L):
            row.append(numbers[i]+numbers[j])
        matrix.append(row)
    return matrix

def reduce_matrix(matrix, mod=30):
    """کاهش اعداد ماتریس به بازه 1 تا mod"""
    reduced = []
    for row in matrix:
        reduced_row = [((x-1)%mod)+1 for x in row]
        reduced.append(reduced_row)
    return reduced

def matrix_to_sentence(matrix):
    """تبدیل ماتریس کاهش یافته به جمله فارسی طولانی"""
    L = len(matrix)
    sentence_chars = []
    for i in range(L):
        val = sum(matrix[i]) % 30 + 1
        # الگوریتم تولید زنجیره طولانی حروف
        for j in range(i%3 +1):
            val = (val + random.randint(1,3)) % 30 +1
            sentence_chars.append(num_to_char.get(val,'ا'))
    # تقسیم حروف به کلمات 3 تا 6 حرفی
    words = []
    i = 0
    while i < len(sentence_chars):
        wlen = random.randint(3,6)
        words.append(''.join(sentence_chars[i:i+wlen]))
        i += wlen
    sentence = ' '.join(words)
    # جمله با حرف اول بزرگ و نقطه پایان
    sentence = sentence.capitalize() + '.'
    return sentence

def main():
    print("=== برنامه جفر پیشرفته ===")
    q = input("سوال خود را وارد کنید: ")
    nums = text_to_abjad(q)
    if not nums:
        print("سوال شامل حروف فارسی معتبر نیست!")
        return
    mat = build_matrix(nums)
    reduced = reduce_matrix(mat)
    output = matrix_to_sentence(reduced)
    print("\nپاسخ جفری پیشرفته:")
    print(output)

if __name__=="__main__":
    main()
