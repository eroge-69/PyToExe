import tkinter as tk
import random

CELL_SIZE = 60
GRID_ROWS = 11
GRID_COLS = 9
DIE_SIZE = 48

class DieWidget(tk.Canvas):
    def __init__(self, master, app=None, value=None, **kwargs):
        super().__init__(master, width=DIE_SIZE, height=DIE_SIZE, highlightthickness=0, **kwargs)
        self.app = app
        self.value = value if value is not None else random.randint(1,6)
        self.selected = False
        self._canvas_window = None
        self._grid_pos = None
        self.locked = False
        self.draw_die()
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_release)
        self._drag_data = {'x':0,'y':0}

    def set_value(self, v):
        self.value = v
        self.draw_die()

    def draw_die(self):
        self.delete('all')
        w = DIE_SIZE; h = DIE_SIZE
        self.create_rectangle(0,0,w,h, fill='#ffffff', outline='#cccccc', width=2)
        pip_coords = {
            1: [(0.5,0.5)],
            2: [(0.25,0.25),(0.75,0.75)],
            3: [(0.2,0.2),(0.5,0.5),(0.8,0.8)],
            4: [(0.25,0.25),(0.25,0.75),(0.75,0.25),(0.75,0.75)],
            5: [(0.25,0.25),(0.25,0.75),(0.5,0.5),(0.75,0.25),(0.75,0.75)],
            6: [(0.25,0.2),(0.25,0.5),(0.25,0.8),(0.75,0.2),(0.75,0.5),(0.75,0.8)],
        }
        radius = 4
        for (nx,ny) in pip_coords[self.value]:
            x = int(nx * w)
            y = int(ny * h)
            self.create_oval(x-radius, y-radius, x+radius, y+radius, fill='#222222', outline='')
        if self.selected:
            self.create_rectangle(0,0,w,h, outline='blue', width=2)

    def on_click(self, event):
        if self.locked:  
            return
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y
        if self.app and hasattr(self.app, 'on_die_selected'):
            self.app.on_die_selected(self)

    def on_drag(self, event):
        if self.locked:  
            return
        dx = event.x - self._drag_data['x']
        dy = event.y - self._drag_data['y']
        if self.app and hasattr(self.app, 'move_die_by'):
            self.app.move_die_by(self, dx, dy)

    def on_release(self, event):
        if self.app and hasattr(self.app, 'on_die_released'):
            self.app.on_die_released(self, event)

    def set_selected(self, flag: bool):
        self.selected = flag
        self.draw_die()


class BoardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ZUGALHO')
        self.resizable(False, False)

        self.current_player_turn = 1  # 1 = jogador 1 (superior), 2 = jogador 2 (inferior)

        # Frame principal
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(padx=10, pady=10)

        # Título acima do tabuleiro
        self.title_label = tk.Label(self.main_frame, text="ZUGALHO", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(0,10))

        # Frame da barra centralizada (pontuações + botão)
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(pady=(0,10))

        # Pontuação jogador 1
        self.score_label_p1 = tk.Label(self.top_frame, text="Jogador 1\nPONTUAÇÃO: 0", font=("Arial", 12))
        self.score_label_p1.pack(side='left', padx=20)

        # Botão rolar dado
        self.roll_button = tk.Button(self.top_frame, text='Rolar dado', command=self.roll_die, width=12)
        self.roll_button.pack(side='left', padx=20)

        # Pontuação jogador 2
        self.score_label_p2 = tk.Label(self.top_frame, text="Jogador 2\nPONTUAÇÃO: 0", font=("Arial", 12))
        self.score_label_p2.pack(side='left', padx=20)

        # Label do turno
        self.turn_label = tk.Label(self.main_frame, text="Turno: Jogador 1", font=("Arial", 12, "italic"))
        self.turn_label.pack(pady=(0,10))

        # Canvas do tabuleiro
        self.canvas = tk.Canvas(self.main_frame, width=CELL_SIZE*GRID_COLS, height=CELL_SIZE*GRID_ROWS, bg='#000000')
        self.canvas.pack()

        self.spawn_pos = (5, 4)
        self.cells = [[None for _ in range(GRID_COLS)] for __ in range(GRID_ROWS)]
        self.selected_die = None

        self.draw_grid()
        self.canvas.bind('<Button-1>', self.on_board_click)

    # --- Funções do jogo ---
    def draw_grid(self):
        self.canvas.delete('all')
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                fill_color = '#000000'
                outline_color = ''
                width = 0
                if (r,c) == self.spawn_pos:
                    fill_color = '#00cc00'
                    outline_color = 'black'
                    width = 2
                elif c in (3,4,5) and r in (1,2,3):
                    fill_color = "#FFFFFF"
                    outline_color = 'black'
                    width = 2
                elif c in (3,4,5) and r in (7,8,9):
                    fill_color = "#FFFFFF"
                    outline_color = 'black'
                    width = 2
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline=outline_color, width=width)

    def roll_die(self):
        r, c = self.spawn_pos
        if self.cells[r][c] is not None:
            return
        die = DieWidget(self.canvas, app=self)
        die.set_value(random.randint(1,6))
        cx = c*CELL_SIZE + CELL_SIZE//2
        cy = r*CELL_SIZE + CELL_SIZE//2
        win = self.canvas.create_window(cx, cy, window=die)
        die._canvas_window = win
        die._grid_pos = (r,c)
        self.cells[r][c] = die
        self.update_scores()

    def on_die_selected(self, die_widget):
        if self.selected_die is die_widget:
            return
        if self.selected_die:
            self.selected_die.set_selected(False)
        self.selected_die = die_widget
        die_widget.set_selected(True)

    def move_die_by(self, die_widget, dx, dy):
        if not hasattr(die_widget, '_canvas_window') or die_widget._canvas_window is None:
            return
        coords = self.canvas.coords(die_widget._canvas_window)
        if not coords:
            return
        x, y = coords
        self.canvas.coords(die_widget._canvas_window, x+dx, y+dy)

    def on_die_released(self, die_widget, event):
        if not hasattr(die_widget, '_canvas_window') or die_widget._canvas_window is None:
            return
        coords = self.canvas.coords(die_widget._canvas_window)
        if not coords:
            return
        x, y = coords
        c = int(x // CELL_SIZE)
        r = int(y // CELL_SIZE)

        # Linhas válidas para o jogador atual
        if self.current_player_turn == 1:
            valid_rows = (1,2,3)
            opposite_rows = (7,8,9)
        else:
            valid_rows = (7,8,9)
            opposite_rows = (1,2,3)

        valid_cells = [(rr,cc) for rr in valid_rows for cc in (3,4,5)]

        if (r,c) in valid_cells and self.cells[r][c] is None:
            # Destruir dados iguais no tabuleiro oposto
            for rr in opposite_rows:
                other_die = self.cells[rr][c]
                if other_die and other_die.value == die_widget.value:
                    x0 = other_die._grid_pos[1]*CELL_SIZE
                    y0 = other_die._grid_pos[0]*CELL_SIZE
                    x1 = x0+CELL_SIZE
                    y1 = y0+CELL_SIZE
                    self.canvas.create_rectangle(x0,y0,x1,y1, fill='#FFFFFF', outline='black', width=2)
                    self.destroy_die(other_die)

            if die_widget._grid_pos:
                pr, pc = die_widget._grid_pos
                if 0 <= pr < GRID_ROWS and 0 <= pc < GRID_COLS and self.cells[pr][pc] is die_widget:
                    self.cells[pr][pc] = None
            cx = c*CELL_SIZE + CELL_SIZE//2
            cy = r*CELL_SIZE + CELL_SIZE//2
            self.canvas.coords(die_widget._canvas_window, cx, cy)
            die_widget._grid_pos = (r,c)
            die_widget.locked = True
            self.cells[r][c] = die_widget

            # Alterna turno
            self.current_player_turn = 2 if self.current_player_turn == 1 else 1
            self.turn_label.config(text=f"Turno: Jogador {self.current_player_turn}")

            self.update_scores()
            self.check_game_over()  # Verifica se o jogo terminou

        else:
            # Retorna dado para spawn
            if die_widget._grid_pos:
                pr, pc = die_widget._grid_pos
                cx = pc*CELL_SIZE + CELL_SIZE//2
                cy = pr*CELL_SIZE + CELL_SIZE//2
                self.canvas.coords(die_widget._canvas_window, cx, cy)

    def destroy_die(self, die_widget):
        try:
            self.canvas.delete(die_widget._canvas_window)
        except:
            pass
        if die_widget._grid_pos:
            pr, pc = die_widget._grid_pos
            if 0 <= pr < GRID_ROWS and 0 <= pc < GRID_COLS and self.cells[pr][pc] is die_widget:
                self.cells[pr][pc] = None

    def on_board_click(self, event):
        if not self.selected_die:
            return
        die = self.selected_die
        if hasattr(die, '_canvas_window') and die._canvas_window is not None:
            return
        c = int(event.x // CELL_SIZE)
        r = int(event.y // CELL_SIZE)

        valid_rows = (1,2,3) if self.current_player_turn == 1 else (7,8,9)
        valid_cells = [(rr,cc) for rr in valid_rows for cc in (3,4,5)]

        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS and self.cells[r][c] is None and (r,c) in valid_cells:
            try:
                die.pack_forget()
            except Exception:
                pass
            cx = c*CELL_SIZE + CELL_SIZE//2
            cy = r*CELL_SIZE + CELL_SIZE//2
            win = self.canvas.create_window(cx, cy, window=die)
            die._canvas_window = win
            die._grid_pos = (r,c)
            die.locked = True
            self.cells[r][c] = die
            die.set_selected(False)
            self.selected_die = None

            self.current_player_turn = 2 if self.current_player_turn == 1 else 1
            self.turn_label.config(text=f"Turno: Jogador {self.current_player_turn}")

            self.update_scores()
            self.check_game_over()  # Verifica se o jogo terminou

    def calculate_score(self, rows):
        total = 0
        for c in (3,4,5):
            values = []
            for r in rows:
                die = self.cells[r][c]
                if die:
                    values.append(die.value)
            for v in values:
                count = values.count(v)
                total += v * count
        return total

    def update_scores(self):
        total1 = self.calculate_score([1,2,3])
        total2 = self.calculate_score([7,8,9])
        self.score_label_p1.config(text=f"Jogador 1\nPONTUAÇÃO: {total1}")
        self.score_label_p2.config(text=f"Jogador 2\nPONTUAÇÃO: {total2}")

        for rows in [(1,2,3),(7,8,9)]:
            for c in (3,4,5):
                value_counts = {}
                for r in rows:
                    die = self.cells[r][c]
                    if die:
                        value_counts.setdefault(die.value, []).append(die)
                for dies in value_counts.values():
                    if len(dies) == 2:
                        color = '#FFFF99'
                    elif len(dies) == 3:
                        color = '#ADD8E6'
                    else:
                        color = None
                    if color:
                        for die in dies:
                            x0 = die._grid_pos[1]*CELL_SIZE
                            y0 = die._grid_pos[0]*CELL_SIZE
                            x1 = x0+CELL_SIZE
                            y1 = y0+CELL_SIZE
                            self.canvas.create_rectangle(x0,y0,x1,y1, fill=color, outline='black', width=2)
                            die.draw_die()

    # --- Verifica se o jogo acabou ---
    def check_game_over(self):
        top_full = all(self.cells[r][c] is not None for r in (1,2,3) for c in (3,4,5))
        bottom_full = all(self.cells[r][c] is not None for r in (7,8,9) for c in (3,4,5))
        if top_full or bottom_full:
            self.show_game_over()

    def show_game_over(self):
        total1 = self.calculate_score([1,2,3])
        total2 = self.calculate_score([7,8,9])
        if total1 > total2:
            winner_text = "Jogador 1 venceu!"
        elif total2 > total1:
            winner_text = "Jogador 2 venceu!"
        else:
            winner_text = "Empate!"

        game_over_window = tk.Toplevel(self)
        game_over_window.title("Fim de Jogo")
        tk.Label(game_over_window, text="FIM DE JOGO", font=("Arial", 24, "bold")).pack(pady=10)
        tk.Label(game_over_window, text=f"Pontuação Jogador 1: {total1}", font=("Arial", 14)).pack(pady=5)
        tk.Label(game_over_window, text=f"Pontuação Jogador 2: {total2}", font=("Arial", 14)).pack(pady=5)
        tk.Label(game_over_window, text=winner_text, font=("Arial", 16, "bold")).pack(pady=10)
        tk.Button(game_over_window, text="Fechar", command=self.destroy, width=15).pack(pady=10)


if __name__ == '__main__':
    app = BoardApp()
    app.mainloop()
