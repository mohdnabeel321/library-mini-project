import mysql.connector

# Database setup
def create_database():
    try:
        mydb = mysql.connector.connect(host="localhost", user="root", password="12345678")
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS library")
        mycursor.execute("USE library")
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                author VARCHAR(255),
                isbn VARCHAR(50),
                student_id VARCHAR(255),
                student_name VARCHAR(255),
                borrow_date DATE,
                return_date DATE
            )
        """)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Something went wrong: {err}")
    finally:
        mycursor.close()
        mydb.close()

class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.student_id = None
        self.student_name = None
        self.borrow_date = None
        self.return_date = None

    def __str__(self):
        status = (f" (Borrowed by ID: {self.student_id}, Name: {self.student_name}, "
                  f"Borrow Date: {self.borrow_date}, Return Date: {self.return_date}") if self.student_id else ""
        return f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}{status})"

class Library:
    def __init__(self):
        self.mydb = mysql.connector.connect(host="localhost", user="root", password="12345678", database="library")
        self.mycursor = self.mydb.cursor()

    def close(self):
        self.mycursor.close()
        self.mydb.close()

    def add_book(self, book):
        sql = "INSERT INTO books (title, author, isbn) VALUES (%s, %s, %s)"
        self.mycursor.execute(sql, (book.title, book.author, book.isbn))
        self.mydb.commit()
        print(f"Book '{book.title}' added to the library.")

    def remove_book(self, title):
        sql = "DELETE FROM books WHERE title = %s"
        self.mycursor.execute(sql, (title,))
        self.mydb.commit()
        if self.mycursor.rowcount > 0:
            print(f"Book '{title}' removed from the library.")
        else:
            print(f"Book '{title}' not found in the library.")

    def find_book(self, title):
        sql = "SELECT * FROM books WHERE title = %s"
        self.mycursor.execute(sql, (title,))
        result = self.mycursor.fetchone()
        if result:
            book = Book(result[1], result[2], result[3])
            book.student_id = result[4]
            book.student_name = result[5]
            book.borrow_date = result[6]
            book.return_date = result[7]
            return book
        return None

    def display_books(self):
        self.mycursor.execute("SELECT * FROM books")
        books = self.mycursor.fetchall()
        if books:
            print("Books in the Library:")
            for row in books:
                print(Book(row[1], row[2], row[3]))
        else:
            print("The library is empty.")

    def borrow_book(self, title, student_id, student_name):
        book = self.find_book(title)
        if book and not book.student_id:
            sql = """
                UPDATE books
                SET student_id = %s, student_name = %s, borrow_date = CURDATE(), return_date = DATE_ADD(CURDATE(), INTERVAL 14 DAY)
                WHERE title = %s
            """
            self.mycursor.execute(sql, (student_id, student_name, title))
            self.mydb.commit()
            if self.mycursor.rowcount > 0:
                print(f"Book '{title}' borrowed by {student_name} (ID: {student_id}).")
            else:
                print(f"Book '{title}' is already borrowed or not found.")
        else:
            print(f"Book '{title}' is either not available or already borrowed.")

    def return_book(self, title, student_id):
        sql = """
            UPDATE books
            SET student_id = NULL, student_name = NULL, borrow_date = NULL, return_date = NULL
            WHERE title = %s AND student_id = %s
        """
        self.mycursor.execute(sql, (title, student_id))
        self.mydb.commit()
        if self.mycursor.rowcount > 0:
            print(f"Book '{title}' returned by student ID {student_id}.")
        else:
            print(f"Book '{title}' was not borrowed by student ID {student_id}.")

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class LibrarySystem:
    def __init__(self):
        self.library = Library()
        self.admin = User("bookstall", "12345678")
        self.student = User("student", "12345678")  # Student credentials
        self.current_user = None

    def login(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        if username == self.admin.username and password == self.admin.password:
            self.current_user = self.admin
            print("Admin logged in successfully.")
        elif username == self.student.username and password == self.student.password:
            self.current_user = self.student
            print("Student logged in successfully.")
        else:
            print("Invalid credentials. Try again.")

    def logout(self):
        self.current_user = None
        print("Logged out successfully.")

    def admin_operations(self):
        while True:
            choice = input("\nAdmin Menu: \n1. Add Book\n2. Remove Book\n3. Display Books\n4. Logout\nChoose an option: ")
            if choice == '1':
                title = input('Enter the title: ')
                author = input('Enter the author: ')
                isbn = input("Enter the ISBN: ")
                book = Book(title, author, isbn)
                self.library.add_book(book)
            elif choice == '2':
                title = input('Enter the title of the book to remove: ')
                self.library.remove_book(title)
            elif choice == '3':
                self.library.display_books()
            elif choice == '4':
                self.logout()
                break
            else:
                print("Invalid option. Please try again.")

    def student_operations(self):
        while True:
            choice = input("\nStudent Menu: \n1. Display Books\n2. Borrow Book\n3. Return Book\n4. Logout\nChoose an option: ")
            if choice == '1':
                self.library.display_books()
            elif choice == '2':
                title = input('Enter the title of the book to borrow: ')
                student_id = input('Enter your student ID: ')
                student_name = input('Enter your name: ')
                self.library.borrow_book(title, student_id, student_name)
            elif choice == '3':
                title = input('Enter the title of the book to return: ')
                student_id = input('Enter your student ID: ')
                self.library.return_book(title, student_id)
            elif choice == '4':
                self.logout()
                break
            else:
                print("Invalid option. Please try again.")

    def run(self):
        while True:
            choice = input("1. Login as Admin\n2. Login as Student\n3. Exit\nChoose an option: ")
            if choice == '1':
                self.login()
                if self.current_user:
                    self.admin_operations()
            elif choice == '2':
                self.login()  # Login as student now handled by the login method
                if self.current_user:
                    self.student_operations()
            elif choice == '3':
                print("Exiting the library management system.")
                break
            else:
                print("Invalid option. Please try again.")

# Create database and run the Library Management System
if __name__ == "__main__":
    create_database()
    system = LibrarySystem()
    system.run()