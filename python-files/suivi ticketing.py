class Ticket :
    def __init__(self, utilisateur, probleme, priorite) :
        self.utilisateur = utilisateur
        self.probleme = probleme
        self.priorite = priorite
        self.statut = "en cours"
        
    def afficher_ticket(self) :
        print("utilisateur : ", self.utilisateur)
        print("probleme : ", self.probleme)
        print("priorite : ", self.priorite)
        print("statut : ", self.statut)
        
    def resoudre(self) :
        self.statut = "resolu"
        print(f"Ticket pour {self.utilisateur} marqué comme resolu")

tickets = []

while True :
    print("\n--- Mini Assistant de Ticketing ---")
    print("1- Creez un nouveau ticket")
    print("2- Voir tous les tickets")
    print("3- Resoudre un ticket")
    print("4- Quitter")
    
    choix = input("Que veux tu faire ? ")
    
    if choix == "1" :
        utilisateur = input("Nom de l'utilisateur : ")
        probleme = input("Probleme rencontrer : ")
        priorite = input("Priorite : ")
        
        ticket = Ticket(utilisateur, probleme, priorite)
        tickets.append(ticket)
        
        print("Ticket a éte bien crée !")
    elif choix == "2" :
        if tickets :
            print("\n--- Tickets en cours --- ")
            for i, ticket in enumerate(tickets) :
                print(f"ID : {i} ")
                ticket.afficher_ticket()
        else :
            print("Aucun ticket pour le moment")
    elif choix == "3" :
        id_ticket = int(input("ID du ticket à resoudre : "))
        if 0 <= id_ticket < len(tickets) :
            tickets[id_ticket].resoudre()
        else :
            print("Ticket Invalide")
    elif choix == "4" :
        print("Assistant Fermer")
        break
    else :
        print("Choix Invalide")