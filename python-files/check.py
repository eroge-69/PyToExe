 

import pyautogui
import time

import pydirectinput
import tkinter as tk
from threading import Thread
import os, sys

X0, Y0 = 960, 490
X1, Y1 = 970, 491
X2, Y2 = 978, 493
X3, Y3 = 986, 497
X4, Y4 = 993, 502
X5, Y5 = 1000, 510
X6, Y6 = 1005, 519
X7, Y7 = 1009, 529
X8, Y8 = 1010, 539
X9, Y9 = 1009, 550
X10, Y10 = 1005, 560
X11, Y11 = 1001, 568
X12, Y12 = 995, 575
X13, Y13 = 988, 581
X14, Y14 = 979, 586
X15, Y15 = 969, 589
X16, Y16 = 959, 589
X17, Y17 = 950, 588
X18, Y18 = 941, 586
X19, Y19 = 933, 582
X20, Y20 = 924, 575
X21, Y21 = 918, 567
X22, Y22 = 914, 560
X23, Y23 = 911, 551
X24, Y24 = 910, 539
X25, Y25 = 911, 530
X26, Y26 = 913, 521
X27, Y27 = 918, 512
X28, Y28 = 923, 506
X29, Y29 = 930, 499
X30, Y30 = 939, 494
X31, Y31 = 949, 491

# Màu mục tiêu ở định dạng RGB (R, G, B)
TARGET_COLOR = (25, 113, 194)


def check_pixel0(x0, y0): return pyautogui.pixel(x0, y0)
def check_pixel1(x1, y1): return pyautogui.pixel(x1, y1)
def check_pixel2(x2, y2): return pyautogui.pixel(x2, y2)
def check_pixel3(x3, y3): return pyautogui.pixel(x3, y3)
def check_pixel4(x4, y4): return pyautogui.pixel(x4, y4)
def check_pixel5(x5, y5): return pyautogui.pixel(x5, y5)
def check_pixel6(x6, y6): return pyautogui.pixel(x6, y6)
def check_pixel7(x7, y7): return pyautogui.pixel(x7, y7)
def check_pixel8(x8, y8): return pyautogui.pixel(x8, y8)
def check_pixel9(x9, y9): return pyautogui.pixel(x9, y9)
def check_pixel10(x10, y10): return pyautogui.pixel(x10, y10)
def check_pixel11(x11, y11): return pyautogui.pixel(x11, y11)
def check_pixel12(x12, y12): return pyautogui.pixel(x12, y12)
def check_pixel13(x13, y13): return pyautogui.pixel(x13, y13)
def check_pixel14(x14, y14): return pyautogui.pixel(x14, y14)
def check_pixel15(x15, y15): return pyautogui.pixel(x15, y15)
def check_pixel16(x16, y16): return pyautogui.pixel(x16, y16)
def check_pixel17(x17, y17): return pyautogui.pixel(x17, y17)
def check_pixel18(x18, y18): return pyautogui.pixel(x18, y18)
def check_pixel19(x19, y19): return pyautogui.pixel(x19, y19)
def check_pixel20(x20, y20): return pyautogui.pixel(x20, y20)
def check_pixel21(x21, y21): return pyautogui.pixel(x21, y21)
def check_pixel22(x22, y22): return pyautogui.pixel(x22, y22)
def check_pixel23(x23, y23): return pyautogui.pixel(x23, y23)
def check_pixel24(x24, y24): return pyautogui.pixel(x24, y24)
def check_pixel25(x25, y25): return pyautogui.pixel(x25, y25)
def check_pixel26(x26, y26): return pyautogui.pixel(x26, y26)
def check_pixel27(x27, y27): return pyautogui.pixel(x27, y27)
def check_pixel28(x28, y28): return pyautogui.pixel(x28, y28)
def check_pixel29(x29, y29): return pyautogui.pixel(x29, y29)
def check_pixel30(x30, y30): return pyautogui.pixel(x30, y30)
def check_pixel31(x31, y31): return pyautogui.pixel(x31, y31)

def script_logic(paused_var):
    print("Script logic started.")


    while not paused_var.get():
        if paused_var.get(): # Nếu đang tạm dừng, đợi
                    time.sleep(0.1)
                    continue # Quay lại đầu vòng lặp để kiểm tra lại trạng thái
        count = 0
        pydirectinput.press('4')
        time.sleep(6)
        while not paused_var.get():      

            if paused_var.get(): # Nếu đang tạm dừng, đợi
                    time.sleep(0.1)
                    continue # Quay lại đầu vòng lặp để kiểm tra lại trạng thái
            
            # Đọc màu 
            pixel0 = check_pixel0(X0, Y0)
            
            if pixel0 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel0 = check_pixel0(X0, Y0)

                    if pixel0 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1

                        break
            if count >= 4:
                print("next")
                time.sleep(0.1)
                break
            pixel1 = check_pixel1(X1, Y1)
            
            if pixel1 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel1 = check_pixel1(X1, Y1)

                    if pixel1 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break

            pixel2 = check_pixel2(X2, Y2)
            
            if pixel2 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel2 = check_pixel2(X2, Y2)

                    if pixel2 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break

            pixel3 = check_pixel3(X3, Y3)
            
            if pixel3 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel3 = check_pixel3(X3, Y3)

                    if pixel3 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break


            pixel4 = check_pixel4(X4, Y4)
            if pixel4 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel4 = check_pixel4(X4, Y4)

                    if pixel4 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break

            pixel5 = check_pixel5(X5, Y5)
            if pixel5 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel5 = check_pixel5(X5, Y5)

                    if pixel5 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel6 = check_pixel6(X6, Y6)
            if pixel6 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel6 = check_pixel6(X6, Y6)

                    if pixel6 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel7 = check_pixel7(X7, Y7)
            if pixel7 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel7 = check_pixel7(X7, Y7)

                    if pixel7 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel8 = check_pixel8(X8, Y8)
            if pixel8 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel8 = check_pixel8(X8, Y8)

                    if pixel8 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel9 = check_pixel9(X9, Y9)
            if pixel9 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel9 = check_pixel9(X9, Y9)

                    if pixel9 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            
            pixel10 = check_pixel10(X10, Y10)
            if pixel10 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel10 = check_pixel10(X10, Y10)

                    if pixel10 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            if count >= 4:
                print("next")
                time.sleep(0.1)
                break
            pixel11 = check_pixel11(X11, Y11)
            if pixel11 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel11 = check_pixel11(X11, Y11)

                    if pixel11 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel12 = check_pixel12(X12, Y12)
            if pixel12 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel12 = check_pixel12(X12, Y12)

                    if pixel12 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel13 = check_pixel13(X13, Y13)
            if pixel13 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel13 = check_pixel13(X13, Y13)

                    if pixel13 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel14 = check_pixel14(X14, Y14)
            if pixel14 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel14 = check_pixel14(X14, Y14)

                    if pixel14 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel15 = check_pixel15(X15, Y15)
            if pixel15 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel15 = check_pixel15(X15, Y15)

                    if pixel15 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel16 = check_pixel16(X16, Y16)
            if pixel16 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel16 = check_pixel16(X16, Y16)

                    if pixel16 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel17 = check_pixel17(X17, Y17)
            if pixel17 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel17 = check_pixel17(X17, Y17)

                    if pixel17 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel18 = check_pixel18(X18, Y18)
            if pixel18 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel18 = check_pixel18(X18, Y18)

                    if pixel18 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel19 = check_pixel19(X19, Y19)
            
            if pixel19 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel19 = check_pixel19(X19, Y19)

                    if pixel19 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            
            pixel20 = check_pixel20(X20, Y20)
            if pixel20 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel20 = check_pixel20(X20, Y20)

                    if pixel20 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            if count >= 4:
                print("next")
                time.sleep(0.1)
                break
            pixel21 = check_pixel21(X21, Y21)
            if pixel21 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel21 = check_pixel21(X21, Y21)

                    if pixel21 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel22 = check_pixel22(X22, Y22)
            if pixel22 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel22 = check_pixel22(X22, Y22)

                    if pixel22 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel23 = check_pixel23(X23, Y23)
            if pixel23 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel23 = check_pixel23(X23, Y23)

                    if pixel23 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel24 = check_pixel24(X24, Y24)
            
            if pixel24 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel24 = check_pixel24(X24, Y24)

                    if pixel24 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel25 = check_pixel25(X25, Y25)
            if pixel25 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel25 = check_pixel25(X25, Y25)

                    if pixel25 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel26 = check_pixel26(X26, Y26)
            if pixel26 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel26 = check_pixel26(X26, Y26)

                    if pixel26 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel27 = check_pixel27(X27, Y27)
            if pixel27 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel27 = check_pixel27(X27, Y27)

                    if pixel27 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel28 = check_pixel28(X28, Y28)
            
            if pixel28 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel28 = check_pixel28(X28, Y28)

                    if pixel28 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel29 = check_pixel29(X29, Y29)
            if pixel29 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel29 = check_pixel29(X29, Y29)

                    if pixel29 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            
            pixel30 = check_pixel30(X30, Y30)
            if pixel30 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel30 = check_pixel30(X30, Y30)

                    if pixel30 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            pixel31 = check_pixel31(X31, Y31)
            if pixel31 == TARGET_COLOR:
                print("→ MÀU KHỚP!")

                while not paused_var.get():
                    pixel31 = check_pixel31(X31, Y31)

                    if pixel31 != TARGET_COLOR:
                        print("trigger")
                        # Thực hiện hành động tại đây
                        pydirectinput.press('e')
                        time.sleep(0.01)
                        count += 1
                        break
            time.sleep(0.05)
            if count >= 4:
                print("next")
                time.sleep(0.1)
                break        
        
        


def create_ui():
    root = tk.Tk()
    root.title("Điều khiển Tool")
    root.geometry("350x200") # Kích thước cửa sổ

    # Biến boolean để theo dõi trạng thái tạm dừng
    paused_var = tk.BooleanVar(value=False)

    def reset_script():
        print("Script RESET.")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    # Hàm khi nhấn nút "Tạm dừng"
    def pause_script():
        paused_var.set(True)
        status_label.config(text="Trạng thái Tool: Tạm dừng", fg="red")
        print("Script PAUSED.")

    # Hàm khi nhấn nút "Tiếp tục"
    def resume_script():
        paused_var.set(False)
        status_label.config(text="Trạng thái Tool: Đang chạy", fg="green")
        print("Script RESUMED.")

    # Tạo nhãn hiển thị trạng thái
    status_label = tk.Label(root, text="Trạng thái Tool: Đang chạy", fg="green", font=("Helvetica", 12))
    status_label.pack(pady=10)
    reset_button = tk.Button(root, text="Reset", command=reset_script, bg="orange", width=22, height=1)
    reset_button.pack(pady=5)
    # Tạo nút "Tạm dừng"
    pause_button = tk.Button(root, text="Tạm dừng", command=pause_script, width=10, height=2)
    pause_button.pack(side=tk.LEFT, padx=10)

    # Tạo nút "Tiếp tục"
    # resume_button = tk.Button(root, text="Tiếp tục", command=resume_script, width=10, height=2)
    # resume_button.pack(side=tk.RIGHT, padx=10)

    # Khởi động logic chính của script trong một luồng riêng
    # Truyền paused_var vào để luồng có thể kiểm tra trạng thái
    script_thread = Thread(target=script_logic, args=(paused_var,))
    script_thread.daemon = True # Đặt luồng là daemon để nó tự động tắt khi chương trình chính thoát
    script_thread.start()

    # Chạy vòng lặp sự kiện Tkinter
    root.mainloop()

# Gọi hàm để tạo và chạy giao diện người dùng
if __name__ == "__main__":
    create_ui()
        