import tkinter as tk
from tkinter import ttk, messagebox
from github import Github, GithubException
import threading
import time
from datetime import datetime

class GitHubRepoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub snos by limit")
        self.root.geometry("600x500")

        # Поле для ввода токена
        self.token_label = tk.Label(root, text="GitHub Token:")
        self.token_label.pack(pady=5)
        self.token_entry = tk.Entry(root, width=50, show="*")
        self.token_entry.pack(pady=5)

        # Кнопка для загрузки репозиториев
        self.load_button = tk.Button(root, text="Load Repositories", command=self.load_repos)
        self.load_button.pack(pady=10)

        # Таблица для отображения репозиториев
        self.tree = ttk.Treeview(root, columns=("Name", "URL"), show="headings")
        self.tree.heading("Name", text="Repository Name")
        self.tree.heading("URL", text="Repository URL")
        self.tree.pack(pady=10, fill="both", expand=True)

        # Полоса прокрутки для таблицы
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Кнопка для удаления файлов
        self.delete_button = tk.Button(root, text="Delete Files", command=self.start_delete_files, state="disabled")
        self.delete_button.pack(pady=5)

        # Прогресс-бар
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        # Текстовое поле для логов
        self.log_text = tk.Text(root, height=6, width=60)
        self.log_text.pack(pady=5)
        self.log_text.config(state="disabled")

        # Переменная для хранения токена
        self.token = None
        self.is_deleting = False
        # Привязка события выбора строки в таблице
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def log_message(self, message):
        self.log_text.config(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def load_repos(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.token = self.token_entry.get()
        if not self.token:
            messagebox.showerror("Error", "Please enter a GitHub token")
            return

        try:
            # Инициализация клиента GitHub
            g = Github(self.token)
            user = g.get_user()

            # Получение всех репозиториев
            for repo in user.get_repos():
                self.tree.insert("", "end", values=(repo.name, repo.html_url))
            self.log_message("Repositories loaded successfully")

        except GithubException as e:
            self.log_message(f"Error loading repositories: {str(e)}")
            messagebox.showerror("Error", f"Failed to load repositories: {str(e)}")

    def on_tree_select(self, event):
        # Активировать кнопку удаления при выборе репозитория
        selected_item = self.tree.selection()
        self.delete_button.config(state="normal" if selected_item else "disabled")

    def start_delete_files(self):
        if self.is_deleting:
            messagebox.showwarning("Warning", "Deletion is already in progress")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a repository")
            return

        # Получаем имя репозитория
        repo_name = self.tree.item(selected_item)["values"][0]
        # Запускаем удаление в отдельном потоке
        threading.Thread(target=self.delete_files, args=(repo_name,), daemon=True).start()

    def delete_files(self, repo_name):
        self.is_deleting = True
        self.delete_button.config(state="disabled")
        self.progress["value"] = 0

        try:
            g = Github(self.token)
            user = g.get_user()
            full_repo_name = None
            for repo in user.get_repos():
                if repo.name == repo_name:
                    full_repo_name = repo.full_name
                    break

            if not full_repo_name:
                self.log_message("Error: Repository not found")
                messagebox.showerror("Error", "Repository not found")
                self.is_deleting = False
                self.delete_button.config(state="normal")
                return

            # Подтверждение удаления
            if not messagebox.askyesno("Confirm", f"Are you sure you want to delete all files in {full_repo_name}?"):
                self.is_deleting = False
                self.delete_button.config(state="normal")
                return

            repo = g.get_repo(full_repo_name)
            contents = repo.get_contents("")
            files = [f for f in contents if f.type == "file"]
            total_files = len(files)

            if total_files == 0:
                self.log_message("No files found in the repository")
                messagebox.showinfo("Info", "No files found in the repository")
                self.is_deleting = False
                self.delete_button.config(state="normal")
                return

            self.progress["maximum"] = total_files
            deleted_files = []
            batch_size = 10  # Удаляем 10 файлов в секунду
            batch_delay = 1.0  # Задержка в 1 секунду

            for i in range(0, total_files, batch_size):
                batch = files[i:i + batch_size]
                start_time = time.time()

                for content_file in batch:
                    try:
                        repo.delete_file(
                            content_file.path,
                            f"Remove {content_file.path}",
                            content_file.sha
                        )
                        deleted_files.append(content_file.path)
                        self.log_message(f"Deleted: {content_file.path}")
                        self.progress["value"] += 1
                        self.root.update_idletasks()  # Обновляем UI
                    except GithubException as e:
                        self.log_message(f"Error deleting {content_file.path}: {str(e)}")

                # Ждем до конца секунды для соблюдения лимита
                elapsed = time.time() - start_time
                if elapsed < batch_delay:
                    time.sleep(batch_delay - elapsed)

            self.log_message(f"Deletion complete. Deleted {len(deleted_files)} files")
            messagebox.showinfo("Success", f"Deleted {len(deleted_files)} files")

        except GithubException as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete files: {str(e)}")
        finally:
            self.is_deleting = False
            self.delete_button.config(state="normal")

def main():
    root = tk.Tk()
    app = GitHubRepoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()