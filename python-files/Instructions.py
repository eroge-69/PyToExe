import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class FBVideoLinkExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Video Link Extractor")
        self.root.geometry("600x400")

        # URL 입력창
        self.label = tk.Label(root, text="페이스북 영상 검색 URL:")
        self.label.pack(pady=5)
        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.pack(pady=5)

        # 버튼
        self.extract_btn = tk.Button(root, text="링크 추출하기", command=self.extract_links)
        self.extract_btn.pack(pady=5)

        self.save_btn = tk.Button(root, text="결과 저장하기", command=self.save_links, state=tk.DISABLED)
        self.save_btn.pack(pady=5)

        # 결과창
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
        self.text_area.pack(pady=10)

        self.links = []

    def extract_links(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("경고", "URL을 입력하세요.")
            return

        driver = webdriver.Chrome()  # 크롬드라이버 필요
        driver.get(url)

        messagebox.showinfo("안내", "페이스북 로그인 후 OK 누르세요.")
        time.sleep(2)

        # 스크롤 여러 번 (더 늘리고 싶으면 range 조정)
        for _ in range(30):
            driver.find_element("tag name", "body").send_keys(Keys.END)
            time.sleep(1.0)

        # 링크 추출
        anchors = driver.find_elements("css selector", "a[href]")
        links = set()
        for a in anchors:
            h = a.get_attribute("href")
            if h and ("/videos/" in h or "/watch/" in h or "?v=" in h):
                links.add(h.split("#")[0])

        driver.quit()

        self.links = sorted(links)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "\n".join(self.links))
        self.save_btn.config(state=tk.NORMAL)
        messagebox.showinfo("완료", f"총 {len(self.links)}개의 링크를 추출했습니다.")

    def save_links(self):
        if not self.links:
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(self.links))
            messagebox.showinfo("저장 완료", f"{filepath} 파일로 저장했습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FBVideoLinkExtractor(root)
    root.mainloop()
