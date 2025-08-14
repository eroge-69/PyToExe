import tkinter as tk
import webview

DEFAULT_HOME = "https://www.google.com"

class MiniBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser (Tkinter + PyWebview)")
        self.root.geometry("1000x700")

        # Navigation frame
        nav_frame = tk.Frame(root)
        nav_frame.pack(fill=tk.X)

        self.url_entry = tk.Entry(nav_frame, font=("Arial", 12))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.url_entry.bind("<Return>", self.load_url)

        go_btn = tk.Button(nav_frame, text="Go", command=self.load_url)
        go_btn.pack(side=tk.LEFT, padx=5)

        home_btn = tk.Button(nav_frame, text="Home", command=lambda: self.navigate(DEFAULT_HOME))
        home_btn.pack(side=tk.LEFT, padx=5)

        # Create a webview window
        self.browser = webview.create_window("Browser", DEFAULT_HOME, width=1000, height=650, resizable=True)
        
        # Run browser in separate thread
        webview.start(gui="tkinter", debug=True)

    def load_url(self, event=None):
        url = self.url_entry.get().strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.navigate(url)

    def navigate(self, url):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.browser.load_url(url)


if __name__ == "__main__":
    root = tk.Tk()
    app = MiniBrowser(root)
