import random
import time

class SovietFinnishWarGame:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.difficulties = {
            "легкий": {"soviet_strength": 50, "finnish_strength": 30, "finnish_stealth": 2},
            "нормальный": {"soviet_strength": 70, "finnish_strength": 50, "finnish_stealth": 3},
            "сложный": {"soviet_strength": 100, "finnish_strength": 70, "finnish_stealth": 4},
            "talvisota": {"soviet_strength": 150, "finnish_strength": 100, "finnish_stealth": 6}
        }
        
        self.stats = self.difficulties[difficulty].copy()
        self.soviet_morale = 100
        self.finnish_morale = 100
        self.temperature = -30  # Типичная температура зимой 1939-40
        self.day = 1
        self.position = "линия Маннергейма"
        
    def weather_effects(self):
        """Эффекты погоды и температуры"""
        if random.random() < 0.3:
            temp_change = random.randint(-10, -5)
            self.temperature += temp_change
            print(f"❄️  Похолодало! Температура: {self.temperature}°C")
            
            # Потери от обморожения
            if self.temperature < -25:
                cold_casualties = random.randint(1, 5)
                self.stats["soviet_strength"] -= cold_casualties
                print(f"☃️  Потери от обморожения: {cold_casualties} бойцов")
        
        # Снегопад влияет на видимость
        if random.random() < 0.4:
            print("🌨️  Снегопад уменьшает видимость!")
            return True  # Пониженная видимость
        return False
    
    def finnish_ambush(self, poor_visibility=False):
        """Атака финских лыжников-снайперов"""
        if self.difficulty == "talvisota":
            ambush_chance = 0.8  # 80% шанс атаки на максимальной сложности
        else:
            ambush_chance = 0.3 + (self.difficulties[self.difficulty]["finnish_stealth"] * 0.1)
        
        if poor_visibility:
            ambush_chance += 0.2
        
        if random.random() < ambush_chance:
            print("\n⚠️  АТАКА ИЗ ЗАСАДЫ!")
            print("Финские лыжники-снайперы атакуют с флангов!")
            
            casualties = random.randint(3, 8) * self.difficulties[self.difficulty]["finnish_stealth"]
            self.stats["soviet_strength"] -= casualties
            self.soviet_morale -= 10
            
            print(f"💀 Потери: {casualties} бойцов")
            print(f"📉 Мораль упала до {self.soviet_morale}%")
            return True
        return False
    
    def player_turn(self):
        """Ход игрока (советский командир)"""
        print(f"\n=== День {self.day} | Позиция: {self.position} ===")
        print(f"❄️  Температура: {self.temperature}°C")
        print(f"🎯 Ваши силы: {self.stats['soviet_strength']} бойцов")
        print(f"⚔️  Финские силы: ~{self.stats['finnish_strength']} бойцов")
        print(f"💪 Мораль: {self.soviet_morale}%")
        
        poor_visibility = self.weather_effects()
        
        print("\nДоступные действия:")
        print("1 - Штурмовать укрепления")
        print("2 - Обороняться на позициях") 
        print("3 - Разведка боем")
        print("4 - Отступить на резервные позиции")
        print("5 - Запросить артподдержку")
        
        choice = input("Ваш приказ: ")
        
        if choice == "1":
            return self.assault(poor_visibility)
        elif choice == "2":
            return self.defend(poor_visibility)
        elif choice == "3":
            return self.reconnaissance(poor_visibility)
        elif choice == "4":
            return self.retreat()
        elif choice == "5":
            return self.artillery_support()
        else:
            print("Неверная команда! Потеря времени...")
            return False
    
    def assault(self, poor_visibility):
        """Штурм финских позиций"""
        print("\n🎯 ПРИКАЗ: ШТУРМ!")
        
        # Финны всегда готовы к обороне
        if self.finnish_ambush(poor_visibility):
            return False
        
        success_chance = 0.4 - (0.1 * self.difficulties[self.difficulty]["finnish_stealth"])
        if poor_visibility:
            success_chance -= 0.1
        
        if random.random() < success_chance:
            # Успешный штурм
            soviet_losses = random.randint(10, 20)
            finnish_losses = random.randint(15, 25)
            
            self.stats["soviet_strength"] -= soviet_losses
            self.stats["finnish_strength"] -= finnish_losses
            self.soviet_morale += 5
            
            print(f"✅ Прорыв! Захвачена новая позиция!")
            print(f"💀 Ваши потери: {soviet_losses}")
            print(f"⚔️  Потери противника: {finnish_losses}")
            return True
        else:
            # Неудачный штурм
            losses = random.randint(15, 30)
            self.stats["soviet_strength"] -= losses
            self.soviet_morale -= 15
            print(f"❌ Штурм отбит! Потери: {losses} бойцов")
            return False
    
    def defend(self, poor_visibility):
        """Оборона на текущих позициях"""
        print("\n🛡️  ПРИКАЗ: ОБОРОНА!")
        
        # Меньший шанс засады при обороне
        if random.random() < 0.5 and self.finnish_ambush(poor_visibility):
            return False
        
        # Финны атакуют при обороне
        if random.random() < 0.6:
            print("⚔️  Финны переходят в контратаку!")
            losses = random.randint(5, 15)
            self.stats["soviet_strength"] -= losses
            self.soviet_morale -= 5
            print(f"💀 Потери при отражении атаки: {losses}")
        else:
            print("✅ Оборона успешна! Потерь нет.")
            self.soviet_morale += 3
        
        return True
    
    def game_over_check(self):
        """Проверка условий окончания игры"""
        if self.stats["soviet_strength"] <= 0:
            print("\n💀 ВАШ ОТРЯД УНИЧТОЖЕН!")
            print("Игра окончена. Финны победили.")
            return True
        
        if self.soviet_morale <= 0:
            print("\n😞 ВОЙСКА ДЕМОРАЛИЗОВАНЫ!")
            print("Солдаты отказываются воевать. Поражение.")
            return True
        
        if self.stats["finnish_strength"] <= 0:
            print("\n🎉 ПОБЕДА! Линия Маннергейма прорвана!")
            print(f"Вы победили на сложности: {self.difficulty}")
            return True
        
        if self.day >= 30:
            print("\n⏰ ВРЕМЯ ВЫШЛО! Зимняя война завершается.")
            print("Мирный договор подписан.")
            return True
        
        return False

def main():
    print("=== ЗИМНЯЯ ВОЙНА 1939-1940 ===")
    print("Вы - командир советской дивизии")
    print("Прорвите линию Маннергейма!")
    print("\nУровни сложности:")
    print("1 - Легкий (учебная операция)")
    print("2 - Нормальный (исторический баланс)") 
    print("3 - Сложный (реалистичный)")
    print("4 - TALVISOTA (кошмарный режим)")
    
    difficulty_map = {
        "1": "легкий", "2": "нормальный", 
        "3": "сложный", "4": "talvisota"
    }
    
    choice = input("Выберите сложность (1-4): ")
    difficulty = difficulty_map.get(choice, "нормальный")
    
    if difficulty == "talvisota":
        print("\n⚡ ВКЛЮЧЕН РЕЖИМ TALVISOTA!")
        print("💀 Финны за каждым деревом! 💀")
        print("❄️  Удачи, товарищ командир! ❄️")
        time.sleep(2)
    
    game = SovietFinnishWarGame(difficulty)
    
    # Основной игровой цикл
    while not game.game_over_check():
        game.player_turn()
        game.day += 1
        
        # На высокой сложности финны усиливаются со временем
        if game.difficulty == "talvisota" and game.day % 5 == 0:
            reinforcements = random.randint(10, 20)
            game.stats["finnish_strength"] += reinforcements
            print(f"\n⚠️  Финны получили подкрепление: +{reinforcements} бойцов")

if __name__ == "__main__":
    main()