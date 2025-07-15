import json
import os

class library ():
    def __init__(self):
        pass


class Book (library):
    
    def __init__(self):
        pass

    def add_book():
        book_info = {
            "name": input("Enter book name: "),
            "author": input("Enter book author: "),
        }

        try:
            book_info["pages"] = int(input("Enter book page: "))
        except ValueError:
            print("Invalid page number. Please enter a number.")
            return

        # اگر فایل وجود داشت، آن را بخوان، وگرنه لیست جدید بساز
        if os.path.exists('book_info.json'):
            with open('book_info.json', 'r') as f:
                try:
                    books = json.load(f)
                except json.JSONDecodeError:
                    books = []
        else:
            books = []

        # افزودن کتاب جدید به لیست
        books.append(book_info)

        # ذخیره دوباره کل لیست در فایل
        with open('book_info.json', 'w') as f:
            json.dump(books, f, indent=4)

        print("\nBook saved successfully!")
        print("-----------------------")
        print(f"Book name: {book_info['name']}")
        print(f"Book author: {book_info['author']}")
        print(f"Book pages: {book_info['pages']}")
        print("-----------------------\n")


    def see_books():
        if not os.path.exists('book_info.json'):
            print("No book data found.")
            return

        with open('book_info.json', 'r') as f:
            try:
                books = json.load(f)
            except json.JSONDecodeError:
                print("Error: Could not read the book list.")
                return

        if not books:
            print("No books in the list.")
            return

        print("\nAll Books:")
        print("-----------------------")
        for i, book in enumerate(books, start=1):
            print(f"Book {i}:")
            print(f"  Name  : {book['name']}")
            print(f"  Author: {book['author']}")
            print(f"  Pages : {book['pages']}")
            print("-----------------------")

    def del_book():

        if not os.path.exists('book_info.json'):
            print("No book data found.")
            return

        with open('book_info.json', 'r') as f:
            try:
                books = json.load(f)
            except json.JSONDecodeError:
                print("Error reading book data.")
                return

        if not books:
            print("No books to delete.")
            return

        # نمایش لیست کتاب‌ها
        print("\nAll Books:")
        print("-----------------------")
        for i, book in enumerate(books, start=1):
            print(f"{i}. {book['name']} by {book['author']} ({book['pages']} pages)")
        print("-----------------------")

        try:
            index = int(input("Enter the book number you want to delete: ")) - 1
        except ValueError:
            print("Invalid input.")
            return

        if index < 0 or index >= len(books):
            print("Index out of range.")
            return

        removed = books.pop(index)  # حذف واقعی کتاب

        with open('book_info.json', 'w') as f:
            json.dump(books, f, indent=4)

        print(f"Book '{removed['name']}' deleted successfully.")

class Eror ():
    def __init__(self):
        pass
    def megdar():
        print("Megdar eshtebah ast!")


def welcome ():
    print("\n\n**********************\nWelcome to my library!\n**********************\n\n")

def menu_list ():
    print("1-Enter book\n2-See Inentory\n3-Delete Book\n0-exit\n\nPlease Enter your act")

    menu = int(input(">"))
    return menu

#-------------------------------------------------------------




#main----------
welcome()

menu = 11
while menu != 0:
    menu = menu_list()
    if menu == 1:
        Book.add_book()
        menu = 10
    elif menu == 2:
        Book.see_books()
        menu = 10
    elif menu == 3:
        Book.del_book()
        menu = 10
    elif menu == 10:
        menu_list()
    elif menu == 0:
        break
    else:
        Eror.megdar()
        menu_list()

print("\n***********\nBe omid didar!\n***********")



