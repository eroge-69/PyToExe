current_time = time.time()
        if current_time - self.last_press_time < self.cooldown:
            return
        
        try:
            screen_gray = self.capture_screen()
            
            for name, template_data in self.templates.items():
                confidence, location = self.find_template(screen_gray, template_data)
                
                if confidence:
                    print(f"🎯 Обнаружена кнопка {name}! Уверенность: {confidence:.2f}")
                    pyautogui.press(template_data['key'])
                    self.last_press_time = current_time
                    time.sleep(0.1)  # Короткая пауза
                    break  # Прекращаем проверку после первого найденного
                    
        except Exception as e:
            print(f"Ошибка проверки: {e}")
    
    def run_bot(self):
        """Основной цикл работы"""
        print("🤖 Бот запущен! Проверка каждые {} сек".format(self.check_interval))
        
        while self.running:
            self.check_screen()
            time.sleep(self.check_interval)
        
        print("⏹️ Бот остановлен")
    
    def start(self):
        """Запускает бота"""
        if self.running:
            print("Бот уже запущен!")
            return
        
        if not self.templates:
            print("⚠️ Нет загруженных шаблонов!")
            return
        
        self.running = True
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def stop(self):
        """Останавливает бота"""
        self.running = False

def setup_templates_automatically():
    """Автоматическая настройка шаблонов"""
    bot = AdvancedImageKeyPressBot()
    
    # Создаем папку для шаблонов если её нет
    templates_dir = "game_templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"📁 Создана папка: {templates_dir}")
        print("📸 Поместите в неё скриншоты кнопок с именами: e.png, f.png, y.png, h.png")
        return bot
    
    # Загружаем шаблоны из папки
    print("🔄 Загружаю шаблоны из папки...")
    bot.load_templates_from_folder(templates_dir)
    
    return bot

def main():
    print("=" * 60)
    print("🎮 ADVANCED GAME BOT - Автоматическое нажатие клавиш")
    print("=" * 60)
    
    bot = setup_templates_automatically()
    
    # Горячие клавиши
    def toggle_bot():
        if bot.running:
            bot.stop()
            print("⏸️ Пауза")
        else:
            bot.start()
            print("▶️ Запуск")
    
    def emergency_stop():
        print("🛑 АВАРИЙНАЯ ОСТАНОВКА!")
        bot.stop()
        keyboard.unhook_all()
        exit()
    
    keyboard.add_hotkey('f1', toggle_bot)
    keyboard.add_hotkey('f2', emergency_stop)
    keyboard.add_hotkey('f3', lambda: bot.check_screen())
    keyboard.add_hotkey('f4', lambda: setattr(bot, 'confidence', max(0.5, bot.confidence - 0.05)) or print(f"🤏 Чувствительность: {bot.confidence:.2f}")))
    keyboard.add_hotkey('f5', lambda: setattr(bot, 'confidence', min(0.95, bot.confidence + 0.05)) or print(f"👆 Чувствительность: {bot.confidence:.2f}")))
    
    print("\n🎯 Горячие клавиши:")
    print("F1 - Запуск/Пауза")
    print("F2 - Аварийная остановка")
    print("F3 - Разовая проверка")
    print("F4 - Увеличить чувствительность")
    print("F5 - Уменьшить чувствительность")
    print("\n⚠️ ВАЖНО: Используйте только в одиночных играх!")
    print("📸 Поместите скриншоты кнопок в папку 'game_templates/'")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
    finally:
        bot.stop()

if name == "main":
    # Проверяем зависимости
    try:
        import cv2
        import pyautogui
        import keyboard
    except ImportError:
        print("❌ Установите зависимости:")
        print("pip install opencv-python pyautogui keyboard pillow numpy")
        exit(1)
    
    main()