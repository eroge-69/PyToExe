import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import sys
import json

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("贪吃蛇 - 精确调速版！")
        self.grid_size = 20
        self.tile_count = 20
        self.canvas = tk.Canvas(root, width=self.tile_count * self.grid_size, 
                                height=self.tile_count * self.grid_size, bg="lightgray")
        self.canvas.pack(pady=10)

        # 分数和历史记录
        self.score = 0
        self.score_history = self.load_scores()
        self.score_label = tk.Label(root, text=f"得分: {self.score}", font=("Arial", 14), fg="red")
        self.score_label.pack()
        self.history_label = tk.Label(root, text=self.get_history_text(), font=("Arial", 12))
        self.history_label.pack()
        self.mode_label = tk.Label(root, text="模式: 正常", font=("Arial", 14), fg="red")
        self.mode_label.pack()

        # 速度选择
        self.game_speed = self.choose_speed()
        self.base_speed = self.game_speed  # 保存基础速度
        self.is_frenzy = False

        # 蛇和食物
        self.snake = [(10, 10)]
        self.food = self.generate_food()
        self.dx, self.dy = 0, 0
        self.game_running = True

        # 键盘绑定
        self.root.bind("<Up>", lambda e: self.change_direction(0, -1))
        self.root.bind("<Down>", lambda e: self.change_direction(0, 1))
        self.root.bind("<Left>", lambda e: self.change_direction(-1, 0))
        self.root.bind("<Right>", lambda e: self.change_direction(1, 0))

        print("游戏初始化，Python版本:", sys.version)  # 调试
        print(f"历史分数: {self.score_history}")  # 调试
        print(f"初始速度: {self.game_speed}ms")  # 调试
        self.draw_game()
        self.update()

    def choose_speed(self):
        while True:
            speed = simpledialog.askstring("设置速度", "输入速度（毫秒，例如100、382）：", parent=self.root)
            try:
                speed = int(speed)
                if speed > 0:
                    return speed
                else:
                    messagebox.showwarning("错误", "请输入正整数！")
            except (ValueError, TypeError):
                messagebox.showwarning("错误", "请输入有效数字！")
        return 200  # 默认200ms

    def load_scores(self):
        try:
            with open("scores.txt", "r") as f:
                return json.load(f)
        except:
            return []

    def save_scores(self):
        try:
            with open("scores.txt", "w") as f:
                json.dump(self.score_history, f)
        except Exception as e:
            print(f"保存分数失败: {e}")  # 调试

    def get_history_text(self):
        if not self.score_history:
            return "历史记录: 无"
        high_score = max(self.score_history) if self.score_history else 0
        recent_scores = self.score_history[-5:][::-1]
        return f"最高分: {high_score}\n最近: {', '.join(map(str, recent_scores))}"

    def generate_food(self):
        while True:
            x = random.randint(0, self.tile_count - 1)
            y = random.randint(0, self.tile_count - 1)
            if (x, y) not in self.snake:
                print(f"生成食物: ({x}, {y})")  # 调试
                return (x, y)

    def change_direction(self, dx, dy):
        if (dx, dy) != (-self.dx, -self.dy):
            self.dx, self.dy = dx, dy
            print(f"方向切换: dx={dx}, dy={dy}")  # 调试

    def toggle_frenzy_mode(self):
        if random.random() < 0.3 and not self.is_frenzy:
            self.is_frenzy = True
            self.game_speed = max(50, self.base_speed - 50)  # 狂暴比基础快50ms
            self.mode_label.config(text="模式: 狂暴")
            print(f"进入狂暴模式！速度: {self.game_speed}ms")  # 调试
            self.root.after(5000, self.reset_frenzy)

    def reset_frenzy(self):
        self.is_frenzy = False
        self.game_speed = self.base_speed  # 恢复基础速度
        self.mode_label.config(text="模式: 正常")
        print(f"恢复正常模式，速度: {self.game_speed}ms")  # 调试

    def update(self):
        if not self.game_running:
            return
        if self.dx == 0 and self.dy == 0:
            self.draw_game()
            self.root.after(self.game_speed, self.update)
            return
        head_x, head_y = self.snake[0]
        head_x += self.dx
        head_y += self.dy
        head_x %= self.tile_count
        head_y %= self.tile_count
        head = (head_x, head_y)
        if len(self.snake) > 1 and head in self.snake[1:]:
            print(f"撞尾巴！头:{head}, 蛇身:{self.snake}")  # 调试
            self.game_over()
            return
        self.snake.insert(0, head)
        if head == self.food:
            self.score += 10
            self.score_label.config(text=f"得分: {self.score}")
            self.food = self.generate_food()
            if not self.is_frenzy:
                self.toggle_frenzy_mode()
        else:
            self.snake.pop()
        self.draw_game()
        self.root.after(self.game_speed, self.update)

    def draw_game(self):
        self.canvas.delete("all")
        fx, fy = self.food
        self.canvas.create_rectangle(fx * self.grid_size, fy * self.grid_size,
                                    (fx + 1) * self.grid_size, (fy + 1) * self.grid_size,
                                    fill="red")
        for x, y in self.snake:
            color = "#c0392b" if self.is_frenzy else "#2c3e50"
            self.canvas.create_rectangle(x * self.grid_size, y * self.grid_size,
                                        (x + 1) * self.grid_size, (y + 1) * self.grid_size,
                                        fill=color)

    def game_over(self):
        self.game_running = False
        self.score_history.append(self.score)
        self.save_scores()
        self.history_label.config(text=self.get_history_text())
        messagebox.showinfo("游戏结束", f"你的得分: {self.score}，撞尾巴了？再战！")
        self.snake = [(10, 10)]
        self.dx, self.dy = 0, 0
        self.score = 0
        self.is_frenzy = False
        self.game_speed = self.choose_speed()  # 重新选择速度
        self.base_speed = self.game_speed
        self.score_label.config(text=f"得分: {self.score}")
        self.mode_label.config(text="模式: 正常")
        self.food = self.generate_food()
        self.game_running = True
        print(f"游戏重启，历史分数: {self.score_history}")  # 调试

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()