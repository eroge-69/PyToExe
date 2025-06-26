
import os
import hashlib
import uuid
from tkinter import Tk, Label, Button, filedialog, messagebox

APP_NAME = "Scanner Auto 29"
LICENSE_FILE = "license.key"

# القيم المستهدفة حسب نوع السيارة
TARGET_VALUES = {
    "1.2 16V": "6E05",
    "1.6 MPI": "3C05"
}

# القيم الممكنة لتعديل الحرارة
ALLOWED_TEMPS = {
    88: "5805",
    89: "5905",
    90: "5A05",
    91: "5B05",
    92: "5C05",
    93: "5D05",
    94: "5E05",
    95: "5F05"
}

def get_hardware_id():
    return str(uuid.getnode())

def generate_license_key(hardware_id):
    return hashlib.sha256(hardware_id.encode()).hexdigest()[:16].upper()

def is_activated():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            saved_key = f.read().strip()
        return saved_key == generate_license_key(get_hardware_id())
    return False

def save_license_key(key):
    with open(LICENSE_FILE, "w") as f:
        f.write(key)

def activate():
    from tkinter.simpledialog import askstring
    hwid = get_hardware_id()
    expected_key = generate_license_key(hwid)
    user_key = askstring(APP_NAME, f"أدخل مفتاح التفعيل لجهازك\n(HWID: {hwid})")
    if user_key and user_key.strip().upper() == expected_key:
        save_license_key(expected_key)
        messagebox.showinfo(APP_NAME, "تم التفعيل بنجاح ✅")
        return True
    else:
        messagebox.showerror(APP_NAME, "مفتاح التفعيل غير صحيح ❌")
        return False

class FanTempEditor:
    def __init__(self, master):
        self.master = master
        master.title(f"{APP_NAME} - تعديل حرارة المروحة")

        self.label = Label(master, text="اختر نوع السيارة ثم درجة الحرارة الجديدة")
        self.label.pack()

        self.file_path = ""
        self.selected_car = None
        self.selected_temp = None

        Button(master, text="1.2 16V", command=lambda: self.select_car("1.2 16V")).pack()
        Button(master, text="1.6 MPI", command=lambda: self.select_car("1.6 MPI")).pack()

        for temp in sorted(ALLOWED_TEMPS.keys()):
            Button(master, text=f"{temp}°C", command=lambda t=temp: self.select_temp(t)).pack()

        Button(master, text="اختيار ملف السيارة", command=self.select_file).pack()
        Button(master, text="حفظ الملف المعدل", command=self.save_file).pack()

    def select_car(self, car_type):
        self.selected_car = car_type
        messagebox.showinfo(APP_NAME, f"تم اختيار: {car_type}")

    def select_temp(self, temp):
        self.selected_temp = temp
        messagebox.showinfo(APP_NAME, f"تم اختيار: {temp}°C")

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            messagebox.showinfo(APP_NAME, f"المسار: {self.file_path}")

    def save_file(self):
        if not self.file_path or not self.selected_car or self.selected_temp is None:
            messagebox.showerror(APP_NAME, "يرجى اختيار الملف، نوع السيارة ودرجة الحرارة أولاً")
            return

        target_value = TARGET_VALUES[self.selected_car]
        new_value = ALLOWED_TEMPS[self.selected_temp]

        with open(self.file_path, "rb") as f:
            content = f.read()

        if target_value.encode() not in content:
            messagebox.showerror(APP_NAME, "لم يتم العثور على القيمة الأصلية في الملف")
            return

        modified_content = content.replace(target_value.encode(), new_value.encode())

        save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
        if save_path:
            with open(save_path, "wb") as f:
                f.write(modified_content)
            messagebox.showinfo(APP_NAME, "تم تعديل الملف بنجاح ✅")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    if is_activated() or activate():
        root.deiconify()
        app = FanTempEditor(root)
        root.mainloop()
    else:
        root.destroy()
