import tkinter as tk
from time import strftime

#创建主窗口
root = tk.Tk()
root.title("桌面大时钟")
root.attributes("-tompost",true) 	#始终在最前面
root.configure(bg="black")			#背景颜色
root.geometry("400x150")			#窗口大小

#时间显示标签
label = tk.Label(root,font=("Arial",48),bg="black",fg="cyan")
label.pack(expand=True)

#更新时间函数
def update_time():
	current_time= strftime("%H:%M:%S")	#24小时制，也可以用%I:%M:%S %p 12小时制
	label.configure(text=current_time)
	label.after(1000,update_time)			#每1000毫秒刷新一次
update_time()
root.mainloop()