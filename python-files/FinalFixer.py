import sys
import os

# الترميزات العربية الأساسية للتجربة (مع ملاحظة أن منطق فك التشفير المزدوج هو الأهم)
ARABIC_ENCODINGS = [
    'windows-1256',  # الترميز الأرجح
    'iso-8859-6',    # الترميز الثاني
    'cp864',         # الترميز الثالث
]

def decode_and_save(input_file_path):
    
    if not os.path.exists(input_file_path):
        print(f"\n❌ خطأ: الملف غير موجود في المسار المحدد: {input_file_path}")
        return

    base, ext = os.path.splitext(input_file_path)
    output_file_path = f"{base}_FIXED{ext}"

    try:
        with open(input_file_path, 'rb') as f:
            content_bytes = f.read()
    except Exception as e:
        print(f"\n❌ خطأ في قراءة الملف: {e}")
        return

    decoded_content = None
    successful_encoding = None

    print(f"جاري محاولة فك تشفير الملف: {os.path.basename(input_file_path)}...")

    # حلقة تجربة فك التشفير المزدوج (الذي يحل المشكلة المعقدة)
    for encoding in ARABIC_ENCODINGS:
        try:
            # المنطق: اقرأ البايتات المشوهة كـ latin-1 (للحفاظ عليها)، ثم فك تشفيرها بالترميز العربي الصحيح
            decoded_content = content_bytes.decode('latin-1').encode('latin-1').decode(encoding)
            successful_encoding = encoding
            
            # تحقق سريع من وجود النص العربي
            if any('\u0600' <= char <= '\u06FF' for char in decoded_content[:100]):
                break
            else:
                 continue 

        except Exception:
            continue
    
    # حفظ النتيجة
    if decoded_content and successful_encoding:
        try:
            # حفظ الملف المصحح بترميز UTF-8 القياسي
            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(decoded_content)
            
            print(f"\n✅ نجاح! تم فك تشفير الملف باستخدام الترميز المزدوج: {successful_encoding.upper()}")
            print(f"✅ تم حفظ الملف المصحح في: {output_file_path}")
        
        except Exception as e:
            print(f"\n❌ خطأ في حفظ ملف الإخراج: {e}")
            
    else:
        print("\n❌ فشل: لم يتمكن البرنامج من فك تشفير الملف باستخدام الترميزات المتاحة.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n========================================================")
        print("  أداة فك تشفير النصوص العربية (Final Fixer)")
        print("========================================================")
        print("يرجى سحب وإسقاط الملف النصي (Text File) على أيقونة البرنامج.")
        input("\nاضغط Enter للخروج...")
        sys.exit(1)
    
    input_file = sys.argv[1]
    decode_and_save(input_file)