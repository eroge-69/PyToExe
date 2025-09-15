class LEDSupportBot:
    def __init__(self):
        self.current_state = "main_menu"
    
    def show_menu(self):
        menus = {
            "main_menu": {
                "text": "Добро пожаловать в службу поддержки! Что у вас за устройство?",
                "options": {
                    "1": "⛪ Аптечный крест",
                    "2": "📜 Бегущая строка", 
                    "3": "📺 Светодиодный экран",
                    "4": "🛠️ Срочная помощь"
                }
            },
            "device_cross": {
                "text": "Аптечный крест. Выберите раздел:",
                "options": {
                    "1": "⚙️ Настройка и ПО",
                    "2": "❗ Частые проблемы",
                    "3": "🔧 Аппаратные сбои",
                    "0": "◀️ Назад"
                }
            },
            "cross_software": {
                "text": "Настройка и ПО для аптечного креста:",
                "options": {
                    "1": "🖥️ HD",
                    "2": "🖥️ BX", 
                    "3": "📚 Инструкция",
                    "0": "◀️ Назад"
                }
            },
            "cross_software_hd": {
                "text": "ПО HD для аптечного креста:\nСкачайте последнюю версию:\nhttps://example.com/hd-cross\n\nОсновные настройки:...",
                "options": {"0": "◀️ К выбору ПО"}
            },
            "cross_software_bx": {
                "text": "ПО BX для аптечного креста:\nСкачайте последнюю версию:\nhttps://example.com/bx-cross\n\nНастройки:...",
                "options": {"0": "◀️ Назад"}
            },
            "cross_manual": {
                "text": "📘 Инструкция по эксплуатации:\nhttps://example.com/manual-cross",
                "options": {"0": "◀️ Назад"}
            },
            "urgent_help": {
                "text": "Для оперативной помощи:\n📞 Телефон: +7 (343) 228-77-10\n✉️ Email: sinfo@eqsrf.ru\n🕒 Время работы: 9:00-18:00",
                "options": {"0": "◀️ В главное меню"}
            }
        }
        return menus.get(self.current_state, {"text": "Ошибка меню", "options": {}})
    
    def handle_input(self, choice):
        transition_map = {
            "main_menu": {
                "1": "device_cross",
                "2": "device_string",
                "3": "device_screen",
                "4": "urgent_help"
            },
            "device_cross": {
                "1": "cross_software",
                "2": "cross_issues",
                "3": "cross_hardware",
                "0": "main_menu"
            },
            "cross_software": {
                "1": "cross_software_hd",
                "2": "cross_software_bx",
                "3": "cross_manual",
                "0": "device_cross"
            },
            "cross_software_hd": {"0": "cross_software"},
            "cross_software_bx": {"0": "cross_software"},
            "cross_manual": {"0": "cross_software"},
            "urgent_help": {"0": "main_menu"}
        }
        
        if self.current_state in transition_map:
            current_transitions = transition_map[self.current_state]
            if choice in current_transitions:
                self.current_state = current_transitions[choice]
                return True
        return False

if __name__ == "__main__":
    bot = LEDSupportBot()
    
    while True:
        current_menu = bot.show_menu()
        print(f"\n{current_menu['text']}\n")
        
        for key, value in current_menu['options'].items():
            print(f"{key}. {value}")
        
        choice = input("\nВаш выбор: ").strip()
        
        if not bot.handle_input(choice):
            print("\n⚠️ Неверный вариант, попробуйте еще раз")
        
        print("\n" + "="*40)