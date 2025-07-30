from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import webbrowser

def login_iot_platform(username, password):
    # 首先用默认浏览器打开网址（可选，因为下面会用Selenium打开）
    webbrowser.open("https://iot.barn-eye.com/login")
    time.sleep(2)  # 等待浏览器打开
    
    # 初始化WebDriver（这里使用Chrome，需要对应版本的chromedriver）
    # 确保chromedriver在系统PATH中，或指定其路径
    driver = webdriver.Chrome()
    
    try:
        # 打开登录页面
        driver.get("https://iot.barn-eye.com/login")
        
        # 等待页面加载完成，最多等待10秒
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 查找用户名和密码输入框并输入信息
        # 注意：实际的元素ID可能不同，需要根据网页实际情况修改
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))  # 替换为实际的用户名输入框ID
        )
        password_field = driver.find_element(By.ID, "password")  # 替换为实际的密码输入框ID
        
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # 查找登录按钮并点击
        login_button = driver.find_element(By.ID, "login-button")  # 替换为实际的登录按钮ID
        login_button.click()
        
        # 等待登录完成
        time.sleep(5)
        
        print("登录成功！")
        
    except Exception as e:
        print(f"登录过程中出现错误: {str(e)}")
    finally:
        # 保持浏览器打开，便于查看结果
        input("按回车键关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    # 请替换为你的用户名和密码
    USERNAME = "Gaobt"
    PASSWORD = "Gaobt999$"
    
    login_iot_platform(USERNAME, PASSWORD)
    