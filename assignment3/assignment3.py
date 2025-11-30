import json

# ---------------- BOOK CLASS -----------------

class Book:
    def __init__(self, title, author, isbn, status="available"):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.status = status

    def issue(self):
        self.status = "issued"

    def return_book(self):
        self.status = "available"

    def is_available(self):
        return self.status == "available"

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status
        }

    def __str__(self):
        return f"{self.title} | {self.author} | {self.isbn} | {self.status}"


# ---------------- LIBRARY INVENTORY -----------------

class LibraryInventory:
    def __init__(self):
        self.books = []
        self.load_books()

    def add_book(self, book):
        self.books.append(book)

    def search_by_title(self, title):
        for b in self.books:
            if b.title.lower() == title.lower():
                return b
        return None

    def search_by_isbn(self, isbn):
        for b in self.books:
            if b.isbn == isbn:
                return b
        return None

    def display_all(self):
        if not self.books:
            print("No books found.")
        for b in self.books:
            print(b)

    def save_books(self):
        data = [b.to_dict() for b in self.books]
        with open("books.json", "w") as f:
            json.dump(data, f)

    def load_books(self):
        try:
            with open("books.json", "r") as f:
                data = json.load(f)
                for item in data:
                    book = Book(item["title"], item["author"], item["isbn"], item["status"])
                    self.books.append(book)
        except:
            # file missing first time — ignore
            pass


# ---------------- MAIN MENU -----------------

library = LibraryInventory()

while True:
    print("\n=== LIBRARY MENU ===")
    print("1. Add Book")
    print("2. Issue Book")
    print("3. Return Book")
    print("4. View All Books")
    print("5. Search Book")
    print("6. Exit")

    ch = input("Enter choice: ")

    if ch == "1":
        t = input("Enter title: ")
        a = input("Enter author: ")
        i = input("Enter ISBN: ")

        b = Book(t, a, i)
        library.add_book(b)
        library.save_books()

        print("Book Added!")

    elif ch == "2":
        i = input("Enter ISBN to issue: ")
        b = library.search_by_isbn(i)

        if b and b.is_available():
            b.issue()
            library.save_books()
            print("Book Issued!")
        else:
            print("Book not found or already issued.")

    elif ch == "3":
        i = input("Enter ISBN to return: ")
        b = library.search_by_isbn(i)

        if b:
            b.return_book()
            library.save_books()
            print("Book Returned!")
        else:
            print("Book not found.")

    elif ch == "4":
        library.display_all()

    elif ch == "5":
        t = input("Enter title: ")
        b = library.search_by_title(t)

        if b:
            print(b)
        else:
            print("Book not found.")

    elif ch == "6":
        print("Goodbye!")
        break

    else:
        print("Invalid choice, try again.")
