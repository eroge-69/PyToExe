from Tkinter import *
import openpyxl
import pandas
fenetre=Tk()

titre=Label(fenetre,bg="GREEN", text="NOM")
titre.place(x=20,y=20)

titre=Label(fenetre,bg="GREEN", text="PRENOM")
titre.place(x=20,y=40)

titre=Label(fenetre,bg="GREEN", text="AGE")
titre.place(x=20,y=60)


wb=openpyxl.load_workbook('test2.xlsx')
sheet =wb['Feuil1']
N=sheet['A1']
P=sheet['B1']
A=sheet['C1']
N1=sheet['A2']
P1=sheet['B2']
A1=sheet['C2']
print('Nom:')
print(N1.value)
print('Prenom:')
print(P1.value)
print('Age:')
print(A1.value)
titre=Label(fenetre,bg="YELLOW", text=N1.value,relief='groove',width=20, height=1)
titre.place(x=200,y=20)
titre=Label(fenetre,bg="YELLOW", text=P1.value,relief='groove',width=20, height=1)
titre.place(x=200,y=40)
titre=Label(fenetre,bg="YELLOW", text=A1.value,relief='groove',width=20, height=1)
titre.place(x=200,y=60)
fenetre.title("INSCRIPTION")
fenetre.configure(bg="GREEN")
fenetre.minsize(400,400)
fenetre.mainloop()
