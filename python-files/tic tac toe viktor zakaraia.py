import tkinter as tk
from tkinter import messagebox


# Tic-Tac-Toe-ს თამაში Mini-Max ალგორითმის გამოყენებით
# მინიმაქსი გვაძლევს საუკეთესო სვლას, იმის და მიუხედავად, რა სვლას გააკეთებს მეორე მოთამაშე
# f(n) შემფასებელი ფუნქცია არის პირველი მოთამაშისთვის ისეთი პოზიციებისთვის, რომლებიც არ არიან დამამთავრებელი პოზიციები
# f(n)=m1(n)-m2(n), სადაც, m1(n) არის იმ სრული სტრიქონების,სვეტების და დიაგონალების რაოდენობა,რომლებიც  ღიაა  პირველი მოთამაშისთვის,
# ხოლო  m2(n)-მეორესთვის.



def checkBoard(board):  # მოგების პირობის განსაზღვრა
    cb = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8],
          [2, 4, 6]];  # მოგების შესაძლო ვარიანტები

    for i in range(0, 8):
        if (board[cb[i][0]] != 0 and
                board[cb[i][0]] == board[cb[i][1]] and
                board[cb[i][0]] == board[cb[i][2]]):
            return board[cb[i][2]];
    return 0;


# მინი-მაქსის ალგორითმი
def Minimax(board, player):  # იღებს მიმდინარე დაფას
    x = checkBoard(board);  # ეძებს უჯრებს რომლებიც არაა დაკავებული
    # მინიმაქსის პროცედურით შეიძლება მოიძებნოს მოცემული კონკრეტული შემფასებელი ფუნქციის შესაბამისი ოპტიმალური სტრატეგია.
    # ამიტომ ყველა შესაძლო კვანძებიდან, რომლებშიც გადავყავართ მოწინააღმდეგეს, ჩვენ უნდა ამოვარჩიოთ კვანძი მინიმალური შეფასებით
    # და ეს შეფასება მივაწეროთ კვანძს, რომელიც დგას ერთი საფეხურით ზევით და წარმოადგენს შერჩეული კვანძის მშობელ კვანძს.

    # ამ კვანძებში უკვე გადავდივართ ჩვენი სვლების შედეგად, ამიტომ ყველა შესაძლო კვანძებს შორის (რომელთაც ერთი და იგივე მშობელი კვანძი ჰყავთ)
    # უნდა ამოვარჩიოთ კვანძი მაქსიმალური შეფასებებით და ეს შეფასებები გადმოვიტანოთ კიდევ ერთი საფეხურით ზევით (მივაწეროთ მშობელ კვანძს).
    # ასე უნდა გავაგრძელოთ, სანამ არ მივაღწევთ საწყის პოზიციას. ამორჩეული სვლების მიმდევრობა შებრუნებული მიმდევრობით
    # წარმოადგენს სწორედ თამაშის სტრატეგიას.

    # მოკლედ და ტექნიკური ტერმინების გარეშე, რომ განვიხილოთ მინიმაქსის პროცედურა ასეთი იქნება:
    # მინიმაქს ალგორითმი(კომპიუტერი, რომლის წინააღმდეგაც ვთამაშობთ) აფასებს ყველა ჩვენ შესაძლო სვლას.
    # ამ სვლებიდან ირჩევს ჩვენთვის საუკეთესოს და თავად აკეთებს ამ სვლას
    # ანუ გვართმევს ჩვენთვის ყველაზე ოპტიმალურ ვარიანტს
    if (x != 0):
        return (x * player);
    pos = -1;
    value = -2;
    for i in range(0, 9):
        if (board[i] == 0):
            board[i] = player;
            score = -Minimax(board, (player * -1));
            if (score > value):
                value = score;
                pos = i;
            board[i] = 0;

    if (pos == -1):
        return 0;
    return value;  # აბრუნებს ქმედებას შვილობილ კვანძთა სიმრავლეში მნიშვნელობით


def PCTurn(board):  # კომპიუტერი იყენებს მინიმაქსის ალგორითმს ყველაზე ოპტიმალური სვლის ამოსარჩევად
    pos = -1;  # საწყისი პოზიცია იყოს -1
    value = -2;  # და მისი მნიშვნელობა -2
    for i in range(0, 9):
        if (board[i] == 0):
            board[i] = 1;
            score = -Minimax(board, -1);
            board[i] = 0;
            if (score > value):
                value = score;
                pos = i;  # მიენიჭება ყველაზე ოპტიმალური სვლის დანიშნულების ციფრი
    board[pos] = 1;
    return pos


class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Mini-Max ალგორითმით")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # თამაშის ცვლადები
        self.board = [0] * 9  # დაფა (0-თავისუფალი, -1-X, 1-O)
        self.game_over = False  # თამაშის დასრულების მდგომარეობა
        self.game_mode = None  # თამაშის რეჟიმი (1-კომპიუტერი, 2-ორი მოთამაშე)
        self.current_player = -1  # მიმდინარე მოთამაშე (-1-X, 1-O)

        # თამაშის რეჟიმის არჩევის გვერდის შექმნა
        self.create_mode_selection()

    def create_mode_selection(self):
        """თამაშის რეჟიმის არჩევის გვერდი"""
        self.clear_window()  # ფანჯრის გასუფთავება

        # სათაური
        title = tk.Label(self.root, text="Tic Tac Toe", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=20)

        tk.Label(mode_frame, text="აირჩიეთ თამაშის რეჟიმი:", font=("Arial", 14)).pack(pady=10)

        btn_frame = tk.Frame(mode_frame)
        btn_frame.pack(pady=10)

        # ერთი მოთამაშის ღილაკი
        single_btn = tk.Button(btn_frame, text="კომპიუტერთან", font=("Arial", 12),
                               width=15, height=2, command=lambda: self.start_game(1))
        single_btn.pack(side=tk.LEFT, padx=10)

        # ორი მოთამაშის ღილაკი
        multi_btn = tk.Button(btn_frame, text="ორი მოთამაშე", font=("Arial", 12),
                              width=15, height=2, command=lambda: self.start_game(2))
        multi_btn.pack(side=tk.LEFT, padx=10)

        # ინსტრუქცია
        instructions = tk.Label(self.root, text="კომპიუტერი: O\nმოთამაშე: X", font=("Arial", 11))
        instructions.pack(pady=20)

    def start_game(self, mode):
        """თამაშის დაწყება არჩეული რეჟიმით"""
        self.game_mode = mode
        self.current_player = -1  # X ყოველთვის იწყებს

        # ერთი მოთამაშის რეჟიმში ვეკითხებით ვინ იწყებს
        if mode == 1:
            self.ask_who_starts()
        else:
            self.create_board()  # დაფის შექმნა

    def ask_who_starts(self):
        """ვინ იწყებს პირველი? (ერთი მოთამაშის რეჟიმისთვის)"""
        self.clear_window()

        tk.Label(self.root, text="ვინ იწყებს პირველი?", font=("Arial", 14)).pack(pady=20)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        # მოთამაშე (X) იწყებს
        human_btn = tk.Button(btn_frame, text="მოთამაშე (X)", font=("Arial", 12),
                              width=12, height=2, command=lambda: self.start_single_player(-1))
        human_btn.pack(side=tk.LEFT, padx=10)

        # კომპიუტერი (O) იწყებს
        comp_btn = tk.Button(btn_frame, text="კომპიუტერი (O)", font=("Arial", 12),
                             width=12, height=2, command=lambda: self.start_single_player(1))
        comp_btn.pack(side=tk.LEFT, padx=10)

    def start_single_player(self, starter):
        """ერთი მოთამაშის რეჟიმის დაწყება"""
        self.current_player = starter
        self.create_board()  # დაფის შექმნა

        # თუ კომპიუტერი იწყებს, გააკეთოს პირველი სვლა
        if starter == 1:
            self.root.after(500, self.computer_move)

    def create_board(self):
        """თამაშის დაფის შექმნა"""
        self.clear_window()

        # სტატუსის ლეიბლის შექმნა
        self.status_var = tk.StringVar()
        self.update_status()
        status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 14, "bold"))
        status_label.pack(pady=10)

        # დაფის ჩარჩო
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=20)

        self.buttons = []  # ღილაკების სია
        for i in range(9):
            row, col = divmod(i, 3)  # გადაყვანა ინდექსიდან მწკრივ/სვეტში
            # ღილაკის შექმნა
            btn = tk.Button(board_frame, text="", font=("Arial", 24),
                            width=4, height=2, relief="ridge", borderwidth=2,
                            command=lambda idx=i: self.make_move(idx))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(btn)

        # თამაშის ხელახლა დაწყების ღილაკი
        restart_btn = tk.Button(self.root, text="თამაშის ხელახლა დაწყება", font=("Arial", 12),
                                command=self.restart_game)
        restart_btn.pack(pady=20)

    def update_status(self):
        """სტატუსის ლეიბლის განახლება"""
        if self.game_over:  # თამაში დასრულებულია
            winner = checkBoard(self.board)
            if winner == -1:
                self.status_var.set("X მოიგო!")
            elif winner == 1:
                if self.game_mode == 1:
                    self.status_var.set("კომპიუტერმა მოიგო!")
                else:
                    self.status_var.set("O მოიგო!")
            else:
                self.status_var.set("ფრე!")
        else:  # თამაში გრძელდება
            if self.game_mode == 1:  # ერთი მოთამაშის რეჟიმი
                if self.current_player == -1:
                    self.status_var.set("თქვენი სვლა (X)")
                else:
                    self.status_var.set("კომპიუტერის სვლა (O)")
            else:  # ორი მოთამაშის რეჟიმი
                if self.current_player == -1:
                    self.status_var.set("X-ის სვლა")
                else:
                    self.status_var.set("O-ს სვლა")

    def make_move(self, position):
        """მოთამაშის სვლის დამუშავება"""
        # შემოწმება: თამაში დასრულებულია ან უჯრა დაკავებულია
        if self.game_over or self.board[position] != 0:
            return

        # ერთი მოთამაშის რეჟიმში კომპიუტერის სვლის იგნორირება
        if self.game_mode == 1 and self.current_player != -1:
            return

        # სვლის გაკეთება
        self.board[position] = self.current_player
        self.buttons[position].config(text="X", state=tk.DISABLED)

        # თამაშის მდგომარეობის შემოწმება
        self.check_game_state()

        # ერთი მოთამაშის რეჟიმში კომპიუტერის სვლა
        if not self.game_over and self.game_mode == 1:
            self.current_player = 1  # მოთამაშის შეცვლა (კომპიუტერი)
            self.update_status()
            self.root.after(500, self.computer_move)  # კომპიუტერის სვლა ხელოვნური დაყოვნებით
        elif self.game_mode == 2:  # ორი მოთამაშის რეჟიმი
            self.current_player *= -1  # მოთამაშის შეცვლა
            self.update_status()

    def computer_move(self):
        """კომპიუტერის სვლის დამუშავება"""
        # კომპიუტერის სვლის გაკეთება მინიმაქსის ალგორითმით
        pos = PCTurn(self.board)
        self.board[pos] = 1
        self.buttons[pos].config(text="O", state=tk.DISABLED)

        # თამაშის მდგომარეობის შემოწმება
        self.check_game_state()

        # თამაშის გაგრძელება
        if not self.game_over:
            self.current_player = -1  # მოთამაშე X-ზე დაბრუნება
            self.update_status()

    def check_game_state(self):
        """თამაშის დასრულების შემოწმება"""
        # გამარჯვების ან ფრის შემოწმება
        result = checkBoard(self.board)
        if result != 0:  # გამარჯვება
            self.game_over = True
        elif 0 not in self.board:  # ყველა უჯრა დაკავებულია - ფრე
            self.game_over = True

        # ინტერფეისის განახლება
        self.update_status()

        # ღილაკების გამორთვა თამაშის დასრულებისას
        if self.game_over:
            for btn in self.buttons:
                btn.config(state=tk.DISABLED)

    def restart_game(self):
        """თამაშის ხელახლა დაწყება"""
        self.board = [0] * 9  # დაფის გასუფთავება
        self.game_over = False  # თამაშის დასრულების აღდგენა

        # ღილაკების განახლება
        for btn in self.buttons:
            btn.config(text="", state=tk.NORMAL)

        # მოთამაშის აღდგენა
        self.current_player = -1
        self.update_status()

        # თუ კომპიუტერი იწყებს ერთი მოთამაშის რეჟიმში
        if self.game_mode == 1 and self.current_player == 1:
            self.root.after(500, self.computer_move)

    def clear_window(self):
        """ფანჯრის გასუფთავება (ყველა ვიჯეტის წაშლა)"""
        for widget in self.root.winfo_children():
            widget.destroy()


# პროგრამის გაშვება
if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()