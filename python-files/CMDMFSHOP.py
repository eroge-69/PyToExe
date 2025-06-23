import os
import subprocess
import sys
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, messagebox

# โฟลเดอร์รูปภาพ (แก้ไขตามที่อยู่ของคุณ)
ASSETS_PATH = Path(r"C:\Users\andre\Downloads\.img")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def run_pk():
    # เรียกใช้ไฟล์ pk_all_in_one.cmd
    try:
        subprocess.call("pk_all_in_one.cmd", shell=True)
        messagebox.showinfo("Success", "ตั้งค่า PK สำเร็จ!\nกรุณารีเครื่อง 1 ครั้งก่อนเล่น")
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")

def run_pk1():
    # เรียกใช้ไฟล์ pk1_all_in_one.cmd
    try:
        subprocess.call("pk1_all_in_one.cmd", shell=True)
        messagebox.showinfo("Success", "ตั้งค่า PK1 (Boost FPS) สำเร็จ!\nกรุณารีเครื่อง 1 ครั้งก่อนเล่น")
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")

def exit_app():
    sys.exit()

def main():
    window = Tk()
    window.title("MF Shop GUI - PK & PK1 Booster")
    window.geometry("802x397")
    window.resizable(False, False)
    window.configure(bg="#FFFFFF")

    canvas = Canvas(window, bg="#FFFFFF", height=900, width=900, highlightthickness=0)
    canvas.place(x=0, y=0)

    try:
        # ภาพพื้นหลัง
        image_image_1 = PhotoImage(file=relative_to_assets("kinfe 1.png"))
        canvas.create_image(401.0, 200.0, image=image_image_1)

        # ปุ่ม PK
        button_image_1 = PhotoImage(file=relative_to_assets("PK.png"))
        Button(image=button_image_1, command=run_pk, borderwidth=0).place(x=614, y=222, width=189, height=43)

        # ปุ่ม PK1
        button_image_2 = PhotoImage(file=relative_to_assets("PK1.png"))
        Button(image=button_image_2, command=run_pk1, borderwidth=0).place(x=614, y=278, width=189, height=44)

        # ปุ่ม Exit
        button_image_3 = PhotoImage(file=relative_to_assets("exit.png"))
        Button(image=button_image_3, command=exit_app, borderwidth=0).place(x=756, y=10)

    except Exception as e:
        messagebox.showerror("Image Load Error", str(e))
        sys.exit()

    window.mainloop()

if __name__ == "__main__":
    main()
