# -*- coding: utf-8 -*-

import sys
import time
import random
import threading
import webbrowser
import os
from urllib.parse import quote_plus, urlparse, parse_qs
from flask import Flask, request, Response, stream_with_context, make_response
import json
from waitress import serve

# --- Cài đặt các thư viện cần thiết ---
# pip install Flask beautifulsoup4 lxml selenium webdriver-manager waitress

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- Khởi tạo Flask App ---
app = Flask(__name__)

# --- Nội dung HTML của giao diện ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Leading Google SERP</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Be Vietnam Pro', sans-serif; }
        .form-input, .form-select, .form-textarea {
            background-color: #F3F4F6;
            border-color: #D1D5DB;
        }
        .dark .form-input, .dark .form-select, .dark .form-textarea {
            background-color: #374151;
            border-color: #4B5563;
        }
        .group:hover .group-hover\\:text-indigo-400 {
            color: #818cf8;
        }
        /* Custom scrollbar */
        #log-container::-webkit-scrollbar { width: 6px; }
        #log-container::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
        #log-container::-webkit-scrollbar-thumb { background: #888; border-radius: 10px; }
        #log-container::-webkit-scrollbar-thumb:hover { background: #555; }
        .dark #log-container::-webkit-scrollbar-track { background: #2d3748; }
        .dark #log-container::-webkit-scrollbar-thumb { background: #4a5568; }
        .dark #log-container::-webkit-scrollbar-thumb:hover { background: #718096; }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-200">

    <div class="container mx-auto p-4 sm:p-6 lg:p-8">
        <header class="text-center mb-10">
            <h1 class="text-3xl sm:text-4xl font-bold text-indigo-600 dark:text-indigo-400">KIỂM TRA THỨ HẠNG TỪ KHOÁ THEO THỜI GIAN THỰC</h1>
            <p class="text-gray-600 dark:text-gray-400 mt-2">ĐƯỢC CUNG CẤP VÀ BẢO LƯU MỌI BẢN QUYỀN BỞI HATHAWAY</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-5 gap-8">
            <!-- Cột điều khiển -->
            <div class="lg:col-span-2">
                <form id="rank-form" class="space-y-6 bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
                    <div>
                        <label for="keyword" class="text-sm font-semibold">Từ khóa <span class="text-red-500">*</span></label>
                        <input type="text" id="keyword" name="keyword" placeholder="Ví dụ: thiết kế website" required class="mt-2 w-full form-input rounded-lg border-2 p-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition">
                    </div>

                    <div>
                        <label for="domain" class="text-sm font-semibold">Tên miền</label>
                        <input type="text" id="domain" name="domain" placeholder="Chỉ cần cho 'Kiểm tra sâu'" class="mt-2 w-full form-input rounded-lg border-2 p-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition">
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label for="location" class="text-sm font-semibold">Khu vực</label>
                            <select id="location" name="location" class="mt-2 w-full form-select rounded-lg border-2 p-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition">
                                <option value="us">Toàn cầu</option>
                                <option value="vn" selected>Việt Nam</option>
                                <option value="kr">Hàn Quốc</option>
                                <option value="jp">Nhật Bản</option>
                                <option value="sg">Singapore</option>
                                <option value="uk">United Kingdom</option>
                            </select>
                        </div>
                        <div>
                            <label for="device_type" class="text-sm font-semibold">Thiết bị</label>
                            <select id="device_type" name="device_type" class="mt-2 w-full form-select rounded-lg border-2 p-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition">
                                <option>Máy tính (PC)</option>
                                <option>Di động (Mobile)</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Cài đặt nâng cao -->
                    <details class="group">
                        <summary class="flex justify-between items-center font-medium cursor-pointer list-none">
                            <span class="text-sm font-semibold">Cài đặt nâng cao</span>
                            <span class="transition group-open:rotate-180">
                                <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24"><path d="M6 9l6 6 6-6"></path></svg>
                            </span>
                        </summary>
                        <div class="mt-4 space-y-4">
                             <div>
                                <label for="proxies" class="text-sm font-medium text-gray-700 dark:text-gray-300">Danh sách Proxy (mỗi dòng 1 proxy)</label>
                                <textarea id="proxies" name="proxies" rows="3" placeholder="user:pass@ip:port" class="mt-1 w-full form-textarea rounded-lg border-2 p-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"></textarea>
                            </div>
                            <div>
                                <label for="buster_path" class="text-sm font-medium text-gray-700 dark:text-gray-300">Tên file Buster (.crx)</label>
                                <input type="text" id="buster_path" name="buster_path" placeholder="buster_solver.crx" class="mt-1 w-full form-input rounded-lg border-2 p-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition">
                                <p class="text-xs text-gray-500 mt-1">Lưu ý: Đặt file .crx trong cùng thư mục với file main.py</p>
                            </div>
                            <div class="flex items-center space-x-4">
                                <label class="flex items-center cursor-pointer">
                                    <input type="checkbox" id="include_ads" name="include_ads" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
                                    <span class="ml-2 text-sm">Tính cả quảng cáo</span>
                                </label>
                                <label class="flex items-center cursor-pointer">
                                    <input type="checkbox" id="debug_mode" name="debug_mode" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
                                    <span class="ml-2 text-sm">Chế độ gỡ lỗi</span>
                                </label>
                            </div>
                        </div>
                    </details>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                         <button type="button" id="top10-btn" class="group flex items-center justify-center gap-2 w-full rounded-lg bg-green-600 px-4 py-3 text-sm font-bold text-white shadow-lg transition hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50">
                            <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.196-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path></svg>
                            Liệt kê Top 10
                        </button>
                        <button type="button" id="deep-check-btn" class="group flex items-center justify-center gap-2 w-full rounded-lg bg-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg transition hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50">
                            <svg class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                            Kiểm tra sâu
                        </button>
                    </div>
                </form>
            </div>

            <!-- Cột kết quả và log -->
            <div class="lg:col-span-3 space-y-8">
                <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
                    <h2 class="text-xl font-bold mb-4">Kết quả</h2>
                    <div id="result-container" class="min-h-[150px]">
                        <p id="placeholder" class="text-gray-500 dark:text-gray-400">Kết quả sẽ được hiển thị ở đây...</p>
                    </div>
                </div>
                <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
                    <h2 class="text-xl font-bold mb-4">Nhật ký xử lý</h2>
                    <div id="log-container" class="h-64 overflow-y-auto bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg text-sm font-mono space-y-2">
                        <!-- Log messages will be appended here -->
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        const form = document.getElementById('rank-form');
        const top10Btn = document.getElementById('top10-btn');
        const deepCheckBtn = document.getElementById('deep-check-btn');
        const resultContainer = document.getElementById('result-container');
        const logContainer = document.getElementById('log-container');
        const placeholder = document.getElementById('placeholder');
        let eventSource;

        top10Btn.addEventListener('click', () => startCheck('top10'));
        deepCheckBtn.addEventListener('click', () => startCheck('deep'));

        function startCheck(checkType) {
            if (eventSource) {
                eventSource.close();
            }

            const keywordInput = document.getElementById('keyword');
            if (!keywordInput.value.trim()) {
                alert('Vui lòng nhập từ khóa.');
                keywordInput.focus();
                return;
            }

            if (checkType === 'deep') {
                const domainInput = document.getElementById('domain');
                if (!domainInput.value.trim()) {
                    alert('Vui lòng nhập tên miền để kiểm tra sâu.');
                    domainInput.focus();
                    return;
                }
            }

            logContainer.innerHTML = '';
            resultContainer.innerHTML = '';
            resultContainer.appendChild(placeholder);
            placeholder.textContent = 'Đang xử lý, vui lòng chờ...';
            setButtonsState(true);

            const formData = new FormData(form);
            const params = new URLSearchParams();
            for (const pair of formData) {
                // Handle checkboxes correctly
                if (pair[0] === 'include_ads' || pair[0] === 'debug_mode') {
                     params.append(pair[0], document.getElementById(pair[0]).checked);
                } else {
                    params.append(pair[0], pair[1]);
                }
            }
            params.append('check_type', checkType);
            
            const url = `/check?${params.toString()}`;
            eventSource = new EventSource(url);

            eventSource.addEventListener('progress', e => handleEvent(e, appendLog));
            eventSource.addEventListener('result', e => handleEvent(e, displayResult));
            eventSource.addEventListener('error', e => {
                handleEvent(e, appendLog, 'error');
                eventSource.close();
                setButtonsState(false);
            });
            
            eventSource.addEventListener('finished', e => {
                handleEvent(e, appendLog, 'finished');
                eventSource.close();
                setButtonsState(false);
            });

            eventSource.onerror = (err) => {
                console.error("EventSource failed:", err);
                appendLog('Mất kết nối với máy chủ.', 'error');
                eventSource.close();
                setButtonsState(false);
            };
        }
        
        function handleEvent(event, handler, type = 'progress') {
            try {
                const data = JSON.parse(event.data);
                handler(data, type);
            } catch (error) {
                console.error("Failed to parse event data:", event.data);
                appendLog("Lỗi xử lý dữ liệu từ server.", 'error');
            }
        }

        function setButtonsState(isChecking) {
            top10Btn.disabled = isChecking;
            deepCheckBtn.disabled = isChecking;
            top10Btn.textContent = isChecking ? 'Đang chạy...' : 'Liệt kê Top 10';
            deepCheckBtn.textContent = isChecking ? 'Đang chạy...' : 'Kiểm tra sâu';
        }

        function appendLog(message, type) {
            const logItem = document.createElement('div');
            let icon = '';
            let colorClass = '';
            switch(type) {
                case 'error':
                    icon = '❌';
                    colorClass = 'text-red-500';
                    break;
                case 'finished':
                    icon = '✅';
                    colorClass = 'text-green-500 font-bold';
                    break;
                default:
                    icon = '⏳';
                    colorClass = 'text-gray-500 dark:text-gray-400';
            }
            logItem.className = `flex items-center ${colorClass}`;
            logItem.innerHTML = `<span>${icon}</span><span class="ml-2">${message}</span>`;
            logContainer.appendChild(logItem);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        function displayResult(data) {
            placeholder.style.display = 'none';
            resultContainer.innerHTML = '';

            if (data.top_domains) {
                const card = document.createElement('div');
                card.className = 'bg-indigo-50 dark:bg-gray-800 p-4 rounded-lg';
                let listHtml = data.top_domains.map((domain, index) => 
                    `<li class="flex items-center py-1"><span class="text-indigo-500 font-bold mr-3 w-6 text-right">${index + 1}.</span><span>${domain}</span></li>`
                ).join('');
                card.innerHTML = `
                    <h3 class="font-bold text-lg text-indigo-800 dark:text-indigo-300">🏆 Top 10 cho '${data.keyword}'</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Khu vực: ${data.location}</p>
                    <ul class="divide-y divide-indigo-200 dark:divide-gray-700">${listHtml}</ul>
                `;
                resultContainer.appendChild(card);
            } else {
                const card = document.createElement('div');
                card.className = 'bg-green-50 dark:bg-gray-800 p-6 rounded-lg text-center';
                card.innerHTML = `
                    <p class="text-sm text-green-700 dark:text-green-300">Tìm thấy tên miền</p>
                    <p class="text-6xl font-bold text-green-600 dark:text-green-400 my-2">${data.rank}</p>
                    <p class="font-semibold text-green-800 dark:text-green-200">'${data.domain}'</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">(${data.rank_type})</p>
                `;
                resultContainer.appendChild(card);
            }
        }
    </script>
</body>
</html>
"""

# --- Lớp xử lý logic kiểm tra thứ hạng ---
class RankChecker:
    def __init__(self, params):
        self.keyword = params.get('keyword')
        self.domain = params.get('domain', '').lower()
        self.pages_to_check = 10 # Mặc định kiểm tra 10 trang
        self.location = params.get('location', 'us')
        self.proxies = params.get('proxies', [])
        self.debug_mode = params.get('debug_mode', False)
        self.use_buster = bool(params.get('buster_path'))
        self.buster_path = params.get('buster_path', '')
        self.include_ads = params.get('include_ads', False)
        self.device_type = params.get('device_type', 'Máy tính (PC)')
        self.driver = None

    def setup_driver(self):
        yield self.sse_message('progress', f"Đang khởi tạo trình duyệt {self.device_type} ảo...")
        options = Options()

        if self.device_type == "Di động (Mobile)":
            mobile_emulation = {
                "deviceMetrics": { "width": 390, "height": 844, "pixelRatio": 3.0 },
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        else:
            options.add_argument("--window-size=1920,1080")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

        if self.use_buster and self.buster_path:
            if os.path.exists(self.buster_path):
                yield self.sse_message('progress', f"Đang tải tiện ích Buster từ: {self.buster_path}")
                options.add_extension(self.buster_path)
            else:
                yield self.sse_message('error', f"Không tìm thấy file Buster: {self.buster_path}. Vui lòng kiểm tra lại.")
                return
        else:
            options.add_argument("--headless=new")

        if self.proxies:
            proxy = random.choice(self.proxies)
            options.add_argument(f'--proxy-server={proxy}')
            yield self.sse_message('progress', f"Đang sử dụng proxy: {proxy}")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f"--lang=vi-VN")
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(45)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            yield self.sse_message('error', f"Không thể khởi tạo trình duyệt Chrome. Vui lòng kiểm tra cài đặt.\nLỗi: {e}")
            self.driver = None

    def run(self, check_type):
        try:
            yield from self.setup_driver()
            if not self.driver: return

            if self.use_buster:
                yield self.sse_message('progress', "Đã tải tiện ích Buster, chờ 5 giây để hoàn tất cài đặt...")
                time.sleep(5)
            
            if check_type == 'top10':
                yield from self.list_top_domains()
            elif check_type == 'deep':
                yield from self.find_domain_rank()
        except Exception as e:
            yield self.sse_message('error', f"Đã xảy ra lỗi nghiêm trọng: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            yield self.sse_message('finished', 'Hoàn thành!')

    def perform_request(self, url):
        try:
            self.driver.get(url)
        except TimeoutException:
            raise Exception("Lỗi: Hết thời gian chờ tải trang.")

        if "unusual traffic" in self.driver.page_source or "recaptcha" in self.driver.page_source:
            raise Exception("Yêu cầu bị Google chặn (CAPTCHA). Tính năng giải tự động chưa hỗ trợ trên web. Vui lòng thử proxy.")
        
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
        except TimeoutException:
            pass
        
        page_source = self.driver.page_source
        if self.debug_mode:
            with open("debug_page.html", "w", encoding="utf-8") as f: f.write(page_source)
            self.driver.save_screenshot("debug_screenshot.png")
            yield self.sse_message('progress', "Đã lưu file debug (HTML và ảnh chụp màn hình).")

        yield BeautifulSoup(page_source, 'lxml')

    def find_domain_rank(self):
        organic_rank = 0
        total_rank = 0
        found = False
        for page in range(self.pages_to_check):
            yield self.sse_message('progress', f"Đang tìm kiếm trang {page + 1}...")
            query = quote_plus(self.keyword)
            url = f"https://www.google.com/search?q={query}&start={page * 10}&gl={self.location}&num=10"
            time.sleep(random.uniform(2.5, 5.0))

            soup = None
            for item in self.perform_request(url):
                if isinstance(item, BeautifulSoup):
                    soup = item
                else:
                    yield item
            
            if not soup: continue

            search_results = soup.select("div[data-hveid]")
            if not search_results and page == 0:
                yield self.sse_message('error', "Không tìm thấy kết quả ở trang đầu tiên.")
                break

            for result_div in search_results:
                has_h3 = result_div.select_one('h3')
                is_advertisement = self.is_ad(result_div)
                if not has_h3 and not is_advertisement: continue

                link_tag = result_div.select_one('a:has(h3)') or result_div.select_one('a[href]')
                if not link_tag: continue
                
                link = link_tag.get('href', '')
                if not link.startswith(('http', '/url?')): continue

                total_rank += 1
                if not is_advertisement: organic_rank += 1
                
                if self.debug_mode:
                    domain_for_log = self.extract_domain(link)
                    status = "Quảng cáo" if is_advertisement else f"Tự nhiên ({organic_rank})"
                    yield self.sse_message('progress', f"Hạng tổng {total_rank}: [{status}] - {domain_for_log[:40]}")

                extracted_domain = self.extract_domain(link)
                if self.domain and self.domain in extracted_domain:
                    final_rank = total_rank if self.include_ads else organic_rank
                    rank_type = "có tính quảng cáo" if self.include_ads else "không tính quảng cáo"
                    
                    result_data = {
                        "keyword": self.keyword, "domain": self.domain, "location": self.location.upper(),
                        "rank": final_rank, "rank_type": rank_type
                    }
                    yield self.sse_message('result', result_data)
                    found = True
                    return

        if not found:
            yield self.sse_message('error', f"Không tìm thấy '{self.domain}' trong top {self.pages_to_check * 10}.")

    def list_top_domains(self):
        yield self.sse_message('progress', f"Đang lấy Top 10...")
        query = quote_plus(self.keyword)
        url = f"https://www.google.com/search?q={query}&gl={self.location}&num=20"
        
        soup = None
        for item in self.perform_request(url):
            if isinstance(item, BeautifulSoup): soup = item
            else: yield item
        
        if not soup: return

        search_results = soup.select("div[data-hveid]")
        if not search_results:
            yield self.sse_message('error', "Không tìm thấy kết quả.")
            return

        top_domains_list = []
        unique_domains_set = set()
        for result_div in search_results:
            if len(top_domains_list) >= 10: break
            if self.is_ad(result_div): continue
            
            link_tag = result_div.select_one('a:has(h3)')
            if not link_tag: continue
            
            link = link_tag.get('href')
            if not link or not link.startswith(('http', '/url?')): continue

            domain = self.extract_domain(link)
            if domain and domain not in unique_domains_set:
                unique_domains_set.add(domain)
                top_domains_list.append(domain)
        
        if not top_domains_list:
             yield self.sse_message('error', "Không thể trích xuất tên miền.")
             return

        result_data = { "keyword": self.keyword, "location": self.location.upper(), "top_domains": top_domains_list }
        yield self.sse_message('result', result_data)

    def is_ad(self, result_div):
        return result_div.get('data-text-ad') == '1' or result_div.find(string=lambda text: "Được tài trợ" in text or "Sponsored" in text)

    def extract_domain(self, url):
        if url.startswith("/url?"):
            try: url = parse_qs(url.split('?')[1])['q'][0]
            except (KeyError, IndexError): return ""
        try: return urlparse(url).netloc.replace('www.', '')
        except Exception: return ""
        
    def sse_message(self, event, data):
        # FIX: Sử dụng ký tự xuống dòng chuẩn `\n` thay vì `\\n`
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

# --- Các Route của Flask ---
@app.route('/')
def index():
    response = make_response(HTML_CONTENT)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/check')
def check():
    params = {
        'keyword': request.args.get('keyword', ''),
        'domain': request.args.get('domain', ''),
        'location': request.args.get('location', 'us'),
        'include_ads': request.args.get('include_ads') == 'true',
        'debug_mode': request.args.get('debug_mode') == 'true',
        'device_type': request.args.get('device_type', 'Máy tính (PC)'),
        'proxies': [p.strip() for p in request.args.get('proxies', '').splitlines() if p.strip()],
        'buster_path': request.args.get('buster_path', ''),
    }
    check_type = request.args.get('check_type', 'deep')
    
    if not params['keyword']:
        def error_stream():
            yield RankChecker(params).sse_message('error', 'Từ khóa không được để trống.')
        return Response(stream_with_context(error_stream()), mimetype='text/event-stream')

    checker = RankChecker(params)
    return Response(stream_with_context(checker.run(check_type)), mimetype='text/event-stream')

def open_browser():
      webbrowser.open_new_tab('http://127.0.0.1:5001/')

if __name__ == "__main__":
    port = 5001
    threading.Timer(1, open_browser).start()
    print(f"--- Khởi động server với Waitress tại http://0.0.0.0:{port}/ ---")
    serve(app, host='0.0.0.0', port=port)
