import os
import shutil
import json

# مسار ملفات اللعبة
game_directory = "C:/path_to_RE4_game_files/"
room_file_path = os.path.join(game_directory, "rooms", "room_01.pak")

# مسار المخرجات للغرفة المنسوخة
output_directory = "C:/path_to_output/"

def load_room_data(file_path):
    """تحميل بيانات الغرفة من الملف (بصيغة JSON كمثال)."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            room_data = json.load(file)  # يمكنك تعديل هذا بناءً على تنسيق البيانات الفعلي
        return room_data
    else:
        print(f"لم يتم العثور على الملف: {file_path}")
        return None

def copy_room_data(room_data):
    """نسخ بيانات الغرفة، مع تغيير المعرف والاسم."""
    copied_room = room_data.copy()
    copied_room['id'] += 1  # تغيير المعرف ليكون فريدًا
    copied_room['name'] = copied_room['name'] + "_copy"  # تغيير اسم الغرفة
    # نسخ الكائنات (إذا كانت موجودة)
    copied_room['objects'] = copied_room['objects'][:]
    
    return copied_room

def save_room_data(copied_room, output_path):
    """حفظ بيانات الغرفة المنسوخة في ملف جديد."""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = os.path.join(output_path, f"{copied_room['name']}.json")
    
    with open(output_file, 'w') as file:
        json.dump(copied_room, file, indent=4)
    
    print(f"تم حفظ الغرفة المنسوخة في: {output_file}")

def main():
    # تحميل بيانات الغرفة من الملف
    room_data = load_room_data(room_file_path)
    
    if room_data:
        # نسخ بيانات الغرفة
        copied_room = copy_room_data(room_data)
        
        # حفظ البيانات المنسوخة
        save_room_data(copied_room, output_directory)

if __name__ == "__main__":
    main()
