from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random

current_window = None

def load_image(image_path, size=None):
    try:
        image = Image.open(image_path)
        if size:
            image = image.resize(size)
        print(f"Изображение {image_path} успешно загружено.")
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")
        return None

stirlitz_jokes = [
    "Штирлиц долго смотрел в одну точку. Потом в другую. Так он понял, что двоеточие.",
    "Штирлиц стрелял вслепую. Слепая умерла.",
    "Штирлиц выстрелил в упор. Упор сгорел.",
    "В дверь постучали восемь раз. Осьминог, - подумал Штирлиц",
    "Штирлиц шел по коридору, и вдруг его осенило. Он вернулся и закрыл дверь.",
    "Штирлиц уронил карандаш. Карандаш не поднялся. Так Штирлиц понял, что карандаш был мертв.",
    "Штрилиц всю ночь топил камин. На утро камин утонул",
    "Штирлиц открыл окно. Из окна дуло. Штирлиц закрыл окно. Дуло пропало.",
    "Штирлиц шёл по улице, вдруг перед ним упал кирпич. Вот тебе раз, - подумал Штрилиц. Вот тебе два, - сказал Мюллер и кинул в него кирпич.",
    "Курица клевала носом. Наверное не выспалась, - подумал Штирлиц",
    "Штирлиц залез на телеграфный столб и, чтобы не привлекать внимания прохожих, развернул газету.",
    "Штирлиц оглянулся: хвоста не было. Оторвался, - подумал Штирлиц.",
    "У Штирлица сломалась машина, он вышел и стал копаться в моторе.- Штирлиц, вы - русский разведчик, - сказал проходивший мимо Мюллер. - Истинный ариец непременно обратился бы в автосервис.",
    "К Штирлицу летел свинец. Штирлиц свернул за угол. - Свинец с хрюканьем промчался мимо.",
    "Мюллер с бешенной скоростью мчался в автомобиле. А рядом шел Штирлиц, делая вид, что он прогуливается.",
    "Штирлиц безуспешно пытался установить личность. Личность всё время падала.",
    "В дверь кто-то вежливо постучал ногой. Безруков! - догадался Штирлиц.",
    "Думаете, легко работать на две Ставки? - вздыхал Штирлиц.",
    "Штирлиц заложил ногу за ногу. На следующий день Ногу—за—ногу забрало Гестапо.",
    "Штирлиц сунул вилку в розетку, но ему тактично намекнули, что из розетки едят ложечкой.",
    "Раздался выстрел. По свисту ветра в голове Штирлиц понял, что ранение сквозное.",
    "Штирлиц всегда спал как убитый. Его даже пару раз обводили мелом...",
    "Штирлиц попал в глубокую яму и чудом из нее вылез. Чудес не бывает, - подумал Штирлиц и на всякий случай залез обратно."
]

shown_jokes = set()

def show_completion_window(parent_window, current_level=1):
    global current_window, shown_jokes

    if current_window:
        current_window.destroy()

    completion_window = Toplevel(root)
    current_window = completion_window
    completion_window.title("Уровень пройден!")
    completion_window.attributes('-fullscreen', True)
    completion_window.resizable(False, False)

    bg_image_path = r'Images/фонанекдота.png'
    bg_image = load_image(bg_image_path, (1920, 1200))
    if bg_image:
        bg_label = Label(completion_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = '#f0f0f0'

    available_jokes = [j for j in stirlitz_jokes if j not in shown_jokes]

    if available_jokes:
        joke = random.choice(available_jokes)
        shown_jokes.add(joke)
    else:
        joke = random.choice(stirlitz_jokes)
        shown_jokes.clear()
        shown_jokes.add(joke)

    text_frame = Frame(completion_window,
                       bg='#d9b3ff',
                       bd=8,
                       relief='ridge')
    text_frame.place(relx=0.5, rely=0.4, anchor='center',
                     width=1100, height=300)

    joke_label = Label(text_frame,
                       text=joke,
                       font=('Cascadia Code', 32),
                       bg='white',
                       fg='black',
                       wraplength=1000,
                       padx=20,
                       pady=20)
    joke_label.pack(expand=True, fill='both')

    def restart_level():
        completion_window.destroy()
        parent_window.destroy()
        if current_level == 1:
            create_level_1()
        elif current_level == 2:
            create_level_2()
        elif current_level == 3:
            create_level_3()
        elif current_level == 4:
            create_level_4()
        elif current_level == 5:
            create_level_5()
        elif current_level == 6:
            create_level_6()
        elif current_level == 7:
            create_level_7()
        elif current_level == 8:
            create_level_8()

    restart_btn = ttk.Button(completion_window,
                             text='Пройти заново',
                             style="Rounded.TButton",
                             command=restart_level)
    restart_btn.place(x=220, y=600)

    def finish_game():
        global current_window
        completion_window.destroy()
        parent_window.destroy()
        current_window = None
        go_to_main_menu()

    if current_level == 8:
        finish_btn = ttk.Button(completion_window,
                                text='Завершить игру',
                                style="Rounded.TButton",
                                command=finish_game)
        finish_btn.place(x=970, y=600)
    else:
        def next_level():
            completion_window.destroy()
            parent_window.destroy()
            if current_level == 1:
                create_level_2()
            elif current_level == 2:
                create_level_3()
            elif current_level == 3:
                create_level_4()
            elif current_level == 4:
                create_level_5()
            elif current_level == 5:
                create_level_6()
            elif current_level == 6:
                create_level_7()
            elif current_level == 7:
                create_level_8()

        next_level_btn = ttk.Button(completion_window,
                                    text='Следующий уровень',
                                    style="Rounded.TButton",
                                    command=next_level)
        next_level_btn.place(x=970, y=600)


def level_not_available():
    messagebox.showinfo("Информация", "Этот уровень пока недоступен")


def toggle_cell(cells, i, j):
    cell = cells[i][j]
    if hasattr(cell, 'square_id'):
        cell.delete(cell.square_id)
        delattr(cell, 'square_id')
    else:
        width = cell.winfo_width()
        height = cell.winfo_height()
        margin = 2
        square = cell.create_rectangle(margin, margin, width - margin, height - margin,
                                       fill='#7342c7', outline='#916ad4')
        cell.square_id = square

def reset_level(cells):
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                cell.delete(cell.square_id)
                delattr(cell, 'square_id')
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')


def create_level_1():
    global current_window
    if current_window:
        current_window.destroy()

    level_window = Toplevel(root)
    level_window.title('Уровень 1')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/4.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level1(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.5, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 200
    for i in range(3):
        row = []
        for j in range(3):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level1(cells, level_window):
    solution = [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 5:
        return

    if filled_cells > 8:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(3):
        for j in range(3):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 50

                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=4)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=4)
                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=1)


def create_level_2():
    level_window = Toplevel(root)
    level_window.title('Уровень 2')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/5.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        change_image()
        level_window.destroy()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level2(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.54, rely=0.49, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 120
    for i in range(5):
        row = []
        for j in range(5):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level2(cells, level_window):
    solution = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 8:
        return

    if filled_cells > 15:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(5):
        for j in range(5):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 30

                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=3)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=3)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=2)


def create_level_3():
    level_window = Toplevel(root)
    level_window.title('Уровень 3')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/6.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        change_image()
        level_window.destroy()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level3(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.5, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 120
    for i in range(5):
        row = []
        for j in range(5):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level3(cells, level_window):
    solution = [
        [1, 1, 0, 1, 1],
        [1, 0, 1, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 13:
        return

    if filled_cells > 20:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(5):
        for j in range(5):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 30

                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=3)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=3)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=3)


def create_level_4():
    level_window = Toplevel(root)
    level_window.title('Уровень 4')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/7.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        change_image()
        level_window.destroy()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level4(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.5, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 100
    for i in range(6):
        row = []
        for j in range(6):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level4(cells, level_window):
    solution = [
        [1, 1, 0, 0, 0, 1],
        [0, 1, 0, 1, 1, 1],
        [0, 1, 0, 1, 1, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 14:
        return

    if filled_cells > 25:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(6):
        for j in range(6):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 25
                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=3)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=3)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=4)

def create_level_5():
    level_window = Toplevel(root)
    level_window.title('Уровень 5')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/8.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        change_image()
        level_window.destroy()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level5(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.5, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 85
    for i in range(7):
        row = []
        for j in range(7):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level5(cells, level_window):
    solution = [
        [0, 1, 1, 1, 1, 1, 0],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 21:
        return

    if filled_cells > 30:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(7):
        for j in range(7):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 20
                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=2.5)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=2.5)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=5)

def create_level_6():
    level_window = Toplevel(root)
    level_window.title('Уровень 6')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/9.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        change_image()
        level_window.destroy()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level6(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.5, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 70
    for i in range(8):
        row = []
        for j in range(8):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level6(cells, level_window):
    solution = [
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 0, 1, 1, 0, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 0]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 26:
        return

    if filled_cells > 34:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(8):
        for j in range(8):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 13
                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=2.5)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=2.5)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=6)

def create_level_7():
    level_window = Toplevel(root)
    level_window.title('Уровень 7')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/10.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        change_image()
        level_window.destroy()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command=lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level7(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.5, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 65
    for i in range(9):
        row = []
        for j in range(9):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level7(cells, level_window):
    solution = [
        [0, 0, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 0, 1, 1, 1, 0]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 29:
        return

    if filled_cells > 40:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(9):
        for j in range(9):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 11
                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=2.5)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=2.5)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=7)

def create_level_8():
    level_window = Toplevel(root)
    level_window.title('Уровень 8')
    level_window.attributes('-fullscreen', True)
    level_window.resizable(False, False)

    bg_image = load_image(r'Images/11.png', (1535, 960))
    if bg_image:
        bg_label = Label(level_window, image=bg_image)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = bg_image
        window_bg = bg_label.cget('bg')
    else:
        window_bg = level_window.cget('bg')

    reset_btn = ttk.Button(level_window, text='Сброс', style="Rounded.TButton",
                           command=lambda: reset_level(cells), width=6)
    reset_btn.place(x=80, y=50)

    def return_to_levels_menu():
        global current_window

        if current_window:
            current_window.destroy()
        current_window = None
        change_image()

    menu_btn = ttk.Button(level_window,
                          text='Выход в главное\n     меню    ',
                          style="Rounded.TButton",
                          command= lambda: [level_window.destroy(), go_to_main_menu()],
                          width=15)
    menu_btn.place(x=25, y=800)

    check_btn = ttk.Button(level_window, text='Проверка', style="Rounded.TButton",
                           command=lambda: check_solution_level8(cells, level_window), width=12)
    check_btn.place(relx=1.0, x=-40, y=450, anchor='ne')

    main_container = Frame(level_window, bg=window_bg)
    main_container.place(relx=0.53, rely=0.48, anchor='center')

    game_container = Frame(main_container, bg=window_bg)
    game_container.pack()

    middle_container = Frame(game_container, bg=window_bg)
    middle_container.pack()

    game_frame = Frame(middle_container, bg=window_bg)
    game_frame.grid(row=0, column=1)

    cells = []
    cell_size = 60
    for i in range(10):
        row = []
        for j in range(10):
            cell = Canvas(game_frame,
                          width=cell_size,
                          height=cell_size,
                          bg='white',
                          highlightthickness=1,
                          highlightbackground='black')
            cell.grid(row=i, column=j, padx=1, pady=1)
            cell.bind('<Button-1>', lambda e, i=i, j=j: toggle_cell(cells, i, j))
            row.append(cell)
        cells.append(row)


def check_solution_level8(cells, level_window):
    solution = [
        [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 1, 0]
    ]

    filled_cells = 0
    for row in cells:
        for cell in row:
            if hasattr(cell, 'square_id'):
                filled_cells += 1

    if filled_cells < 31:
        return

    if filled_cells > 50:
        reset_level(cells)
        return

    for row in cells:
        for cell in row:
            if hasattr(cell, 'cross_id'):
                for cross in cell.cross_id:
                    cell.delete(cross)
                delattr(cell, 'cross_id')

    has_errors = False
    for i in range(10):
        for j in range(10):
            user_cell = 1 if hasattr(cells[i][j], 'square_id') else 0
            if user_cell != solution[i][j]:
                has_errors = True
                width = cells[i][j].winfo_width()
                height = cells[i][j].winfo_height()
                margin = 10
                cross1 = cells[i][j].create_line(margin, margin, width - margin, height - margin,
                                                 fill='#FFB6C1', width=2)
                cross2 = cells[i][j].create_line(width - margin, margin, margin, height - margin,
                                                 fill='#FFB6C1', width=2)

                cells[i][j].cross_id = (cross1, cross2)

    if not has_errors:
        show_completion_window(level_window, current_level=8)

def open_tutorial():
    tutorial_window = Toplevel(root)
    tutorial_window.title("Обучение")
    tutorial_window.attributes('-fullscreen', True)
    tutorial_window.resizable(False, False)

    tutorial_bg = load_image('Images/3.png', (1920, 1200))
    if tutorial_bg:
        print("Фоновое изображение для обучения загружено.")
        bg_label = Label(tutorial_window, image=tutorial_bg)
        bg_label.place(relx=0.5, rely=0.5, anchor='center')
        bg_label.image = tutorial_bg
    else:
        print("Фоновое изображение для обучения не загружено.")
        tutorial_window.config(bg='white')

    tutorial_text = """
    Добро пожаловать в обучение по игре Нонограмм!

        Цель игры:
 Заполните клеточки на поле, основываясь на 
 числовых подсказках.
 Числа указывают, сколько клеток необходимо 
 заполнить в строке или столбце.

        Правила:
 1. Клетки, которые необходимо заполнить, отмечаются 
 цветом.
 2. Сначала подумайте, как лучше всего заполнить 
 клетки, используя подсказки.

   Пример 1:
 - Если в строке указано число "5", это означает, что 
 в этой строке нужно закрасить 5 клеток подряд.
   Пример 2:
 - Если в строке указано "2 1", это означает, что 
 нужно закрасить две группы клеток: первую из 2 клеток 
 и вторую из 1 клетки, с хотя бы одной пустой клеткой 
 между ними.

 3. Удачи в игре!

        Совет:
 - Начинайте с строк и столбцов, где есть только одна 
 группа клеток.
        """

    label = Label(tutorial_window, text=tutorial_text, justify="left", padx=0, pady=0, font=('Cascadia Code', 14),
                  bg='white')
    label.place(relx=0.25, rely=0.44, anchor='center')

    example_images = [
        'Images/пример2.png',
        'Images/пример3.png',
    ]
    current_image_index = 0

    def show_next_image():
        nonlocal current_image_index
        current_image_index = (current_image_index + 1) % len(example_images)
        image = load_image(example_images[current_image_index], (600, 600))
        if image:
            image_label.config(image=image)
            image_label.image = image

    image = load_image(example_images[current_image_index], (580, 580))
    image_label = Label(tutorial_window, image=image, bg='white')
    image_label.image = image
    image_label.place(relx=0.75, rely=0.35, anchor='center')

    next_button = ttk.Button(tutorial_window, text="Далее", style="Rounded.TButton",
                             command=show_next_image)
    next_button.place(relx=0.75, rely=0.75, anchor='center')

    close_button = ttk.Button(tutorial_window, text='Закрыть обучение', style="Rounded.TButton", width=20,
                              padding=5,
                              command=tutorial_window.destroy)
    close_button.place(relx=0.25, rely=0.9, anchor='center')


def change_image():
    global current_window

    btn.place_forget()
    exit_btn.place_forget()

    if current_window:
        current_window.destroy()

    levels_window = Toplevel(root)
    current_window = levels_window
    levels_window.title('Главное меню')
    levels_window.attributes('-fullscreen', True)
    levels_window.resizable(False, False)

    new_photo = load_image(r'Images/2.png', (1920, 1200))
    if new_photo:
        label = Label(levels_window, image=new_photo)
        label.place(relx=0.5, rely=0.5, anchor='center')
        label.image = new_photo
    else:
        label = Label(levels_window, text="Изображение не загружено", font=('Cascadia Code', 20))
        label.pack()

    create_level_buttons(levels_window)

    exit_main_btn = ttk.Button(levels_window,
                               text='Выход на главную',
                               style="Exit.TButton",
                               width=18,
                               command=lambda: [levels_window.destroy(), show_main_screen()])
    exit_main_btn.place(relx=0.5, rely=0.85, anchor='center')

def create_level_buttons(window):
    training_button = ttk.Button(window, text='ОБУЧЕНИЕ', width=20, style="Rounded.TButton", command=open_tutorial)
    training_button.place(relx=0.5, y=50, anchor='center')

    levels = [
        (90, 210), (440, 210), (790, 210), (1140, 210),
        (90, 470), (440, 470), (790, 470), (1140, 470)
    ]

    for i, (x, y) in enumerate(levels):
        level_num = i + 1
        if level_num == 1:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_1)
        elif level_num == 2:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_2)
        elif level_num == 3:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_3)
        elif level_num == 4:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_4)
        elif level_num == 5:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_5)
        elif level_num == 6:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_6)
        elif level_num == 7:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_7)
        elif level_num == 8:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=create_level_8)
        else:
            button = ttk.Button(window, text=f'Уровень {level_num}', width=12, padding=30,
                                style="Rounded.TButton", command=level_not_available)
        button.place(x=x, y=y)


def show_main_screen():
    global current_window

    if current_window:
        current_window.destroy()
    current_window = None

    label.config(image=photo)
    btn.place(relx=0.5, rely=0.5, anchor='center')
    exit_btn.place(relx=0.5, rely=0.6, anchor='center')

def go_to_main_menu():
        global current_window

        if current_window:
            current_window.destroy()
        change_image()

def clear_level_buttons():
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Button) and ('Уровень' in widget.cget("text") or widget.cget("text") == "ОБУЧЕНИЕ"):
            widget.destroy()


root = Tk()
root.title('Нонограмм')
root.attributes('-fullscreen', True)
root.resizable(False, False)

style = ttk.Style()
btn_font = ('Cascadia Code', 24)
level_btn_font = ('Cascadia Code', 14)

style.configure("Rounded.TButton", padding=10, relief="flat", background="#666FFF", borderwidth=1,
                focusthickness=1,
                font=btn_font)
style.map("Rounded.TButton", background=[("active", "#666FFF")], foreground=[("active", "black")])
style.configure("Exit.TButton", padding=10, relief="flat", background="#666FFF", borderwidth=1,
                focusthickness=1,
                font=btn_font)
style.map("Exit.TButton", background=[("active", "#666FFF")], foreground=[("active", "black")])

photo = load_image('Images/1.png', (1920, 1200))
if photo:
    label = Label(root, image=photo)
    label.place(relx=0.5, rely=0.5, anchor='center')
else:
    label = Label(root, text="Изображение не загружено", font=('Cascadia Code', 20))
    label.pack()

btn = ttk.Button(root, text='Начать игру', style="Rounded.TButton", width=20, command=change_image)
btn.place(relx=0.5, rely=0.5, anchor='center')

exit_btn = ttk.Button(root, text='Выход из игры', style="Exit.TButton", width=18, command=root.quit)
exit_btn.place(relx=0.5, rely=0.6, anchor='center')

root.mainloop()