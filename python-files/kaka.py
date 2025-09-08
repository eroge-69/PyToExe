print("Buonasera, sono kakapuzzino il programmino ")
name=input("Come ti chiami bella gnocca? ")
age=int(input(f"Quanti anni hai {name}? "))
if age < 18:
    print("CBCR")
    input()
elif age > 50:
    print("Vai a nanna vecchiaccia")
    input()
else:
    print("Molto bene, voglio fare un gioco con te.")
    print(f"Ora leggerò la tua mente cara {name}, sempre che ci sia qualcosa lì dentro.")
    print("Pensa ad un numero da 1 a 20.")
    print("...")
    print("...")
    print("...")
    print("Ci sei?")
    risp=input("Dammi un si o un no ")
    if risp == "no":
          print("Porco il dio, me ne vado ciao")
          input()
    else:
          print("Bene, ora ti darò una serie di semplici operazioni da svolgere "
          "sul numero che stai pensando, ti chiedo di confermarmi ad ogni "
          "passaggio, digitando un \'fatto\', che il tuo cervello è ancora "
          "in funzione e non è esploso.")
          risp2=input("Scrivimi un \'fatto\' come prova ")
          if risp2 != "fatto":
              print("Porco il dio, me ne vado ciao")
              input()
          else:
              risp3=input("Moltiplica il numero per 4 ")
              if risp3 != "fatto":
                  print("Porco il dio, me ne vado ciao")
                  input()
              else:
                  risp4=input("Sommaci 8 ")
                  if risp4 != "fatto":
                      print("Porco il dio, me ne vado ciao")
                      input()
                  else:
                      risp5=input("Dividilo per 2 ")
                      if risp5 != "fatto":
                          print("Porco il dio, me ne vado ciao")
                          input()
                      else:
                          risp6=input("Sottrai 1 ")
                          if risp2 != "fatto":
                              print("Porco il dio, me ne vado ciao")
                              input()
                          else:
                              numop=int(input("Tutto bene? Moltiplica ancora il risultato per 3 e scrivimi "
                              "che numero hai ottenuto "))
                              num=int((numop-9)/6)
                              print(f"Il numero a cui avevi pensato è... {num}")
                              print("MUAHAHAHAHAHAHAHAHAHA")
                              print("That's all folks, bye!")
                              input()
              
          

    
