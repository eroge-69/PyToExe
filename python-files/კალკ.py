Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> def calculator():
...     print("მოგესალმები კალკულატორში!")
...     
...     while True:
...         try:
...             num1 = float(input("შეიყვანე პირველი რიცხვი: "))
...             operator = input("შეიყვანე ოპერატორი (+, -, *, /): ")
...             num2 = float(input("შეიყვანე მეორე რიცხვი: "))
... 
...             if operator == "+":
...                 result = num1 + num2
...             elif operator == "-":
...                 result = num1 - num2
...             elif operator == "*":
...                 result = num1 * num2
...             elif operator == "/":
...                 if num2 != 0:
...                     result = num1 / num2
...                 else:
...                     print("ნულზე გაყოფა შეუძლებელია!")
...                     continue
...             else:
...                 print("არასწორი ოპერატორი!")
...                 continue
... 
...             print(f"შედეგი: {result}")
...         
...         except ValueError:
...             print("გთხოვ, შეიყვანე რიცხვები სწორი ფორმატით.")
... 
...         cont = input("გინდა კიდევ რამე გამოთვლა? (კი/არა): ")
...         if cont.lower() != "კი":
...             print("ნახვამდის!")
...             break
... 
