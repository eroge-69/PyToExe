dizionario= {
    "pReverse" : 'a',
    "X" : 'b',
    "frecciaAlto" : 'c',
    "croceMoltoStorta" : 'd',
    "dueSpade" : 'e',
    "roboidaleX" : 'f',
    "fReverse" : 'g',
    "doppiaX" : 'h',
    "croceMenoStorta" : 'i',
    "tomba" : 'k',
    "doppiaFreverse" : 'l',
    "beta" : 'm',
    "maggiore" : 'n',
    "gReverse" : 'o',
    "omino" : 'p',
    "hStorta" : 'r',
    "piramide" : 's',
    "Y" : 't',
    "clessidraOrizzontale" : 'u',
    "M" : 'v',
    "scala" : 'z',
    "spazio" : ' '


}
chiave_che_cerco = "non exit"

array = []



while(chiave_che_cerco != "exit"):
    
    chiave_che_cerco = input("chiave che cerco (scrivi exit per uscire) ")

    if chiave_che_cerco in dizionario:
        array.append(dizionario[chiave_che_cerco])
        print(f"Array finale '{array}'")
        

    else:
        # If the key isn't found, let the user know
        print(f"La chiave '{chiave_che_cerco}' non è presente nel dizionario.")
