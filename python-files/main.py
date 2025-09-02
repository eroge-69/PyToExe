from turtle import shape, Screen
from player import Player


IMG = "/home/pisut/Belgeler/kisisel/program-ogrenme/python-angela/25_csv-pandas/oyun_il-tahmin/tr.gif"


def kent_tahmin(x, y):
    player.goto(x,y)
    for i in player.kent_liste:
        if player.distance(player.data.x[player.data.kent == i].iloc[0], player.data.y[player.data.kent == i].iloc[0]) < 10:
            tahmin_kent = screen.textinput(f"Doğru cevap sayısı: {player.dogru_cevap}", f"{player.data.hint[player.data.kent == i].iloc[0]}")
            player.cevap_kontrol(tahmin_kent, player.data.x[player.data.kent == i].iloc[0], player.data.y[player.data.kent == i].iloc[0])
            

screen = Screen()
screen.title("Türkiye İlleri")
screen.addshape(IMG)
harita = shape(IMG)
player = Player()


screen.onclick(kent_tahmin)


screen.mainloop()