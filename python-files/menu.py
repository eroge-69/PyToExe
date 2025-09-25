import tkinter as tk
import os
import platform
import subprocess

def shutdown():
    """
    מבצע כיבוי של המחשב בהתאם למערכת ההפעלה.
    """
    system_name = platform.system()
    if system_name == "Windows":
        os.system("shutdown /s /t 0")
    elif system_name in ["Linux", "Darwin"]:  # Darwin = macOS
        os.system("shutdown now")
    else:
        print("מערכת ההפעלה לא נתמכת.")

def option1():
    """
    פונקציית כיבוי המחשב עבור כפתור 1.
    """
    shutdown()

def option2():
    """
    פונקציה המנסה להריץ קובץ בשם VAR.exe הממוקם באותה התיקייה.
    """
    exe_name = "VAR.exe"
    # משיג את הנתיב המלא של התיקייה הנוכחית.
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # בונה את הנתיב המלא לקובץ VAR.exe.
    exe_path = os.path.join(current_directory, exe_name)
    
    if os.path.exists(exe_path):
        subprocess.Popen(exe_path)
        root.destroy()  # סוגר את החלון הנוכחי
    else:
        label.config(text=f"לא נמצא {exe_name}")
        print(f"File not found: {exe_path}")

def option3():
    """
    פונקציית כיבוי המחשב עבור כפתור 3.
    """
    shutdown()

def option4():
    """
    פונקציית כיבוי המחשב עבור כפתור 4.
    """
    shutdown()

# יצירת חלון
root = tk.Tk()
root.title("ברוך הבא")
root.geometry("300x250")

# כותרת
label = tk.Label(root, text="ברוך הבא!\nבחר אפשרות:", font=("Arial", 14))
label.pack(pady=20)

# כפתורים
btn1 = tk.Button(root, text="חמישית", width=20, height=2, command=option1)
btn1.pack(pady=5)

btn2 = tk.Button(root, text="שישית", width=20, height=2, command=option2)
btn2.pack(pady=5)

btn3 = tk.Button(root, text="שביעית", width=20, height=2, command=option3)
btn3.pack(pady=5)

btn4 = tk.Button(root, text="שמינית", width=20, height=2, command=option4)
btn4.pack(pady=5)

# הפעלת הלולאה
root.mainloop()