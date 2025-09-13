
# Online Python - IDE, Editor, Compiler, Interpreter


capital = int(input('Enter whole capital in USDT: '))
#risk = int(input('Enter risk percentage: '))
#RR = int(input('Enter reward/risk: '))
Margin = capital*5/100   #risk=5
ExpectedP= Margin*3      #RR=3

print (" ")
print (f'Money at risk (Margin) is: {Margin}$')
print (f'Expected profit is {ExpectedP}$')

#print(f'Sum of {a} and {b} is {sum(a, b)}')
