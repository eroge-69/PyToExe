import tkinter
import random
game=['با لگو ماشین بساز ','ده تا دراز نشست برو','قسمت اول روبیک رو حل کن ','یه نقاشی از یک بازی بکش','با لگو تفنگ بساز','با اسکرچ یک برنامه بساز که یک گربه ده قدم راه بره و بگه مییووو','با لگوبستنی بساز','با پلی استیشن به منتخب جهان در فوتبال 2 گل بزن','10 بار بافیکس برو','پوچ','10 صفحه کتاب بخون']
def chalesh():
    a=(random.randint(0,9))
    # (game[a])
    lblr.config (text="                     "+game[a]+"                     ")
win=tkinter.Tk()
win.config(bg="#aaf956")
win.title("chalesh")
win.iconbitmap('chatgpt.ico')
win.geometry("700x200")
lblr=tkinter.Label(bg="#aaf956",font=("B Mitra",20),fg="#0004FF",text="                          هنوز انتخاب نکردید                           " )
lblr.grid(row=2,column=4)
btngame=tkinter.Button(win,bg="#FFFFFF",text="محمد صادق انتخاب کن",command=chalesh)
btngame.grid(row=3,column=4,padx=2,pady=2)
win.mainloop()