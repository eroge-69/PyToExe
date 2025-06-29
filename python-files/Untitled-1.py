import cv2 as cv
import numpy as np
import mss
import time
import win32api
import win32con







# Load ảnh mẫu
template_path = '1.png'
template = cv.imread(template_path)
if template is None:
    raise Exception("1w  ")

w, h = template.shape[1], template.shape[0]
template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)


x_start, x_end = 1, 1920
y_start, y_end = 858, 1080
click_step_x = 40  
click_step_y = 35  
click_offset_y = 5  
click_interval = 0  

def fast_click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def find_template(screen_img):
    screen_gray = cv.cvtColor(screen_img, cv.COLOR_BGR2GRAY)
    res = cv.matchTemplate(screen_gray, template_gray, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)
    return max_val, max_loc

last_spam_time = 0
t0 = time.time()
n_frames = 1

with mss.mss() as sct:
    monitor = sct.monitors[0]

    while True:
        img = sct.grab(monitor)
        img = np.array(img)
        img_bgr = cv.cvtColor(img, cv.COLOR_BGRA2BGR)

        max_val, max_loc = find_template(img_bgr)
        threshold = 0.6

        if max_val >= threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            current_time = time.time()
            if current_time - last_spam_time >= click_interval:
                

                for y in range(y_start, y_end, click_step_y):
                    click_y = y + click_offset_y  

                    for x in range(x_start, x_end, click_step_x):
                        fast_click(x, click_y)
                        time.sleep(0.0001)  

                  
                    screen = sct.grab(monitor)
                    screen_np = np.array(screen)
                    screen_bgr = cv.cvtColor(screen_np, cv.COLOR_BGRA2BGR)
                    check_val, _ = find_template(screen_bgr)

                    if check_val < threshold:
                        
                        break

                last_spam_time = current_time

        

        if cv.waitKey(1) == ord('q'):
            break

cv.destroyAllWindows()
