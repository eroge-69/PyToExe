import requests
import re
import os
import time
import requests
from lxml import etree
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import csv
import os
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import subprocess
import os





headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "abRequestId=c8b02aa8-d5c4-5bf3-b568-0b98a1a240cd; a1=192d1644928xlsjfsh7zjicalkjd31qlbzp9lww8250000254928; webId=e2a22125547c3f225ef924330451f104; gid=yjJfyK42yWD0yjJfyK44juEEJYC1MViMxWuVUYJ3S01TVj28fqyA11888J24jJY8SiqYYyS2; web_session=040069b66c14bd2ac08df2602a354bca45949d; webBuild=4.40.3; acw_tc=7314dac60b4af01055ccd2ae222199590d76742277c424fb12360758a84ff812; xsecappid=xhs-pc-web; unread={'ub':'67165dbf000000002401506a','ue':'671ccaf6000000001b02e1e2','uc':22}; websectiga=2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d; sec_poison_id=004b876c-dfbf-41fc-aec0-d3bad4260f62",
    "priority": "u=0, i",
    "referer": "https://www.xiaohongshu.com/search_result?keyword=%E8%88%AA%E6%8B%8D%E9%AB%98%E6%B8%85%E8%A7%86%E9%A2%91%E7%B4%A0%E6%9D%90&source=web_search_result_notes",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}


def run_script(driver):
    try:
        work_obj = {}
        # 页面高度
        vh = driver.execute_script("return window.innerHeight")
        # 主逻辑函数
        def action():
            last_height = driver.execute_script("return document.body.offsetHeight")
            ul = driver.find_elements(By.CSS_SELECTOR, 'a.cover.ld.mask')
            for index, element in enumerate(ul):
                has_play_icon = driver.execute_script("return!!arguments[0].querySelector('.play-icon')", element)
                work_obj[driver.execute_script("return arguments[0].href", element)] = 1 if has_play_icon else 0
            driver.execute_script(f"window.scrollBy(0, 1000);")
            time.sleep(1.5)
            new_height = driver.execute_script("return document.body.offsetHeight")
            if new_height > last_height:
                return action()
            else:
                print('end')
                print(datetime.now(), f'博主获取完毕，共计{len(work_obj)}条笔记')
                # 遍历字典打印信息并访问 URL
                count = 1
                for url, value in work_obj.items():
                    if value == 0:
                        print(datetime.now(), f'图片笔记，跳过')
                        continue
                    print(f"共计{len(work_obj)}条笔记，正在获取第{count}条。")
                    count += 1
                    resp_3 = requests.get(url, headers=headers, timeout=60)
                    resp_3.encoding = resp_3.apparent_encoding

                    obj_2 = re.compile('originVideoKey":"(?P<href>.*?)"', re.S)
                    match_2 = obj_2.search(resp_3.text)
                    if match_2 == None:
                        obj_3 = re.compile('"masterUrl":"(?P<masterUrl>.*?)"', re.S)
                        match_3 = obj_3.search(resp_3.text)
                        if match_3 == None:
                            print(datetime.now(), f'未找到视频链接')
                            continue
                        masterUrl = match_3.group("masterUrl")
                        mp4_url = masterUrl.replace('\\u002F', '/')
                    else:
                        href = match_2.group('href').replace('\\u002F', '/')
                        mp4_url = f'https://sns-video-bd.xhscdn.com/{href}'
                    # 创建文件夹
                    title = hashlib.sha256(mp4_url.encode()).hexdigest()
                    folder_name = fr"E:\未处理\航拍\袁采集源数据\小红书\{up_id}"
                    os.makedirs(folder_name, exist_ok=True)
                    file_path = os.path.join(folder_name, f"{title}.mp4")
                    if os.path.exists(file_path):
                        print(f"文件已存在: {file_path}, 跳过下载。")

                        # 检查视频是否存在
                    else:
                        try:
                            with requests.get(mp4_url, headers=headers, stream=True,timeout=60) as response:
                                response.raise_for_status()  # 如果请求失败，将抛出HTTPError异常
                                with open(file_path, 'wb') as file:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:  # 过滤掉keep-alive new chunks
                                            file.write(chunk)
                            print(f"成功下载 {up_id}.mp4 到 {file_path}")
                            time.sleep(2)
                        except requests.RequestException as e:
                            print(f"下载文件时发生错误: {e}")
                            # 如果下载失败，删除已创建的文件（如果存在）
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"已删除因错误而创建的文件: {file_path}")

                return work_obj
        return action()
    finally:
        driver.quit()

if __name__ == "__main__":
    s = Service(r"D:\chrom driver\chromedriver.exe")
    options = Options()
    # options.page_load_strategy = 'eager'  # 设置页面加载策略为eager
    # options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(service=s, options=options)
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
    #                        {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})
    driver.implicitly_wait(10)

    cookie_str = '_gid=GA1.2.1489234054.1731383453; _fbp=fb.1.1731383453602.445047197986930187; PAPVisitorId=mTXvCUmALuvKzIVB2gPHtyUCsmfWluZL; _gcl_au=1.1.322785501.1731383455; userVisitorNew=cd294f62-639c-4cdf-a697-1fa45751fc38; ajs_anonymous_id=a4fde9d7-dfbf-4188-afa2-ca5687908f0e; _hjSessionUser_1166798=eyJpZCI6ImNlYmU5YWVjLTY3MWMtNTEwMS1hYzcwLWRmYjYyZmQzOWI3ZSIsImNyZWF0ZWQiOjE3MzEzODM0NTQ2MjMsImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_1166798=eyJpZCI6IjQwODUzMzNjL-ThhM2EtNGJhNy05NDhhLWM4Y2QyZGNhMGQ2NCIsImMiOjE3MzEzOTQ3NDA5MzAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _ga=GA1.2.301439588.1731383453; __cf_bm=Os8aX.uIpM_O5IxT5UUbLvvNMWBpHI7xcsW0IyfOPm4-1731399187-1.0.1.1-GC6ttJRuhWkBVexY2XJqH5GG95xdj.d1yg0mC.fJAQnIPnzafF4SapN0shLAeWXBwpfrIrqvMTHGXA46j1xycQ; cf_clearance=OFRAHZN4g3LoP1dMgmYAh0mrGll3Xbh29S4C9RegyjE-1731399187-1.2.1.1-Uu5cyJbDKwmAsjghY4VRFmUBrCH_xXIDTKduF1PWaOaSZGsiyUwP8Q7igwM3Vwzl0onHiINXBwEBGMJDtLRRMGETBblVTtAbbqCKvoks.3niNpe1S_g5HpOuEGkeCtTAFy5UhkeZk.gvCuLw8MMdUQJI0g22uk_JczMhvKXoz58TI0hVga0R_RkmJFQfsApY6a6lgKmuMqkrYz0atRVMuQsas3ACCp7.GXI3csRuwkGcAM.ObZhj5gJhH22VUv2YcXmr.Vr72EPXdw3JL8wmL9SUo28N_RRzL1skAoIWFx7jPbKYv8vpFls6IwmuhdOUK4r3T_s4IE0wI4hstILVvKz_tBewaqWp3QDR9UF8Zefb58Fzp4AFOkcsfw2Wx_gaWIvXLvXcNy5lrOFSxS1ipQ; _gat_gtag_UA_71276289_3=1; _rdt_uuid=1731383453456.3e25fd7e-218e-447a-9b44-d90bec49ef1d; userSession=1b185b34-989e-4663-ab3f-11123e366171; _ga_YDG5KH2Y7K=GS1.1.1731399186.3.0.1731399191.55.0.0; XSRF-TOKEN=Q9nHgxbztRiZGETzfKtP7OxFLzSwu_v1xoVHJIbLVxqX5Hs9HeL-PAh6ATqJ-DhVUygdhlt0GSNR8maZwvmbNbnM2GM_xxipmPBdOmsvFcY1:1zRNXf2XS3dxd2BNK5pLVAMY5nqSOK8Qywa6FB-q2xz-vkxfdrGfYPt85D-f7JXMyYPTxbZOjd-L-frId8Iprn0javeMsSEn_S5B1_Eiqlk1'

    driver.get('https://artgrid.io')
    # 将cookie字符串分割成单个的cookie项
    cookie_list = cookie_str.split('; ')

    # 遍历每个cookie项，将其添加到driver中
    for cookie in cookie_list:
        cookie_dict = {}
        key_value = cookie.split('=')
        cookie_dict['name'] = key_value[0]
        cookie_dict['value'] = key_value[1]
        driver.add_cookie(cookie_dict)
    time.sleep(1)
    driver.get('https://artgrid.io/category/180/animals-&-wildlife?sortId=1')
    run_script(driver)
