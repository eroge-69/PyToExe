import tkinter as tk
from tkinter import messagebox

class Finestra(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master.title("ILOVEYOU")
        self.master.geometry("300x200")
        self.grid()
        self.crea_widgets()

    def crea_widgets(self):
        self.lblNome = tk.Label(self, text = "Nome")
        self.lblNome.grid(row = 0, column = 0)
        self.vNome = tk.StringVar()
        self.txtNome = tk.Entry(self, textvariable = self.vNome)
        self.txtNome.grid(row = 0, column = 1)
        messagebox.showwarning("Attenzione", "Identificati")


        self.btnInvio = tk.Button(self, text = "Invio", command = self.invio_dati)
        self.btnInvio.grid(row = 1, column = 1)


    def invio_dati(self):
        nome = self.vNome.get()
        if nome == "Charlie" or nome == "charlie":
            messagebox.showinfo("Conferma", "Puoi continuare")
            self.btn1 = tk.Button(self, text = "Premi", command = self.Ciao)
            self.btn1.grid(row = 0, column = 0)
            self.lblNome.destroy()
            self.btnInvio.destroy()
            self.txtNome.destroy()
            
        else:
            messagebox.showwarning("Attenzione", "Negro sto programma non è per te")
            self.txtNome.delete(0, tk.END)



    def Ciao(self):
        messagebox.showinfo("Info", "Ehi amore")
        self.btn1 = tk.Button(self, text = "Premi", command = self.cosa)
        self.btn1.grid(row = 2, column = 1)
        

    def cosa(self):
        messagebox.showinfo("Info", "Con questo programma volevo dirti un pò di cose")
        self.btn1 = tk.Button(self, text = "Premi", command = self.muah)
        self.btn1.grid(row = 3, column = 2)

    def muah(self):
        messagebox.showinfo("Info", "Volevo dirti quanto ti ritengo perfetta, quanto mi fai sorridere, quanto la tua bellezza sia unica sulla terra, come il tuo sorriso mi faccia gioire il cuore e la tua sola presenza mi cure le ferite")
        self.btn1 = tk.Button(self, text = "Premi", command = self.grazie)
        self.btn1.grid(row = 2, column = 3)

    def grazie(self):
        messagebox.showinfo("Info", "Voglio ringraziarti per come mi fai sentire amato ogni giorno, per come le nostre conversazioni siano il mio momento preferito della giornata, quanto le tue parole di affetto e amore mi facciano essere la persona più felice su questa terra, di quanto i tuoi abbracci mi fanno sentire al sicuro. Grazie di esistere, grazie di essere te stessa, grazie per essere unica")
        self.btn1 = tk.Button(self, text = "Premi", command = self.supporto)
        self.btn1.grid(row = 0, column = 4)

    def supporto(self):
        messagebox.showinfo("Info", "Voglio anche dirti che sarò al tuo fianco per sempre, quando ti sentirai sola io ci sarò, quanto ti sentirai stanca ci sarò io a sostenerti, quanto avrai bisogno di una spalla su cui piangere avrai entrambe le mie, quando avrai paura la affronteremo insieme, il peso che porti lo porteremo insieme in modo che sarà più leggero. Io ti aiuterò per sempre, con me non sarai mai da sola, sono qui per questo, sono qui per aiutarti")
        self.btn1 = tk.Button(self, text = "Premi", command = self.wow)
        self.btn1.grid(row = 2, column = 5)

    def wow(self):
        messagebox.showinfo("Info", "Sai a volte non ci rendiamo conto della fortuna che abbiamo, ma io me ne rendo davvero molto conto, perché averti nella mia vita significa aver avuto la fortuna più grande di tutte, e lo riconosco alla perfezione, dalla vita non volevo altro se non te, non hai idea di come mi senta fortunato la mattina sapendo che ho te nella mia vita")
        self.btn1 = tk.Button(self, text = "Premi", command = self.tiamo)
        self.btn1.grid(row = 4, column = 0)

    def tiamo(self):
        messagebox.showinfo("Info", "Infine volevo dirti che ti amo con tutto me stesso, non ho mai amato una persona cosi tanto in vita mia e lo continuerò a fare finchè il mio cuore continuerà a battere, le sole parole non sono abbastanza per descrivere i sentimenti che ho verso di te, sei la persona che ho sempre sognato nella vita, il mio amore verso di te non conosce limit e mai li potrà raggiungere, voglio renderti la persona più felice al mondo, voglio farti stare bene e darti la vita che hai sempre meritato, voglio vederti stare bene, voglio vedere realizzare i tuoi sogni, raggiungere i tuoi obiettivi, voglio vederti avere successo nella vita. Ti Amo <3") 
        self.btn1 = tk.Button(self, text = "Esci", command = self.master.destroy)
        self.btn1.grid(row = 6, column = 3)




def main():
    f = Finestra()
    f.mainloop()

main()
