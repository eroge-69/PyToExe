
from tkinter import *
from tkinter import messagebox
from payscapitales import liste

point = 0
nbre = 0
liste_de_question = None
new = 0
activite = True
tour = 0

def points(x ="0"):
    label_point.configure(text = f"Score: {x} ",
                        font=("helvetica",15,"bold"), bg="cyan")
def choix():
    import random
    pays = liste.keys()
    country = random.choice(list(pays))
    return country

def chargement():
    #nbre = int(input("Voulez-vous combien de questions? "))
    questions = []
    compteur = 0
    while compteur < nbre:
        compteur += 1
        gen = choix()
        if gen not in questions:
            questions.append(gen)
        else:
            compteur -=1
    return questions

def questions(x):
    global capitale
    capitale =  liste[liste_de_question[x]]
    questionnaire.configure(text = (f"Quelle est la capitale (de,du,de la) {liste_de_question[x]} "),
                            font = ("helvetica",15,"bold"),bd=5, bg="white")

def valider():
    global tour, point
    if reponse.get() == "":
        reponse.configure(bg="yellow")
        messagebox.showerror("Champs vide", "Veuillez entrer une donnee comme reponse")
        return

    else:
        question = reponse.get()
        if question.lower() == capitale:
            messagebox.showinfo("Bravo", "Vous avez bien repondu")
            point = point + 100
            points(point)
        else:
            messagebox.showinfo("Oups!", f"La bonne reponse etait {capitale}")
    reponse.delete(0,END)
    if tour < nbre - 1:
        tour = tour + 1
        questions(tour)
    else:
        total_question = int(question_entry.get())

        question_entry.configure(state="normal")
        question_entry.delete(0, END)
        question_entry.configure(state="readonly")
        questionnaire.configure(text = (f"La partie est terminee!!\n<< Votre score est de {int(point/total_question)} % >>"),
                                font = ("helvetica",15,"bold"),bd=5, bg="white",
                                fg="red")
        validation.configure(state = "disabled", bg="light green", activebackground="Light green",activeforeground="light green")
        reponse.delete(0,END)
        reponse.configure(state = "readonly")
        commencer.configure(state="active", text = "Recommencer", command = recommencer)

def lancer():
    global liste_de_question, compteur
    liste_de_question = chargement()
    compteur = 0
    questions(compteur)
    validation.configure(state = "active",bg="green", command = valider)
    reponse.configure(state = "normal")

def commencer_jeux():
    global nbre
    total_question = len(liste)
    try:
        question_entry.configure(state="normal")
        commencer.configure(state="normal")
        if int(question_entry.get()) > total_question:
            question_entry.configure(bg="yellow")
            messagebox.showerror("Erreur", f"Desole\nLe nombre de question doit etre inferieur ou egal a {total_question}")
            question_entry.delete(0,END)
            return

        if question_entry.get() == "":
            question_entry.configure(bg="yellow")
            messagebox.showerror("Erreur","Veuillez definir le nombre de question")
            return
        elif int(question_entry.get()) < 2:
            messagebox.showwarning("Attention", "Les questions doivent etre au moins 2")
            return
        else:
            reponse.configure(state="normal")
            nbre = int(question_entry.get())
            commencer.configure(state = "disabled")
            question_entry.configure(state = "readonly")
            validation.configure(state="normal", bg="green")
            lancer()
    except Exception as e:
        question_entry.configure(bg="yellow")
        messagebox.showerror("Erreur", f"Erreur due au {e}")
        question_entry.delete(0, END)

def recommencer():
    global nbre,tour,point
    commencer.configure(state="active")
    question_entry.configure(state = "normal")
    tour = 0
    point = 0
    nbre = 0
    label_point.configure(text = f"Score: {point} ",
                          font=("helvetica",15,"bold"), bg="cyan")
    questionnaire.config(text = "Soyez pret pour vos questions",
                         font = ("helvetica",15,"bold"),bd=5, bg="white", fg="black")
    reponse.configure(state = "disabled")
    commencer.configure(text="Commencer", command= commencer_jeux)

fen = Tk()
fen.title("PAYS-CAPITALE")
fen.geometry("600x500+50+50")
fen.configure(bg="Royalblue2")
fen.grab_set()

lbl1 = Label(fen, text="JEU DE PAYS-CAPITALES",
             font=("arial",20,"bold"),bg="Royalblue2", fg="yellow")
lbl1.pack()

frame1 = Frame(fen, bg="cyan",width=596, height=400, bd=2)
frame1.place(x=2, y = 30)

label_point = Label(frame1, text = f"Score: {point} ", font=("helvetica",15,"bold"), bg="cyan")
label_point.place(x=2, y=5)

label_question = Label(frame1, text = "Nombre de questions:", font=("helvetica",15,"bold"))
label_question.place(x = 2, y = 32)

question_entry = Entry(frame1, font=("helvetica",15,"bold"), bg="white", width = 3)
question_entry.place(x = 220, y = 32)

questionnaire = Label(frame1, text = "Soyez pret, les questions apparaitront ici",
                      font = ("helvetica",15,"bold"),bd=5, bg="white" )
questionnaire.place(x = 2, y = 80,width = 587, height= 50)

commencer = Button(frame1, text = "Commencer", font=("helvetica",15,"bold"), cursor = "hand2",
                   bg="light yellow", state = "normal", command = commencer_jeux)
commencer.place(x = 2, y = 200)

reponse = Entry(frame1, font=("helvetica",15,"bold"), bg="light yellow", state="readonly")
reponse.place(x = 200, y = 200, width = 200, height=40)

validation = Button(frame1, text = "Valider", font=("helvetica",15,"bold"),bg="light green",
                    activebackground="green", cursor = "hand2",state = "disabled")
validation.place(x = 220, y = 300, width = 150)

quitter = Button(frame1, text = "Quitter", font=("Arial", 12, "bold"), bg="blue", fg="white", cursor = "hand2",
                 activebackground="blue", command = lambda: fen.destroy())
quitter.place(x = 500, y = 350)
lbl2 = Label(fen, text="Copyright: odpcorp 2025\nodpcorp@gmail.com",
             font=("arial",10,"bold"),bg="Royalblue2", fg="white")
lbl2.pack(side=BOTTOM, pady=20)

fen.mainloop()