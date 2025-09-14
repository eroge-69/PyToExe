import tkinter as tk
import webbrowser
from tkinter import messagebox

class LinkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("app test")
        self.root.geometry("500x300")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Anatoli's bumfuck atrocious code", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Link display frame
        link_frame = tk.Frame(self.root)
        link_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Sample links with descriptions
        links = [
            ("Mitski Tracker", "https://docs.google.com/spreadsheets/d/1Vbj-En7Acqeh0yJ9kgCaWzNyKof-jPjTm5nruRk-YI8/edit?gid=0#gid=0"),
            ("Carti Tracker", "https://docs.google.com/spreadsheets/d/1rAU0sktd1GKpqo_AAWBtkXy10Px3BB_dnK9yJoN0umw/htmlview"),
            ("Kanye Tracker", "https://docs.google.com/spreadsheets/d/1tEs5GFu7grxliQAQQjX9_gQx9BnoLn2KvC1mmGUPA9w/edit?gid=199908479#gid=199908479"),
            ("SoundCloud", "https://soundcloud.com/discover")
        ]
        
        for text, url in links:
            self.create_link_button(link_frame, text, url)
        
        # Custom link entry
        self.setup_custom_link()
    
    def create_link_button(self, parent, text, url):
        """Create a clickable link button"""
        btn = tk.Button(parent, text=text, fg="blue", cursor="hand2",
                       command=lambda: self.open_link(url))
        btn.pack(pady=5, anchor="w")
        
        # Add URL label
        url_label = tk.Label(parent, text=url, fg="gray", font=("Arial", 8))
        url_label.pack(anchor="w", padx=20)
    
    def open_link(self, url):
        """Open link in default browser"""
        webbrowser.open_new(url)
        print(f"Opened: {url}")
    
    def setup_custom_link(self):
        """Setup for custom URL entry"""
        custom_frame = tk.Frame(self.root)
        custom_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Label(custom_frame, text="Enter custom URL:").pack(anchor="w")
        
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(custom_frame, textvariable=self.url_var, width=40)
        url_entry.pack(side="left", padx=5)
        
        open_btn = tk.Button(custom_frame, text="Open", 
                           command=self.open_custom_link)
        open_btn.pack(side="left")

    def open_custom_link(self):
        """Open custom URL from entry"""
        url = self.url_var.get().strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            self.open_link(url)
        else:
            messagebox.showwarning("Input Error", "Please enter a URL")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkGUI(root)
    root.mainloop()