print('program to find bmi')
wt=float(input('ENTER YOUR WEIGHT(KG): '))
ht=float(input('ENTER YOUR HEIGHT(M): '))
bmi=wt/ht**2
print('YOUR BMI IS: ',bmi)
if bmi<18.5:
  print('OOPS! YOU ARE UNDERWEIGHT.')
elif bmi<24.9:
  print('GOOD! YOU ARE HEALTHY.')
elif bmi<29.9:
  print('YOU ARE OVERWEIGHT.')
elif bmi<30:
  print('YOU ARE SUFFERING WITH OBESITY.')

