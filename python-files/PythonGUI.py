import tkinter as tk

# Create main window
root = tk.Tk()
root.title("Interactive Rectangle (Press 1–6)")

# Canvas setup
canvas_width = 400
canvas_height = 300
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Rectangle position and size
x, y, w, h = 50, 50, 300, 150
cell_w = w / 3
cell_h = h / 2

# Draw grid
canvas.create_rectangle(x, y, x + w, y + h, outline="black", width=2)
# Vertical lines
canvas.create_line(x + cell_w, y, x + cell_w, y + h, width=2)
canvas.create_line(x + 2 * cell_w, y, x + 2 * cell_w, y + h, width=2)
# Horizontal line
canvas.create_line(x, y + cell_h, x + w, y + cell_h, width=2)

# Create a list of rectangles (store their canvas IDs)
# Index 0 = bottom-left box (box 1)
boxes = []
for r in range(2):  # 0=top, 1=bottom
    for c in range(3):  # left to right
        cell_x1 = x + c * cell_w
        cell_y1 = y + r * cell_h
        cell_x2 = cell_x1 + cell_w
        cell_y2 = cell_y1 + cell_h
        rect = canvas.create_rectangle(cell_x1+1, cell_y1+1, cell_x2-1, cell_y2-1, fill="white", outline="")
        boxes.append(rect)

# Reverse so bottom row comes first (1–3 bottom, 4–6 top)
boxes = [boxes[3], boxes[4], boxes[5], boxes[0], boxes[1], boxes[2]]

# Function to color box when number key is pressed
def key_pressed(event):
    if event.char in "123456":
        index = int(event.char) - 1
        canvas.itemconfig(boxes[index], fill="green")

# Bind key press events
root.bind("<Key>", key_pressed)

root.mainloop()
