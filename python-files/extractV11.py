import xlrd
from PIL import ImageFont
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog


def browseFiles():
    global filename
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.*"),
                                                       ("all files",
                                                        "*.*")))

def openWindow(): # Opens the GUI
    root=Tk() # Is the window itself and every new item gets attached here
    finishtext = Label(root, text="") # Text-Label to show when the program is done.
    checkboxVar = IntVar() # To select between output with/without english translation (without doesn´t work at the moment. Somewhere js works with the translation and would have to work with undefined)
    openFileExplorer = Button(root, text="File browser", command=browseFiles) # To open an Explorer and select the Excel-file
    def retrieve_input(): # Method is called by the Commit-button and starts the "real" programm
        finishtext.pack()
        finishtext.config(text="Something went wrong.") # If something goes wrong, this text will appear (hopefully)
        searchWithLetter(filename, tablenames.get("1.0", "end-1c"), checkboxVar.get()) # Takes file where to get the data from, the tablenames and wether to read the english translation or not
        searchWithWord(filename, tablenames.get("1.0", "end-1c"), checkboxVar.get()) # Takes file where to get the data from, the tablenames and wether to read the english translation or not
        finishtext.config(text="The files are ready.") # After all is done, show this text.
    root.geometry("400x300")
    text = Label(root, text="Select the Excel-file")
    text.pack()
    openFileExplorer.pack()
    tabellentext = Label(root, text="Provide all table names as the given pattern:")
    tabellentext.pack()
    tablenames = Text(root, height=3, width=30)
    tablenames.insert(END, "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z") # Basic tablenames
    tablenames.pack()
    buttonCommit=Button(root, width=10, text="Commit", 
                        command=lambda: retrieve_input())
    buttonCommit.pack()
    checkbox = Checkbutton(root, text="With english translation", variable=checkboxVar)
    checkbox.pack()
    
    mainloop()

def get_pil_text_size(text, font_size, font_name):
    '''
    Returns the size of the given text in the size and font-style in pixels
    '''
    font = ImageFont.truetype(font_name, font_size)
    size = font.getlength(text)
    return size

def searchWithWord(url, tables, withEnglishTranslation):
    '''
    url: The path to the excel-file
    tables: the names of all tables
    withEnglishTranslation: Wether the english translation is wanted or not
    Creates a txt-file with javascript code in it. The code is used to search for an specific string in a word.
    '''
    open(url[0: -len(url.split('/')[-1])] + "searchWithWord.txt", 'w', encoding="utf-8").close() # Empty the previous file
    workbook = xlrd.open_workbook(url) # open the Excel-file
    f = open(url[0: -len(url.split('/')[-1])] + "searchWithWord.txt", "a", encoding="utf-8") # Start writing the js-file
    worksheet2 = workbook.sheet_by_name("Zusatz") # Here are some special sentences.
    # Just some information and definitions. To work on the js-file please open the generated one and paste it back to the python-file. Don´t edit js in the python-file.
    f.write('/*To add more words to the dictionary please continuo this pattern:\ndictionary.addPair("Searched word", "Title", "Explanation");\n\n\nPlease remember to add the new words to the "search with letter" too.\nWritten by Paul Gerfelder\n\n This is "Search with words"\n*/\n\nclass Eray{\n    constructor(){\n        this.words = [];\n        this.explanations = [];\n        this.keys = [];\n        this.engl = [];\n        this.matchingKeys = [];\n    }\n    addSearchOption(key, perfect){\n        if (perfect){\n            this.matchingKeys.unshift(key)\n        } else{\n            this.matchingKeys.push(key)\n        }\n    }\n    addPair(key, word, explanation, engl){\n        this.words[key]=word;\n        this.explanations[key]=explanation;\n        this.keys[this.keys.length]=key;\n        this.engl[key]=engl;   \n}\n    getWord(key){\n        return this.words[key];\n    }\n    getExplanation(key){\n        return this.explanations[key];\n    }\n    getKey(key){\n        return this.keys[key];\n    }\n    getEngl(key){\n         return this.engl[key];\n    }\n    getWordContains(key, number){\n        var gesetzt = 0;\n        for (let i=0;i<this.keys.length;i++){\n            if (this.keys[i].normalize("NFD").replace(/[\u0300-\u0326]/g, "").replace(/[\u0328-\u036f]/g, "")==key '  + ( '|| this.engl[this.keys[i].toLowerCase()]==key' if withEnglishTranslation else '') + '){\n                this.addSearchOption(this.keys[i], true);\n                gesetzt = 1;\n            }else if ((this.keys[i].normalize("NFD").replace(/[\u0300-\u0326]/g, "").replace(/[\u0328-\u036f]/g, "").includes(key) ' + ( '|| this.engl[this.keys[i]].toLowerCase().includes(key)' if withEnglishTranslation else '') + ')){\n                this.addSearchOption(this.keys[i], false);\n                gesetzt = 1;\n            }         \n        }\n        if (gesetzt){\n            if (number >= this.matchingKeys.length){\n                console.log("Länge" + this.matchingKeys.length);\n                number = this.matchingKeys.length -1;\n                p.SetVar("dictionaryCounter", number);\n                p.SetVar("dictionaryLastItem", true);\n            }\n            if (number >= this.matchingKeys.length - 1){\n                p.SetVar("dictionaryLastItem", true);\n            } else {\n                p.SetVar("dictionaryLastItem", false);\n            }\n            p.SetVar("dictionaryTitle", this.getWord(this.matchingKeys[number])' + (' + " (" + this.getEngl(this.matchingKeys[number]) + ")" ' if withEnglishTranslation else '') + ');\n            p.SetVar("dictionaryExplanation", this.getExplanation(this.matchingKeys[number]));\n        } else {\n            p.SetVar("dictionaryLastItem", true);\n        }\n    }\n }\n const dictionary = new Eray();\n')
    tables = tables.split(",") # get the tablenames as a list
    for i in tables:
        worksheet = workbook.sheet_by_name(i) # get the table
        counter = 1 # This is the y-coordinate of the cell to read.
        while(True): # The loop stops when there are no other words to read. (It ain´t pretty but it´s honest work)
            try: 
                description = worksheet.cell(counter, 1) # 0==Titel, 1==Descritpion, 2==English
                titel = worksheet.cell(counter, 0)
                try: # Knowledge: Python ignores columns and rows that are empty and if you want to get the value of a cell it is undefined. -> If all words in a table have no english translation this column is undefined and the program can´t find any words. That is the second try for.
                    engl = worksheet.cell(counter, 2).value
                except:
                    engl = ""
                if (withEnglishTranslation): # Depending if the english translation is required or not.
                    f.write('dictionary.addPair("' + titel.value.lower().replace('"', '\\"') + '", "' + titel.value.replace('"', '\\"') + '", "' + description.value.replace('"', '\\"') + '", "' + worksheet2.cell(5, 1).value.replace('"', '\\"') + engl.replace('"', '\\"') + '");\n')
                else:
                    f.write('dictionary.addPair("' + titel.value.lower().replace('"', '\\"') + '", "' + titel.value.replace('"', '\\"') + '", "' + description.value.replace('"', '\\"') + '");\n')
                counter += 1
            except:
                break
    f.write('                                                    //From here can be worked with the dictionary\nvar p=GetPlayer();                                  //Getting access to all variables of the project\nvar text=p.GetVar("dictionaryInput");               //Getting the input from the speech bubble\nvar number=p.GetVar("dictionaryCounter");\nif (number < 0){\n    number = 0;\np.SetVar("dictionaryCounter", 0);\n}\ntext = text.replaceAll("", "");                   //All new lines are removed\ntext = text.toLowerCase();                          //Set all the letters to lowercasing letters to evade problems with the correct writing.\ntext = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "")  //delete all accents\np.SetVar("dictionaryTitle", "' + worksheet2.cell(3, 1).value + '");                                          //If the searched word doesn´t exist in the dictionary\np.SetVar("dictionaryExplanation", "' + worksheet2.cell(4, 1).value + '");\n \ndictionary.getWordContains(text, number);\nconsole.log(number);')
    f.close()
    
def generateLineBreaks(titel, description):
    '''
    title: The title (and the english translation) of the word
    description: The description of the word

    Adds line breaks to the title or description so they are shown on the same height. Otherwise multiple titles under each other would not be on the same height as their matching description.
    '''
    descriptionTotal = ""
    titelTotal = ""
    descriptionWord = description.split()
    descriptionWithSpaces = descriptionWord[0]
    titelWord = titel.split()
    titelWithSpaces = titelWord[0]
    titelWidth = 180 # The width in pixels of the textbox for the title
    descriptionWidth = 400 # The width in pixels of the textbox for the description
    for i in range(1, len(descriptionWord), 1):
        if (get_pil_text_size(descriptionWithSpaces + " " + descriptionWord[i], 20, "arial.ttf")>=descriptionWidth): # For every character is checked if it is too much for the same line
            descriptionTotal = descriptionTotal + descriptionWithSpaces + "\\n" # If it is too long and an other line is needed, an line break is added to the title
            descriptionWithSpaces = descriptionWord[i]
        else:
            descriptionWithSpaces = descriptionWithSpaces + " " + descriptionWord[i] # Otherwise the character is simply added. (Words may not be perfectly split by syllables)
    descriptionTotal = descriptionTotal + descriptionWithSpaces + "\\n\\n" # After every title is at least one empty line
    for i in range(1, len(titelWord), 1): # If the title needs more lines than the description, line breaks are added to the description in the same way.
        if (get_pil_text_size(titelWithSpaces + " " + titelWord[i], 20, "arial.ttf")>=titelWidth):
            titelTotal = titelTotal + titelWithSpaces + "\\n"
            titelWithSpaces = titelWord[i]
        else:
            titelWithSpaces = titelWithSpaces + " " + titelWord[i]
    titelTotal = titelTotal + titelWithSpaces + "\\n\\n"
    for i in range(descriptionTotal.count("\\n"), titelTotal.count("\\n"), 1): # Evens the amount of line breaks in title and description
        descriptionTotal = descriptionTotal + "\\n"
    for i in range(titelTotal.count("\\n"), descriptionTotal.count("\\n"), 1):
        titelTotal = titelTotal + "\\n"
    return titelTotal.replace('"', '\\"'), descriptionTotal.replace('"', '\\"')


def searchWithLetter(url, tables, withEnglishTranslation):
    '''
    url: The path to the excel-file
    tables: the names of all tables
    withEnglishTranslation: Wether the english translation is wanted or not
    Creates a txt-file with javascript code in it. The code is used to search for all words with this letter as a capital
    '''
    open(url[0: -len(url.split('/')[-1])] + "searchWithLetter.txt", 'w', encoding="utf-8").close()
    workbook = xlrd.open_workbook(url)
    f = open(url[0: -len(url.split('/')[-1])] + "searchWithLetter.txt", "a", encoding="utf-8")
    f.write('/*  To add more words you must find the correct letter and add the title in the upper and the explanation in the lower line.\n    By using "\n" the following text will start in the next line. Use these to make the title and the matching explanation start in the same line\n    titles2.addPair("B", "Beam:\n\n\nBobbin:\nBatching:");\n    explanations2.addPair("B", "Warp yarns for one guide bar come from several sectional warp beams which are placed on a beam axis (general use).\nCarrier wrapped with yarn (Modul1)\nWinding the fabric on a carrier (Modul2)");\n\n This is "Search with letter"\n*/\n\nclass HashtTable{                               //code stolen from: https://linuxhint.com/javascript-hash-tables/#:~:text=In%20JavaScript%2C%20a%20“hash%20table,key%20within%20a%20hash%20table.\n    constructor(){\n        this.object = {};\n        this.size=0;\n        this.length=0;\n    }\n\n    hashFunc(key) {\n        return key.toString().length % this.size;\n    }\n    addPair(key, value) {\n        const hash = this.hashFunc(key);\n        if (!this.object.hasOwnProperty(hash)) {\n             this.object[hash] = {};\n        }\n        if (!this.object[hash].hasOwnProperty(key)) {\n              this.length++;\n        }\n            this.object[hash][key] = value;\n    }\n    searchFunction(key) {\n        const hash = this.hashFunc(key);\n        if (this.object.hasOwnProperty(hash) && this.object[hash].hasOwnProperty(key)) {\n                return this.object[hash][key];\n            } else {\n                return null;\n            }\n        }\n}\n                                                                                                    //Fill the Dictionary\nconst titles2 = new HashtTable();\nconst explanations2 = new HashtTable();')
    tables=tables.split(",")
    worksheet2 = workbook.sheet_by_name("Zusatz")
    for i in tables:
        print(i) # shows the progress of the program.
        worksheet = workbook.sheet_by_name(i)
        counter = 1
        descriptionTotal = ""
        titelTotal = ""
        while(True):
            try: 
                description = worksheet.cell(counter, 1).value
                titel = worksheet.cell(counter, 0).value
                if (withEnglishTranslation):
                    try:
                        titel = titel + " (" + worksheet2.cell(5, 1).value + " " + worksheet.cell(counter, 2).value + ")"
                    except:
                        pass
                titel, description = generateLineBreaks(titel, description)
                counter += 1
                titelTotal = titelTotal + titel
                descriptionTotal = descriptionTotal + description
            except:
                break
        if (titelTotal == ""):
            f.write('titles2.addPair("' + i + '", "");\n')
            f.write('explanations2.addPair("' + i + '", "' + worksheet2.cell(2, 1).value + ' ' + i + ' ");\n')
        if (titelTotal != ""):
            f.write('titles2.addPair("' + i + '", "' + titelTotal + '");\n')
            f.write('explanations2.addPair("' + i + '", "' + descriptionTotal + '");\n')
    f.write('var p=GetPlayer();\nvar text=p.GetVar("dictionaryLetter");\n//text.toLowerCase();\np.SetVar("dictionaryTitleLetter", titles2.searchFunction(text));\np.SetVar("dictionaryExplanationLetter", explanations2.searchFunction(text));')


openWindow()