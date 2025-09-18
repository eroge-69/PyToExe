import random
import time
import sys
from typing import Dict


class RouletteSimulator:
    def __init__(self):
        self.numbers = list(range(0, 37))  # Европейская рулетка (0-36)
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        self.balance = 1000  # Уменьшенный начальный баланс в рублях (1000₽)
        self.min_bet = 10  # Уменьшенная минимальная ставка 10₽
        self.max_bet = 500  # Уменьшенная максимальная ставка 500₽
        self.exchange_rate = 1  # Курс рубля

    def animate_text(self, text: str, delay: float = 0.03):
        """Анимация печати текста"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()

    def spinning_animation(self, duration: int = 3):
        """Анимация вращения рулетки"""
        symbols = ["◐", "◓", "◑", "◒"]
        start_time = time.time()

        print("\n🎡 ", end="")
        while time.time() - start_time < duration:
            for symbol in symbols:
                print(f"\r🎡 Рулетка вращается... {symbol}", end="", flush=True)
                time.sleep(0.1)
        print()

    def countdown_animation(self):
        """Анимация обратного отсчета"""
        for i in range(3, 0, -1):
            print(f"\r⏱️  {i}...", end="", flush=True)
            time.sleep(1)
        print("\r🎯 Результат! ", end="", flush=True)
        time.sleep(0.5)

    def spin_wheel(self) -> int:
        """Вращение рулетки и выпадение числа"""
        return random.choice(self.numbers)

    def get_color(self, number: int) -> str:
        """Определение цвета выпавшего числа"""
        if number == 0:
            return 'зеленый'
        elif number in self.red_numbers:
            return 'красный'
        else:
            return 'черный'

    def format_money(self, amount: int) -> str:
        """Форматирование денежной суммы"""
        return f"{amount:,}₽".replace(",", " ")

    def simple_betting(self, bet_amount: int, bet_type: str, bet_value: str) -> bool:
        """Простая ставка на конкретный вариант"""
        if bet_amount > self.balance:
            self.animate_text("❌ Недостаточно средств!", 0.01)
            return False

        if bet_amount < self.min_bet:
            self.animate_text(f"❌ Минимальная ставка: {self.format_money(self.min_bet)}!", 0.01)
            return False

        if bet_amount > self.max_bet:
            self.animate_text(f"❌ Максимальная ставка: {self.format_money(self.max_bet)}!", 0.01)
            return False

        self.balance -= bet_amount
        print(f"\n🎲 Ставка: {self.format_money(bet_amount)} на {bet_type}: {bet_value}")
        print(f"💰 Баланс перед спином: {self.format_money(self.balance + bet_amount)}")

        # Анимация вращения
        self.spinning_animation()
        self.countdown_animation()

        # Вращаем рулетку
        result = self.spin_wheel()
        result_color = self.get_color(result)

        # Анимация выпадения результата
        print(f"Выпало: ", end="", flush=True)
        time.sleep(0.5)

        if result_color == 'красный':
            print(f"🔴 {result} ({result_color})")
        elif result_color == 'черный':
            print(f"⚫ {result} ({result_color})")
        else:
            print(f"🟢 {result} ({result_color})")

        # Проверяем выигрыш
        win = False
        win_multiplier = 0

        if bet_type == 'цвет':
            if bet_value == result_color:
                win = True
                win_multiplier = 2
        elif bet_type == 'число':
            if str(result) == bet_value:
                win = True
                win_multiplier = 36
        elif bet_type == 'чет/нечет':
            if result != 0:
                if (bet_value == 'чет' and result % 2 == 0) or (bet_value == 'нечет' and result % 2 == 1):
                    win = True
                    win_multiplier = 2

        # Анимация результата
        time.sleep(1)
        if win:
            win_amount = bet_amount * win_multiplier
            self.balance += win_amount
            print("✨" * 30)
            self.animate_text(f"🎉 ВЫИГРЫШ! +{self.format_money(win_amount)}", 0.02)
            print("✨" * 30)
            print(f"💰 Новый баланс: {self.format_money(self.balance)}")
        else:
            print("💥" * 20)
            self.animate_text("💔 Проигрыш", 0.05)
            print("💥" * 20)
            print(f"💰 Баланс: {self.format_money(self.balance)}")

        return win

    def display_stats(self):
        """Показать статистику игры"""
        print("\n" + "=" * 60)
        print("📊 СТАТИСТИКА ИГРЫ")
        print("=" * 60)
        profit_loss = self.balance - 1000  # Изменено на новый начальный баланс
        percent_change = ((self.balance - 1000) / 1000 * 100)  # Изменено на новый начальный баланс

        print(f"💰 Финальный баланс: {self.format_money(self.balance)}")

        if profit_loss > 0:
            print(f"📈 Прибыль: +{self.format_money(profit_loss)}")
            print(f"📊 Процент прибыли: +{percent_change:.1f}%")
        else:
            print(f"📉 Убыток: {self.format_money(profit_loss)}")
            print(f"📊 Процент убытка: {percent_change:.1f}%")


def main():
    simulator = RouletteSimulator()

    # Красивое приветствие
    print("🎰" * 20)
    simulator.animate_text("🎰 ДОБРО ПОЖАЛОВАТЬ В РУССКУЮ РУЛЕТКУ! 🎰", 0.03)
    print("🎰" * 20)
    print(f"💰 Ваш начальный баланс: {simulator.format_money(simulator.balance)}")
    print(f"🎯 Минимальная ставка: {simulator.format_money(simulator.min_bet)}")
    print(f"🎯 Максимальная ставка: {simulator.format_money(simulator.max_bet)}")

    while simulator.balance > 0:
        print("\n" + "═" * 40)
        simulator.animate_text("🎲 Выберите действие:", 0.02)
        print("═" * 40)
        print("1. 🎨 Сделать ставку на цвет")
        print("2. 🔢 Сделать ставку на число")
        print("3. 🔄 Сделать ставку на чет/нечет")
        print("4. 💰 Проверить баланс")
        print("5. 🚪 Выйти")
        print("═" * 40)

        choice = input("🎯 Ваш выбор (1-5): ")

        if choice == '1':
            color = input("🎨 Выберите цвет (красный/черный): ").lower()
            if color in ['красный', 'черный']:
                try:
                    amount = int(input("💵 Сумма ставки: "))
                    simulator.simple_betting(amount, 'цвет', color)
                except ValueError:
                    simulator.animate_text("❌ Введите корректную сумму!", 0.01)
            else:
                simulator.animate_text("❌ Неверный выбор цвета!", 0.01)

        elif choice == '2':
            number = input("🔢 Выберите число (0-36): ")
            if number.isdigit() and 0 <= int(number) <= 36:
                try:
                    amount = int(input("💵 Сумма ставки: "))
                    simulator.simple_betting(amount, 'число', number)
                except ValueError:
                    simulator.animate_text("❌ Введите корректную сумму!", 0.01)
            else:
                simulator.animate_text("❌ Неверный номер! Выберите от 0 до 36", 0.01)

        elif choice == '3':
            eo = input("🔄 Выберите (чет/нечет): ").lower()
            if eo in ['чет', 'нечет']:
                try:
                    amount = int(input("💵 Сумма ставки: "))
                    simulator.simple_betting(amount, 'чет/нечет', eo)
                except ValueError:
                    simulator.animate_text("❌ Введите корректную сумму!", 0.01)
            else:
                simulator.animate_text("❌ Неверный выбор! Выберите 'чет' или 'нечет'", 0.01)

        elif choice == '4':
            print(f"💰 Текущий баланс: {simulator.format_money(simulator.balance)}")
            time.sleep(1)

        elif choice == '5':
            simulator.animate_text("👋 До свидания! Спасибо за игру!", 0.03)
            break

        else:
            simulator.animate_text("❌ Неверный выбор! Выберите от 1 до 5", 0.01)

        # Проверяем, остались ли деньги
        if simulator.balance < simulator.min_bet:
            print("\n" + "💸" * 20)
            simulator.animate_text("💸 У вас недостаточно средств для дальнейшей игры!", 0.03)
            print("💸" * 20)
            break

        time.sleep(1)

    simulator.display_stats()

    print("\n" + "⭐" * 30)
    if simulator.balance > 1000:  # Изменено на новый начальный баланс
        simulator.animate_text("🎉 Поздравляем! Вы в плюсе! 🎉", 0.03)
    elif simulator.balance == 1000:  # Изменено на новый начальный баланс
        simulator.animate_text("➖ Вы остались при своих! ➖", 0.03)
    else:
        simulator.animate_text("💸 К сожалению, вы в минусе. Удачи в следующий раз! 💸", 0.03)
    print("⭐" * 30)


if __name__ == "__main__":
    main()