import telebot
from math import sqrt

TOKEN = "7704795429:AAFIRkLTvbEwmM2UYAsPYE7KIadC6qe4MII"
bot = telebot.TeleBot(TOKEN)

# Таблицы сечений (медь и алюминий)
CABLE_TABLES = {
    'copper': {
        1.5: 19, 2.5: 27, 4: 38, 6: 50, 10: 70
    },
    'aluminum': {
        2.5: 21, 4: 29, 6: 38, 10: 55
    }
}

# Коэффициенты для разных типов прокладки
INSTALLATION_FACTORS = {
    'open': 1.0,
    'closed': 1.2  # +20% к току для закрытой прокладки
}

@bot.message_handler(commands=['start'])
def start(message):
    help_text = """
    ⚡ *Расширенный калькулятор электромонтажника*
    
    Введите данные в формате:
    `U, P, I, R, материал, прокладка, длина`
    
    Где:
    - Первые 4 параметра (U,P,I,R): значения или `?`
    - Материал: `медь` (по умолчанию) или `алюминий`
    - Прокладка: `открытая` (по умолч.) или `закрытая`
    - Длина: число (м) для расчёта падения напряжения
    
    Примеры:
    `220, 5500, ?, ?, медь, закрытая, 25`
    `380, ?, 20, ?, алюминий, открытая, 10`
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help(message):
    help_text = '''U - Напряжение (В)
    P - Мощность(Вт)
    I - Сила тока(А)
    R - Сопротивление(Ом)\n
    Данный бот подставляет данные в существующие формулы и выдает ответ с данными.
    '''
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['tips'])
def send_tips(message):
    tips = """
    📜 Нормы:
    • Освещение: 1.5 мм² медь
    • Розетки: 2.5 мм²
    • Варочная: 6 мм²
    """
    bot.reply_to(message, tips)

def calculate_cable_section(current, material='copper', installation='open'):
    """Выбор сечения с учётом материала и прокладки"""
    adjusted_current = current * INSTALLATION_FACTORS.get(installation, 1.0)
    table = CABLE_TABLES.get(material, CABLE_TABLES['copper'])
    
    for section, max_current in sorted(table.items()):
        if adjusted_current <= max_current:
            return section
    return max(table.keys(), default=10)

def calculate_voltage_drop(U, I, length, section, material='copper'):
    """Расчёт падения напряжения в %"""
    rho = 0.0175 if material == 'copper' else 0.028
    if U == 0 or section == 0:
        return 0
    drop = (2 * I * length * rho) / section
    return (drop / U) * 100

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        parts = [p.strip().lower() for p in message.text.split(',')]
        
        # Парсинг входных данных
        U = float(parts[0]) if parts[0] != '?' else None
        P = float(parts[1]) if len(parts) > 1 and parts[1] != '?' else None
        I = float(parts[2]) if len(parts) > 2 and parts[2] != '?' else None
        R = float(parts[3]) if len(parts) > 3 and parts[3] != '?' else None
        
        material = 'copper'
        installation = 'open'
        length = 0
        
        if len(parts) > 4:
            material = parts[4] if parts[4] in ['медь', 'алюминий'] else 'copper'
        if len(parts) > 5:
            installation = parts[5] if parts[5] in ['открытая', 'закрытая'] else 'open'
        if len(parts) > 6:
            length = float(parts[6])

        # Расчёт неизвестных величин
        if U is None and P is not None and I is not None:
            U = P / I
        if P is None and U is not None and I is not None:
            P = U * I
        if I is None and P is not None and U is not None:
            I = P / U
        if R is None and U is not None and I is not None:
            R = U / I

        # Формирование результата
        result = f"""
        🔌 *Электрические параметры:*
        Напряжение (U): {U or '?'} В
        Мощность (P): {P or '?'} Вт
        Ток (I): {I or '?'} А
        Сопротивление (R): {R or '?'} Ом
        """

        # Расчёт сечения и падения напряжения
        if I is not None:
            section = calculate_cable_section(I, material, installation)
            result += f"\n📏 *Рекомендуемое сечение:* {section} мм² ({material})"
            
            if length > 0 and U is not None:
                drop = calculate_voltage_drop(U, I, length, section, material)
                result += f"\n⚠ *Падение напряжения:* {drop:.2f}% ({length} м)"
                
                if drop > 5:
                    result += "\n❌ Превышено допустимое падение! Увеличьте сечение кабеля"

        bot.reply_to(message, result, parse_mode="Markdown")

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "❌ Ошибка в формате данных! Используйте:\n`220, 5500, ?, ?, медь, закрытая, 25`")

bot.polling()