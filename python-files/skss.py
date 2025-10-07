import customtkinter as ctk
from tkinter import messagebox
import random

class HicomInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HiPath4000")
        self.geometry("800x690")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.bg_color = "#f0f0f0"
        self.frame_color = "#ffffff"
        self.text_color = "#000000"
        self.accent_color = "#0078d7"
        self.configure(fg_color=self.bg_color)
        self.create_main_widgets()

    def create_main_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(
            self,
            fg_color=self.frame_color,
            corner_radius=10
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text="HiPath4000",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.text_color
        )
        title_label.pack(pady=(10, 5))

        algorithm_label = ctk.CTkLabel(
            main_frame,
            text="Выберите алгоритм:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.text_color
        )
        algorithm_label.pack(anchor="w", padx=50, pady=(0, 5))

        algorithm_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.frame_color,
            border_width=2,
            border_color=self.accent_color,
            corner_radius=5
        )
        algorithm_frame.pack(fill="x", padx=50, pady=(0, 15))

        algorithms = [
            "Учетная запись",
            "Подключение АТА и ЦТА",
            "Перенос ТА на другой PEN",
            "Дополнительный ЦТА через адаптер",
            "КЕY- и BLF- модули",
            "Раскладки",
            "Задание функций ДВО для клавиш",
            "Создание групп (перехват вызова)",
            "Группа поиска",
            "Группа руководитель-секретарь"
        ]

        self.selected_algorithm = ctk.StringVar(value="")
        for i, algorithm in enumerate(algorithms):
            radio_btn = ctk.CTkRadioButton(
                algorithm_frame,
                text=algorithm,
                variable=self.selected_algorithm,
                value=algorithm,
                font=ctk.CTkFont(size=14),
                text_color=self.text_color,
                fg_color=self.accent_color,
                hover_color=self.accent_color
            )
            radio_btn.pack(anchor="w", padx=15, pady=8)

        difficulty_label = ctk.CTkLabel(
            main_frame,
            text="Выберите сложность:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.text_color
        )
        difficulty_label.pack(anchor="w", padx=50, pady=(0, 10))

        difficulty_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.frame_color,
            border_width=2,
            border_color=self.accent_color,
            corner_radius=5
        )
        difficulty_frame.pack(fill="x", padx=50, pady=(0, 20))

        difficulty_buttons_frame = ctk.CTkFrame(
            difficulty_frame,
            fg_color=self.frame_color
        )
        difficulty_buttons_frame.pack(padx=10, pady=10)

        self.selected_difficulty = ctk.StringVar(value="")
        difficulties = ["Базовая", "Продвинутая"]
        for i, difficulty in enumerate(difficulties):
            radio_btn = ctk.CTkRadioButton(
                difficulty_buttons_frame,
                text=difficulty,
                variable=self.selected_difficulty,
                value=difficulty,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.text_color,
                fg_color=self.accent_color,
                hover_color=self.accent_color,
                corner_radius=8
            )
            if i == 0:
                radio_btn.pack(side="left", padx=(0, 20))
            else:
                radio_btn.pack(side="left")

        confirm_button = ctk.CTkButton(
            main_frame,
            text="Подтвердить выбор",
            command=self.open_task_window,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color=self.accent_color,
            hover_color="#005a9e",
            text_color="white",
            corner_radius=8
        )
        confirm_button.pack(pady=(0, 20))

    def open_task_window(self):
        algorithm = self.selected_algorithm.get()
        difficulty = self.selected_difficulty.get()

        if not algorithm:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите алгоритм!")
            return
        if not difficulty:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите сложность!")
            return

        self.withdraw()
        TaskWindow(self, algorithm, difficulty)

class TaskWindow(ctk.CTkToplevel):
    def __init__(self, parent, algorithm, difficulty):
        super().__init__(parent)
        self.title(f"{algorithm}")
        self.geometry("800x690")
        self.resizable(False, False)
        self.bg_color = "#f0f0f0"
        self.frame_color = "#ffffff"
        self.text_color = "#000000"
        self.accent_color = "#0078d7"
        self.configure(fg_color=self.bg_color)
        self.parent = parent
        self.algorithm = algorithm
        self.difficulty = difficulty
        self.create_task_widgets(algorithm, difficulty)

    def create_task_widgets(self, algorithm, difficulty):
        main_frame = ctk.CTkFrame(
            self,
            fg_color=self.frame_color,
            corner_radius=10
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=5)

        back_button = ctk.CTkButton(
            top_frame,
            text="←",
            command=self.back_to_main,
            font=ctk.CTkFont(size=20, weight="bold"),
            width=50,
            height=50,
            fg_color=self.accent_color,
            hover_color="#005a9e",
            text_color="white",
            corner_radius=25
        )
        back_button.pack(side="left", padx=(10, 0), pady=(10, 0))

        title_label = ctk.CTkLabel(
            top_frame,
            text=algorithm,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.text_color
        )
        title_label.pack(side="left", expand=True, padx=(0, 60))

        if difficulty == "Продвинутая":
            if algorithm == "Учетная запись":
                self.create_knowledge_test_complex(main_frame)
            elif algorithm == "Подключение АТА и ЦТА":
                self.create_ata_cta_test(main_frame)
            elif algorithm == "Перенос ТА на другой PEN":
                self.create_pen_transfer_test(main_frame)
            elif algorithm == "Дополнительный ЦТА через адаптер":
                self.create_additional_cta_test(main_frame)
            elif algorithm == "КЕY- и BLF- модули":
                self.create_key_blf_test(main_frame)
            elif algorithm == "Раскладки":
                self.create_layout_test(main_frame)
            elif algorithm == "Задание функций ДВО для клавиш":
                self.create_dvo_functions_test(main_frame)
            elif algorithm == "Создание групп (перехват вызова)":
                self.create_call_intercept_test(main_frame)
            elif algorithm == "Группа поиска":
                self.create_search_group_test(main_frame)
            elif algorithm == "Группа руководитель-секретарь":
                self.create_boss_secretary_test(main_frame)
        else:  # Простая сложность - везде квиз
            if algorithm == "Учетная запись":
                self.create_account_quiz(main_frame)
            elif algorithm == "Подключение АТА и ЦТА":
                self.create_ata_cta_quiz(main_frame)
            elif algorithm == "Перенос ТА на другой PEN":
                self.create_pen_transfer_quiz(main_frame)
            elif algorithm == "Дополнительный ЦТА через адаптер":
                self.create_additional_cta_quiz(main_frame)
            elif algorithm == "КЕY- и BLF- модули":
                self.create_key_blf_quiz(main_frame)
            elif algorithm == "Раскладки":
                self.create_layout_quiz(main_frame)
            elif algorithm == "Задание функций ДВО для клавиш":
                self.create_dvo_functions_quiz(main_frame)
            elif algorithm == "Создание групп (перехват вызова)":
                self.create_call_intercept_quiz(main_frame)
            elif algorithm == "Группа поиска":
                self.create_search_group_quiz(main_frame)
            elif algorithm == "Группа руководитель-секретарь":
                self.create_boss_secretary_quiz(main_frame)

    # Квиз для Учетной записи - сфокусирован на последовательности
    def create_account_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Какое действие выполняется ПЕРВЫМ при создании учетной записи?",
                "options": [
                    "Открыть ярлык «Connect» на рабочем столе",
                    "Войти под учетной записью root1",
                    "Нажать Ctrl+Tab для открытия редактора пользователей"
                ],
                "correct": 0
            },
            {
                "question": "Что делается сразу после открытия «Connect»?",
                "options": [
                    "Вход в сессию пользователя root1 (пароль: hicom1)",
                    "Создание нового пользователя",
                    "Установка пароля для root1"
                ],
                "correct": 0
            },
            {
                "question": "Как открыть окно редактирования пользователей после входа в систему?",
                "options": [
                    "Нажать сочетание клавиш Ctrl+Tab",
                    "Выбрать пункт меню 'Пользователи'",
                    "Ввести команду ADD-USER"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности задаются параметры безопасности пользователя?",
                "options": [
                    "AUTH → OPT → RETRIES → LOCK TIME",
                    "OPT → AUTH → LOCK TIME → RETRIES",
                    "RETRIES → LOCK TIME → AUTH → OPT"
                ],
                "correct": 0
            },
            {
                "question": "Когда устанавливается пароль для нового пользователя?",
                "options": [
                    "После создания пользователя и задания параметров безопасности",
                    "До создания пользователя",
                    "Пароль устанавливается автоматически"
                ],
                "correct": 0
            },
            {
                "question": "Как проверить создание учетной записи ДО выхода из системы?",
                "options": [
                    "Использовать команду DISPLAY-USER",
                    "Попробовать войти под новой учетной записью",
                    "Перезагрузить систему"
                ],
                "correct": 0
            },
            {
                "question": "Что делается после проверки учетной записи командой DISPLAY-USER?",
                "options": [
                    "Нажать ОТКЛЮЧИТЬ для выхода из сессии",
                    "Сразу создавать следующую учетную запись",
                    "Изменять параметры безопасности"
                ],
                "correct": 0
            },
            {
                "question": "Финальное действие для проверки работоспособности учетной записи:",
                "options": [
                    "Войти в систему под новой учетной записью",
                    "Удалить учетную запись root1",
                    "Создать резервную копию системы"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Подключения АТА и ЦТА - сфокусирован на последовательности
    def create_ata_cta_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "С чего начинается процесс подключения ТА?",
                "options": [
                    "С проверки физической коммутации (кросс-крест) ТА",
                    "С создания номера в плане нумерации",
                    "С присвоения имени ТА"
                ],
                "correct": 0
            },
            {
                "question": "Что делается после физического подключения ТА к портам АТС?",
                "options": [
                    "Проверка цифрового плана станции (DISPLAY-WABE)",
                    "Немедленное присвоение номера",
                    "Настройка функций клавиш"
                ],
                "correct": 0
            },
            {
                "question": "Как определить свободен ли номер для подключения?",
                "options": [
                    "Проверить параметр R в таблице WABE - номер свободы",
                    "Позвонить на номер и проверить",
                    "Посмотреть на индикацию ТА"
                ],
                "correct": 0
            },
            {
                "question": "Что делать если номер отсутствует в плане нумерации?",
                "options": [
                    "Создать номер в плане нумерации",
                    "Использовать любой занятый номер",
                    "Отказаться от подключения ТА"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности настраивается порт для ТА?",
                "options": [
                    "Проверить порт → Присвоить номер → Присвоить имя",
                    "Присвоить имя → Присвоить номер → Проверить порт",
                    "Присвоить номер → Присвоить имя → Проверить порт"
                ],
                "correct": 0
            },
            {
                "question": "Какой порт используется для АТА?",
                "options": [
                    "SCSU",
                    "SBCSU",
                    "Оба варианта верны"
                ],
                "correct": 0
            },
            {
                "question": "Финальный шаг при подключении ТА:",
                "options": [
                    "Проверить номер на экране ТА или программно",
                    "Перезагрузить АТС",
                    "Создать резервную копию конфигурации"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Переноса ТА на другой PEN - сфокусирован на последовательности
    def create_pen_transfer_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Первое действие при переносе ТА на другой порт:",
                "options": [
                    "Резервирование нового порта для переноса",
                    "Отключение старого порта",
                    "Изменение номера ТА"
                ],
                "correct": 0
            },
            {
                "question": "Что делается после резервирования нового порта?",
                "options": [
                    "Отключение ТА от старого порта (CHANGE-DSSU: TYPE=signoff)",
                    "Немедленное подключение к новому порту",
                    "Удаление старого порта"
                ],
                "correct": 0
            },
            {
                "question": "Как выполняется подключение ТА к новому порту?",
                "options": [
                    "CHANGE-DSSU: TYPE=signon с указанием нового PEN",
                    "ADD-DSSU для создания нового порта",
                    "RESTART-DSSU для автоматического переноса"
                ],
                "correct": 0
            },
            {
                "question": "Что делать если после переноса ТА не работает?",
                "options": [
                    "Перезагрузить порт командой RESTART-DSSU",
                    "Вернуть ТА на старый порт",
                    "Удалить ТА и создать заново"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности выполняется перенос?",
                "options": [
                    "Резервирование → Отключение → Подключение → Проверка",
                    "Отключение → Подключение → Резервирование → Проверка",
                    "Подключение → Отключение → Резервирование → Проверка"
                ],
                "correct": 0
            },
            {
                "question": "Какой параметр указывает на физический порт подключения?",
                "options": [
                    "PEN (например, PEN=1-3-71-1)",
                    "STNO (номер станции)",
                    "TYPE (тип подключения)"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Дополнительного ЦТА через адаптер - сфокусирован на последовательности
    def create_additional_cta_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Первое действие при подключении дополнительного ЦТА:",
                "options": [
                    "Подключить адаптер расширения к основному ТА",
                    "Создать новый номер в плане нумерации",
                    "Настроить функции клавиш"
                ],
                "correct": 0
            },
            {
                "question": "Где размещается адаптер расширения?",
                "options": [
                    "В посадочное гнездо с задней стороны основного ТА",
                    "Через USB-порт компьютера",
                    "Независимо от основного ТА"
                ],
                "correct": 0
            },
            {
                "question": "Какая команда добавляет адаптер расширения в систему?",
                "options": [
                    "ADD-SBCSU с параметрами STNO, OPT-OPTIEXP, MAIN0",
                    "CHANGE-TAPRO для настройки функций",
                    "ADD-SCSU для создания нового порта"
                ],
                "correct": 0
            },
            {
                "question": "Что означает параметр MAIN0-7501 в команде добавления адаптера?",
                "options": [
                    "Номер основного ТА, к которому подключен адаптер",
                    "Номер дополнительного ТА",
                    "Тип адаптера расширения"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности подключается дополнительный ЦТА?",
                "options": [
                    "Физическое подключение → Добавление в систему → Настройка параметров",
                    "Добавление в систему → Физическое подключение → Настройка параметров",
                    "Настройка параметров → Физическое подключение → Добавление в систему"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для KEY- и BLF- модулей - сфокусирован на последовательности
    def create_key_blf_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Первое действие при подключении модулей к ТА:",
                "options": [
                    "Определить тип модуля (KEY или BLF)",
                    "Немедленно подключить модуль физически",
                    "Настроить функции клавиш в системе"
                ],
                "correct": 0
            },
            {
                "question": "Чем отличается KEY модуль от BLF модуля?",
                "options": [
                    "KEY - дополнительные клавиши, BLF - индикация занятости",
                    "KEY - для аналоговых ТА, BLF - для цифровых",
                    "Разницы нет, это синонимы"
                ],
                "correct": 0
            },
            {
                "question": "Какая команда настраивает BLF модуль?",
                "options": [
                    "CHANGE-SBCSU с параметром BLF-YES",
                    "ADD-BLF с указанием номера ТА",
                    "SET-MODULE TYPE=BLF"
                ],
                "correct": 0
            },
            {
                "question": "Что означает параметр RFP-Q в настройке модулей?",
                "options": [
                    "Тип модуля (0 - KEY, Q - BLF)",
                    "Номер порта подключения",
                    "Количество клавиш в модуле"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности подключаются модули?",
                "options": [
                    "Определение типа → Физическое подключение → Настройка в системе",
                    "Настройка в системе → Физическое подключение → Определение типа",
                    "Физическое подключение → Определение типа → Настройка в системе"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Раскладок - сфокусирован на последовательности
    def create_layout_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "С чего начинается настройка раскладки клавиш?",
                "options": [
                    "С определения стандарта раскладки клавиатуры ЦТА",
                    "С физического нажатия клавиш на ТА",
                    "С создания новой учетной записи"
                ],
                "correct": 0
            },
            {
                "question": "Какая команда используется для определения стандарта раскладки?",
                "options": [
                    "TAPRO (DISP, TYPE=STD, DIGTYPE=OPENSTAO)",
                    "DISPLAY-KEYBOARD TYPE=STD",
                    "SHOW-LAYOUT ALL"
                ],
                "correct": 0
            },
            {
                "question": "Что делается после определения стандарта раскладки?",
                "options": [
                    "Загрузка стандарта на ЦТА (TAPRO CHANGE)",
                    "Перезагрузка ТА",
                    "Проверка работы клавиш"
                ],
                "correct": 0
            },
            {
                "question": "Как проверить результат загрузки раскладки?",
                "options": [
                    "TAPRO (DISP, TYPE=STN, STNO=номер ЦТА)",
                    "Позвонить на другой ТА",
                    "Нажать все клавиши по очереди"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности настраивается раскладка?",
                "options": [
                    "Определение → Загрузка → Проверка",
                    "Проверка → Определение → Загрузка",
                    "Загрузка → Проверка → Определение"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Задания функций ДВО для клавиш - сфокусирован на последовательности
    def create_dvo_functions_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Что делается перед назначением функций клавишам?",
                "options": [
                    "Загрузка стандарта раскладки на ЦТА",
                    "Физическая маркировка клавиш",
                    "Перезагрузка ТА"
                ],
                "correct": 0
            },
            {
                "question": "Какая команда назначает функцию клавише?",
                "options": [
                    "TAPRO STNO с указанием KYxx-ФУНКЦИЯ",
                    "SET-KEY FUNCTION=...",
                    "ADD-FUNCTION KEY=..."
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности настраиваются функции ДВО?",
                "options": [
                    "Загрузка раскладки → Назначение функций → Настройка адресации",
                    "Настройка адресации → Назначение функций → Загрузка раскладки",
                    "Назначение функций → Загрузка раскладки → Настройка адресации"
                ],
                "correct": 0
            },
            {
                "question": "Что такое ZIEL в контексте настройки функций?",
                "options": [
                    "Направление адресации для функциональных клавиш",
                    "Тип телефонного аппарата",
                    "Модель клавиатуры"
                ],
                "correct": 0
            },
            {
                "question": "Как настроить прямую связь между двумя ТА?",
                "options": [
                    "ADD-ZIEL: TYPE=DSS с указанием исходного и целевого ТА",
                    "TAPRO STNO с параметром DIRECT=YES",
                    "SET-CONNECTION BETWEEN=..."
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Создания групп (перехват вызова) - сфокусирован на последовательности
    def create_call_intercept_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Первое действие при создании группы перехвата вызова:",
                "options": [
                    "Создание группы с номером (ADD-AUNTYR-GR)",
                    "Настройка клавиши PU на ТА",
                    "Добавление ТА в группу"
                ],
                "correct": 0
            },
            {
                "question": "Как добавляются ТА в группу перехвата?",
                "options": [
                    "Через параметр STND с перечислением номеров через &",
                    "Поочередным созданием для каждого ТА",
                    "Автоматически по диапазону номеров"
                ],
                "correct": 0
            },
            {
                "question": "Какая клавиша настраивается для перехвата вызова?",
                "options": [
                    "PU (call pick-up)",
                    "DSS (прямой вызов)",
                    "FWD (переадресация)"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности создается группа перехвата?",
                "options": [
                    "Создание группы → Добавление ТА → Настройка клавиш → Проверка",
                    "Настройка клавиш → Создание группы → Добавление ТА → Проверка",
                    "Добавление ТА → Создание группы → Настройка клавиш → Проверка"
                ],
                "correct": 0
            },
            {
                "question": "Как проверить работу группы перехвата?",
                "options": [
                    "DISPLAY-TAPRO-TYPE-STN для просмотра раскладки",
                    "Позвонить на один ТА и попробовать перехватить с другого",
                    "Оба варианта верны"
                ],
                "correct": 2
            }
        ]
        self.start_quiz()

    # Квиз для Группы поиска - сфокусирован на последовательности
    def create_search_group_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "С чего начинается создание группы поиска?",
                "options": [
                    "Создание кода выхода в плане нумерации (ADD-WABE)",
                    "Добавление ТА в группу",
                    "Настройка параметров поиска"
                ],
                "correct": 0
            },
            {
                "question": "Что означает параметр DAR-HUNT?",
                "options": [
                    "Тип поиска - последовательный обход (hunting)",
                    "Тип группы - динамическая",
                    "Режим работы - автоматический"
                ],
                "correct": 0
            },
            {
                "question": "Как создается сама группа поиска?",
                "options": [
                    "ADD-SA: TYPE-VCE с указанием кода и участников",
                    "CREATE-GROUP TYPE=SEARCH",
                    "ADD-HUNTGROUP с параметрами"
                ],
                "correct": 0
            },
            {
                "question": "Что означает COMAX=3 в настройке группы?",
                "options": [
                    "Максимум 3 одновременных вызова в группе",
                    "3 участника в группе",
                    "3 секунды ожидания ответа"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности создается группа поиска?",
                "options": [
                    "Код выхода → Создание группы → Добавление участников → Настройка параметров",
                    "Создание группы → Код выхода → Добавление участников → Настройка параметров",
                    "Добавление участников → Создание группы → Код выхода → Настройка параметров"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Квиз для Группы руководитель-секретарь - сфокусирован на последовательности
    def create_boss_secretary_quiz(self, main_frame):
        self.quiz_frame = ctk.CTkFrame(main_frame, fg_color=self.frame_color)
        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.original_questions = [
            {
                "question": "Первое действие при создании группы руководитель-секретарь:",
                "options": [
                    "Настройка ТА руководителя и секретаря",
                    "Создание группы (CHANGE-SBCSU: SECR-YES)",
                    "Назначение функциональных клавиш"
                ],
                "correct": 0
            },
            {
                "question": "Какая функция на ТА руководителя отключает перехват секретаря?",
                "options": [
                    "RNGXFER",
                    "DSS",
                    "SPLT"
                ],
                "correct": 0
            },
            {
                "question": "Какая функция на ТА секретаря позволяет переменный разговор?",
                "options": [
                    "SPLT",
                    "DSS",
                    "RNGXFER"
                ],
                "correct": 0
            },
            {
                "question": "Как добавляется секретарь в группу?",
                "options": [
                    "ADD-CHESE: GRNO-Z, EXEC-YYYY, SECR-XXXX",
                    "SET-SECRETARY BOSS=YYYY SECRETARY=XXXX",
                    "ADD-SECRETARY TO=YYYY FROM=XXXX"
                ],
                "correct": 0
            },
            {
                "question": "В какой последовательности создается группа руководитель-секретарь?",
                "options": [
                    "Настройка ТА → Создание группы → Назначение клавиш → Добавление участников",
                    "Создание группы → Настройка ТА → Добавление участников → Назначение клавиш",
                    "Добавление участников → Настройка ТА → Создание группы → Назначение клавиш"
                ],
                "correct": 0
            }
        ]
        self.start_quiz()

    # Общие методы для квиза
    def start_quiz(self):
        self.quiz_questions = []
        for question in self.original_questions:
            options = question["options"].copy()
            correct_answer = options[question["correct"]]
            random.shuffle(options)
            new_correct_index = options.index(correct_answer)
            self.quiz_questions.append({
                "question": question["question"],
                "options": options,
                "correct": new_correct_index
            })

        self.current_question = 0
        self.correct_answers = 0
        self.show_quiz_question()

    def show_quiz_question(self):
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        if self.current_question < len(self.quiz_questions):
            question_data = self.quiz_questions[self.current_question]

            question_label = ctk.CTkLabel(
                self.quiz_frame,
                text=f"Вопрос {self.current_question + 1}/{len(self.quiz_questions)}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.accent_color
            )
            question_label.pack(pady=(20, 10))

            question_text = ctk.CTkLabel(
                self.quiz_frame,
                text=question_data["question"],
                font=ctk.CTkFont(size=16),
                text_color=self.text_color
            )
            question_text.pack(pady=10)

            for i, option in enumerate(question_data["options"]):
                button = ctk.CTkButton(
                    self.quiz_frame,
                    text=option,
                    command=lambda idx=i: self.check_quiz_answer(idx),
                    font=ctk.CTkFont(size=14),
                    height=40,
                    fg_color="#e6e6e6",
                    hover_color="#d4d4d4",
                    text_color=self.text_color,
                    corner_radius=5
                )
                button.pack(fill="x", padx=50, pady=5)

            self.quiz_result_label = ctk.CTkLabel(
                self.quiz_frame,
                text="",
                font=ctk.CTkFont(size=14),
                text_color="#666666"
            )
            self.quiz_result_label.pack(pady=10)
        else:
            self.show_quiz_results()

    def check_quiz_answer(self, selected_index):
        question_data = self.quiz_questions[self.current_question]
        if selected_index == question_data["correct"]:
            self.correct_answers += 1
            self.quiz_result_label.configure(text="✓ Правильно!", text_color="green")
            self.current_question += 1
            self.after(1000, self.show_quiz_question)
        else:
            self.quiz_result_label.configure(text="✗ Неправильно! Попробуйте еще раз", text_color="red")

    def show_quiz_results(self):
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        result_text = f"Результат: {self.correct_answers}/{len(self.quiz_questions)}"
        if self.correct_answers == len(self.quiz_questions):
            result_color = "green"
            message = "Отлично! Вы прекрасно усвоили последовательность действий!"
        elif self.correct_answers >= len(self.quiz_questions) // 2:
            result_color = "orange"
            message = "Хорошо! Но нужно еще повторить последовательность действий."
        else:
            result_color = "red"
            message = "Попробуйте еще раз! Обратите внимание на порядок выполнения операций."

        result_label = ctk.CTkLabel(
            self.quiz_frame,
            text=result_text,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=result_color
        )
        result_label.pack(pady=(30, 10))

        message_label = ctk.CTkLabel(
            self.quiz_frame,
            text=message,
            font=ctk.CTkFont(size=16),
            text_color=result_color
        )
        message_label.pack(pady=10)

        retry_button = ctk.CTkButton(
            self.quiz_frame,
            text="Пройти еще раз",
            command=self.start_quiz,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color=self.accent_color,
            hover_color="#005a9e",
            text_color="white",
            corner_radius=8
        )
        retry_button.pack(pady=20)

    # Сложные задания (упорядочивание шагов) - остаются без изменений
    def create_knowledge_test_complex(self, main_frame):
        self.steps = [
            "На рабочем столе ПЭВМ открыть ярлык «Connect»",
            "Войти в сессию стандартного пользователя root1 (hicom1)",
            "Нажать сочетание клавиш Ctrl+Tab",
            "Добавить пользователя USER с правами AUTH 0&810; OPT = E, F, I, L, P, R, T; RETRIES = 3; LOCK TIME = 0",
            "Скопировать и вставить пароль (PASSW), ввести новый пароль (6-8 символов)",
            "Контроль учетной записи (DISPLAY-USER)",
            "Нажать ОТКЛЮЧИТЬ (сессию), затем СОЕДИНИТЬ (войти в сессию)",
            "Проверить вход в учетную запись"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_ata_cta_test(self, main_frame):
        self.steps = [
            "Проверить коммутацию (кросс-крест) ТА, при необходимости произвести коммутацию",
            "Подключить ЦТА (SLMO) или АТА (SLMA) к портам АТС",
            "КОНТРОЛЬ - цифровой план станции (DISPLAY-WABE)",
            "Проверить наличие/свободность номера: параметр R в таблице - номер свободы",
            "При отсутствии номера – создать",
            "Проверить или добавить порт (PEN) для АТА (SCSU) и ЦТА (SBCSU)",
            "Присвоить номер соответствующим портам",
            "Проверить, изменить/присвоить имя для ТА (PERSI)",
            "При присвоении имени порту удалить прописанное ранее имя с помощью DELETE",
            "КОНТРОЛЬ - проверить номер (на экране ТА или программно)"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_pen_transfer_test(self, main_frame):
        self.steps = [
            "Создать учетную запись",
            "Подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Резервирование нового порта для переноса",
            "Перенос ТА на новый порт (CHANGE-DSSU)",
            "В случае отказа в работе перезагрузить порт (RESTART-DSSU)",
            "Проверить работоспособность ТА на новом порту",
            "Обновить конфигурацию станции",
            "Провести тестовый вызов",
            "Зафиксировать изменения в документации"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_additional_cta_test(self, main_frame):
        self.steps = [
            "Создать учетную запись, подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Установить адаптер Phone adapter на главный ЦТА",
            "Добавить на ЦТА номер дополнительного ТА",
            "Добавить адаптер расширения (SBCSU)",
            "Настроить параметры адаптера",
            "Проверить соединение между основным и дополнительным ТА",
            "Настроить переадресацию вызовов",
            "Провести тестовые вызовы",
            "Завершить настройку дополнительного ЦТА"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_key_blf_test(self, main_frame):
        self.steps = [
            "Создать учетную запись",
            "Подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Уточнить модуль подключения к ТА: BLF, KEY (CHANGE-SBCSU)",
            "Добавить модуль и ввести параметры (REP=1 или REP=0, BLF=YES)",
            "Настроить индикацию состояния линии",
            "Проверить работу BLF-индикаторов",
            "Настроить функциональные клавиши",
            "Протестировать работу модулей",
            "Зафиксировать конфигурацию"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_layout_test(self, main_frame):
        self.steps = [
            "Уточнить тип ТА (на его обратной стороне)",
            "Учесть при необходимости KEY и BLF-модули",
            "Создать учетную запись, подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Определить стандарт раскладки клавиш для ЦТА и его модуля: TAPRO, DISP, STD",
            "Загрузить требуемый стандарт раскладки: TAPRO, CHANGE",
            "Настроить расположение функциональных клавиш",
            "Проверить соответствие раскладки",
            "КОНТРОЛЬ - проверить результат загрузки стандарта клавиш: TAPRO, DISP",
            "Сохранить конфигурацию раскладки"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_dvo_functions_test(self, main_frame):
        self.steps = [
            "Создать учетную запись, подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Загрузить требуемый стандарт раскладки и доп. модуля LITA: TAPRO, CHANGE",
            "Задать функции для клавиш: TAPRO",
            "Настроить DND (не беспокоить)",
            "Настроить FWD (перенаправление вызова)",
            "Настроить DSS (прямой вызов абонента)",
            "Настроить NAME (клавиши именные и функциональные)",
            "Определить направление адресации: ZIEL",
            "КОНТРОЛЬ – проверка раскладки, функций клавиш ТА для ДВО (DISPLAY-TAPRO)"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_call_intercept_test(self, main_frame):
        self.steps = [
            "Создать учетную запись, подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Загрузить команды ТА, функции клавиш (TAPRO, CHANGE)",
            "Для ТА в группе прописать клавишу PU (call pick-up)",
            "Создать группу (ADD-AUN, qr)",
            "Включить в группу ТА (STNO)",
            "Настроить параметры перехвата вызова",
            "Проверить работу перехвата внутри группы",
            "Настроить приоритеты перехвата",
            "Протестировать функционал перехвата вызовов"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_search_group_test(self, main_frame):
        self.steps = [
            "Создать учетную запись, подключить ТА (PEN)",
            "Добавить номер (N), имя (PERSI)",
            "Загрузить требуемый стандарт на ЦТА: TAPRO, CHANGE",
            "Задать функций для клавиш: TAPRO",
            "Создать в плане нумерации код выхода на группу (пилотная): WABE",
            "Создать группу с кодом выхода (master SA): SA, ADD",
            "Настроить параметры поиска в группе",
            "Удалить группу серийного поиска: SA DEL",
            "Проверить маршрутизацию вызовов в группе",
            "Протестировать функционал группы поиска"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_boss_secretary_test(self, main_frame):
        self.steps = [
            "Создать учетную запись, подключить ТА (PEN)",
            "Добавить необходимое количество номеров (N) – 3, имя (PERSI)",
            "Загрузить команды (на два ТА – директор/секретарь)",
            "Настроить функции клавиш ДВО (ТАРRO, CHANGE)",
            "Настроить функций на клавишах ТА руководителя и секретаря",
            "ТА руководителя: DSS-для выхода на секретаря",
            "ТА руководителя: RNGXFER-деактивация перехвата от секретаря",
            "ТА секретаря: DSS-для выхода на руководителя",
            "ТА секретаря: SPLT-переменный разговор",
            "Указать ТА под директора (Y) и секретаря (N)",
            "Учесть при необходимости KEY и BLF – модули",
            "Создать группу руководитель-секретарь"
        ]
        self.create_knowledge_test_template(main_frame, self.steps)

    def create_knowledge_test_template(self, main_frame, steps):
        self.steps = steps
        self.correct_order = list(range(len(self.steps)))
        self.shuffled_steps = self.steps.copy()
        random.shuffle(self.shuffled_steps)
        self.step_numbers = {}
        self.current_number = 1

        instruction_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        instruction_frame.pack(fill="x", padx=50, pady=(10, 5))

        instruction_label = ctk.CTkLabel(
            instruction_frame,
            text="Присвойте порядковые номера шагам алгоритма:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.text_color
        )
        instruction_label.pack()

        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=self.frame_color,
            border_width=2,
            border_color=self.accent_color,
            corner_radius=5,
            height=400
        )
        scroll_frame.pack(fill="both", expand=True, padx=50, pady=5)

        self.steps_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.steps_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.step_buttons = []
        for i, step in enumerate(self.shuffled_steps):
            btn = ctk.CTkButton(
                self.steps_frame,
                text=step,
                font=ctk.CTkFont(size=10),
                height=30,
                fg_color="#e6e6e6",
                hover_color="#d4d4d4",
                text_color=self.text_color,
                corner_radius=5,
                anchor="w",
                command=lambda idx=i: self.assign_step_number(idx)
            )
            btn.pack(fill="x", pady=1)
            self.step_buttons.append(btn)

        check_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        check_frame.pack(fill="x", padx=50, pady=5)

        self.check_order_button = ctk.CTkButton(
            check_frame,
            text="Проверить порядок",
            command=self.check_order,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            fg_color=self.accent_color,
            hover_color="#005a9e",
            text_color="white",
            corner_radius=8,
            state="disabled"
        )
        self.check_order_button.pack(pady=(5, 5))

        self.result_label = ctk.CTkLabel(
            check_frame,
            text="Присвойте номера всем шагам",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.result_label.pack(pady=(0, 5))

    def assign_step_number(self, index):
        if index in self.step_numbers:
            old_number = self.step_numbers[index]
            del self.step_numbers[index]
            self.step_buttons[index].configure(
                text=self.shuffled_steps[index],
                fg_color="#e6e6e6",
                text_color=self.text_color
            )
            if old_number == self.current_number - 1:
                self.current_number -= 1
        else:
            self.step_numbers[index] = self.current_number
            self.step_buttons[index].configure(
                text=f"{self.current_number}. {self.shuffled_steps[index]}",
                fg_color=self.accent_color,
                text_color="white"
            )
            self.current_number += 1

        all_numbered = len(self.step_numbers) == len(self.shuffled_steps)
        self.check_order_button.configure(state="normal" if all_numbered else "disabled")

        if all_numbered:
            self.result_label.configure(
                text="Все шаги пронумерованы. Нажмите 'Проверить порядок'",
                text_color=self.accent_color
            )
        else:
            self.result_label.configure(
                text=f"Присвойте номера всем шагам ({len(self.step_numbers)}/{len(self.shuffled_steps)})",
                text_color="#666666"
            )

    def check_order(self):
        ordered_indices = sorted(self.step_numbers.keys(), key=lambda x: self.step_numbers[x])
        current_order = []
        for idx in ordered_indices:
            step_text = self.shuffled_steps[idx]
            for i, step in enumerate(self.steps):
                if step_text == step:
                    current_order.append(i)
                    break

        if current_order == self.correct_order:
            self.result_label.configure(
                text="«Правильно! Порядок шагов верный»",
                text_color="green"
            )
            messagebox.showinfo("Успех", "Порядок шагов правильный!")
        else:
            self.result_label.configure(
                text="«Неправильно! Порядок шагов неверный»",
                text_color="red"
            )
            messagebox.showerror("Ошибка", "Порядок шагов неправильный!")

    def back_to_main(self):
        self.destroy()
        self.parent.deiconify()

if __name__ == "__main__":
    app = HicomInterface()
    app.mainloop()