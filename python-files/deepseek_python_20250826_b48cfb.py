import xlwings as xw
import math
from datetime import datetime, timedelta

# មុខងារបំលែងកាលបរិច្ឆេទសុរិយគតិទៅចន្ទគតិ
def solar_to_lunar(solar_date):
    # ក្បួនគណនាប្រហាក់ប្រហែលសម្រាប់បំលែងសុរិយគតិទៅចន្ទគតិ
    # ក្នុងការអនុវត្តជាក់ស្តែង អ្នកគួរប្រើហ្វើងចែន external ដូចជា convertdate
    # នេះគ្រាន់តែជាឧទាហរណ៍ប៉ុណ្ណោះ
    
    # កំណត់ថ្ងៃដើមគិតពី 1900-01-31 (ថ្ងៃចន្ទគតិ)
    base_lunar_date = datetime(1900, 1, 31)
    solar_date = datetime.strptime(solar_date, "%Y-%m-%d")
    
    # គណនាភាពខុសគ្នារវាងកាលបរិច្ឆេទ
    delta_days = (solar_date - base_lunar_date).days
    
    # គណនាខែចន្ទគតិ (ខែចន្ទគតិមានប្រហែល 29.53 ថ្ងៃ)
    lunar_months = delta_days / 29.53
    lunar_month = int(lunar_months % 12) + 1
    
    # គណនាថ្ងៃចន្ទគតិ
    lunar_day = int((lunar_months - int(lunar_months)) * 29.53) + 1
    
    # គណនាឆ្នាំចន្ទគតិ
    lunar_year = 1900 + int(delta_days / (29.53 * 12))
    
    return f"{lunar_year}-{lunar_month:02d}-{lunar_day:02d}"

# មុខងារបំលែងកាលបរិច្ឆេទចន្ទគតិទៅសុរិយគតិ
def lunar_to_solar(lunar_date):
    # ក្បួនគណនាប្រហាក់ប្រហែលសម្រាប់បំលែងចន្ទគតិទៅសុរិយគតិ
    # នេះគ្រាន់តែជាឧទាហរណ៍ប៉ុណ្ណោះ
    
    lunar_year, lunar_month, lunar_day = map(int, lunar_date.split('-'))
    
    # កំណត់ថ្ងៃដើមគិតពី 1900-01-31 (ថ្ងៃចន្ទគតិ)
    base_lunar_date = datetime(1900, 1, 31)
    
    # គណនាចំនួនខែចន្ទគតិចាប់តាំងពីឆ្នាំ 1900
    total_lunar_months = (lunar_year - 1900) * 12 + (lunar_month - 1)
    
    # បម្លែងខែចន្ទគតិទៅជាថ្ងៃសុរិយគតិ
    solar_date = base_lunar_date + timedelta(days=total_lunar_months * 29.53 + (lunar_day - 1))
    
    return solar_date.strftime("%Y-%m-%d")

# មុខងារដើម្បីបង្ហាញ dialog សម្រាប់ជ្រើសរើសកាលបរិច្ឆេទ
def show_date_dialog():
    try:
        import tkinter as tk
        from tkinter import simpledialog
        
        root = tk.Tk()
        root.withdraw()  # លាក់ window មេ
        
        # សួរអ្នកប្រើប្រាស់ថាតើចង់បញ្ចូលកាលបរិច្ឆេទអ្វី
        choice = simpledialog.askstring("ជម្រើស", "សូមជ្រើសរើស:\n1. សុរិយគតិទៅចន្ទគតិ\n2. ចន្ទគតិទៅសុរិយគតិ")
        
        if choice == '1':
            date_str = simpledialog.askstring("សុរិយគតិ", "សូមបញ្ចូលកាលបរិច្ឆេទសុរិយគតិ (YYYY-MM-DD):")
            if date_str:
                lunar_date = solar_to_lunar(date_str)
                return lunar_date
        elif choice == '2':
            date_str = simpledialog.askstring("ចន្ទគតិ", "សូមបញ្ចូលកាលបរិច្ឆេទចន្ទគតិ (YYYY-MM-DD):")
            if date_str:
                solar_date = lunar_to_solar(date_str)
                return solar_date
        else:
            return None
    except ImportError:
        # ប្រសិនបើ tkinter មិនមាន ប្រើ input ពី console
        choice = input("សូមជ្រើសរើស:\n1. សុរិយគតិទៅចន្ទគតិ\n2. ចន្ទគតិទៅសុរិយគតិ\nជម្រើសរបស់អ្នក: ")
        
        if choice == '1':
            date_str = input("សូមបញ្ចូលកាលបរិច្ឆេទសុរិយគតិ (YYYY-MM-DD): ")
            lunar_date = solar_to_lunar(date_str)
            return lunar_date
        elif choice == '2':
            date_str = input("សូមបញ្ចូលកាលបរិច្ឆេទចន្ទគតិ (YYYY-MM-DD): ")
            solar_date = lunar_to_solar(date_str)
            return solar_date
        else:
            return None

# មុខងារចម្បងដែល Excel នឹងហៅ
@xw.func
def convert_date():
    """បម្លែងកាលបរិច្ឆេទរវាងសុរិយគតិនិងចន្ទគតិ"""
    result = show_date_dialog()
    if result:
        return result
    else:
        return "មិនមានកាលបរិច្ឆេទត្រូវបានជ្រើសរើស"

# មុខងារសម្រាប់បម្លែងកាលបរិច្ឆេទដោយផ្ទាល់
@xw.func
def solar_to_lunar_date(solar_date):
    """បម្លែងកាលបរិច្ឆេទសុរិយគតិទៅចន្ទគតិ"""
    try:
        if isinstance(solar_date, datetime):
            solar_str = solar_date.strftime("%Y-%m-%d")
        else:
            solar_str = str(solar_date)
        return solar_to_lunar(solar_str)
    except:
        return "កាលបរិច្ឆេទមិនត្រឹមត្រូវ"

@xw.func
def lunar_to_solar_date(lunar_date):
    """បម្លែងកាលបរិច្ឆេទចន្ទគតិទៅសុរិយគតិ"""
    try:
        if isinstance(lunar_date, datetime):
            lunar_str = lunar_date.strftime("%Y-%m-%d")
        else:
            lunar_str = str(lunar_date)
        return lunar_to_solar(lunar_str)
    except:
        return "កាលបរិច្ឆេទមិនត្រឹមត្រូវ"

if __name__ == "__main__":
    # ភ្ជាប់កម្មវិធីជាមួយ Excel
    xw.serve()