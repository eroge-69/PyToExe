import random
import os

class JugendwortSpiel:
    def __init__(self):
        self.punkte = 0
        self.genannte_woerter = []
        self.ziel_anzahl = 15  # Anzahl der zu erratenden Wörter für den Sieg
        
        # Liste mit Jugendwörtern und deren Bedeutungen
        self.jugendwoerter = {
            "cringe": "Peinlich, unangenehm",
            "sus": "Verdächtig, fragwürdig",
            "wyld": "Krass, verrückt (alternative Schreibweise)",
            "slay": "Etwas sehr gut machen",
            "smash": "Jemanden attraktiv finden",
            "digga": "Kumpel, Freund",
            "safe": "Sicher, garantiert",
            "same": "Zustimmung, geht mir genauso",
            "goofy": "Albern, trottelig",
            "lost": "Verwirrt, ahnungslos",
            "macher": "Jemand, der Dinge erledigt",
            "lol": "Laughing out loud",
            "lmao": "Laughing my ass off",
            "yallah": "Los geht's, schnell",
            "bra": "Bruder (aus dem Russischen (bratan))",
            "vallah": "Ich schwöre",
            "icks": "Etwas, das einen abturnt",
            "main character": "Sich wie die Hauptfigur fühlen",
            "rizz": "Flirtfähigkeiten, Charme",
            "no cap": "Ohne zu lügen, ehrlich",
            "nh": "Nicht wahr?",
            "lass ihn kochen": "Unterbrich ihn nicht und lass uns sehen, was er kann." ,
            "bro" : "bruder auf englisch" , 
            "talahon" : "ein jugendlicher der ein kanake ist" , 
        }
    
    def bildschirm_leeren(self):
        # Bildschirm leeren (funktioniert für Windows und Unix/Linux/Mac)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def zeige_willkommen(self):
        self.bildschirm_leeren()
        print("="*60)
        print("Willkommen beim Jugendwort-Rätselspiel!")
        print("="*60)
        print("Regeln:")
        print(f"1. Sammle {self.ziel_anzahl} Jugendwörter, um das Spiel zu gewinnen.")
        print("2. Für jedes korrekte Jugendwort erhältst du einen Punkt.")
        print("3. Bereits genannte Wörter zählen nicht erneut.")
        print("4. Tippe 'hilfe' ein, um Beispiele für Jugendwörter zu sehen.")
        print("5. Tippe 'ende' ein, um das Spiel vorzeitig zu beenden.")
        print("6. Tippe 'liste' ein, um alle bisher genannten Wörter zu sehen.")
        print("="*60)
        input("Drücke Enter, um zu beginnen...")
    
    def zeige_info_zu_wort(self, wort):
        if wort.lower() in self.jugendwoerter:
            bedeutung = self.jugendwoerter[wort.lower()]
            print(f"\nInfo: '{wort}' bedeutet: {bedeutung}")
    
    def zeige_bekannte_jugendwoerter(self):
        print("\nHier sind einige Jugendwörter zur Inspiration:")
        beispiele = random.sample(list(self.jugendwoerter.keys()), min(10, len(self.jugendwoerter)))
        for i, wort in enumerate(beispiele):
            print(f"{i+1}. {wort}", end="   ")
            if (i+1) % 5 == 0:
                print()
        print("\n")
    
    def liste_genannter_woerter(self):
        print("\nBisher genannte Wörter:")
        if not self.genannte_woerter:
            print("Noch keine Wörter genannt!")
            return
        
        for i, wort in enumerate(self.genannte_woerter):
            print(f"{i+1}. {wort} - {self.jugendwoerter[wort]}")
        print(f"\nGesamtpunktzahl: {self.punkte}/{self.ziel_anzahl}")
    
    def spiele_runde(self):
        self.bildschirm_leeren()
        print("="*60)
        print("Jugendwort-Challenge beginnt!")
        print("="*60)
        
        print(f"Ziel: Sammle {self.ziel_anzahl} Jugendwörter!")
        print("Befehle: 'hilfe' für Beispiele, 'liste' für genannte Wörter, 'ende' zum Beenden")
        print("-"*60)
        
        while self.punkte < self.ziel_anzahl:
            print(f"Deine Punkte: {self.punkte}/{self.ziel_anzahl}")
            print("Genannte Wörter:", ", ".join(self.genannte_woerter) if self.genannte_woerter else "Noch keine")
            print("-"*60)
            
            print("Gib ein Jugendwort ein (oder 'hilfe', 'liste', 'ende'):")
            wort = input("> ").strip().lower()
            
            if wort == "ende":
                break
            elif wort == "hilfe":
                self.zeige_bekannte_jugendwoerter()
                continue
            elif wort == "liste":
                self.liste_genannter_woerter()
                input("\nDrücke Enter, um fortzufahren...")
                self.bildschirm_leeren()
                continue
                
            if not wort:
                print("Bitte gib ein Wort ein!")
                continue
                
            if wort in self.genannte_woerter:
                print(f"'{wort}' wurde bereits genannt!")
                input("Drücke Enter, um fortzufahren...")
            elif wort in self.jugendwoerter:
                print(f"✓ '{wort}' ist korrekt! +1 Punkt")
                self.punkte += 1
                self.genannte_woerter.append(wort)
                self.zeige_info_zu_wort(wort)
                input("Drücke Enter, um fortzufahren...")
            else:
                print(f"✗ '{wort}' ist kein bekanntes Jugendwort in unserer Liste!")
                input("Drücke Enter, um fortzufahren...")
            
            self.bildschirm_leeren()
    
    def zeige_ergebnis(self):
        self.bildschirm_leeren()
        print("\n" + "="*60)
        
        if self.punkte >= self.ziel_anzahl:
            print(f"Glückwunsch! Du hast das Ziel von {self.ziel_anzahl} Jugendwörtern erreicht!")
        else:
            print(f"Spiel beendet! Du hast {self.punkte} von {self.ziel_anzahl} Punkten erreicht.")
        
        print("="*60)
        
        if self.punkte >= self.ziel_anzahl:
            print("Sheesh! Du bist ein echter Jugendwort-Profi! Richtig wild!")
        elif self.punkte >= self.ziel_anzahl * 0.7:
            print("Nice! Du kennst dich gut mit Jugendwörtern aus! Fast ein Ehrenmann!")
        elif self.punkte >= self.ziel_anzahl * 0.4:
            print("Nicht schlecht! Du hast schon einige Jugendwörter drauf!")
        else:
            print("Ein Anfang! Mit mehr Übung wirst du zum Jugendwort-Experten!")
        
        print("\nDeine genannten Jugendwörter:")
        for i, wort in enumerate(self.genannte_woerter):
            print(f"{i+1}. {wort} - {self.jugendwoerter[wort]}")
        
        print("="*60)
    
    def starte_spiel(self):
        self.zeige_willkommen()
        self.spiele_runde()
        self.zeige_ergebnis()
        
        while True:
            nochmal = input("\nMöchtest du nochmal spielen? (j/n): ").lower()
            if nochmal == "j":
                self.punkte = 0
                self.genannte_woerter = []
                self.starte_spiel()
                break
            elif nochmal == "n":
                print("\nDanke fürs Spielen! Du bist echt wyld!")
                break
            else:
                print("Bitte antworte mit j oder n.")

# Spiel starten
if __name__ == "__main__":
    spiel = JugendwortSpiel()
    spiel.starte_spiel()