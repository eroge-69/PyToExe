import sys
import pyttsx3
import datetime
import operator
import os
import smtplib
import time
import webbrowser
import pyjokes
import pyautogui
import pywhatkit as kit
import requests
import speech_recognition as sr
import wikipedia
from requests import get
import PyPDF2
from pywikihow import search_wikihow
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pratikUi import Ui_MainWindow

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)
engine.setProperty('rate',160)

# text to speech
def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()

# To Wish
def wish():
    hour = int(datetime.datetime.now().hour)
    tt = time.strftime("%I:%M:%p")

    if hour >= 0 and hour <= 12:
        speak(f"Good Morning Boss, it's {tt}")
    elif hour > 12 and hour < 18:
        speak(f"Good Afternoon Boss, it's {tt}")
    else:
        speak(f"Good Evening Boss, it's {tt}")
    speak("Hii I am ZENO Your virtual assistant, Please tell me how can I help you, Boss?")


# To read the line of PDF
def pdf_reader():
    book = open('py3.pdf', 'rb')
    pdfReader = PyPDF2.PdfFileReader(book)  # pip install PyPDF2
    pages = pdfReader.numPages
    speak(f"Total number of pages in this book: {pages}")
    speak("Sir, please enter the page number which I have to read.")
    pg = int(input("Please enter the page number Pratik: "))
    page = pdfReader.getPage(pg)
    text = page.extractText()
    speak(text)

# To send Email
def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('your email', 'your password')
    server.sendmail('your email', to, content)
    server.close()


class MainThread(QThread):
    def __init__(self):
        super(MainThread,self).__init__()

    def run(self):
        self.TaskExecution()   

 # To take command from the user
    def takecommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Zeno: Listening...")
            r.pause_threshold = 1
            try:
                # Increased timeout to 5 seconds to avoid quick timeouts
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                speak("zeno:  I didn't hear Anything. Could you please speak again?")
                return "none"
            except Exception as e:
                speak(f"Sorry, there was an error: {str(e)}")
                return "none"

            try:
                print("Recognizing...")
                query = r.recognize_google(audio, language='en-in')
                print(f"Pratik: {query}\n")
            except sr.UnknownValueError:
                speak("Sorry, I could not understand what you said.")
                return "none"
            except sr.RequestError:
                speak("Sorry, I'm having trouble connecting to the speech recognition service.")
                return "none"
            query = query.lower()
        return query       


    def TaskExecution(self):    
        wish()
        while True:
            self.query = self.takecommand()

            # Logic building for tasks

            if "open notepad" in self.query:
                npath = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Accessories\\notepad.exe"
                os.startfile(npath)
                speak("Openaing notepad")

            if "open This pc" in self.query:
                os.startfile("explorer.exe shell:::{20D04FE0-3AEA-1069-A2D8-08002B30309D}")
                speak("Openaing This pc")

            if "open V S-Code" in self.query:
                qpath = "C:\\Users\\HP\\AppData\\Local\\Programs\\Microsoft VS Code.exe"
                os.startfile(qpath)
                speak("Openaing v s-code")

            if "open Q T-Desiner" in self.query:
                apath = "C:\\Program Files (x86)\\Qt Designer.exe"
                os.startfile(apath)
                speak("Openaing Q T-Desiner")        


            elif "open command prompt" in self.query:
                os.system("start cmd")
                speak("Openaing cmd")


            elif 'volume up' in self.query:
                pyautogui.press("volumeup")

            elif 'volume down' in self.query:
                pyautogui.press("volumedown")

            elif 'volume mute' in self.query:
                pyautogui.press("volumemute")  


            elif "my ip address" in self.query:
                ip = get('https://api.ipify.org').text
                speak(f"Your IP address is {ip}")


            elif "wikipedia" in self.query:
                speak("Searching Wikipedia...")
                self.query = self.query.replace("wikipedia", "")
                results = wikipedia.summary(self.query, sentences=2)
                speak("According to Wikipedia:")
                speak(results)

            elif "open youtube" in self.query:
                webbrowser.open("https://www.youtube.com")
                speak("Openaing youtube")

            elif "open arjit song on youtub" in self.query:
                webbrowser.open("https://www.youtube.com/results?search_query=arjit+singh+song")
                speak("playing song")    

            elif "open facebook" in self.query:
                webbrowser.open("https://www.facebook.com")
                speak("Openaing facebook")

            elif "open instagram" in self.query:
                webbrowser.open("https://www.instagram.com")
                speak("Openaing instagram")

            elif "open google" in self.query:
                speak("Sir, what should I search on Google?")
                cm = self.takecommand()
                webbrowser.open(f"https://www.google.com/search?q={cm}")



            elif "send message to Adinath" in self.query:
                kit.sendwhatmsg("+919359235729", "Hello", 2, 25)
                speak("sending message")

            elif "send message to Shivam-Bro" in self.query:
                kit.sendwhatmsg("+918605251745", "Hello", 2, 25)
                speak("sending message")

            elif "send message to vaishnav G" in self.query:
                kit.sendwhatmsg("+919209503180", "Hello", 2, 25)
                speak("sending message")





            elif "open hindi songs" in self.query:
                kit.playonyt("https://www.youtube.com/results?search_query=new+hindi+song+2025")
                speak("playing hindi songs")

            elif "open ChatGPT" in self.query:
                webbrowser.open("https://openai.com/")
                speak("opeaning chatgpt")

            elif "open Flipkart" in self.query:
                webbrowser.open("https://www.flipkart.com/")
                speak("opeaning flipkart")

            elif "open Amazon" in self.query:
                webbrowser.open("https://www.amazon.com/")
                speak("opeaning amazon")

            elif "open scanner" in self.query:
                webbrowser.open("https://qrcodescan.in/")
                speak("opeaning scanner")    

            elif "open Google-Map" in self.query:
                webbrowser.open("https://www.google.com/maps/@19.9350847,74.2391035,17z?entry=ttu&g_ep=EgoyMDI1MDIyNS4wIKXMDSoASAFQAw%3D%3D")
                speak("opeaning google-map")    

            elif "open Clock" in self.query:
                webbrowser.open("https://www.bing.com/search?q=clock+timer&form=WNSGPH&qs=AS&cvid=83d864d998494be59048bc9edb519099&pq=clock&cc=IN&setlang=en-US&nclid=3B79D686526F5925BDCA39E692E925C7&ts=1740740056593&wsso=Moderate")
                speak("opeaning clock")

            elif "open Cricket Score" in self.query:
                webbrowser.open("https://www.cricbuzz.com/cricket-match/live-scores")
                speak("opeaning score")

            elif "open vivo store" in self.query:
                webbrowser.open("https://www.vivo.com/in/product/activity/56")        


            elif "send email to pratik" in self.query:
                try:
                    speak("What shall I send?")
                    content = self.takecommand()
                    to = "pratikghumare2006@gmail.com"
                    sendEmail(to, content)
                    speak("Email has been sent")
                except Exception as e:
                    print(e)
                    speak("Sorry sir, I am not able to send the email.")
                    speak("Thanks for using me, sir. Have a good day.")
                    sys.exit()

            elif "send email to kaki" in self.query:
                try:
                    speak("What shall I send?")
                    content = self.takecommand()
                    to = "sangitaghumare2004@gmail.com"
                    sendEmail(to, content)
                    speak("Email has been sent")
                except Exception as e:
                    print(e)
                    speak("Sorry sir, I am not able to send the email.")
                    speak("Thanks for using me, sir. Have a good day.")
                    sys.exit()        


            # To close the application
            elif "close notepad" in self.query:
                speak("Ok Pratik, closing notepad")
                os.system("taskkill /f /im notepad.exe")


            elif "close cmd" in self.query:
                speak("Ok Pratik, closing cmd")
                os.system('taskkill /f /im cmd.exe')



            # To set an alarm
            elif "set alarm" in self.query:
                nn = int(datetime.datetime.now().hour)
                if nn == 22:
                    music_dir = 'F:\\Brezza song\\Saurabh'
                    songs = os.listdir(music_dir)
                    os.startfile(os.path.join(music_dir, songs[0]))


            # To tell a joke
            elif "tell me jokes" in self.query:
                joke = pyjokes.get_joke()
                speak(joke)

            elif "shut down the system" in self.query:
                os.system("shutdown /s /t 5")
                speak("Ok Pratik, I am shutdowning system")

            elif "restart the system" in self.query:
                os.system("shutdown /r /t 5")
                speak("Ok Pratik, I am restarting system")

            elif "sleep the system" in self.query:
                os.system("rundll32.exe powr.dll,SetSuspendState 0,1,0")
                speak("Ok Pratik, Know I am sleaping, Byy")


            # To switch window
            elif 'switch the window' in self.query:
                import pyautogui
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(1)
                pyautogui.keyUp("alt")
                speak("switiching window")


            # To read news
            elif "tell me today's news" in self.query:
                speak("Please wait for it, I am searching the news")
                # You can implement your news fetching logic here.


            # To perform calculations
            elif "do some calculation" in self.query or "can you calculate" in self.query:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    speak("Tell me what you want to calculate, for example: 4 plus 5")
                    print("Listening...")
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                my_string = r.recognize_google(audio, language='en-in')
                print(my_string)

                def get_operator_fn(op):
                    return {
                        '+' : operator.add,  # plus
                        '-' : operator.sub,  # minus
                        'x' : operator.mul,  # multiplied by
                        'divided' : operator.truediv,  # divided
                    }[op]

                def eval_binary_expr(op1, oper, op2):
                    op1, op2 = int(op1), int(op2)
                    return get_operator_fn(oper)(op1, op2)

                speak("Your result is here")
                speak(eval_binary_expr(*(my_string.split())))


            # To find location
            elif "where am i" in self.query or "where we are" in self.query:
                speak("Wait sir, let me check your location...")
                try:
                    ipAdd = requests.get('https://api.ipify.org').text
                    url = f'https://get.geojs.io/v1/ip/geo/{ipAdd}.json'
                    geo_requests = requests.get(url)
                    geo_data = geo_requests.json()

                    city = geo_data['city']
                    country = geo_data['country']
                    speak(f"Pratik, I am not sure, but I think we are in {city} city of {country} country.")
                except Exception as e:
                    speak("Sorry Pratik, due to network issue I am not able to find where we are right now.")
                    pass


            # To take screenshot
            elif "take screenshot" in self.query or "take a screenshot" in self.query:
                speak("Pratik, please tell me the name to save the screenshot file.")
                name = self.takecommand()
                speak("Pratik, please hold the screen for a moment. I am taking the screenshot...")
                time.sleep(4)
                img = pyautogui.screenshot()
                img.save(f"{name}.png")
                speak("I have taken the screenshot, Pratik. It's saved in our folder.")


            # To read PDF
            elif "read pdf" in self.query:
                pdf_reader()


            # To handle files visibility
            elif "hide my files" in self.query or "hide this folder" in self.query or "visible for everyone" in self.query:
                speak("Pratik, please tell me whether you want to hide this folder or make it visible for everyone.")
                condition = self.takecommand()
                if "hide" in condition:
                    os.system("attrib +h D:/App")
                    speak("Pratik, all files are hidden for everyone.")
                elif "visible" in condition:
                    os.system("attrib -h D:/App")
                    speak("Pratik, all files are visible for everyone.")
                else:
                    speak("Ok Pratik, I will leave it.")


            elif "activate how to do mode" in self.query:

                speak("How to do mode is activated please tell me what you want to know?")
                how = self.takecommand()
                max_results = 1
                how_to = search_wikihow(how, max_results)
                assert len(how_to) == 1
                how_to[0].print()
                speak(how_to[0].summary)


            elif "how much power left" in self.query or "how much power we have" in self.query or "battery" in self.query:
                import psutil
                battery = psutil.sensors_battery()
                percentage = battery.percent
                speak(f"Pratik in our system have {percentage} percent battery left")  
                if percentage>=75:
                    speak("we have enough power to continue our work")
                elif percentage>=40 and percentage<=75:
                    speak("we should connect our system to charging point to charge our battery")
                elif percentage<=15 and percentage<=30:
                    speak("We don't have enough power to work, please connect to charging")
                elif percentage<=15:
                    speak("we have too low power, please connect to charging either system will shutdown very soon...")    


            elif "tell me internet speed" in self.query:

                import speedtest
                st = speedtest.Speedtest()
                dl = st.download()
                up = st.upload()
                speak(f"Pratik we have {dl} bit per second downloading speed and {up} bit per second uploading speed")
 

startExecution = MainThread()



class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)

    def startTask(self):
        self.ui.movie = QtGui.QMovie("zeno12.jpg")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("zeno1.gif")
        self.ui.label_2.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("light2.jpg")
        self.ui.label_3.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("zeno10.jpg")
        self.ui.label_4.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("zeno10.jpg")
        self.ui.label_5.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("zeno8.gif")
        self.ui.label_6.setMovie(self.ui.movie)
        self.ui.movie.start()
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000) 
        startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_time)
        self.ui.textBrowser_2.setText(label_date)   

app = QApplication(sys.argv)
jarvis = Main()
jarvis.show()
exit(app.exec_()) 
speak("Let's try again or continue with other tasks.")

