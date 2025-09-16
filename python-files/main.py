from companion_core import CompanionCore
from gui_messenger import AnimeMessengerGUI

def main():
    try:
        # Создаем экземпляр компаньона
        companion = CompanionCore()
        
        # Создаем и запускаем GUI
        gui = AnimeMessengerGUI(companion)
        gui.run()
        
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        input("Нажмите Enter для выхода...")
    
    finally:
        # Корректно закрываем соединения при выходе
        try:
            companion.close()
        except:
            pass

if __name__ == "__main__":
    main()
