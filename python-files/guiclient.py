import os, sys
import json

import socket
import time
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import pyaudio
import wave
import keyboard
import requests
import threading
import getpass
from colorama import Fore, Back, Style
import tkinter as tk
from tkinter import ttk

def redraw_chat(chatlist):
    global username, msg_frame, canvas
    # clear old messages
    for widget in msg_frame.winfo_children():
        widget.destroy()
    
    for i in chatlist:
        try:
            if username in i:
                label = tk.Label(msg_frame, text=i.replace("\n", "").split("--> ")[1], bg="#DCF8C6",
                                 anchor="e", justify="right", wraplength=250)
                label.pack(anchor="e", pady=2, padx=5)
            else:
                label = tk.Label(msg_frame, text=i.replace("\n", "").split("--> ")[1], bg="#FFFFFF",
                                 anchor="w", justify="left", wraplength=250)
                label.pack(anchor="w", fill="x", padx=5, pady=2)
        except IndexError: #when i is not a message
            pass
    
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)




def recive():
    global ai, chat, chatlist, firsttranslate, language, username, reciver
    

    if tktranslate.get():
        firsttranslate = False
        response = client.models.generate_content(
            model=model_id,
            contents=[chat, f"Translate every message in this chat that was sent by {reciver}. Do not translate messages sent by {username}. Translate to {language}. Your response will contain only the chat translated and nothing else. Keep the formating the exact same as the original chat, do not change how the user is displayed before the message."]
        )
        chatlist = response.text.split("\n")
    else:
        chatlist = chat.split("\n")
       
    redraw_chat(chatlist)
    #try:
    open(f"{username}//chats//{reciver}.txt", "w").write(chat)
    #except FileNotFoundError:


    while True:
        mes = username + "//" + reciver
        s = socket.socket()
        s.connect((sendurl, sendport))
        s.send(mes.encode("utf-8"))
        chat = s.recv(20000000).decode("utf-8")
        s.close()

        

        if chat != open(f"{username}//chats//{reciver}.txt").read() or firsttranslate:
            firsttranslate = False
            if tktranslate.get():
                response = client.models.generate_content(
                    model=model_id,
                    contents=[chat, f"Translate every message in this chat that was sent by {reciver}. Do not translate messages sent by {username}. Translate to {language}. Your response will contain only the chat translated and nothing else. Keep the formating the exact same as the original chat, do not change how the user is displayed before the message."]
                )
                chatlist = response.text.split("\n")
            else:
                chatlist = chat.split("\n")

            redraw_chat(chatlist)
            open(f"{username}//chats//{reciver}.txt", "w").write(chat)


        time.sleep(3)

def send(event=None):
        try:
            global ai, chat, entry, username, reciver
                
            #mes = "asd@gmail.com//qwe@gmail.com//Cso fasz"
            be = entry.get().strip()
            entry.delete(0, tk.END)

            if tkformal.get():
                response = client.models.generate_content(
                    model=model_id,
                    contents=["this is the convesation so far: ", chat, "write the following message in a more formal/polite way, DO NOT change the language of the message, only use utf-8 character, dont use weird language, just usual polite speech: ", be, " dont say anything else, just the message, write only one answer"]
                )
                be = response.text


            elif tkautocorrect.get():
                response = client.models.generate_content(
                    model=model_id,
                    contents=["Correct grammar mistakes of this text, DO NOT change the language of the message, only use utf-8 character your repsonse will only contain the gramatically fixed text and nothing else, this is the text: ", be],
                )
                be = response.text

            mes = f"{username}//{reciver}//{be}"
            s = socket.socket()
            s.connect((reciveurl, reciveport))
            s.send(mes.encode("utf-8"))
            s.close() 

            
            time.sleep(2)
        except EOFError:
            pass

goback = False
def back():
    global goback
    wd()
    root.quit()
    goback = True

##################################################################################

urls = requests.get('https://mess.pythonanywhere.com').text
urls = urls.replace("Public URL: ", "").replace("  ->  Local: ", "").replace("tcp://", "").split()
urls2 = []
for i in urls:
    urls2.append(i.split("localhost:"))

urls2.sort(key=lambda x: x[1])


reciveurl = urls2[0][0].split(":")[0]
loginurl = urls2[1][0].split(":")[0]
sendurl = urls2[2][0].split(":")[0]

reciveport = int(urls2[0][0].split(":")[1])
loginport = int(urls2[1][0].split(":")[1])
sendport = int(urls2[2][0].split(":")[1])



#this is jsut to get rid of yellow warnings
client = None
google_search_tool = None
model_id = None

##################################################################################
root = tk.Tk()
while True:

    username = None
    password = None
    username_login = None
    password_login = None
    username_reg = None
    password_reg = None


    def wd(event=None):
        for widget in root.winfo_children():
            widget.destroy()

    def quit():
        wd()
        root.quit()

    def signup(event=None):
        wd()
        global username_entry_reg, password_entry_reg

        username_label_reg = tk.Label(root, text = 'Username', font =('arial', 10, 'bold')).grid(row=0, column=0)
        username_entry_reg = tk.Entry(root, font=('arial', 10, 'normal'))
        username_entry_reg.grid(row=0, column=1)

        password_label_reg = tk.Label(root, text = 'Password', font =('arial', 10, 'bold')).grid(row=1, column=0)
        password_entry_reg = tk.Entry(root, font=('arial', 10, 'normal'), show='*')
        password_entry_reg.grid(row=1, column=1)

        continue_button_reg = tk.Button(root, text= 'Continue', command=signup2).grid(row=2)

    def signup2(event=None):
        global username, password, loginurl, loginport
        username_reg = username_entry_reg.get()
        password_reg = password_entry_reg.get()

        mes = "signup//" + username_reg + "//" + password_reg

        s = socket.socket()
        s.connect((loginurl, loginport))
        s.send(mes.encode("utf-8"))
        mes = s.recv(1024).decode("utf-8")
        s.close()

        if mes == "accepted":
            username = username_reg
            password = password_reg
            reg_accepted = tk.Label(root, text = 'Sign up completed successfully!')
            proceed_after_reg = tk.Button(root, text = 'Continue', command = quit())

        elif mes == "denied":
            reg_denied = tk.Label(root, 'Your username is taken, please use an another one')
            reg_tryagain = tk.Button(root, text = 'Try again', command = tryagain())

        else:
            reg_unknown_error = tk.Label(root, text= 'An unknown error occurred, please try again!')
            reg_tryagain_ue = tk.Button(root, text= 'Try again', command = tryagain())


    def login(event=None):
        wd()
        
        global username_entry_login, password_entry_login

        username_label_login = tk.Label(root, text = 'Username', font =('arial', 10, 'bold')).grid(row=0, column=0)
        username_entry_login = tk.Entry(root, font=('arial', 10, 'normal'))
        username_entry_login.grid(row=0, column=1)

        password_label_login = tk.Label(root, text = 'Password', font =('arial', 10, 'bold')).grid(row=1, column=0)
        password_entry_login = tk.Entry(root, font=('arial', 10, 'normal'), show='*')
        password_entry_login.grid(row=1, column=1)

        continue_button_login = tk.Button(root, text= 'Continue', command=login2).grid(row=2)


    def login2(event=None):
        global username, password, loginurl, loginport
        username_login = username_entry_login.get()
        password_login = password_entry_login.get()

        mes = "login//" + username_login + "//" + password_login

        try:
            s = socket.socket()
            s.connect((loginurl, loginport))
            s.send(mes.encode("utf-8"))
            mes = s.recv(1024).decode("utf-8")
            s.close()
            if mes == "accepted":
                username = username_login
                password = password_login
                wd()
                login_accepted = tk.Label(root, text= 'Login successfull!').grid(row=0)
                proceed_after_login = tk.Button(root, text= 'Continue', command = quit).grid(row=1)
            elif mes == "denied":
                wd()
                login_notaccepted = tk.Label(root, text = 'Login unsuccessfull! Please try again!').grid(row=0)
                login_tryagain = tk.Button(root, text = 'Try again', command = tryagain).grid(row=1)
        except ConnectionRefusedError:  #servers down
            wd()
            noserver_label = tk.Label(root, text = 'Servers are unreachable, please try again later!').grid(row=0)
            noserver_button = tk.Button(root, text= 'Try again', command=tryagain).grid(row=1)

    def tryagain(event=None):
        wd()
        signup_button = tk.Button(text='Sign Up', width=30, command=signup)
        signup_button.place(relx=0.5, rely=0.47, anchor='center')
        login_button = tk.Button(text='Log In', width=30, command=login)
        login_button.place(relx=0.5, rely=0.53, anchor='center')

    root.title('Login / Signup')
    root.geometry("400x500")


    signup_button = tk.Button(text='Sign Up', width=30, command=signup)
    signup_button.place(relx=0.5, rely=0.47, anchor='center')

    login_button = tk.Button(text='Log In', width=30, command=login)
    login_button.place(relx=0.5, rely=0.53, anchor='center')


    root.mainloop()

    ##################################################################################

    #MAKING FILES AND FOLDERS FOR NEW USER
    lista = os.listdir()
    if username not in lista:
        os.system("mkdir " + username)

    lista = os.listdir(username)
    if "chats" not in lista:
        os.system("mkdir " + username + "\\" + "chats")
    if "aihistory.txt" not in lista:
        open(username + "//" + "aihistory.txt", "w")
    if "api_key.txt" not in lista:
        open(username + "//" + "api_key.txt", "w")
    if "memory.txt" not in lista:
        open(username + "//" + "memory.txt", "w")


    #AI

    api = open(username + "//" + "api_key.txt").read()
    if api == "":

        def getapi(event=None):
            open(username + "//" + "api_key.txt", "w").write(api_entry.get())
            wd()
            root.quit()

        api_label = tk.Label(root, text = 'Get an api key to use ai features here: https://aistudio.google.com/apikey   To continue without ai features write nothing', font =('arial', 10, 'bold')).grid(row=0, column=0)
        api_entry = tk.Entry(root, font=('arial', 10, 'normal'))
        api_entry.grid(row=1, column=0)
        tk.Button(root, text= 'Continue', command=getapi).grid(row=2)

        root.mainloop()
        api = open(username + "//" + "api_key.txt").read()



    if api == "":
        print("Continuing without ai features")
    else:
        try:
            client = genai.Client(api_key=api)
            google_search_tool = Tool(google_search = GoogleSearch())
            model_id = "gemini-2.5-flash"
            response = client.models.generate_content(
                model=model_id,
                contents="Hi",
                config=GenerateContentConfig(
                    tools=[google_search_tool]
                )
            )
            print("Ai feautres available")
        except:
            print("Continuing without ai features")




    ##############################################################################################
    #CHAT SELECTION
    time.sleep(1)

    while True:

        root.title("Select chat")

        mes = username+"//update"
        s = socket.socket()
        s.connect((sendurl, sendport))
        s.send(mes.encode("utf-8"))
        mes = s.recv(1024).decode("utf-8").split(".txt")
        s.close()

        recivers = []
        for i in mes:
            if i != "":
                recivers.append(i.replace(username, ""))

        #if recivers[0] != "No chats found.":

        def chatselect(person):
            global reciver, recivers
            reciver = recivers[person]
            wd()
            root.quit()
                
        index = 1
        for reciver in recivers:
            mes = username + "//" + reciver
            s = socket.socket()
            s.connect((sendurl, sendport))
            s.send(mes.encode("utf-8"))
            time.sleep(0.2)
            chat = s.recv(20000000).decode("utf-8")
            s.close()
            btn = tk.Button(root, text=reciver, width=15,
                        command=lambda n=index-1: chatselect(n))
            btn.grid(row=index-1, column=0)
            try:
                if open(username + "//" + "chats//" + reciver + ".txt").read() == chat:
                    pass
                elif len(open(username + "//" + "chats//" + reciver + ".txt").read()) < len(chat):
                    tk.Label(root, text = 'NEW MESSAGE').grid(row=index-1, column=1)
                else:
                    tk.Label(root, text = "Corrupt local save, open chat to update files!").grid(row=index-1, column=1)
            except FileNotFoundError:
                tk.Label(root, text = "NEW CONTACT").grid(row=index-1, column=1)

            index += 1
                    
                
        def aireciver(event=None):
            global reciver
            reciver = "ai"
            wd()
            root.quit()
        btn = tk.Button(root, text="AI", width=15, command= aireciver)
        btn.grid(row=index, column=0)

        def newcontact2():
            global username, reciver, contact_entry, reciveurl, reciveport

            reciver = contact_entry.get()

            mes = username +"//"+ reciver +"//"+ "@newcontact@"
            s = socket.socket()
            s.connect((reciveurl, reciveport))
            s.send(mes.encode("utf-8"))
            s.close() 
            wd()
            root.quit()

        goback_newcontact = False
        def newcontact():
                global contact_entry, goback_newcontact
                goback_newcontact = True

                wd()


                contact_label = tk.Label(root, text = 'Username of new contact:', font =('arial', 10, 'bold')).grid(row=0, column=0)
                contact_entry = tk.Entry(root, font=('arial', 10, 'normal'))
                contact_entry.grid(row=1, column=0)
                tk.Button(root, text= 'Continue', command=newcontact2).grid(row=2)


        btn = tk.Button(root, text="New contact", width=15, command= newcontact)
        btn.grid(row=index+2, column=0)
        
        back_button = tk.Button(root, text="Back", command=back)
        back_button.place(relx=1.0, x=-5, y=5, anchor="ne")   
        root.mainloop()
        if goback_newcontact:
            continue
        if goback:
            goback = False
            break

        ##############################################################################################
        if reciver == "ai":
            def redraw_chat_ai(chatlist):
                global username, msg_frame, canvas
                # clear old messages
                for widget in msg_frame.winfo_children():
                    widget.destroy()
                
                for i in chatlist:
                    try:
                        if "User" in i:
                            label = tk.Label(msg_frame, text=i.replace("\n", "").split("User: ")[1], bg="#DCF8C6",
                                            anchor="e", justify="right", wraplength=250)
                            label.pack(anchor="e", pady=2, padx=5)
                        else:
                            label = tk.Label(msg_frame, text=i.replace("\n", "").split("Ai: ")[1], bg="#FFFFFF",
                                            anchor="w", justify="left", wraplength=250)
                            label.pack(anchor="w", fill="x", padx=5, pady=2)
                    except IndexError: #when i is not a message
                        pass

                canvas.update_idletasks()
                canvas.yview_moveto(1.0)
            def send_ai(event=None):
                global entry
                mes = entry.get()
                entry.delete(0, tk.END)
                aihistory = client.files.upload(file=username + "//" + "aihistory.txt")
                history = client.files.upload(file=username + "//" + "memory.txt")
                response = client.models.generate_content(
                    model=model_id,
                    contents=[history, aihistory, mes],
                    config=GenerateContentConfig(
                        tools=[google_search_tool]
                    )
                )
                open(username + "//" + "aihistory.txt", "a", encoding="utf-8").write("\nUser: " + mes + "\nAi: " + response.text.replace("*", "")) 
                redraw_chat_ai(open(username + "//" + "aihistory.txt").readlines())

           
            
            # --- GUI setup ---

            for widget in root.winfo_children():
                widget.destroy()
            
            chat_frame = tk.Frame(root)
            chat_frame.pack(fill="both", expand=True)
                    
            canvas = tk.Canvas(chat_frame)
            canvas.pack(side="left", fill="both", expand=True)
                    
            scrollbar = tk.Scrollbar(chat_frame, command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)
                        
            msg_frame = tk.Frame(canvas)
            canvas_window = canvas.create_window((0,0), window=msg_frame, anchor="nw")
                    
            def update_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            msg_frame.bind("<Configure>", update_scroll_region)
                            
            def resize_frame(event):
                canvas.itemconfig(canvas_window, width=event.width)
            canvas.bind("<Configure>", resize_frame)

            # -------- Mouse wheel bindings (cross-platform) --------
            def _on_mousewheel(event):
                # Windows / most Linux: event.delta is a multiple of 120
                # macOS: event.delta is small (±1, ±2, …)
                if sys.platform == "darwin":
                    canvas.yview_scroll(-1 * int(event.delta), "units")
                else:
                    canvas.yview_scroll(-1 * int(event.delta / 120), "units")

            # X11 fallback (older Linux sends Button-4/5 instead of <MouseWheel>)
            def _on_mousewheel_up(event):
                canvas.yview_scroll(-1, "units")

            def _on_mousewheel_down(event):
                canvas.yview_scroll(1, "units")

            # Only scroll when pointer is over the canvas:
            def _bind_wheel(_):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
                canvas.bind_all("<Button-4>", _on_mousewheel_up)   # X11
                canvas.bind_all("<Button-5>", _on_mousewheel_down) # X11

            def _unbind_wheel(_):
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

            canvas.bind("<Enter>", _bind_wheel)
            canvas.bind("<Leave>", _unbind_wheel)

            
            # --- Input area ---
            input_frame = tk.Frame(root)
            input_frame.pack(fill="x")
                        
            entry = tk.Entry(input_frame, font=("Arial",12))
            entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
                    
            send_btn = tk.Button(input_frame, text="Send")
            send_btn.pack(side="right", padx=5, pady=5)
                        
            send_btn.config(command=send_ai)
            entry.bind("<Return>", send_ai)


            back_button = tk.Button(root, text="Back", command=back)
            back_button.place(relx=1.0, x=-5, y=5, anchor="ne")  

            redraw_chat_ai(open(username + "//" + "aihistory.txt").readlines()) 

            root.mainloop()
            if goback:
                goback = False
                continue
                
        else:
            #SETTINGS

            ai = ""
            try:
                settings = json.loads(open("settings.json").read())
            except FileNotFoundError:
                settings = {"translate": False, "autocorrect": False, "language": "English", "formal": False}
                open("settings.json", "w").write(json.dumps(settings))

            firsttranslate = False
            def translate(event=None):
                global language, firsttranslate
                def langselect():
                    global firsttranslate
                    language = password_entry_reg.get()
                    settings["language"] = language
                    settings["translate"] = tktranslate.get()
                    open("settings.json", "w").write(json.dumps(settings))
                    firsttranslate = True

                    root2.destroy()
                global restart
                if not tktranslate.get():
                    settings["translate"] = tktranslate.get()
                    open("settings.json", "w").write(json.dumps(settings))
                    firsttranslate = True

                if tktranslate.get():
                    root2 = tk.Tk()
                    root2.title('Language select')
                    root2.geometry("400x100")

                    password_label_reg = tk.Label(root2, text = 'Translate to', font =('arial', 10, 'bold')).grid(row=1, column=0)
                    password_entry_reg = tk.Entry(root2, font=('arial', 10, 'normal'))
                    password_entry_reg.grid(row=1, column=1)

                    continue_button_reg = tk.Button(root2, text= 'Continue', command=langselect).grid(row=2)
                

            def autocorrect(event=None):
                settings["autocorrect"] = tkautocorrect.get()
                open("settings.json", "w").write(json.dumps(settings))

            def formal(event=None):
                settings["formal"] = tkformal.get()
                open("settings.json", "w").write(json.dumps(settings))

            def memory():
                if os.name == "nt":
                    os.system(f"start {username}//memory.txt")
                else:
                    os.system(f"xdg-open {username}//memory.txt")

            def remember():
                global chat
                chat = chat.split("-->")
                if len(chat) > 30:
                    chat = chat[-30:]
                for i in chat:
                    open(username + "//" + "memory.txt", "a").write(i)
                messageVar = tk.Message(root, text="chat saved to AI memory")
                messageVar.config(bg='lightgreen')
                messageVar.pack()
                messageVar.after(2000, messageVar.destroy)

            responses = None
            def answer2(event=None):
                global answers, responses
                mes = username +"//"+ reciver +"//"+ responses[answers.current()]
                s = socket.socket()
                s.connect((reciveurl, reciveport))
                s.send(mes.encode("utf-8"))
                s.close()
                answers.destroy()

            def answer(event=None):
                global chat, reciveurl, reciveport, responses, answers
                chat = chat.split("\n")
                if len(chat) > 9:
                    chat = chat[10:]
                response = client.models.generate_content(
                    model=model_id,
                    contents=[str(chat), "Give multiple type of answers. positive negative and everything, recommend 5 answer options based on the conversation, and after that you can see how the user wants to respond, form your answers accordingly, number the options, dont say anything else just the 5 options under each other"],
                    config=GenerateContentConfig(
                        tools=[google_search_tool]
                    )
                )


                index = 1
                responses = []
                for i in response.text.split("\n"):
                    if i.startswith(str(index)):
                        responses.append(i.replace(str(index)+". ", ""))
                        index+=1
                #choose from menu
                answers = ttk.Combobox(root, width = 50)
                answers["values"] = tuple(responses)
                answers.pack()
                answers.bind("<<ComboboxSelected>>", answer2)

            def summarize(event=None):
                response = client.models.generate_content(
                model=model_id,
                contents=[str(chat), "write a short summary of this conversation, only summarize the most recent topic of the conversation, keep your answer short. Your response will only contain the summary and nothing else."],
                config=GenerateContentConfig(tools=[google_search_tool])
                )
                messageVar = tk.Message(root, text=response.text)
                messageVar.config(bg='lightgreen')
                messageVar.pack()
                messageVar.after(4000, messageVar.destroy)

            # --- GUI setup ---
                
            for widget in root.winfo_children():
                widget.destroy()
                    
            chat_frame = tk.Frame(root)
            chat_frame.pack(fill="both", expand=True)
                    
            canvas = tk.Canvas(chat_frame)
            canvas.pack(side="left", fill="both", expand=True)
                    
            scrollbar = tk.Scrollbar(chat_frame, command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)
                        
            msg_frame = tk.Frame(canvas)
            canvas_window = canvas.create_window((0,0), window=msg_frame, anchor="nw")
                    
            def update_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            msg_frame.bind("<Configure>", update_scroll_region)
                            
            def resize_frame(event):
                canvas.itemconfig(canvas_window, width=event.width)
            canvas.bind("<Configure>", resize_frame)

            # -------- Mouse wheel bindings (cross-platform) --------
            def _on_mousewheel(event):
                # Windows / most Linux: event.delta is a multiple of 120
                # macOS: event.delta is small (±1, ±2, …)
                if sys.platform == "darwin":
                    canvas.yview_scroll(-1 * int(event.delta), "units")
                else:
                    canvas.yview_scroll(-1 * int(event.delta / 120), "units")

            # X11 fallback (older Linux sends Button-4/5 instead of <MouseWheel>)
            def _on_mousewheel_up(event):
                canvas.yview_scroll(-1, "units")

            def _on_mousewheel_down(event):
                canvas.yview_scroll(1, "units")

            # Only scroll when pointer is over the canvas:
            def _bind_wheel(_):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
                canvas.bind_all("<Button-4>", _on_mousewheel_up)   # X11
                canvas.bind_all("<Button-5>", _on_mousewheel_down) # X11

            def _unbind_wheel(_):
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")

            canvas.bind("<Enter>", _bind_wheel)
            canvas.bind("<Leave>", _unbind_wheel)

                                            
            #MENU
            menu = tk.Menu(root)
            root.config(menu=menu)

            filemenu = tk.Menu(menu, tearoff=0)
            menu.add_cascade(label='File', menu=filemenu)

            filemenu.add_command(label="AI memory", command=memory)


            aimenu = tk.Menu(menu, tearoff=0)
            menu.add_cascade(label='AI', menu=aimenu)

            aimenu.add_command(label="Remember", command=remember)
            aimenu.add_command(label="Answer", command=answer)
            aimenu.add_command(label="Summary", command=summarize)

                        
            optionsmenu = tk.Menu(menu, tearoff=0)
            menu.add_cascade(label='Options', menu=optionsmenu)
                    
            language = settings["language"]
            tktranslate = tk.BooleanVar(value=settings["translate"])
            optionsmenu.add_checkbutton(label='Translate', variable=tktranslate, onvalue=True, offvalue=False, command=translate)
                    
                                
            tkautocorrect = tk.BooleanVar(value=settings["autocorrect"])
            tkformal = tk.BooleanVar(value=settings["formal"])
            optionsmenu.add_checkbutton(label='Auto-Correct', variable=tkautocorrect, onvalue=True, offvalue=False, command=autocorrect)
            optionsmenu.add_checkbutton(label='Formal', variable=tkformal, onvalue=True, offvalue=False, command=formal)
                    
                                                        
            # --- Input area ---
            input_frame = tk.Frame(root)
            input_frame.pack(fill="x")
                        
            entry = tk.Entry(input_frame, font=("Arial",12))
            entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
                    
            send_btn = tk.Button(input_frame, text="Send")
            send_btn.pack(side="right", padx=5, pady=5)
                        
            send_btn.config(command=send)
            entry.bind("<Return>", send)

            root.title(reciver)


            t2 = threading.Thread(target=recive)
            t2.start()

            back_button = tk.Button(root, text="Back", command=back)
            back_button.place(relx=1.0, x=-5, y=5, anchor="ne")   
            root.mainloop()
            if goback:
                goback = False
                continue