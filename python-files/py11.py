import winsound
import random
import tkinter as tk

# ����� ������� � ������������ ������
frequencies = [500, 1000, 100, 2000]
durations = [550, 500, 1500]

while True:
    # �������� ��������� ��������
    freq = random.choice(frequencies)
    dur = random.choice(durations)
    
    # ������������� ����
    winsound.Beep(freq, dur)
    window = tk.Tk()
    # ������� ����
root = tkk.Tk()
root.title("Random Error Icons")
root.geometry("800x600")

# ������ ���������� ������� ������ Windows
icons = [
    tk.PhotoImage(file="@error"),  # ������ ������
    tk.PhotoImage(file="@warning"),  # ������ ��������������
    tk.PhotoImage(file="@info")  # ������ ����������
]

# ������� ��� ����������� ���������� ������
def show_random_icon(event):
    x, y = event.x, event.y
    icon = random.choice(icons)
    label = tk.Label(root, image=icon)
    label.image = icon  # ��������� ������ �� �����������
    label.place(x=x, y=y)
    root.after(6000, label.destroy)  # ������� ������ ����� 1 �������

# ����������� ������� �������� ����
root.bind("<Motion>", show_random_icon)

# ��������� �������� ����
root.mainloop()