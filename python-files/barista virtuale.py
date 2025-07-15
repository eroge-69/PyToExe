drink_speciale = "DigitalVodka"
prezzo_drink = 5.5
alcolici = ("whisky", "Vodka", "Graspa")
analcolici = ("Cocacola", "Succhi", "Fanta")

print("benvenuto al PUB")
print("mi chiamo edobot")
print("sono pronto a servirti! =)")

print("il drink in offerta è:")
print(drink_speciale)
print("provalo subito, solo:")
print(prezzo_drink)
print("\nI drik alcolici sono "+str(len(alcolici)))
print("\nI drik analcolici sono "+str(len(analcolici)))
print("come ti chiami?")
nome_cliente = input()
print("benvenuto carissimo:")
print(nome_cliente)
print("\nInserisci il tuo anno di nascita")
anno_nascita = int(input())
anni_cliente = 2025 - anno_nascita
print ("hai" + str(anni_cliente)+" anni")
drink_disponibili = []
if anni_cliente < 18:
    print("sei minorenne puoi ordinare solo analcolici")
    drink_disponibili += analcolici
else:
    print("\nSei maggiorenne: puoi ordinare alcolici e analcolici")
    drink_disponibili =  alcolici + analcolici
print("Ecco i drink consigliati per te: ")
for drink_disponibile in drink_disponibili :
    print (drink_disponibile)
drink_scelto = input()
if drink_scelto in drink_disponibili:
    print("hai scelto "+drink_scelto+".Buon aperitivo!")
else:
    print("mi spiace, il drink "+drink_scelto+" non è disponibile = (")
    
    

 






