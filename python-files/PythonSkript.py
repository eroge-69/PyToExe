import pyttsx3
import time
	
# Engine starten	
engine = pyttsx3.init()	
voices = engine.getProperty("voices")	
	
# Stimmen finden (abhängig vom System!)	
de_voice = next(v for v in voices if "de" in v.id.lower())   # Deutsch	
jp_voice = next(v for v in voices if "jp" in v.id.lower())   # Japanisch	
	
# Beispiel-Vokabeln: (Deutsch, Japanisch)	
vokabeln = [	
("Hund", "犬"),	
("Katze", "猫"),	
("Haus", "家")	
]	
	
# Vorlesen: erst Deutsch, dann Japanisch	
for de, jp in vokabeln:
    print(de)
    engine = pyttsx3.init()	
    engine.setProperty("voice", jp_voice.id)
    engine.say(jp)
    engine.runAndWait()
    print(jp)
    engine.setProperty("voice", de_voice.id)
    engine.say(de)
    engine.runAndWait()
