print("BMI CALCULATOR FOR MENS AND WOMEN")
a=float(input("Enter your weight in kgs"))
b=float(input("Enter your height in meters"))
c=a/(b**2)
print("Your BMI is : ",c)
if 18.5<=c<=24.9:
    print("Normal Weight")
elif 25<=c<=29.9:
    print("Over Weight")
elif 30.0<=c<=34.9:
    print("Obesity Class 1")
elif 35<=c<=39.9:
    print("Obesity Class 2")
print("MADE BY AMRIT")