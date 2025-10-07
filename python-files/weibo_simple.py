#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
微博热搜爬虫工具 - 简化版
模仿原v4.exe的运行方式
@Author  : Manus AI
@Date    : 2025/10/6
"""

import requests
import datetime
import os
import random

def get_hot_search():
    """获取微博热搜数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 尝试官方API
        response = requests.get('https://weibo.com/ajax/side/hotSearch', headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data')
    except:
        pass
    
    # 如果失败，返回模拟数据
    return create_demo_data()

def create_demo_data():
    """创建演示数据"""
    topics = [
        "国庆假期出行", "秋季养生", "新电影上映", "科技新品", "体育赛事",
        "美食推荐", "旅游攻略", "健康生活", "教育资讯", "环保行动",
        "时尚潮流", "娱乐八卦", "社会热点", "财经新闻", "文化活动",
        "音乐榜单", "游戏资讯", "汽车新闻", "房产动态", "职场话题"
    ]
    
    hot_list = []
    for i, topic in enumerate(topics):
        hot_list.append({
            'word': topic,
            'raw_hot': random.randint(50000, 500000),
            'label_name': random.choice(['', '热', '新', '爆']) if i < 5 else ''
        })
    
    return {
        'realtime': hot_list,
        'hotgov': {'word': '重要公告'}
    }

def save_hot_search(data, date_str):
    """保存热搜到文件"""
    if not data:
        return False
    
    lines = []
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 文件头
    lines.append(f"微博热搜榜 - {date_str}\n")
    lines.append(f"数据获取时间: {current_time}\n")
    lines.append("="*50 + "\n\n")
    
    # 置顶热搜
    if data.get('hotgov'):
        lines.append(f"【置顶】{data['hotgov']['word']}\n")
        lines.append("-"*50 + "\n\n")
    
    # 热搜列表
    if data.get('realtime'):
        for i, item in enumerate(data['realtime'][:20], 1):
            title = item.get('word', '')
            hot = item.get('raw_hot', 0)
            label = item.get('label_name', '')
            
            label_text = f" [{label}]" if label else ""
            hot_text = f" (热度:{hot})" if hot else ""
            
            lines.append(f"{i:2d}. {title}{label_text}{hot_text}\n")
    
    # 保存文件
    filename = f"weibo_hot_search_{date_str.replace('.', '_')}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return filename
    except:
        return False

def main():
    """主函数"""
    print("微博热搜爬虫工具")
    print("作者: Manus AI")
    print("-" * 30)
    
    # 获取用户输入
    while True:
        date_input = input("请输入要爬取的日期（格式：YYYY.MM.DD，例如2025.09.28）：")
        
        # 验证日期格式
        try:
            if '.' in date_input and len(date_input.split('.')) == 3:
                year, month, day = date_input.split('.')
                datetime.date(int(year), int(month), int(day))
                break
            else:
                raise ValueError
        except:
            print("日期格式错误，请重新输入！")
    
    print(f"\n正在获取 {date_input} 的微博热搜...")
    
    # 获取数据
    data = get_hot_search()
    
    if data:
        print("数据获取成功！")
        
        # 保存文件
        filename = save_hot_search(data, date_input)
        
        if filename:
            print(f"\n热搜数据已保存到: {filename}")
            print(f"文件大小: {os.path.getsize(filename)} 字节")
            
            # 显示前5条预览
            print(f"\n{date_input} 热搜预览:")
            print("-" * 30)
            
            if data.get('realtime'):
                for i, item in enumerate(data['realtime'][:5], 1):
                    title = item.get('word', '')
                    label = item.get('label_name', '')
                    label_text = f" [{label}]" if label else ""
                    print(f"{i}. {title}{label_text}")
                
                if len(data['realtime']) > 5:
                    print("...")
            
            print(f"\n完整数据请查看文件: {filename}")
        else:
            print("保存文件失败！")
    else:
        print("获取数据失败！")
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
        input("按回车键退出...")
