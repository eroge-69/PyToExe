import pytesseract
import pyautogui
import sympy
from tkinter import *
from PIL import ImageGrab

# Set the path to tesseract.exe (change this if yours is installed somewhere else)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to capture screen, solve question, and type answer
def solve_question():
    # Capture screen region where Sparx question appears
    print("📸 Capturing screen...")
    x, y, width, height = 500, 300, 800, 200  # Adjust these values to match your browser window
    img = ImageGrab.grab(bbox=(x, y, x + width, y + height))

    # Use OCR to extract question text
    question_text = pytesseract.image_to_string(img)
    print("📝 Detected question:", question_text.strip())

    try:
        # Attempt to solve the maths question
        expr = sympy.sympify(question_text)
        answer = sympy.solve(expr)
        print("✅ Answer:", answer)

        # Type the answer into the browser automatically
        pyautogui.typewrite(str(answer[0]))
        pyautogui.press("enter")
        print("🚀 Answer entered into Sparx!")
    except Exception as e:
        print("❌ Error solving question:", e)

# Build GUI
root = Tk()
root.title("Sparx Auto Solver")
root.geometry("300x150")

solve_btn = Button(root, text="Solve Question", font=("Arial", 16), command=solve_question)
solve_btn.pack(expand=True)

root.mainloop()