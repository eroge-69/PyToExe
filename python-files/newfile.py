import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

class Vehicle:
    def __init__(self, plate_number):
        self.plate_number = plate_number
        self.entry_time = datetime.now()

    def get_duration(self):
        return datetime.now() - self.entry_time

    def calculate_fee(self, rate_per_hour=25000):
        duration = self.get_duration()
        hours = duration.total_seconds() / 3600
        return round(hours * rate_per_hour)

class ParkingLot:
    def __init__(self, capacity):
        self.capacity = capacity
        self.vehicles = {}

    def is_full(self):
        return len(self.vehicles) >= self.capacity

    def vehicle_entry(self, plate_number):
        if self.is_full():
            return "پارکینگ پر است."
        if plate_number in self.vehicles:
            return "این خودرو قبلاً وارد شده."
        self.vehicles[plate_number] = Vehicle(plate_number)
        return f"خودروی {plate_number} وارد شد."

    def vehicle_exit(self, plate_number):
        if plate_number not in self.vehicles:
            return "این خودرو در پارکینگ نیست."
        vehicle = self.vehicles.pop(plate_number)
        duration = vehicle.get_duration()
        fee = vehicle.calculate_fee()
        return f"خودروی {plate_number} خارج شد.\nمدت زمان پارک: {str(duration).split('.')[0]}\nمبلغ قابل پرداخت: {fee:,} تومان"

    def get_vehicles_list(self):
        if not self.vehicles:
            return "هیچ خودرویی در پارکینگ نیست."
        result = "خودروهای حاضر:\n"
        for plate, vehicle in self.vehicles.items():
            duration = vehicle.get_duration()
            result += f"- {plate} | ورود: {vehicle.entry_time.strftime('%H:%M:%S')} | مدت پارک: {str(duration).split('.')[0]}\n"
        return result

class ParkingApp:
    def __init__(self, root):
        self.lot = ParkingLot(capacity=10)
        self.root = root
        self.root.title("مدیریت پارکینگ")
        self.root.geometry("300x250")

        tk.Label(root, text="سیستم مدیریت پارکینگ", font=("B Nazanin", 14, "bold")).pack(pady=10)

        tk.Button(root, text="🚗 ورود خودرو", width=25, command=self.enter_vehicle).pack(pady=5)
        tk.Button(root, text="🚙 خروج خودرو", width=25, command=self.exit_vehicle).pack(pady=5)
        tk.Button(root, text="📋 نمایش خودروها", width=25, command=self.show_vehicles).pack(pady=5)
        tk.Button(root, text="❌ خروج از برنامه", width=25, command=root.quit).pack(pady=20)

    def enter_vehicle(self):
        plate = simpledialog.askstring("ورود خودرو", "شماره پلاک را وارد کنید:")
        if plate:
            msg = self.lot.vehicle_entry(plate.strip())
            messagebox.showinfo("نتیجه", msg)

    def exit_vehicle(self):
        plate = simpledialog.askstring("خروج خودرو", "شماره پلاک را وارد کنید:")
        if plate:
            msg = self.lot.vehicle_exit(plate.strip())
            messagebox.showinfo("نتیجه", msg)

    def show_vehicles(self):
        info = self.lot.get_vehicles_list()
        messagebox.showinfo("وضعیت پارکینگ", info)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
