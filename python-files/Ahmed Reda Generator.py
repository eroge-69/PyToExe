import tkinter as tk
from tkinter import messagebox, filedialog
import random
import pyperclip
import os
from datetime import datetime, timedelta

class EgyptianDataGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Ahmed Reda Generator")
        self.root.geometry("500x400")
        
        # إعداد واجهة المستخدم
        self.setup_ui()
        
        # قوائم البيانات المصرية
        self.egyptian_first_names = ["Ahmed", "Mohamed", "Mahmoud", "Ali", "Omar", 
                                    "Ibrahim", "Youssef", "Khaled", "Mustafa", "Hassan",
                                    "Layla", "Fatma", "Aya", "Mona", "Hana",
                                    "Nour", "Amal", "Samira", "Zeinab", "Dalia"]
        self.egyptian_last_names = ["Reda", "Zaki", "Hassan", "Ibrahim", "Kamal",
                                   "Mohamed", "Mahmoud", "Ali", "Osman", "Saleh",
                                   "Abdallah", "Farouk", "Wahba", "Ashraf", "Hamdy",
                                   "El-Sayed", "Naguib", "Adel", "Fawzy", "Ramzy"]
        self.egyptian_cities = ["Cairo", "Alexandria", "Giza", "Aswan", "Luxor",
                               "Port Said", "Suez", "Ismailia", "Mansoura", "Tanta",
                               "Fayoum", "Zagazig", "Damietta", "Minya", "Beni Suef",
                               "Qena", "Sohag", "Hurghada", "Sharm El-Sheikh", "Damanhur"]
        self.egyptian_streets = ["Masr Rd", "Nile St", "Tahrir Sq", "Pyramids Rd",
                                 "Corniche", "Saad Zaghloul", "Al Haram", "Ramses St",
                                 "Kasr El Nil", "Abbas El Akkad", "Makram Ebeid", "El Nozha",
                                 "El Hegaz", "El Thawra", "El Gomhoureya", "El Khalifa"]
        
        # إنشاء ملف التخزين إذا لم يكن موجوداً
        self.profile_file = "Ahmed_Reda_Profiles.txt"
        if not os.path.exists(self.profile_file):
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                f.write("Ahmed Reda Generator - Profiles Database\n\n")
    
    def setup_ui(self):
        # عنوان البرنامج
        title_label = tk.Label(self.root, text="Random Data Generator", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Nationality
        nationality_frame = tk.Frame(self.root)
        nationality_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(nationality_frame, text="Nationality", width=15, anchor="w").pack(side=tk.LEFT)
        self.nationality_entry = tk.Entry(nationality_frame)
        self.nationality_entry.insert(0, "Egypt")
        self.nationality_entry.config(state="readonly")
        self.nationality_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ID Type و ID Number
        id_frame = tk.Frame(self.root)
        id_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(id_frame, text="ID Type", width=15, anchor="w").pack(side=tk.LEFT)
        self.id_type_entry = tk.Entry(id_frame)
        self.id_type_entry.insert(0, "National ID")
        self.id_type_entry.config(state="readonly")
        self.id_type_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        id_number_frame = tk.Frame(self.root)
        id_number_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(id_number_frame, text="ID Number", width=15, anchor="w").pack(side=tk.LEFT)
        self.id_number_entry = tk.Entry(id_number_frame)
        self.id_number_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Given Name و Family Name
        given_name_frame = tk.Frame(self.root)
        given_name_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(given_name_frame, text="Given Name", width=15, anchor="w").pack(side=tk.LEFT)
        self.given_name_entry = tk.Entry(given_name_frame)
        self.given_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        family_name_frame = tk.Frame(self.root)
        family_name_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(family_name_frame, text="Family Name", width=15, anchor="w").pack(side=tk.LEFT)
        self.family_name_entry = tk.Entry(family_name_frame)
        self.family_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Address
        address_frame = tk.Frame(self.root)
        address_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(address_frame, text="Address (Street, City)", width=15, anchor="w").pack(side=tk.LEFT)
        self.address_entry = tk.Entry(address_frame)
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Date of Birth
        dob_frame = tk.Frame(self.root)
        dob_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(dob_frame, text="Date of Birth", width=15, anchor="w").pack(side=tk.LEFT)
        self.dob_entry = tk.Entry(dob_frame)
        self.dob_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Phone Number
        phone_frame = tk.Frame(self.root)
        phone_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(phone_frame, text="Phone Number", width=15, anchor="w").pack(side=tk.LEFT)
        self.phone_entry = tk.Entry(phone_frame)
        self.phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Email
        email_frame = tk.Frame(self.root)
        email_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(email_frame, text="Email", width=15, anchor="w").pack(side=tk.LEFT)
        self.email_entry = tk.Entry(email_frame)
        self.email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # أزرار التحكم
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.generate_btn = tk.Button(button_frame, text="Generate", command=self.generate_data, width=15)
        self.generate_btn.pack(side=tk.LEFT, padx=10)
        
        self.copy_btn = tk.Button(button_frame, text="Copy All", command=self.copy_all, width=15)
        self.copy_btn.pack(side=tk.LEFT, padx=10)
        
        self.save_btn = tk.Button(button_frame, text="Save", command=self.save_profile, width=15)
        self.save_btn.pack(side=tk.LEFT, padx=10)
    
    def generate_egyptian_national_id(self):
        """توليد رقم قومي مصري عشوائي"""
        # الرقم القومي المصري يتكون من 14 رقمًا
        # أول رقمين يمثلان سنة الميلاد (مثلاً 98 لسنة 1998)
        # الأرقام من 3-5 تمثل المحافظة (مثلاً 02 للقاهرة)
        # الأرقام من 6-9 تمثل تاريخ الميلاد (يوم وشهر)
        birth_date = datetime.now() - timedelta(days=random.randint(18*365, 60*365))
        year_part = birth_date.strftime("%y")
        gov_code = f"{random.randint(1, 27):02d}"
        date_part = birth_date.strftime("%d%m")
        random_part = f"{random.randint(0, 9999):04d}"
        gender_digit = str(random.randint(1, 9))
        
        national_id = f"{year_part}{gov_code}{date_part}{random_part}{gender_digit}"
        return national_id
    
    def generate_egyptian_phone(self):
        """توليد رقم هاتف مصري عشوائي"""
        prefixes = ["10", "11", "12", "15"]
        prefix = random.choice(prefixes)
        number = f"01{prefix}{random.randint(1000000, 9999999)}"
        return number
    
    def generate_email(self, first_name, last_name):
        """توليد إيميل عشوائي"""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        random_num = random.randint(1, 999)
        email = f"{first_name.lower()}.{last_name.lower()}{random_num}@{random.choice(domains)}"
        return email
    
    def generate_data(self):
        """توليد بيانات عشوائية"""
        # توليد الأسماء
        first_name = random.choice(self.egyptian_first_names)
        last_name = random.choice(self.egyptian_last_names)
        
        # توليد تاريخ الميلاد
        birth_date = datetime.now() - timedelta(days=random.randint(18*365, 60*365))
        formatted_date = birth_date.strftime("%d/%m/%Y")
        
        # توليد العنوان
        street = random.choice(self.egyptian_streets)
        city = random.choice(self.egyptian_cities)
        address = f"{street}, {city}"
        
        # توليد باقي البيانات
        national_id = self.generate_egyptian_national_id()
        phone = self.generate_egyptian_phone()
        email = self.generate_email(first_name, last_name)
        
        # تعبئة الحقول
        self.given_name_entry.delete(0, tk.END)
        self.given_name_entry.insert(0, first_name)
        
        self.family_name_entry.delete(0, tk.END)
        self.family_name_entry.insert(0, last_name)
        
        self.id_number_entry.delete(0, tk.END)
        self.id_number_entry.insert(0, national_id)
        
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, address)
        
        self.dob_entry.delete(0, tk.END)
        self.dob_entry.insert(0, formatted_date)
        
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, phone)
        
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, email)
        
        # الحفظ التلقائي
        self.save_profile()
    
    def copy_all(self):
        """نسخ جميع البيانات"""
        data = f"""Nationality: {self.nationality_entry.get()}
ID Type: {self.id_type_entry.get()}
ID Number: {self.id_number_entry.get()}
Given Name: {self.given_name_entry.get()}
Family Name: {self.family_name_entry.get()}
Address: {self.address_entry.get()}
Date of Birth: {self.dob_entry.get()}
Phone Number: {self.phone_entry.get()}
Email: {self.email_entry.get()}"""
        
        pyperclip.copy(data)
        messagebox.showinfo("Copied", "All data has been copied to clipboard!")
    
    def save_profile(self):
        """حفظ البيانات في ملف"""
        data = f"""\n=== Profile - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ===
Nationality: {self.nationality_entry.get()}
ID Type: {self.id_type_entry.get()}
ID Number: {self.id_number_entry.get()}
Given Name: {self.given_name_entry.get()}
Family Name: {self.family_name_entry.get()}
Address: {self.address_entry.get()}
Date of Birth: {self.dob_entry.get()}
Phone Number: {self.phone_entry.get()}
Email: {self.email_entry.get()}\n"""
        
        with open(self.profile_file, 'a', encoding='utf-8') as f:
            f.write(data)
        
        # messagebox.showinfo("Saved", "Profile has been saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = EgyptianDataGenerator(root)
    root.mainloop()