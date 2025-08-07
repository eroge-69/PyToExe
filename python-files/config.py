# Конфигурация PixelWare CMD Loader

class Config:
    # Dropbox настройки
    DROPBOX_URL = "https://www.dropbox.com/scl/fi/higlxfi6fvrdt7jmx6ioe/PixelWare.jar?rlkey=hg7cvevjji7rzvk7ppsuuce1h&st=qj1diot7&dl=1"
    
    # Пути
    EXTRACT_PATH = "C:\\PixelWare"
    JAVA_PATH = "C:\\Java17"
    JAR_NAME = "PixelWare.jar"
    
    # Java 17 URL (официальный OpenJDK)
    JAVA_URL = "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_windows-x64_bin.zip"
    
    # Название приложения
    APP_TITLE = "PixelWare"
    APP_VERSION = "v1.0.0"
    
    # Цвета для CMD (ANSI коды)
    COLORS = {
        "reset": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m"
    }
    
    # Сообщения
    MESSAGES = {
        "welcome": "Добро пожаловать в PixelWare Loader!",
        "java_check": "Проверка Java 17...",
        "java_download": "Загрузка Java 17...",
        "java_install": "Установка Java 17...",
        "client_download": "Загрузка PixelWare клиента...",
        "client_launch": "Запуск PixelWare...",
        "success": "PixelWare успешно загружен и запущен!",
        "error": "Произошла ошибка:",
        "interrupted": "Загрузка прервана пользователем",
        "critical_error": "Критическая ошибка:"
    }
    
    # Таймауты (в секундах)
    JAVA_CHECK_TIMEOUT = 5
    DOWNLOAD_TIMEOUT = 300  # 5 минут
    
    # Размеры буфера для скачивания
    DOWNLOAD_CHUNK_SIZE = 8192
    
    @classmethod
    def validate_config(cls):
        """Проверка конфигурации"""
        if cls.DROPBOX_URL == "https://dl.dropboxusercontent.com/s/YOUR_FILE_ID/pixelware.jar":
            raise ValueError("Пожалуйста, настройте URL Dropbox в config.py")
        
        if not cls.JAR_NAME:
            raise ValueError("Пожалуйста, укажите имя JAR файла в config.py")
        
        return True
