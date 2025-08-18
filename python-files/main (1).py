import json
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil  # 新增：用于跨平台文件复制

class WrongQuestionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("错题再测系统")
        self.root.resizable(True, True)  # 支持窗口大小调整
        self.json_file = "questions.json"
        self.image_dir = "image"
        self.questions = self.load_questions()
        self.current_question = None
        self.test_questions = []
        self.current_index = 0
        self.correct_count = 0
        self.test_count = 0
        self.option_vars = None

        # 创建图片文件夹
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        # 主界面
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=20)
        tk.Button(self.main_frame, text="填充题库", command=self.show_add_question).pack(pady=10)
        tk.Button(self.main_frame, text="错题再测", command=self.show_test).pack(pady=10)

    def load_questions(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_questions(self):
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=4)

    def show_add_question(self):
        self.main_frame.pack_forget()
        self.add_frame = tk.Frame(self.root)
        self.add_frame.pack(pady=20)

        # 问题描述
        tk.Label(self.add_frame, text="问题描述:").grid(row=0, column=0, sticky="w")
        self.question_entry = tk.Entry(self.add_frame, width=50)
        self.question_entry.grid(row=0, column=1, pady=5)

        # 图片选择
        tk.Label(self.add_frame, text="图片（可选）:").grid(row=1, column=0, sticky="w")
        self.image_entry = tk.Entry(self.add_frame, width=50)
        self.image_entry.grid(row=1, column=1, pady=5)
        tk.Button(self.add_frame, text="选择图片", command=self.select_image).grid(row=1, column=2, padx=5)

        # 选项
        self.option_entries = []
        for i in range(4):
            tk.Label(self.add_frame, text=f"选项 {i+1}:").grid(row=i+2, column=0, sticky="w")
            entry = tk.Entry(self.add_frame, width=50)
            entry.grid(row=i+2, column=1, pady=5)
            self.option_entries.append(entry)

        # 正确答案
        tk.Label(self.add_frame, text="正确答案:").grid(row=6, column=0, sticky="w")
        self.answer_var = tk.StringVar(value="options_1")
        tk.OptionMenu(self.add_frame, self.answer_var, "options_1", "options_2", "options_3", "options_4").grid(row=6, column=1, sticky="w")

        # 保存和返回
        tk.Button(self.add_frame, text="保存", command=self.save_question).grid(row=7, column=1, pady=10)
        tk.Button(self.add_frame, text="返回", command=self.back_to_main).grid(row=7, column=2, pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            # 复制图片到 image 文件夹（跨平台）
            dest_path = os.path.join(self.image_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)  # 使用 shutil 替代 os.system
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, dest_path)

    def save_question(self):
        question = self.question_entry.get().strip()
        image = self.image_entry.get().strip()
        options = [entry.get().strip() for entry in self.option_entries]
        answer = self.answer_var.get()

        # 输入验证
        if not question:
            messagebox.showerror("错误", "问题描述不能为空")
            return
        valid_options = [opt for opt in options if opt]
        if len(valid_options) < 2:
            messagebox.showerror("错误", "至少需要 2 个选项")
            return
        if image and not os.path.exists(image):
            messagebox.showerror("错误", "图片路径无效")
            return
        if answer not in ["options_1", "options_2", "options_3", "options_4"] or not options[int(answer[-1])-1]:
            messagebox.showerror("错误", "请选择有效的正确答案")
            return

        # 生成新题目
        new_id = max([q["id"] for q in self.questions], default=0) + 1
        question_data = {
            "id": new_id,
            "question": question,
            "image": image,
            "options_1": options[0],
            "options_2": options[1],
            "options_3": options[2],
            "options_4": options[3],
            "answer": answer,
            "history_answer": 1
        }
        self.questions.append(question_data)
        self.save_questions()
        messagebox.showinfo("成功", "题目已保存")
        self.back_to_main()

    def back_to_main(self):
        self.add_frame.destroy()
        self.main_frame.pack(pady=20)

    def show_test(self):
        self.main_frame.pack_forget()
        self.test_frame = tk.Frame(self.root)
        self.test_frame.pack(pady=20)

        # 随机选择题目（30% 错题，70% 正确题）
        wrong_questions = [q for q in self.questions if q["history_answer"] == 0]
        correct_questions = [q for q in self.questions if q["history_answer"] == 1]
        self.test_questions = []
        total_questions = min(len(self.questions), 10)  # 假设每次 10 题
        for _ in range(total_questions):
            if random.random() < 0.3 and wrong_questions:
                q = random.choice(wrong_questions)
                wrong_questions.remove(q)
            elif correct_questions:
                q = random.choice(correct_questions)
                correct_questions.remove(q)
            else:
                break
            self.test_questions.append(q)
        random.shuffle(self.test_questions)

        self.current_index = 0
        self.correct_count = 0
        self.test_count = 0
        self.show_question()

    def show_question(self):
        for widget in self.test_frame.winfo_children():
            widget.destroy()

        if not self.test_questions:
            messagebox.showinfo("提示", "题库为空")
            self.back_to_main()
            return

        self.current_question = self.test_questions[self.current_index]
        tk.Label(self.test_frame, text=self.current_question["question"], wraplength=500).pack(pady=10)

        # 显示图片
        if self.current_question["image"]:
            try:
                img = Image.open(self.current_question["image"])
                img = img.resize((300, 300), Image.LANCZOS)  # 自动调整大小
                self.photo = ImageTk.PhotoImage(img)
                tk.Label(self.test_frame, image=self.photo).pack(pady=10)
            except:
                tk.Label(self.test_frame, text="图片加载失败").pack(pady=10)

        # 随机排列选项
        options = [
            (self.current_question["options_1"], "options_1"),
            (self.current_question["options_2"], "options_2"),
            (self.current_question["options_3"], "options_3"),
            (self.current_question["options_4"], "options_4")
        ]
        valid_options = [(opt, key) for opt, key in options if opt]  # 过滤空选项
        random.shuffle(valid_options)  # 随机打乱选项
        self.option_vars = tk.StringVar()
        self.shuffled_options = {}  # 记录打乱后的选项和原始键的映射
        for opt, key in valid_options:
            self.shuffled_options[opt] = key  # 映射选项内容到原始键
            tk.Radiobutton(self.test_frame, text=opt, variable=self.option_vars, value=opt).pack(anchor="w")

        # 按钮
        tk.Button(self.test_frame, text="上一题", command=self.prev_question).pack(side=tk.LEFT, padx=10)
        tk.Button(self.test_frame, text="提交", command=self.submit_answer).pack(side=tk.LEFT, padx=10)
        tk.Button(self.test_frame, text="下一题", command=self.next_question).pack(side=tk.LEFT, padx=10)
        tk.Button(self.test_frame, text="结束测试", command=self.end_test).pack(side=tk.LEFT, padx=10)

        # 实时反馈
        self.feedback_label = tk.Label(self.test_frame, text=f"已测试：{self.test_count}/{len(self.test_questions)}，正确率：{self.correct_count/self.test_count*100 if self.test_count else 0:.1f}%")
        self.feedback_label.pack(side=tk.BOTTOM, pady=10)

    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

    def submit_answer(self):
        if not self.option_vars.get():
            messagebox.showerror("错误", "请选择一个答案")
            return
        self.test_count += 1
        selected_option = self.option_vars.get()
        selected_key = self.shuffled_options.get(selected_option, "")  # 获取用户选择的原始键
        if selected_key == self.current_question["answer"]:
            self.correct_count += 1
        else:
            self.current_question["history_answer"] = 0
        self.feedback_label.config(text=f"已测试：{self.test_count}/{len(self.test_questions)}，正确率：{self.correct_count/self.test_count*100 if self.test_count else 0:.1f}%")
        # 高亮正确答案
        correct_key = self.current_question["answer"]
        correct_option = self.current_question[correct_key]
        for widget in self.test_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton) and widget["value"] == correct_option:
                widget.config(fg="green", font=("Arial", 10, "bold"))
        self.save_questions()

    def next_question(self):
        if self.current_index < len(self.test_questions) - 1:
            self.current_index += 1
            self.show_question()

    def end_test(self):
        messagebox.showinfo("测试总结", f"总题目数：{self.test_count}\n正确率：{self.correct_count/self.test_count*100 if self.test_count else 0:.1f}%")
        self.test_frame.destroy()
        self.main_frame.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = WrongQuestionApp(root)
    root.mainloop()