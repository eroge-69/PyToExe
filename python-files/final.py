import tkinter as tk
import datetime

# Segment coordinates
segments = {
    'A': ((15, 0), (45, 0), (50, 5), (45, 10), (15, 10), (10, 5)),
    'B': ((50, 10), (55, 5), (60, 10), (60, 50), (55, 55), (50, 50)),
    'C': ((50, 60), (55, 55), (60, 60), (60, 100), (55, 105), (50, 100)),
    'D': ((15, 100), (45, 100), (50, 105), (45, 110), (15, 110), (10, 105)),
    'E': ((0, 60), (5, 55), (10, 60), (10, 100), (5, 105), (0, 100)),
    'F': ((0, 10), (5, 5), (10, 10), (10, 50), (5, 55), (0, 50)),
    'G': ((15, 50), (45, 50), (50, 55), (45, 60), (15, 60), (10, 55)),
    '/': ((5, 110), (25, 0), (35, 0), (15, 110))  # Diagonal slash coordinates
}

# Segment mapping per digit or symbol
digits = {
    '0': 'ABCDEF',
    '1': 'BC',
    '2': 'ABGED',
    '3': 'ABGCD',
    '4': 'FGBC',
    '5': 'AFGCD',
    '6': 'AFGECD',
    '7': 'ABC',
    '8': 'ABCDEFG',
    '9': 'AFGBC',
    ':': ':',
    '/': '/'
}

# Create window
window = tk.Tk()
window.title("Digital Clock")
canvas = tk.Canvas(window, width=530, height=370, bg="black", highlightthickness=0)
canvas.pack()

# Draw a digit or symbol
def draw_digit_colon(canvas, digit, x_offset, y_offset):
    canvas.create_rectangle(x_offset, y_offset, x_offset+60, y_offset+120, fill="black")
    if digit == ":":
        canvas.create_oval(x_offset+10, y_offset+30, x_offset+20, y_offset+40, fill="green2", outline="black")
        canvas.create_oval(x_offset+10, y_offset+70, x_offset+20, y_offset+80, fill="green2", outline="black")
        return
    elif digit == "/":
        coords = segments['/']
        translated = [(x + x_offset, y + y_offset) for x, y in coords]
        canvas.create_polygon(translated, fill="green2", outline="black")
        return
    for segment in "ABCDEFG":
        if segment in digits.get(digit, ''):
            coords = segments[segment]
            translated = [(x + x_offset, y + y_offset) for x, y in coords]
            canvas.create_polygon(translated, fill="green2", outline="black")

# Update the display
def update_clock():
    canvas.delete("all")
    current_date = datetime.datetime.now().strftime("%m/%d/%y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Name and Section label
    canvas.create_text(270, 20, text="Maninang, Allein Dane G.          CS-301", fill="white", font=("Helvetica", 20, "bold"))
    
    # Date label
    canvas.create_text(50, 60, text="Date:", fill="white", font=("Helvetica", 20, "bold"))

    # Date
    x_date = 20
    for char in current_date:
        draw_digit_colon(canvas, char, x_date, 80)
        if char != "/":
            x_date += 70 
        else:
            x_date += 40

    # Time label
    canvas.create_text(50, 220, text="Time:", fill="white", font=("Helvetica", 20, "bold"))

    # Time
    x_time = 20
    for char in current_time:
        draw_digit_colon(canvas, char, x_time, 240)
        if char != ":":
            x_time += 70  
        else:
            x_time += 40

    window.after(1000, update_clock)

update_clock()
window.mainloop()
