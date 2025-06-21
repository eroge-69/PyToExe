import json
import os

# Файл для сохранения статистики
FILE_NAME = "stats.json"

# Загрузка данных из JSON при запуске
def load_data():
    global players
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            players.update(json.load(f))  # Обновляем текущие данные
        print("📂 Данные игроков загружены из файла.")
    else:
        print("📁 Файл данных не найден. Используются начальные значения.")

# Сохранение данных в JSON после каждого изменения
def save_data():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4, ensure_ascii=False)
    print("✅ Данные сохранены.")

# список игроков
players = {
    0: {
        'name': 'Danya',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    1: {
        'name': 'Enrike',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    2: {
        'name': 'Timur',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    3: {
        'name': 'Arseniy',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    4: {
        'name': 'Gosha',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    5: {
        'name': 'Lisa',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    6: {
        'name': 'Dasha',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    7: {
        'name': 'Oleg',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    8: {
        'name': 'Timur',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    9: {
        'name': 'Vasiliy',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    10: {
        'name': 'Sanya',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    11: {
        'name': 'Anya',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    12: {
        'name': 'Adriatic',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    13: {
        'name': 'Ruth',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    14: {
        'name': 'Masha',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    15: {
        'name': 'Alena',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    16: {
        'name': 'Asya',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    17: {
        'name': 'Arseniy',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    18: {
        'name': 'Adriatic',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    19: {
        'name': 'Polina',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    20: {
        'name': 'Yuri',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    21: {
        'name': 'Stefa',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    22: {
        'name': 'Liza',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    23: {
        'name': 'Yana',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    24: {
        'name': 'Adriatic',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    30: {
        'name': 'Natt',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    33: {
        'name': 'Nikita',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    52: {
        'name': 'Sasha',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    77: {
        'name': 'Stanislav',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    },
    88: {
        'name': 'Egor',
        'att': {'kills': 0, 'errors': 0},
        'digs': {'success': 0, 'errors': 0},
        'assists': {'success': 0, 'errors': 0},
        'blocks': {'success': 0, 'block touch': 0, 'errors': 0},
        'serves': {'ace': 0, 'kills': 0, 'serve errors': 0},
        'receptions': {'perfect pass': 0, 'done receptions': 0, 'reception error': 0},
        'matches': 0
    }
}

def attacks(player_id):
    if player_id in players.keys():
        total_attacks = players[player_id]['att']['kills'] + players[player_id]['att']['errors']
        success_attacks_rate = players[player_id]['att']['kills']/total_attacks * 0.01
    else:
        return "Нет игрока под таким номером"

def serves(player_id):
    total_serves = players[player_id]['serves']['ace'] + players[player_id]['serves']['serve errors'] + players[player_id]['serves']['kills']
    success_serves_rate = ((players[player_id]['serves']['ace'] + players[player_id]['serves']['kills'] ) / total_serves) * 0.01

def receptions(player_id):
    total_receptions = players[player_id]['receptions']['perfect pass'] + players[player_id]['receptions']['done receptions']
    perfect_receptions_rate = ((players[player_id]['receptions']['done receptions'] +players[player_id]['receptions']['perfect pass']) / total_receptions) * 0.01

def blocks(player_id):
    total_blocks = players[player_id]['blocks']['success'] + players[player_id]['blocks']['block touch'] + players[player_id]['blocks']['errors']

def digs(player_id):
    total_digs = players[player_id]['digs']['success'] + players[player_id]['digs']['errors']

def assists(player_id):
    total_assists = players[player_id]['assists']['success'] + players[player_id]['assists']['errors']

def check_player_exists(player_id):
    if player_id not in players:
        print("Нет игрока с таким номером")
        return False
    return True

def show_player_stats(player_id):
    player = players[player_id]
    print(f"\nСтатистика игрока: {player['name']} (ID: {player_id})")

    print("\nАтака:")
    for key, value in player['att'].items():
        print(f"  {key}: {value}")

    print("\nЗащита (диг):")
    for key, value in player['digs'].items():
        print(f"  {key}: {value}")

    print("\nПасы (ассисты):")
    for key, value in player['assists'].items():
        print(f"  {key}: {value}")

    print("\nБлоки:")
    for key, value in player['blocks'].items():
        print(f"  {key}: {value}")

    print("\nПодачи:")
    for key, value in player['serves'].items():
        print(f"  {key}: {value}")

    print("\nПриём:")
    for key, value in player['receptions'].items():
        print(f"  {key}: {value}")

    print(f"\nМатчи сыграно: {player['matches']}")
    print(f"Кол-во замен: {player['changes']}")

    total_won_points = (
        player['att']['kills'] +
        player['serves']['ace'] +
        player['serves']['kills'] +
        player['blocks']['success']
    )
    print(f"Выигранные очки: {total_won_points}")

load_data()

# Главный цикл
while True:
    print("1. Настройка составов")
    print("2. Выход")
    choise_1 = int(input("Выберите один из вариантов: "))

    if choise_1 == 1:
        print("Настройка составов")
        n = int(input("Общее кол-во игроков в команде: "))
        for _ in range(n):
            player_id = int(input("Введите номер игрока: "))
            if not check_player_exists(player_id):
                continue
            players[player_id]["matches"] += 1
        save_data()
        print("Состав команды установлен!")  # подтверждение

    elif choise_1 == 2:
        save_data()
        break  # корректный выход из программы

    else:
        print("Нет такого варианта")
        continue

    # Второй блок действий: после настройки состава
    while True:
        print("1. Добавить к статистике")
        print("2. Просмотреть статистику")
        print("3. Назад")  # выход в главное меню
        choise = int(input("Выберите дейтсвие: "))  # выбор действия

        if choise == 1:
            player_id = int(input("Введите номер игрока: "))
            if not check_player_exists(player_id):
                continue

            # выбор действия
            action_num = int(input("Выберите дейтвие(атака(1)/защита(2)/пас(3)/блок(4)/подача(5)/приём(6)/замена(7)): "))

            if action_num == 1:  # добавляем к атаке
                att_choise = int(input("удачно - 1, неудачно - 2: "))
                if att_choise == 1:
                    players[player_id]['att']['kills'] += 1
                elif att_choise == 2:
                    players[player_id]['att']['errors'] += 1
                else:
                    print("Нету такого действия")
                    continue

            elif action_num == 2:  # добавляем к защите
                digs_choise = int(input("удачно - 1, неудачно - 2: "))
                if digs_choise == 1:
                    players[player_id]['digs']['success'] += 1
                elif digs_choise == 2:
                    players[player_id]['digs']['errors'] += 1
                else:
                    print("Нет такого варианта")
                    continue

            elif action_num == 3:  # добавляем к пасу
                assists_choice = int(input("удачно - 1, неудачно - 2: "))
                if assists_choice == 1:
                    players[player_id]['assists']['success'] += 1
                elif assists_choice == 2:
                    players[player_id]['assists']['errors'] += 1
                else:
                    print("Нету такого выбора")
                    continue

            elif action_num == 4:  # добавляем к блоку
                block_choise = int(input("удачно - 1, касание - 2, неудачно - 3: "))
                if block_choise == 1:
                    players[player_id]['blocks']['success'] += 1
                elif block_choise == 2:
                    players[player_id]['blocks']['block touch'] += 1
                elif block_choise == 3:
                    players[player_id]['blocks']['errors'] += 1
                else:
                    print("Нету такого выбора")
                    continue

            elif action_num == 5:  # добавляем к подаче
                serves_choise = int(input("Эйс - 1, удачно - 2, неудачно - 3: "))
                if serves_choise == 1:
                    players[player_id]['serves']['ace'] += 1
                elif serves_choise == 2:
                    players[player_id]['serves']['kills'] += 1
                elif serves_choise == 3:
                    players[player_id]['serves']['serve errors'] += 1
                else:
                    print("Нету такого выбора")
                    continue

            elif action_num == 6:  # добавляем к приему
                receptions_choise = int(input("идеально - 1, удачно - 2, неудачно - 3: "))
                if receptions_choise == 1:
                    players[player_id]['receptions']['perfect pass'] += 1
                elif receptions_choise == 2:
                    players[player_id]['receptions']['done receptions'] += 1
                elif receptions_choise == 3:
                    players[player_id]['receptions']['reception error'] += 1
                else:
                    print("Нету такого выбора")
                    continue

            elif action_num == 7:  # добавляем замену
                players[player_id]["changes"] += 1

            else:
                print("Нету такого действия")
                continue

            save_data()

        elif choise == 2:
            player_id = int(input("Введите номер игрока, чью статистику желаете просмотреть: "))
            if check_player_exists(player_id):
                show_player_stats(player_id)

        elif choise == 3:
            save_data()
            break  # возвращаемся к главному меню

        else:
            print("Нет такого выбора")
