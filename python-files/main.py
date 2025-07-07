import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import time

DATA_DIR = "data"
PENDING_DIR = os.path.join(DATA_DIR, "pending_review")
APPROVED_DIR = os.path.join(DATA_DIR, "approved")

os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(APPROVED_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def douyin_mock_collect():
    sample = {
        "douyin_url": "https://v.douyin.com/example/",
        "desc": "这是示例文案，抖音采集结果",
        "video_path": "data/sample_video.mp4",
        "cover_path": "data/sample_cover.jpg"
    }
    filename = os.path.join(PENDING_DIR, f"item_{int(time.time())}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False)
    return True

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("多平台自动发布工具（简易版）")
        self.geometry("500x400")

        self.collect_btn = tk.Button(self, text="采集抖音内容", command=self.collect)
        self.collect_btn.pack(pady=10)

        self.review_btn = tk.Button(self, text="审核待发布内容", command=self.review)
        self.review_btn.pack(pady=10)

        self.publish_btn = tk.Button(self, text="开始发布（模拟）", command=self.publish)
        self.publish_btn.pack(pady=10)

    def collect(self):
        res = douyin_mock_collect()
        if res:
            messagebox.showinfo("提示", "采集成功！数据已保存到待审核区。")

    def review(self):
        ReviewWindow(self)

    def publish(self):
        messagebox.showinfo("提示", "这里是模拟发布功能，后续可接真实接口。")

class ReviewWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("待审核内容")
        self.geometry("400x300")
        self.items = self.load_items()
        self.index = 0

        self.text = tk.Text(self, height=10)
        self.text.pack(pady=5)

        self.approve_btn = tk.Button(self, text="通过", command=self.approve)
        self.approve_btn.pack(side=tk.LEFT, padx=20, pady=10)

        self.delete_btn = tk.Button(self, text="删除", command=self.delete)
        self.delete_btn.pack(side=tk.RIGHT, padx=20, pady=10)

        self.show_item()

    def load_items(self):
        items = []
        for f in os.listdir(PENDING_DIR):
            if f.endswith(".json"):
                with open(os.path.join(PENDING_DIR, f), "r", encoding="utf-8") as file:
                    data = json.load(file)
                    data["_file"] = f
                    items.append(data)
        return items

    def show_item(self):
        if not self.items:
            self.text.delete("1.0", "end")
            self.text.insert("end", "无待审核内容")
            self.approve_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            return
        item = self.items[self.index]
        content = f"抖音链接：{item.get('douyin_url','')}\n文案：{item.get('desc','')}\n视频路径：{item.get('video_path','')}\n封面路径：{item.get('cover_path','')}"
        self.text.delete("1.0", "end")
        self.text.insert("end", content)

    def approve(self):
        item = self.items[self.index]
        os.rename(os.path.join(PENDING_DIR, item["_file"]), os.path.join(APPROVED_DIR, item["_file"]))
        messagebox.showinfo("提示", "审核通过，已加入发布队列（模拟）")
        self.items.pop(self.index)
        if self.index >= len(self.items):
            self.index = max(0, len(self.items)-1)
        self.show_item()

    def delete(self):
        item = self.items[self.index]
        os.remove(os.path.join(PENDING_DIR, item["_file"]))
        messagebox.showinfo("提示", "已删除该素材")
        self.items.pop(self.index)
        if self.index >= len(self.items):
            self.index = max(0, len(self.items)-1)
        self.show_item()

if name == "__main__":
    app = App()
    app.mainloop()