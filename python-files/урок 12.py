import tkinter as tk
import tkinter.messagebox as tkm
def restart():
    if tkm.askyesno("Tic Tac Toe", "Do you want to play again?"):
        global turn
        turn = 0
        for row in field:
            for btn in row:
                btn.config(text = "")
    else:
        window.quit()
def check_win(char):
    if field [0][0]["text"] == char and field[0][1]["text"] == char and field [0][2]["text"] == char:
        return True
    if field [1][0]["text"] == char and field[1][1]["text"] == char and field [1][2]["text"] == char:
        return True
    if field [2][0]["text"] == char and field[2][1]["text"] == char and field [2][2]["text"] == char:
        return True
    if field [0][0]["text"] == char and field[1][0]["text"] == char and field [2][0]["text"] == char:
        return True
    if field [0][1]["text"] == char and field[1][1]["text"] == char and field [2][1]["text"] == char:
        return True
    if field [0][2]["text"] == char and field[1][2]["text"] == char and field [2][2]["text"] == char:
        return True
    if field [0][0]["text"] == char and field[1][1]["text"] == char and field [2][2]["text"] == char:
        return True
    if field [0][2]["text"] == char and field[1][1]["text"] == char and field [2][0]["text"] == char:
        return True
def click(btn):
    global turn
    if btn["text"] != "":
        return
        
    turn = turn + 1
    if turn %2 == 1:
        char = "X"
    else:
        char = "O"
    btn.config(text = char)
    if check_win(char):
        tkm.showinfo("Tic Tac Toe", char + " is winner")
        restart()
    elif turn == 9:
        tkm.showinfo("Tic Tac Toe" ,"Tie")
        restart()
window = tk.Tk()
window.geometry("600x600")
window.title("Tic Tac Toe")
field = []
turn = 0
for i in range(3):
    field.append([])
    for j in range(3):
        button = tk.Button(bg = "#9cfffc", activebackground = "#ff9c9f", font = ("Algerian", 150))
        button.place(x = j * 200, y = i * 200, width = 200, height = 200)
        button.config(command = lambda btn = button: click(btn))
        field[i].append(button)






































window.mainloop()
