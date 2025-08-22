import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import csv
import datetime
import os
import sys
import webbrowser
import re
import random
from collections import Counter
import threading
import time

class CommentAnalyzer:
    def __init__(self):
        self.comments = []
        self.analysis_results = {}
    
    def analyze_sentiment(self, text):
        positive_words = ['好', '棒', '赞', '喜欢', '优秀', '完美', 'amazing', 'great', 'good', 'love', 'excellent', 'perfect']
        negative_words = ['差', '烂', '讨厌', '糟糕', '失望', 'bad', 'terrible', 'hate', 'awful', 'disappointed']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'Positive'
        elif negative_count > positive_count:
            return 'Negative'
        else:
            return 'Neutral'
    
    def extract_keywords(self, texts):
        all_text = ' '.join(texts).lower()
        words = re.findall(r'\b\w+\b', all_text)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        return Counter(filtered_words).most_common(10)
    
    def analyze_comments(self, comments_data):
        if not comments_data:
            return {}
        
        sentiments = []
        texts = []
        high_priority = []
        
        for comment in comments_data:
            text = comment.get('text', '')
            texts.append(text)
            
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment)
            
            likes = comment.get('likes', 0)
            if likes > 10 or len(text) > 100:
                high_priority.append(comment)
        
        sentiment_dist = Counter(sentiments)
        total = len(sentiments)
        sentiment_percentages = {
            'Positive': round(sentiment_dist.get('Positive', 0) / total * 100, 1),
            'Negative': round(sentiment_dist.get('Negative', 0) / total * 100, 1),
            'Neutral': round(sentiment_dist.get('Neutral', 0) / total * 100, 1)
        }
        
        keywords = self.extract_keywords(texts)
        
        return {
            'total_comments': total,
            'sentiment_distribution': sentiment_percentages,
            'top_keywords': keywords,
            'high_priority_comments': high_priority[:5],
            'sample_comments': comments_data[:10]
        }

class SimpleCommentAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("社交媒体评论分析系统 v2.0")
        self.root.geometry("800x600")
        
        self.analyzer = CommentAnalyzer()
        self.current_data = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="社交媒体评论分析系统", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        input_frame = ttk.LabelFrame(main_frame, text="数据输入", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="视频/帖子URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(input_frame, width=60)
        self.url_entry.grid(row=0, column=1, padx=(10, 0), pady=(0, 10))
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="导入CSV文件", command=self.import_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="生成演示数据", command=self.generate_demo_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="开始分析", command=self.start_analysis).pack(side=tk.LEFT)
        
        result_frame = ttk.LabelFrame(main_frame, text="分析结果", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.result_text = scrolledtext.ScrolledText(result_frame, width=80, height=20)
        self.result_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        export_frame = ttk.Frame(result_frame)
        export_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(export_frame, text="导出CSV", command=self.export_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="生成报告", command=self.generate_report).pack(side=tk.LEFT)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.current_data = list(reader)
                
                messagebox.showinfo("成功", f"已导入 {len(self.current_data)} 条评论数据")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"已导入数据：{len(self.current_data)} 条评论\n")
                
            except Exception as e:
                messagebox.showerror("错误", f"导入文件失败：{str(e)}")
    
    def generate_demo_data(self):
        demo_comments = [
            {"text": "这个视频太棒了！学到了很多东西", "likes": 15, "username": "user1"},
            {"text": "内容很有用，感谢分享", "likes": 8, "username": "user2"},
            {"text": "讲解很清楚，继续加油", "likes": 12, "username": "user3"},
            {"text": "有点难懂，希望能更详细一些", "likes": 3, "username": "user4"},
            {"text": "Great content! Very helpful", "likes": 20, "username": "user5"},
            {"text": "音质有点问题，但内容不错", "likes": 5, "username": "user6"},
            {"text": "Perfect explanation, thank you!", "likes": 18, "username": "user7"},
            {"text": "希望能出更多这样的教程", "likes": 10, "username": "user8"},
            {"text": "This is exactly what I was looking for", "likes": 25, "username": "user9"},
            {"text": "质量很高的内容，订阅了", "likes": 14, "username": "user10"}
        ]
        
        self.current_data = demo_comments
        messagebox.showinfo("成功", f"已生成 {len(demo_comments)} 条演示数据")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"已生成演示数据：{len(demo_comments)} 条评论\n")
    
    def start_analysis(self):
        if not self.current_data:
            messagebox.showwarning("警告", "请先导入数据或生成演示数据")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "正在分析评论数据...\n")
        self.root.update()
        
        try:
            results = self.analyzer.analyze_comments(self.current_data)
            self.display_results(results)
        except Exception as e:
            messagebox.showerror("错误", f"分析失败：{str(e)}")
    
    def display_results(self, results):
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, "=== 分析结果 ===\n\n")
        self.result_text.insert(tk.END, f"总评论数：{results['total_comments']}\n\n")
        
        self.result_text.insert(tk.END, "情感分布：\n")
        for sentiment, percentage in results['sentiment_distribution'].items():
            self.result_text.insert(tk.END, f"  {sentiment}: {percentage}%\n")
        self.result_text.insert(tk.END, "\n")
        
        self.result_text.insert(tk.END, "热门关键词：\n")
        for word, count in results['top_keywords']:
            self.result_text.insert(tk.END, f"  {word}: {count}次\n")
        self.result_text.insert(tk.END, "\n")
        
        if results['high_priority_comments']:
            self.result_text.insert(tk.END, "重点关注评论：\n")
            for i, comment in enumerate(results['high_priority_comments'], 1):
                self.result_text.insert(tk.END, f"  {i}. {comment['text'][:50]}... (点赞: {comment.get('likes', 0)})\n")
        
        self.analysis_results = results
    
    def export_csv(self):
        if not self.current_data:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if self.current_data:
                        fieldnames = ['username', 'text', 'likes', 'sentiment']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for comment in self.current_data:
                            row = {
                                'username': comment.get('username', ''),
                                'text': comment.get('text', ''),
                                'likes': comment.get('likes', 0),
                                'sentiment': self.analyzer.analyze_sentiment(comment.get('text', ''))
                            }
                            writer.writerow(row)
                
                messagebox.showinfo("成功", f"数据已导出到：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def generate_report(self):
        if not self.analysis_results:
            messagebox.showwarning("警告", "请先进行分析")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存HTML报告",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                html_content = self.create_html_report()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                messagebox.showinfo("成功", f"报告已生成：{file_path}")
                
                if messagebox.askyesno("打开报告", "是否现在打开HTML报告？"):
                    webbrowser.open(file_path)
                    
            except Exception as e:
                messagebox.showerror("错误", f"生成报告失败：{str(e)}")
    
    def create_html_report(self):
        results = self.analysis_results
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>评论分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .summary {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .chart {{ margin: 20px 0; }}
        .keywords {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .keyword {{ background: #2196f3; color: white; padding: 5px 10px; border-radius: 15px; font-size: 14px; }}
        .comment {{ background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #2196f3; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>社交媒体评论分析报告</h1>
        <p style="text-align: center; color: #666;">生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>📊 数据概览</h2>
            <p><strong>总评论数:</strong> {results['total_comments']}</p>
            <p><strong>正面评论:</strong> {results['sentiment_distribution']['Positive']}%</p>
            <p><strong>负面评论:</strong> {results['sentiment_distribution']['Negative']}%</p>
            <p><strong>中性评论:</strong> {results['sentiment_distribution']['Neutral']}%</p>
        </div>
        
        <div class="chart">
            <h2>🔥 热门关键词</h2>
            <div class="keywords">
"""
        
        for word, count in results['top_keywords']:
            html += f'<span class="keyword">{word} ({count})</span>'
        
        html += """
            </div>
        </div>
        
        <div>
            <h2>⭐ 重点关注评论</h2>
"""
        
        for i, comment in enumerate(results.get('high_priority_comments', []), 1):
            html += f"""
            <div class="comment">
                <strong>评论 {i}:</strong> {comment['text']}<br>
                <small>点赞数: {comment.get('likes', 0)} | 用户: {comment.get('username', '匿名')}</small>
            </div>
"""
        
        html += """
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
            <p>报告由社交媒体评论分析系统生成</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def run(self):
        self.root.mainloop()

def main():
    try:
        app = SimpleCommentAnalyzerGUI()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()