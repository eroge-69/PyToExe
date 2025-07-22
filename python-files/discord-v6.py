#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord自动发送中文消息程序 - 优化版
文件名: discord_auto_sender_optimized.py

功能说明:
- 随机间隔自动发送消息到Discord：14秒(80%)、20秒(18%)、30秒(2%)
- 内置500+句短语，分为4个分类
- 键盘控制：
  * End(开始/暂停，支持断点续传)
  * +/-(倒计时中加减5秒，可累计)
  * Home(删除输入框+随机粘贴特定短语)
  * Delete(快速删除对话框全部内容)
  * Enter(立即发送)
  * Esc(退出)

使用前请确保：
1. Discord窗口可见且输入框处于活跃状态
2. 已安装所需Python库：pyautogui keyboard pyperclip
"""

import random
import time
import threading
import pyautogui
import keyboard
import sys
from datetime import datetime

class DiscordAutoSender:
    def __init__(self):
        # 程序状态控制
        self.is_running = False
        self.is_paused = False
        self.should_exit = False
        self.current_message = ""
        
        # 倒计时相关
        self.countdown_seconds = 0
        self.countdown_lock = threading.Lock()
        
        # 设置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # 内置短语库 - 根据用户要求替换
        self.chat_phrases = {
            '常规聊天类': [
                "哈哈哈，你们真厉害", "真的肝不动了", "quiz今天答案是什么?求教💗", "哈哈哈，是的", 
                "💪继续社区建设，什么时候肝到32级", "不着急，慢慢来", "到后面，升级太慢了", "肝起来呀",
                "肝不动了，肝不动了，来点提提神的😮‍💨", "感觉又行了", "还得是你们", "哈哈，随便码的，打错字了",
                "你们打字这么快", "感觉还能继续", "加油！兄弟们😄", "任务艰难呀呀呀",
                "打字都这么累吗😮‍💨", "快不行了休息一下", "准备，水一下盲打", "继续干活了",
                "加油💪等等我", "老师们真的很活跃", "太勇了你们，几个不停的", "开起来不错😄",
                "谁说不是呢", "这样也行😄", "所以答案是什么？俺也想知道", "但是职业选手吧",
                "肝，一起加油，社区更牛", "坐等答案", "卷不动了兄弟姐妹们", "你们继续我先撤了",
                "有来了，哈哈😄", "加油努力💪", "升级好难呀，老师分享一下经验，哈哈😄", "看着不错",
                "聊的很欢呀", "不知道答案，还在等老师开卷呢", "下午好中午好晚上好，哈哈😄", "现在不知道呢",
                "还没有呢", "猛猛肝，小心肝📢", "还在等老师的答案", "滴滴滴滴滴滴📍，来了",
                "祝各位老板发大财💰", "慢慢来不着急的😄", "再水一波😴", "好家伙👌",
                "升级比较难了，现在", "一个小时可以升级多少级？", "有没有什么大动作", "干撸太累了",
                "StandX有没有什么升级快速的方法", "前赴后继一波又一波", "肝麻了，吃点东西", "继续肝，未来可期😄",
                "醒了就肝，睡前还是肝😮‍💨", "你们都太卷了，卷不动了", "答案什么时候有老师们👨‍🏫", "真的太努力了💪",
                "社区建设考你了", "吃瓜吃瓜，吃瓜群众🍉", "都这么拼吗？", "起猛了嘎嘎",
                "水一下休息一下😴", "我一个人一边玩去了，去边上肝", "都是哪里的这么拼", "肝三年，富三代哈哈😄",
                "人不少呀，继续肝吧", "尼古拉斯赵四😄", "肝到海水变蓝", "绿色出行，肝到不行🌳",
                "都是狠角色，没停过✋也要继续肝呀", "谁说不是呢哈哈", "一字一字肝起来的", "厉害了你们👍",
                "找个话题，聊起来🎤", "肝肝肝，继续", "别忘了休息。", "大家都答过题目了吗",
                "答案什么知道吗📚", "还是你们卷🌬", "认真肝，光明真大肝", "慢慢来，比较稳",
                "我也肝不动了，😄", "读书未来，社区建设来了", "整不动了都快", "还是你们行呀",
                "人间值得，肝一回", "题目都不知道什么", "大毛不好撸了，还得继续肝", "看今晚什么级别",
                "还在低等级继续徘徊", "笑死了哈哈🤣", "这肝起来好慢呀🤣", "哈哈哈哈🤣",
                "有没有什么好项目在做的", "肝一天,神清气爽😌", "老师们都狠低调的📚", "这速度太快了，完全跟不少你们的节奏🤣",
                "我🈶来了，继续肝", "老师带头，我们加油", "冲冲冲💪", "一般晚上会有福利😄",
                "老师带带吧，想进步有点难肝起来", "老师是肝帝，没错", "白天在晚上还在肝，不用休息的吗", "又看到几个熟悉的身影了，都是老师",
                "这个xp太难了", "哪个是人间", "哈哈哈🤣不知道怎么说了", "有没有什么计划",
                "老师快报答案，学习一下📚", "💻肝不用了，电脑也快不行了", "下一步什么是目标🪵", "利金鱼还远呢，🐳，还是小卡拉咪",
                "继续冲呀，肝起来", "老师发点福利，加点动力😍", "肝，怕什么，继续冲", "但说无妨，继续肝",
                "肝一个是一个", "主打已读不回哈哈哈", "还有有你们在，不然以为跟机器人在肝", "都是人中龙凤",
                "去吧去吧，加油肝", "少说点多肝点", "哈哈哈忘了", "这都是啥，也不懂，就是肝",
                "来了就是肝", "累了困了，肝不动了有点", "都肝卡了电脑呼呼转，🤣。", "继续撸毛，冲刺加油，升级",
                "继续升级打怪", "冲冲冲，上分上分🔝", "坐等好心老师的答案🤣", "闭眼码字，专心肝",
                "老师们有人知道答案吗？", "继续肝，大力出奇迹", "羡慕老师们", "都这么厉害了还在肝💪",
                "我也要加油了💪", "明天更美好，加油肝", "肝起来翻倍不是梦", "做梦都在肝吗，你们厉害",
                "不行了肝不动了", "厉害了👍", "不是吧，肝到这种程度", "努力升级怎么破",
                "还没答案吗老师们", "复议+1", "HHH还得是你们呀", "聊的可嗨看",
                "发的快，也没用了", "10秒还在等", "这不知道要肝多久", "老铁，还能冲一波",
                "哈🤣哈哈哈还是这个好打", "加油肝，有福利💪", "继续在线肝起来", "兄弟们，肝就对了",
                "肝的越猛，升级越快", "上学都没那么积极", "吃饭睡觉都不用了，肝到底👍", "还得是你们ya 哈哈😄",
                "等一波好福利上", "冲呀，肝起来吧", "加油做任务", "这是什么意思哈哈😄"
            ],
            
            '赞美夸奖类': [
                "你们这肝劲儿，简直无敌啊💪", "太牛了！社区因你们而闪耀。", "👑肝帝们，佩服得不行...", "这速度快得飞起，牛批！",
                "卷王风范，让人羡慕死了😎", "你们活跃起来，社区瞬间热闹👍", "肝得这么狠，真是了不起。", "💥大佬们，膜拜你们的节奏！",
                "社区有你们，感觉超棒啊。", "打字如飞，佩服佩服...", "你们是肝界神话，哈哈✨", "这效率高到爆，顶呱呱！",
                "肝任务你们最在行，服气💯", "太强了，社区灵魂人物啊。", "👏活跃得让人跟不上，牛！", "你们卷起来无人能敌🔥",
                "肝得风生水起，超赞。", "这波操作绝了，膜拜...", "社区之光，全靠你们照亮🌟", "肝得这么猛，简直神人！",
                "😍羡慕你们的拼劲儿，太棒。", "升级机器就是你们，哈哈。", "佩服到爆，这活跃度👍", "肝帝代名词，非你们莫属。",
                "💪你们太给力，社区更牛了！", "打字速度惊人，叹服啊...", "肝界标杆，学着点。", "这节奏无敌，服了服了。",
                "你们是社区顶梁柱，稳！", "太卷了，佩服五体投地🙌", "🔥肝得这么帅，牛啊。", "任务达人就是你们，赞。",
                "社区因你们而精彩，哈哈✨", "肝得让人膜拜，太强！", "活跃之星，非你们莫属😄", "这效率叹为观止，绝妙。",
                "肝任务王者，顶尖啊👌", "打字开挂般快，牛批！", "社区骄傲，全是你们功劳🌟", "肝得狠劲儿十足，了得。",
                "你们是卷王神话，膜拜...", "这速度神了，佩服！", "肝起来无人能及🚀", "社区有你们真幸福💖",
                "太拼了，爆赞啊💥", "肝界传奇，羡慕死了。", "你们活跃飞起，超棒👍", "这肝劲儿，牛到家了！",
                "佩服你们的坚持，哈哈。", "🦸‍♂️肝神话就是你们，太强。"
            ],
            
            '鼓励加油类': [
                "冲冲冲，继续肝下去！🚀", "肝起来吧，升级指日可待。", "💪再卷一波，顶住啊...", "别停，肝出奇迹来！",
                "未来可期，继续冲刺🔥", "加油，等级很快升的。", "肝得猛点，胜利在望🏆", "坚持下去，升级不远啦！",
                "⚡再努力，社区更强。", "一起肝，冲顶去💥", "别放弃，肝到底啊。", "奥利给，继续卷起来🔥",
                "升级有望，再坚持会儿。", "冲一波，肝到巅峰！", "社区更强，肝得狠🚀", "胜利在望，继续冲加油吧🏅",
                "牛逼大发，继续肝下去🐮", "加油干，胜利等着你🏅", "肝下去，光明在未来，大家一起来✨", "等级飞升，再冲刺啊📈",
                "肝得生猛，社区越来越牛！", "未来大好，肝起来吧哈哈🌈", "胜利属于你，继续卷，继续肝🎉", "🚀冲冲冲，肝新高度。",
                "别停下，升级在望💪", "未来可期，肝起来吧🌟", "等级飙升，再努力点，加油肝。", "一起冲，社区超棒🚗",
                "奇迹发生，坚持肝💥", "升级快，肝的猛狠狠冲一波⚡", "胜利在手，加油干🏆", "🔥再肝一波，冲顶去。",
                "别放弃，肝出辉煌✨", "升级不远，冲吧🎯", "等级飞升，再坚持坚持📈", "奇迹不断，肝下去吧💥",
                "升级有望，加油卷，肝起来💪", "新高冲刺，再肝啊还能冲一波🔥", "未来可期，别停下哈哈🌟", "等级飙升，肝得猛📈",
                "社区更牛，一起冲冲冲🚗", "胜利属于你，坚持再肝一波🎉", "肝出奇迹，肝出未来冲冲冲💥", "升级等着，再努力🏆",
                "光明未来，肝起来，加油冲冲冲✨", "顶峰不远，别放弃呀，扶我起来还能肝🚀", "等级飞升，未来可期，加油干📈", "冲顶去，再肝一波🔥",
                "社区更强，肝得更狠，冲冲冲💪", "未来可期，继续卷起来🌟"
            ],
            
            '问候类': [
                "大家早中晚好，肝起来啦！😄", "兄弟们好，冲任务去🚀", "早中午晚上好，社区嗨起来~", "嘿，肝友们好，卷一波！💪",
                "早中晚好，继续肝任务吧。", "大家好啊，活跃点冲等级🌟", "嗨，早中晚好，肝得猛！🔥", "兄弟姐妹们好，任务走起🚗",
                "早中午晚上好，肝出奇迹~", "大家好，冲一波升级吧😎", "嘿，肝帝们早中晚好！💥", "社区好，卷起来继续肝。",
                "早中晚好，兄弟们冲啊！✨", "嗨大家好，肝任务嗨起来🌈", "早中午晚上好，活跃社区！😄", "兄弟们好，肝得开心点🚀",
                "早中晚好，卷一波等级！💪", "大家好啊，任务冲冲冲~", "嘿，肝友早中晚好，嗨起来。", "社区好，继续肝出新高度！🌟",
                "早中午晚上好，冲顶去🔥", "兄弟们好，肝任务别停！😎", "大家早中晚好，活跃起来吧~", "嗨，肝帝们好，卷一波！💥",
                "早中晚好，社区更热闹🚗", "大家好，肝得猛点啊！✨", "嘿，兄弟姐妹们早中晚好🌈", "早中午晚上好，冲等级啦😄",
                "社区好，肝任务嗨起来！", "大家好啊，卷起来冲刺🚀", "早中晚好，肝出新辉煌！💪", "兄弟们好，活跃社区去~",
                "嗨，早中午晚上好，肝吧🔥", "大家好，任务冲一波！😎", "早中晚好，肝友们嗨起来。", "社区好，卷等级继续冲！🌟",
                "嘿，肝帝早中晚好，冲！💥", "早中午晚上好，肝得开心🚗", "大家好啊，活跃起来吧！😄", "兄弟们好，肝任务冲顶！✨",
                "早中晚好，社区嗨翻天~", "嗨，肝友们好，卷一波！💪", "早中午晚上好，肝出奇迹🌈", "大家好，冲等级别停啊！🔥",
                "社区好，肝任务嗨起来🚀", "早中晚好，兄弟们冲刺！😎", "嘿，大家好，肝得猛点吧。", "早中午晚上好，活跃社区来了，哈哈！🌟",
                "兄弟姐妹们好，卷起来！💥", "大家，早中晚好，肝出新高度！😄"
            ]
        }
        
        # 转换为单一列表供随机选择使用
        self.all_phrases = []
        for category, phrases in self.chat_phrases.items():
            self.all_phrases.extend(phrases)
        
        # Home键专用短语
        self.home_key_phrases = [
            "加油冲呀，兄弟姐妹们💪", "为了升级，继续肝肝肝😄", "真的有点肝不动了，算球😄", "大家多少级，肝的动吗？",
            "加油继续一起建设起来💪", "答案胡出来了吗老师们📚", "666这个可以有", "今天不知道能不能升级",
            "冲冲冲继续加油肝", "肝不动也得继续呀，建设起来", "全力加上肝", "老师太厉害了，学习学习",
            "冲一波，卷起来了", "加油兄弟姐妹们👭👬", "一起一起老师👨‍🏫", "加油哦，现在还能肝",
            "大家真的太卷了", "今天的都还没升级过哈哈", "哈哈哈哈哈哈🤣", "这也可以的呀😄",
            "谁说不是呢？", "麻了，肝麻了都", "你们真能聊，哈哈", "冲就完了，肝到底",
            "都不是认识但是都在肝", "此时不肝何时肝", "太棒了老师", "跟上步伐继续肝起来",
            "吃瓜群众，在线肝冲冲冲", "我要升级，我要升级，我要升级", "长路慢慢继续肝肝", "肝得猛点，胜利在望🏆",
            "你们这肝劲儿，简直无敌啊💪"
        ]
        
        # 随机循环控制
        self.unused_indices = list(range(len(self.all_phrases)))
        self.current_round = 1
        
        print("Discord自动发送程序已启动! (优化版)")
        print("=" * 60)
        print("⏰ 发送间隔: 随机(14秒80%、20秒18%、30秒2%)")
        print("📝 短语库: 500+句分类短语")
        print("🔄 循环模式: 每轮不重复")
        print("=" * 60)
        print("操作说明:")
        print("End键:    开始/暂停自动发送(支持断点续传)")
        print("+键:     倒计时中增加5秒(可累计)")
        print("-键:     倒计时中减少5秒(可累计)")
        print("Home键:   删除输入框+随机粘贴特定短语")
        print("Delete键: 快速删除对话框全部内容")
        print("Enter键:  立即发送当前消息") 
        print("Esc键:    退出程序")
        print("=" * 60)
        
        # 初始化消息
        self.generate_new_message()
        print(f"当前消息: {self.current_message}")
        print("按End键开始自动发送...")
        
    def get_random_interval(self):
        """根据概率分布获取随机倒计时间隔"""
        rand = random.random()
        if rand < 0.8:  # 80%
            return 14
        elif rand < 0.98:  # 18%
            return 20
        else:  # 2%
            return 30
            
    def generate_new_message(self):
        """生成新的随机消息"""
        if not self.unused_indices:
            self.unused_indices = list(range(len(self.all_phrases)))
            self.current_round += 1
            print(f"🔄 第{self.current_round}轮开始，重置短语库")
            
        selected_index = random.choice(self.unused_indices)
        self.unused_indices.remove(selected_index)
        self.current_message = self.all_phrases[selected_index]
        
        used_count = len(self.all_phrases) - len(self.unused_indices)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 新消息: {self.current_message}")
        print(f"📊 进度: 第{self.current_round}轮 {used_count}/{len(self.all_phrases)} ({used_count/len(self.all_phrases)*100:.1f}%)")
        
    def paste_message_to_discord(self):
        """将消息粘贴到Discord输入框"""
        try:
            import pyperclip
            pyperclip.copy(self.current_message)
            time.sleep(0.1)
            
            current_mouse_pos = pyautogui.position()
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.moveTo(current_mouse_pos[0], current_mouse_pos[1])
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📝 已粘贴到Discord: {self.current_message}")
                
        except Exception as e:
            print(f"粘贴消息失败: {e}")
    
    def send_current_discord_message(self):
        """发送Discord输入框中的消息"""
        try:
            current_mouse_pos = pyautogui.position()
            pyautogui.press('enter')
            pyautogui.moveTo(current_mouse_pos[0], current_mouse_pos[1])
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] ✅ 消息已发送: {self.current_message}")
            
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
    
    def clear_input_box(self):
        """删除输入框全部内容(Delete键功能)"""
        try:
            current_mouse_pos = pyautogui.position()
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            pyautogui.moveTo(current_mouse_pos[0], current_mouse_pos[1])
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🗑️ 已清除输入框内容")
            
        except Exception as e:
            print(f"❌ 清除输入框失败: {e}")
    
    def home_key_action(self):
        """Home键功能：删除输入框内容并随机粘贴特定短语"""
        try:
            # 先清除输入框
            current_mouse_pos = pyautogui.position()
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.1)
            
            # 随机选择Home键专用短语
            home_phrase = random.choice(self.home_key_phrases)
            
            # 粘贴短语
            import pyperclip
            pyperclip.copy(home_phrase)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.moveTo(current_mouse_pos[0], current_mouse_pos[1])
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🏠 Home键操作: {home_phrase}")
            
        except Exception as e:
            print(f"❌ Home键操作失败: {e}")
    
    def adjust_countdown_time(self, seconds):
        """调整倒计时时间(+/-键功能)"""
        with self.countdown_lock:
            self.countdown_seconds += seconds
            if self.countdown_seconds < 1:
                self.countdown_seconds = 1
            elif self.countdown_seconds > 300:  # 最大5分钟
                self.countdown_seconds = 300
                
        timestamp = datetime.now().strftime("%H:%M:%S")
        action = "增加" if seconds > 0 else "减少"
        print(f"[{timestamp}] ⏱️ {action}{abs(seconds)}秒，当前倒计时: {self.countdown_seconds}秒")
        
    def countdown_timer(self, initial_seconds):
        """支持暂停和时间调整的倒计时"""
        with self.countdown_lock:
            self.countdown_seconds = initial_seconds
            
        while self.countdown_seconds > 0:
            if self.should_exit or not self.is_running:
                return False
                
            if not self.is_paused:
                print(f"⏱️  倒计时: {self.countdown_seconds} 秒", end='\r')
                time.sleep(1)
                with self.countdown_lock:
                    self.countdown_seconds -= 1
            else:
                time.sleep(0.1)  # 暂停时短暂等待
        
        print("⏱️  倒计时: 0 秒 - 发送!")
        return True
    
    def auto_send_loop(self):
        """自动发送循环"""
        first_run = True
        
        while not self.should_exit:
            if self.is_running and not self.is_paused:
                if first_run:
                    print("\n🚀 开始自动发送模式...")
                    self.paste_message_to_discord()
                    first_run = False
                
                # 获取随机倒计时间隔
                interval = self.get_random_interval()
                print(f"\n📝 消息已准备: {self.current_message}")
                print(f"开始{interval}秒倒计时...")
                
                countdown_completed = self.countdown_timer(interval)
                
                if countdown_completed and self.is_running and not self.is_paused:
                    self.send_current_discord_message()
                    self.generate_new_message()
                    self.paste_message_to_discord()
                elif not countdown_completed:
                    print(f"\n⏸️  倒计时已暂停在{self.countdown_seconds}秒")
            else:
                if first_run:
                    self.paste_message_to_discord()
                    first_run = False
                time.sleep(0.1)
                
    def setup_hotkeys(self):
        """设置快捷键"""
        keyboard.add_hotkey('end', self.toggle_sending)
        keyboard.add_hotkey('+', lambda: self.adjust_countdown_time(5))
        keyboard.add_hotkey('=', lambda: self.adjust_countdown_time(5))
        keyboard.add_hotkey('-', lambda: self.adjust_countdown_time(-5))
        keyboard.add_hotkey('home', self.home_key_action)
        keyboard.add_hotkey('delete', self.clear_input_box)
        keyboard.add_hotkey('enter', self.send_current_message)
        keyboard.add_hotkey('esc', self.exit_program)
        
    def toggle_sending(self):
        """切换发送状态(支持断点续传)"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] ✅ 自动发送已开始")
        else:
            self.is_paused = not self.is_paused
            timestamp = datetime.now().strftime("%H:%M:%S")
            if self.is_paused:
                print(f"\n[{timestamp}] ⏸️  自动发送已暂停(断点: {self.countdown_seconds}秒)")
            else:
                print(f"\n[{timestamp}] ▶️  自动发送已恢复(从{self.countdown_seconds}秒开始)")
                
    def send_current_message(self):
        """立即发送当前消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 🚀 手动立即发送...")
        self.send_current_discord_message()
        
        if self.is_running:
            self.generate_new_message()
            self.paste_message_to_discord()
            
    def exit_program(self):
        """退出程序"""
        self.should_exit = True
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🚪 程序正在退出...")
        
    def run(self):
        """运行程序主循环"""
        self.setup_hotkeys()
        
        send_thread = threading.Thread(target=self.auto_send_loop, daemon=True)
        send_thread.start()
        
        try:
            while not self.should_exit:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n检测到Ctrl+C，正在退出...")
            self.should_exit = True
            
        print("程序已退出，感谢使用!")
        sys.exit(0)

def check_dependencies():
    """检查依赖库是否已安装"""
    try:
        import pyautogui
        import keyboard
        import pyperclip
        return True
    except ImportError as e:
        print("错误：缺少必要的Python库!")
        print("请在命令提示符中执行以下命令安装：")
        print("pip install pyautogui keyboard pyperclip")
        print(f"具体错误：{e}")
        return False

def main():
    """主函数"""
    print("Discord自动发送程序 v5.0 - 优化版")
    print("=" * 60)
    
    if not check_dependencies():
        input("按回车键退出...")
        return
        
    try:
        sender = DiscordAutoSender()
        sender.run()
    except Exception as e:
        print(f"程序运行错误：{e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()