# class Car:
#     def __init__(self, brand, model):
#         self.brand = brand  # Instance attribute
#         self.model = model  # Instance attribute
#
# # Create objects (instances) of the Car class
# car1 = Car("Toyota", "Corolla")
# car2 = Car("Honda", "Civic")
#
# print(f"Car 1: {car1.brand} {car1.model}")
# print(f"Car 2: {car2.brand} {car2.model}")
#
# # Define a class for a simple calculator
# class Calculator:
#     def add(self, a, b):
#         return a + b
#
#     def subtract(self, a, b):
#         return a - b
#
# # Create an object (instance) of the Calculator class
# calc = Calculator()
#
# # Use the object to call methods
# print("Addition:", calc.add(10, 5))
# print("Subtraction:", calc.subtract(10, 5))
#
# class Dog:
#     # Class attribute
#     species = "Canis Familiaris"
#
#     def __init__(self, name, age):
#         # Instance attributes
#         self.name = name
#         self.age = age
#
# # Create objects
# dog1 = Dog("Buddy", 3)
# dog2 = Dog("Milo", 5)
#
# # Access class and instance attributes
# print(f"{dog1.name} is a {dog1.species} and is {dog1.age} years old.")
# print(f"{dog2.name} is a {dog2.species} and is {dog2.age} years old.")
#
# class Person:
#     def __init__(self, name, age):
#         # 'self' refers to the current instance
#         self.name = name
#         self.age = age
#
#     def greet(self):
#         # Using 'self' to access attributes
#         return f"Hello, my name is {self.name} and I am {self.age} years old."
#
# # Create an object
# person = Person("Alice", 30)
#
# # Call a method
# print(person.greet())
#
# class MathUtils:
#     # Static method: Doesn't use 'self' or 'cls'
#     @staticmethod
#     def is_even(number):
#         return number % 2 == 0
#
#     # Instance method: Uses 'self'
#     def double(self, number):
#         return number * 2
#
# # Use static method without creating an object
# print("Is 4 even?", MathUtils.is_even(4))
#
# # Create an object to use the instance method
# math_util = MathUtils()
# print("Double of 5:", math_util.double(5))
#
# class Book:
#     def __init__(self, title, author, pages):
#         # Initialize attributes when the object is created
#         self.title = title
#         self.author = author
#         self.pages = pages
#
#     def details(self):
#         return f"'{self.title}' by {self.author}, {self.pages} pages."
#
# # Create an object with attributes initialized
# book = Book("1984", "George Orwell", 328)
#
# # Call the method to display details
# print(book.details())
#
# # Define the AdvancedCalculator class
# class AdvancedCalculator:
#     # Class attribute shared by all instances
#     brand_name = "SuperCalc"
#
#     def __init__(self, model):
#         # Instance attributes initialized by __init__()
#         self.model = model
#         self.memory_value = 0  # Default memory value for each object
#
#     # Instance method to perform addition
#     def add(self, a, b):
#         return a + b
#
#     # Instance method to perform subtraction
#     def subtract(self, a, b):
#         return a - b
#
#     # Instance method to perform multiplication
#     def multiply(self, a, b):
#         return a * b
#
#     # Instance method to perform division with error handling for zero division
#     def divide(self, a, b):
#         if b != 0:
#             return a / b
#         else:
#             return "Error: Division by zero"
#
#     # Static method to check if a number is even
#     @staticmethod
#     def is_number_even(number):
#         return number % 2 == 0
#
#     # Method to display the calculator's information
#     def display_info(self):
#         print(f"Model: {self.model}, Brand: {AdvancedCalculator.brand_name}")
#
#
# # Create an instance of the AdvancedCalculator class
# calc1 = AdvancedCalculator("Model X")
#
# # Perform some calculations
# print(f"Addition: {calc1.add(10, 5)}")        # 15
# print(f"Subtraction: {calc1.subtract(10, 5)}")  # 5
# print(f"Multiplication: {calc1.multiply(10, 5)}")  # 50
# print(f"Division: {calc1.divide(20, 4)}")      # 5.0
#
# # Using the static method without creating an object
# print(f"Is 4 even? {AdvancedCalculator.is_number_even(4)}")  # True
#
# # Displaying calculator details
# calc1.display_info()
#
# # Define the Book class
# class Book:
#     def __init__(self, title, author):
#         # Instance attributes for title and author
#         self.title = title
#         self.author = author
#
#     # Method to return the book's details
#     def get_details(self):
#         return f"'{self.title}' by {self.author}"
#
#
# # Define the BookCollection class
# class BookCollection:
#     # Class attribute for collection name
#     collection_name = "My Favorite Books"
#
#     def __init__(self):
#         # Instance attribute to hold books as a list
#         self.books = []
#
#     # Method to add a book to the collection
#     def add_book(self, book):
#         self.books.append(book)
#
#     # Method to display all books in the collection
#     def display_books(self):
#         print(f"Collection: {self.collection_name}")
#         for book in self.books:
#             print(book.get_details())
#
#
# # Create book objects
# book1 = Book("1984", "George Orwell")
# book2 = Book("To Kill a Mockingbird", "Harper Lee")
#
# # Create a book collection object
# my_collection = BookCollection()
#
# # Add books to the collection
# my_collection.add_book(book1)
# my_collection.add_book(book2)
#
# # Display all books in the collection
# my_collection.display_books()




class Student:
    def __init__(self, sr_code, score):
        self.sr_code = sr_code
        self.score = score

# A list of student objects
students = [
    Student("SR2025001", 85),
    Student("SR2025002", 90),
    Student("SR2025003", 76),
    Student("SR2025004", 95),
    Student("SR2025005", 88)
]


sr_input = input("Enter your SR Code: ").strip()


found = False
for student in students:
    if student.sr_code == sr_input:
        print("Access Granted")
        print(f"Your score is: {student.score}")
        found = True
        break

if not found:
    print("SR Code not found.")
