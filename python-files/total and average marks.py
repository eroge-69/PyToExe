m = float(input("Enter marks for subject 1:"))
n = float(input("Enter marks for subject 2:"))
o = float(input("Enter marks for subject 3:"))
p = float(input("Enter marks for subject 4:"))
q = float(input("Enter marks for subject 5:"))
total= m+n+o+p+q
average =total/5
if average >= 90:
        grade = 'A+'

elif average >= 80:
        grade = 'A'
elif average >= 70:
        grade = 'B'
elif average >= 60:
        grade = 'C'
elif average >= 50:
        grade = 'D'
else :
        grade = fail
print(total)
print(average)



