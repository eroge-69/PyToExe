import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import random
from math import sqrt


class Country:
    def __init__(self, name, x, y, economy, military, relations=0, population=50000, territory=500000):
        self.name = name
        self.x = x
        self.y = y
        self.economy = economy
        self.military = military
        self.relations = relations  # -100 to 100
        self.at_war = False
        self.alliance = False
        self.population = population
        self.territory = territory
        self.ideology = "Нейтралитет"
        self.religion = random.choice(["Христианство", "Ислам", "Атеизм"])
        self.war_support = 30
        self.intimidation_level = 0  # Уровень запугивания (для фашизма)


class AdvisorGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Дипломатическая Игра: Советник")
        self.root.geometry("1200x800")

        # Запрос названия страны и валюты у игрока
        self.country_name = simpledialog.askstring("Название страны", "Введите название вашей страны:",
                                                   initialvalue="Моя Империя")
        if not self.country_name:
            self.country_name = "Моя Империя"

        self.currency_name = simpledialog.askstring("Название валюты", "Введите название вашей валюты:",
                                                    initialvalue="кредиты")
        if not self.currency_name:
            self.currency_name = "кредиты"

        # Параметры государства игрока
        self.gold = 1000
        self.stability = 75
        self.influence = 50
        self.military = 30
        self.technology = 20
        self.population = 50000
        self.territory = 500000
        self.ideology = "Нейтралитет"
        self.religion = "Христианство"
        self.war_support = 30
        self.borders_closed = False
        self.intimidation_power = 0  # Сила запугивания (для фашизма)

        # Список стран
        self.countries = self.generate_countries()
        self.player_country = self.countries[0]  # Первая страна - игрок
        self.player_country.name = self.country_name

        # Создание элементов интерфейса
        self.create_widgets()

        # Первый доклад
        self.report("Ваше Величество, я ваш советник. Страна ждет ваших решений.")
        self.report(
            f"Казна: {self.gold} {self.currency_name}. Стабильность: {self.stability}%. Влияние: {self.influence}.")
        self.report("Введите 'помощь' для списка команд.")

        # Запуск периодических событий
        self.periodic_events()

        # Обновление информации о стране
        self.update_country_info()

    def generate_countries(self):
        # Список из 100 реальных и вымышленных стран
        country_names = [
            "Россия", "Китай", "США", "Германия", "Франция", "Великобритания", "Япония", "Индия", "Бразилия", "Канада",
            "Австралия", "Италия", "Испания", "Мексика", "Южная Корея", "Индонезия", "Турция", "Саудовская Аравия",
            "Швейцария", "Швеция",
            "Норвегия", "Польша", "Нидерланды", "Бельгия", "Греция", "Португалия", "Финляндия", "Дания", "Чехия",
            "Румыния",
            "Венгрия", "Украина", "Казахстан", "Беларусь", "Азербайджан", "Армения", "Грузия", "Узбекистан",
            "Туркменистан", "Киргизия",
            "Таджикистан", "Молдова", "Латвия", "Литва", "Эстония", "Болгария", "Сербия", "Хорватия", "Словакия",
            "Словения",
            "Албания", "Македония", "Черногория", "Босния", "Косово", "Кипр", "Мальта", "Ирландия", "Исландия",
            "Люксембург",
            "Монако", "Андорра", "Лихтенштейн", "Сан-Марино", "Ватикан", "Египет", "ЮАР", "Нигерия", "Кения", "Эфиопия",
            "Марокко", "Тунис", "Алжир", "Ливия", "Судан", "Ангола", "Гана", "Камерун", "Кот-д'Ивуар", "Сенегал",
            "Танзания", "Замбия", "Зимбабве", "Уганда", "Мозамбик", "Мадагаскар", "Намибия", "Ботсвана", "Маврикий",
            "Сейшелы",
            "Аргентина", "Чили", "Колумбия", "Перу", "Венесуэла", "Эквадор", "Куба", "Ямайка", "Багамы", "Доминикана"
        ]

        # Выбираем 10 случайных стран
        selected_names = random.sample(country_names, 10)
        countries = []

        # Первая страна - игрок
        countries.append(Country("Моя Империя", 500, 350, 50, 30, 0, 50000, 500000))

        # Генерируем остальные 9 стран
        for i, name in enumerate(selected_names[1:], 1):
            x = random.randint(100, 900)
            y = random.randint(100, 600)
            economy = random.randint(20, 80)
            military = random.randint(10, 70)
            relations = random.randint(-50, 50)
            population = random.randint(30000, 100000)
            territory = random.randint(200000, 1000000)
            countries.append(Country(name, x, y, economy, military, relations, population, territory))

        return countries

    def create_widgets(self):
        # Фрейм для информации о стране
        info_frame = tk.Frame(self.root)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Название страны
        self.country_label = tk.Label(info_frame, text=f"{self.country_name}", font=('Arial', 16, 'bold'))
        self.country_label.pack(side=tk.LEFT)

        # Валюта
        self.currency_label = tk.Label(info_frame, text=f"Валюта: {self.currency_name}", font=('Arial', 12))
        self.currency_label.pack(side=tk.LEFT, padx=20)

        # Идеология
        self.ideology_label = tk.Label(info_frame, text=f"Идеология: {self.ideology}", font=('Arial', 12))
        self.ideology_label.pack(side=tk.LEFT, padx=20)

        # Религия
        self.religion_label = tk.Label(info_frame, text=f"Религия: {self.religion}", font=('Arial', 12))
        self.religion_label.pack(side=tk.LEFT, padx=20)

        # Основной фрейм для контента
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для карты
        map_frame = tk.Frame(content_frame)
        map_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Холст для карты
        self.canvas = tk.Canvas(map_frame, width=600, height=500, bg="lightblue")
        self.canvas.pack()

        # Фрейм для кнопок идеологий
        ideology_frame = tk.Frame(map_frame)
        ideology_frame.pack(fill=tk.X, pady=5)

        tk.Label(ideology_frame, text="Выбрать идеологию:", font=('Arial', 10)).pack(side=tk.LEFT)

        ideology_btn_frame = tk.Frame(ideology_frame)
        ideology_btn_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(ideology_btn_frame, text="Фашизм", command=lambda: self.set_ideology("Фашизм")).pack(side=tk.LEFT,
                                                                                                       padx=2)
        tk.Button(ideology_btn_frame, text="Коммунизм", command=lambda: self.set_ideology("Коммунизм")).pack(
            side=tk.LEFT, padx=2)
        tk.Button(ideology_btn_frame, text="Нейтралитет", command=lambda: self.set_ideology("Нейтралитет")).pack(
            side=tk.LEFT, padx=2)
        tk.Button(ideology_btn_frame, text="Демократия", command=lambda: self.set_ideology("Демократия")).pack(
            side=tk.LEFT, padx=2)

        # Фрейм для кнопок религий
        religion_frame = tk.Frame(map_frame)
        religion_frame.pack(fill=tk.X, pady=5)

        tk.Label(religion_frame, text="Выбрать религию:", font=('Arial', 10)).pack(side=tk.LEFT)

        religion_btn_frame = tk.Frame(religion_frame)
        religion_btn_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(religion_btn_frame, text="Христианство", command=lambda: self.set_religion("Христианство")).pack(
            side=tk.LEFT, padx=2)
        tk.Button(religion_btn_frame, text="Ислам", command=lambda: self.set_religion("Ислам")).pack(side=tk.LEFT,
                                                                                                     padx=2)
        tk.Button(religion_btn_frame, text="Атеизм", command=lambda: self.set_religion("Атеизм")).pack(side=tk.LEFT,
                                                                                                       padx=2)

        # Кнопка для закрытия/открытия границ
        self.borders_btn = tk.Button(map_frame, text="Закрыть границы", command=self.toggle_borders)
        self.borders_btn.pack(pady=5)

        # Фрейм для управления
        control_frame = tk.Frame(content_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Поле для ввода команд
        self.entry = tk.Entry(control_frame, width=30, font=('Arial', 12))
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.process_command)

        # Кнопка отправки
        self.button = tk.Button(control_frame, text="Отправить", command=self.process_command)
        self.button.pack(pady=5)

        # Поле для вывода докладов
        self.report_area = scrolledtext.ScrolledText(control_frame, width=50, height=20, font=('Arial', 12))
        self.report_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.report_area.config(state=tk.DISABLED)

        # Кнопка для отображения карты
        self.map_button = tk.Button(control_frame, text="Обновить карту", command=self.draw_map)
        self.map_button.pack(pady=5)

        # Отрисовываем карту
        self.draw_map()

    def draw_map(self):
        self.canvas.delete("all")

        # Рисуем страны
        for country in self.countries:
            color = "green"
            if country == self.player_country:
                color = "blue"
            elif country.at_war:
                color = "red"
            elif country.alliance:
                color = "yellow"

            # Размер страны зависит от территории
            size = 10 + (country.territory / 500000) * 5
            self.canvas.create_oval(country.x - size, country.y - size, country.x + size, country.y + size, fill=color,
                                    outline="black")
            self.canvas.create_text(country.x, country.y - size - 15, text=country.name, font=("Arial", 8))

            # Показываем отношения с игроком
            if country != self.player_country:
                rel_text = f"{country.relations}"
                rel_color = "green" if country.relations >= 0 else "red"
                self.canvas.create_text(country.x, country.y + size + 15, text=rel_text, font=("Arial", 8),
                                        fill=rel_color)

                # Показываем уровень запугивания для фашизма
                if self.ideology == "Фашизм" and country.intimidation_level > 0:
                    intimidation_text = f"Запугание: {country.intimidation_level}%"
                    self.canvas.create_text(country.x, country.y + size + 30, text=intimidation_text, font=("Arial", 8),
                                            fill="purple")

    def update_country_info(self):
        """Обновление информации о стране в верхней части интерфейса"""
        self.country_label.config(text=f"{self.country_name}")
        self.currency_label.config(text=f"Валюта: {self.currency_name}")
        self.ideology_label.config(text=f"Идеология: {self.ideology}")
        self.religion_label.config(text=f"Религия: {self.religion}")

        # Обновляем текст кнопки границ
        border_text = "Открыть границы" if self.borders_closed else "Закрыть границы"
        self.borders_btn.config(text=border_text)

    def set_ideology(self, ideology):
        """Установка идеологии"""
        if ideology == self.ideology:
            return

        self.ideology = ideology
        self.update_country_info()

        # Эффекты от смены идеологии
        if ideology == "Фашизм":
            self.stability -= 20
            self.war_support += 40
            self.intimidation_power = 10
            self.report(
                "Вы выбрали фашизм. Стабильность снизилась, но поддержка войны возросла. Теперь вы можете запугивать другие страны.")
        elif ideology == "Коммунизм":
            self.stability -= 10
            self.war_support = 100
            self.report("Вы выбрали коммунизм. Поддержка войны максимальна, но стабильность снизилась.")
        elif ideology == "Нейтралитет":
            self.stability += 15
            self.war_support = 30
            self.report("Вы выбрали нейтралитет. Стабильность возросла, но вы не можете объявлять войны.")
        elif ideology == "Демократия":
            self.stability = 80
            self.war_support = 25
            self.report(
                "Вы выбрали демократию. Стабильность высока, но поддержка войны низкая. Вы можете объявлять войны только в составе союзов.")

    def set_religion(self, religion):
        """Установка религии"""
        if religion == self.religion:
            return

        old_religion = self.religion
        self.religion = religion
        self.update_country_info()

        # Эффекты от смены религии
        if old_religion == "Ислам" and religion != "Ислам":
            self.war_support -= 15  # Убираем бонус ислама
        elif old_religion == "Христианство" and religion != "Христианство":
            pass  # Бонус к налогам применяется при сборе, поэтому не нужно убирать здесь

        if religion == "Ислам":
            self.war_support += 15
            self.report("Вы приняли ислам. Поддержка войны увеличилась на 15%.")
        elif religion == "Христианство":
            self.report("Вы приняли христианство. Теперь вы получаете на 15% больше доходов от налогов.")
        elif religion == "Атеизм":
            self.report("Вы приняли атеизм. Религиозное влияние больше не воздействует на вашу страну.")

    def toggle_borders(self):
        """Закрытие/открытие границ"""
        self.borders_closed = not self.borders_closed

        if self.borders_closed:
            self.stability -= 10
            self.report("Границы закрыты. Стабильность снизилась, но emigration остановлена.")
        else:
            self.report("Границы открыты. Стабильность может восстановиться, но есть риск emigration.")

        self.update_country_info()

    def report(self, message):
        """Добавление сообщения в область отчетов"""
        self.report_area.config(state=tk.NORMAL)
        self.report_area.insert(tk.END, message + "\n\n")
        self.report_area.config(state=tk.DISABLED)
        self.report_area.see(tk.END)

    def process_command(self, event=None):
        """Обработка введенных команд"""
        command = self.entry.get().lower()
        self.entry.delete(0, tk.END)

        # Проверка на проигрыш
        if self.stability < 30:
            messagebox.showerror("Поражение", "В стране восстание! Вы свергнуты.")
            self.root.quit()
            return

        if self.war_support < 5:
            messagebox.showerror("Поражение", "Поддержка войны упала ниже 5%! Вы свергнуты.")
            self.root.quit()
            return

        if self.population < 15000:
            messagebox.showerror("Поражение", "Население упало ниже 15000! Страна нежизнеспособна.")
            self.root.quit()
            return

        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "статус":
            self.report(
                f"Казна: {self.gold} {self.currency_name}\nСтабильность: {self.stability}%\nВлияние: {self.influence}\n"
                f"Армия: {self.military}\nТехнологии: {self.technology}\nНаселение: {self.population}\n"
                f"Территория: {self.territory} км²\nПоддержка войны: {self.war_support}%")
        elif cmd == "налоги":
            income = random.randint(150, 300)

            # Бонус христианства к налогам
            if self.religion == "Христианство":
                income = int(income * 1.15)
                self.report("Бонус христианства: +15% к налогам")

            self.gold += income
            self.stability -= random.randint(1, 5)
            self.report(f"Собрано налогов: {income} {self.currency_name}. Стабильность немного снизилась.")
        elif cmd == "договор" and args:
            country_name = " ".join(args).title()
            country = self.find_country(country_name)
            if country:
                if country.relations < 50:
                    self.report(
                        f"Отношения с {country_name} недостаточно хороши для торгового договора. Нужно минимум 50.")
                    return

                if self.gold >= 300:
                    self.gold -= 300
                    country.relations += random.randint(10, 25)
                    self.influence += 5
                    self.report(f"Заключен торговый договор с {country_name}! Отношения улучшены.")
                else:
                    self.report("Недостаточно золота для дипломатических миссий!")
            else:
                self.report(f"Страна {country_name} не найдена.")
        elif cmd == "война" and args:
            if self.ideology == "Нейтралитет":
                self.report("Вы не можете объявлять войны при нейтралитете.")
                return

            if self.ideology == "Демократия" and not any(
                    c.alliance for c in self.countries if c != self.player_country):
                self.report("Вы не можете объявлять войны при демократии без союзников.")
                return

            country_name = " ".join(args).title()
            country = self.find_country(country_name)
            if country:
                # Автоматическое объявление войны при очень плохих отношениях
                if country.relations < 5 and not country.at_war:
                    self.report(f"{country_name} объявляет вам войну из-за плохих отношений!")
                    country.at_war = True
                    self.war_support += 10
                    return

                if self.military > country.military * 1.2:
                    victory_chance = 0.7
                elif self.military > country.military:
                    victory_chance = 0.5
                else:
                    victory_chance = 0.3

                if random.random() < victory_chance:
                    loot = random.randint(500, 1500)
                    self.gold += loot
                    self.stability -= random.randint(5, 15)
                    self.war_support += random.randint(5, 15)
                    country.relations -= random.randint(30, 50)
                    country.at_war = True
                    self.report(
                        f"Победа над {country_name}! Добыча: {loot} {self.currency_name}. Стабильность снизилась, но поддержка войны возросла.")
                else:
                    losses = random.randint(200, 500)
                    self.gold -= losses
                    self.military -= random.randint(5, 15)
                    self.stability -= random.randint(10, 20)
                    self.war_support -= random.randint(5, 10)
                    country.relations -= random.randint(20, 40)
                    self.report(
                        f"Поражение в войне с {country_name}! Потери: {losses} {self.currency_name}. Армия, стабильность и поддержка войны снизились.")
            else:
                self.report(f"Страна {country_name} не найдена.")
        elif cmd == "союз" and args:
            country_name = " ".join(args).title()
            country = self.find_country(country_name)
            if country:
                if country.relations < 85:
                    self.report(f"Отношения с {country_name} недостаточно хороши для союза. Нужно минимум 85.")
                    return

                if country.relations > 50:
                    cost = random.randint(400, 800)
                    if self.gold >= cost:
                        self.gold -= cost
                        country.alliance = True
                        self.influence += 10
                        self.report(
                            f"Заключен военный союз с {country_name}! Стоимость: {cost} {self.currency_name}. Влияние увеличено.")
                    else:
                        self.report(f"Недостаточно золота для заключения союза. Нужно {cost} {self.currency_name}.")
                else:
                    self.report(f"Отношения с {country_name} недостаточно хороши для союза. Нужно более 50.")
            else:
                self.report(f"Страна {country_name} не найдена.")
        elif cmd == "помощь":
            self.report("Доступные команды:\n"
                        "- статус: показать параметры\n"
                        "- налоги: собрать налоги\n"
                        "- договор [страна]: заключить торговый договор (300 {self.currency_name})\n"
                        "- война [страна]: объявить войну\n"
                        "- союз [страна]: заключить военный союз\n"
                        "- развить армия/технологии: улучшить параметры\n"
                        "- запугать [страна]: запугать страну (только для фашизма)\n"
                        "- присоединить [страна]: присоединить страну (только для фашизма)\n"
                        "- страны: список всех стран\n"
                        "- отношения [страна]: узнать отношения")
        elif cmd == "развить" and args:
            if args[0] == "армия":
                cost = self.military * 10
                if self.gold >= cost:
                    self.gold -= cost
                    self.military += random.randint(5, 10)
                    self.report(
                        f"Армия улучшена! Стоимость: {cost} {self.currency_name}. Текущая сила армии: {self.military}.")
                else:
                    self.report(f"Недостаточно {self.currency_name}. Нужно {cost} {self.currency_name}.")
            elif args[0] == "технологии":
                cost = self.technology * 15
                if self.gold >= cost:
                    self.gold -= cost
                    self.technology += random.randint(3, 7)
                    self.report(
                        f"Технологии улучшены! Стоимость: {cost} {self.currency_name}. Текущий уровень: {self.technology}.")
                else:
                    self.report(f"Недостаточно {self.currency_name}. Нужно {cost} {self.currency_name}.")
        elif cmd == "запугать" and args:
            if self.ideology != "Фашизм":
                self.report("Запугивание доступно только при фашистской идеологии.")
                return

            country_name = " ".join(args).title()
            country = self.find_country(country_name)
            if country:
                if self.military > country.military:
                    intimidation = random.randint(10, 25) + self.intimidation_power
                    country.intimidation_level += intimidation
                    self.report(
                        f"{country_name} запугана на {intimidation}%. Текущий уровень запугивания: {country.intimidation_level}%.")
                else:
                    self.report(f"Вы недостаточно сильны, чтобы запугивать {country_name}.")
            else:
                self.report(f"Страна {country_name} не найдена.")
        elif cmd == "присоединить" and args:
            if self.ideology != "Фашизм":
                self.report("Присоединение доступно только при фашистской идеологии.")
                return

            country_name = " ".join(args).title()
            country = self.find_country(country_name)
            if country:
                if country.intimidation_level > 70 and self.influence > 65:
                    # Присоединение страны
                    self.gold += country.economy * 100  # Захват экономики
                    self.territory += country.territory
                    self.stability -= 20
                    self.war_support = 100
                    self.countries.remove(country)
                    self.report(
                        f"{country_name} присоединена к вашей империи! Получено {country.economy * 100} {self.currency_name}. Территория увеличена на {country.territory} км². Стабильность снизилась, но поддержка войны максимальна.")
                else:
                    self.report(
                        f"Не удается присоединить {country_name}. Нужно запугать более чем на 70% и иметь влияние более 65%.")
            else:
                self.report(f"Страна {country_name} не найдена.")
        elif cmd == "страны":
            country_list = "\n".join(
                [f"{c.name} (Отношения: {c.relations}, Запугание: {c.intimidation_level}%)" for c in self.countries if
                 c != self.player_country])
            self.report("Список стран:\n" + country_list)
        elif cmd == "отношения" and args:
            country_name = " ".join(args).title()
            country = self.find_country(country_name)
            if country:
                status = "Союзник" if country.alliance else "Вражда" if country.at_war else "Нейтральные"
                self.report(f"Отношения с {country_name}: {country.relations} ({status})")
            else:
                self.report(f"Страна {country_name} не найдена.")
        else:
            self.report("Неизвестная команда. Введите 'помощь' для списка команд.")

        # Обновляем карту после команды
        self.draw_map()

    def find_country(self, name):
        for country in self.countries:
            if country.name.lower() == name.lower():
                return country
        return None

    def periodic_events(self):
        """Периодические события в игре"""
        # Случайные события
        if random.random() < 0.2:  # 20% шанс события
            event_type = random.choice(["кризис", "бунт", "открытие", "союз_предложение"])

            if event_type == "кризис":
                crisis_type = random.choice(["экономический", "политический", "природный"])
                if crisis_type == "экономический":
                    loss = random.randint(100, 300)
                    self.gold -= loss
                    self.report(f"Экономический кризис! Потеряно {loss} {self.currency_name}.")
                elif crisis_type == "политический":
                    loss = random.randint(5, 15)
                    self.stability -= loss
                    self.report(f"Политический кризис! Стабильность снизилась на {loss}%.")
                else:
                    loss = random.randint(10, 20)
                    self.stability -= loss
                    self.report(f"Природный катаклизм! Стабильность снизилась на {loss}%.")

            elif event_type == "бунт":
                loss = random.randint(5, 10)
                self.stability -= loss
                self.report(f"Бунт в провинции! Стабильность снизилась на {loss}%.")

            elif event_type == "открытие":
                gain = random.randint(200, 500)
                self.gold += gain
                self.report(f"Научное открытие! Получено {gain} {self.currency_name}.")

            elif event_type == "союз_предложение":
                country = random.choice([c for c in self.countries if c != self.player_country and not c.alliance])
                if country and country.relations > 30:
                    country.alliance = True
                    self.report(f"{country.name} предлагает военный союз! Союз заключен.")

        # Эмиграция населения при низкой стабильности
        if not self.borders_closed and self.stability < 50:
            emigration = random.randint(100, 500)
            self.population -= emigration
            self.report(f"Из-за низкой стабильности {emigration} человек эмигрировало из страны.")

        # Бонус к доходу от территории
        if random.random() < 0.1:  # 10% шанс на дополнительный доход
            territory_bonus = int(self.territory / 100000)
            self.gold += territory_bonus
            self.report(f"Бонус от территории: +{territory_bonus} {self.currency_name}.")

        # Штраф к стабильности от большой территории
        if self.territory > 1000000 and random.random() < 0.15:
            stability_penalty = int(self.territory / 500000)
            self.stability -= stability_penalty
            self.report(f"Управление большой территорией сложно! Стабильность снизилась на {stability_penalty}%.")

        # Проверка на проигрыш
        if self.stability < 30:
            messagebox.showerror("Поражение", "В стране восстание! Вы свергнуты.")
            self.root.quit()
            return

        if self.war_support < 5:
            messagebox.showerror("Поражение", "Поддержка войны упала ниже 5%! Вы свергнуты.")
            self.root.quit()
            return

        if self.population < 15000:
            messagebox.showerror("Поражение", "Население упало ниже 15000! Страна нежизнеспособна.")
            self.root.quit()
            return

        # Планируем следующее событие
        self.root.after(30000, self.periodic_events)  # Событие каждые 30 секунд


if __name__ == "__main__":
    root = tk.Tk()
    game = AdvisorGame(root)
    root.mainloop()