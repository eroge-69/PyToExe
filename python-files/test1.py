import tkinter as tk
from tkinter import messagebox, Menu, Canvas, Text

class DotaTIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The International - Dota 2 Championship")
        self.root.option_add("*tearOff", False)
        self.root.resizable(True, True)
        self.root.configure(bg='#1c2833')
        
        self.min_width = 800
        self.min_height = 500
        
        self.image_paths = {
            'main': 'ti_main.png',
            'tournaments': {i: f'ti{i}.png' for i in range(1, 11)},
            'winners': {i: f'tiw{i}.png' for i in range(1, 11)},
        }
        
        self.setup_ui()
        self.create_menu()
        self.show_main_image()
        self.bind_mouse_wheel()

    def bind_mouse_wheel(self):
        self.canvas.bind("<MouseWheel>", self._on_vertical_scroll)
        self.canvas.bind("<Shift-MouseWheel>", self._on_horizontal_scroll)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_vertical_scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_horizontal_scroll(self, event):
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

    def setup_ui(self):
        # Фрейм для Canvas
        canvas_frame = tk.Frame(self.root, bg='#1c2833')
        canvas_frame.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        
        self.canvas = Canvas(
            canvas_frame, 
            bg='#1c2833', 
            highlightthickness=0,
            borderwidth=0,
            xscrollincrement=10,
            yscrollincrement=10
        )
        self.canvas.pack(side='top', fill='both', expand=True, padx=0, pady=0)
        
        # Текстовое поле для описания
        self.text_frame = tk.Frame(self.root, bg='#1c2833')
        self.text_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 0))
        
        self.text = Text(
            self.text_frame,
            wrap='word',
            height=6,
            font=('Arial', 11),
            bg='#1c2833',
            fg='white',
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=0,
            insertbackground='white'
        )
        self.text.pack(side='left', fill='both', expand=True, padx=0, pady=0)
        
        # Фрейм для вкладок-кнопок
        self.tab_frame = tk.Frame(self.root, bg='#1c2833')
        self.tab_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))
        
        # Создаем вкладки-кнопки
        self.create_tabs()
        
        # Настройка весов
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

    def create_tabs(self):
        # Список вкладок
        tabs = [
            ("Главная", self.show_main_image),
            ("Турниры", self.show_tournaments_menu),
            ("Победители", self.show_winners_menu),
            ("О программе", self.show_about),
            ("Выход", self.confirm_exit)
        ]
        
        # Создаем кнопки-вкладки
        for text, command in tabs:
            tab = tk.Button(
                self.tab_frame,
                text=text,
                command=command,
                font=('Arial', 12, 'bold'),
                bg='#2c3e50',
                fg='white',
                padx=15,
                pady=8,
                relief='flat',
                borderwidth=0,
                highlightthickness=0,
                activebackground='#3498db',
                activeforeground='white'
            )
            tab.pack(side='left', padx=5, pady=0)
            
            # Выделяем кнопку "Выход" красным цветом
            if text == "Выход":
                tab.config(bg='#e74c3c', activebackground='#c0392b')

    def show_tournaments_menu(self):
        """Показывает меню выбора турнира"""
        menu = Menu(self.root, 
                   tearoff=0, 
                   font=('Arial', 11), 
                   bg='#2c3e50', 
                   fg='white',
                   activebackground='#3498db',
                   activeforeground='white',
                   borderwidth=0)
        
        for i in range(1, 11):
            menu.add_command(
                label=f"The International {i}", 
                command=lambda idx=i: self.show_tournament(idx)
            )
        
        # Показываем меню рядом с кнопкой "Турниры"
        tab_x = self.tab_frame.winfo_x()
        tab_y = self.tab_frame.winfo_y() + self.tab_frame.winfo_height()
        menu.post(tab_x + 100, tab_y)

    def show_winners_menu(self):
        """Показывает меню выбора победителя"""
        menu = Menu(self.root, 
                   tearoff=0, 
                   font=('Arial', 11), 
                   bg='#2c3e50', 
                   fg='white',
                   activebackground='#3498db',
                   activeforeground='white',
                   borderwidth=0)
        
        for i in range(1, 11):
            menu.add_command(
                label=f"Победитель TI {i}", 
                command=lambda idx=i: self.show_winner(idx)
            )
        
        # Показываем меню рядом с кнопкой "Победители"
        tab_x = self.tab_frame.winfo_x()
        tab_y = self.tab_frame.winfo_y() + self.tab_frame.winfo_height()
        menu.post(tab_x + 220, tab_y)

    def create_menu(self):
        self.main_menu = Menu(self.root, 
                             font=('Verdana', 12), 
                             bg='#1c2833', 
                             fg='white',
                             activebackground='#3498db',
                             activeforeground='white',
                             borderwidth=0)
        
        self.main_menu.add_command(label="Главная", command=self.show_main_image)
        
        tournaments_menu = Menu(self.main_menu, 
                              tearoff=0, 
                              font=('Verdana', 11), 
                              bg='#1c2833', 
                              fg='white',
                              activebackground='#3498db',
                              activeforeground='white',
                              borderwidth=0)
        for i in range(1, 11):
            tournaments_menu.add_command(
                label=f"The International {i}", 
                command=lambda idx=i: self.show_tournament(idx)
            )
        self.main_menu.add_cascade(label="Турниры", menu=tournaments_menu)
        
        winners_menu = Menu(self.main_menu, 
                          tearoff=0, 
                          font=('Verdana', 11), 
                          bg='#1c2833', 
                          fg='white',
                          activebackground='#3498db',
                          activeforeground='white',
                          borderwidth=0)
        for i in range(1, 11):
            winners_menu.add_command(
                label=f"Победитель TI {i}", 
                command=lambda idx=i: self.show_winner(idx)
            )
        self.main_menu.add_cascade(label="Победители", menu=winners_menu)
        
        self.main_menu.add_command(label="О программе", command=self.show_about)
        self.main_menu.add_command(label="Выход", command=self.confirm_exit)
        
        self.root.config(menu=self.main_menu)

    def load_image(self, filename):
        try:
            return tk.PhotoImage(file=filename)
        except Exception as e:
            print(f"Ошибка загрузки изображения {filename}: {e}")
            return tk.PhotoImage(width=1, height=1)

    def resize_window_to_image(self, img):
        if not img:
            return
            
        img_width = img.width()
        img_height = img.height()
        
        text_height = 150
        buttons_height = 70
        padding = 40
        
        window_width = min(img_width + 20, self.root.winfo_screenwidth() - 100)
        window_height = min(img_height + text_height + buttons_height + padding, 
                           self.root.winfo_screenheight() - 100)
        
        window_width = max(window_width, self.min_width)
        window_height = max(window_height, self.min_height)
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.canvas.config(scrollregion=(0, 0, img_width, img_height))

    def show_main_image(self):
        self.canvas.delete("all")
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        
        img = self.load_image(self.image_paths['main'])
        if img:
            self.canvas.create_image(0, 0, anchor='nw', image=img)
            self.canvas.image = img
            self.resize_window_to_image(img)
        
        main_text = (
            "The International — ежегодный чемпионат мира по Dota 2. Первый турнир состоялся в 2011 году в Кёльне, "
            "Германия. С тех пор мероприятие стало крупнейшим в киберспорте с рекордными призовыми фондами. "
            "В 2021 году призовой фонд составил $40 миллионов, а чемпионом стала российская команда Team Spirit."
        )
        self.text.insert(tk.END, main_text)
        self.text.config(state='disabled')

    def show_tournament(self, event_id):
        self.canvas.delete("all")
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        
        img = self.load_image(self.image_paths['tournaments'][event_id])
        if img:
            self.canvas.create_image(0, 0, anchor='nw', image=img)
            self.canvas.image = img
            self.resize_window_to_image(img)
        
        tournament_texts = {
            1: "The International 2011: Кёльн, Германия (16-21 августа)\nПризовой фонд: $1.6 млн\nПобедитель: Natus Vincere",
            2: "The International 2012: Сиэтл, США (26 августа - 2 сентября)\nПризовой фонд: $1.6 млн\nПобедитель: Invictus Gaming",
            3: "The International 2013: Сиэтл, США (3-11 августа)\nПризовой фонд: $2.8 млн\nПобедитель: Alliance",
            4: "The International 2014: Сиэтл, США (18-21 июля)\nПризовой фонд: $10.9 млн\nПобедитель: Newbee",
            5: "The International 2015: Сиэтл, США (3-8 августа)\nПризовой фонд: $18.4 млн\nПобедитель: Evil Geniuses",
            6: "The International 2016: Сиэтл, США (8-13 августа)\nПризовой фонд: $20.7 млн\nПобедитель: Wings Gaming",
            7: "The International 2017: Сиэтл, США (7-12 августа)\nПризовой фонд: $24.7 млн\nПобедитель: Team Liquid",
            8: "The International 2018: Ванкувер, Канада (20-25 августа)\nПризовой фонд: $25.5 млн\nПобедитель: OG",
            9: "The International 2019: Шанхай, Китай (20-25 августа)\nПризовой фонд: $34.3 млн\nПобедитель: OG",
            10: "The International 2021: Бухарест, Румыния (7-17 октября)\nПризовой фонд: $40.0 млн\nПобедитель: Team Spirit"
        }
        self.text.insert(tk.END, tournament_texts.get(event_id, "Информация о турнире отсутствует."))
        self.text.config(state='disabled')

    def show_winner(self, winner_id):
        self.canvas.delete("all")
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        
        img = self.load_image(self.image_paths['winners'][winner_id])
        if img:
            self.canvas.create_image(0, 0, anchor='nw', image=img)
            self.canvas.image = img
            self.resize_window_to_image(img)
        
        winner_texts = {
            1: "Natus Vincere (2011)\nСостав: Dendi, XBOCT, ArtStyle, Puppey, LighTofHeaveN",
            2: "Invictus Gaming (2012)\nСостав: Ferrari_430, Zhou, YYF, ChuaN, Faith",
            3: "Alliance (2013)\nСостав: s4, Loda, AdmiralBulldog, EGM, Akke",
            4: "Newbee (2014)\nСостав: Hao, Mu, xiao8, Banana, Sansheng",
            5: "Evil Geniuses (2015)\nСостав: SumaiL, Fear, UNiVeRsE, Aui_2000, ppd",
            6: "Wings Gaming (2016)\nСостав: Shadow, bLink, iceice, Innocence, y`",
            7: "Team Liquid (2017)\nСостав: MATUMBAMAN, Miracle-, MinD_ContRoL, GH, KuroKy",
            8: "OG (2018)\nСостав: ana, Topson, 7ckngMad, N0tail, JerAx",
            9: "OG (2019)\nСостав: ana, Topson, Ceb, N0tail, JerAx",
            10: "Team Spirit (2021)\nСостав: Yatoro, TORONTOTOKYO, Collapse, Mira, Miposhka"
        }
        self.text.insert(tk.END, winner_texts.get(winner_id, "Информация о победителе отсутствует."))
        self.text.config(state='disabled')

    def show_about(self):
        messagebox.showinfo("О программе", 
                           "The International Dota 2 Encyclopedia\nВерсия 1.0\n",
                           icon='info')

    def confirm_exit(self):
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти?", icon='question'):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DotaTIApp(root)
    root.mainloop()