import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading
import math
from datetime import datetime, timedelta
try:
    import winsound
    BEEP_AVAILABLE = True
except ImportError:
    BEEP_AVAILABLE = False

class BlitzSquashTimerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blitz Squash Timer")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Переменные
        self.players = []
        self.num_players = 0
        self.num_circles = 1
        self.total_rounds = 0
        self.schedule = []
        self.results = {}
        self.current_round_index = 0
        self.is_running = False
        self.is_paused = False
        self.remaining_time = 0
        self.current_mode = None  # 'game' или 'break'
        
        # Создаем интерфейс
        self.create_widgets()
        self.show_setup_screen()
        
    def create_widgets(self):
        # Главный фрейм
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Экраны
        self.setup_screen = ttk.Frame(self.main_frame)
        self.tournament_screen = ttk.Frame(self.main_frame)
        
        # Настройка экрана
        self.setup_widgets()
        
        # Экран турнира
        self.tournament_widgets()
    
    def setup_widgets(self):
        # Заголовок
        title_label = ttk.Label(self.setup_screen, text="Blitz Squash Timer", 
                               font=('Arial', 24, 'bold'), foreground='#3498db')
        title_label.pack(pady=20)
        
        # Фрейм для ввода параметров
        input_frame = ttk.Frame(self.setup_screen)
        input_frame.pack(pady=20, fill=tk.X)
        
        # Количество игроков
        ttk.Label(input_frame, text="Количество игроков:", font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=5)
        self.players_var = tk.StringVar(value="4")
        players_entry = ttk.Entry(input_frame, textvariable=self.players_var, font=('Arial', 12), width=10)
        players_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Количество кругов
        ttk.Label(input_frame, text="Количество кругов:", font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.circles_var = tk.StringVar(value="1")
        circles_entry = ttk.Entry(input_frame, textvariable=self.circles_var, font=('Arial', 12), width=10)
        circles_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Длительность раунда (минуты)
        ttk.Label(input_frame, text="Длительность раунда (мин):", font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=5)
        self.game_duration_var = tk.StringVar(value="5")
        game_entry = ttk.Entry(input_frame, textvariable=self.game_duration_var, font=('Arial', 12), width=10)
        game_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Длительность перерыва (минуты)
        ttk.Label(input_frame, text="Длительность перерыва (мин):", font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=5)
        self.break_duration_var = tk.StringVar(value="2")
        break_entry = ttk.Entry(input_frame, textvariable=self.break_duration_var, font=('Arial', 12), width=10)
        break_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Кнопка начала
        start_btn = ttk.Button(self.setup_screen, text="Начать турнир", 
                              command=self.start_tournament, style='Accent.TButton')
        start_btn.pack(pady=20)
        
        # Информация о турнире
        self.info_label = ttk.Label(self.setup_screen, text="", font=('Arial', 10), foreground='#7f8c8d')
        self.info_label.pack(pady=10)
        
        # Обновляем информацию при изменении параметров
        players_entry.bind('<KeyRelease>', self.update_info)
        circles_entry.bind('<KeyRelease>', self.update_info)
    
    def tournament_widgets(self):
        # Верхняя панель с таймером и управлением
        top_frame = ttk.Frame(self.tournament_screen)
        top_frame.pack(fill=tk.X, pady=10)
        
        # Таймер
        self.timer_label = ttk.Label(top_frame, text="05:00", font=('Arial', 48, 'bold'), 
                                   foreground='#e74c3c', background='#34495e')
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        # Информация о раунде
        self.round_info_label = ttk.Label(top_frame, text="Раунд: 1/1", font=('Arial', 14))
        self.round_info_label.pack(side=tk.LEFT, padx=20)
        
        # Режим (Игра/Перерыв)
        self.mode_label = ttk.Label(top_frame, text="ИГРА", font=('Arial', 18, 'bold'), 
                                  foreground='#27ae60')
        self.mode_label.pack(side=tk.LEFT, padx=20)
        
        # Кнопки управления
        control_frame = ttk.Frame(top_frame)
        control_frame.pack(side=tk.RIGHT, padx=20)
        
        self.pause_btn = ttk.Button(control_frame, text="Пауза", command=self.toggle_pause)
        self.pause_btn.pack(pady=2)
        
        self.stop_btn = ttk.Button(control_frame, text="Стоп", command=self.stop_tournament)
        self.stop_btn.pack(pady=2)
        
        # Центральная часть с парами и результатами
        center_frame = ttk.Frame(self.tournament_screen)
        center_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Фрейм для пар
        matches_frame = ttk.LabelFrame(center_frame, text="Текущие пары", padding=10)
        matches_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.matches_text = tk.Text(matches_frame, height=15, font=('Arial', 11), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(matches_frame, orient=tk.VERTICAL, command=self.matches_text.yview)
        self.matches_text.configure(yscrollcommand=scrollbar.set)
        self.matches_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Фрейм для результатов
        results_frame = ttk.LabelFrame(center_frame, text="Результаты", padding=10)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.results_text = tk.Text(results_frame, height=15, font=('Arial', 11), wrap=tk.WORD)
        scrollbar2 = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar2.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Нижняя панель с таблицей
        bottom_frame = ttk.LabelFrame(self.tournament_screen, text="Таблица результатов", padding=10)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        self.standings_text = tk.Text(bottom_frame, height=8, font=('Arial', 10))
        self.standings_text.pack(fill=tk.X)
        
        # Кнопка ввода результатов
        self.results_btn = ttk.Button(self.tournament_screen, text="Ввести результаты", 
                                     command=self.input_results, state=tk.DISABLED)
        self.results_btn.pack(pady=5)
    
    def update_info(self, event=None):
        try:
            players = int(self.players_var.get())
            circles = int(self.circles_var.get())
            if players >= 2 and circles >= 1:
                total_matches = (players * (players - 1) // 2) * circles
                total_rounds = (players - 1) * circles if players % 2 == 0 else players * circles
                total_time = total_rounds * (int(self.game_duration_var.get()) + int(self.break_duration_var.get())) - int(self.break_duration_var.get())
                
                self.info_label.configure(
                    text=f"Матчей: {total_matches} | Раундов: {total_rounds} | Примерное время: {total_time} мин"
                )
        except ValueError:
            self.info_label.configure(text="Введите корректные числа")
    
    def show_setup_screen(self):
        self.tournament_screen.pack_forget()
        self.setup_screen.pack(fill=tk.BOTH, expand=True)
        self.update_info()
    
    def show_tournament_screen(self):
        self.setup_screen.pack_forget()
        self.tournament_screen.pack(fill=tk.BOTH, expand=True)
    
    def start_tournament(self):
        try:
            self.num_players = int(self.players_var.get())
            self.num_circles = int(self.circles_var.get())
            self.game_duration = int(self.game_duration_var.get()) * 60  # в секунды
            self.break_duration = int(self.break_duration_var.get()) * 60  # в секунды
            
            if self.num_players < 2:
                messagebox.showerror("Ошибка", "Должно быть не менее 2 игроков")
                return
            if self.num_circles < 1:
                messagebox.showerror("Ошибка", "Должен быть хотя бы 1 круг")
                return
            
            # Создаем игроков (Player 1, Player 2, ...)
            self.players = [f"Игрок {i+1}" for i in range(self.num_players)]
            
            # Можно добавить диалог для ввода имен
            if messagebox.askyesno("Имена игроков", "Использовать стандартные имена (Игрок 1, Игрок 2...) или ввести свои?"):
                self.ask_player_names()
            
            self.generate_round_robin_schedule()
            self.current_round_index = 0
            self.results = {}
            
            self.show_tournament_screen()
            self.start_round()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа")
    
    def ask_player_names(self):
        for i in range(self.num_players):
            name = simpledialog.askstring("Имя игрока", f"Введите имя игрока {i+1}:", 
                                         initialvalue=f"Игрок {i+1}")
            if name:
                self.players[i] = name
            else:
                self.players[i] = f"Игрок {i+1}"
    
    def generate_round_robin_schedule(self):
        players = self.players[:]
        n = len(players)
        if n % 2:
            players.append(None)
            n += 1

        self.schedule = []
        for circle in range(self.num_circles):
            for round_num in range(n - 1):
                round_matches = []
                for i in range(n // 2):
                    player1 = players[i]
                    player2 = players[n - 1 - i]
                    if player1 is not None and player2 is not None:
                        if circle % 2 == 0 or round_num % 2 == 0:
                            round_matches.append((player1, player2))
                        else:
                            round_matches.append((player2, player1))
                players.insert(1, players.pop())
                self.schedule.append(round_matches)
        
        self.total_rounds = len(self.schedule)
    
    def start_round(self):
        if self.current_round_index >= self.total_rounds:
            self.tournament_finished()
            return
        
        self.is_running = True
        self.is_paused = False
        self.current_mode = 'game'
        self.remaining_time = self.game_duration
        
        self.update_display()
        self.pause_btn.config(text="Пауза")
        self.results_btn.config(state=tk.DISABLED)
        
        # Запускаем таймер в отдельном потоке
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def start_break(self):
        self.is_running = True
        self.is_paused = False
        self.current_mode = 'break'
        self.remaining_time = self.break_duration
        
        self.update_display()
        self.pause_btn.config(text="Пауза")
        self.results_btn.config(state=tk.DISABLED)
        
        self.timer_thread = threading.Thread(target=self.run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def run_timer(self):
        start_time = time.time()
        target_time = start_time + self.remaining_time
        
        while self.is_running and time.time() < target_time:
            if not self.is_paused:
                self.remaining_time = max(0, target_time - time.time())
                self.update_timer_display()
                
                # Проверяем каждую секунду
                time.sleep(0.1)
            else:
                # Если на паузе, корректируем целевое время
                target_time = time.time() + self.remaining_time
                time.sleep(0.1)
        
        if self.is_running:
            self.root.after(0, self.timer_finished)
    
    def update_timer_display(self):
        minutes = int(self.remaining_time) // 60
        seconds = int(self.remaining_time) % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Меняем цвет в зависимости от оставшегося времени
        if self.remaining_time <= 30:  # Последние 30 секунд
            color = '#e74c3c'  # Красный
        elif self.remaining_time <= 60:  # Последняя минута
            color = '#f39c12'  # Оранжевый
        else:
            color = '#27ae60'  # Зеленый
        
        self.root.after(0, lambda: self.timer_label.config(text=time_str, foreground=color))
    
    def update_display(self):
        # Обновляем информацию о раунде
        round_text = f"Раунд: {self.current_round_index + 1}/{self.total_rounds}"
        self.round_info_label.config(text=round_text)
        
        # Обновляем режим
        mode_text = "ПЕРЕРЫВ" if self.current_mode == 'break' else "ИГРА"
        mode_color = '#3498db' if self.current_mode == 'break' else '#27ae60'
        self.mode_label.config(text=mode_text, foreground=mode_color)
        
        # Показываем текущие пары
        self.matches_text.config(state=tk.NORMAL)
        self.matches_text.delete(1.0, tk.END)
        
        if self.current_mode == 'game' and self.current_round_index < len(self.schedule):
            matches = self.schedule[self.current_round_index]
            self.matches_text.insert(tk.END, f"Раунд {self.current_round_index + 1}:\n\n")
            for i, (p1, p2) in enumerate(matches, 1):
                self.matches_text.insert(tk.END, f"Корт {i}: {p1} vs {p2}\n")
        else:
            self.matches_text.insert(tk.END, "Перерыв - следующий раунд скоро начнется")
        
        self.matches_text.config(state=tk.DISABLED)
        
        # Обновляем таблицу результатов
        self.update_standings()
    
    def update_standings(self):
        standings = {player: 0 for player in self.players}
        
        for key, result in self.results.items():
            winner, score = result
            if winner in standings:
                standings[winner] += 1
        
        sorted_standings = sorted(standings.items(), key=lambda x: x[1], reverse=True)
        
        self.standings_text.config(state=tk.NORMAL)
        self.standings_text.delete(1.0, tk.END)
        
        self.standings_text.insert(tk.END, "Место | Игрок | Победы\n")
        self.standings_text.insert(tk.END, "-" * 30 + "\n")
        
        for i, (player, wins) in enumerate(sorted_standings, 1):
            self.standings_text.insert(tk.END, f"{i:>5} | {player:<15} | {wins:>6}\n")
        
        self.standings_text.config(state=tk.DISABLED)
    
    def timer_finished(self):
        self.beep()
        
        if self.current_mode == 'game':
            # Завершилась игра - предлагаем ввести результаты
            self.results_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Раунд завершен", "Игровой раунд завершен! Введите результаты матчей.")
        else:
            # Завершился перерыв - начинаем следующий раунд
            self.current_round_index += 1
            self.start_round()
    
    def toggle_pause(self):
        if not self.is_running:
            return
        
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="Продолжить")
        else:
            self.pause_btn.config(text="Пауза")
    
    def stop_tournament(self):
        self.is_running = False
        if messagebox.askokcancel("Подтверждение", "Вы уверены, что хотите остановить турнир?"):
            self.show_setup_screen()
    
    def input_results(self):
        if self.current_round_index >= len(self.schedule):
            return
        
        matches = self.schedule[self.current_round_index]
        results_window = tk.Toplevel(self.root)
        results_window.title("Ввод результатов")
        results_window.geometry("500x400")
        results_window.transient(self.root)
        results_window.grab_set()
        
        frame = ttk.Frame(results_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Результаты раунда {self.current_round_index + 1}", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.result_vars = {}
        
        for i, (p1, p2) in enumerate(matches, 1):
            match_frame = ttk.LabelFrame(frame, text=f"Корт {i}: {p1} vs {p2}", padding=10)
            match_frame.pack(fill=tk.X, pady=5)
            
            var = tk.StringVar(value=p1)
            ttk.Radiobutton(match_frame, text=f"Победитель: {p1}", variable=var, value=p1).pack(anchor='w')
            ttk.Radiobutton(match_frame, text=f"Победитель: {p2}", variable=var, value=p2).pack(anchor='w')
            
            score_frame = ttk.Frame(match_frame)
            score_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(score_frame, text="Счет:").pack(side=tk.LEFT)
            score_var = tk.StringVar(value="11-9")
            score_entry = ttk.Entry(score_frame, textvariable=score_var, width=10)
            score_entry.pack(side=tk.LEFT, padx=5)
            
            self.result_vars[(p1, p2)] = (var, score_var)
        
        def save_results():
            for (p1, p2), (winner_var, score_var) in self.result_vars.items():
                winner = winner_var.get()
                score = score_var.get()
                
                # Сохраняем результат
                sorted_players = tuple(sorted([p1, p2]))
                circle = self.current_round_index // ((self.num_players - 1) or 1) + 1
                key = (*sorted_players, circle)
                
                self.results[key] = (winner, score)
            
            results_window.destroy()
            self.results_btn.config(state=tk.DISABLED)
            
            # Начинаем перерыв
            self.start_break()
        
        ttk.Button(frame, text="Сохранить результаты и начать перерыв", 
                  command=save_results).pack(pady=20)
    
    def tournament_finished(self):
        self.beep(duration=3000)
        messagebox.showinfo("Турнир завершен", "Турнир успешно завершен!")
        self.update_standings()
        
        # Показываем итоговую таблицу
        standings = {player: 0 for player in self.players}
        for key, result in self.results.items():
            winner, score = result
            if winner in standings:
                standings[winner] += 1
        
        sorted_standings = sorted(standings.items(), key=lambda x: x[1], reverse=True)
        
        result_text = "ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:\n\n"
        for i, (player, wins) in enumerate(sorted_standings, 1):
            result_text += f"{i}. {player} - {wins} побед\n"
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result_text)
        self.results_text.config(state=tk.DISABLED)
        
        self.is_running = False
    
    def beep(self, duration=1000, freq=1000):
        def play_beep():
            if BEEP_AVAILABLE:
                winsound.Beep(freq, duration)
            else:
                # Альтернатива для других ОС
                print(f"\aBEEP! {duration}ms")  # Системный звонок
        threading.Thread(target=play_beep, daemon=True).start()

def main():
    # Создаем стиль для современных кнопок
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    
    # Настраиваем стиль для акцентной кнопки
    style.configure('Accent.TButton', foreground='white', background='#3498db', 
                   font=('Arial', 12, 'bold'))
    
    app = BlitzSquashTimerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()