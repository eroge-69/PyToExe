import os
import shutil
import tkinter as tk
from tkinter import messagebox
import win32com.client


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmetrix Demo App")
        self.root.configure(bg="#f5f5f5")

        # Lấy kích thước màn hình
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Đặt cửa sổ app ngang bằng màn hình, cao = 15%, nằm sát dưới
        win_w = screen_w
        win_h = int(screen_h * 0.15)
        win_x = 0
        win_y = screen_h - win_h - 80
        self.root.geometry(f"{win_w}x{win_h}+{win_x}+{win_y}")

        self.projects = self.load_projects()
        self.current_project = None
        self.current_task_index = 0

        self.word_app = None
        self.word_doc = None

        # Lưu các nút project
        self.project_buttons = {}

        # === Layout ===
        top_frame = tk.Frame(self.root, bg="#f5f5f5")
        top_frame.pack(fill="x", pady=5)

        self.project_frame = tk.Frame(top_frame, bg="#f5f5f5")
        self.project_frame.pack(side="left", padx=10)

        self.control_frame = tk.Frame(top_frame, bg="#f5f5f5")
        self.control_frame.pack(side="right", padx=10)

        self.task_label = tk.Label(self.root, text="", font=("Arial", 12),
                                   bg="#ffffff", fg="#333333", wraplength=win_w - 100,
                                   relief="solid", bd=1, padx=10, pady=10)
        self.task_label.pack(pady=5, fill="both", expand=True)

        bottom_frame = tk.Frame(self.root, bg="#f5f5f5")
        bottom_frame.pack(fill="x", pady=5)

        self.prev_btn = tk.Button(bottom_frame, text="← Trước", command=self.prev_task,
                                  bg="#0078d7", fg="white", font=("Arial", 10, "bold"))
        self.prev_btn.pack(side="left", padx=5)

        self.task_btn_frame = tk.Frame(bottom_frame, bg="#f5f5f5")
        self.task_btn_frame.pack(side="left", padx=10, expand=True)

        self.next_btn = tk.Button(bottom_frame, text="Tiếp →", command=self.next_task,
                                  bg="#0078d7", fg="white", font=("Arial", 10, "bold"))
        self.next_btn.pack(side="right", padx=5)

        self.task_buttons = []

        self.load_ui()

    def load_projects(self):
        projects = {}
        base_dir = "Projects"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        for folder in os.listdir(base_dir):
            project_path = os.path.join(base_dir, folder)
            if os.path.isdir(project_path):
                student = os.path.join(project_path, "student.docx")
                original = os.path.join(project_path, "student_original.docx")
                answer = os.path.join(project_path, "answer.docx")
                tasks_file = os.path.join(project_path, "tasks.txt")

                if os.path.exists(student) and os.path.exists(original) and os.path.exists(answer) and os.path.exists(tasks_file):
                    tasks = []
                    with open(tasks_file, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                tasks.append(line)
                    projects[folder] = {
                        "student": student,
                        "original": original,
                        "answer": answer,
                        "tasks": tasks
                    }
        return projects

    def load_ui(self):
        # Tạo nút project
        for widget in self.project_frame.winfo_children():
            widget.destroy()
        self.project_buttons.clear()

        for project_name in self.projects.keys():
            btn = tk.Button(self.project_frame, text=project_name,
                            command=lambda n=project_name: self.select_project(n),
                            bg="#e0e0e0", fg="#000", font=("Arial", 10, "bold"))
            btn.pack(side="left", padx=5)
            self.project_buttons[project_name] = btn

        # Nút control
        for widget in self.control_frame.winfo_children():
            widget.destroy()

        tk.Button(self.control_frame, text="Mở File", command=self.open_file,
                  bg="#28a745", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        tk.Button(self.control_frame, text="Restart", command=self.restart_file,
                  bg="#ffc107", fg="black", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        tk.Button(self.control_frame, text="Chấm điểm", command=self.check_answer,
                  bg="#dc3545", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)

    def select_project(self, name):
        self.current_project = self.projects[name]
        self.current_task_index = 0
        self.show_task()

        # Đổi màu nút project
        for pname, btn in self.project_buttons.items():
            if pname == name:
                btn.config(bg="#0078d7", fg="white")
            else:
                btn.config(bg="#e0e0e0", fg="#000")

    def show_task(self):
        if not self.current_project:
            return
        tasks = self.current_project["tasks"]
        if tasks:
            task_text = tasks[self.current_task_index]
            self.task_label.config(text=task_text)
            self.update_task_buttons()

    def update_task_buttons(self):
        for widget in self.task_btn_frame.winfo_children():
            widget.destroy()
        self.task_buttons.clear()

        for i, _ in enumerate(self.current_project["tasks"]):
            btn = tk.Button(self.task_btn_frame, text=f"{i+1}",
                            command=lambda idx=i: self.goto_task(idx),
                            font=("Arial", 8, "bold"), width=2, height=1)
            if i == self.current_task_index:
                btn.config(bg="#0078d7", fg="white")
            else:
                btn.config(bg="#e0e0e0", fg="black")
            btn.pack(side="left", padx=1)
            self.task_buttons.append(btn)

    def goto_task(self, idx):
        self.current_task_index = idx
        self.show_task()

    def prev_task(self):
        if self.current_project and self.current_task_index > 0:
            self.current_task_index -= 1
            self.show_task()

    def next_task(self):
        if self.current_project and self.current_task_index < len(self.current_project["tasks"]) - 1:
            self.current_task_index += 1
            self.show_task()

    def open_file(self):
        if not self.current_project:
            return
        student = self.current_project["student"]
        self.open_word(student)

    def open_word(self, filepath):
        try:
            if not self.word_app:
                self.word_app = win32com.client.Dispatch("Word.Application")
                self.word_app.Visible = True
            self.word_doc = self.word_app.Documents.Open(os.path.abspath(filepath))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file Word: {e}")

    def restart_file(self):
        if not self.current_project:
            return

        confirm = messagebox.askyesno("Xác nhận Restart",
                                      "Bạn có chắc muốn làm lại bài này không?\nFile hiện tại sẽ bị thay thế.")
        if not confirm:
            return

        try:
            if self.word_doc:
                self.word_doc.Close(False)
                self.word_doc = None
        except:
            self.word_doc = None

        try:
            if self.word_app:
                self.word_app.Quit()
                self.word_app = None
        except:
            self.word_app = None

        student = self.current_project["student"]
        original = self.current_project["original"]
        shutil.copyfile(original, student)

        self.open_word(student)

    def check_answer(self):
        if not self.current_project:
            return
        student = self.current_project["student"]
        answer = self.current_project["answer"]

        from docx import Document
        try:
            doc_student = Document(student)
            doc_answer = Document(answer)

            text_student = "\n".join([p.text for p in doc_student.paragraphs])
            text_answer = "\n".join([p.text for p in doc_answer.paragraphs])

            if text_student.strip() == text_answer.strip():
                messagebox.showinfo("Kết quả", "Bài làm ĐÚNG")
            else:
                messagebox.showwarning("Kết quả", "Bài làm CHƯA đúng")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chấm điểm: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
