import os
import sys
import pygame
from pygame import mixer
from tkinter import Tk, filedialog, Button, Label, Scale, HORIZONTAL, Canvas, PhotoImage
from tkinter.ttk import Frame

# Инициализация Pygame
pygame.init()
mixer.init()

class BoykisserPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Boykisser MP3 Player")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#FFC0CB')
        
        # Переменные
        self.current_file = None
        self.paused = False
        self.playing = False
        self.dance_frames = []
        self.current_frame = 0
        self.animation_speed = 100  # мс
        
        # Создание интерфейса
        self.create_widgets()
        self.load_animation_frames()
        
        # Запуск анимации
        self.animate_cat()
    
    def create_widgets(self):
        # Фрейм для элементов управления
        control_frame = Frame(self.root)
        control_frame.pack(pady=10)
        
        # Кнопки
        self.play_btn = Button(control_frame, text="Play", command=self.play_music, bg='#FF69B4', fg='white')
        self.play_btn.pack(side='left', padx=5)
        
        self.pause_btn = Button(control_frame, text="Pause", command=self.pause_music, bg='#FF69B4', fg='white')
        self.pause_btn.pack(side='left', padx=5)
        
        self.stop_btn = Button(control_frame, text="Stop", command=self.stop_music, bg='#FF69B4', fg='white')
        self.stop_btn.pack(side='left', padx=5)
        
        self.open_btn = Button(control_frame, text="Open", command=self.open_file, bg='#FF69B4', fg='white')
        self.open_btn.pack(side='left', padx=5)
        
        # Ползунок громкости
        self.volume_slider = Scale(self.root, from_=0, to=100, orient=HORIZONTAL, 
                                  command=self.set_volume, label="Volume", bg='#FFC0CB')
        self.volume_slider.set(70)
        self.volume_slider.pack(fill='x', padx=20, pady=5)
        
        # Информация о треке
        self.track_label = Label(self.root, text="No track selected", bg='#FFC0CB', fg='#8B008B')
        self.track_label.pack(pady=5)
        
        # Холст для анимации кота
        self.canvas = Canvas(self.root, width=400, height=400, bg='#FFC0CB', highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Создаем изображение кота (заглушка, будет заменена анимацией)
        self.cat_image = PhotoImage()
        self.cat_obj = self.canvas.create_image(200, 200, image=self.cat_image)
    
    def load_animation_frames(self):
        # Здесь должны быть кадры анимации танцующего кота
        # В реальном приложении нужно загрузить несколько изображений
        # Для примера создадим простые кадры с разными положениями ушек
        
        # Кадр 1 - ушки вверх
        frame1 = PhotoImage(data="""
            R0lGODlhZABkAOf/AAABAAECAwQFBgYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQl
            JicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpb
            XF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CR
            kpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbH
            yMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9
            /v///////////////////////////////////////////////////////////////yH5BAEK
            AP8ALAAAAABkAGQAAAj+AP8JHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOK
            HEmypMmTKFOqXMmypcuXMGPKnEmzps2bOHPq3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qdOnUKNK
            nUq1qtWrWLNq3cq1q9evYMOKHUu2rNmzaNOqXcu2rdu3cOPKnUu3rt27ePPq3cu3r9+/gAML
            Hky4sOHDiBMrXsy4sePHkCNLnky5suXLmDNr3sy5s+fPoEOLHk26tOnTqFOrXs26tevXsGPL
            nk27tu3buHPr3s27t+/fwIMLH068uPHjyJMrX868ufPn0KNLn069uvXr2LNr3869u/fv4MP+
            ix9Pvrz58+jTq1/Pvr379/Djy59Pv779+/jz69/Pv7///wAGKOCABBZo4IEIJqjgggw26OCD
            EEYo4YQUVmjhhRhmqOGGHHbo4YcghijiiCSWaOKJKKao4oostujiizDGKOOMNNZo44045qjj
            jjz26OOPQAYp5JBEFmnkkUgmqeSSTDbp5JNQRinllFRWaeWVWGap5ZZcdunll2CGKeaYZJZp
            5plopqnmmmy26eabcMYp55x01mnnnXjmqeeefPbp55+ABirooIQWauihiCaq6KKMNuroo5BG
            KumklFZq6aWYZqrpppx26umnoIYq6qiklmrqqaimquqqrLbq6qv+sMYq66y01mrrrbjmquuu
            vPbq66/ABivssMQWa+yxyCar7LLMNuvss9BGK+201FZr7bXYZqvtttx26+234IYr7rjklmvu
            ueimq+667Lbr7rvwxivvvPTWa++9+Oar77789uvvvwAHLPDABBds8MEIJ6zwwgw37PDDEEcs
            8cQUV2zxxRhnrPHGHHfs8ccghyzyyCSXbPLJKKes8sost+zyyzDHLPPMNNds880456zzzjz3
            7PPPQAct9NBEF2300UgnrfTSTDft9NNQRy311FRXbfXVWGet9dZcd+3112CHLfbYZJdt9tlo
            p6322my37fbbcMct99x012333Xjnrff+3nz37fffgAcu+OCEF2744YgnrvjijDfu+OOQRy75
            5JRXbvnlmGeu+eacd+7556CHLvropJdu+umop6766qy37vrrsMcu++y012777bjnrvvuvPfu
            ++/ABy/88MQXb/zxyCev/PLMN+/889BHL/301Fdv/fXYZ6/99tx37/334Icv/vjkl2/++ein
            r/767Lfv/vvwxy///PTXb//9+Oev//789+///wAMoAAHSMACGvCACEygAhfIwAY68IEQjKAE
            J0jBClrwghjMoAY3yMEOevCDIAyhCEdIwhKa8IQoTKEKV8jCFrrwhTCMoQxnSMMa2vCGOMyh
            DnfIwx768IdADKIQh0jEIhrxiEhMohL+J0jEJjrxiVCMohSnSMUqWvGKWMyiFrfIxS568Ytg
            DKMYx0jGMprxjGhMoxrXyMY2uvGNcIyjHOdIxzra8Y54zKMe98jHPvrxj4AMpCAHSchCGvKQ
            iEykIhfJyEY68pGQjKQkJ0nJSlrykpjMpCY3yclOevKToAylKEdJylKa8pSoTKUqV8nKVrry
            lbCMpSxnScta2vKWuMylLnfJy1768pfADKYwh0nMYhrzmMhMpjKXycxmOvOZ0IymNKdJzWpa
            85rYzKY2t8nNbnrzm+AMpzjHSc5ymvOc6EynOtfJzna6853wjKc850nPetrznvjMpz73yc9+
            +vOfAA2oQAdK0IIa9KAITahCF8rQhjr0oRCNqEQnStGKWvSiGM2oRjfK0Y569KMgDalIR0rS
            kpr0pChNqUpXytKWuvSlMI2pTGdK05ra9KY4zalOd8rTnvr0p0ANqlCHStSiGvWoSE2qUpfK
            1KY69alQjapUp0rVqlr1qljNqla3ytWuevWrYA2rWMdK1rKa9axoTata18rWtrr1rXCNq1zn
            Ste62vWueM2rXvfK17769a+ADaxgB0vYwhr2sIhNrGIXy9jGOvaxkI2sZCdL2cpa9rKYzaxm
            N8vZznr2s6ANrWhHS9rSmva0qE2talfL2ta69rWwja1sZ0vb2tr2trjNrW53y9ve+va3wA2u
            cIdL3OIa97jITa5yl8vc5jr3udCNrnSnS93qWve62M2udrfL3e5697vgDa94x0ve8pr3vOhN
            r3rXy972uve98I2vfOdL3/ra9774za9+98vf/vr3vwAOsIAHTOACG/jACE6wghfM4AY7+MEQ
            /hr4wRCOsIQnTOEKW/jCGM6whjfM4Q57+MMgDrGIR0ziEpv4xChOsYpXzOIWu/jFMI6xjGdM
            4xrb+MY4zrGOd8zjHvv4x0AOspCHTOQiG/nISE6ykpfM5CY7+clQjrKUp0zlKlv5yljOspa3
            zOUue/nLYA6zmMdM5jKb+cxoTrOa18zmNrv5zXCOs5znTOc62/nOeM6znvfM5z77+c+ADrSg
            B03oQhv60IhOtKIXzehGO/rRkI60pCdN6Upb+tKYzrSmN83pTnv606AOtahHTepSm/rUqE61
            qlfN6la7+tWwjrWsZ03rWtv61rjOta53zete+/rXwA62sIdN7GIb+9jITrayl83sZjv72dCO
            trSnTe1qW/va2M62trfN7W57+9vgDre4x03ucpv73OhOt7rXze52u/vd8I63vOdN73rb+974
            zre+983vfvv73wAPuMAHTvCCG/zgCE+4whfO8IY7/OEQj7jEJ07xilv84hjPuMY3zvGOe/zj
            IA+5yEdO8pKb/OQoT7nKV87ylrv85TCPucxnTvOa2/zmOM+5znfO8577/OdAD7rQh070ohv9
            6EhPutKXzvSmO/3pUI+61KdO9apb/epYz7rWt871rnv962APu9jHTvaym/3saE+72tfO9ra7
            /e1wj7vc5073utv97njPu973zve++/3vgA+84AdP+MIb/vCIT7ziF8/4xjv+8ZCPvOQnT/nK
            W/7ymM+85jfP+c57/vOgD73oR0/60pv+9KhPvepXz/rWu/71sI+97GdP+9rb/va4z73ud8/7
            3vv+98APvvCHT/ziG//4yE++8pfP/OY7//nQj770p0/96lv/+tjPvva3z/3ue//74A+/+MdP
            /vKb//zoT7/618/+9rv//fCPv/znT//62//++M+//vfP//77//8AGIACOIAEWIAGeIAImIAK
            uIAM2IAO+IAQGIESOIEUWIEWeIEYmIEauIEc2IEe+IEgGIIiOIIkWIImeIIomIIquIIs2IIu
            +IIwGIMyOIM0WIM2eIM4mIM6uIM82IM++INAGIRCOIREWIRGeIRImIRKuIRM2IRO+IRQGIVS
            OIVUWIVWeIVYmIVauIVc2IVe+IVgGIZiOIZkWIZmeIZomIZquIZs2IZu+IZwGIdyOId0WId2
            eId4mId6uId82Id++IeAGIiCOIiEWIiGeIiImIiKuIiM2IiO+IiQGImSOImUWImWeImYmIma
            uImc2Ime+ImgGIqiOIqkWIqmeIqomIqquIqs2Iqu+IqwGIuyOIu0WIu2eIu4mIu6uIu82Iu+
            +IvAGIzCOIzEWIzGeIzImIzKuIzM2IzO+IzQGI3SOI3UWI3WeI3YmI3auI3c2I3e+I3gGI7i
            OI7kWI7meI7omI7quI7s2I7u+I7wGI/yOI/0WI/2eI/4mI/6uI/82I/++I8AGZACOZAEWZAG
            eZAImZAKuZAM2ZAO+ZAQGZESOZEUWZEWKQkBAAD7
        """)
        
        # Кадр 2 - ушки вниз
        frame2 = PhotoImage(data="""
            R0lGODlhZABkAOf/AAABAAECAwQFBgYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQl
            JicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpb
            XF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CR
            kpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbH
            yMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9
            /v///////////////////////////////////////////////////////////////yH5BAEK
            AP8ALAAAAABkAGQAAAj+AP8JHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOK
            HEmypMmTKFOqXMmypcuXMGPKnEmzps2bOHPq3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qdOnUKNK
            nUq1qtWrWLNq3cq1q9evYMOKHUu2rNmzaNOqXcu2rdu3cOPKnUu3rt27ePPq3cu3r9+/gAML
            Hky4sOHDiBMrXsy4sePHkCNLnky5suXLmDNr3sy5s+fPoEOLHk26tOnTqFOrXs26tevXsGPL
            nk27tu3buHPr3s27t+/fwIMLH068uPHjyJMrX868ufPn0KNLn069uvXr2LNr3869u/fv4MP+
            ix9Pvrz58+jTq1/Pvr379/Djy59Pv779+/jz69/Pv7///wAGKOCABBZo4IEIJqjgggw26OCD
            EEYo4YQUVmjhhRhmqOGGHHbo4YcghijiiCSWaOKJKKao4oostujiizDGKOOMNNZo44045qjj
            jjz26OOPQAYp5JBEFmnkkUgmqeSSTDbp5JNQRinllFRWaeWVWGap5ZZcdunll2CGKeaYZJZp
            5plopqnmmmy26eabcMYp55x01mnnnXjmqeeefPbp55+ABirooIQWauihiCaq6KKMNuroo5BG
            KumklFZq6aWYZqrpppx26umnoIYq6qiklmrqqaimquqqrLbq6qv+sMYq66y01mrrrbjmquuu
            vPbq66/ABivssMQWa+yxyCar7LLMNuvss9BGK+201FZr7bXYZqvtttx26+234IYr7rjklmvu
            ueimq+667Lbr7rvwxivvvPTWa++9+Oar77789uvvvwAHLPDABBds8MEIJ6zwwgw37PDDEEcs
            8cQUV2zxxRhnrPHGHHfs8ccghyzyyCSXbPLJKKes8sost+zyyzDHLPPMNNds880456zzzjz3
            7PPPQAct9NBEF2300UgnrfTSTDft9NNQRy311FRXbfXVWGet9dZcd+3112CHLfbYZJdt9tlo
            p6322my37fbbcMct99x012333Xjnrff+3nz37fffgAcu+OCEF2744YgnrvjijDfu+OOQRy75
            5JRXbvnlmGeu+eacd+7556CHLvropJdu+umop6766qy37vrrsMcu++y012777bjnrvvuvPfu
            ++/ABy/88MQXb/zxyCev/PLMN+/889BHL/301Fdv/fXYZ6/99tx37/334Icv/vjkl2/++ein
            r/767Lfv/vvwxy///PTXb//9+Oev//789+///wAMoAAHSMACGvCACEygAhfIwAY68IEQjKAE
            J0jBClrwghjMoAY3yMEOevCDIAyhCEdIwhKa8IQoTKEKV8jCFrrwhTCMoQxnSMMa2vCGOMyh
            DnfIwx768IdADKIQh0jEIhrxiEhMohL+J0jEJjrxiVCMohSnSMUqWvGKWMyiFrfIxS568Ytg
            DKMYx0jGMprxjGhMoxrXyMY2uvGNcIyjHOdIxzra8Y54zKMe98jHPvrxj4AMpCAHSchCGvKQ
            iEykIhfJyEY68pGQjKQkJ0nJSlrykpjMpCY3yclOevKToAylKEdJylKa8pSoTKUqV8nKVrry
            lbCMpSxnScta2vKWuMylLnfJy1768pfADKYwh0nMYhrzmMhMpjKXycxmOvOZ0IymNKdJzWpa
            85rYzKY2t8nNbnrzm+AMpzjHSc5ymvOc6EynOtfJzna6853wjKc850nPetrznvjMpz73yc9+
            +vOfAA2oQAdK0IIa9KAITahCF8rQhjr0oRCNqEQnStGKWvSiGM2oRjfK0Y569KMgDalIR0rS
            kpr0pChNqUpXytKWuvSlMI2pTGdK05ra9KY4zalOd8rTnvr0p0ANqlCHStSiGvWoSE2qUpfK
            1KY69alQjapUp0rVqlr1qljNqla3ytWuevWrYA2rWMdK1rKa9axoTata18rWtrr1rXCNq1zn
            Ste62vWueM2rXvfK17769a+ADaxgB0vYwhr2sIhNrGIXy9jGOvaxkI2sZCdL2cpa9rKYzaxm
            N8vZznr2s6ANrWhHS9rSmva0qE2talfL2ta69rWwja1sZ0vb2tr2trjNrW53y9ve+va3wA2u
            cIdL3OIa97jITa5yl8vc5jr3udCNrnSnS93qWve62M2udrfL3e5697vgDa94x0ve8pr3vOhN
            r3rXy972uve98I2vfOdL3/ra9774za9+98vf/vr3vwAOsIAHTOACG/jACE6wghfM4AY7+MEQ
            /hr4wRCOsIQnTOEKW/jCGM6whjfM4Q57+MMgDrGIR0ziEpv4xChOsYpXzOIWu/jFMI6xjGdM
            4xrb+MY4zrGOd8zjHvv4x0AOspCHTOQiG/nISE6ykpfM5CY7+clQjrKUp0zlKlv5yljOspa3
            zOUue/nLYA6zmMdM5jKb+cxoTrOa18zmNrv5zXCOs5znTOc62/nOeM6znvfM5z77+c+ADrSg
            B03oQhv60IhOtKIXzehGO/rRkI60pCdN6Upb+tKYzrSmN83pTnv606AOtahHTepSm/rUqE61
            qlfN6la7+tWwjrWsZ03rWtv61rjOta53zete+/rXwA62sIdN7GIb+9jITrayl83sZjv72dCO
            trSnTe1qW/va2M62trfN7W57+9vgDre4x03ucpv73OhOt7rXze52u/vd8I63vOdN73rb+974
            zre+983vfvv73wAPuMAHTvCCG/zgCE+4whfO8IY7/OEQj7jEJ07xilv84hjPuMY3zvGOe/zj
            IA+5yEdO8pKb/OQoT7nKV87ylrv85TCPucxnTvOa2/zmOM+5znfO8577/OdAD7rQh070ohv9
            6EhPutKXzvSmO/3pUI+61KdO9apb/epYz7rWt87N9ra7/e1wj7vc5073utv97njPu973zve+
            +/3vgA+84AdP+MIb/vCIT7ziF8/4xjv+8ZCPvOQnT/nKW/7ymM+85jfP+c57/vOgD73oR0/6
            0pv+9KhPvepXz/rWu/71sI+97GdP+9rb/va4z73ud8/73vv+98APvvCHT/ziG//4yE++8pfP
            /OY7//nQj770p0/96lv/+tjPvva3z/3ue//74A+/+MdP/vKb//zoT7/618/+9rv//fCPv/zn
            T//62//++M+//vfP//77//8AGIACOIAEWIAGeIAImIAKuIAM2IAO+IAQGIESOIEUWIEWeIEY
            mIEauIEc2IEe+IEgGIIiOIIkWIImeIIomIIquIIs2IIu+IIwGIMyOIM0WIM2eIM4mIM6uIM8
            2IM++INAGIRCOIREWIRGeIRImIRKuIRM2IRO+IRQGIVSOIVUWIVWeIVYmIVauIVc2IVe+IVg
            GIZiOIZkWIZmeIZomIZquIZs2IZu+IZwGIdyOId0WId2eId4mId6uId82Id++IeAGIiCOIiE
            WIiGeIiImIiKuIiM2IiO+IiQGImSOImUWImWeImYmImauImc2Ime+ImgGIqiOIqkWIqmeIqo
            mIqquIqs2Iqu+IqwGIuyOIu0WIu2eIu4mIu6uIu82Iu++IvAGIzCOIzEWIzGeIzImIzKuIzM
            2IzO+IzQGI3SOI3UWI3WeI3YmI3auI3c2I3e+I3gGI7iOI7kWI7meI7omI7quI7s2I7u+I7w
            GI/yOI/0WI/2eI/4mI/6uI/82I/++I8AGZACOZAEWZAGeZAImZAKuZAM2ZAO+ZAQGZESOZEU
            WZEWKQkBAAD7
        """)
        
        # Добавляем кадры в список
        self.dance_frames = [frame1, frame2]
    
    def animate_cat(self):
        if self.playing and not self.paused:
            # Анимация только когда музыка играет и не на паузе
            self.current_frame = (self.current_frame + 1) % len(self.dance_frames)
            self.canvas.itemconfig(self.cat_obj, image=self.dance_frames[self.current_frame])
        
        # Продолжаем анимацию
        self.root.after(self.animation_speed, self.animate_cat)
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if file_path:
            self.current_file = file_path
            self.track_label.config(text=os.path.basename(file_path))
    
    def play_music(self):
        if self.current_file:
            if self.paused:
                mixer.music.unpause()
                self.paused = False
            else:
                mixer.music.load(self.current_file)
                mixer.music.play()
                self.playing = True
            self.animation_speed = 100  # Быстрая анимация при воспроизведении
    
    def pause_music(self):
        if self.playing and not self.paused:
            mixer.music.pause()
            self.paused = True
            self.animation_speed = 500  # Медленная анимация на паузе
    
    def stop_music(self):
        mixer.music.stop()
        self.playing = False
        self.paused = False
        self.animation_speed = 1000  # Очень медленная анимация при остановке
    
    def set_volume(self, val):
        volume = float(val) / 100
        mixer.music.set_volume(volume)

def main():
    root = Tk()
    app = BoykisserPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()