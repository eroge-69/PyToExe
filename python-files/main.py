import tkinter as tk
from tkinter import filedialog
import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import hashlib
import threading
import re


class App:
    def __init__(self, root):
        self.test = 0
        self.stop_check = threading.Event()
        self.start_thread = threading.Thread(target=self.start, daemon=True)
        self.process_thread = threading.Thread(target=self.process, daemon=True)

        self.root = root
        self.root.title("Grand-ClassCard-Auto")

        self.file_loc = tk.Label(root, text="단어장")
        self.file_loc.grid(row=0, column=0, padx=10, pady=10)
        self.file_entry = tk.Entry(root, width=50)
        self.file_entry.grid(row=0, column=1)
        self.file_button = tk.Button(root, text="찾기", command=self.file_select)
        self.file_button.grid(row=0, column=2, padx=10, pady=10)

        self.link_label = tk.Label(root, text="주소")
        self.link_label.grid(row=1, column=0, padx=10, pady=10)
        self.link_entry = tk.Entry(root, width=50)
        self.link_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2)


        self.match = tk.IntVar()
        self.is_matching = tk.Checkbutton(root, text="매칭게임", variable=self.match)
        self.is_matching.grid(row=4, column=0, padx=10, pady=10)

        self.start_button = tk.Button(root, text="시작", command=self.start_thread.start, width=50)
        self.start_button.grid(row=4, column=1, padx=10, pady=10, columnspan=2)

        self.log = tk.Text(root, height=10)
        self.log.bind("<Key>", lambda e: "break")
        self.log.grid(row=5, column=0, padx=10, pady=10, columnspan=3)

    def start(self):
        try:
            self.start_button.configure(state="disabled")
            self.log.insert(tk.END, "프로세스 시작...\n")

            if self.file_entry.get() == "":
                raise Exception("단어장 파일을 선택해주세요.")
            self.dict = self.make_answer(self.file_entry.get())
            self.md5dict = {}

            for i in range(int(len(self.dict) / 2)):
                engword = list(self.dict.keys())[i]
                md5word = self.md5_encode(engword)
                self.md5dict[md5word] = engword
            self.log.insert(tk.END, "단어 dict 생성 완료.\n")

            service = Service(ChromeDriverManager().install())
            options = Options()
            options.add_argument('--disable-blink-features=AutomationControlled')
            self.driver = webdriver.Chrome(service=service, options=options)
            login_url = 'https://www.classcard.net/Login'
            self.driver.get(login_url)
            self.log.insert(tk.END, "직접 로그인 완료 후 아래 계속 버튼을 눌러주세요.")

            self.start_button.configure(state="active")
            self.start_button.configure(text="계속")
            self.start_button.configure(command=self.login_wait)

        except Exception as e:
            self.log.insert(tk.END, "오류 발생 : " + str(e) + "\n")
            self.start_button.configure(state="active")
            self.start_button.configure(text="시작")
            self.start_button.configure(command=self.start_thread.start)


    def login_wait(self):
        self.driver.get(self.link_entry.get())
        time.sleep(3)
        self.log.insert(tk.END, "로그인 완료, 시작하시려면 '진행' 버튼을 눌러주세요.\n")
        self.log.insert(tk.END, "매칭게임인 경우 그냥 누르시고\n테스트인 경우 테스트 창에 접속하신후 눌러주세요.\n")

        self.start_button.configure(state="active")
        self.start_button.configure(text="진행")
        self.start_button.configure(command=self.process_thread.start)


    def file_select(self):
        folder_path = filedialog.askopenfilename()
        if folder_path:
            self.file_entry.insert(0, folder_path)

    def process(self):
        while not self.stop_check.is_set():
            if self.match.get() == 1:
                self.matching()
            else:
                self.testing()

    def md5_encode(self, word):
        md5_hash = hashlib.md5()
        word_b = word.encode('utf-8')
        md5_hash.update(word_b)
        result = md5_hash.hexdigest()
        return result

    def invert_dic(self, original_dict):
        inverted_dict = {v: k for k, v in original_dict.items()}
        return inverted_dict

    def make_answer(self, file_path):
        eng_dic = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    key, value = line.split('\t')
                    eng_dic[key] = value

        han_dic = self.invert_dic(eng_dic)
        return dict(eng_dic, **han_dic)

    def matching(self):
        start_button = self.driver.find_element(By.XPATH, '//*[@id="wrapper-learn"]/div[2]/div/div[3]/div/div[2]')
        start_button.click()
        while True:
            try:
                lc1 = self.driver.find_element(By.XPATH, value='//*[@id="left_card_0"]/div/div[1]/div/div')
                lc2 = self.driver.find_element(By.XPATH, value='//*[@id="left_card_1"]/div/div[1]/div/div')
                lc3 = self.driver.find_element(By.XPATH, value='//*[@id="left_card_2"]/div/div[1]/div/div')
                lc4 = self.driver.find_element(By.XPATH, value='//*[@id="left_card_3"]/div/div[1]/div/div')

                rc1 = self.driver.find_element(By.XPATH, value='//*[@id="right_card_0"]/div/div/div/div')
                rc2 = self.driver.find_element(By.XPATH, value='//*[@id="right_card_1"]/div/div/div/div')
                rc3 = self.driver.find_element(By.XPATH, value='//*[@id="right_card_2"]/div/div/div/div')
                rc4 = self.driver.find_element(By.XPATH, value='//*[@id="right_card_3"]/div/div/div/div')

                a = 0
                for lc in [lc1, lc2, lc3, lc4]:
                    lct = lc.text
                    if lct == "":
                        lc = self.driver.find_element(By.XPATH,
                                                      value=f'//*[@id="left_card_{str(a)}"]/div/div[1]/div/a/i')
                        temp1 = lc.get_attribute("data-src")
                        temp2 = temp1.split("/")[-1].rstrip(".mp3")
                        lct = self.md5dict.get(temp2)

                    for rc in [rc1, rc2, rc3, rc4]:
                        if rc.text in self.dict[lct]:
                            lc.click()
                            rc.click()
                            time.sleep(1.5)
                    a = a + 1

            except KeyError:
                self.log.insert(tk.END, "오류: 사전에 없는 단어\n")
            except selenium.common.exceptions.NoSuchElementException:
                #self.log.insert(tk.END, "오류: 해당하는 오브젝트를 찾을 수 없음\n")
                pass
            except selenium.common.exceptions.StaleElementReferenceException:
                #self.log.insert(tk.END, "오류: 요소가 존재하지 않음\n")
                pass
            except selenium.common.exceptions.ElementNotInteractableException:
                #self.log.insert(tk.END, "오류: 요소에 접근 할 수 없음\n")
                pass
            except selenium.common.exceptions.ElementClickInterceptedException:
                #self.log.insert(tk.END, "오류: 요소에 접근 할 수 없음\n")
                pass
            except selenium.common.exceptions.NoSuchWindowException:
                self.log.insert(tk.END, "오류: 창이 닫혔거나 접근할 수 없음\n")
                break
            except Exception as e:
                print(str(e))
                self.log.insert(tk.END, "오류: " + type(e).__name__ + "\n")

    def take_text(self, html):
        match = re.search(r'>(.*?)<', html)
        return match.group(1)

    def testing(self):
        while True:
            try:
                que_num = self.driver.find_element(By.CLASS_NAME, 'current-quest-num').text
                try:
                    checking = self.take_text(self.driver.find_element(By.XPATH,
                                                                       f'//*[@id="testForm"]/div[{que_num}]/div/div[1]/div/div[2]/div/a/div').get_attribute(
                        'outerHTML'))
                    if checking == "오디오 재생":
                        try:
                            audio_path = self.driver.find_element(By.XPATH,
                                                                  f'//*[@id="testForm"]/div[{que_num}]/div/div[1]/div/div[2]/div/a').get_attribute(
                                'data-src')
                            md5_question = audio_path.split("/")[-1].rstrip(".mp3")
                            question = self.md5dict.get(md5_question)
                            answer = self.dict[question]
                            for i in range(6):
                                card = self.driver.find_element(By.XPATH,
                                                                f'//*[@id="testForm"]/div[{que_num}]/div/div[2]/div/div[1]/div[{i + 1}]/label/div/div')
                                if self.take_text(card.get_attribute('outerHTML')) == answer:
                                    while que_num == self.driver.find_element(By.CLASS_NAME, 'current-quest-num').text:
                                        card.click()
                                        time.sleep(0.1)
                        except Exception as e:
                            self.log.insert(tk.END, "오류: " + type(e).__name__ + "\n")
                    else:
                        raise Exception("오류: 알 수 없는 오류\n")
                except:
                    question = self.take_text(self.driver.find_element(By.XPATH,
                                                                       f'//*[@id="testForm"]/div[{que_num}]/div/div[1]/div[2]/div[1]').get_attribute(
                        'outerHTML'))
                    answer = self.dict[question]
                    for i in range(6):
                        card = self.driver.find_element(By.XPATH,
                                                        f'//*[@id="testForm"]/div[{que_num}]/div/div[2]/div/div[1]/div[{i + 1}]/label/div/div')
                        if self.take_text(card.get_attribute('outerHTML')) == answer:
                            while que_num == self.driver.find_element(By.CLASS_NAME, 'current-quest-num').text:
                                card.click()
                                time.sleep(0.1)

            except KeyError:
                self.log.insert(tk.END, "오류: 사전에 없는 단어\n")
            except selenium.common.exceptions.NoSuchElementException:
                self.log.insert(tk.END, "오류: 해당하는 오브젝트를 찾을 수 없음\n")
            except selenium.common.exceptions.StaleElementReferenceException:
                # self.log.insert(tk.END, "오류: 요소가 존재하지 않음\n")
                pass
            except selenium.common.exceptions.ElementNotInteractableException:
                self.log.insert(tk.END, "오류: 요소에 접근 할 수 없음\n")
            except selenium.common.exceptions.ElementClickInterceptedException:
                self.log.insert(tk.END, "오류: 요소에 접근 할 수 없음\n")
            except selenium.common.exceptions.NoSuchWindowException:
                self.log.insert(tk.END, "오류: 창이 닫혔거나 접근할 수 없음\n")
                break
            except Exception as e:
                self.log.insert(tk.END, "오류: " + type(e).__name__ + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()