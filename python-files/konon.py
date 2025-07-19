import tkinter as tk
from tkinter import ttk, font, messagebox
from PIL import Image, ImageTk
import webbrowser
import json
import os
import io
import requests
from pytube import YouTube

# Konfiguracja
HISTORY_FILE = "watch_history.json"
CACHE_DIR = "thumbnails"
os.makedirs(CACHE_DIR, exist_ok=True)

# PEŁNA BAZA FILMÓW (2006-2025) - ZASTĄP LINKI PRAWDZIWYMI!
films_by_year = {
    "2006": [
        {"title": "Kononowicz kandydatem na prezydenta Białegostoku", "url": "https://www.youtube.com/watch?v=dWrCx85aob0"},
        {"title": "Krzysztof Kononowicz - napadli mi na matkę", "url": "https://www.youtube.com/watch?v=RF6XGFqm_oU"},
        {"title": "Spot wyborczy Kononowicza z TV Jard", "url": "https://www.youtube.com/watch?v=KBFb_9T20RU" },
        {"title": "Krzysztof Kononowicz - wywiad dla Kuriera Porannego", "url": "https://www.youtube.com/watch?v=cfqKO3pEnvM"},
        {"title": "Krzysztof Kononowicz w Wiadomościach TVP", "url": "https://www.youtube.com/watch?v=OjeoT8NZI10"},
        {"title": "Krzysztof Kononowicz w Tok2Szok", "url": "https://www.youtube.com/watch?v=GbXsESGQRLI"},
        {"title": "Krzysztof Kononowicz pozdrawia słuchaczy radia Wawa", "url": "https://www.youtube.com/watch?v=IlmOJSAAgdo"},
        {"title": "Wizyta u Kononowicza (białostocka gimbaza)", "url": "https://www.youtube.com/watch?v=L5DZaJykXwY"}

    ],
       "2007": [
        {"title": "Krzysztof Kononowicz - wywiad dla lesznotv.pl", "url": "https://www.youtube.com/watch?v=Rf5vmOOVx-U"},
        {"title": "Kononowicz w lubelskim klubie Sema4", "url": "https://www.youtube.com/watch?v=fdo1105Q_UE"},
        {"title": "Krzysztof Kononowicz walczy z hipermarketami", "url": "https://www.youtube.com/watch?v=lfRBrmxTIs0"},
        {"title": "Kononowicz ratuje Rospudę", "url": "https://www.youtube.com/watch?v=opga1_PyXC8"},
        {"title": "Kononowicz - życzenia na Dzień Kobiet", "url": "https://www.youtube.com/watch?v=JAJXlSZMd5E"},
        {"title": "Krzysztof Kononowicz kontra Donald Tusk", "url": "https://www.youtube.com/watch?v=et68KOnAL_o"},
        {"title": "Kononowicz zgrywa VIP-a na festynie trzeciomajowym", "url": "https://www.youtube.com/watch?v=hXwUcHiF5X8"},
        {"title": "Kononowicz na marszałka sejmiku wojewódzkiego", "url": "https://www.youtube.com/watch?v=v1WFianERak"},
        {"title": "Spot wyborczy KWW Podlasie XXI wieku (2007)", "url": "https://www.youtube.com/watch?v=5zke3acTGA4"},
        {"title": "Konon w Kielcach", "url": "https://www.youtube.com/watch?v=zwPOZ1ccJJg"},
        {"title": "Kononowicz na prezydenta Kielc?", "url": "https://www.youtube.com/watch?v=6q4bQD1yKZE"},
        {"title": "Krzysztof Kononowicz w Grajewie w 2007 roku + głosowanie w komisji wyborczej", "url": "https://www.youtube.com/watch?v=gKJugBsDeU0"},
        {"title": "Krzysztof Kononowicz w komisji wyborczej + kulisy kampanii wyborczej 2007", "url": "https://www.youtube.com/watch?v=YDUjIup96zE"},
        {"title": "Kononowicz życzy na święta", "url": "https://www.youtube.com/watch?v=LmAI5sx0EwA"}
    ],
    "2008": [
        {"title": "Kononowicz do Jana Rokity", "url": "https://www.youtube.com/watch?v=0rc8R9wr_w8"},
        {"title": "Kononowicz o bitwie pod Grunwaldem", "url": "https://www.youtube.com/watch?v=P5Kf4PG4Vv0"},
        {"title": "Kononowicz w disco klubie", "url": "https://www.youtube.com/watch?v=iZhEvTJ0U4w"},
        {"title": "Kononowicz prezesem PZPN!", "url": "https://www.youtube.com/watch?v=1J3CIdEYzIQ"},
        {"title": "Kononowicz Krzysztof a ekologia (Debiut Niemieckiego)", "url": "https://www.youtube.com/watch?v=4-PvWGH-3Eg"},
        {"title": "Kononowicz po wiecu zawiedziony nieobecnością burmistrza", "url": "https://www.youtube.com/watch?v=kqHB0otZ6sU"},
        {"title": "Krzysztof Kononowicz i zatrute śledziki", "url": "https://www.youtube.com/watch?v=1xUaKgbog6w"},
        {"title": "Kononowicz Krzysztof daruje życie dla karpia", "url": "https://www.youtube.com/watch?v=8JxrFFGU0qg"}
    ],
        "2009": [
        {"title": "Nibemben ogłoszony kandydatem na europosła", "url": "https://www.youtube.com/watch?v=DF2kydr1Gyw"},
        {"title": "Konon wypowiada się w sprawie oczerniającego go artykułu w Kurierze Porannym", "url": "https://www.youtube.com/watch?v=Kro3HsLaMpU"},
        {"title": "Belweder obrzucony kamieniami i butelkami", "url": "https://www.youtube.com/watch?v=4lAHn0nIwxU"},
        {"title": "Kononowicz testuje rikszę Warszawskiej Masy Krytycznej", "url": "https://www.youtube.com/watch?v=AX31t-cq8Z0"},
        {"title": "Ksiek gościem festiwalu muzycznego Basowiszcza, na który przyjechał Lublinem", "url": "https://www.youtube.com/watch?v=jkAEZuqbDjU"},
        {"title": "Knur i Kosno ponownie w Hryniewiczach, legendarna awantura w autobusie", "url": "https://www.youtube.com/watch?v=6mKh8vjAjeE"},
        {"title": "Kononowicz na planie zdjęciowym filmu Ciacho", "url": "https://www.youtube.com/watch?v=t3C50CjdBY0"},
        {"title": "Nibemben reklamuje napój energetyczny Electro Life", "url": "https://www.youtube.com/watch?v=nt9QGJM5Ww8"},
        {"title": "Kononowicz pozdrawia Mławiaków", "url": "https://www.youtube.com/watch?v=PmSoC-dVP6E"},
        {"title": "Knur agituje politycznie w klubie Wyższy Wymiar w Katowicach", "url": "https://www.youtube.com/watch?v=qHII4Vow8Rk"},
        {"title": "napad Niemiec na Starosielce", "url": "https://www.youtube.com/watch?v=NZvPfXcc7M8"},
        {"title": "Konon składa życzenia wigilijne i zapowiada start w wyborach prezydenckich", "url": "https://www.youtube.com/watch?v=MkubFuKiJ_s"}
    ],
    "2010": [
        {"title": "Konon łamie rękę i ma ją w gipsie", "url": "https://www.youtube.com/watch?v=fXv_uyU3oXw&t=19s"},
        {"title": "Ostatni film z Nibembenem na kanale Marka Kuleszy", "url": "https://www.youtube.com/watch?v=G-PdFDgmzbQ"},
        {"title": "Knurowicz pozdrawia Juvepoland i Przemyśl", "url": "https://www.youtube.com/watch?v=IyyxM_0BRn4"},
        {"title": "Bartłomiej Kurzeja zaprasza Konona na debatę przed wyborami prezydenckimi", "url": "https://www.youtube.com/watch?v=DJa5DI49iEA"},
        {"title": "Knur składa mitomańskie kondolencje po katastrofie smoleńskiej", "url": "https://www.youtube.com/watch?v=G-996DepNNo"},
        {"title": "Kononowicz ratuje Wietnamkę w Warszawie", "url": "https://www.youtube.com/watch?v=O2QSUS0MVfA"},
        {"title": "Konon i Czeczetkowicz na uroczystościach pogrzebowych Lecha i Marii Kaczyńskich", "url": "https://www.youtube.com/watch?v=g7RFxuBzzF0"},
        {"title": "Konon zdradzony przez Marka Czarniawskiego", "url": "https://www.youtube.com/watch?v=I11ooGOWNNo"},
        {"title": "Ksiek przekazuje poparcie Jarosławowi Kaczyńskiemu", "url": "https://www.youtube.com/watch?v=8nOPfZLI6k0"},
        {"title": "Knur interweniuje w sprawie usunięcia krzyża spod Pałacu Prezydenckiego", "url": "https://www.youtube.com/watch?v=f87FsXuQlgU"},
        {"title": "Bogumił Kononowicz umieszczony w Choroszczy", "url": "https://www.youtube.com/watch?v=HnLleR9bPdc"},
        {"title": "Nibemben wygłasza exposé po zabraniu brata", "url": "https://www.youtube.com/watch?v=RYZp1P84EKo"},
        {"title": "Kononowicz płacze i modli się na kolanach", "url": "https://www.youtube.com/watch?v=PUt9GGsRuPQ"},
        {"title": "Organizatorzy zbiórki wręczają Knurowi 5859 zł, debiut Mariusza Chodora na Szkolnej", "url": "https://www.youtube.com/watch?v=NxAM6f6bHCY"},
        {"title": "Kononowicz i Czeczetkowicz składają świąteczne życzenia", "url": "https://www.youtube.com/watch?v=qBtowfany08"}
    ],
    "2011": [
        {"title": "Kononowicz wygłasza orędzie dla studentów", "url": "https://www.youtube.com/watch?v=K87ZqmCijmc"},
        {"title": "Pazerny Knur wyrywa widzom pieniądze z ręki", "url": "https://www.youtube.com/watch?v=y1peE37BJTs"},
        {"title": "Leonarda ma zostać zabrana do DPS-u", "url": "https://www.youtube.com/watch?v=4U2kG4VnMqw"},
        {"title": "Film 'W domu pana Krzysztofa Kononowicza'", "url": "https://www.youtube.com/watch?v=fM5FfFazCig"},
        {"title": "Kononowicz wyprzedaje majątek", "url": "https://www.youtube.com/watch?v=aNShWKeKn5s"},
        {"title": "Konon dziękuje Tuskowi za realizację programu 'Nie będzie niczego'", "url": "https://www.youtube.com/watch?v=ZSYLHzVKTX8"},
        {"title": "Kononowicz gościem na meczu Legii Warszawa z Wisłą Kraków", "url": "https://www.youtube.com/watch?v=wZxjO4zotFc"},
        {"title": "Ksiek wypowiada się o oprawie kibiców Korony i działaniach rządu", "url": "https://www.youtube.com/watch?v=vQ5z0-tnYPw"},
        {"title": "Niżarłak spotyka się z kibicami Jagiellonii", "url": "https://www.youtube.com/watch?v=UgLEh3T7lv4"}
    ],
    "2012": [
        {"title": "Kononowicz protestuje przeciwko ACTA", "url": "https://www.youtube.com/watch?v=PYsRotHJd4s"},
        {"title": "Konon daje wywiad Gazecie Współczesnej w związku z oskarżeniem go przez MOPR o pobicie brata", "url": "https://www.youtube.com/watch?v=BNZqR80gnYY&t=6s"},
        {"title": "MOPR nasyła na Kononowicza policję, oskarżając go o pobicie Bogumiła", "url": "https://www.youtube.com/watch?v=6K_95KgEluY"},
        {"title": "Brudny i potargany Kononowicz bredzi w szpitalu w przeddzień śmierci matki", "url": "https://www.youtube.com/watch?v=z_-8a75eBis"},
        {"title": "Film 'Tragedia Kononowicza - Ostatnie ekspoze' (ostatnie nagranie Czeczeta jako redaktora)", "url": "https://www.youtube.com/watch?v=O9oyExEZV6M"},
        {"title": "Andrzej Pochylski po donosie Knura aresztowany za próbę zamachu na Truskolaskiego", "url": "https://www.youtube.com/watch?v=4uDHvqCg4T4&t=23s"}
    ],
     "2013": [
        {"title": "Podlasie XXI wieku oskarża ośrodek w Ciechanowie o eutanazję na Bogumile i ujawnia aferę pogrzebową", "url": "https://www.youtube.com/watch?v=1m2q35Zx92o"},
        {"title": "Fani z Krakowa zapraszają prezydenta na gryla bożego", "url": "https://www.youtube.com/watch?v=g2tqazLTu8s"},
        {"title": "Kononowicz obserwuje protest Federacji Zielonych przeciwko prywatyzacji MPEC", "url": "https://www.youtube.com/watch?v=ki1cA6CJSZg&t=6s"},
        {"title": "Axelio na Woodstocku sprzedaje Miecugowowi plaskacza z opóźnionym zapłonem", "url": "https://www.youtube.com/watch?v=q1B7g16EEW8&t=29s"},
        {"title": "Kononowicz szuka Niemieckiego w Bielsku Podlaskim", "url": "https://www.youtube.com/watch?v=iLm0Mzh1ZN0"},
        {"title": "Część druga podcastu Kononowicz o rzyció z Nibembenem", "url": "https://www.youtube.com/watch?v=ZIP9oYALSNs"},
        {"title": "Emisja programu 'Puk, puk, to my!' na kanale Viva Polska", "url": "https://www.youtube.com/watch?v=lrqYdcOGiNk"},
        {"title": "Wychodzi trzeci i ostatni odcinek serii Kononowicz o rzyció", "url": "https://www.youtube.com/watch?v=A9Z27mm"}
    ],
    "2014": [
        {"title": "Kononowicz wygłasza exposé pod bramką", "url": "https://www.youtube.com/watch?v=-8rhxB8Ttm0&t=182s"},
        {"title": "Ksiek zamierza jechać z Chodorem i jego ekipą na Woodstock", "url": "https://www.youtube.com/watch?v=twA8n8SUuws"},
        {"title": "Nagranie filmu 'Kononowicz największy wróg Putina' (opublikowanego rok później)", "url": "https://www.youtube.com/watch?v=IUANvTuthDs"},
        {"title": "Kononowicz odwiedza protest rolników pod Urzędem Wojewódzkim", "url": "https://www.youtube.com/watch?v=y0Xk8YXTX7g"}
    ],
    "2015": [
        {"title": "Prawdopodobnie pierwszy film na kanale 'Kononowicz w olejku lub pomidorkach' pt. 'O Kajetanie Piechowitzu'", "url": "https://www.youtube.com/watch?v=ei340EQoHIo"},
        {"title": "Nibemben apeluje do Anny Grodzkiej", "url": "https://www.youtube.com/watch?v=9ad8vDgwR1o"},
        {"title": "Konsumpcja paprykarza", "url": "https://www.youtube.com/watch?v=xpvfDABCCZc"},
        {"title": "Jabłuszek", "url": "https://www.youtube.com/watch?v=YY7PQqnF8S0"},
        {"title": "Pierwsze rąbanie drzewka", "url": "https://www.youtube.com/watch?v=afbZ4JzaH6k"},
        {"title": "Publikacja filmu 'Jebniem po jednym, resztę walnę sam w domu' z 2014 roku", "url": "https://www.youtube.com/watch?v=JMyI3aS-wmw"},
        {"title": "Umorzany Kononowicz czyta dzieciom bajki", "url": "https://www.youtube.com/watch?v=Vy0JlsOuo0A"},
        {"title": "Debiut Majora trzymającego transparent na filmie Niemieckiego, zaczyna się żebranie o dary", "url": "https://www.youtube.com/watch?v=_Shyo5pn0Tg&t=18s"},
        {"title": "Majówka na Szkolnej", "url": "https://www.youtube.com/watch?v=bk_F9yxrw-E&t=8s"},
        {"title": "Monolog Kononowicza pt. 'Naród młody, tak, jak ja'", "url": "https://www.youtube.com/watch?v=pIJwnkgSxME"},
        {"title": "Zaginięcie Majora, Konon apeluje do niego o powrót", "url": "https://www.youtube.com/watch?v=tDz1eIHumKo&t=270s"},
        {"title": "Kononowicz ochoczo testuje konserwy rybne, mieszając je z pieczarkami i ziemniaczkami", "url": "https://www.youtube.com/watch?v=tDz1eIHumKo&t=54s"}
    ],
    "2016": [
        {"title": "Śmingus-minguś na Szkolnej, debiut Nera i Asterki Bożej", "url": "https://www.youtube.com/watch?v=ZRNLSlydzdM"},
        {"title": "Założenie przez Niemca kanału Kononowicz Orginal", "url": "https://www.youtube.com/channel/UCXf8RmFdAgpIU1kUk5xoCfg"},
        {"title": "Policjanci z trójki odbierają Knurowi pistolet gazowy", "url": "https://www.youtube.com/watch?v=3aS-zbivl7U"},
        {"title": "Knur raczy się konserwowymi sardynkami i prezentuje, jak należy odlewać z nich olej", "url": "https://www.youtube.com/watch?v=2YyLNeXhcWY&t=13s"},
        {"title": "Kononowicz wypowiada się na temat afery w stadninie koni w Janowie Podlaskim", "url": "https://www.youtube.com/watch?v=NCXCDr-B6v8&t=17s"},
        {"title": "Kononowicz odpowiada na pytanie widza o Trójkącie Bermudzkim", "url": "https://www.youtube.com/watch?v=bsiC899nkpk"},
        {"title": "Major po raz pierwszy przywdziewa radziecki mundur", "url": "https://www.youtube.com/watch?v=g-lLSdmzE5M"},
        {"title": "Lejtnant Starosiuk debiutuje na Szkolnej i recenzuje placki Kononowicza", "url": "https://www.youtube.com/watch?v=ktzUlaRP1oE"},
        {"title": "Kononowicz apeluje do Anglików, aby przestali bić i mordować Polaków", "url": "https://www.youtube.com/watch?v=Ebw_JTO5cTc&t=9s"},
        {"title": "Kononowicz komentuje mecz Polska–Szwajcaria na EURO 2016", "url": "https://www.youtube.com/watch?v=fO7gp9Y9db0"},
        {"title": "Konon obiecuje zająć się sprawą śmierci Pawła Klima i zrobić czystki w policji", "url": "https://www.youtube.com/watch?v=ZMRgVTX6pJ4"},
        {"title": "Niemiecki nagrywa pierwszą kłótnię między małżonkami", "url": "https://www.youtube.com/watch?v=cGNjF3shras"},
        {"title": "Oględziny czołgu T–34", "url": "https://www.youtube.com/watch?v=L9S-NYMC050"},
        {"title": "Exposé o Podlasianach – narodzie bandyckim i morderczym", "url": "https://www.youtube.com/watch?v=rTyHaBAylIY"},
        {"title": "Po nieudanym zamachu stanu w Turcji Konon przestrzega turystów przed Erdoğanem – bandytą i mordercą", "url": "https://www.youtube.com/watch?v=zGlBqDu0DT4&t=24s"},
        {"title": "Kononowicz chce pomóc podlaskim taksówkarzom i składa wniosek o montaż szyb kuloodpornych", "url": "https://www.youtube.com/watch?v=qBqUVnbaWko"},
        {"title": "Kononowicz pali flagę Państwa Islamskiego", "url": "https://www.youtube.com/watch?v=k_4S-2D6--w"},
        {"title": "Nibemben zapowiada walkę z Państwem Islamskim", "url": "https://www.youtube.com/watch?v=2wUMPElTa7w"},
        {"title": "Wybuch afery gównianej i Wielki Test mleka", "url": "https://www.youtube.com/watch?v=tB6o7vpDM8U"},
        {"title": "Prof. Tomasz Baranowski i Kononowicz dyskutują o bieżącej sytuacji w Rosji", "url": "https://www.youtube.com/watch?v=IuTkgNnSW5Q"},
        {"title": "Kononowicz zachęca młodzież do uprawiania sportu", "url": "https://www.youtube.com/watch?v=LoQZpaVFyW8"},
        {"title": "Przygotowanie gogla–mogla", "url": "https://www.youtube.com/watch?v=XgtHYMjhD74"},
        {"title": "Wielki test musztard na Szkolnej", "url": "https://www.youtube.com/watch?v=Gu018jEcpxU"},
        {"title": "Kononowicz apeluje do polityków, aby zaprzestali kłótni i by żyli po bożemu", "url": "https://www.youtube.com/watch?v=BRt0Rw_iQvY&t=43s"},
        {"title": "Wywiad USA donosi Knurowi, że Putin rozmieścił rakiety 'Islander'", "url": "https://www.youtube.com/watch?v=drHaBQydXYw"},
        {"title": "Kononowicz nagrywa pozdrowienia dla znajomego handlarza z bazaru przy ul. Jurowieckiej", "url": "https://www.youtube.com/watch?v=K1SMsbz2Jxg"},
        {"title": "Odcinek pilotażowy Koncertu życzeń", "url": "https://www.youtube.com/watch?v=R5ovtAXFJNY"},
        {"title": "Testowanie twarożku", "url": "https://www.youtube.com/watch?v=yxCXczVVNyo"},
        {"title": "Kononowicz promuje film 'Wołyń'", "url": "https://www.youtube.com/watch?v=ZJrdf3H10r4"},
        {"title": "Żałoba w Belwederze po zabójstwie Arsena 'Motoroli' Pawłowa – rosyjskiego separatysty z Donbasu", "url": "https://www.youtube.com/watch?v=8oVrc6R3XXM"},
        {"title": "Sielankowa atmosfera na Szkolnej - podziękowania za listy, pozdrowienia i konsumpcja konserw rybnych", "url": "https://www.youtube.com/watch?v=8mtDWb6wE-I&t=3s"},
        {"title": "Kononowicz kpi z byłego ministra Sławomira Nowaka, który po zakończeniu kariery politycznej w Polsce wyemigrował na Ukrainę", "url": "https://www.youtube.com/watch?v=O9BxwuZ01mo&t=27s"},
        {"title": "Bankiet z okazji 10. rocznicy startu Knura w wyborach", "url": "https://www.youtube.com/watch?v=6kPoBsLcNdg"},
        {"title": "Kononowicz deklaruje chęć pogodzenia się ze swoim sąsiadem Kargulem", "url": "https://www.youtube.com/watch?v=1tZ-1sLl0nY&t=2s"},
        {"title": "Kononowicz wypowiada się krytycznie o bieżącej sytuacji i apeluje do ministrów, żeby zmienić tą sytuację na lepsze", "url": "https://www.youtube.com/watch?v=Q5DeHCjgPPU"},
        {"title": "Testowanie czekolad", "url": "https://www.youtube.com/watch?v=27vYYRrM9zM"},
        {"title": "Oraz spaniałej kobiety Karoliny żądłem bożym", "url": "https://www.youtube.com/watch?v=zYmeXw3y1eQ&t=69s"},
        {"title": "Ostatni epizod Koncertu życzeń", "url": "https://www.youtube.com/watch?v=DQ8D_lqc5S8"},
        {"title": "Kononowicz cieszy się z dobrych według niego zmian w Europie i na świecie", "url": "https://www.youtube.com/watch?v=k78AYqAlm44"},
        {"title": "Kononowicz i Major przeciwko ukraińskiemu ekspansjonizmowi", "url": "https://www.youtube.com/watch?v=5jG6v0PYV00"},
        {"title": "Test chipsów Laos i Helios", "url": "https://www.youtube.com/watch?v=cQuXq2yhZdg"},
        {"title": "Degustacja konserw mięsnych", "url": "https://www.youtube.com/watch?v=U4IVYAihshQ"},
        {"title": "Zapowiedź wielkiego testu produktów na Szkolnej", "url": "https://www.youtube.com/watch?v=MSWuYpWfi58&t=6s"},
        {"title": "Noworoczne orędzie na Szkolnej z gościnnym udziałem profesora Tomasza, który siedział ze zwisającym glutem", "url": "https://www.youtube.com/watch?v=Vu9TYT1-shg&t=300s"},
        {"title": "Sylwester na Szkolnej, test perfumów", "url": "https://www.youtube.com/watch?v=UbcoXKgyfB4"}
    ],
    "2017": [
        {"title": "Pierwszy film Meksyka ze Szkolnej. Wybuch afery rasistowskiej", "url": "https://www.youtube.com/watch?v=0nijfKomaI4"},
        {"title": "Kononowicz i Major komentują wybryki wnuka Lecha Wałęsy - Dominika", "url": "https://www.youtube.com/watch?v=CNE5rGRUjsw&t=18s"},
        {"title": "Otwieranie kiszonych śledzi ze Szwecji (Surströmming)", "url": "https://www.youtube.com/watch?v=2oFIBqUdBhw"},
        {"title": "Żołnierka z Bombasu przyjechała zakosztować żądła Majora", "url": "https://www.youtube.com/watch?v=89ySHbbGUtY"},
        {"title": "Premiera Pal Hajs TV z Kononowiczem i Dziąślakiem", "url": "https://www.youtube.com/watch?v=BW7YcpGqeC0"},
        {"title": "Kononowicz chce sprzedać Asterkę Bożą za 7000 zł", "url": "https://www.youtube.com/watch?v=oUWNcH0UYNI"},
        {"title": "Film 'Major nagrał a Kononowicz pozwolił to nagrać'", "url": "https://www.youtube.com/watch?v=ZesxqtNqEew"},
        {"title": "Wybuch afery kartkowej. Mateusz Kupiec pisze list, grożąc karą pozbawienia wolności do lat 25 za śmieci na podwórku. Wybuch afery gejowskiej. Struś nazywa 11-letnią córkę widza 'niezłą szprychą'", "url": "https://www.youtube.com/watch?v=9aK_6DzptYs"},
        {"title": "Konon i Major żebrzą o węgiel na filmie Rąbanko", "url": "https://www.youtube.com/watch?v=Qlh2Zxk4j1A"},
        {"title": "Kanał Jarosław Andrzejewski spada z rowerka za film 'Komentarz polityczny'", "url": "https://www.youtube.com/watch?v=6ufUZUxqTUc"},
        {"title": "Podpity Meksyk nagrywa wieczornego vloga dzień po usunięciu kanału Jarosław Andrzejewski", "url": "https://www.youtube.com/watch?v=HynNkPq6wAQ"},
        {"title": "Prośba do prezesa JuTuby o zwrot kanału Jarosław Andrzejewski", "url": "https://www.youtube.com/watch?v=fvAWuyz4ZEc"},
        {"title": "Struś narzeka, że opieka nie daje żadnych pieniędzy i przez to na Szkolnej nie ma węgla", "url": "https://m.youtube.com/watch?v=uvDxwCa0VFk&t=36s"},
        {"title": "Suchodolskioriginal zawieszony za rasistowskie komentarze. Państwo Budyniowie pojawiają się na Szkolnej", "url": "https://www.youtube.com/watch?v=wYlXPe32yTo"},
        {"title": "Kłótnia o krzanik przy śniadanku bożym", "url": "https://www.youtube.com/watch?v=pdtWJmxhrkI"},
        {"title": "Powstaje przypowieść o ojcu i synu", "url": "https://www.youtube.com/watch?v=VlVQQyEzAu0"},
        {"title": "Wybuch afery kubkowej. Debiut Pawła z Warszawy", "url": "https://www.youtube.com/watch?v=796KHOZ5KSE"},
        {"title": "Film 'Nero, straż i wasze dary'", "url": "https://www.youtube.com/watch?v=HXxEqnUcODE"},
        {"title": "Spaniała kłótnia małżeńska z wejściem do pieca i zepsutą kiełbasą w tle", "url": "https://www.youtube.com/watch?v=m_3SINSkCGo"}
    ],
    "2018": [
        {"title": "Degustacja moczu przez Matkobijano", "url": "https://www.youtube.com/watch?v=vETQhINR4ik"},
        {"title": "Film 'Kabab jest ok' - Konon też dostał, Major położył mu na patelnię", "url": "https://www.youtube.com/watch?v=-iNGM6ziR_s"},
        {"title": "Szkolną odwiedza discopolowy zespół Defis", "url": "https://www.youtube.com/watch?v=WiRWYOVdibE"},
        {"title": "Konon i Major na Wixapolu w klubie Metro", "url": "https://www.youtube.com/watch?v=rLCQz2uIG-U"},
        {"title": "Rozpoczyna się kariera Mariusza Jejebaka", "url": "https://www.youtube.com/watch?v=JsPZHl2UHF4"},
        {"title": "Mexicano oskarża Ewę o wyłudzenie od niego pieniędzy", "url": "https://www.youtube.com/watch?v=HdWoKSqt50E"},
        {"title": "Melon Gerzdorf (prezent od widzów) pocięty maczetą", "url": "https://www.youtube.com/watch?v=ZDGpnoVU3Ow"},
        {"title": "Jan Łoś debiutuje w Uniwersum", "url": "https://www.youtube.com/watch?v=4B-PoEpsuAY"},
        {"title": "Mariusz z Krzaków rozpoczyna maraton testów, na pierwszy ogień idzie Surströmming", "url": "https://www.youtube.com/watch?v=k1SVra9IWnI"},
        {"title": "Beztoaletano wyłudza pieniądze na protezę dla koleżanki", "url": "https://www.youtube.com/watch?v=UiKcayLgf5A"},
        {"title": "Lajt hotelowy Fiodora z Krzyśkiem", "url": "https://www.youtube.com/watch?v=457G4esAjsw&list=PLyaGUNhPvm-wZ78hnHxwSOFrr2L0M_I3P&index=6"},
        {"title": "Warmianin robi pajacyki", "url": "https://www.youtube.com/watch?v=6p1zAFQTtaU"},
        {"title": "Jarek w filmie 'Deko prawdy' oskarża Kononowicza o wykorzystywanie seksualne matki", "url": "https://www.youtube.com/watch?v=o6jjHCnaJmY"}
    ],
    "2019": [
        {"title": "Sradek po raz pierwszy ujawnia legowisko Strusia. Publikacja filmu 'Kononowicz mówi wam całą prawdę o Majorze'", "url": "https://www.youtube.com/watch?v=RkR7-4Hy20Q"},
        {"title": "Konon nagrywa legendarny film 'Major sprzedaje Opla i chce się wymeldować'", "url": "https://www.youtube.com/watch?v=-Sz0HzLHul0"},
        {"title": "Film 'Kononowicz mówi całą prawdę dla właścicieli o wynajęciu mieszkań dla ludzi i patologicznych'", "url": "https://www.youtube.com/watch?v=un4wZ7-_TZw"},
        {"title": "Przewodniczący opuszcza placówkę", "url": "https://www.youtube.com/watch?v=c0PCc3u4fLE&ab_channel=KononowiczOrginal"},
        {"title": "Major i Sradek spędzają romantyczny wieczór w hotelu", "url": "https://www.youtube.com/watch?v=1jOdkZmR0m0"},
        {"title": "Centaur publikuje podsłuchaną pod oknem rozmowę pary prezydenckiej", "url": "https://www.youtube.com/watch?v=46fz2SK1mOs"},
        {"title": "Potańcówka disco-polo na Szkolnej", "url": "https://www.youtube.com/shorts/AbEHZgbUVoY"},
        {"title": "Pijany Szczudlak szczy do wiadra na lajcie", "url": "https://www.youtube.com/watch?v=iZFQiF2LRVs&t=4h55m10s"},
        {"title": "W ciągu kilku dni z Kononowicz Orginal w tajemniczych okolicznościach ginie kilkadziesiąt filmów, w tym klasyki Niemieckiego - dostęp do konta miał wówczas Pato", "url": "https://www.youtube.com/watch?v=VVdXYIvZqFI&t=203s"}
    ],
    "2020": [
        {"title": "Kononowicz wypowiada się na temat Majora", "url": "https://www.youtube.com/watch?v=mDNwiukcdMk&t=9s"},
        {"title": "Adam Czeczetkowicz zapowiada wizytę u Kononowicza", "url": "https://www.youtube.com/watch?v=8JVDd0ngDrs&t=4s"},
        {"title": "Kononowicz po liście siostry Grażyny nie wyklucza zostania misjonarzem w Afryce", "url": "https://www.youtube.com/watch?v=6PZxmBzaqIE&t=10s"},
        {"title": "Kononowicz relacjonuje odwiedziny Czeczetkowicza na Szkolnej", "url": "https://www.youtube.com/watch?v=TVdE8AmYwHM&t=144s"},
        {"title": "Knur za nagrywanie bije widza po łypie", "url": "https://www.youtube.com/watch?v=hAS7m3atuR4"},
        {"title": "Asterka Kononowicza obrzucona gównem", "url": "https://www.youtube.com/watch?v=AXcFDGLy-OE"},
        {"title": "Knur opuszcza szpital z zapasem papieru toaletowego", "url": "https://www.youtube.com/watch?v=wV4Nlc5oxlE&ab_channel=mexicanotv"},
        {"title": "Kononowicz nachodzi mieszkanie Łosiów", "url": "https://www.youtube.com/watch?v=TnoN7lWqMxA"},
        {"title": "Zaginięcie Azorka - lament bembeński i pijany w sztok Szczudlak", "url": "https://www.youtube.com/watch?v=SJVXI4VnfPk"},
        {"title": "Pod Belweder przyjeżdżają karawany", "url": "https://www.youtube.com/watch?v=9DHxMJh_Bno"},
        {"title": "Knur otrzymuje od widza koronę cierniową, nakłada ją ofiarnie, przyjmując na siebie grzechy całej Polski", "url": "https://www.youtube.com/watch?v=UP-27NEJjRQ&ab_channel=MlecznyCz%C5%82owiek"},
        {"title": "Kononowicz wykonuje diss na hejterów i przestępców", "url": "https://www.youtube.com/watch?v=AwQh6ad-n1I&ab_channel=MlecznyCz%C5%82owiek"},
        {"title": "Potężna awantura w Belwederze - Struś oskarża Knura o kradzież pieniędzy", "url": "https://www.youtube.com/watch?v=UisfGdI79I8"},
        {"title": "Naćpany Dziąślak przypadkiem odpala lajta, którego szybko wyłącza. Powrót wychudzonego Odleżynowicza do Belwederu", "url": "https://www.youtube.com/watch?v=W7LqZA0eIGo&t=21s"},
        {"title": "Sradek rysuje odleżynę Knura", "url": "https://www.youtube.com/watch?v=dGLOFo-ExOM"},
        {"title": "Widz przysyła na Szkolną obraz z Mariuszem Trynkiewiczem", "url": "https://www.youtube.com/watch?v=-xNeVR8jn5U&ab_channel=MlecznyCz%C5%82owiek"}
    ],
    "2021": [
        {"title": "Major wraca z zabawy sylwestrowej, sceny zazdrości wściekłej żony", "url": "https://www.youtube.com/watch?v=4LEOwL8YxMc"},
        {"title": "Pierwszy film Radka ze Szrotu z Kononowiczem", "url": "https://www.youtube.com/watch?v=RNt2578tJco"},
        {"title": "Konon obwinia Meksyka o wysłanie paczki z gównem i wrobienie Kargula", "url": "https://www.youtube.com/watch?v=-ikm_OutGjM"},
        {"title": "Pierwszy film z Niżarłakiem na kanale Paweł z Knyszyna", "url": "https://www.youtube.com/watch?v=g2g7xwdaryU"},
        {"title": "Film Czeczeta i Kosno pt. 'Cała prawda o Krzysztofie Kononowiczu'", "url": "https://www.youtube.com/watch?v=BnJPnjCNOzI"},
        {"title": "Kononowicz bije w twarz Mariusza Chodora", "url": "https://www.youtube.com/watch?v=l1gSdlptasc"},
        {"title": "Wybuch afery kempingowej. Nitrodolski ukarany mandatami na kwotę 1600 złotych", "url": "https://www.youtube.com/watch?v=dMLJ6jA3O9o"},
        {"title": "Kononowicz wpada do sklepu budowlanego i dyskutuje ze sprzedawczynią - całą sytuację rejestruje", "url": "https://youtu.be/bnurLi-_uc0"},
        {"title": "Debiut Andrzeja Geremka", "url": "https://www.youtube.com/watch?v=XdZtoMg63B0"},
        {"title": "Major wyzywa widzów i ogłasza zakończenie kariery", "url": "https://www.youtube.com/watch?v=OcAyQhPPmhg"},
        {"title": "Katastrofa dobrzyniewska – Knur w drodze na grób Janka rozbija Passata z Majorem i Jackiem na pokładzie", "url": "https://www.youtube.com/watch?v=QTEhxlocb84"},
        {"title": "Egipskie ciemności na Szkolnej, Struś płaci 1340 zł za światło", "url": "https://www.youtube.com/watch?v=UDIbYFLwAhk"},
        {"title": "Knur wygrywa z MOPR-em trzy rozprawy w sądzie", "url": "https://www.youtube.com/watch?v=tiDxjGOKrrs"},
        {"title": "Mariusz Chodor składa wniosek o rejestrację Biura Interwencji Obywatelskich", "url": "https://www.youtube.com/watch?v=9jabB5_j4yI"},
        {"title": "Olgierano publikuje film 'Górskie opowieści'", "url": "https://www.youtube.com/watch?v=x2KQl6Jgfw4"},
        {"title": "Pijacka kłótnia Majora i Jacka o to, kto ma wypierdalać", "url": "https://www.youtube.com/watch?v=rHW2CNDBsjw"},
        {"title": "Kłótnia o babkę ziemniaczaną", "url": "https://www.youtube.com/watch?v=L3QfvpaJb0w"},
        {"title": "Uniwerstal zostaje wyzwolony spod bombaskiej okupacji", "url": "https://www.youtube.com/watch?v=jEG533AiSiI"},
        {"title": "Nieudana wizyta Kononowicza na grobie Jana Łosia (Jacek pomylił groby)", "url": "https://www.youtube.com/watch?v=fn27a65vZBQ"},
        {"title": "Ksiek i Jacek ponownie udają się na grób Janka, tym razem odnajdując właściwy", "url": "https://www.youtube.com/watch?v=kO-26xTx3Xs"},
        {"title": "Major spotyka się z widzami w monopolowym", "url": "https://www.youtube.com/watch?v=rV96nwGxPWI"},
        {"title": "Potężna kłótnia między Kononowiczem, Majorem i Jackiem", "url": "https://www.youtube.com/watch?v=pk5n7viRlA4"},
        {"title": "Debiut Adama Akordeonisty, letnie kolędowanie na Szkolnej", "url": "https://www.youtube.com/watch?v=EWemfILpuiE"},
        {"title": "Wyjazd Odleżynowicza i Majora na Warmię tudzież Mazury", "url": "https://www.youtube.com/watch?v=6hvOak8fGME"},
        {"title": "Kononowicz i Major w Wilkowie i Świętej Lipce, gorsząca wizyta na grobie Marianka", "url": "https://www.youtube.com/watch?v=VeEjFYMO_y4"},
        {"title": "Aron puszcza spreparowane nagranie, w którym Knur rzekomo oskarża Strusia o bycie gejem", "url": "https://www.youtube.com/watch?v=yM0nAJ3KbJE"},
        {"title": "Paulina z Holandii za sprawą Konona oskarża J00ra o bycie gejem, awantura o nożyczki", "url": "https://www.youtube.com/watch?v=Sz5KsyCw-RE"},
        {"title": "Masturbator", "url": "https://www.youtube.com/watch?v=rSA-SAP5gr4"},
        {"title": "Knur rujnuje uroczystość ku pamięci pradziadka Józefa Piłsudskiego", "url": "https://www.youtube.com/watch?v=qfRQvTBkFis"},
        {"title": "Lajt z gościnnym udziałem Kosno i Jacka od psa Arona", "url": "https://www.youtube.com/watch?v=CkfmLrA4P10"},
        {"title": "Małżeńska kłótnia o wyrywanie metek z ubrań", "url": "https://www.youtube.com/watch?v=mg_PYEWxyhE"},
        {"title": "Dziąślak kupuje w komisie w Sienkiewiczach Mazdę 323", "url": "https://www.youtube.com/watch?v=-fnogHyrE8Q&t=164s"},
        {"title": "Konon spotyka się z Pudzianem na otwarciu siłowni", "url": "https://www.youtube.com/watch?v=3XJvv0FJxZU"},
        {"title": "BIO pacyfikuje wariacki festiwal na Zielonych Wzgórzach", "url": "https://www.youtube.com/watch?v=t8o3D0T5W0I"},
        {"title": "Ksiek w dwóch exposé wyjaśnia zielonego Rafałka", "url": "https://www.youtube.com/watch?v=HxIqZTtkcko&t=135s"},
        {"title": "I Jacusia", "url": "https://www.youtube.com/watch?v=rn_uua0XVHk&t=75s"},
        {"title": "Kononowicz i Ekoludek poszli na grzybobranie", "url": "https://www.youtube.com/watch?v=PTseq9lHoU4"},
        {"title": "Major próbuje sprzedać Astrę w Uniwerstalu, ale Kononowicz się temu sprzeciwia", "url": "https://www.youtube.com/watch?v=NpN4j9m2wxs"},
        {"title": "Wielka kłótnia pary prezydenckiej o kobietę J00ra", "url": "https://www.youtube.com/watch?v=RjZHp6q3Ukw&t=30s"},
        {"title": "Olgierdano powraca z filmem o Bobolaku", "url": "https://www.youtube.com/watch?v=QAJQW-Jq5IY"},
        {"title": "Struś dostaje paczkę z gnojem, Knur rozwala go po podłodze", "url": "https://www.youtube.com/watch?v=5tN1z-3BBQM"},
        {"title": "Major ostro wyjaśnia Kononowicza", "url": "https://www.youtube.com/watch?v=7KWc7vB4NSs&t=1079s"},
        {"title": "Knur wyjawia, że Ekogroszek grzebie w śmieciach", "url": "https://www.youtube.com/watch?v=rzB7epo2pVk&t=751s"},
        {"title": "Asterka Majora obrzucona pomidorami", "url": "https://www.youtube.com/watch?v=xPbYteI0WMc&t=132s"},
        {"title": "Pato składa wizytę w Belwederze, kłótnia Konona z Jackiem", "url": "https://www.youtube.com/watch?v=JZbVOnPR-W4&t=797s"},
        {"title": "Potężny Mazur wykopuje Majora z jego służbowego samochodu", "url": "https://www.youtube.com/watch?v=3UbhWoQZS5M&t=51s"},
        {"title": "Nitrodolski jedzie po Ekogrochówie i oskarża go o przywłaszczenie hulajnogi", "url": "https://www.youtube.com/watch?v=a5Wn5Bsvc8c&t=390s"},
        {"title": "MOPR kontroluje nawąchanego Majora", "url": "https://www.youtube.com/watch?v=I8YNzcDfPZc&t=687s"},
        {"title": "Czym pali w piecu Konon", "url": "https://www.youtube.com/watch?v=Cd8ptHGarwI"},
        {"title": "Kosno torpeduje lajta Olgierda, oddaje hulajnogę mimo wcześniejszych wyzwań", "url": "https://www.youtube.com/watch?v=XouWV32Pp9c"},
        {"title": "Piotr z Warszawy prowadzi antylateksowego lajta z Knyszonem", "url": "https://www.youtube.com/watch?v=Totj9nWDN0s"},
        {"title": "Szkolną odwiedza 66-letni widz Tadeusz, nachlany Jacek kłóci się z Kononem", "url": "https://www.youtube.com/watch?v=zGNWs2RE8-o"},
        {"title": "Nibemben wzywa policję na nawąchanego Motylka", "url": "https://www.youtube.com/watch?v=K7X2BDQNuGE"},
        {"title": "Ktoś rozbija tylną lampę w ekodieslu, podejrzenia padają na Olgierdano", "url": "https://www.youtube.com/watch?v=nlEXVIhXFhk"},
        {"title": "Major sprzedaje IV Asterkę dla Krzysztofa za pieniądze Arona", "url": "https://www.youtube.com/watch?v=tbfulZx9jVA&t=558s"},
        {"title": "Szymon Hołownia uraczony smrodem warmiańskim podczas rozmowy z Kononem", "url": "https://www.youtube.com/watch?v=7dt-czFziRM&t=686s"},
        {"title": "Spaniałe dymy pod bramką, ostatni chuj Polski zwyzywany przez widza", "url": "https://www.youtube.com/watch?v=_GMyJu7EwiM&t=134s"},
        {"title": "Ksiek ogłasza gotowość na przybicie do krzyża i śmierć", "url": "https://www.youtube.com/watch?v=ZltmTIwOtUk&t=2709s"},
        {"title": "Młodzież bandycka wybija tylną szybę w IV Asterce", "url": "https://www.youtube.com/watch?v=fh8s2dphQx8"},
        {"title": "Pato i Major dają ubrania bezdomnym", "url": "https://www.youtube.com/watch?v=KLAtrREk0vs&t=127s"},
        {"title": "Lajt Vincenta Vegi i pojazd Knura po Pato i Kroście", "url": "https://www.youtube.com/watch?v=doSbXqI-x8c"},
        {"title": "Małolaci atakują Belweder petardą, frajerzy spod Łomży pogonieni kulachą", "url": "https://www.youtube.com/watch?v=d_mqIT0WRNQ"},
        {"title": "Dobry frekwencyjnie lajt Olgierdano, Ekoparówa nasyła na Ola Knurowicza", "url": "https://www.youtube.com/watch?v=jbeFLJ7_CrU"},
        {"title": "W Szczuczynie odbywa się pogrzeb Teresy Korol. Inwazja pluskiew i wszy na Belweder", "url": "https://www.youtube.com/watch?v=nnpE0s3ctfc&t=160s"},
        {"title": "Rozprawa sądowa w sprawie rozbicia Passata odroczona, nad Belwederem pojawia się dron", "url": "https://www.youtube.com/watch?v=1sxHrsHp6KY"},
        {"title": "Olgierdano składa zawiadomienia do Urzędu Miasta i ZUS o fundację Kosno", "url": "https://www.youtube.com/watch?v=lNTN5mJuA6Q"},
        {"title": "Morderczy koledzy Majora wrzucają śmieci na posesję belwederską", "url": "https://www.youtube.com/watch?v=ZDuFQLZRmqc"},
        {"title": "Widzowie kradną telefon i kamerę Majora, po kilku godzinach oddają", "url": "https://www.youtube.com/watch?v=zPPKEgdFNfY&t=22s"},
        {"title": "Kanał mexicano tv zbanowany za 'podszywania się pod inne osoby'", "url": "https://www.youtube.com/watch?v=0Fq4fK2kuHk"},
        {"title": "Sąd odbiera Kononowiczowi prawo jazdy", "url": "https://www.youtube.com/watch?v=HEF1gHyVQSo"},
        {"title": "Major w towarzystwie Pato i Jacka odwiedza grób swojej matki", "url": "https://www.youtube.com/watch?v=6FstBV67Kak"},
        {"title": "Dwóch lateksów Pato i Krecik spotykają się na Wierzbowa Park", "url": "https://www.youtube.com/watch?v=is_13tZrPCQ"},
        {"title": "Konon stwierdza, że Janina Suchodolska zmarła przez wybryki syna", "url": "https://www.youtube.com/watch?v=U2E-ENdMWa0&t=292s"},
        {"title": "Blackout na Szkolnej, Belweder w ciemności", "url": "https://www.youtube.com/watch?v=5mdS9Pxubfg"},
        {"title": "Struś wyrzuca bigos do hoboka, Nibemben rzuca klątwę warmiańską", "url": "https://www.youtube.com/watch?v=Dwq3AfPnT9I"},
        {"title": "Zwieńczenie wątku bigosowego - para tuszy bigos", "url": "https://www.youtube.com/watch?v=-Qs_PCZKIh0"},
        {"title": "Szczoch żebrze na lajcie, unika wyjaśnień w sprawie §207", "url": "https://www.youtube.com/watch?v=Cy3Gg1InpzA"},
        {"title": "Seria trzech lajtów: Knur błaga o dzwonienie na policję", "url": "https://www.youtube.com/watch?v=3l_4rjmlH7U"},
        {"title": "Ksiek ponownie kandyduje na prezydenta Białegostoku", "url": "https://www.youtube.com/watch?v=53yajJ9YeYM"},
        {"title": "El Szympanso prowadzi lajta spod Belwederu, kłótnia z Kononem", "url": "https://www.youtube.com/watch?v=yuM4YibTDik&t=3600s"},
        {"title": "Wybuch afery postrzałowej - nieudany zamach na prezydenta", "url": "https://www.youtube.com/watch?v=3O4-YlKddpE&t=430s"},
        {"title": "Kononowicz atakuje widza PodjeżdżanoTV pod bramką", "url": "https://www.youtube.com/watch?v=RZmO-2dMld4"},
        {"title": "Świąteczna paczka od Łukasza z Barwic na Szkolnej", "url": "https://www.youtube.com/watch?v=PZQT__sBGss&t=664s"}
    ],
    "2022": [
        {"title": "Rozmowa telefoniczna pomiędzy Olgierdano a Sławkiem, w której ten drugi kuli ogon pod siebie i rozłącza się", "url": "https://www.youtube.com/watch?v=W3F6KoWg0a8"},
        {"title": "Olgierd zapowiedział kroki prawne przeciwko rudej kurwie. Kononowicz dostaje mandat 500 zł za nieuzasadnione wezwanie policji", "url": "https://www.youtube.com/watch?v=0_ofMh-oT3E&t=50s"},
        {"title": "Pato mierzy chodnik przy ulicy Szkolnej, udowadniając bezzasadność żali Konona", "url": "https://youtu.be/1UZMM0-h3A0"},
        {"title": "Knur wyproszony z trójki ze względu na bijący od niego fetor", "url": "https://www.youtube.com/watch?v=5mBFNtbvpCU&t=112s"},
        {"title": "Kononowicz oburzony na film Papo Kukasa o chodniku, wydaje dekret o zakazie parkowania na chodniku przy Szkolnej", "url": "https://www.youtube.com/watch?v=n15lgqLU8P4"},
        {"title": "Odyniec podczas szarży na frajerów przypadkowo psika się gazem", "url": "https://www.youtube.com/watch?v=M9CNUhwY5rc&t=150s"},
        {"title": "Kononowicz planuje inwazję na Józefa Kosno", "url": "https://www.youtube.com/watch?v=sD2qXJVOwDw"},
        {"title": "Beria jechany przez Majora jak po MOPR-u oraz kopany przez widza na lajcie u Piotra Wawy", "url": "https://www.youtube.com/watch?v=EP6GigfE5u4"},
        {"title": "Lajt z Pato z jazdy z Majorem, który podczas lajta kupuje nitro", "url": "https://www.youtube.com/watch?v=zc7eQQHo3bI"},
        {"title": "Gumowy Adaś wraca na Szkolną i idąc po mleczko wypierdala się na śniegu", "url": "https://www.youtube.com/watch?v=e0kYFG37rTA"},
        {"title": "Kononowicz jedzie na trójkę z torbą donosów", "url": "https://youtu.be/MeX-up6eiQ4?t=282"},
        {"title": "Młody Redaktor zatrzymany przez milicję podczas lajta bożego spod bramki", "url": "https://www.youtube.com/watch?v=vPpF_7j-d0w"},
        {"title": "Podjeżdżano TV rozmawia przez telefon z Eko Kukasem", "url": "https://www.youtube.com/watch?v=ouCUeLcGVys"},
        {"title": "Szkolną odwiedziła policja i straż miejska", "url": "https://www.youtube.com/watch?v=pE3yka57IIA"},
        {"title": "Major dostaje od Potężnego Warmianina najpierw w jądra, a potem w łypę", "url": "https://www.youtube.com/watch?v=CyPvNSjpdj4"},
        {"title": "Na Szkolnej pojawia się Dryblas, nowy lokator Belwederu", "url": "https://youtu.be/KtXDwffzVMQ"},
        {"title": "Niemiecki wraca na Szkolną - Ksiek żąda jego ciągłej obecności", "url": "https://www.youtube.com/watch?v=eEmthIU4aus"},
        {"title": "Motofrajer otrzymuje po łypie od Ksieka i odjeżdża", "url": "https://www.youtube.com/watch?v=3ga7nhF29ok"},
        {"title": "Walka Majora z Adasiem na Speluna MMA 1", "url": "https://www.youtube.com/watch?v=MisCTx9sb-U"},
        {"title": "Ze ściany wyrwało bojler. J00r tęskni za Szkolną", "url": "https://www.youtube.com/watch?v=Xp0UZ5k8kOk"},
        {"title": "Powrót zbiega Organisty - montuje klawisze muzyczne dla Kononowicza", "url": "https://www.youtube.com/watch?v=hT37XSni8Lc"},
        {"title": "Kononowicz kupuje deskę do krojenia za 100 zł. Pracownik Umysłowy ogląda wysrywy", "url": "https://www.youtube.com/watch?v=3wxBp5vUyW4"},
        {"title": "Major oświadczył się swojej nowej dziewczynie", "url": "https://odysee.com/@KononopediaRu:2/major_oswiadczyny_24_07_2022:1"},
        {"title": "Suchodolski narzeka na Kśka", "url": "https://www.youtube.com/watch?v=pyPz0NhM_vU"},
        {"title": "Podjeżdżano odnajduje Suchodolskiego w lesie", "url": "https://www.youtube.com/watch?v=x6dswSncDAI"},
        {"title": "Nitrołak nagrywa śniadanie w Ogrodach Belwederskich", "url": "https://www.youtube.com/watch?v=xcHY2g9OLuM"},
        {"title": "Piąta przeprowadzka Szczura w 2022 roku", "url": "https://www.youtube.com/watch?v=QI6ma3D5LJU"},
        {"title": "Major obwieszcza zmianę numeru telefonu", "url": "https://www.youtube.com/watch?v=Y7q1XGbKJNc"},
        {"title": "Kajor nagrywa różne gnioty", "url": "https://www.youtube.com/watch?v=GegujTqt9YY"},
        {"title": "Nitro Hunter relacjonuje nitrosafari na żywo", "url": "https://www.youtube.com/watch?v=mx2cuWeeXEo"},
        {"title": "Nagrywanie skwierczącego na grylu mięsa", "url": "https://www.youtube.com/watch?v=V5bpPz1JB9o"},
        {"title": "Wojtek nagrywa gnioty z Mazur", "url": "https://www.youtube.com/watch?v=EymE9WGtJT8"},
        {"title": "Wstępne nagranie do Sprawy dla Reportera - Szczudlarz na Mazurach", "url": "https://www.youtube.com/watch?v=0or9wMxg3MA"},
        {"title": "Suchodolski wstawia gniota z siniedania", "url": "https://www.youtube.com/watch?v=KGLTN4Gvlfc"},
        {"title": "Negocjacje o nagrywanie lajtów - Struś grozi, że żadnego lajta nie będzie", "url": "https://www.youtube.com/watch?v=mt1gzdAEYY4"},
        {"title": "Sendecki pozwala Ksiekowi użyć mikrofonu", "url": "https://www.youtube.com/live/DW2H_ZvkHmI?t=3384"},
        {"title": "Knur atakuje frajerów robiących sobie z nim zdjęcie bez zgody", "url": "https://youtu.be/azrRzIpWORk"},
        {"title": "Szkolna The Game", "url": "https://youtu.be/NY7geukFzto"},
        {"title": "Krzysiek pyta Majora o uderzenie Janka Rodo", "url": "https://youtu.be/XdK2qiEek0k"},
        {"title": "Słynny warmiański okrzyk", "url": "https://youtu.be/SJWZEoQe6HE"},
        {"title": "Krzysiek po rozmowie telefonicznej przystępuje do 40-minutowego exposé", "url": "https://youtu.be/RtdLhiwWNfw"},
        {"title": "Krzysiek o Wojtku w kolejnym 40-minutowym exposé", "url": "https://youtu.be/_cvrKpPDOMg"},
        {"title": "Krzysiek wspomina Majorowi o obrażaniu świętych podczas afery końskiej", "url": "https://youtu.be/g_zVg_udLLw"}
    ],
    "2023": [
        {"title": "Sierżant Bagieta komentuje zachowanie policjantów w kontekście ataku Knura na Piotra z Warszawy, myli WSW z Barnejem", "url": "https://youtu.be/MjmRg_YT5h0"},
        {"title": "Organista pokazuje Kśkowi dwa ciekawe filmy (część 1)", "url": "https://kononopedia.ru/doku.php?id=chronologia:chronologia_uniwersum_2023#refnotes:1:note10"}, 
        {"title": "Organista pokazuje Kśkowi dwa ciekawe filmy (część 2)", "url": "https://youtu.be/iNdIZWJMCfE"}
    ],
    "2024": [
        {"title": "Jareczek podgrzewa danie gotowe z Biedronki w mikrofalówce. Krzysiek ogląda i odnosi się do filmu Mexicana", "url": "https://youtu.be/qfBM8xAAO30"},
        {"title": "Nabożeństwo na Szkolnej", "url": "https://youtu.be/URqL179PPlQ?t=725"},
        {"title": "Ksiek przekomarza się ze Sławkiem przez telefon i śpiewa mu piosenkę", "url": "https://youtu.be/SnSJ79J0zXE?t=91"},
        {"title": "Olgierdano publikuje 'Taśmy prawdy'", "url": "https://youtu.be/BezqEzaZHKc"},
        {"title": "Organista wiezie Ksieka na Szkolną, łamiąc przepisy drogowe (słynne zawracanie na rondzie)", "url": "https://youtu.be/iyqK1ULJILQ"},
        {"title": "Jacek od psa Arona wymienia filtr w oczyszczaczu powietrza w Belwederze", "url": "https://youtu.be/kQi0xrHtW7k"},
        {"title": "Kononowicz ogląda film Mexicana o 'specjalnym immunitecie' na jazdę bez prawa jazdy", "url": "https://youtu.be/K4tRSqkHd28"},
        {"title": "Krzysztof ogląda kolejny film Mexicana o 'magicznym immunitecie'", "url": "https://youtu.be/c8BUbWbJDxc"}
    ],
    "2025": [
        {
            "title": "Incydent kałowy podczas lajta Pawła w Warszawie",
            "url": "https://www.youtube.com/watch?v=ZLI9oLgeYZ8"
        },
        {
            "title": "Mitoman Kacper wydaje nowe oświadczenie (opublikowane przez Olgierdano), zniknięcie wilmu z włamania",
            "url": "https://odysee.com/@KononopediaRu:2/wtargniecie-i-dewastacja-kamery-(noc-z-25-na-26-stycznia-2025)"
        },
        {
            "title": "Nietypowy film na kanale Niedobrego Centaura - Jacek o powrocie Krzysztofa do zdrowia",
            "url": "https://odysee.com/Pot%C4%99%C5%BCny-Warmianin-wraca-do-siebie--fQ1uezUZRys-:0"
        },
        {
            "title": "Kosno dodaje film ze sprzeczną informacją o stanie zdrowia Kśka",
            "url": "https://odysee.com/@KononopediaRu:2/Stan-zdrowia--Kononowicz-niestety,-mia%C5%82em-racj%C4%99,-sam-nie-je-nie-pije-ubezw%C5%82asnowolnienie,-karma-%EF%BC%9F--M42aTYSzWto-:d"
        },
        {
            "title": "NWASD przedstawia historię wykorzystywania Kononowicza",
            "url": "https://www.youtube.com/watch?v=ejVXd-ON7bc"
        },
        {
            "title": "Sradek wyjaśnia źródła informacji kanału 'Nie wiem ale się dowiem'",
            "url": "https://odysee.com/@KononopediaRu:2/sk%C4%85d-kana%C5%82-%EF%BC%82Nie-Wiem-Ale-Si%C4%99-Dowiem%EF%BC%82-czerpie-wiedz%C4%99-do-swoich-film%C3%B3w-%E2%9D%93%E2%9D%94-%F0%9F%A6%A7-%F0%9F%A4%94-(czytaj-opis)--FRjrKohhjK8-:7"
        },
        {
            "title": "Sum Wąsaty rozpoczyna serię filmów spod szpitala",
            "url": "https://youtu.be/kHVxiRPa66o"
        },
        {
            "title": "Materiał z sali szpitalnej na kanale Olgierdano official",
            "url": "https://www.youtube.com/watch?v=S48JCEEOR1w"
        },
        {
            "title": "Kosno próbuje zmienić narrację o stanie zdrowia Krzyśka",
            "url": "https://odysee.com/@KononopediaRu:2/15.02.2025--Kononowicz-nagranie-ze-szpitala-po-zapaleniu-p%C5%82uc-oddycha-patrzy,-rozumie,-pr%C3%B3buje-m%C3%B3wi%C4%87--0SD7H0f8GkU-:3"
        }
    ],
}


# Funkcja do pobierania miniaturek
def get_thumbnail(url):
    try:
        video_id = url.split("v=")[1].split("&")[0]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        response = requests.get(thumbnail_url)
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((160, 90), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        default_img = Image.new('RGB', (160, 90), color='gray')
        return ImageTk.PhotoImage(default_img)

# GUI
root = tk.Tk()
root.title("Archiwum Kononowicza")
root.geometry("1100x750")

# Zakładki
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Zakładka "Filmy"
films_frame = ttk.Frame(notebook)
notebook.add(films_frame, text="Filmy")

# Wybór roku
year_var = tk.StringVar()
year_combo = ttk.Combobox(
    films_frame, 
    textvariable=year_var,
    values=["Wszystkie"] + sorted(films_by_year.keys()),
    state="readonly"
)
year_combo.pack(pady=10)
year_combo.set("Wszystkie")

# Lista filmów
film_tree = ttk.Treeview(
    films_frame,
    columns=("title", "year"),
    show="headings",
    height=15
)
film_tree.heading("title", text="Tytuł")
film_tree.heading("year", text="Rok")
film_tree.column("title", width=400)
film_tree.column("year", width=100)
film_tree.pack(fill=tk.BOTH, expand=True)

# Zakładka "Ostatnio oglądane"
history_frame = ttk.Frame(notebook)
notebook.add(history_frame, text="Ostatnio oglądane")

history_tree = ttk.Treeview(
    history_frame,
    columns=("title",),
    show="headings",
    height=15
)
history_tree.heading("title", text="Tytuł")
history_tree.pack(fill=tk.BOTH, expand=True)

# Przycisk "Oglądaj"
def watch_selected():
    tab = notebook.tab(notebook.select(), "text")
    tree = film_tree if tab == "Filmy" else history_tree
    
    selected = tree.selection()
    if selected:
        item = tree.item(selected)
        url = item["values"][-1]  # URL jest ostatnim elementem
        webbrowser.open(url)
        save_to_history({"title": item["values"][0], "url": url})
        update_history_tab()

watch_btn = ttk.Button(
    root,
    text="Oglądaj",
    command=watch_selected
)
watch_btn.pack(pady=10)

# Aktualizacja listy filmów
def update_films(*args):
    film_tree.delete(*film_tree.get_children())
    year = year_var.get()
    
    films = []
    if year == "Wszystkie":
        for y, items in films_by_year.items():
            films.extend([(film["title"], y, film["url"]) for film in items])
    else:
        films = [(film["title"], year, film["url"]) for film in films_by_year.get(year, [])]
    
    for film in films:
        thumb = get_thumbnail(film[2])
        film_tree.insert("", tk.END, values=film, image=thumb)

# Historia oglądania
def update_history_tab():
    history_tree.delete(*history_tree.get_children())
    for item in load_history():
        thumb = get_thumbnail(item["url"])
        history_tree.insert("", tk.END, values=(item["title"], item["url"]), image=thumb)

# Powiązania zdarzeń
year_combo.bind("<<ComboboxSelected>>", update_films)
notebook.bind("<<NotebookTabChanged>>", lambda e: update_history_tab())

# Inicjalizacja
update_films()
root.mainloop()