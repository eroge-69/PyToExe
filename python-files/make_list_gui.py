# make_list_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
import io

# --------------------------------------------------------------------
# 1. 기존의 파일 분석 및 리포트 생성 로직 (엔진 부분)
# 이 부분은 이전과 동일하며, GUI의 버튼을 눌렀을 때 내부적으로 실행됩니다.
# --------------------------------------------------------------------

def parse_csv_file(file_path):
    encodings = ['utf-16', 'utf-8-sig', 'cp949']
    for encoding in encodings:
        try:
            with open(file_path, mode='r', encoding=encoding, newline='') as csvfile:
                lines = csvfile.readlines()
                header_start_index = -1
                for i, line in enumerate(lines):
                    line_upper = line.upper()
                    if 'FILENAME' in line_upper and 'MD5' in line_upper and 'SHA1' in line_upper:
                        header_start_index = i
                        break
                if header_start_index == -1:
                    continue
                header_line = lines[header_start_index]
                data_lines = lines[header_start_index + 1:]
                delimiter = '\t' if header_line.count('\t') > header_line.count(',') else ','
                header_reader = csv.reader(io.StringIO(header_line), delimiter=delimiter)
                fieldnames = next(header_reader)
                reader = csv.DictReader(data_lines, fieldnames=fieldnames, delimiter=delimiter)
                files_data = []
                for row in reader:
                    row_data = {str(k).strip().upper(): v for k, v in row.items() if k}
                    filename = row_data.get('FULLPATH') or row_data.get('FILENAME')
                    if not filename: continue
                    hashes = []
                    if row_data.get('MD5'): hashes.append({'type': 'MD5', 'value': row_data['MD5']})
                    if row_data.get('SHA1'): hashes.append({'type': 'SHA1', 'value': row_data['SHA1']})
                    if row_data.get('SHA256'): hashes.append({'type': 'SHA256', 'value': row_data['SHA256']})
                    if hashes:
                        files_data.append({'filename': filename, 'hashes': hashes})
                if files_data:
                    return files_data
        except Exception:
            continue
    return None

def parse_txt_file(file_path):
    files_data = []
    encodings = ['utf-8-sig', 'utf-16', 'cp949']
    for encoding in encodings:
        try:
            with open(file_path, mode='r', encoding=encoding) as txtfile:
                content = txtfile.read()
            records = content.strip().replace('\x00', '').split('\n\n')
            parsed_records = []
            for record in records:
                lines = record.strip().split('\n')
                data = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()
                filename = data.get('Path')
                algorithm = data.get('Algorithm')
                hash_value = data.get('Hash')
                if filename and algorithm and hash_value:
                    parsed_records.append({'filename': filename, 'hashes': [{'type': algorithm, 'value': hash_value}]})
            if parsed_records:
                return parsed_records
        except Exception:
            continue
    return None

def generate_html_report(files_data, output_filename="전자정보_상세목록.html"):
    total_files = len(files_data)
    html_content = f"""
    <!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><title>전자정보 상세목록</title>
    <style>body{{font-family:'Malgun Gothic','맑은 고딕',sans-serif;width:210mm;margin:auto;padding:15mm;box-sizing:border-box}}.header{{text-align:center;margin-bottom:20px}}.header h1{{font-size:24px;font-weight:bold;margin:0}}.info-table{{width:100%;border-collapse:collapse;border:2px solid black}}.info-table th,.info-table td{{border:1px solid black;padding:8px;text-align:center;vertical-align:middle;font-size:11pt}}.info-table th{{background-color:#EAEAEA;font-weight:bold}}.total-files-cell{{text-align:right;font-size:12pt;padding-bottom:5px}}.category-col{{width:25%;background-color:#F8F8F8;font-weight:bold}}.content-col{{width:65%;text-align:left;word-break:break-all}}.num-col{{width:10%}}.hash-block p{{margin:0 0 5px 0;padding:0}}.hash-block p:last-child{{margin-bottom:0}}</style>
    </head><body><div class="header"><h1>전자정보 상세목록</h1></div><div class="total-files-cell"><b>총 {total_files}개 파일</b></div>
    <table class="info-table"><thead><tr><th class="num-col">번호</th><th class="category-col">구분</th><th class="content-col">내용</th></tr></thead><tbody>
    """
    for i, file_info in enumerate(files_data, 1):
        filename = file_info['filename']
        hashes_html = "<div class='hash-block'>"
        for h in file_info['hashes']:
            hashes_html += f"<p>{h['value']} ({h['type']})</p>"
        hashes_html += "</div>"
        html_content += f"""
        <tr><td class="num-col" rowspan="2">{i}</td><td class="category-col">파일명</td><td class="content-col">{filename}</td></tr>
        <tr><td class="category-col">해시값 (해시종류)</td><td class="content-col">{hashes_html.strip()}</td></tr>
        """
    html_content += """
    </tbody></table><div style="text-align:right;margin-top:20px;font-size:10pt;color:grey;">210mm×297mm[백상지 80g/m² 또는 중질지 80g/m²]</div></body></html>
    """
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

# --------------------------------------------------------------------
# 2. GUI 프로그램 로직 (사용자 인터페이스 부분)
# --------------------------------------------------------------------

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("전자정보 상세목록 생성 도구")
        self.master.geometry("500x250") # 창 크기 설정
        self.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.selected_file_path = ""
        self.create_widgets()

    def create_widgets(self):
        # 파일 선택 프레임
        file_frame = tk.Frame(self)
        file_frame.pack(fill="x", pady=10)

        self.select_button = tk.Button(file_frame, text="입력 파일 선택 (.csv, .txt)", command=self.select_file, width=25)
        self.select_button.pack(side="left", padx=(0, 10))

        self.file_label = tk.Label(file_frame, text="선택된 파일이 없습니다.", relief="sunken", anchor="w", justify="left")
        self.file_label.pack(side="left", fill="x", expand=True)

        # 실행 버튼
        self.run_button = tk.Button(self, text="✅ 목록 생성 실행", command=self.run_generation, font=('Helvetica', 12, 'bold'), height=2)
        self.run_button.pack(fill="x", pady=20)

        # 상태 메시지 라벨
        self.status_label = tk.Label(self, text="준비", relief="ridge", anchor="w")
        self.status_label.pack(fill="x", side="bottom")

    def select_file(self):
        filetypes = (("지원하는 파일", "*.csv *.txt"), ("모든 파일", "*.*"))
        filepath = filedialog.askopenfilename(title="입력 파일을 선택하세요", filetypes=filetypes)
        if filepath:
            self.selected_file_path = filepath
            # 파일 경로가 너무 길면 줄여서 표시
            display_path = os.path.basename(filepath)
            if len(filepath) > 50:
                display_path = "..." + filepath[-47:]
            self.file_label.config(text=display_path)
            self.status_label.config(text="파일이 선택되었습니다. '목록 생성 실행'을 눌러주세요.")

    def run_generation(self):
        if not self.selected_file_path:
            messagebox.showerror("오류", "먼저 입력 파일을 선택해야 합니다.")
            return

        self.status_label.config(text="처리 중... 잠시만 기다려주세요.")
        self.update_idletasks() # 상태 메시지 즉시 업데이트

        try:
            file_data = None
            if self.selected_file_path.lower().endswith('.csv'):
                file_data = parse_csv_file(self.selected_file_path)
            elif self.selected_file_path.lower().endswith('.txt'):
                file_data = parse_txt_file(self.selected_file_path)

            if not file_data:
                raise ValueError("파일에서 데이터를 추출할 수 없습니다. 파일 형식이나 내용을 확인해 주세요.")

            output_filename = "전자정보_상세목록.html"
            generate_html_report(file_data, output_filename)
            
            self.status_label.config(text=f"성공! '{output_filename}' 파일이 저장되었습니다.")
            messagebox.showinfo("성공", f"전자정보 상세목록이 성공적으로 생성되었습니다.\n\n저장된 파일: {os.path.abspath(output_filename)}")

        except Exception as e:
            self.status_label.config(text="오류 발생!")
            messagebox.showerror("오류 발생", f"작업 중 오류가 발생했습니다:\n{e}")

# --- 프로그램 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()