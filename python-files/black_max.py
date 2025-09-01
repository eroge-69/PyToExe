import tkinter as tk
import sys

def create_black_screen():

    root = tk.Tk()

    root.overrideredirect(True)

    root.attributes('-topmost', True)
    
    root.configure(bg='black')
    
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    
    label = tk.Label(
        root,
        text="", 
        bg='black',  
        fg='black'  
    )

    label.pack(fill=tk.BOTH, expand=True)
    
    def close_app(event=None):
        root.destroy() 
        # sys.exit()
    
    root.bind('<Escape>', close_app) 
    
    root.mainloop()

if __name__ == "__main__":
    create_black_screen()