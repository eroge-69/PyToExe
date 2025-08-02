"code-keyword">import tkinter "code-keyword">as tk
"code-keyword">from tkinter "code-keyword">import ttk
"code-keyword">from gui.main_window "code-keyword">import MainWindow
"code-keyword">from utils.logger "code-keyword">import setup_logger
"code-keyword">import logging

"code-keyword">class="code-keyword">def main():
    setup_logger()
    logging.info("Application starting...")

    root = tk.Tk()
    root.title("Photo Organizer")
    root.geometry("800x600") # Initial size

    main_window = MainWindow(root)
    root.mainloop()

    logging.info("Application exiting...")

"code-keyword">if __name__ == "__main__":
    main()
