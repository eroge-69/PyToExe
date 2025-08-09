import time
import winsound  # Windows系统声音
import os
from threading import Thread
try:
    import pygame  # 用于闪光效果
except ImportError:
    pygame = None

class EnhancedTelegraph:
    def __init__(self):
        # 扩展的摩尔斯电码字典
        self.morse_code_dict = {
            # 字母
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
            'Z': '--..',
            # 数字
            '0': '-----', '1': '.----', '2': '..---', '3': '...--', 
            '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
            '8': '---..', '9': '----.',
            # 标点符号和特殊字符
            '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', 
            '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', 
            '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', 
            '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.', 
            '$': '...-..-', '@': '.--.-.', ' ': '/', '\n': '.-.-',
            # 扩展字符
            'Á': '.--.-', 'Ä': '.-.-', 'É': '..-..', 'Ñ': '--.--',
            'Ö': '---.', 'Ü': '..--', 'ß': '...--..', 'Ç': '-.-..',
            'À': '.--.-', 'È': '.-..-', 'Ì': '..', 'Ò': '---',
            'Ù': '..--', 'Æ': '.-.-', 'Ø': '---.', 'Å': '.--.-',
            # 协议控制字符
            '[START]': '-.-.-', '[END]': '.-.-.', '[WAIT]': '...-.-',
            '[ERROR]': '........', '[INVITE]': '-.-', '[ACK]': '.-.-'
        }
        
        # 反向字典用于解码
        self.reverse_morse_dict = {v: k for k, v in self.morse_code_dict.items()}
        
        # 电报协议标志
        self.use_protocol = True
        self.flash_enabled = False
        self.sound_enabled = False
        
        # 初始化pygame用于闪光效果
        if pygame:
            pygame.init()
            self.screen = pygame.display.set_mode((100, 100))
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
    
    def __del__(self):
        if pygame:
            pygame.quit()
    
    def encode(self, text):
        """
        将文本编码为摩尔斯电码，可添加协议控制字符
        """
        encoded_message = []
        
        if self.use_protocol:
            encoded_message.append(self.morse_code_dict['[START]'])
        
        for char in text.upper():
            if char in self.morse_code_dict:
                encoded_message.append(self.morse_code_dict[char])
            else:
                # 如果字符不在字典中，保留原样
                encoded_message.append(char)
        
        if self.use_protocol:
            encoded_message.append(self.morse_code_dict['[END]'])
        
        return ' '.join(encoded_message)
    
    def decode(self, morse_code):
        """
        将摩尔斯电码解码为文本，处理协议控制字符
        """
        decoded_message = []
        codes = morse_code.split(' ')
        
        for code in codes:
            if code in self.reverse_morse_dict:
                char = self.reverse_morse_dict[code]
                # 处理协议控制字符
                if char.startswith('[') and char.endswith(']'):
                    if char == '[START]':
                        decoded_message.append('\n[通信开始]')
                    elif char == '[END]':
                        decoded_message.append('[通信结束]\n')
                    elif char == '[WAIT]':
                        decoded_message.append('[等待响应]')
                    elif char == '[ERROR]':
                        decoded_message.append('[错误]')
                    elif char == '[INVITE]':
                        decoded_message.append('[邀请发送]')
                    elif char == '[ACK]':
                        decoded_message.append('[确认收到]')
                    else:
                        decoded_message.append(char)
                else:
                    decoded_message.append(char)
            else:
                # 如果代码不在字典中，保留原样
                decoded_message.append(code)
        
        return ''.join(decoded_message)
    
    def play_sound(self, morse_code):
        """
        播放摩尔斯电码的声音
        """
        if not self.sound_enabled:
            return
            
        dot_duration = 100  # 点的时间(毫秒)
        dash_duration = 3 * dot_duration  # 划的时间
        freq = 800  # 频率(Hz)
        
        for symbol in morse_code:
            if symbol == '.':
                winsound.Beep(freq, dot_duration)
                time.sleep(dot_duration / 1000)
            elif symbol == '-':
                winsound.Beep(freq, dash_duration)
                time.sleep(dot_duration / 1000)
            elif symbol == ' ':
                time.sleep(3 * dot_duration / 1000)
            else:
                time.sleep(dot_duration / 1000)
    
    def flash_screen(self, morse_code):
        """
        通过屏幕闪烁显示摩尔斯电码
        """
        if not self.flash_enabled or not pygame:
            return
            
        dot_duration = 0.1  # 点的持续时间(秒)
        dash_duration = 3 * dot_duration  # 划的持续时间
        
        for symbol in morse_code:
            if symbol == '.':
                self.screen.fill((255, 255, 255))
                pygame.display.flip()
                time.sleep(dot_duration)
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
                time.sleep(dot_duration)
            elif symbol == '-':
                self.screen.fill((255, 255, 255))
                pygame.display.flip()
                time.sleep(dash_duration)
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
                time.sleep(dot_duration)
            elif symbol == ' ':
                time.sleep(3 * dot_duration)
            else:
                time.sleep(dot_duration)
    
    def transmit(self, morse_code):
        """
        传输摩尔斯电码(声音和闪光)
        """
        if self.sound_enabled:
            sound_thread = Thread(target=self.play_sound, args=(morse_code,))
            sound_thread.start()
        
        if self.flash_enabled:
            flash_thread = Thread(target=self.flash_screen, args=(morse_code,))
            flash_thread.start()
        
        if self.sound_enabled or self.flash_enabled:
            # 计算总传输时间
            duration = sum(
                0.1 if c == '.' else 
                0.3 if c == '-' else 
                0.3 if c == ' ' else 
                0.1 for c in morse_code
            )
            time.sleep(duration)
    
    def save_to_file(self, content, filename):
        """
        将内容保存到文件
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"内容已保存到 {filename}")
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False
    
    def load_from_file(self, filename):
        """
        从文件加载内容
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return None
    
    def run(self):
        """
        运行电报编码解码器的交互界面
        """
        print("增强版电报编码解码器")
        print("=" * 40)
        
        while True:
            print("\n主菜单:")
            print("1. 编码文本")
            print("2. 解码摩尔斯电码")
            print("3. 传输摩尔斯电码(声音/闪光)")
            print("4. 文件操作")
            print("5. 设置")
            print("6. 退出")
            
            choice = input("\n请选择操作 (1-6): ")
            
            if choice == '1':
                text = input("请输入要编码的文本: ")
                encoded = self.encode(text)
                print(f"\n编码结果: {encoded}")
                
                save = input("是否保存到文件? (y/n): ").lower()
                if save == 'y':
                    filename = input("输入文件名: ")
                    self.save_to_file(encoded, filename)
            
            elif choice == '2':
                morse = input("请输入要解码的摩尔斯电码: ")
                decoded = self.decode(morse)
                print(f"\n解码结果: {decoded}")
                
                save = input("是否保存到文件? (y/n): ").lower()
                if save == 'y':
                    filename = input("输入文件名: ")
                    self.save_to_file(decoded, filename)
            
            elif choice == '3':
                morse = input("请输入要传输的摩尔斯电码: ")
                print("传输中... (按Ctrl+C中断)")
                try:
                    self.transmit(morse)
                    print("\n传输完成!")
                except KeyboardInterrupt:
                    print("\n传输中断!")
            
            elif choice == '4':
                print("\n文件操作:")
                print("1. 从文件加载文本并编码")
                print("2. 从文件加载摩尔斯电码并解码")
                print("3. 返回主菜单")
                
                file_choice = input("请选择文件操作 (1-3): ")
                
                if file_choice == '1':
                    filename = input("输入要加载的文本文件名: ")
                    text = self.load_from_file(filename)
                    if text:
                        encoded = self.encode(text)
                        print(f"\n编码结果: {encoded}")
                        save = input("是否保存编码结果到文件? (y/n): ").lower()
                        if save == 'y':
                            out_filename = input("输入输出文件名: ")
                            self.save_to_file(encoded, out_filename)
                
                elif file_choice == '2':
                    filename = input("输入要加载的摩尔斯电码文件名: ")
                    morse = self.load_from_file(filename)
                    if morse:
                        decoded = self.decode(morse)
                        print(f"\n解码结果: {decoded}")
                        save = input("是否保存解码结果到文件? (y/n): ").lower()
                        if save == 'y':
                            out_filename = input("输入输出文件名: ")
                            self.save_to_file(decoded, out_filename)
            
            elif choice == '5':
                print("\n设置:")
                print(f"1. 协议控制: {'开启' if self.use_protocol else '关闭'}")
                print(f"2. 声音效果: {'开启' if self.sound_enabled else '关闭'}")
                print(f"3. 闪光效果: {'开启' if self.flash_enabled else '关闭'}")
                print("4. 返回主菜单")
                
                setting_choice = input("请选择设置 (1-4): ")
                
                if setting_choice == '1':
                    self.use_protocol = not self.use_protocol
                    print(f"协议控制已{'开启' if self.use_protocol else '关闭'}")
                elif setting_choice == '2':
                    self.sound_enabled = not self.sound_enabled
                    print(f"声音效果已{'开启' if self.sound_enabled else '关闭'}")
                elif setting_choice == '3':
                    if pygame:
                        self.flash_enabled = not self.flash_enabled
                        print(f"闪光效果已{'开启' if self.flash_enabled else '关闭'}")
                    else:
                        print("未安装pygame，无法使用闪光效果")
            
            elif choice == '6':
                print("退出电报编码解码器。")
                break
            
            else:
                print("无效选择，请重新输入。")


# 使用示例
if __name__ == "__main__":
    telegraph = EnhancedTelegraph()
    telegraph.run()