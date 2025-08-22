import pyautogui
import time
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

# 화면에서 마우스 클릭으로 좌표를 선택하는 함수
def get_mouse_position():
    root = tk.Tk()
    root.title("좌표 선택")
    root.geometry("400x100+500+200")
    
    label = tk.Label(root, text="클릭할 위치를 화면에서 한 번 클릭하세요.", font=("Helvetica", 12))
    label.pack(pady=20)
    
    root.attributes("-topmost", True)
    
    def on_click(event):
        global click_x, click_y
        click_x = event.x_root
        click_y = event.y_root
        messagebox.showinfo("좌표 설정 완료", f"선택된 좌표: ({click_x}, {click_y})")
        root.destroy()

    root.bind("<Button-1>", on_click)
    root.mainloop()

# 사용자로부터 대기 시간을 입력받는 함수
def get_delay_time():
    while True:
        root = tk.Tk()
        root.withdraw() # 메인 윈도우를 숨김
        delay_input = simpledialog.askstring("대기 시간 입력", 
                                             "클릭을 실행할 시간을 입력하세요.\n"
                                             "예시) 10s (초), 5m (분), 1h (시간)\n"
                                             "숫자만 입력하면 '초'로 인식합니다.")
        
        if delay_input is None: # 사용자가 취소 버튼을 누른 경우
            sys.exit()
            
        delay_input = delay_input.lower().strip()
        
        try:
            if delay_input.endswith('s'):
                return int(delay_input[:-1])
            elif delay_input.endswith('m'):
                return int(delay_input[:-1]) * 60
            elif delay_input.endswith('h'):
                return int(delay_input[:-1]) * 3600
            else:
                return int(delay_input) # 단위가 없으면 초로 가정
        except ValueError:
            messagebox.showerror("입력 오류", "잘못된 형식입니다. 다시 입력해주세요.")
            continue
            
# --- 메인 프로그램 실행 ---
try:
    print("좌표 선택을 위해 창이 나타납니다. 화면에서 클릭할 위치를 클릭하세요.")
    get_mouse_position()

    delay_seconds = get_delay_time()

    print(f"\n{delay_seconds}초 후 ({click_x}, {click_y}) 좌표를 클릭합니다.")
    print("프로그램을 종료하려면 Ctrl+C를 누르세요.")

    # 지정된 시간만큼 대기
    time.sleep(delay_seconds)

    # 마우스 커서를 지정된 좌표로 이동시키고 클릭
    pyautogui.click(click_x, click_y)

    print("클릭이 완료되었습니다.")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")
    sys.exit()

