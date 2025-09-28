
# simple_game.py
# Простая консольная игра с HP, деньгами и магазином.
import random
import sys
import time

class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.max_hp = 100
        self.hp = 100
        self.money = 50
        self.attack = 10
        self.potions = 1

    def is_alive(self):
        return self.hp > 0

def clear():
    # cross-platform clear
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nНажмите Enter, чтобы продолжить...")

def show_status(p):
    print(f"\n{p.name} — HP: {p.hp}/{p.max_hp} | Деньги: ${p.money} | Зелья: {p.potions}")

def shop(player):
    while True:
        clear()
        print("=== Магазин ===")
        print("1) Купить зелье (+50 HP) — $20")
        print("2) Купить улучшение атаки (+5 к атаке) — $40")
        print("3) Выйти")
        show_status(player)
        choice = input("\nВыберите действие: ")
        if choice == "1":
            if player.money >= 20:
                player.money -= 20
                player.potions += 1
                print("Вы купили зелье.")
            else:
                print("Недостаточно денег.")
            pause()
        elif choice == "2":
            if player.money >= 40:
                player.money -= 40
                player.attack += 5
                print("Атака увеличена.")
            else:
                print("Недостаточно денег.")
            pause()
        elif choice == "3":
            break
        else:
            print("Неверный выбор.")
            pause()

def fight(player):
    enemy_hp = random.randint(30, 120)
    enemy_attack = random.randint(5, 18)
    enemy_name = random.choice(["Гоблин", "Скелет", "Бандит", "Дикий волк"])
    clear()
    print(f"Появился враг: {enemy_name} (HP {enemy_hp}, Атака {enemy_attack})")
    while enemy_hp > 0 and player.is_alive():
        show_status(player)
        print(f"\nВраг {enemy_name} — HP: {enemy_hp}")
        print("1) Атаковать")
        print("2) Использовать зелье")
        print("3) Убежать")
        choice = input("Выберите действие: ")
        if choice == "1":
            dmg = player.attack + random.randint(-2, 6)
            enemy_hp -= max(1, dmg)
            print(f"Вы нанесли {max(1,dmg)} урона.")
        elif choice == "2":
            if player.potions > 0:
                player.potions -= 1
                heal = 50
                player.hp = min(player.max_hp, player.hp + heal)
                print(f"Вы использовали зелье и восстановили {heal} HP.")
            else:
                print("Залений закончились.")
        elif choice == "3":
            if random.random() < 0.5:
                print("Вам удалось убежать.")
                return False
            else:
                print("Не удалось убежать.")
        else:
            print("Неверный выбор.")

        if enemy_hp > 0:
            ed = enemy_attack + random.randint(-3,4)
            player.hp -= max(0, ed)
            print(f"Вас атаковали и нанесли {max(0,ed)} урона.")
        time.sleep(0.8)

    if player.is_alive():
        loot = random.randint(10, 60)
        player.money += loot
        print(f"\nВы победили {enemy_name}! Получено ${loot}.")
        return True
    else:
        print("\nВы были повержены...")
        return False

def main():
    clear()
    print("=== Простая текстовая игра ===")
    name = input("Введите имя персонажа: ").strip() or "Игрок"
    player = Player(name)
    while True:
        clear()
        print(f"Добро пожаловать, {player.name}!")
        show_status(player)
        print("\nЧто хотите сделать?")
        print("1) Сражаться")
        print("2) Магазин")
        print("3) Отдохнуть (+30 HP, бесплатно)")
        print("4) Сохранить и выйти")
        choice = input("Ваш выбор: ")
        if choice == "1":
            survived = fight(player)
            if not survived:
                print("Игра окончена.")
                break
            pause()
        elif choice == "2":
            shop(player)
        elif choice == "3":
            player.hp = min(player.max_hp, player.hp + 30)
            print("Вы отдохнули и восстановили 30 HP.")
            pause()
        elif choice == "4":
            print("До свидания!")
            break
        else:
            print("Неверный выбор.")
            pause()

if __name__ == '__main__':
    main()
