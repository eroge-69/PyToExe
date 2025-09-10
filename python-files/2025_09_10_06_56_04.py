from tkinter import *
from PIL import Image, ImageTk
import tkinter.messagebox as mb

class CinemaHall:
    def __init__(self, rows=10, seats_per_row=15):
        self.rows = rows
        self.seats_per_row = seats_per_row
        self.seating = [[True for _ in range(seats_per_row)] for _ in range(rows)]
        
    def display_seating(self, canvas):
        canvas.delete("all")
        canvas.create_text(20, 20, text="Схема зала:", font=("Arial", 14))
        
        # Отображение номеров мест
        for i in range(1, self.seats_per_row + 1):
            canvas.create_text(50 + i * 30, 50, text=str(i), font=("Arial", 12))
            
        # Отображение схемы мест
        for row in range(self.rows):
            for seat in range(self.seats_per_row):
                x = 50 + seat * 30
                y = 80 + row * 30
                if self.seating[row][seat]:
                    color = "green"  # Свободное место
                else:
                    color = "red"    # Занятое место
                canvas.create_rectangle(x, y, x+25, y+25, fill=color, outline="black")
                canvas.create_text(x+12, y+15, text=f"{row+1}:{seat+1}", font=("Arial", 8))
                
    def book_seat(self, row, seat):
        if row < 1 or row > self.rows or seat < 1 or seat > self.seats_per_row:
            mb.showerror("Ошибка", "Неверный номер места!")
            return False
        if not self.seating[row-1][seat-1]:
            mb.showerror("Ошибка", "Место уже занято!")
            return False
        self.seating[row-1][seat-1] = False
        mb.showinfo("Успех", f"Место {row}:{seat} успешно забронировано!")
        return True

    def get_statistics(self):
        total_seats = self.rows * self.seats_per_row
        free_seats = sum(sum(row) for row in self.seating)
        occupied_seats = total_seats - free_seats
        return {
            'total': total_seats,
            'free': free_seats,
            'occupied': occupied_seats,
            'percent': (occupied_seats / total_seats) * 100
        }

def main():
    root = Tk()
    root.title("Система бронирования мест в кинотеатре")
    root.geometry("800x600")
    
    # Загрузка фонового изображения
    try:
        bg_image = Image.open("background.png")
        bg_image = bg_image.resize((800, 600), Image.ANTIALIAS)
        bg_photo = ImageTk.PhotoImage(bg_image)
    except FileNotFoundError:
        bg_photo = None
        
    canvas = Canvas(root, width=800, height=600)
    canvas.pack(fill=BOTH, expand=True)
    
    if bg_photo:
        canvas.create_image(0, 0, image=bg_photo, anchor=NW)
        canvas.image = bg_photo  # Сохраняем ссылку на изображение
        
    hall = CinemaHall()
    
    def book_seat():
        try:
            row = int(entry_row.get())
            seat = int(entry_seat.get())
            hall.book_seat(row, seat)
            hall.display_seating(canvas)
        except ValueError:
            mb.showerror("Ошибка", "Неверный формат ввода!")
            
    def show_stats():
        stats = hall.get_statistics()
        message = (
            f"Статистика зала:\n"
            f"Всего мест: {stats['total']}\n"
            f"Свобо