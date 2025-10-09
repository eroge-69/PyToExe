import tkinter as tk
import pyautogui
import time 

def startspam():
    time.sleep(1) 
    for x in range(10):
        pyautogui.write("teamjynxzerjointoday")
        pyautogui.press("enter")

root = tk.Tk()
root.geometry("600x600")  
root.configure(bg="#2c67dd")
button = tk.Button(root, text="start spam🎯", bg="#58f011", command=startspam)
button.pack(pady=20)

root.mainloop()
