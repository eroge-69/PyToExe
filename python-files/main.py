import pygame
from setting import get_display_size
import cutscene
import menu
from data_manager import DataManager  # اضافه شد

def main():
    pygame.init()

    # دریافت رزولوشن مانیتور و تنظیم فول‌اسکرین
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("404: Lost Hero")

    # دریافت مرحله ذخیره‌شده از DataManager
    dm = DataManager()
    saved_level = dm.get_current_level()

    # اجرای کات‌سین و بعد منو با مرحله ذخیره‌شده
    cutscene.cutscene_screen(screen, lambda s: menu.main_menu(s, saved_level))

if __name__ == "__main__":
    main()
