import tkinter as tk
from tkinter import ttk
import threading
import time
import random

FAKE_LOGS = [
    "위험 요소 탐지: 악성 사이트 연결 기록 발견",
    "취약점 스캔: 포트 445 접근 시도 차단",
    "브라우저 캐시 정리 중...",
    "쿠키 삭제 완료",
    "레지스트리 복구: 시스템 키 재설정",
    "악성 파일 제거 완료",
    "네트워크 위협 요소 차단",
    "시스템 복원 지점 생성 완료"
]

class DKSecurityPlusModern:
    def __init__(self, root):
        self.root = root
        self.root.title("DK Security +")
        self.root.geometry("700x600")
        self.root.configure(bg="#f5f9fc")
        self.root.resizable(False, False)

        self.create_ui()

    def create_ui(self):
        # 상단 제목
        header_frame = tk.Frame(self.root, bg="#f5f9fc")
        header_frame.pack(pady=20)
        title_label = tk.Label(header_frame, text="DK Security +", font=("맑은 고딕", 22, "bold"), fg="#1a1a1a", bg="#f5f9fc")
        title_label.pack()
        subtitle_label = tk.Label(header_frame, text="Trust · Protect · Harden", font=("맑은 고딕", 12), fg="#4a4a4a", bg="#f5f9fc")
        subtitle_label.pack()

        # 상태 표시
        self.status_label = tk.Label(self.root, text="상태: 대기 중", font=("맑은 고딕", 12), fg="#0078ff", bg="#f5f9fc")
        self.status_label.pack(pady=5)

        # 진행바
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=20, troughcolor='#dce3e8', background='#0078ff', bordercolor='#dce3e8')
        self.progress = ttk.Progressbar(self.root, length=500, mode='determinate', style="TProgressbar")
        self.progress.pack(pady=15)

        # 로그창
        self.log_box = tk.Text(self.root, height=15, width=80, state='disabled', bg="#1a1a1a", fg="#00ff88", font=("Consolas", 10))
        self.log_box.pack(pady=10)

        # 버튼
        button_frame = tk.Frame(self.root, bg="#f5f9fc")
        button_frame.pack(pady=10)

        scan_btn = tk.Button(button_frame, text="지금 검사", command=self.start_fake_scan,
                             font=("맑은 고딕", 12, "bold"), fg="white", bg="#0078ff", activebackground="#005bb5",
                             relief="flat", width=15, height=2)
        scan_btn.grid(row=0, column=0, padx=5)

        deep_btn = tk.Button(button_frame, text="심층 검사", command=lambda: self.start_fake_scan(deep=True),
                             font=("맑은 고딕", 12, "bold"), fg="white", bg="#28a745", activebackground="#1e7e34",
                             relief="flat", width=15, height=2)
        deep_btn.grid(row=0, column=1, padx=5)

        purge_btn = tk.Button(button_frame, text="긴급 복구", command=lambda: self.start_fake_scan(emergency=True),
                              font=("맑은 고딕", 12, "bold"), fg="white", bg="#dc3545", activebackground="#a71d2a",
                              relief="flat", width=15, height=2)
        purge_btn.grid(row=0, column=2, padx=5)

    def start_fake_scan(self, deep=False, emergency=False):
        thread = threading.Thread(target=self.fake_scan_process, args=(deep, emergency))
        thread.start()

    def fake_scan_process(self, deep, emergency):
        self.status_label.config(text="상태: 검사 중...")
        self.progress["value"] = 0
        self.clear_log()

        log_count = 8 if deep else 5
        if emergency:
            log_count = 10

        for i in range(log_count):
            time.sleep(random.uniform(0.5, 1.0))
            self.add_log(random.choice(FAKE_LOGS))
            self.progress["value"] = ((i+1) / log_count) * 100
            self.root.update_idletasks()

        self.status_label.config(text="상태: 완료 ✔")
        self.add_log("=== 검사 완료 ===")

    def add_log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def clear_log(self):
        self.log_box.config(state='normal')
        self.log_box.delete(1.0, tk.END)
        self.log_box.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = DKSecurityPlusModern(root)
    root.mainloop()
