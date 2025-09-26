import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from datetime import datetime, timedelta
import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# text_area_console=None


# 2024-07-12 取得时间,d1指需要增加的天数
def get_time(d1, today=None):
    if not today:
        today = datetime.date.today()
    time1 = today + timedelta(days=d1)
    return time1


# 2024-01-14 取得时间格式,d1指需要增加的天数,可以是负值 格式:2023-06-03
def get_time_format(d1, today=None):
    if not today:
        today = datetime.date.today()
    time1 = get_time(d1,today).strftime("%Y-%m-%d")
    return time1


# 设置 Selenium 浏览器选项
def get_table_data(minus_day):
    url = "http://211.64.248.12:8080/easytong_web/login"  #url_entry.get()  # 获取用户输入的网址
    if not url:
        # messagebox.showerror("错误", "请输入网址！")
        return

    # 设置无头浏览器
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 启用无头模式
    chrome_options.add_argument("--no-sandbox")

    # 启动浏览器
    driver = webdriver.Chrome()  #options=chrome_options
    driver.get(url)

    # 1. 登录页面
    # 查找输入框，用户名
    input_box = driver.find_element(By.ID, 'txt_user')
    # 向输入框中填入数据
    input_box.send_keys('100008')
    time.sleep(2)
    # 查找输入框，用户名
    input_box = driver.find_element(By.ID, 'txt_pwd')
    # 向输入框中填入数据
    input_box.send_keys('88888888')
    time.sleep(2)

    # 查找并点击登录按钮
    button = driver.find_element(By.ID, "loginButton")
    button.click()

    #  等待页面加载（可以根据页面加载时间进行调整）
    time.sleep(2)
    # 2. 首页
    # 找到名称为“营业终端汇总”的 table id="treeview-1012-record-6"
    try:
        # 找到id为treeview-1012-record-6的table
        table = driver.find_element(By.ID, 'treeview-1012-record-6')

        # 找到table内的第一个div元素
        div_element = table.find_element(By.TAG_NAME, 'div')

        # 点击该div元素
        ActionChains(driver).move_to_element(div_element).click().perform()

        print("营业终端汇总点击成功!")
    except Exception as e:
        print(f"出现错误: {e}")

    # 等待新页面加载
    time.sleep(2)

    # 3. 营业终端汇总 页面
    # 到达 终端营业汇总页面之后 点击“统计”按钮，id是button-1036、
    button = driver.find_element(By.ID, "button-1036")
    button.click()
    # 等待新页面加载
    time.sleep(1)

    # 开始日期和结束日期都输入昨天的日期
    yesterday = get_time_format(minus_day)
    # 查找输入框，开始日期
    try:
        # 找到具有data-ref属性为inputE1的输入框
        input_element = driver.find_element(By.NAME, 'startDate')
        # 清除input中的内容
        input_element.clear()
        # 输入日期（根据需求格式填写）
        input_element.send_keys(yesterday)  # 输入你想要的日期
        # 模拟按下Enter键
        input_element.send_keys(Keys.RETURN)
        print("日期已填入并按下Enter键!")
    except Exception as e:
        print(f"出现错误: {e}")
    # 查找输入框，结束日期
    try:
        # 找到具有data-ref属性为inputE1的输入框
        input_element = driver.find_element(By.NAME, 'endDate')
        # 清除input中的内容
        input_element.clear()
        # 输入日期（根据需求格式填写）
        input_element.send_keys(yesterday)  # 输入你想要的日期
        # 模拟按下Enter键
        input_element.send_keys(Keys.RETURN)
        print("日期已填入并按下Enter键!")
    except Exception as e:
        print(f"出现错误: {e}")

    # 找到dialog里面的确定按钮并点击

    # 找到 input 元素的父级 div 元素
    # parent_div = input_element.find_element(By.XPATH, "./parent::div")
    # 等待页面加载并找到所有 class 包含 'your-class-name' 的 a 标签
    a_tag = driver.find_element(By.XPATH, "//a[contains(@class, 'x-btn x-unselectable x-box-item x-toolbar-item x-btn-default-small')]")
    # 使用 JavaScript 执行代码，获取该元素的所有事件监听器
    # 使用 JavaScript 捕获并返回绑定的事件监听器
    events = driver.execute_script("""
        const events = [];
        const element = arguments[0];

        // 获取所有事件类型
        const eventTypes = ['click', 'mouseover', 'keydown', 'keyup', 'focus', 'blur', 'change', 'submit'];
        eventTypes.forEach(eventType => {
            const clone = element.cloneNode(true);  // 克隆元素，避免直接影响原元素
            clone.addEventListener(eventType, function() {
                events.push(eventType);  // 捕获事件类型
            });
            document.body.appendChild(clone);  // 将克隆元素添加到页面中，触发事件
            clone.click();  // 模拟事件
            clone.remove();  // 删除克隆元素
        });

        return events;
    """, a_tag)

    print("a 标签支持的事件：", events)
    # # 获取并打印 a 标签的具体内容
    # print("a 标签的文本内容：", a_tag.text)
    # print("a 标签的完整 HTML 内容：", a_tag.get_attribute('outerHTML'))

    # wait = WebDriverWait(driver, 10)
    # element = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'x-btn x-unselectable x-box-item x-toolbar-item x-btn-default-small')]")))
    # element.click()
    # 获取 a 标签的父级 div 元素
    # parent_div = a_tag.find_element(By.XPATH, "./parent::div")
    # # 获取 a 标签内部的 span 元素
    # span_element = a_tag.find_element(By.XPATH, ".//span")
    # print("span_element HTML 内容：", span_element.get_attribute('outerHTML'))
    # span_element = span_element.find_element(By.XPATH, ".//span")
    # print("span_element HTML 内容：", span_element.get_attribute('outerHTML'))
    # span_element = span_element.find_element(By.XPATH, ".//span")
    # print("span_element HTML 内容：", span_element.get_attribute('outerHTML'))
    # # 获取 span 元素后面的下一个兄弟 span 元素
    # next_span = span_element.find_element(By.XPATH, "following-sibling::span")
    # print("next_span HTML 内容：", next_span.get_attribute('outerHTML'))

    # 点击 span 元素
    # print("parent_div HTML 内容：", parent_div.get_attribute('outerHTML'))
    # # 获取 a 标签的父级 div 元素
    # parent_div = parent_div.find_element(By.XPATH, "./parent::div")
    # print("parent_div2 HTML 内容：", parent_div.get_attribute('outerHTML'))
    # parent_div = parent_div.find_element(By.XPATH, "./parent::div")
    # print("parent_div3 HTML 内容：", parent_div.get_attribute('outerHTML'))
    # parent_div.click()
    # print("a_tags",a_tags)
    # 点击第一个 a 标签
    # a_tag.send_keys(Keys.ENTER)

    # try:
    #     a_elements = driver.find_elements(By.TAG_NAME, 'a')  # 查找所有的a标签
    #     for a in a_elements:
    #         # 查找a标签内的所有span标签
    #         span_elements = a.find_elements(By.TAG_NAME, 'span')
    #         for span in span_elements:
    #             # 如果span的文字内容是"确定"，点击该a标签
    #             print("span.text:",span.text)
    #             if span.text == "确定":
    #                 a.click()
    #                 print("点击了包含'确定'的a标签!")
    #                 break  # 找到目标后退出循环
    #     print("a标签循环结束 没找打确定按钮a标签")
    # except Exception as e:
    #     print(f"a标签出现错误: {e}")

    time.sleep(1)  # 等待新页面加载

    # 找到table数据并下载
    table_data = []
    try:
        # 找到id为report_finance_devicebusinesstotal_show_paneldiv的div
        panel_div = driver.find_element(By.ID, 'report_finance_devicebusinesstotal_show_paneldiv')

        # 找到第二个table
        tables = panel_div.find_elements(By.TAG_NAME, 'table')
        if len(tables) >= 2:
            second_table = tables[1]

            # 提取tbody中的所有行
            tbody = second_table.find_element(By.TAG_NAME, 'tbody')
            rows = tbody.find_elements(By.TAG_NAME, 'tr')

            # 打印每一行的内容
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                data = [col.text for col in cols]
                dict1=handle_data(data,yesterday)
                table_data.append(dict1)
                dict1={}
        else:
            print("没有找到第二个table")
    except Exception as e:
        print(f"出现错误: {e}")

    # 关闭浏览器
    time.sleep(10)  # 等待一段时间，让数据缓存下
    # 将数据发送到另一个网站
    send_data_to_another_site(table_data,yesterday)

    driver.quit()
    print("成功", "数据抓取并发送成功！",yesterday)
    driver.quit()


def handle_data(data,date):
    # data 是一个list
    dict1={}
    if data[1] == "消费":
        dict1={"name":data[0],"avenue":data[-1],"date":date}
    elif data[2] == "消费":
        dict1={"name":data[1],"avenue":data[-1],"date":date}
    return dict1


# 解析字典中的Unicode转义字符
def decode_unicode_escape(dictionary):
    return {key: value.encode('utf-8').decode('unicode_escape') if isinstance(value, str) else value
            for key, value in dictionary.items()}


# 发送数据到另一个网站
def send_data_to_another_site(data,date):
    url = 'https://lclg.nongxiaotong.com/customer/GetAvenueFromTool'  # 目标网站的 API URLGetAvenueFromTool
    print("send_data_to_another_site:",data,date)  # 你可以将数据存入其他地方，比如列表或文件
    # url = 'http://127.0.0.1:8081/customer/GetAvenueFromTool'  # 目标网站的 API
    headers = {'Content-Type': 'application/json'}
    # 保存在本地txt文件
    response = requests.post(url, json={"data": data,"date": date}, headers=headers)
    import json
    # # 对列表中的每个字典元素进行转义字符解析
    # decoded_data = [decode_unicode_escape(item) for item in data]
    #
    # # 保存到TXT文件
    # with open(str(date)+".txt", "w", encoding="utf-8") as file:
    #     json.dump(decoded_data, file, ensure_ascii=False,indent=4)
    # print("数据已保存到data.txt")
    f = open(str(date)+".json", "w", encoding="utf8")
    json.dump(data, f, ensure_ascii=False)

    if response.status_code == 200:
        print("数据成功发送到目标网站")
    else:
        print("发送数据失败，状态码:", response.status_code)


def execute_task():
    global text_area_execute
    get_table_data(-1)
    print("执行完毕第1个任务")
    timestamp = time.time()  # 获取当前时间戳
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    text_area_execute.insert(tk.END, f"{formatted_time},执行完毕取得昨天数据任务\n")
    text_area_execute.yview(tk.END)  # 保证文本框内容自动滚动到最后
    time.sleep(4)
    # 但是不执行取得当天的数据任务，因为那边网站没有当天数据，
    # get_table_data(0)
    # print("执行完毕第2个任务")
    # timestamp = time.time()  # 获取当前时间戳
    # formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    # text_area_execute.insert(tk.END, f"{formatted_time},执行完毕第2个任务\n")
    # text_area_execute.yview(tk.END)  # 保证文本框内容自动滚动到最后
    return 1


def main_fun():
    global text_area_console,text_area_execute
    # 创建窗口
    root = tk.Tk()
    root.title("Python 桌面小工具")

    # 设置窗口大小
    root.geometry("500x400")  # 宽度800像素，高度600像素
    # 设置界面元素
    # pady=10：指定了标签控件与其他控件（或窗口边缘）之间的垂直间距。pady 表示“上下间距”（"padding"），单位是像素。10 表示上下各留 10 个像素的间距。

    # 创建一个滚动文本框
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=6)
    text_area.pack(padx=10, pady=10)

    # 添加文本内容
    text_content = """现在的设计思路：
    只更新昨天的数据，如果昨天没有营业额数据，则会新增。
    如果有昨天的营业额是数据，则不会更新。
    窗口刚打开的时候检测一下，然后每隔3个小时检测一下。"""
    text_area.insert(tk.INSERT, text_content)
    # 禁用编辑（如果你只想显示文字，不允许用户修改）
    text_area.config(state=tk.DISABLED)
    # print(text_area)
    # url_entry = tk.Entry(root, width=40)
    # url_entry.pack(pady=5)

    # 创建一个滚动文本框
    text_area_console = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=2)
    text_area_console.pack(padx=10, pady=10)

    text_area_execute = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=7)
    text_area_execute.pack(padx=10, pady=10)
    # get_button = tk.Button(root, text="获取数据并发送")#command=lambda: main_fun1(text_area_console),  command=main_fun1
    # get_button.pack(pady=20)
    execute_task()  # 先执行一次任务
    # 记录开始时间
    start_time = time.time()
    update_console_text(start_time)

    # 启动 GUI
    root.mainloop()
    # for i in [16,17,1]:
    #     print(get_time_format(-i))
    #     get_table_data(-i)
    #     time.sleep(60)


def main_fun1():
    while True:
        print("2")
        # task()

        # 记录开始时间
        start_time = time.time()
        # 取得3小时之后的时间
        # 目标时间（3小时后）
        target_time = start_time + 3 * 60 * 60  # 3小时转换为秒
        # 循环检查是否到达目标时间
        while True:
            # 获取当前时间
            current_time = time.time()
            # 检查是否到达3小时
            if current_time >= target_time:
                print("3小时已经过去！")
                break  # 达到目标时间，退出循环
            # 每隔2秒检查一次
            print("每隔2秒检查一次！")
            time.sleep(2)
        # 启动定时器更新等待时间

        # time.sleep(3*60*60)  # 每隔3小时执行一次


def update_console_text(start_time):
    global text_area_console
    # 计算已经过去的时间
    elapsed_time = time.time() - start_time
    # 转换为小时、分钟、秒
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60
    # 更新 text_area_console 显示内容
    text_area_console.delete(1.0, tk.END)  # 清空当前显示内容
    text_area_console.insert(tk.END, f"等待时间: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")
    # print(f"等待时间: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")

    # 每 3 小时执行一次任务
    if elapsed_time >= 3 * 3600:
        execute_task()
        start_time = time.time()  # 重置开始时间，避免多次触发
        text_area_console.insert(tk.END, f"执行完毕任务")
    # 每 1 分钟更新一次
    text_area_console.after(1000, update_console_text, start_time)


#
if __name__ == "__main__":
    # time.sleep(2)
    main_fun()