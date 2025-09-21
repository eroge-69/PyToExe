from tkinter import *
import json
from PIL import Image, ImageTk


herbal_color = "#630204"
herbal_btn_color = '#2D0001'
black_color = '#3F2C0E'
black_btn_color = '#191105'
green_color = '#50D93D'
green_btn_color = '#0B3D07'
oolong_color = '#BAD5B7'
oolong_btn_color = '#3E6E3D'
head_color = '#104209'
bg_color = '#061C03'
    

def add_tea():
    file = open('data.json', 'r')
    tea_collection = json.load(file)
    file.close

    file = open('data.json', 'w')
    name = input('name')
    quantity = input('quantity')
    type_of_tea = input('type')
    seller = input('seller')
    
    tea_collection.append([{'name': name}, {'quantity': quantity}, {'type_of_tea': type_of_tea}, {'seller': seller}])
    json.dump(tea_collection, file, indent = 1)
    file.close
    print('got it!')
    return tea_collection


def choose_herbal_tea():
    tea_slot(herbal_color, herbal_btn_color, 63, 100, 'E:\my_tea_library\herbal_tea_pics\strawberry_garden.png', 'Strawberry Garden')
    tea_slot(herbal_color, herbal_btn_color, 413, 100, 'E:\my_tea_library\herbal_tea_pics\cherry_blossom.png', 'Cherry Blossom')
    tea_slot(herbal_color, herbal_btn_color, 763, 100, 'E:\my_tea_library\herbal_tea_pics\summer_bouquet.png', 'Summer Bouquet')
    tea_slot(herbal_color, herbal_btn_color, 1113, 100, 'E:\my_tea_library\herbal_tea_pics\oberry_sunset.png', 'Berry Sunset')
    tea_slot(herbal_color, herbal_btn_color, 1463, 100, 'E:\my_tea_library\herbal_tea_pics\ofestive_grape.png', 'Festive Grape')
    tea_slot(herbal_color, herbal_btn_color, 63, 482, 'E:\my_tea_library\herbal_tea_pics\orich_camomile.png', 'Rich Camomile')
    tea_slot(herbal_color, herbal_btn_color, 413, 482, 'E:\my_tea_library\herbal_tea_pics\spirit_mate.png', 'Spirit Mate')
    tea_slot(herbal_color, herbal_btn_color, 763, 482, 'E:\my_tea_library\herbal_tea_pics\wildberry_rooibos.png', 'Wildberry Rooibos')
    tea_slot(herbal_color, herbal_btn_color, 1113, 482, 'E:\my_tea_library\herbal_tea_pics\camomile_meadow.png', 'Camomile Meadow')
    plug_slot('E:\my_tea_library\herbal_tea_pics\plug_0.png', 1463, 482)

def choose_black_tea():
    tea_slot(black_color, black_btn_color, 63, 100, 'E:\my_tea_library\dark_tea_pics\obarberry_garden.png', 'Barberry Garden')
    tea_slot(black_color, black_btn_color, 413, 100, 'E:\my_tea_library\dark_tea_pics\oblueberry_nights.png', 'Blueberry Nights')
    tea_slot(black_color, black_btn_color, 763, 100, 'E:\my_tea_library\dark_tea_pics\christmas_mistery.png', 'Christmas Mistery')
    tea_slot(black_color, black_btn_color, 1113, 100, 'E:\my_tea_library\dark_tea_pics\currant_mint.png', 'Currant & Mint')
    tea_slot(black_color, black_btn_color, 1463, 100, 'E:\my_tea_library\dark_tea_pics\gourmand_pear.png', 'Gourmand Pear')
    tea_slot(black_color, black_btn_color, 63, 482, 'E:\my_tea_library\dark_tea_pics\grand_fruit.png', 'Grand Fruit')
    tea_slot(black_color, black_btn_color, 413, 482, 'E:\my_tea_library\dark_tea_pics\lemon_spark.png', 'Lemon Spark')
    tea_slot(black_color, black_btn_color, 763, 482, 'E:\my_tea_library\dark_tea_pics\oriental_lime.png', 'Oriental Lime')
    tea_slot(black_color, black_btn_color, 1113, 482, 'E:\my_tea_library\dark_tea_pics\spring_melody.png', 'Spring Melody')
    tea_slot(black_color, black_btn_color, 1463, 482, 'E:\my_tea_library\dark_tea_pics\strawberry_bloom.png', 'Strawberry Bloom')

def choose_green_tea():
    tea_slot(green_color, green_btn_color, 63, 100, 'E:\my_tea_library\green_tea_pics\citrus_breeze.png', 'Citrus Breeze')
    tea_slot(green_color, green_btn_color, 413, 100, 'E:\my_tea_library\green_tea_pics\green_melissa.png', 'Green Melissa')
    tea_slot(green_color, green_btn_color, 763, 100, 'E:\my_tea_library\green_tea_pics\mellow_peach.png', 'Mellow Peach')
    plug_slot('E:\my_tea_library\green_tea_pics\plug_1.png', 1113, 100)
    plug_slot('E:\my_tea_library\green_tea_pics\plug_2.png', 1463, 100)
    plug_slot('E:\my_tea_library\green_tea_pics\plug_3.png', 63, 482)
    plug_slot('E:\my_tea_library\green_tea_pics\plug_4.png', 413, 482)
    plug_slot('E:\my_tea_library\green_tea_pics\plug_5.png', 763, 482)
    plug_slot('E:\my_tea_library\green_tea_pics\plug_6.png', 1113, 482)
    plug_slot('E:\my_tea_library\green_tea_pics\plug_7.png', 1463, 482)

def choose_oolong_tea():
    tea_slot(oolong_color, oolong_btn_color, 63, 100, 'E:\my_tea_library\oolong_tea_pics\spicy_mango.png', 'Spicy Mango')
    tea_slot(oolong_color, oolong_btn_color, 413, 100, 'E:\my_tea_library\oolong_tea_pics\otropical_tarragon.png', 'Tropical Tarragon')
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_0.png', 763, 100)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_1.png', 1113, 100)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_2.png', 1463, 100)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_3.png', 63, 482)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_4.png', 413, 482)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_5.png', 763, 482)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_6.png', 1113, 482)
    plug_slot('E:\my_tea_library\oolong_tea_pics\plug_7.png', 1463, 482)


def tea_slot(bg_color, btn_color, x_place, y_place, pic, name_of_tea):
    
    def plus_quantity(name_of_tea):
        file = open('data.json', 'r')
        tea_collection = json.load(file)
        file.close

        for tea in tea_collection:
            if tea[0]['name'] == name_of_tea:
                global quantity_of_tea
                quantity_of_tea = int(tea[1]['quantity']) + 1
                tea[1]['quantity'] = quantity_of_tea
                quantity_label.config(text = quantity_of_tea)
                break
                

        file = open('data.json', 'w')
        json.dump(tea_collection, file, indent = 1)
        file.close

    def minus_quantity(name_of_tea):
        file = open('data.json', 'r')
        tea_collection = json.load(file)
        file.close

        for tea in tea_collection:
            if tea[0]['name'] == name_of_tea:
                global quantity_of_tea
                quantity_of_tea = int(tea[1]['quantity']) - 1
                tea[1]['quantity'] = quantity_of_tea
                quantity_label.config(text = quantity_of_tea)
                break
                

        file = open('data.json', 'w')
        json.dump(tea_collection, file, indent = 1)
        file.close

    new_frame = Frame(root, bg = bg_color)
    new_frame.place(width = 300, height = 350, x = x_place, y = y_place)
    img = Image.open(pic) 
    tea_pic = ImageTk.PhotoImage(img)
    label = Label(new_frame, image=tea_pic, bg=bg_color)
    label.image = tea_pic 
    label.place(x=66, y=7)

    file = open('data.json', 'r')
    tea_collection = json.load(file)
    file.close

    for tea in tea_collection:
        if tea[0]['name'] == name_of_tea:
            quantity_of_tea = int(tea[1]['quantity'])
            break
        else:
            quantity_of_tea = 'N/A'

    quantity_label = Label(new_frame, text = quantity_of_tea, bg = btn_color, fg = 'white', font = ('Babelfish', 36))
    quantity_label.place(width = 150, height = 42, x = 75, y = 295)
    add_plus_btn = Button(new_frame, text = '+', bg = btn_color, fg = 'white', font = ('Babelfish', 36), command = lambda: plus_quantity(name_of_tea))
    add_plus_btn.place(width = 50, height = 325, x = 235, y = 12)

    add_minus_btn = Button(new_frame, text = '-', bg = btn_color, fg = 'white', font = ('Babelfish', 36), command = lambda: minus_quantity(name_of_tea))
    add_minus_btn.place(width = 50, height = 325, x = 15, y = 12)

def navigate():
    head_label = Label(root, bg = head_color)
    head_label.place(width = 1826, height = 70, x = 0, y = 0)

    black_tea_btn = Button(head_label, text = 'Black Tea', bg = bg_color, fg = 'white', font = ('Babelfish', 18), command = lambda: choose_black_tea())
    black_tea_btn.place(width = 400, height = 70, x = 0, y = 0)
    green_tea_btn = Button(head_label, text = 'Green Tea', bg = bg_color, fg = 'white', font = ('Babelfish', 18), command = lambda: choose_green_tea())
    green_tea_btn.place(width = 400, height = 70, x = 474, y = 0)
    oolong_tea_btn = Button(head_label, text = 'Oolong Tea', bg = bg_color, fg = 'white', font = ('Babelfish', 18), command = lambda: choose_oolong_tea())
    oolong_tea_btn.place(width = 400, height = 70, x = 950, y = 0)
    herbal_tea_btn = Button(head_label, text = 'Herbal Tea', bg = bg_color, fg = 'white', font = ('Babelfish', 18), command = lambda: choose_herbal_tea())
    herbal_tea_btn.place(width = 400, height = 70, x = 1423, y = 0)

def plug_slot(pic, x_place, y_place):
    new_frame = Frame(root, bg = bg_color)
    new_frame.place(width = 300, height = 350, x = x_place, y = y_place)
    img = Image.open(pic) 
    tea_pic = ImageTk.PhotoImage(img)
    label = Label(new_frame, image=tea_pic, bg=bg_color)
    label.image = tea_pic 
    label.place(x=x_place, y=y_place)

root = Tk()
root.geometry('1826x900')


bg_frame = Frame(root, bg = bg_color)
bg_frame.place(width = 1826, height = 900)

navigate()


root.mainloop()