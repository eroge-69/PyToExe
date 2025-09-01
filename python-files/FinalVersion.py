# Import Module
from tkinter import *
#import periodictable
from mendeleev import *
# create root window
root = Tk()
# root window title and dimension
root.title("Periodic Table Details Finder")
# Set geometry(widthxheight)
root.geometry('500x2000')

# adding a label to the root window
lbl = Label(root, text = "Please enter the atmoic number: ", fg = "Red",font=("Arial", 12, "bold"))
          #  ,anchor=CENTER,justify=RIGHT)
lbl.grid()

# adding Entry Field
txt = Entry(root, width=10)
txt.grid(column =1, row =0)
# function to display user text when 
# button is clicked
def clicked():
    try:
        finalAns = ""
        elementToBeConsidered = element(int(txt.get().strip()))
        finalAns = finalAns + "Atomic Mass Number: "+ str(elementToBeConsidered.mass_number)
        finalAns = finalAns + "\nSymbol: " + str(elementToBeConsidered.symbol)
        finalAns = finalAns + "\nAtomic Number: "+ str(elementToBeConsidered.atomic_number)
        finalAns = finalAns + "\nName: "+ str(elementToBeConsidered.name)
        finalAns = finalAns + "\nName Origin: "+ str(elementToBeConsidered.name_origin)
        finalAns = finalAns + "\nAtomic Weight: "+ str(elementToBeConsidered.atomic_weight)
        finalAns = finalAns + "\nDiscoverers Information: "+ str(elementToBeConsidered.discoverers)+","+str(elementToBeConsidered.discovery_location)+","+str(elementToBeConsidered.discovery_year)
        finalAns = finalAns + "\nElectronic Configuration: " + str(elementToBeConsidered.ec)
        finalAns = finalAns + "\nBlock Information: "+str(elementToBeConsidered.block)
        finalAns = finalAns + "\nGroup Name Information: " + str(elementToBeConsidered.group.name)
        finalAns = finalAns + "\nPrice per kg: $" + str(elementToBeConsidered.price_per_kg)
        """
        listOfElements = dir(elementToBeConsidered)
        print(listOfElements)
        
        Atomic_no = int(txt.get().strip())
        element = periodictable.elements[Atomic_no]
        finalAns = finalAns + "Atomic Number: "+ str(element.number)
        finalAns = finalAns + "\nSymbol: "+ str(element.symbol)
        finalAns = finalAns + "\nName: "+ str(element.name).capitalize()
        finalAns = finalAns + "\nAtomic Mass: "+ str(element.mass)
        #listOfElements = dir(element)
        #print(listOfElements)
        #finalAns = finalAns + "\nCrystal_structure: "+ str(element.crystal_structure)
        """
    except ValueError:
        finalAns = "Please enter a valid atomic number."
    except KeyError:
        finalAns = "The entered atomic number does not exist in the periodic table."
    finally:
        finalAns = finalAns + "\n ***** "
        lbl1 = Label(text=finalAns,fg="Green",font=("Arial", 10))
        lbl1.grid()
        btn.configure(state='disabled')
        txt.configure(state='disabled')
# button widget with red color text inside
btn = Button(root, text = "Find the details" ,fg = "Blue", command=clicked,font=("Arial", 12, "bold"))
# Set Button Grid
btn.grid(column=0, row=2)

# Execute Tkinter
root.mainloop()
