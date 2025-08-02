# auto_clicker.py

import pyautogui
import keyboard
import time
import sys

def get_position_with_countdown(prompt_message):
    """
    Displays a prompt and a countdown, then gets the mouse position.
    """
    print(prompt_message)
    for i in range(5, 0, -1):
        # The end='\r' makes the cursor return to the start of the line
        sys.stdout.write(f"آماده برای ثبت در {i} ثانیه...")
        sys.stdout.flush()
        time.sleep(1)
    
    position = pyautogui.position()
    print(f"\n✅ مختصات ثبت شد: {position}")
    time.sleep(1) # Give user time to see the confirmation
    return position

def main():
    """
    Main function to run the auto-clicker logic.
    """
    print("--- شروع برنامه کلیک خودکار ---")
    print("برای توقف کامل برنامه، کلید 'q' را فشار دهید.\n")

    # 1. Get the coordinate to watch
    watch_pos = get_position_with_countdown(
        "لطفاً موس را روی نقطه‌ای که باید نظارت شود ببرید..."
    )
    
    # 2. Get the target color from that coordinate
    target_color = pyautogui.pixel(watch_pos.x, watch_pos.y)
    print(f"🎨 رنگ مورد نظر ثبت شد: {target_color}\n")
    
    # 3. Get the coordinate to click
    click_pos = get_position_with_countdown(
        "لطفاً موس را روی نقطه‌ای که باید کلیک شود ببرید..."
    )

    print("\n🚀 ...::: نظارت شروع شد :::...")
    print("برای خروج کلید 'q' را نگه دارید.")

    try:
        while True:
            # Check for exit condition
            if keyboard.is_pressed('q'):
                print("\nکلید 'q' فشرده شد. خروج از برنامه...")
                break

            # 4. Check the current color of the watch position
            current_color = pyautogui.pixel(watch_pos.x, watch_pos.y)
            
            # 5. If color matches, perform the click
            if current_color == target_color:
                print(f"✔️ رنگ مورد نظر در {watch_pos} پیدا شد. در حال کلیک روی {click_pos}")
                pyautogui.click(click_pos.x, click_pos.y)
                # Wait a bit after clicking to avoid multiple rapid clicks
                time.sleep(2) 
            
            # Wait a short moment before the next check to reduce CPU usage
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nبرنامه توسط کاربر متوقف شد.")
    finally:
        print("--- پایان برنامه ---")

if __name__ == "__main__":
    main()