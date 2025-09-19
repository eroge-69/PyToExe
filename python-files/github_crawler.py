import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time

class GitHubCrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Repository Crawler")
        self.root.state('zoomed')  # Maximized window
        self.root.configure(bg='#1e1e1e')  # Default dark theme
        self.is_dark_mode = True

        self.api_token = self.get_api_token()
        if not self.api_token:
            messagebox.showerror("Error", "API Token is missing. Please set a valid GitHub API Token.")
            root.quit()
            return

        self.base_url = "https://api.github.com"
        self.current_page = 1
        self.current_results = []
        self.total_count = 0
        self.per_page_var = tk.StringVar(value="30")
        self.sort_var = tk.StringVar(value="stars")
        self.current_keywords = ""

        self.create_widgets()

    def get_api_token(self):
        api_token = os.getenv("GITHUB_API_TOKEN", "")
        if not api_token:
            # Prompt user to enter the token if not found in the environment variable
            api_token = self.prompt_for_api_token()
        return api_token

    def prompt_for_api_token(self):
        def on_submit():
            token = token_entry.get()
            if token:
                self.api_token = token
                token_window.destroy()
            else:
                messagebox.showerror("Error", "API Token cannot be empty.")

        token_window = tk.Toplevel(self.root)
        token_window.title("Enter GitHub API Token")
        token_window.geometry("400x150")
        
        prompt_label = ttk.Label(token_window, text="Enter your GitHub API Token:", padding=10)
        prompt_label.pack(pady=10)
        
        token_entry = ttk.Entry(token_window, width=40, show="*")
        token_entry.pack(pady=10)
        token_entry.focus()
        
        submit_button = ttk.Button(token_window, text="Submit", command=on_submit)
        submit_button.pack(pady=10)

        token_window.wait_window(token_window)
        return self.api_token

    def create_widgets(self):
        # Search input
        self.search_label = ttk.Label(self.root, text="Search Query:", background='#1e1e1e', foreground='white')
        self.search_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.search_entry = ttk.Entry(self.root, width=40)
        self.search_entry.grid(row=0, column=1, padx=20, pady=10)

        self.search_button = ttk.Button(self.root, text="Search", command=self.search_repositories, style='Neon.TButton')
        self.search_button.grid(row=0, column=2, padx=20, pady=10)

        # Results display area
        self.results_text = tk.Text(self.root, wrap=tk.WORD, height=25, width=100, bg='#000000', fg='#00FF00')  # Black bg, lime green text
        self.results_text.grid(row=1, column=0, columnspan=3, padx=20, pady=10)

        # Pagination controls
        self.pagination_label = ttk.Label(self.root, text="Page: 1", background='#1e1e1e', foreground='white')
        self.pagination_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.next_button = ttk.Button(self.root, text="Next", command=self.next_page, style='Neon.TButton')
        self.next_button.grid(row=2, column=1, padx=20, pady=10)

        self.prev_button = ttk.Button(self.root, text="Previous", command=self.prev_page, style='Neon.TButton')
        self.prev_button.grid(row=2, column=2, padx=20, pady=10)

        # Per-page and Sort filters
        self.per_page_label = ttk.Label(self.root, text="Per Page:", background='#1e1e1e', foreground='white')
        self.per_page_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.per_page_entry = ttk.Combobox(self.root, values=["10", "30", "50", "100"], textvariable=self.per_page_var, width=10)
        self.per_page_entry.grid(row=3, column=1, padx=20, pady=10)

        self.sort_label = ttk.Label(self.root, text="Sort By:", background='#1e1e1e', foreground='white')
        self.sort_label.grid(row=3, column=2, padx=20, pady=10, sticky="w")

        self.sort_entry = ttk.Combobox(self.root, values=["stars", "forks", "updated"], textvariable=self.sort_var, width=10)
        self.sort_entry.grid(row=3, column=3, padx=20, pady=10)

        # Theme toggle button
        self.create_theme_button()

    def create_theme_button(self):
        theme_button = ttk.Button(self.root, text="🌗 Toggle Theme", command=self.toggle_theme, style='Neon.TButton')
        theme_button.grid(row=0, column=4, padx=20, pady=10, sticky="ne")

    def toggle_theme(self):
        if self.is_dark_mode:
            self.root.configure(bg='#f4f4f4')  # Light theme
            self.is_dark_mode = False
        else:
            self.root.configure(bg='#1e1e1e')  # Dark theme
            self.is_dark_mode = True

    def search_repositories(self):
        self.current_keywords = self.search_entry.get()
        if not self.current_keywords:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return
        self.current_page = 1
        self._fetch_repos()

    def next_page(self):
        self.current_page += 1
        self._fetch_repos()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._fetch_repos()

    def _fetch_repos(self):
        try:
            headers = {"Authorization": f"token {self.api_token}"} if self.api_token else {}
            params = {
                "q": self.current_keywords,
                "per_page": int(self.per_page_var.get()),
                "sort": self.sort_var.get(),
                "order": "desc",
                "page": self.current_page
            }
            response = requests.get(f"{self.base_url}/search/repositories", headers=headers, params=params)
            response.raise_for_status()

            remaining = int(response.headers.get('X-RateLimit-Remaining', '0'))
            reset_time = int(response.headers.get('X-RateLimit-Reset', '0'))
            
            if remaining == 0:
                reset_str = datetime.fromtimestamp(reset_time).strftime("%Y-%m-%d %H:%M:%S")
                self.root.after(0, lambda: messagebox.showinfo("Rate Limit Exceeded", f"Rate limit exceeded. Resets at {reset_str}", parent=self.root))
                return

            data = response.json()
            self.current_results = data.get("items", [])
            self.total_count = data.get("total_count", 0)

            self.root.after(0, self._update_ui_after_fetch)

        except requests.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch repositories: {str(e)}", parent=self.root))

    def _update_ui_after_fetch(self):
        self.results_text.delete(1.0, tk.END)  # Clear previous results
        if self.current_results:
            for repo in self.current_results:
                self.results_text.insert(tk.END, f"Name: {repo['full_name']}\n")
                self.results_text.insert(tk.END, f"Description: {repo['description']}\n")
                self.results_text.insert(tk.END, f"Stars: {repo['stargazers_count']}  Forks: {repo['forks_count']}\n")
                self.results_text.insert(tk.END, f"Language: {repo.get('language', 'N/A')}\n")
                self.results_text.insert(tk.END, f"License: {repo.get('license', {}).get('name', 'N/A')}\n")
                self.results_text.insert(tk.END, f"URL: {repo['html_url']}\n\n")
            self.pagination_label.config(text=f"Page: {self.current_page} / {self.total_count // 30 + 1}")
        else:
            self.results_text.insert(tk.END, "No repositories found.\n")
            self.pagination_label.config(text=f"Page: {self.current_page} / 1")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubCrawlerApp(root)
    root.mainloop()
