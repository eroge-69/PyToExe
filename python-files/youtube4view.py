import tkinter as tk
import webview

class MultiViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Мультівіконний відеоплеєр")
        
        self.urls = [tk.StringVar() for _ in range(4)]
        self.frames = []
        
        for i in range(4):
            frame = tk.Frame(root)
            frame.grid(row=i//2, column=i%2, padx=5, pady=5)
            tk.Entry(frame, textvariable=self.urls[i], width=40).pack()
            tk.Button(frame, text="Відкрити", command=lambda i=i: self.open_video(i)).pack()
            self.frames.append(frame)

    def open_video(self, index):
        url = self.urls[index].get()
        if url:
            webview.create_window(f'Вікно {index+1}', url)

root = tk.Tk()
app = MultiViewer(root)
root.mainloop()

