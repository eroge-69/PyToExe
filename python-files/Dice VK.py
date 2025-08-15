import random
import re
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = 'vk1.a.YPaimp1hIjG4kcMNwLx09ZGCvlC-plBQMJrpOHRsYxl-dSTnmDim7-69sdaRAo05zn7y6hM_NCF69ylRHKZ1XJMcAGdFHlqd5xtmskiF4F944I0yqyZZul3uWEI_xUB5gL4A9XHe1hjcFk-YIWbM2cqtZR83IW0QfxHETfLvFDUI4aYcdDJAO4d7UNhyZnevSgCA5VskQCgJBQoDkW18vg'  # Замени на токен твоего сообщества
GROUP_ID = 232138023  # ID группы

# функция для парсинга команды X/rY±Z
def parse_dice_command(command_text):
    # регулярное выражение для парсинга: опциональное число бросков, '/r', опциональный минус, число граней, опциональный модификатор ±/*число
    match = re.match(r'^/(\d*)[rRdDlLдДкКвВ](-?\d+)([+*-]\d+)?$', command_text)
    if not match:
        return None
    num_rolls = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    modifier_str = match.group(3) if match.group(3) else None
    modifier = 0
    mod_type = None
    if modifier_str:
        mod_type = modifier_str[0]  # +, -, или *
        modifier = int(modifier_str[1:])
        if mod_type == '-':
            modifier = -modifier
    if abs(sides) < 2 or num_rolls < 1:
        return None
    return num_rolls, abs(sides), modifier, mod_type, sides < 0

# функция для ролла кубиков
def roll_dice(num_rolls, sides, modifier, mod_type, is_negative):
    rolls = [random.randint(1, sides) for _ in range(num_rolls)]
    total = sum(rolls)
    if mod_type == '+' or mod_type == '-':
        total += modifier
    elif mod_type == '*':
        total *= modifier
    if is_negative:
        total = -total
        rolls = [-r for r in rolls]  # инвертируем сами броски для отображения
    if num_rolls > 1:
        rolls_str = ' + '.join(map(str, rolls))
        if mod_type == '+':
            rolls_str += f' + {modifier}'
        elif mod_type == '-':
            rolls_str += f' - {abs(modifier)}'
        elif mod_type == '*':
            rolls_str += f' * {modifier}'
        return f'Броски: {rolls_str} = {total}', total
    else:
        if mod_type:
            symbol = '+' if mod_type == '+' else mod_type
            return f'Бросок: {rolls[0]} {symbol} {abs(modifier)} = {total}', total
        else:
            return f'Бросок: {rolls[0]}', rolls[0]

# Функция для получения инструкции
def get_info():
    return (
        "Рандомайзер (дайсроллер) для чатов, собран из говна и палок руками https://vk.com/rotten_curse\n\n"
        "Для вызова этой инструкции используйте /help или напишите 'Начать'\n\n"
        "Используйте команды /r, /d, /к или /д с параметрами для броска кубиков\n\n"
        "Формат параметров: /XrY±Z (или /XdY±Z, /XвY±Z, /XкY±Z, /XдY±Z, /XlY±Z) в любом регистре\n"
        "- X: Количество бросков (опционально, по умолчанию 1)\n"
        "- Y: Количество граней кубика (минимум 2, можно использовать отрицательное число для инверсии)\n"
        "- ±Z: Модификатор (опционально, +, - или * число)\n\n"
        "Примеры:\n"
        "- /r20 или /d20: Один бросок кубика с 20 гранями\n"
        "- /2к6: Два броска кубика с 6 гранями, сумма\n"
        "- /д100+5: Один бросок с 100 гранями плюс 5\n"
        "- /3r10-2: Три броска с 10 гранями минус 2\n"
        "- /к-50: Один бросок с 50 гранями, результат инвертирован\n"
        "- /d20*3: Один бросок с 20 гранями, умноженный на 3\n"
        "- /10д20-50: 10 бросков кубика с 20 гранями минус 50\n"
        "- /6r-10+20: 6 бросков кубика с 10 гранями, инвертированных, плюс 20\n"
        "- /2r20 /3д50 /10к5+20: Несколько бросков с разными параметрами в одном сообщении. Разделяйте команды пробелом\n\n"
        "Примечание: Можно не ограничиваться исключительно дайсами - рандомить можно до любого числа, хоть до миллиона\n"
        "Бот работает в чатах, если у него есть права на отправку сообщений\n"
    )

# Обработчик команд
def handle_dice_command(vk, event):
    # Проверяем, что сообщение из беседы или личного чата
    if 'text' not in event.obj.message or not event.obj.message['text']:
        return

    command_text = event.obj.message['text'].strip()  # убираем лишние пробелы
    peer_id = event.obj.message['peer_id']
    
    # Проверяем команду "Начать"
    if command_text.lower() == 'начать':
        vk.messages.send(
            peer_id=peer_id,
            message=get_info(),
            random_id=random.randint(1, 1000000)
        )
        return

    # разделяем команду на отдельные броски по пробелу
    commands = [cmd.strip() for cmd in command_text.split() if cmd.strip()]  # убираем пустые команды
    if not commands:
        return  # не отвечаем, если пусто

    results = []
    has_valid_command = False
    for cmd in commands:
        if cmd.lower() == '/help':
            results.append(get_info())
            has_valid_command = True
            continue
        
        # проверяем на наличие чисел с плавающей точкой в этой команде
        if (re.match(r'^/\d*[rRdDlLдДкКвВ]-?\d*\.\d+', cmd) or 
            re.match(r'^/\d*[rRdDlLдДкКвВ]-?\d+[+*-]\d*\.\d+', cmd)):
            results.append('Блять, олух, я понимаю только целые числа, не умничай тут блять')
            has_valid_command = True  # считаем как обработанную
            continue

        # проверяем, что команда соответствует формату
        parsed = parse_dice_command(cmd)
        if parsed:
            num_rolls, sides, modifier, mod_type, is_negative = parsed
            result, _ = roll_dice(num_rolls, sides, modifier, mod_type, is_negative)
            results.append(result)
            has_valid_command = True
        else:
            results.append('Иди нахуй, не тот формат')

    if has_valid_command:
        vk.messages.send(
            peer_id=peer_id,
            message='\n'.join(results),
            random_id=random.randint(1, 1000000)
        )

def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                handle_dice_command(vk, event)
    except Exception as e:
        print(f"Error in Long Poll: {e}")

if __name__ == '__main__':
    main()