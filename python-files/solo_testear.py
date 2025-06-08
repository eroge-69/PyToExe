import tkinter as tk

# Lista de elementos básicos
BASIC_ELEMENTS = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
                  "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Ga", "Ge",
                  "As", "Se", "Br", "Kr", "Rb", "Sr", "In", "Sn", "Sb", "Te", "I", "Xe",
                  "Cs", "Ba", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra"]

# Datos de la tabla periódica con nombres completos
ELEMENTS = [
    ("H", 0, 0, "Hydrogen"), ("He", 17, 0, "Helium"),
    ("Li", 0, 1, "Lithium"), ("Be", 1, 1, "Beryllium"), ("B", 12, 1, "Boron"), 
    ("C", 13, 1, "Carbon"), ("N", 14, 1, "Nitrogen"), ("O", 15, 1, "Oxygen"), 
    ("F", 16, 1, "Fluorine"), ("Ne", 17, 1, "Neon"),
    ("Na", 0, 2, "Sodium"), ("Mg", 1, 2, "Magnesium"), ("Al", 12, 2, "Aluminium"), 
    ("Si", 13, 2, "Silicon"), ("P", 14, 2, "Phosphorus"), ("S", 15, 2, "Sulfur"), 
    ("Cl", 16, 2, "Chlorine"), ("Ar", 17, 2, "Argon"),
    ("K", 0, 3, "Potassium"), ("Ca", 1, 3, "Calcium"), ("Sc", 2, 3, "Scandium"), 
    ("Ti", 3, 3, "Titanium"), ("V", 4, 3, "Vanadium"), ("Cr", 5, 3, "Chromium"), 
    ("Mn", 6, 3, "Manganese"), ("Fe", 7, 3, "Iron"), ("Co", 8, 3, "Cobalt"), 
    ("Ni", 9, 3, "Nickel"), ("Cu", 10, 3, "Copper"), ("Zn", 11, 3, "Zinc"),
    ("Ga", 12, 3, "Gallium"), ("Ge", 13, 3, "Germanium"), ("As", 14, 3, "Arsenic"), 
    ("Se", 15, 3, "Selenium"), ("Br", 16, 3, "Bromine"), ("Kr", 17, 3, "Krypton"),
    ("Rb", 0, 4, "Rubidium"), ("Sr", 1, 4, "Strontium"), ("Y", 2, 4, "Yttrium"), 
    ("Zr", 3, 4, "Zirconium"), ("Nb", 4, 4, "Niobium"), ("Mo", 5, 4, "Molybdenum"), 
    ("Tc", 6, 4, "Technetium"), ("Ru", 7, 4, "Ruthenium"), ("Rh", 8, 4, "Rhodium"), 
    ("Pd", 9, 4, "Palladium"), ("Ag", 10, 4, "Silver"), ("Cd", 11, 4, "Cadmium"),
    ("In", 12, 4, "Indium"), ("Sn", 13, 4, "Tin"), ("Sb", 14, 4, "Antimony"), 
    ("Te", 15, 4, "Tellurium"), ("I", 16, 4, "Iodine"), ("Xe", 17, 4, "Xenon"),
    ("Cs", 0, 5, "Cesium"), ("Ba", 1, 5, "Barium"), ("La", 2, 5, "Lanthanum"), 
    ("Hf", 3, 5, "Hafnium"), ("Ta", 4, 5, "Tantalum"), ("W", 5, 5, "Tungsten"), 
    ("Re", 6, 5, "Rhenium"), ("Os", 7, 5, "Osmium"), ("Ir", 8, 5, "Iridium"), 
    ("Pt", 9, 5, "Platinum"), ("Au", 10, 5, "Gold"), ("Hg", 11, 5, "Mercury"),
    ("Tl", 12, 5, "Thallium"), ("Pb", 13, 5, "Lead"), ("Bi", 14, 5, "Bismuth"), 
    ("Po", 15, 5, "Polonium"), ("At", 16, 5, "Astatine"), ("Rn", 17, 5, "Radon"),
    ("Fr", 0, 6, "Francium"), ("Ra", 1, 6, "Radium"), ("Ac", 2, 6, "Actinium"), 
    ("Rf", 3, 6, "Rutherfordium"), ("Db", 4, 6, "Dubnium"), ("Sg", 5, 6, "Seaborgium"), 
    ("Bh", 6, 6, "Bohrium"), ("Hs", 7, 6, "Hassium"), ("Mt", 8, 6, "Meitnerium"), 
    ("Ds", 9, 6, "Darmstadtium"), ("Rg", 10, 6, "Roentgenium"), ("Cn", 11, 6, "Copernicium"),
    ("Nh", 12, 6, "Nihonium"), ("Fl", 13, 6, "Flerovium"), ("Mc", 14, 6, "Moscovium"), 
    ("Lv", 15, 6, "Livermorium"), ("Ts", 16, 6, "Tennessine"), ("Og", 17, 6, "Oganesson")
]

symbol_to_info = {s: {"col": col, "row": row, "name": name} for (s, col, row, name) in ELEMENTS}

class PeriodicTableGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Juego de la Tabla Periódica")
        self.selected_elements = set()
        self.incorrect_answers = []

        # Frame principal
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(padx=10, pady=10)

        tk.Label(self.main_frame, text="Selecciona los elementos que quieras estudiar:").pack()

        # Botón para seleccionar básicos
        tk.Button(self.main_frame, text="Básicos", command=self.select_basics).pack(pady=5)

        # Tabla periódica
        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.pack()
        self.create_table()

        # Botón para iniciar juego
        tk.Button(self.main_frame, text="Iniciar Juego", command=self.open_mode_selection).pack(pady=10)

        # Feedback
        self.feedback_label = tk.Label(self.main_frame, text="", fg="blue")
        self.feedback_label.pack()

        # Variables dinámicas
        self.game_widgets = []

    def create_table(self):
        self.buttons = {}
        for (symbol, col, row, name) in ELEMENTS:
            btn = tk.Button(self.table_frame, text=symbol, width=5, relief=tk.RAISED,
                            command=lambda s=symbol: self.toggle_element(s))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons[symbol] = btn

    def toggle_element(self, symbol):
        if symbol in self.selected_elements:
            self.selected_elements.remove(symbol)
            self.buttons[symbol].config(relief=tk.RAISED, bg="SystemButtonFace")
        else:
            self.selected_elements.add(symbol)
            self.buttons[symbol].config(relief=tk.SUNKEN, bg="lightblue")

    def select_basics(self):
        for element in BASIC_ELEMENTS:
            if element in self.buttons:
                self.selected_elements.add(element)
                self.buttons[element].config(relief=tk.SUNKEN, bg="lightblue")

    def open_mode_selection(self):
        if not self.selected_elements:
            self.feedback_label.config(text="Debes seleccionar al menos un elemento.", fg="red")
            return

        self.clear_game_widgets()

        self.mode_frame = tk.Frame(self.main_frame)
        self.mode_frame.pack(pady=10)
        self.game_widgets.append(self.mode_frame)

        tk.Label(self.mode_frame, text="¿Qué quieres aprender?").pack()
        tk.Button(self.mode_frame, text="Nombre", width=20,
                  command=lambda: self.start_game("name")).pack(pady=5)
        tk.Button(self.mode_frame, text="Posición", width=20,
                  command=lambda: self.choose_position_mode()).pack(pady=5)

    def choose_position_mode(self):
        self.clear_game_widgets()

        self.position_frame = tk.Frame(self.main_frame)
        self.position_frame.pack(pady=10)
        self.game_widgets.append(self.position_frame)

        tk.Label(self.position_frame, text="¿Cómo quieres practicar las posiciones?").pack()
        tk.Button(self.position_frame, text="Buscar posición por nombre", width=25,
                  command=lambda: self.start_game("name_to_position")).pack(pady=5)
        tk.Button(self.position_frame, text="Buscar nombre por posición", width=25,
                  command=lambda: self.start_game("position_to_name")).pack(pady=5)

    def start_game(self, mode):
        self.mode = mode
        self.current_questions = list(self.selected_elements.copy())
        self.incorrect_answers = []
        self.clear_game_widgets()

        if mode == "name":
            self.setup_name_mode()
        elif mode in ["name_to_position", "position_to_name"]:
            self.setup_position_mode(mode)

    def setup_name_mode(self):
        self.show_next_name_question()

    def show_next_name_question(self):
        if not self.current_questions:
            self.show_summary()
            return

        self.current_element = self.current_questions.pop(0)
        info = symbol_to_info[self.current_element]
        self.correct_name = info["name"]

        self.name_frame = tk.Frame(self.main_frame)
        self.name_frame.pack(pady=10)
        self.game_widgets.append(self.name_frame)

        tk.Label(self.name_frame, text=f"Escribe el nombre para: {self.current_element}", font=("Arial", 14)).pack()
        self.answer_entry = tk.Entry(self.name_frame, font=("Arial", 14))
        self.answer_entry.pack(pady=5)
        tk.Button(self.name_frame, text="Enviar", command=self.handle_name_submit).pack(pady=5)

    def handle_name_submit(self):
        user_input = self.answer_entry.get().strip()
        correct = user_input.lower() == self.correct_name.lower()
        color = "green" if correct else "red"
        self.feedback_label.config(text="Correcto!" if correct else f"Incorrecto. Era: {self.correct_name}.", fg=color)

        if not correct:
            self.incorrect_answers.append(self.current_element)

        self.name_frame.destroy()
        self.master.after(1000, self.show_next_name_question)

    def setup_position_mode(self, submode):
        self.submode = submode
        self.current_questions = list(self.selected_elements.copy())
        self.incorrect_answers = []
        self.clear_game_widgets()

        # Mostrar tabla periódica modificable
        self.position_game_frame = tk.Frame(self.main_frame)
        self.position_game_frame.pack(pady=10)
        self.game_widgets.append(self.position_game_frame)

        self.question_label = tk.Label(self.position_game_frame, text="", font=("Arial", 14))
        self.question_label.pack()

        self.table_in_game_frame = tk.Frame(self.position_game_frame)
        self.table_in_game_frame.pack()

        self.cell_widgets = {}
        for (symbol, col, row, name) in ELEMENTS:
            cell = tk.Button(self.table_in_game_frame, text="", width=5, height=2,
                             command=lambda c=col, r=row: self.handle_position_click(c, r))
            cell.grid(row=row, column=col, padx=2, pady=2)
            self.cell_widgets[(col, row)] = cell

        if self.submode == "position_to_name":
            self.answer_entry = tk.Entry(self.position_game_frame, font=("Arial", 14))
            self.answer_entry.pack(pady=5)
            tk.Button(self.position_game_frame, text="Enviar", command=self.handle_position_name_submit).pack(pady=5)

        self.show_next_position_question()

    def show_next_position_question(self):
        if not self.current_questions:
            self.show_summary()
            return

        self.current_element = self.current_questions.pop(0)
        info = symbol_to_info[self.current_element]
        self.correct_col, self.correct_row, self.correct_name = info["col"], info["row"], info["name"]

        if self.submode == "name_to_position":
            self.question_label.config(text=f"{self.correct_name} ({self.current_element})")
        elif self.submode == "position_to_name":
            self.question_label.config(text="Ingresa el símbolo del elemento resaltado:")
            self.highlighted_cell = self.cell_widgets[(self.correct_col, self.correct_row)]
            self.original_bg = self.highlighted_cell.cget("bg")
            self.highlighted_cell.config(bg="red")

    def handle_position_click(self, col, row):
        if self.submode != "name_to_position":
            return

        correct = (col == self.correct_col) and (row == self.correct_row)
        cell = self.cell_widgets[(col, row)]

        for other_cell in self.cell_widgets.values():
            other_cell.config(state=tk.DISABLED)

        if correct:
            cell.config(text=self.current_element, bg="green")
            self.feedback_label.config(text="¡Correcto!", fg="green")
        else:
            cell.config(bg="red")
            target_cell = self.cell_widgets[(self.correct_col, self.correct_row)]
            target_cell.config(text=self.current_element, bg="green")
            self.feedback_label.config(text=f"Incorrecto. Era: {self.current_element}", fg="red")
            self.incorrect_answers.append(self.current_element)

        self.master.after(1000, self.reset_game_board)

    def handle_position_name_submit(self):
        user_input = self.answer_entry.get().strip()
        correct = user_input == self.current_element
        if correct:
            self.cell_widgets[(self.correct_col, self.correct_row)].config(
                text=self.current_element, bg="green")
            self.feedback_label.config(text="¡Correcto!", fg="green")
        else:
            self.cell_widgets[(self.correct_col, self.correct_row)].config(
                text=self.current_element, bg="green")
            self.feedback_label.config(text=f"Incorrecto. Era: {self.current_element}", fg="red")
            self.incorrect_answers.append(self.current_element)

        for cell in self.cell_widgets.values():
            cell.config(state=tk.DISABLED)

        self.master.after(1000, self.reset_game_board)

    def reset_game_board(self):
        for cell in self.cell_widgets.values():
            cell.config(text="", bg="SystemButtonFace", state=tk.NORMAL)
        self.feedback_label.config(text="")
        self.show_next_position_question()

    def show_summary(self):
        self.feedback_label.config(text="¡Has terminado todas las preguntas!", fg="green")
        retry = tk.Button(self.main_frame, text="Reintentar solo errores", command=self.retry_incorrect)
        retry.pack(pady=10)
        self.game_widgets.append(retry)

    def retry_incorrect(self):
        self.current_questions = self.incorrect_answers.copy()
        self.incorrect_answers = []
        if self.mode == "name":
            self.show_next_name_question()
        else:
            self.setup_position_mode(self.submode)

    def clear_game_widgets(self):
        for widget in self.game_widgets:
            widget.destroy()
        self.game_widgets.clear()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = PeriodicTableGame(root)
    root.mainloop()