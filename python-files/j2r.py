import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Photos - Image Viewer")
root.configure(bg='black')

# Canvas size
width, height = 400, 400
canvas = tk.Canvas(root, width=width, height=height, bg='white', highlightthickness=0)
canvas.pack()

# Draw the yellow face
canvas.create_oval(50, 50, 350, 350, fill="#ffff66", outline="black", width=3)

# Draw the eyes (small solid black circles)
canvas.create_oval(140, 150, 160, 170, fill="black")  # Left eye
canvas.create_oval(240, 150, 260, 170, fill="black")  # Right eye

# Draw the smile (soft arc like 🙂)
canvas.create_arc(140, 200, 260, 300, start=0, extent=-180, style=tk.ARC, width=4)

# Set fixed window size
root.geometry(f"{width}x{height}")

# Run the app
root.mainloop()



