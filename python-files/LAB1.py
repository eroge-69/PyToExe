#Raizen Miel Q. Songco
#BCPET-1104
#Laboratory Activity No.1
#September 3, 2025
print("ABC Bank")
print("Client Investment Information Form") 
print()
print("Client Information")
LastName = input("\tLast Name:") 
FirstName = input("\tFirst Name:") 
MiddleName = input("\tMiddle Name:") 
number = input("\tContact Number:") 
address = input("\tAddress: ")
print("Investment Details")
Amount = float(input("\tAmount: Php"))
Interest = float(input("\tAnnual Interest Rate:")) 
Investment = int(input("\tInvestment Term:"))
print("-----Investment Details-----")
print("Full Name:", LastName+"," , FirstName ,MiddleName) 
print("Contact Number:", number)
print ("Address:", address)
print("Principal Amount: php", Amount)
print("Annual Interest Rate:", Interest)
print("Investment Term:", Investment, "year/s")
Increase = (Amount/100)*Interest*Investment
Value = Amount+Increase
print("Future Value: Php", Value)
print("---End of The Form---")