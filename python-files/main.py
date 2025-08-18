import tkinter
from ventanas import Login

if __name__ == "__main__":
    app = tkinter.Tk()
    app.withdraw()
    Login()
    app.mainloop()