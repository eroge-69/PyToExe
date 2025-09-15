students={}
n=int(input("Enter number of students:"))
for i in range(n):
    name=input(f"Enter name of student {i+1}:")
    marks=int(input(f"Enter marks of {name}:"))
    students[name]=marks

    for name,marks in students.items():
        if marks>90:
            grade="A"
        elif marks>=80:
            grade="B"
        elif marks>70:
            grade="C"
        else:
            grade="D"
        print(f"{name}'s grade={grade}")

sorted_students=sorted(students.items(),key=lambda items:items[1],reverse=True)

print("\n---Students Ranks---")
rank=1
previous_marks=None

for i,(name,marks) in enumerate(sorted_students,start=1):
    if marks!=previous_marks:
        rank=i

    print(f"Rank {i}: {name} with {marks} marks")
    previous_marks=marks
