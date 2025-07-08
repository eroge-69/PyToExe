import tkinter as tk

# יצירת חלון ראשי
root = tk.Tk()
root.title("הממשק שלי")
root.geometry("300x200")  # רוחב x גובה

# יצירת תווית (Label)
label = tk.Label(root, text="שלום עולם!", font=("Arial", 16))
label.pack(pady=10)

# יצירת תיבת טקסט
entry = tk.Entry(root)
entry.pack(pady=5)

# פונקציית לחצן
def say_hello():
    name = entry.get()
    label.config(text=f"שלום {name}!")

# יצירת לחצן (Button)
button = tk.Button(root, text="אישור", command=say_hello)
button.pack(pady=10)

# הפעלת הלולאה של הממשק
root.mainloop()
