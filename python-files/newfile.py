import tkinter as tk

a = ""
#numeros pra conta
def primeiro():
	global a
	a += "1"
	nunber["text"] = a
	
def segundo():
	global a
	a += "2"	
	nunber["text"] = a
	
		
def terçeiro():
	global a
	a += "3"	
	nunber["text"] = a
	
		
def quarto():
	global a
	a += "4"	
	nunber["text"] = a
	
		
def quinto():
	global a
	a += "5"	
	nunber["text"] = a
	
		
def sesto():
	global a
	a += "6"	
	nunber["text"] = a
	
		
def setimo():
	global a
	a += "7"	
	nunber["text"] = a
	
		
def oitavo():
	global a
	a += "8"	
	nunber["text"] = a
	
		
def nono():
	global a
	a += "9"	
	nunber["text"] = a
	
def zero():
		global a
		a += "0"
		nunber["text"] = a
#func		
def en():
		global a
		a += "+"
		nunber["text"] = a
		
def go():
		global a
		try:
			b = eval(a)
			a = ""
			nunber["text"] = b
			
		except:
			a = ""
			nunber["text"] = "error"			
		
def paga():
		global a
		a = ""
		nunber["text"] = ""												
		
#gui	
janela = tk.Tk()
janela.title("calc_py")
janela.geometry("400x600")
#texto
nunber = tk.Label(janela, text="bote algum numero")
nunber.place(x=60, y=10)

#botãos de 1 a 9 e o 0				
botão_1 = tk.Button(janela, text="1", command=primeiro)
botão_1.place(x=10, y=90)

botão_2 = tk.Button(janela, text="2", command=segundo)
botão_2.place(x=150, y=90)

botão_3 = tk.Button(janela, text="3", command=terçeiro)
botão_3.place(x=290, y=90)

botão_4 = tk.Button(janela, text="4", command=quarto)
botão_4.place(x=10, y=200)

botão_5 = tk.Button(janela, text="5", command=quinto)
botão_5.place(x=150, y=200)

botão_6 = tk.Button(janela, text="6", command=sesto)
botão_6.place(x=290, y=200)

botão_7 = tk.Button(janela, text="7", command=setimo)
botão_7.place(x=10, y=320)

botão_8 = tk.Button(janela, text="8", command=oitavo)
botão_8.place(x=150, y=320)

botão_9 = tk.Button(janela, text="9", command=nono)
botão_9.place(x=290, y=320)

botão_0 = tk.Button(janela, text="0", command=zero)
botão_0.place(x=150, y=420)

botãot = tk.Button(janela, text="+", command=en)
botãot.place(x=290, y=420)

botão_fim = tk.Button(janela, text="=", command=go)
botão_fim.place(x=10, y=420)

botão_apaga = tk.Button(janela, text="clear", command=paga)
botão_apaga.place(x=10, y=500)


janela.mainloop()