import random
import time

def clear_screen():
    # Eine einfache Funktion, um den Bildschirm zu leeren (simuliert)
    # Funktioniert möglicherweise nicht in allen Umgebungen gleich gut
    print("\n" * 50)

def main():
    clear_screen()
    print("Willkommen zum Autorennspiel: Von Dresden nach Berlin!")
    print("-----------------------------------------------------")
    print("Dein Ziel ist es, Berlin zu erreichen, bevor dir der Sprit oder das Geld ausgeht.")
    print("Viel Glück!\n")
    time.sleep(2)

    # Initialisiere Spielvariablen
    distance_to_berlin = 190  # KM
    fuel = 100                # Liter
    money = 200               # Euro
    car_condition = 100       # Prozent (100 = perfekt, 0 = kaputt)
    current_km_driven = 0     # Bereits gefahrene Kilometer
    game_over = False
    
    # Gegnerische Distanz (simuliert)
    opponent_distance_to_berlin = 190

    # Spielschleife
    while not game_over:
        clear_screen()
        print("--- Dein aktueller Status ---")
        print(f"Verbleibende Strecke nach Berlin: {distance_to_berlin:.1f} KM")
        print(f"Tankfüllung: {fuel:.1f} Liter")
        print(f"Geld: {money:.2f} Euro")
        print(f"Zustand deines Autos: {car_condition}%")
        print(f"Dein Gegner ist noch {opponent_distance_to_berlin:.1f} KM von Berlin entfernt.")
        print("-----------------------------\n")

        if distance_to_berlin <= 0:
            print("Herzlichen Glückwunsch! Du hast Berlin erreicht!")
            print(f"Du hast insgesamt {current_km_driven:.1f} KM zurückgelegt.")
            print("Du hast das Rennen gewonnen!")
            game_over = True
            break
        
        if fuel <= 0:
            print("Oh nein! Dein Tank ist leer. Du bleibst liegen.")
            print("Du hast das Rennen verloren!")
            game_over = True
            break

        if car_condition <= 0:
            print("Dein Auto ist komplett kaputt! Du kannst nicht weiterfahren.")
            print("Du hast das Rennen verloren!")
            game_over = True
            break

        # Spieleraktionen
        print("Was möchtest du tun?")
        print("1. Fahren")
        print("2. Anhalten (Tankstelle/Werkstatt suchen)")
        choice = input("Deine Wahl (1/2): ")

        if choice == '1':
            print("\nWie schnell möchtest du fahren?")
            print("1. Schnell (Verbraucht mehr Sprit, hohes Risiko, schneller)")
            print("2. Normal (Ausgeglichen)")
            print("3. Langsam (Verbraucht wenig Sprit, geringes Risiko, langsamer)")
            speed_choice = input("Deine Wahl (1/2/3): ")

            km_to_drive = 0
            fuel_cost_per_km = 0
            car_wear_per_km = 0
            risk_factor = 0

            if speed_choice == '1':
                km_to_drive = random.randint(40, 60)
                fuel_cost_per_km = 0.3  # Liter pro KM
                car_wear_per_km = 0.8   # Verschleiß pro KM
                risk_factor = 30        # Wahrscheinlichkeit für Probleme in %
                print(f"\nDu trittst aufs Gas! Du wirst ca. {km_to_drive} KM fahren.")
            elif speed_choice == '2':
                km_to_drive = random.randint(25, 45)
                fuel_cost_per_km = 0.2
                car_wear_per_km = 0.5
                risk_factor = 15
                print(f"\nDu fährst entspannt mit normaler Geschwindigkeit. Du wirst ca. {km_to_drive} KM fahren.")
            elif speed_choice == '3':
                km_to_drive = random.randint(15, 30)
                fuel_cost_per_km = 0.15
                car_wear_per_km = 0.3
                risk_factor = 5
                print(f"\nDu fährst vorsichtig und sparsam. Du wirst ca. {km_to_drive} KM fahren.")
            else:
                print("Ungültige Eingabe. Du fährst normal weiter.")
                km_to_drive = random.randint(25, 45)
                fuel_cost_per_km = 0.2
                car_wear_per_km = 0.5
                risk_factor = 15

            # Gegner bewegt sich
            opponent_speed = random.randint(20, 50)
            opponent_distance_to_berlin -= opponent_speed
            if opponent_distance_to_berlin < 0:
                opponent_distance_to_berlin = 0

            # Berechne Verbrauch und Verschleiß
            fuel_consumed = km_to_drive * fuel_cost_per_km
            car_wear = km_to_drive * car_wear_per_km

            if fuel >= fuel_consumed:
                fuel -= fuel_consumed
                car_condition -= car_wear
                distance_to_berlin -= km_to_drive
                current_km_driven += km_to_drive
                print(f"Du bist {km_to_drive:.1f} KM gefahren. {fuel_consumed:.1f} Liter Sprit verbraucht. Auto um {car_wear:.1f}% abgenutzt.")

                # Zufällige Ereignisse während der Fahrt
                event_chance = random.randint(1, 100)
                if event_chance <= risk_factor:
                    event_type = random.choice(["Panne", "Verkehrskontrolle", "Stau", "Gutes Wetter", "Schlechtes Wetter"])
                    print(f"\nEIN EREIGNIS! {event_type}!")

                    if event_type == "Panne":
                        damage = random.randint(10, 30)
                        car_condition -= damage
                        print(f"Du hast eine Panne! Dein Auto hat {damage}% Schaden erlitten.")
                        if car_condition <= 0:
                            print("Dein Auto ist zu stark beschädigt, um weiterzufahren!")
                            game_over = True
                    elif event_type == "Verkehrskontrolle":
                        fine = random.randint(20, 50)
                        money -= fine
                        print(f"Verkehrskontrolle! Du wurdest mit {fine:.2f} Euro Bußgeld belegt.")
                        if money < 0:
                            money = 0
                            print("Du hast kein Geld mehr!")
                    elif event_type == "Stau":
                        time_lost_km = random.randint(5, 15)
                        distance_to_berlin += time_lost_km # Simuliere Stillstand/Umweg
                        print(f"Verkehrsstau! Du verlierst {time_lost_km} KM an effektiver Strecke.")
                    elif event_type == "Gutes Wetter":
                        print("Das Wetter ist perfekt! Du fühlst dich erfrischt und das Fahren geht leichter.")
                        car_condition = min(100, car_condition + 5) # Leichte Erholung
                    elif event_type == "Schlechtes Wetter":
                        fuel_penalty = random.randint(5, 15)
                        fuel -= fuel_penalty
                        print(f"Schlechtes Wetter! Du verbrauchst extra {fuel_penalty:.1f} Liter Sprit.")
                        if fuel < 0:
                            fuel = 0

            else:
                print("Nicht genug Sprit zum Fahren! Du musst tanken.")
                fuel = 0 # Tank ist leer
            
            input("\nDrücke Enter, um fortzufahren...")

        elif choice == '2':
            print("\nDu hältst an. Was möchtest du tun?")
            print("1. Tanken")
            print("2. Auto reparieren")
            print("3. Nichts tun und weiterfahren (Keine Aktion, zurück zum Menü)")
            stop_choice = input("Deine Wahl (1/2/3): ")

            if stop_choice == '1':
                fuel_price_per_liter = 1.80
                max_refill = 100 - fuel
                
                if max_refill <= 0:
                    print("Dein Tank ist bereits voll oder fast voll!")
                    input("Drücke Enter, um fortzufahren...")
                    continue

                print(f"Der Sprit kostet {fuel_price_per_liter:.2f} Euro pro Liter.")
                print(f"Du kannst maximal {max_refill:.1f} Liter tanken.")
                try:
                    refill_amount_str = input("Wie viele Liter möchtest du tanken? ")
                    refill_amount = float(refill_amount_str)
                    
                    if refill_amount <= 0:
                        print("Das ist keine gültige Menge.")
                    elif refill_amount > max_refill:
                        print(f"Du kannst nur maximal {max_refill:.1f} Liter tanken.")
                        refill_amount = max_refill
                    
                    cost = refill_amount * fuel_price_per_liter
                    if money >= cost:
                        fuel += refill_amount
                        money -= cost
                        print(f"Du hast {refill_amount:.1f} Liter getankt. Kosten: {cost:.2f} Euro.")
                    else:
                        print(f"Nicht genug Geld! Du kannst nur {money / fuel_price_per_liter:.1f} Liter tanken.")
                except ValueError:
                    print("Ungültige Eingabe. Bitte gib eine Zahl ein.")
                
            elif stop_choice == '2':
                if car_condition >= 100:
                    print("Dein Auto ist bereits in perfektem Zustand!")
                    input("Drücke Enter, um fortzufahren...")
                    continue

                repair_cost_per_percent = 2.50
                needed_repair_percent = 100 - car_condition
                max_repair_cost = needed_repair_percent * repair_cost_per_percent

                print(f"Die Reparatur kostet {repair_cost_per_percent:.2f} Euro pro Prozent Schaden.")
                print(f"Um dein Auto komplett zu reparieren, würden {max_repair_cost:.2f} Euro fällig.")
                try:
                    repair_amount_str = input("Wie viele Prozent Schaden möchtest du reparieren lassen? ")
                    repair_amount = float(repair_amount_str)

                    if repair_amount <= 0:
                        print("Das ist keine gültige Menge.")
                    elif repair_amount > needed_repair_percent:
                        print(f"Du kannst maximal {needed_repair_percent:.1f}% reparieren.")
                        repair_amount = needed_repair_percent
                    
                    cost = repair_amount * repair_cost_per_percent
                    if money >= cost:
                        car_condition += repair_amount
                        money -= cost
                        print(f"Du hast {repair_amount:.1f}% deines Autos repariert. Kosten: {cost:.2f} Euro.")
                    else:
                        print(f"Nicht genug Geld! Du kannst nur {money / repair_cost_per_percent:.1f}% reparieren.")
                except ValueError:
                    print("Ungültige Eingabe. Bitte gib eine Zahl ein.")
            elif stop_choice == '3':
                print("Du entscheidest dich, nichts zu tun und weiterzufahren.")
            else:
                print("Ungültige Eingabe. Du machst nichts.")
            
            input("\nDrücke Enter, um fortzufahren...")

        else:
            print("Ungültige Eingabe. Bitte wähle 1 oder 2.")
            input("\nDrücke Enter, um fortzufahren...")

    print("\n--- Spielende ---")
    print("Vielen Dank fürs Spielen!")

if __name__ == "__main__":
    main()


