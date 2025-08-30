import random

class DrunkRoadTripGame:
    def __init__(self):
        self.sobriety = 100
        self.inventory = ['car keys', 'phone', 'wallet']
        self.location = None
        self.game_over = False
        self.ending = None
        self.turns = 0
        self.completed_events = []

        # Each location has at least 5 unique events
        self.events = {
            "Las Vegas, NV": ["vegas_strip", "vegas_wrong_exit", "vegas_taxi_mishap",
                              "vegas_motel", "vegas_grandpa", "vegas_police"],
            "Crestline, CA": ["crestline_fog", "crestline_cliff", "crestline_cabin",
                              "crestline_kisha", "crestline_wildlife", "crestline_police"],
            "Hawaiian Paradise Park, HI": ["hpp_backroads", "hpp_pothole", "hpp_neighbor",
                                           "hpp_siobhan", "hpp_random_stranger", "hpp_lava_stream"],
            "Yucaipa, CA": ["yucaipa_traffic", "yucaipa_wrong_turn", "yucaipa_nitch",
                            "yucaipa_police", "yucaipa_small_town", "yucaipa_construction"],
            "Mojave Desert": ["mojave_breakdown", "mojave_lost", "mojave_coyote",
                              "mojave_sleep", "mojave_cody", "mojave_hot_sand"]
        }

    def display_status(self):
        print("\n--- CURRENT STATUS ---")
        print(f"Sobriety Level: {self.sobriety}%")
        print(f"Location: {self.location}")
        print(f"Inventory: {', '.join(self.inventory)}")
        print(f"Events Survived: {self.turns}")

    def reduce_sobriety(self, amount):
        self.sobriety = max(0, self.sobriety - amount)

    def start_game(self):
        print("🍺 Drunken Road Trip Roulette 🍺")
        print("Lukas is drunk, restless, and holding his car keys...")
        self.choose_location()
        self.main_menu()

    def choose_location(self):
        print("\nChoose Lukas's starting location:")
        print("1. Las Vegas, NV (near the Strip)")
        print("2. Crestline, CA (San Bernardino Mountains)")
        print("3. Hawaiian Paradise Park, HI (Puna District, Big Island)")
        print("4. Yucaipa, CA (Inland Empire, California)")
        print("5. Middle of the Mojave Desert (heading to Marvin's Mary J)")

        while True:
            choice = input("Enter your choice (1-5): ")
            if choice == '1':
                self.location = "Las Vegas, NV"
            elif choice == '2':
                self.location = "Crestline, CA"
            elif choice == '3':
                self.location = "Hawaiian Paradise Park, HI"
            elif choice == '4':
                self.location = "Yucaipa, CA"
            elif choice == '5':
                self.location = "Mojave Desert"
            else:
                print("Invalid choice. Try again.")
                continue
            break

    def main_menu(self):
        while not self.game_over:
            self.display_status()
            print("\nWhat should Lukas do?")
            print("1. Drive")
            print("2. Check inventory")
            print("3. Rest and recover")
            print("4. Quit game")

            choice = input("Enter your choice (1-4): ")

            if choice == '1':
                self.drive()
            elif choice == '2':
                self.check_inventory()
            elif choice == '3':
                self.rest()
            elif choice == '4':
                self.quit_game()
            else:
                print("Invalid choice. Try again.")

        self.show_ending()

    def drive(self):
        # Fixed: If all events are completed, allow repeating events or create new scenarios
        remaining_events = [e for e in self.events[self.location] if e not in self.completed_events]
        
        if not remaining_events:
            # Reset completed events to allow replaying or create a generic event
            print("\nLukas continues driving through familiar territory...")
            self.generic_drive_event()
            return
        
        event_name = random.choice(remaining_events)
        self.completed_events.append(event_name)
        self.turns += 1

        # Call the event dynamically
        getattr(self, event_name)()

        if self.turns >= 5:
            self.check_game_over()

    def generic_drive_event(self):
        """Fallback event when all location events are completed"""
        self.turns += 1
        scenarios = [
            "Lukas drives past familiar landmarks, muscle memory guiding him.",
            "The roads blur together as Lukas continues his journey.",
            "Lukas navigates another stretch of road, fighting to stay focused."
        ]
        print(random.choice(scenarios))
        self.reduce_sobriety(random.randint(5, 15))
        
        if self.turns >= 5:
            self.check_game_over()

    def check_game_over(self):
        if self.sobriety <= 0:
            print("\nLukas passes out at the wheel...")
            self.ending = "crash"
            self.game_over = True
        elif self.turns >= 10 and self.sobriety > 30:
            print("\nLukas has survived long enough to make it home safely!")
            self.ending = "safe_home"
            self.game_over = True

    def safe_drive(self):
        print("\nLukas keeps control of the car for now...")
        self.reduce_sobriety(random.randint(5, 10))

    def check_inventory(self):
        print("\nLukas checks his pockets:")
        for item in self.inventory:
            print(f"- {item}")

    def rest(self):
        print("\nLukas pulls over and leans back in the driver's seat...")
        recovery = random.randint(10, 25)
        self.sobriety = min(100, self.sobriety + recovery)
        print(f"Lukas regains {recovery}% sobriety.")

    def quit_game(self):
        print("\nLukas tosses his keys into the glovebox. He waits it out.")
        self.game_over = True
        self.ending = "quit"

    def show_ending(self):
        print("\n--- GAME OVER ---")
        endings = {
            "crash": "Lukas crashed the car. Metal twisted, glass shattered.",
            "quit": "Lukas decided not to risk it. The car stayed parked.",
            "vegas_safe_grandpa": "Grandpa Mike guided Lukas safely to a hotel. Love and wisdom prevailed.",
            "hpp_siobhan_safe": "Siobhan drove Lukas home safely. Love won the night.",
            "yucaipa_nitch_safe": "Cousin Nitch took Lukas in and fed him snacks. Safe at last!",
            "mojave_cody_safe": "Cody guided Lukas safely to Marvin's Mary J. Dispensary. Adventure complete!",
            "safe_home": "Lukas made it home safely after surviving the night.",
        }
        print(endings.get(self.ending, "Lukas's journey ends... unpredictably."))

    # -------------------------
    # LAS VEGAS EVENTS (Grandpa Mike)
    # -------------------------
    def vegas_strip(self):
        print("\nLukas drifts onto Las Vegas Blvd, dodging taxis and drunken pedestrians.")
        print("1) Floor it down the Strip like a maniac.")
        print("2) Pull over and stumble into a casino.")
        print("3) Slow down and try to play it safe.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Lukas nearly clips a taxi. His sobriety drops fast.")
            self.reduce_sobriety(15)
        elif choice == '2':
            print("He parks and staggers into a casino, losing track of time.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("He steadies himself and keeps control… for now.")
            self.safe_drive()
        else:
            print("Confused, Lukas just keeps driving.")
            self.safe_drive()

    def vegas_wrong_exit(self):
        print("\nLukas misses the exit and winds up in a dark alley behind Fremont Street.")
        print("1) Reverse out carefully.")
        print("2) Keep driving deeper into the alley.")
        print("3) Get out of the car to look around.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He backs out nervously but makes it back to the road.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("The alley gets sketchier and Lukas gets more stressed.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("He stumbles around but finds nothing. Wanders back to the car.")
            self.reduce_sobriety(10)
        else:
            print("He panics and just guns it forward.")
            self.reduce_sobriety(15)

    def vegas_taxi_mishap(self):
        print("\nA taxi cuts Lukas off near the Bellagio. He swerves sharply.")
        print("1) Honk and scream at the taxi driver.")
        print("2) Try to cut around them aggressively.")
        print("3) Slow down and let it go.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Lukas leans on the horn. His anger distracts him.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("He swerves recklessly and nearly crashes.")
            self.reduce_sobriety(20)
        elif choice == '3':
            print("He grits his teeth and calms down.")
            self.reduce_sobriety(5)
        else:
            print("He freezes up. The taxi speeds off anyway.")
            self.safe_drive()

    def vegas_motel(self):
        print("\nNeon signs flash. Lukas spots a cheap motel on Tropicana Ave.")
        print("1) Pull in and rent a room.")
        print("2) Sit in the parking lot and drink more.")
        print("3) Ignore it and keep driving.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He rests briefly but doesn't really sober up.")
            self.sobriety = min(100, self.sobriety + 5)
        elif choice == '2':
            print("He drinks alone in the lot. Bad idea.")
            self.reduce_sobriety(20)
        elif choice == '3':
            print("He keeps going, the neon still glowing behind him.")
            self.safe_drive()
        else:
            print("Lukas just circles the block aimlessly.")
            self.reduce_sobriety(10)

    def vegas_grandpa(self):
        print("\nGrandpa Mike calls: 'Lukas, come inside before you wreck!'")
        print("1) Listen to Grandpa Mike and go inside.")
        print("2) Argue with him, insisting you're fine.")
        print("3) Ignore the call and keep driving.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Grandpa Mike guides Lukas to safety.")
            if self.turns >= 5:
                self.ending = "vegas_safe_grandpa"
                self.game_over = True
            else:
                print("But Lukas isn't done yet… the night goes on.")
                self.safe_drive()
        elif choice == '2':
            print("Mike sighs and hangs up. Lukas feels a pang of guilt.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("Lukas ignores Grandpa Mike and keeps driving.")
            self.safe_drive()
        else:
            print("He fumbles the phone and drops it.")
            self.reduce_sobriety(5)

    def vegas_police(self):
        print("\nFlashing lights appear behind Lukas on I-15 near the Strip.")
        print("1) Pull over and hope for mercy.")
        print("2) Try to outrun them.")
        print("3) Pretend not to notice and keep cruising.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("The cop lectures him but lets him off with a warning.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("He floors it, weaving dangerously through traffic.")
            self.reduce_sobriety(25)
        elif choice == '3':
            print("The cop keeps following, adding to his stress.")
            self.reduce_sobriety(15)
        else:
            print("He panics and pulls onto a random off-ramp.")
            self.reduce_sobriety(10)

    # -------------------------
    # CRESTLINE EVENTS (Kisha)
    # -------------------------
    def crestline_fog(self):
        print("\nFog covers the Rim of the World Highway (CA-18). Visibility is minimal.")
        print("1) Slow way down and creep along the road.")
        print("2) Blast the high beams and hope for the best.")
        print("3) Pull over and wait for the fog to clear.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He crawls through the fog, stressed but steady.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("The bright lights blind him even more. Bad move.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("He waits in silence. The fog feels endless.")
            self.reduce_sobriety(10)
        else:
            print("He hesitates, stuck in the fog.")
            self.safe_drive()

    def crestline_cliff(self):
        print("\nLukas approaches a cliff edge on CA-18. Heart pounding!")
        print("1) Hug the guardrail carefully.")
        print("2) Speed up to get past it faster.")
        print("3) Stop the car and try to breathe.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He keeps his eyes glued to the rail, white-knuckled.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("He speeds dangerously close to the drop.")
            self.reduce_sobriety(20)
        elif choice == '3':
            print("He pulls over briefly, calming down a little.")
            self.reduce_sobriety(5)
        else:
            print("He closes his eyes for a second—too long.")
            self.reduce_sobriety(15)

    def crestline_cabin(self):
        print("\nA cabin offers shelter. Lukas takes a brief safe rest.")
        print("1) Knock on the cabin door for help.")
        print("2) Sit outside the cabin and drink from his flask.")
        print("3) Keep walking past it and ignore the cabin.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("A kind stranger lets him sit and rest briefly.")
            self.sobriety = min(100, self.sobriety + 5)
        elif choice == '2':
            print("The flask burns his throat. His mind spins.")
            self.reduce_sobriety(20)
        elif choice == '3':
            print("He ignores the cabin and pushes forward.")
            self.safe_drive()
        else:
            print("He just stares at the cabin, too indecisive.")
            self.reduce_sobriety(10)

    def crestline_kisha(self):
        print("\nKisha shouts from the roadside: 'Lukas, party time!'")
        print("1) Go with her and join the party.")
        print("2) Argue and tell her you need to focus.")
        print("3) Ignore her and drive away.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Lukas loses focus and drinks more, reducing sobriety.")
            self.reduce_sobriety(20)
        elif choice == '2':
            print("Kisha rolls her eyes, but Lukas feels steadier.")
            self.safe_drive()
        elif choice == '3':
            print("He ignores Kisha completely and drives on.")
            self.safe_drive()
        else:
            print("He laughs nervously but doesn't stop.")
            self.reduce_sobriety(10)

    def crestline_wildlife(self):
        print("\nA deer jumps onto CA-18! Lukas swerves.")
        print("1) Slam the brakes immediately.")
        print("2) Try to swerve around it.")
        print("3) Honk the horn and hope it runs.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Hard braking jolts Lukas, but he avoids hitting the deer.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("He swerves wildly, nearly losing control on the mountain road.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("The horn startles the deer and it bounds away safely.")
            self.reduce_sobriety(5)
        else:
            print("He panics and jerks the wheel.")
            self.reduce_sobriety(15)

    def crestline_police(self):
        print("\nA San Bernardino County Sheriff sits at a speed trap on CA-18.")
        print("1) Slow down and drive past casually.")
        print("2) Take a detour through residential streets.")
        print("3) Speed past and hope they don't notice.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("The officer gives him a suspicious look but lets him pass.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("The detour through neighborhoods confuses him.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("The sheriff immediately pulls out and follows with lights flashing!")
            self.reduce_sobriety(25)
        else:
            print("He freezes, drawing unwanted attention.")
            self.reduce_sobriety(15)

    # -------------------------
    # HAWAIIAN PARADISE PARK EVENTS (Siobhan)
    # -------------------------
    def hpp_backroads(self):
        print("\nTwisting jungle backroads on Paradise Drive. Dense trees on both sides.")
        print("1) Floor it and hope nothing jumps out.")
        print("2) Slow down and admire the scenery.")
        print("3) Pull over and stretch your legs.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("The rough terrain shakes Lukas, lowering his focus.")
            self.reduce_sobriety(15)
        elif choice == '2':
            print("He drives carefully, enjoying the jungle sights.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("He gets out briefly, calming down and taking a deep breath.")
            self.sobriety = min(100, self.sobriety + 5)
        else:
            print("He hesitates mid-road, losing focus.")
            self.reduce_sobriety(10)

    def hpp_pothole(self):
        print("\nA hidden pothole on Kaloli Drive throws Lukas' car off balance.")
        print("1) Brake hard to avoid it.")
        print("2) Try to swerve around it.")
        print("3) Hit it head-on and pray for the best.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He stops just in time. Adrenaline spikes.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("He swerves sharply but keeps control.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("The car jolts hard. Lukas holds on tight.")
            self.reduce_sobriety(20)
        else:
            print("He panics and jerks the wheel.")
            self.reduce_sobriety(15)

    def hpp_neighbor(self):
        print("\nA friendly neighbor waves Lukas down on Makuu Drive. Offers a safe path.")
        print("1) Follow them for guidance.")
        print("2) Thank them but keep driving cautiously.")
        print("3) Ignore them and take a riskier shortcut.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("The neighbor guides Lukas safely a short distance.")
            self.safe_drive()
        elif choice == '2':
            print("He cautiously follows his instincts, all seems fine.")
            self.safe_drive()
        elif choice == '3':
            print("He takes the shortcut and bumps over some rocks.")
            self.reduce_sobriety(10)
        else:
            print("He hesitates, wasting time on the road.")
            self.reduce_sobriety(10)

    def hpp_siobhan(self):
        print("\nSiobhan calls: 'Lukas, I'll drive you home!'")
        print("1) Accept her help and get in the car.")
        print("2) Politely refuse and keep driving.")
        print("3) Hesitate, unsure what to do.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Siobhan drives Lukas safely home.")
            if self.turns >= 5:
                self.ending = "hpp_siobhan_safe"
                self.game_over = True
            else:
                print("The night isn't over yet…")
                self.safe_drive()
        elif choice == '2':
            print("He keeps driving, still intoxicated.")
            self.safe_drive()
        elif choice == '3':
            print("He wastes precious time deciding. Road is tricky.")
            self.reduce_sobriety(10)
        else:
            print("He freezes in indecision. Nothing happens.")
            self.reduce_sobriety(10)

    def hpp_random_stranger(self):
        print("\nA stranger offers help through a lava path.")
        print("1) Follow the stranger cautiously.")
        print("2) Politely decline and find your own way.")
        print("3) Ignore them and speed past.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("The stranger guides him safely through.")
            self.safe_drive()
        elif choice == '2':
            print("He navigates alone, careful but slower.")
            self.reduce_sobriety(5)
        elif choice == '3':
            print("He rushes past, nearly losing control.")
            self.reduce_sobriety(15)
        else:
            print("He hesitates, losing focus.")
            self.reduce_sobriety(10)

    def hpp_lava_stream(self):
        print("\nLukas drives near a cooled lava stream, careful not to skid.")
        print("1) Hug the edge and drive slowly.")
        print("2) Drive confidently across the path.")
        print("3) Step out to check the terrain first.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He drives carefully and maintains control.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("He drives boldly, car slips slightly but recovers.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("Stepping out costs time and focus, but he avoids danger.")
            self.reduce_sobriety(5)
        else:
            print("He freezes, unsure how to proceed.")
            self.reduce_sobriety(10)

    # -------------------------
    # YUCAIPA EVENTS (Cousin Nitch)
    # -------------------------
    def yucaipa_traffic(self):
        print("\nHeavy I-10 traffic near Yucaipa. Lukas weaves between cars.")
        print("1) Aggressively cut between lanes.")
        print("2) Stay calm and wait for an opening.")
        print("3) Take the next exit to avoid traffic.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He weaves dangerously. Heart racing!")
            self.reduce_sobriety(15)
        elif choice == '2':
            print("He moves carefully, keeping his cool.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("He avoids traffic but adds time to the trip.")
            self.reduce_sobriety(5)
        else:
            print("He freezes in the lane. Other drivers honk.")
            self.reduce_sobriety(10)

    def yucaipa_wrong_turn(self):
        print("\nLukas takes a wrong turn off I-10 into Redlands.")
        print("1) Try to navigate back immediately.")
        print("2) Keep exploring and see where it leads.")
        print("3) Pull over and check the map.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He finds his way quickly, barely losing focus.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("He drives a bit aimlessly, stress rising.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("Checking the map slows him down but he recovers slightly.")
            self.reduce_sobriety(5)
        else:
            print("He panics and circles the block.")
            self.reduce_sobriety(10)

    def yucaipa_nitch(self):
        print("\nCousin Nitch calls: 'Lukas! Come over, I'll help you chill.'")
        print("1) Go to Nitch and take a break.")
        print("2) Politely decline and keep driving.")
        print("3) Hesitate, unsure what to do.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Nitch feeds Lukas snacks and he rests safely.")
            if self.turns >= 5:
                self.ending = "yucaipa_nitch_safe"
                self.game_over = True
            else:
                print("But the night isn't over yet…")
                self.safe_drive()
        elif choice == '2':
            print("He keeps driving, trying to handle it alone.")
            self.safe_drive()
        elif choice == '3':
            print("He wastes time deciding. Stress builds.")
            self.reduce_sobriety(10)
        else:
            print("He hesitates indecisively.")
            self.reduce_sobriety(10)

    def yucaipa_police(self):
        print("\nA Yucaipa police car appears on Oak Glen Road.")
        print("1) Pull over politely.")
        print("2) Try to blend in and keep going.")
        print("3) Speed up to avoid attention.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("The cop lets him go with a warning.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("He drives cautiously, trying to look normal.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("Speeding draws the cop's attention. Risky move!")
            self.reduce_sobriety(20)
        else:
            print("He panics slightly but drives on.")
            self.reduce_sobriety(10)

    def yucaipa_small_town(self):
        print("\nLukas drives through the quaint streets of Yucaipa.")
        print("1) Slow down and take in the sights.")
        print("2) Drive quickly to get past the town.")
        print("3) Pull over and grab a snack at a diner.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He enjoys the view, focus stays stable.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("Speeding slightly stresses him out.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("He rests briefly and gains some composure.")
            self.sobriety = min(100, self.sobriety + 5)
        else:
            print("He hesitates, wandering slowly.")
            self.reduce_sobriety(10)

    def yucaipa_construction(self):
        print("\nRoad construction on Oak Glen Road! Lukas maneuvers carefully.")
        print("1) Follow detour signs precisely.")
        print("2) Try to cut through a shortcut.")
        print("3) Wait for traffic to clear.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He follows the signs safely.")
            self.reduce_sobriety(5)
        elif choice == '2':
            print("Shortcut is rough, car rattles violently.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("He waits and watches other cars, calm for a moment.")
            self.reduce_sobriety(0)
        else:
            print("He hesitates in the middle of the lane.")
            self.reduce_sobriety(10)

    # -------------------------
    # MOJAVE DESERT EVENTS (Cody)
    # -------------------------
    def mojave_breakdown(self):
        print("\nLukas' car sputters on Amboy Road in the Mojave.")
        print("1) Try to fix it himself.")
        print("2) Call for roadside assistance.")
        print("3) Push the car to a nearby shade.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He fiddles under the hood, wasting time and energy.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("Help is on the way, but he waits nervously.")
            self.reduce_sobriety(5)
        elif choice == '3':
            print("Pushing the car burns his energy under the sun.")
            self.reduce_sobriety(15)
        else:
            print("He panics and does nothing.")
            self.reduce_sobriety(10)

    def mojave_lost(self):
        print("\nLost in the desert heat near US-95.")
        print("1) Call Cody for directions.")
        print("2) Wander blindly hoping to find a road.")
        print("3) Stay put and conserve energy.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            self.mojave_cody()
        elif choice == '2':
            print("The sun beats down and Lukas loses focus.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("He rests in the shade, losing some momentum but saving energy.")
            self.sobriety = min(100, self.sobriety + 5)
        else:
            print("He panics and moves in circles.")
            self.reduce_sobriety(10)

    def mojave_coyote(self):
        print("\nA coyote darts across US-95! Lukas swerves.")
        print("1) Slam the brakes.")
        print("2) Steer around it.")
        print("3) Honk to scare it away.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Hard braking shocks Lukas, but avoids the coyote.")
            self.reduce_sobriety(10)
        elif choice == '2':
            print("He swerves carefully, car bounces over sand.")
            self.reduce_sobriety(10)
        elif choice == '3':
            print("Coyote runs off, Lukas keeps driving.")
            self.reduce_sobriety(5)
        else:
            print("He freezes briefly; the coyote escapes.")
            self.reduce_sobriety(10)

    def mojave_sleep(self):
        print("\nLukas pulls over in the middle of the Mojave Desert to take a break.")
        print("The desert is still, and the night is starting to set in.")
        print("1) Drink Fireball and blast хардбас music, hoping to chill and relax.")
        print("2) Try to sleep in the car, but it's too hot and uncomfortable.")
        print("3) Drink water and stay awake, keeping an eye out for anything in the desert.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Lukas drinks some Fireball and jams to хардбас music, dancing around the car.")
            self.reduce_sobriety(20)
        elif choice == '2':
            print("Lukas falls asleep in the car, but the heat wakes him up after a short nap.")
            self.reduce_sobriety(5)
        elif choice == '3':
            print("Lukas stays awake, sipping water, but struggles to stay focused.")
            self.reduce_sobriety(10)
        else:
            print("Invalid choice. Lukas tries to sleep but keeps tossing and turning.")
            self.reduce_sobriety(10)

    def mojave_cody(self):
        print("\nCody appears on speaker: 'Yo Lukas, follow me. I'll get you to Marvin's safely.'")
        print("1) Follow Cody exactly.")
        print("2) Ignore him and keep driving.")
        print("3) Hesitate, unsure if you should trust him.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("Cody guides Lukas to Marvin's Mary J. Mission complete!")
            if self.turns >= 5:
                self.ending = "mojave_cody_safe"
                self.game_over = True
            else:
                print("The adventure continues…")
                self.safe_drive()
        elif choice == '2':
            print("He drives alone, focus waning in the desert heat.")
            self.reduce_sobriety(15)
        elif choice == '3':
            print("He hesitates, losing valuable time.")
            self.reduce_sobriety(10)
        else:
            print("He panics and stays put.")
            self.reduce_sobriety(10)

    def mojave_hot_sand(self):
        print("\nThe sun beats down on US-95. Heatwaves blur the road.")
        print("1) Speed through while sweating profusely.")
        print("2) Pull over and cover up from the sun.")
        print("3) Drink water and proceed carefully.")
        choice = input("Enter 1, 2, or 3: ")
        if choice == '1':
            print("He loses focus in the heat, driving dangerously.")
            self.reduce_sobriety(15)
        elif choice == '2':
            print("He rests briefly and shields himself from the sun.")
            self.sobriety = min(100, self.sobriety + 5)
        elif choice == '3':
            print("Hydrated, Lukas manages to keep moving cautiously.")
            self.reduce_sobriety(5)
        else:
            print("He freezes, unsure how to continue in the heat.")
            self.reduce_sobriety(10)


# To run the game:
if __name__ == "__main__":
    game = DrunkRoadTripGame()
    game.start_game()