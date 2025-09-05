from tkinter import *
from tkinter import ttk
## Creating the student class

class Student :

    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    @classmethod
    def calculateAvg(self, grades) :
        n = len(grades)

        res = 0

        for i in range(n) :
            res = res + int(grades[i])

        ans = res / n

        return ans, res, n
    
students = {}
std = []
avg = []
grading = []

def turn2List(str) :
    arr = []
    for x in str.split() :
        arr.append(int(x))
    return arr


def addNew() :
        name = StringVar()
        getName = ttk.Entry(mainframe, textvariable=name)
        getName.grid(column=1, row=3)
        grades = StringVar()
        getGrades = ttk.Entry(mainframe, textvariable=grades )
        getGrades.grid(column=1, row=4)
        def set2Student() :
            s = Student(name.get(), grades.get())
            nameText.config()
            std.append(s.name)
            students[name.get()] = turn2List(grades.get())
            avg.append(s.calculateAvg(turn2List(grades.get())))
            grading.append(grades.get())
            print(name.get(), grades.get(), std, students, avg, grading)
        nameText = ttk.Label(mainframe, text='Enter the name of the student')
        nameText.grid(column=2, row=3)
        gradeText = ttk.Label(mainframe, text='Enter the grades of the student')
        gradeText.grid(column=2, row=4)
        button5 = ttk.Button(mainframe, text='Submit', command=set2Student)
        button5.grid(column=1, row=5)

def showStudents() :
     for i in range(len(std)) :
        namesText = ttk.Label(mainframe, text=std[i])
        namesText.grid(column=4, row=i + 3)

def findAvg() :
    nameOfAvg = StringVar()
    nameOfAvgText = ttk.Entry(mainframe, textvariable=nameOfAvg)
    nameOfAvgText.grid(column=7, row=3)
    someWords = ttk.Label(mainframe, text='Enter the name of the student')
    someWords.grid(column=8, row=3)
    def cal() :
        for a in range(len(std)) :
            if nameOfAvg.get() == std[a] :
                avgLabel = ttk.Label(mainframe, text=avg[a][0])
                avgLabel.grid(column=7, row=a+5)
                
    button6 = ttk.Button(mainframe, text='Calculate Average', command=cal)
    button6.grid(column=7, row=4)
        
def save2File() :
        f = open('grades.txt', 'a')
        for b in range(len(std)) : 
            f.write(f'{std[b]} : {grading[b]}')

## program runnning in a loop

root = Tk()
root.title('Student Managment System')
ttk.Style().theme_use("clam")
root.geometry('1700x500')

mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_Text = ttk.Label(mainframe, text="WELCOME!, Choose one of the following options")
main_Text.grid(column=5, row=1)

button1 = ttk.Button(mainframe, text='Add a Student', command=addNew)
button1.grid(column=1, row=2)

button2 = ttk.Button(mainframe, text='Show All Students', command=showStudents)
button2.grid(column=4, row=2)

button3 = ttk.Button(mainframe, text='Find the Average Of the Student', command=findAvg)
button3.grid(column=7, row=2)

button4 = ttk.Button(mainframe, text='Save to a File (grades.txt)', command=save2File)
button4.grid(column=10, row=2)

root.mainloop()


        

