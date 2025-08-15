# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random as rn


x=''
y=''



def load_image(path):
    img = Image.open(path)
    img = img.resize((1024, 568), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

window = tk.Tk()
window.title("Love Calculator ❤ mk-2")
window.geometry("1024x568")
window.resizable(False, False)



    




image_paths = ["1600w-zwtpUKFUbW.png", "1600w-zwtpUKFUbWs.png"]  
images = [load_image(path) for path in image_paths]
current_index = [0]

canvas = tk.Canvas(window, width=1024, height=568, highlightthickness=0)
canvas.pack(fill="both", expand=True)


bg_canvas_image = canvas.create_image(0, 0, image=images[0], anchor="nw")


def toggle_image():
    current_index[0] = 1 - current_index[0]
    canvas.itemconfig(bg_canvas_image, image=images[current_index[0]])


def change_language(event=None):
    global current_lang
    current_lang = lang_box.get()
    update_ui_language()


title_text_shadow = canvas.create_text(514, 42, text="Love Calculator ❤ mk-II",
                                       font=("Noto Sans HK", 42, "bold"),
                                       fill="#000000", anchor="center")

title_text = canvas.create_text(512, 40, text="Love Calculator ❤ mk-II",
                                font=("Noto Sans HK", 42, "bold"),
                                fill="#FF00D0", anchor="center")

name1_label_shadow = canvas.create_text(513, 100, text="Name 1",
                                        font=("OCR A Extended", 19),
                                        fill="#FFFFFF", anchor="center")

name1_label = canvas.create_text(512, 102, text="Name 1",
                                 font=("OCR A Extended", 19),
                                 fill="#000000", anchor="center")

name2_label_shadow = canvas.create_text(512, 180, text="Name 2",
                                        font=("OCR A Extended", 19),
                                        fill="#ffffff", anchor="center")

name2_label = canvas.create_text(514, 182, text="Name 2",
                                 font=("OCR A Extended", 19),
                                 fill="#000000", anchor="center")

name1 = tk.Entry(window, font=("High Tower Text", 18), width=22, justify="center",
                 bg="white", fg="black", bd=2, relief="groove", highlightbackground="#ff69b4", highlightcolor="#ff69b4", highlightthickness=1)


name2 = tk.Entry(window, font=("High Tower Text", 18), width=22, justify="center",
                 bg="white", fg="black", bd=2, relief="groove", highlightbackground="#ff69b4", highlightcolor="#ff69b4", highlightthickness=1)


canvas.create_window(512, 135, window=name1, anchor="center")


canvas.create_window(512, 215, window=name2, anchor="center")


ameii = tk.Label(window, text="", font=("Times New Roman", 18), fg="#000000",
                 bg="#fdf1f6", padx=20, pady=10, wraplength=800, bd=2, relief="flat")


canvas.create_window(512, 300, window=ameii, anchor="center")
LANGUAGES = {
    "English": {
        "title": "Love Calculator ❤ mk-2",
        "name1": "Name 1",
        "name2": "Name 2",
        "empty_both": "Air with air? B.K.L",
        "empty_y": "Single? me too T_T",
        "empty_x": "Your name?",
        "calc": "Calculating love 💘",
        "kundli": "Looking at kundli",
        "done": "Done!",
        "result": "The love ❤ between {x} and {y} is {a}%",
        "txt":"Wait a bit, be patient🙏",
        "100":"—are 4 floors enough?",
        "80":"—ts pisses me off, idk why",
        "77":" — Thala for a reason ❤❤",
        "60":f"— did wet",
        "40":f" — You'll always be my nigga❤❤, {y} ~ {x}",
        "20":" — 💔 sybau🥀",
        "7":"— Thala for a reason",
        "0":"— Leave hope bro",
        "<0":"— Even RCB have a trophy now",
        "check":"Check",
        "reset":"Reset"
        
        
    },

  "कुमाऊनी ": {
        "title": "प्रेम गणक mk -2",
        "name1": "नाम 1",
        "name2": "नाम 2",
        "empty_both": "हवै को हवै बटि मिलौं B.K.L",
        "empty_y": "अक्यळ छ? मै लै T_T",
        "empty_x": "त्यर नाम?",
        "calc": "प्रेमै कै गिणनु 💘",
        "kundli": "कुण्डली द्येखणु",
        "done": "हैगौ!",
        "result": "{x} आ {y} कै बीच प्रेम {a}% छै",
        "txt":"रुक, मड़ीं द्येर🙏",
        "100":"—४ मजिल काफ् छै क्ये?",
        "80":"—चिंज्ञान है जूळ मैं",
        "77":" — थाला फॉर अ रीजन ❤❤",
        "60":f"— गिळ् हैगे आँह",
        "40":f" — म्यर निगर छै तू❤❤, {y} ~ {x}",
        "20":" — 💔 सिबौ लै🥀",
        "7":"— थाला फॉर अ रीजन",
        "0":"— भिड़े बाटि कुद जा",
        "<0":"— अब तो RCB कै पास लै ट्रफी छै ",
        "check":"बतौं",
        "reset":"पहिलु जैस कर "
        
        
    },
    
    "हिंदी": {
        "title": "प्रेम गणक ❤ mk-2",
        "name1": "नाम 1",
        "name2": "नाम 2",
        "empty_both": "हवा से हवा मिलाऊँ? बी.के.एल",
        "empty_y": "सिंगल? मैं भी T_T",
        "empty_x": "तेरा नाम?",
        "calc": "प्रेम की गणना हो रही है 💘",
        "kundli": "कुंडली देख रहे हैं",
        "done": "पूरा हो गया!",
        "result": "{x} और {y} के बीच प्यार ❤ {a}% है",
        "txt":"रुको जरा सबर करो🙏",
        "100":"—क्या 4 मंज़िलें काफ़ी हैं?",
            "80":"—ये मुझे गुस्सा दिलाती है, पता नहीं क्यों",
        "77":" — थाला किसी वजह से ❤❤",
        "60":f"—  गीला है",
            "40":f" — तुम हमेशा मेरे निग्गा रहोगे❤❤, {y} ~ {x}",
"20":" — 💔 sybau🥀",
"7":"—  थाला किसी वजह से",
"0":"— उम्मीद छोड़ दो भाई",
"<0":"— अब तो RCB के पास भी ट्रॉफी है",
        "check":"जाँचें",
"reset":"पुनः स्तापित "},
    
   
    
    "सम्सकृतम्":{
        "title": "प्रेम गणक ❤ mk-2",
        "name1": "नामः १" ,
        "name2":"नामः ‌२",
        "empty_both":"किं मया वायुः मिलितव्यम् ?B.K.L",
        "empty_y":"एकलः, अहमपि..T_T",
        "empty_x":"तव नाम्ना किं? ",
        "calc":"प्रेम 💘 गणना करते हुए",
        "done":"समाप्ति !",
         "kundli": "कुण्डलीम् अवलोकयन्",
        "result":"{x} तथा {y} मध्ये प्रेम ❤ {a}%",
        "txt":"किञ्चित् प्रतीक्ष्यताम्, धैर्यं धारयतु",
        "100":"—४ तलाः पर्याप्ताः सन्ति वा?", 
"80":"—ts मां क्रोधयति, idk किमर्थं", 
"77":" — थला कारणात् ❤❤", 
"60":f"— {y} आर्द्रः अस्ति", 
"40":f" — त्वं मम निग्गा❤❤, {y} ~ {x}", 
"20":" — 💔 sybau🥀", 
"7":"— थला कारणात्", 
"0":"— आशां त्यजतु भ्राता", 
"<0":"— आरसीबी अपि इदानीं ट्राफी अस्ति",
        "check":"परीक्षण", 
"reset":"पुनर्स्थापनम्"},
    "ਪੰਜਾਬੀ": {
"title": "ਲਵ ਕੈਲਕੂਲੇਟਰ ❤ mk-2",
"name1": "ਨਾਮ 1",
"name2": "ਨਾਮ 2",
"empty_both": "ਹਵਾ ਨਾਲ ਹਵਾ? B.K.L",
"empty_y": "ਇਕੱਲਾ? ਮੈਂ ਵੀ T_T",
"empty_x": "ਤੁਹਾਡਾ ਨਾਮ?",
"calc": "ਪਿਆਰ ਦੀ ਗਣਨਾ ਕਰ ਰਿਹਾ ਹਾਂ 💘",
"kundli": "ਕੁੰਡਲੀ ਨੂੰ ਦੇਖ ਰਿਹਾ ਹਾਂ",
"done": "Done!",
"result": "{x} ਅਤੇ {y} ਵਿਚਕਾਰ ਪਿਆਰ ❤ {a}% ਹੈ",
"txt":"ਥੋੜਾ ਇੰਤਜ਼ਾਰ ਕਰੋ, ਸਬਰ ਰੱਖੋ🙏",
"100":"—ਕੀ 4 ਮੰਜ਼ਿਲਾਂ ਕਾਫ਼ੀ ਹਨ?",
"80":"—ts ਮੈਨੂੰ ਪਰੇਸ਼ਾਨ ਕਰਦਾ ਹੈ, ਪਤਾ ਨਹੀਂ ਕਿਉਂ",
"77":" — ਥਾਲਾ ਕਿਸੇ ਕਾਰਨ ਕਰਕੇ ❤❤",
"60":f"—ਗਿੱਲਾ ਹੋਇਆ",
"40":f" — ਤੂੰ ਹਮੇਸ਼ਾ ਮੇਰਾ ਨਿੱਗਾ ਰਹੇਂਗਾ❤❤, {y} ~ {x}",
"20":" — 💔 sybau🥀",
"7":"— ਇੱਕ ਕਾਰਨ ਕਰਕੇ ਥਾਲਾ",
"0":"— ਉਮੀਦ ਛੱਡੋ ਭਰਾ",
"<0":"— ਹੁਣ ਆਰਸੀਬੀ ਕੋਲ ਵੀ ਟਰਾਫੀ ਹੈ",
"check":"ਚੈੱਕ",
"reset":"ਰੀਸੈੱਟ"},
    
  "தமிழ்": {
"title": "காதல் கால்குலேட்டர் ❤ mk-2",
"name1": "பெயர் 1",
"name2": "பெயர் 2",
"empty_both": "காற்றுடன் காற்று? B.K.L",
"empty_y": "தனியா? நானும் T_T",
"empty_x": "உங்கள் பெயர்?",
"calc": "காதலைக் கணக்கிடுகிறது 💘",
"kundli": "குண்ட்லியைப் பார்க்கிறேன்",
"done": "முடிந்தது!",
"result": "{x}க்கும் {y}க்கும் இடையிலான காதல் ❤ {a}%",
"txt":"கொஞ்சம் காத்திருங்கள், பொறுமையாக இருங்கள்🙏",
"100":"—4 தளங்கள் போதுமா?",
"80":"—அது என்னை எரிச்சலூட்டுகிறது, ஏன் என்று தெரியவில்லை",
"77":" — ஒரு காரணத்திற்காக தல ❤❤",
"60":f"— {y} ஈரமாக இருக்கிறது",
"40":f" — நீங்கள் எப்போதும் இருப்பீர்கள் என் நிக்கா❤❤, {y} ~ {x}",
"20":" — 💔 சைபா🥀",
"7":"— ஒரு காரணத்திற்காக தல",
"0":"— நம்பிக்கையை விடுங்கள் சகோ",
"<0":"— ஆர்சிபி கூட இப்போது ஒரு கோப்பையைக் கொண்டுள்ளது",
"check":"சரிபார்",
"reset":"மீட்டமை"},


"Deutsch": {
"title": "Liebesrechner ❤ mk-2",
"name1": "Name 1",
"name2": "Name 2",
"empty_both": "Luft mit Luft? B.K.L",
"empty_y": "Single? Ich auch T_T",
"empty_x": "Dein Name?",
"calc": "Liebe wird berechnet 💘",
"kundli": "Kundli ansehen",
"done": "Fertig!",
"result": "Die Liebe ❤ zwischen {x} und {y} beträgt {a}%",
"txt": "Warte kurz, hab Geduld 🙏",
"100": "—Reicht das 4 Stockwerke?",
"80": "—Das kotzt mich an, ich weiß nicht warum",
"77": "—Thala aus gutem Grund",
"60": "—Hat nass gemacht",
"40": "—Du wirst immer mein Nigga❤❤, {y} ~ {x}",
"20":" — 💔 sybau🥀",
"7":"— Thala aus gutem Grund",
"0":"— Hör auf zu hoffen, Bruder",
"<0":"— Sogar RCB hat jetzt eine Trophäe",
"check":"Check",
"reset":"Zurücksetzen"
},
    "Latinum": {
"title": "Calculator Amoris ❤ mk-2",
"name1": "Nomen 1",
"name2": "Nomen 2",
"empty_both": "Aer cum aere? B.K.L",
"empty_y": "Solus? Ego quoque T_T",
"empty_x": "Nomen tuum?",
"calc": "Calculans amorem 💘",
"kundli": "Kundli spectans",
"done": "Factum!",
"result": "Amor ❤ inter {x} et {y} est {a}%",
"txt":"Exspecta paulisper, patientia esto🙏",
"100":"—satisne sunt quattuor tabulata?",
"80":"—ts me vexat, nescio cur",
"77":"—Thala sine causa",
"60":f"—madefecit",
"40":f" — Semper eris meus nigger❤❤, {y} ~ {x}",
"20":" — 💔 sybau🥀",
"7":"— Thala causa",
"0":"— Spem relinque, frater",
"<0":"— Etiam RCB nunc tropaeum habet",
"check":"Check",
"reset":"Repone"},

"Русский": {
"title": "Калькулятор любви ❤ mk-2",
"name1": "Имя 1",
"name2": "Имя 2",
"empty_both": "Воздух с воздухом? B.K.L",
"empty_y": "Холост? Я тоже T_T",
"empty_x": "Твоё имя?",
"calc": "Рассчитываю любовь 💘",
"kundli": "Гляжу на kundli",
"done": "Готово!",
"result": "Любовь ❤ между {x} и {y} составляет {a}%",
"txt":"Подожди немного, потерпи🙏",
"100":"—4 этажа достаточно?",
"80":"—ts меня бесит, не знаю почему",
"77":"—Thala не просто так",
"60":f"—обмочился",
"40":f" — Ты всегда будешь моим ниггером❤❤, {y} ~ {x}",
"20":" — 💔 sybau🥀",
"7":"— Тала не просто так",
"0":"— Оставь надежду, бро",
"<0":"— Даже у RCB теперь есть трофей",
"check":"Проверить",
"reset":"Сбросить"},

     "日本語": {
        "title": "ラブ計算機 ❤ mk-2",
        "name1": "名前1",
        "name2": "名前2",
        "empty_both": "空気と空気？B.K.L",
        "empty_y": "シングル？私も T_T",
        "empty_x": "君の名は？",
        "calc": "愛を計算中 💘",
        "kundli": "運命を見てます",
        "done": "完了!",
        "result": "{x} と {y} の愛 ❤ {a}%",
        "txt":"少し待って、辛抱してください",
        "100":"—4階建てで十分？",
"80":"—TSがムカつく、理由はわからないけど",
"77":"—Thalaには理由がある ❤❤",
"60":f"— {y}は濡れてる",
"40":f"—お前はいつまでも俺のニガー❤❤、{y} ~ {x}",
"20":"— 💔 sybau🥀",
"7":"— Thalaには理由がある",
"0":"— 希望を捨てろよ兄弟",
"<0":"— RCBだって今ならトロフィー持ってるぞ",
        "check":"チェック",
"reset":"リセット"
        },
    "中国人": {
"title": "爱情计算器❤ mk-2",
"name1": "姓名1",
"name2": "姓名2",
"empty_both": "空气和空气？B.K.L",
"empty_y": "单身？我也是T_T",
"empty_x": "你的名字？",
"calc": "正在计算爱情💘",
"kundli": "正在看kundli",
"done": "完成！",
"result": "{x} 和 {y} 之间的爱情❤是{a}%",
"txt":"稍等，耐心点🙏",
"100":"—4层楼够吗？",
"80":"—ts让我很生气，不知道为什么",
"77":"—Thala是有原因的",
"60":f"—did wet",
"40":f"—你永远是我的黑鬼❤❤，{y} ~ {x}",
"20":" — 💔 sybau🥀",
"7":"— Thala 是有原因的",
"0":"— 兄弟，留下希望吧",
"<0":"— 现在连 RCB 都有奖杯了",
"check":"检查",
"reset":"重置"},

"한국인": {
"title": "사랑 계산기 ❤ mk-2",
"name1": "이름 1",
"name2": "이름 2",
"empty_both": "공기랑 공기? B.K.L",
"empty_y": "싱글? 나도 T_T",
"empty_x": "이름이 뭐야?",
"calc": "사랑 계산 💘",
"kundli": "쿤들리 보고 있어",
"done": "끝났어!",
"result": "{x}와 {y}의 사랑 ❤은 {a}%야",
"txt": "잠깐만, 조금만 기다려",
"100":"—4층짜리면 충분해?",
"80":"—이거 진짜 짜증 나, 왜 그런지 모르겠어",
"77":"—탈라가 있는 데는 이유가 있어",
"60":f"—젖었어",
"40":f"—넌 언제나 내 친구❤❤, {y} ~ {x}",
"20":"—💔 sybau🥀",
"7":"— 탈라가 된 데에는 이유가 있어",
"0":"— 희망을 버려, 형",
"<0":"— 이제 RCB도 트로피를 가지고 있어",
"check":"확인",
"reset":"재설정"}



    }
current_lang = "English"  
lang = LANGUAGES[current_lang] 

def culculate():
    global x, y
    x = name1.get().strip()
    y = name2.get().strip()
    lang = LANGUAGES[current_lang] 
    # Empty input checks
    if not x and not y:
        ameii.config(text=lang["empty_both"])
        return
    elif not y:
        ameii.config(text=lang["empty_y"])
        return
    elif not x:
        ameii.config(text=lang["empty_x"])
        return

    # Start animation
    ameii.config(text=lang["calc"])
    progress['value'] = 0

    def animate_progress(i=0):
        if i * 0.1 < 100:  # run until progress bar fills
            progress['value'] = i * 0.1
            window.after(5, animate_progress, i + 1)

            # Animation text updates
            if i * 0.1 <= 10:
                ameii.config(text=lang["calc"] + ".")
            elif i * 0.1 <= 15:
                ameii.config(text=lang["calc"] + "..")
            elif i * 0.1 <= 20:
                ameii.config(text=lang["calc"] + "...")
            elif i * 0.1 <= 25:
                ameii.config(text=lang["calc"] + "....")
            elif i * 0.1 <= 35:
                ameii.config(text=lang["kundli"])
            elif i * 0.1 <= 70:
                ameii.config(text=lang["txt"])
            elif i * 0.1 == 98:
                ameii.config(text=lang["done"])
        else:
            # Progress complete → show result
            a = rn.randint(0, 100)
            b = lang["result"].format(x=x, y=y, a=a)

            # Extra remarks
            if a == 100:
                b += lang["100"].format(x=x, y=y, a=a)
            
            elif a > 80:
                b += lang["80"].format(x=x, y=y, a=a)
            elif a == 77:
                b += lang["77"].format(x=x, y=y, a=a)
            elif a > 60:
                b += lang["60"].format(x=x, y=y, a=a)
            elif a > 40:
                b += lang["40"].format(x=x, y=y, a=a)
            elif a > 20:
                b += lang["20"].format(x=x, y=y, a=a)
                toggle_image()
            elif a == 7:
                b += lang["7"].format(x=x, y=y, a=a)
                toggle_image()
            elif 0 < a < 20:
                b += lang["0"].format(x=x, y=y, a=a)
                toggle_image()
            elif a == 0:
                b += lang["<0"].format(x=x, y=y, a=a)
                toggle_image()

            ameii.config(text=b)

    animate_progress()





def clear_names():
    name1.delete(0, tk.END)
    name2.delete(0, tk.END)
    ameii.config(text="")  
    progress['value'] = 0
    current_index[0] = 0 
    canvas.itemconfig(bg_canvas_image, image=images[0])





    


progress = ttk.Progressbar(window, style="TProgressbar", orient="horizontal", length=300, mode="determinate")
progress.place(x=360,y=400)

style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar",
                troughcolor='#ffe6f0',     
                background='#FF69B4',      
                thickness=20,
                bordercolor="#990094",
                lightcolor="#FFC2ED",
                darkcolor="#FF04BC")







btn = tk.Button(window, text=LANGUAGES[current_lang]["check"], command=culculate,
                font=("Times New Roman", 16),
                bg="#ff729d", fg="white", activebackground="#ff00dd", 
                activeforeground="white", bd=0, relief="flat", cursor="hand2")


btn2 = tk.Button(window, text=LANGUAGES[current_lang]["reset"], command=clear_names,
                 font=("Times New Roman", 16),
                 bg="#ff729d", fg="white", activebackground="#ff00dd", 
                 activeforeground="white", bd=0, relief="flat", cursor="hand2")


btn.place(relx=0.5, y=440, anchor="center")
btn2.place(relx=0.5, y=500, anchor="center")



def update_ui_language():
    lang = LANGUAGES[current_lang]
    window.title(lang["title"])
    canvas.itemconfig(title_text, text=lang["title"])
    canvas.itemconfig(title_text_shadow, text=lang["title"])
    canvas.itemconfig(name1_label_shadow, text=lang["name1"])
    canvas.itemconfig(name1_label, text=lang["name1"])
    canvas.itemconfig(name2_label_shadow, text=lang["name2"])
    canvas.itemconfig(name2_label, text=lang["name2"])
    btn.config(text=lang["check"])
    btn2.config(text=lang["reset"])

style.theme_use('clam')  # keeps your current theme

style.configure(
    "LangBox.TCombobox",
    fieldbackground="#ff729d",   # same pink background
    background="#ff00dd",        # dropdown button background
    foreground="ff729d",          # text color
    arrowcolor="white",
    
    borderwidth=0,
    selectbackground="#ff00dd",  # highlight color when selecting
    selectforeground="white"
    
)

lang_box = ttk.Combobox(window, values=list(LANGUAGES.keys()),width=10, state="readonly",
                        font=("Kokila", 16), style="LangBox.TCombobox")
lang_box.set(current_lang)
lang_box.place(x=0, y=0)  # you can move it under Reset if you want
lang_box.bind("<<ComboboxSelected>>", change_language)

window.mainloop()
