import pygame
import keyboard
import sys
import win32gui
import win32con
import win32api
import py2exe
# تهيئة pygame
pygame.init()

# حجم النافذة المنبثقة
window_width = 150
window_height = 80

# إعدادات الشاشة
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# موقع النافذة في أعلى يمين الشاشة
window_x = screen_width - window_width - 10
window_y = 10

# إنشاء نافذة صغيرة
screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
screen.fill((0, 0, 0))
screen.set_colorkey((0, 0, 0))  # جعل اللون الأسود شفافًا
pygame.display.set_caption("Overlay")

# جعل النافذة دائمًا في المقدمة وشفافة (Windows فقط)
hwnd = pygame.display.get_wm_info()["window"]

# جعل النافذة شفافة
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                     win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                     win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# تثبيت النافذة في المقدمة
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, window_x, window_y, window_width, window_height, 
                     win32con.SWP_NOACTIVATE)

# الخطوط والألوان
font = pygame.font.SysFont("Arial", 18, bold=True)
active_color = (0, 255, 0)  # أخضر للحالة النشطة

# حالة الميزات
killaura_active = False
scaffold_active = False

# الدالة الرئيسية
running = True
while running:
    # معالجة الأحداث
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # التحقق من ضغط المفاتيح
    if keyboard.is_pressed('f') and not keyboard.is_pressed('ctrl'):
        # انتظر حتى يتم تحرير المفتاح لتجنب التكرار
        while keyboard.is_pressed('f'):
            pass
        killaura_active = not killaura_active
    
    if keyboard.is_pressed('ctrl'):
        # انتظر حتى يتم تحرير المفتاح لتجنب التكرار
        while keyboard.is_pressed('ctrl'):
            pass
        scaffold_active = not scaffold_active
    
    # مسح الشاشة
    screen.fill((0, 0, 0))
    
    # رسم النص - فقط للخصائص النشطة
    y_position = 10
    
    # عرض KillAura فقط إذا كانت نشطة
    if killaura_active:
        killaura_surface = font.render("KillAura", True, active_color)
        screen.blit(killaura_surface, (10, y_position))
        y_position += 25
    
    # عرض Scaffold فقط إذا كانت نشطة
    if scaffold_active:
        scaffold_surface = font.render("Scaffold", True, active_color)
        screen.blit(scaffold_surface, (10, y_position))
    
    # تحديث الشاشة
    pygame.display.update()
    
    # إعادة تثبيت النافذة في مكانها (في حالة تم تحريكها)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, window_x, window_y, window_width, window_height, 
                         win32con.SWP_NOACTIVATE)
    
    # التحكم في معدل التحديث
    pygame.time.delay(10)

# إنهاء البرنامج
pygame.quit()
sys.exit()