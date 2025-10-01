import time
from tkinter.font import names


class animal:
    type = "Животное"
    def __init__(self,  sex, lifetime , Type = "Базовое"):
        self.selfType = Type
        self.born = time.time()
        self.age = 0
        self.Sex = sex
        self.state = "Живой"
        self.lifetime = lifetime
        print(f"создано новое {self.type}:{self.selfType}, {self.Sex}")

    def check(self):
        if self.state == "Живой":
            print(f"{self.type}: {self.selfType}, {self.Sex}, {self.age} дней")

            if self.age > self.lifetime:
                self.state = "Умер"
        else:
            print(f"{self.type}: {self.selfType}, {self.Sex}, {self.state}")
    def living(self):
        self.age = time.time() - self.born


class hamster(animal):

    def __init__(self, sex ,name):
        super().__init__(sex, 50, "Хомячок")
        self.name = name

    def check(self):
        print(self.name)
        super().check()


import random
names = ["Тимофей", "Пенек", "Валера", "Жигули", "Сонечка"]
s = ["Мальчик", "Девочка"]
cage = []
while True:
    move = input("1 - проверить всех, 2 - создать хомячка, 3 - выход")
    if move == "1":
        for a in cage:
            a.check()
            a.living()
    if move == "2":
        cage.append(hamster(sex = s[random.randint(0,1)], name = names[random.randint(0,4)]))
        for a in cage:
            a.living()
    if move == "3":
        break