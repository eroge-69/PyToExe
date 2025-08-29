import os
import sys
import pygame
from PIL import Image
import ctypes
from ctypes import wintypes
import time

# Константы для блокировки клавиш
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_TAB = 0x09
VK_MENU = 0x12  # ALT key
VK_ESCAPE = 0x1B

# Глобальная переменная для хранения хука
hook_id = None

def low_level_keyboard_handler(nCode, wParam, lParam):
    if nCode >= 0:
        # Получаем информацию о нажатой клавише
        vk_code = ctypes.c_uint32(lParam[0]).value
        
        # Блокируем Win, Alt, Tab, Escape
        blocked_keys = [VK_LWIN, VK_RWIN, VK_TAB, VK_MENU, VK_ESCAPE]
        
        if vk_code in blocked_keys:
            # Блокируем все системные клавиши
            return 1
        
        if wParam in [WM_KEYDOWN, WM_SYSKEYDOWN]:
            # Проверяем комбинации
            ctrl_pressed = user32.GetAsyncKeyState(0x11) & 0x8000 != 0
            alt_pressed = user32.GetAsyncKeyState(VK_MENU) & 0x8000 != 0
            win_pressed = (user32.GetAsyncKeyState(VK_LWIN) & 0x8000 != 0 or 
                          user32.GetAsyncKeyState(VK_RWIN) & 0x8000 != 0)
            
            # Разрешаем только Ctrl+Q, все остальные комбинации блокируем
            if vk_code == 0x51:  # Q key
                if not ctrl_pressed:
                    return 1
            else:
                # Блокируем все комбинации с Alt, Win, Ctrl (кроме Ctrl+Q)
                if alt_pressed or win_pressed or ctrl_pressed:
                    return 1
    
    return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

def set_keyboard_hook():
    global hook_id
    hook_proc = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)(low_level_keyboard_handler)
    hook_id = user32.SetWindowsHookExA(WH_KEYBOARD_LL, hook_proc, kernel32.GetModuleHandleA(None), 0)
    return hook_id

def remove_keyboard_hook():
    if hook_id:
        user32.UnhookWindowsHookEx(hook_id)

def block_windows_keys():
    """Дополнительная блокировка через реестр (эмулируем игровой режим)"""
    try:
        # Пытаемся эмулировать игровой режим
        user32.BlockInput(True)
        # Скрываем панель задач
        user32.ShowWindow(user32.FindWindowA("Shell_TrayWnd", None), 0)
    except:
        pass

def unblock_windows_keys():
    """Разблокировка системных клавиш"""
    try:
        user32.BlockInput(False)
        user32.ShowWindow(user32.FindWindowA("Shell_TrayWnd", None), 1)
    except:
        pass

def show_image_fullscreen(image_file, sound_file):
    pygame.init()
    pygame.mixer.init()

    # Устанавливаем хук для блокировки клавиш
    set_keyboard_hook()
    block_windows_keys()

    # Скрываем курсор мыши
    pygame.mouse.set_visible(False)

    # Захватываем ввод мыши и клавиатуры
    pygame.event.set_grab(True)

    # Загружаем картинку
    img = Image.open(image_file)
    screen = pygame.display.set_mode(img.size, pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.display.set_caption("BSOD")

    # Конвертируем картинку в pygame
    mode = img.mode
    size = img.size
    data = img.tobytes()
    surface = pygame.image.fromstring(data, size, mode)

    # Загружаем звук
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(-1)  # бесконечный цикл

    # Основной цикл
    running = True
    last_check = time.time()
    
    while running:
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        
        # Периодически перехватываем фокус
        current_time = time.time()
        if current_time - last_check > 0.5:  # Каждые 0.5 секунды
            pygame.event.set_grab(True)  # Перезахватываем ввод
            last_check = current_time
        
        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue
            
            if event.type == pygame.KEYDOWN:
                # Проверяем Ctrl+Q
                modifiers = pygame.key.get_mods()
                if event.key == pygame.K_q and (modifiers & pygame.KMOD_CTRL):
                    running = False
                else:
                    # Блокируем все другие клавиши
                    continue
            
            # Игнорируем все другие события
            continue

    # Восстанавливаем систему
    pygame.event.set_grab(False)
    remove_keyboard_hook()
    unblock_windows_keys()
    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    # Определяем папку, где лежит .py или .exe
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

    image_file = os.path.join(base_path, "bsod.jpg")
    sound_file = os.path.join(base_path, "sound.mp3")

    if not os.path.exists(image_file):
        print("❌ Не найден bsod.jpg")
        sys.exit(1)
    if not os.path.exists(sound_file):
        print("❌ Не найден sound.mp3")
        sys.exit(1)

    try:
        show_image_fullscreen(image_file, sound_file)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Гарантированно восстанавливаем систему при любом выходе
        try:
            remove_keyboard_hook()
            unblock_windows_keys()
        except:
            pass