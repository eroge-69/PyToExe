import tkinter as tk

win = tk.Tk()
win.title("質數篩選器")
win.geometry("600x260")
win.config(bg = "#efee8d")

def go():
  s = int(dataEntry.get())
  a = 2
  r = s % a
  
  while s > a:
         r = s % a
         if r == 0:
            lbl['text'] = (s, '是合成數'  )
            break
         a += 1
  else:
        lbl['text'] = (s, '是質數'  )
      
title = tk.Label (win,
                  text = ("請輸入數字"),
                  bg = "#efee8d",
                  fg = "#b88bf3",
                  width = 50,
                  font = ("Arial", 20, "bold"))
title.pack ()

dataEntry = tk.Entry(win,
              bg = "white",
              fg = "#9f6dea",
              width = 30,
              font = ("Arial", 20))
dataEntry.focus()              
dataEntry.pack()

btn = tk.Button (win,
                bg = "#caf0f7",
                fg = "#fc8787",
                width = 20,
                text = "開始檢測",
                font = ("Arial", 23, "bold"),
                command = go)
btn.pack()

lbl = tk.Label ( win,
                bg = "lightblue",
                fg = "white",
                width = 35,
                font = ("Arial", 23))
lbl.pack()

win.mainloop()
