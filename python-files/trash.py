import random

class PlayerStats:
    def __init__(self):
        self.d = 55.0
        self.c = 17.0
        self.b = 11.0
        self.a = 7.0
        self.s1 = 6.0
        self.s2 = 4.0

        self.money = 0.0
        self.scan = 20.0
        self.driving = 20.0
        self.break_in = 20.0
        self.hot_wire = 20.0
        self.strength = 20.0
        self.agility = 20.0
        self.level = .0
        self.sell = 0.0
        self.success = 0.0

        self.response_time = 150.0
        self.scan_correct = False
        self.car_stolen = ""
        self.tutorial = False
        self.cops_called = False


class CarDatabase:
    def __init__(self):
        self.Lots = [
            "Galloway Parking Garage", "Medley's Medicine", "Gary's Repair & Garage", "Leckers Ave Parking",
            "Pay to Park", "Lizzie's Bar & Grill", "Cinema 16", "Murph's Parking Garage", "Shelly's Botique & Flower Shop", "Fuck City Bank", "Korger", "Fuck City General Hospital"
        ]

        self.d_cars = ["Volkswagen: Golf GTI, 1983", "Toyota: Land Cruiser AT37, 2016", "Talbot: Sunbeam Lotus, 1979", "Pontiac: Trans AM, 1977","Nissan: Titan Warrior, 2016", "Mazda: MX-5 Miata, 1994", "Jeep: Wrangler Rubicon, 2012", "Honda: Civic RS, 1974", "GMC: Vandura G-1500, 1983", "Ford: Transit, 2011", "Ford: Bronco, 1975", "Abarth: Fiat 131, 1980"]
        self.c_cars = ["Acura: RSX Type-S, 2002", "BMW: M5, 1998", "Buick: Regal GNX, 1987", "Chevrolet: Impala, 2001", "Dodge: Charger, 1989", "Ford: Escort Cosworth, 1992", "Honda: Civic Type-R, 2007", "Mazda: MX-5, 2013", "Mercedes: Evolution, 1990", "Mitsubishi: Eclipse GSX, 1995", "Nissan: Sentra Nismo, 2018", "Renault: Clio RS, 2010", "Subaru: BRZ, 2013", "Toyota: Hilux AT38, 2007"]
        self.b_cars = ["Fiat: 695 Biposto, 2016", "Audi: RS 4 Avant, 2001", "Audi: S1, 2015", "BMW: M3, 1997", "Chevrolet: Corvette ZR-1, 1970", "Ford: F-150 Raptor, 2017", "Ford: Focus RS, 2009", "Ford: Fiesta ST, 2014", "Honda: S2000 CR, 2009", "Hyundai: Veloster N, 2019", "Mazda: Mazda Speed MX-5, 2005", "Mini: Cooper, 2011", "Mitsubishi: Lancer, 2008", "Mitsubishi: Evolution, 2006", "Nissan: Fairlady Z, 2003", "Subaru: WRX STI, 2015"]
        self.a_cars = ["Alfa Romeo: 4C, 2014", "Audi: TTS Coupe, 2015", "BMW: X5 M, 2011", "Cadillac: ATS-V, 2016", "Chevrolet: Corvette Z06, 2002", "Dodge: Charger, 2015", "Ford: Mustang GT, 2018", "Honda: Civic Type-R, 2015", "Infiniti: Rogue, 2014", "Kia: Stinger, 2018", "Land Rover: Range Rover, 2015", "Mercedes: C 63 S, 2016", "Porsche: 911, 2012"]
        self.s1_cars = ["Acura: NSX, 2017", "Aston Martin: Vantage, 2018", "Audi: R8 V10 Plus, 2016", "BMW: M4 GTS, 2016", "Chevrolet: Corvette ZR1, 2019", "Dodge: Viper ACR, 2016", "Ferrari: 599 GTO, 2010", "Lamborghini: Aventador, 2012"]
        self.s2_cars = ["Bugatti: Chiron, 2018", "Ferrari: F12TDF, 2015", "Koenigsegg: Agera RS, 2017", "Lamborghini: Centinario, 2016", "McLaren: Senna, 2018", "Pagani: Huayra, 2016", "Porsche: 918 Spyder, 2014", "Aston Martin: Vulcan, 2016"]


class GameMechanics:
    def __init__(self, stats: PlayerStats, db: CarDatabase, up: 'Upgrades', ct: 'Contacts', game: 'CityGame'):
        self.stats = stats
        self.db = db
        self.ct = ct
        self.up = up
        self.game = game
        
    def pick_lot(self):
        if self.stats.tutorial:
            print("\nLet's go steal you your first car.\nFirst you need to pick a place.")
        random_lot = random.sample(self.db.Lots, 4)
    
        while True:
            print("\nPick a parking lot (1-4).\n")
            for i, lot in enumerate(random_lot, 1):
                print(f"{i}. {lot}")
            lot_picked = input("\n")
            if lot_picked in ["1", "2", "3", "4"]:
                print(f"\nLot Picked: {random_lot[int(lot_picked) - 1]}\n")
                break
            else:
                print("\nEnter (1-4) dickhead.")
    
        self.pick_car()

        
    def pick_car(self):
        if self.stats.tutorial:
            print("Now you need to make a real\ndecision. Every car has a different\nprice point. So when choosing a car,\nlook at things like brand, model,\nand year to try and get a higher\nvalue car.\n")

        car_list = []
        selected_cars = set()

        for _ in range(4):
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                rand = random.random() * 100
                selected_car = None
                if rand < self.stats.d and self.db.d_cars:
                        available_cars = [car for car in self.db.d_cars if car not in selected_cars]
                        if available_cars:
                            selected_car = random.choice(available_cars)
                elif rand < self.stats.d + self.stats.c and self.db.c_cars:
                    available_cars = [car for car in self.db.c_cars if car not in selected_cars]
                    if available_cars:
                        selected_car = random.choice(available_cars)
                elif rand < self.stats.d + self.stats.c + self.stats.b and self.db.b_cars:
                    available_cars = [car for car in self.db.b_cars if car not in selected_cars]
                    if available_cars:
                        selected_car = random.choice(available_cars)
                elif rand < self.stats.d + self.stats.c + self.stats.b + self.stats.a and self.db.a_cars:
                    available_cars = [car for car in self.db.a_cars if car not in selected_cars]
                    if available_cars:
                        selected_car = random.choice(available_cars)
                elif rand < self.stats.d + self.stats.c + self.stats.b + self.stats.a + self.stats.s1 and self.db.s1_cars:
                        available_cars = [car for car in self.db.s1_cars if car not in selected_cars]
                        if available_cars:
                            selected_car = random.choice(available_cars)
                elif self.db.s2_cars:
                    available_cars = [car for car in self.db.s2_cars if car not in selected_cars]
                    if available_cars:
                        selected_car = random.choice(available_cars)
                    
                attempts += 1
                
                if selected_car and selected_car not in selected_cars:
                    car_list.append(selected_car)
                    selected_cars.add(selected_car)
                    break
                       
            if len(car_list) < len(selected_cars) - 1:
                fallback_cars = [car for car in self.db.d_cars if car not in selected_cars]
                if fallback_cars:
                    selected_car = random.choice(fallback_cars)
                    car_list.append(selected_car)
                    selected_cars.add(selected_car)        
                    
        while len(car_list) < 4:
            car_list.append(random.choice(self.db.d_cars1))            
                
        while True:
            print("Pick a car to boost (1-4).\n")
            for i, car in enumerate(car_list, 1):
                print(f"{i}. {car}")
            car_picked = input("\n")
            if car_picked in ["1", "2", "3", "4"]:
                selected_car = car_list[int(car_picked) - 1]
                self.stats.car_stolen = selected_car
                print(f"\nCar Picked:\n{selected_car}")
                break
            else:
                print("\nEnter (1-4) dickhead.\n")
        self.run_scan()        
        
    def run_scan(self):
        if self.stats.tutorial:
            print("\nYour scanner is like sonar.\nIt scans the area and tells you\nif a witness is present. If someone\nis watching, scan again. But it\ncan malfunction and miss witnesses,\nif a witness is present while\nbreaking in they'll call the cops.")
            self.stats.scan += 90.0

        while True:
            witness_present = random.choice([True, False])
            scan_result = random.random() < (self.stats.scan/100)
            scan_button = input("\nEnter Scan: ")
        
            if scan_button.lower() != "scan":
                print("\nType 'Scan' fuck face!")
                continue

            if self.stats.scan >= 100.0:
                print("\nWitness Present: " + str(witness_present))
                if not witness_present:
                    self.stats.scan_correct = True
                    self.up.upgrade_points += 1.0
                    break
            elif scan_result == witness_present:
                print("\nWitness Present: " + str(witness_present))
                if not scan_result:
                    self.stats.scan_correct = True
                    self.up.upgrade_points += 1.0
                    break
            else:
                print("\nWitness Present: " + str(scan_result))
                if not scan_result:
                    self.stats.scan_correct = False
                    break

        self.breaking_in()
    
    def breaking_in(self):
        if self.stats.tutorial:
            print("\nIf your 'Break In' skill is higher\nthan 30, you can jimmie locks. This\navoids car alarms, which cause\npasserby's to call the cops. For\nthis tutorial, I've maxed out all\nof your skills.")        
            self.stats.break_in += 90.0

        while True:
            commit = input("\nEnter Break In: ")
            if commit.lower() == "break in":
                break
            print("\nType 'Break In' you fucking moron.")

        if self.stats.break_in >=50.0:
            if random.random() < (self.stats.break_in / 100):
                print("\nYou successfully jimmied the lock.")
                self.up.upgrade_points += 1.0
            else:
                while True:
                    try_again = input("\nYou did not jimmy the lock. \nTry again? \n")
                    if try_again.lower() == "yes":
                        return self.breaking_in()
                    else:
                        return self.game.home()
        else:
            if random.random() < 0.9:
                if random.random() < (self.stats.break_in / 100):
                    print("\nYou broke the window without \nsetting off the alarm.")
                else:
                    print("\nYou broke the window, but tripped \nthe alarm.")
                    print("\nA passerby heard the alarm go off.")
                    self.call_cops()
                self.up.upgrade_points += 1.0
            else:
                print("\nYour weak little arms could not \nsmash through the window.")
                return self.breaking_in()

        if not self.stats.scan_correct and not self.stats.cops_called:
            print("\nYour scanner malfunctioned, there \nwas a witness you couldn't see.")
            self.call_cops()

        self.hot_wiring()
        
    def hot_wiring(self):
        if self.stats.tutorial:
            print("\nIf you've been caught by now, and\nthe witness called the cops; then\nevery time you attempt to hot wire, \nthe cops get closer.")
            self.stats.hot_wire += 90.0
            attempts = 0

        while True:
            if attempts <= 8:
                spark = input("\nEnter Hot Wire: ")
                if spark.lower() != "hot wire":
                    print("\nType 'Hot Wire' doofus.")
                    continue
                if random.random() < (self.stats.hot_wire / 100):
                    print("\nYou hot wired the ride.\n")
                    self.up.upgrade_points += 1.0
                    break
                else:
                    print("\nYou couldn't hot wire this ride.")
                    attempts += 1
                    if self.stats.cops_called:
                        self.stats.response_time -= 20.0
                        self.call_jail()
            else:
                print("\nYou hot wired the ride.\n")
                break

        self.drive_off()
        
    def drive_off(self):
        if self.stats.tutorial:
            print("When driving off, there is a chance\nyou can crash. Then it's up to your\nagility to try and get away before\nthe cops show up.\n")    
            self.stats.driving += 90.0

        while True:
            gas = input("Enter Drive Off: ")
            if gas.lower() == "drive off":
                break
            print("\nJust fucking type \n'Drive Off' asshole.\n")

        if random.random() < (self.stats.driving / 100):
            print(f"\n{self.stats.car_stolen} \nsuccessfully boosted.")
            self.up.upgrade_points += 1.0
            self.stats.level += 1.0
            return self.game.home()
        else:
            print(f"\n{self.stats.car_stolen} \nwrecked.\n")
            agility_outcome = random.random() < (self.stats.agility/100)
            while True:
                run_away = input("Run: ")
                if run_away.lower() == "run":
                    if agility_outcome:
                        print("\nYou got away before the cops came.")
                        self.stats.level += 1.0
                    else:
                        print("\nYou took too long to flee the \nscene. The cops arrived \nand found you.\n")
                        return self.jail()
                    return self.game.home()
                else:
                    print("\nFucking type run already!\n")
                    
    def call_cops(self):
        response_time = (150.0 - self.stats.response_time)
        self.stats.response_time += response_time
        if not self.stats.cops_called:
            self.stats.cops_called = True
        strength_outcome = random.random() < (self.stats.strength/100)
        choice_witness = input(
            "\nA witness is calling the cops! \n1. Beat Witness. \n2. Run Away. \n3. Ignore.\n \n")
        if choice_witness == "1":
            if strength_outcome == True:
                print("\nYou knocked out the witness.")
                self.up.upgrade_points += 1.0
                self.breaking_in()
            else:
                print("\nThe witness pummeled you.\n")
                self.stats.response_time -= 150.0
                self.call_jail()
                
        elif choice_witness == "2":
            print("\nYou got away before \nthe cops arrived.")
            self.up.upgrade_points += 1.0
            self.game.home()
        else:
            self.stats.response_time -= 10.0
            self.call_jail()
            
    def call_jail(self):
        if self.stats.response_time <= 0.0:
            response_time = (150.0 - self.stats.response_time)
            self.stats.response_time += response_time
            print("You took too long.\nThe cops arrived.\n")
            self.jail()
            
    def scan_big(self):
        if self.stats.scan <= 20.0:
            self.break_big()
        else:
            self.stats.scan -= 2.0
            self.break_big()
            
    def break_big(self):
        if self.stats.break_in <= 20.0:
            self.hot_big()
        else:
            self.stats.break_in -= 2.0
            self.hot_big()
            
    def hot_big(self):
        if self.stats.hot_wire <= 20.0:
            self.drive_big()
        else:
            self.stats.hot_wire -= 2.0
            self.drive_big()
            
    def drive_big(self):
        if self.stats.driving <= 20.0:
            self.strength_big()
        else:
            self.stats.driving -= 2.0
            self.strength_big()
            
    def strength_big(self):
        if self.stats.strength <= 20.0:
            self.agility_big()
        else:
            self.stats.strength -= 2.0
            self.agility_big()
            
    def agility_big(self):
        if self.stats.agility <= 20.0:
            self.game.home()
        else:
            self.stats.agility -= 2.0
            self.game.home()
            
    def jail(self):
        print("You went to jail, loser.")
        if self.stats.money >= 1000:
            print("\nYou could afford the $1000 bail.\n$1000 has been subtracted\nfrom your account.")
            self.stats.money -= 1000
            self.game.home()
        else:
            print("\nYou couldn't afford the $1000 bail.\n \nYou spent 1 month in jail.\nAll of your skills decreased\nby 2 due to lack of practice.")
            self.scan_big()
            
class Contacts:
    def __init__(self, stats: PlayerStats, db: CarDatabase, game):
        self.contact_list = ["1. Hanna", "Complete the tutorial first.", "2. Diya", "Reach level 10 to unlock.", "3. Ali", "Reach level 20 to unlock.", "4. Charles", "Reach level 30 to unlock.", "5. Gabriel", "Reach level 40 to unlock.", "6. Jola", "Reach level 50 to unlock.", "7. Lucille", "Reach level 60 to unlock.", "8. David", "Reach level 70 to unlock.", "9. Rinaldo", "Reach level 80 to unlock.", "10. Haris", "Reach level 90 to unlock.", "11. Giove", "Reach level 100 to unlock."]
        self.stats = stats
        self.db = db
        self.game = game
        
    def hanna(self):
        if self.stats.level >= 1.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(500, 1000)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(700, 1300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(900, 1500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(1100, 1700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(1400, 2000)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(1700, 2300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[1]}")
            print("Exiting game.")
            return
            
    def diya(self):
        if self.stats.level >= 10.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(700, 1200)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(900, 1500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(1100, 1700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(1300, 1900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(1600, 2200)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(1900, 2500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[3]}")
            self.contacts()
    
    def ali(self):
        if self.stats.level >= 20.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(900, 1400)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(1100, 1700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(1300, 1900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(1500, 2100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(1800, 2400)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(2100, 2700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[5]}")
            self.contacts()
            
    def charles(self):
        if self.stats.level >= 30.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(1100, 1600)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(1300, 1900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(1500, 2100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(1700, 2300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(2000, 2600)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(2300, 2900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[7]}")
            self.contacts()
            
    def gabriel(self):
        if self.stats.level >= 40.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(1300, 1800)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(1500, 2100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(1700, 2300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(1900, 2500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(2200, 2800)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(2500, 3100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[9]}")
            self.contacts()
            
    def jola(self):
        if self.stats.level >= 50.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(1500, 2000)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(1700, 2300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(1900, 2500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(2100, 2700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(2400, 3000)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(2700, 3300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[11]}")
            self.contacts()
        
    def lucille(self):
        if self.stats.level >= 60.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(1700, 2200)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(1900, 2500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(2100, 2700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(2300, 2900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(2600, 3200)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(2900, 3500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[13]}")
            self.contacts()
        
    def david(self):
        if self.stats.level >= 70.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(1900, 2400)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(2100, 2700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(2300, 2900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(2500, 3100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(2800, 3400)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(3100, 3700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[15]}")
            self.contacts()
        
    def rinaldo(self):
        if self.stats.level >= 80.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(2100, 2600)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(2300, 2900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(2500, 3100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(2700, 3300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(3000, 3600)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(3300, 3900)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[17]}")
            self.contacts()
        
    def haris(self):
        if self.stats.level >= 90.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(2300, 2800)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(2500, 3100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(2700, 3300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(2900, 3500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(3200, 3800)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(3500, 4100)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[19]}")
            self.contacts()
        
    def giove(self):
        if self.stats.level >= 100.0:
            if self.stats.car_stolen in self.db.d_cars:
                reward = random.randint(2500, 3000)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.c_cars:
                reward = random.randint(2700, 3300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.b_cars:
                reward = random.randint(2900, 3500)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.a_cars:
                reward = random.randint(3100, 3700)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s1_cars:
                reward = random.randint(3400, 4000)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()
            elif self.stats.car_stolen in self.db.s2_cars:
                reward = random.randint(3700, 4300)
                self.stats.money += reward
                print(f"\nCongratulations, you sold \n{self.stats.car_stolen}\nfor ${reward}.")
                self.game.home()    
        else:
            print(f"\n{self.contact_list[21]}")
            self.contacts()
    
    def contacts(self):
        contact = input(f"\nContacts:\n{self.contact_list[0]}\n{self.contact_list[2]}\n{self.contact_list[4]}\n{self.contact_list[6]}\n{self.contact_list[8]}\n{self.contact_list[10]}\n{self.contact_list[12]}\n{self.contact_list[14]}\n{self.contact_list[16]}\n{self.contact_list[18]}\n{self.contact_list[20]}\n\n")
        if self.stats.car_stolen:
            if contact == "1":
                self.hanna()
            elif contact == "2":
                self.diya()
            elif contact == "3":
                self.ali()
            elif contact == "4":
                self.charles()
            elif contact == "5":
                self.gabriel()
            elif contact == "6":
                self.jola()
            elif contact == "7":
                self.lucille()
            elif contact == "8":
                self.david()
            elif contact == "9":
                self.rinaldo()
            elif contact == "10":
                self.haris()
            elif contact == "11":
                self.giove()
            elif contact.lower() == "home":
                self.game.home()
            else:
                print("\nEnter (1-11) or 'home'.")
                self.contacts()
        else:
            print("\nYou do'nt have any cars to sell.")
            self.contacts()
            
class Upgrades:
    def __init__(self, stats: PlayerStats, game):
        self.upgrade_points = 0.0
        self.stats = stats
        self.game = game
        
    def upgrade(self):
        while True:
            upgrade = input(f"\nUpgrades:      Upgrade Points: {int(self.upgrade_points)}\n \n1. Scanner: {int(self.stats.scan - 20.0)}/80 \n2. Strength: {int(self.stats.strength - 20.0)}/80 \n3. Agility: {int(self.stats.agility - 20.0)}/80 \n4. Break In: {int(self.stats.break_in - 20.0)}/80 \n5. Hot Wire: {int(self.stats.hot_wire - 20.0)}/80 \n6. Driving: {int(self.stats.driving - 20.0)}/80\n\n")
        
            if upgrade == "1":
                if self.upgrade_points > 0 and self.stats.scan < 100:
                    self.stats.scan += 1.0
                    self.upgrade_points -= 1.0
                elif self.stats.scan >= 100:
                    print("This skill has been maxed out.")
                else:
                    print("\nAre you dumb? You got \nno upgrade points.")
            elif upgrade == "2":
                if self.upgrade_points > 0 and self.stats.strength < 100:
                    self.stats.strength += 1.0
                    self.upgrade_points -= 1.0
                elif self.stats.strength >= 100:
                    print("This skill has been maxed out.")
                else:
                    print("\nAre you dumb? You got \nno upgrade points.")
            elif upgrade == "3":
                if self.upgrade_points > 0 and self.stats.agility < 100:
                    self.stats.agility += 1.0
                    self.upgrade_points -= 1.0
                elif self.stats.agility >= 100:
                    print("This skill has been maxed out.")
                else:
                    print("\nAre you dumb? You got \nno upgrade points.")
            elif upgrade == "4":
                if self.upgrade_points > 0 and self.stats.break_in < 100:
                    self.stats.break_in += 1.0
                    self.upgrade_points -= 1.0
                elif self.stats.break_in >= 100:
                    print("This skill has been maxed out.")
                else:
                    print("\nAre you dumb? You got \nno upgrade points.")
            elif upgrade == "5":
                if self.upgrade_points > 0 and self.stats.hot_wire < 100:
                    self.stats.hot_wire += 1.0
                    self.upgrade_points -= 1.0
                elif self.stats.hot_wire >= 100:
                    print("This skill has been maxed out.")
                else:
                    print("\nAre you dumb? You got \nno upgrade points.")
            elif upgrade == "6":
                if self.upgrade_points > 0 and self.stats.driving < 100:
                    self.stats.driving += 1.0
                    self.upgrade_points -= 1.0
                elif self.stats.driving >= 100:
                    print("This skill has been maxed out.")
                else:
                    print("\nAre you dumb? You got \nno upgrade points.")
            elif upgrade.lower() == "home":
                return self.game.home()
            else:
                print("\nEnter a valid command you \nlousy fuck.")
                
class CityGame:
    def __init__(self):
        self.stats = PlayerStats()
        self.db = CarDatabase()
        self.ct = Contacts(self.stats, self.db, self)
        self.up = Upgrades(self.stats, self)
        self.mechanics = GameMechanics(self.stats, self.db, self.up, self.ct,self)

    def run(self):
        self.welcome()

    def welcome(self):
        print("Welcome to Fuck City! Where only \nthe dirtiest and slimiest survive.\n")
        enter = input("Press Enter to continue.")
        if enter == "":
            self.tut()
        else:
            print("Exiting game.")
            return

    def tut(self):
        self.stats.tutorial = True
        self.mechanics.pick_lot()

    def home(self):
        if self.stats.tutorial:
            tutorial_steps = [
                "\nHere you will see all the \nthings you can do. \nTo pick one, enter a number (1-6). \n\nHome         Level: 1\n\n1. Contacts \n2. Upgrades \n3. Auction \n4. City \n5. Stock Market \n6. Businesses \n\nI'll walk you through them. \nPress Enter to continue. \n",
                f"\nThis is where you sell\nthe cars that you steal.\nPick (1-11) to call.\n\nContacts:\n{self.ct.contact_list[0]}\n{self.ct.contact_list[2]}\n{self.ct.contact_list[4]}\n{self.ct.contact_list[6]}\n{self.ct.contact_list[8]}\n{self.ct.contact_list[10]}\n{self.ct.contact_list[12]}\n{self.ct.contact_list[14]}\n{self.ct.contact_list[16]}\n{self.ct.contact_list[18]}\n{self.ct.contact_list[20]}\n\nPress Enter to continue. \n",
                "This is where you can\nupgrade your skills. \nDo this by picking (1-6).\n\nUpgrades:      Upgrade Points: 0\n\n1. Scanner: 80/80 \n2. Strength: 80/80 \n3. Agility: 80/80 \n4. Break In: 80/80 \n5. Hot Wire: 80/80 \n6. Driving: 80/80\n\nPress Enter to continue.\n",
                "Auction House:\n\nAuction house will be here. \nPress Enter to continue. \n",
                "City:\n\nThis will take you to the city, \nto boost cars like you just did.\nYou can only steal and sell\none car at a time. If you\nattempt to steal another\ncar before you sell the one \nyou have,the previous car \nwill be disposed of.\nPress Enter to continue. \n",
                "Stock Market:\n\nThe stock market will be here. \nPress Enter to continue. \n",
                "Businesses:\n\nPurchaseable businesses \nwill be here. \nPress Enter to continue."
            ]
        
            i = 0
            while i < len(tutorial_steps):
                response = input(tutorial_steps[i])
                if response.strip() == "":
                    i += 1  # move to the next step
                else:
                    print("\nJust press Enter you fucking doofus.\n")

            # Reset tutorial state after tutorial finishes
            self.stats.scan -= 90.0
            self.stats.break_in -= 90.0
            self.stats.hot_wire -= 90.0
            self.stats.driving -= 90.0
            self.stats.tutorial = False

        # Show main home menu after tutorial or if tutorial skipped
        print(f"\nHome             Level: {int(self.stats.level)}\n                Money: ${int(self.stats.money)}\n1. Contacts \n2. Upgrades \n3. Auction \n4. City \n5. Stock Market \n6. Businesses")
        destination = input("\n")
        if destination == "1":
            self.ct.contacts()
        elif destination == "2":
            self.up.upgrade()
        elif destination == "3":
            print("\nIncomplete:\nAuction house will be here.")
            self.home()
        elif destination == "4":
            self.mechanics.pick_lot()
        elif destination == "5":
            print("\nIncomplete:\nThe stock market will be here.")
            self.home()
        elif destination == "6":
            print("\nIncomplete:\nPurchaseable businesses will be here.")
            self.home()
        else:
            print("Pick (1-6).")
            self.home()            


# Run the game
if __name__ == "__main__":
    game = CityGame()
    game.run()