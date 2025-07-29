import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import win32gui
import win32con

def toggle_always_on_top():
    try:
        # Get the selected window title
        selected_window = window_listbox.get(window_listbox.curselection())
        hwnd = gw.getWindowsWithTitle(selected_window)[0]._hWnd

        # Check current state
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if ex_style & win32con.WS_EX_TOPMOST:
            # Remove always-on-top
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            messagebox.showinfo("Success", f"'{selected_window}' is no longer always on top.")
        else:
            # Set always-on-top
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            messagebox.showinfo("Success", f"'{selected_window}' is now always on top.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def refresh_window_list():
    window_listbox.delete(0, tk.END)
    for window in gw.getAllTitles():
        if window.strip():  # Exclude empty titles
            window_listbox.insert(tk.END, window)

def m_toggle_always_on_top(): # for GUI itself
    global always_on_top
    always_on_top = not always_on_top
    root.attributes("-topmost", always_on_top)
    keep_on_top_button.config(text="Disable Always on Top" if always_on_top else "Enable Always on Top")


# Global variable to track "always on top" state GUI itself
always_on_top = False

# Create the main GUI window
root = tk.Tk()
root.title("Always On Top Manager")

# Create a listbox to display windows
window_listbox = tk.Listbox(root, width=53, height=15)
window_listbox.pack(pady=10)

# Create a button to toggle always-on-top
toggle_button = tk.Button(root, text="Toggle Always On Top for the apps in th window above", command=toggle_always_on_top)
toggle_button.pack(pady=5)

# Create the "Keep on Top" button for the GUI itself
keep_on_top_button = tk.Button(root, text="Enable Always on Top", command=m_toggle_always_on_top)
keep_on_top_button.pack(pady=10)

# Create a button to refresh the window list
refresh_button = tk.Button(root, text="Refresh Window List", command=refresh_window_list)
refresh_button.pack(pady=5)

# Populate the window list on startup
refresh_window_list()

# Run the GUI event loop
root.mainloop()
