import sys
from dbconn import connect_to_db
from user_queries import create_user, auth

#init global vars
conn = None
cursor = None 
current_user = None

def login():
    global current_user
    
    print("\n---LOGIN---")
    username = input("Username: ")
    password = input("Password: ")

    success, message = auth(cursor, conn, username, password)
    print(f"\n{message}\n")

    if success:
        current_user = username

def create_account():
    print("\n---CREATE ACCOUNT---")
    username = input("Username: ")
    password = input("Password: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")

    success, message = create_user(cursor, conn, username, password, first_name, last_name)

    print(f"\n{message}")

    if success:
        print("You can now login with your new account.\n")

def menu():
    print("Movie System")
    print("-------------------------")

    if current_user:
        print(f"Logged in as: {current_user}")
        print("\n1. Manage Collections")
        print("2. Search Movies")
        print("3. Rate/Watch Movies")
        print("4. Social Features")
        print("5. Logout")
        print("6. Exit")
    else: 
        print("\n1. Login")
        print("2. Create Account")
        print("3. Exit")
    
    return input("Please select an option: ")

def logged_in(choice):
    match choice:
        case "1":
            print("\nCollection Management - To be implemented")
        case "2":
            print("\nMovie Search - To be implemented")
        case "3":
            print("\nRate/Watch Movies - To be implemented")
        case "4":
            print("\nSocial Features - To be implemented")
        case "5":
            global current_user
            current_user = None
            print("Logged out successfully!")
        case "6":
            return False
        case _:
            print("Invalid choice! Please try again.")

def guest(choice):
    match choice:
        case "1":
            login()
        case "2":
            create_account()
        case "3":
            return False
        case _:
            print("Invalid choice! Please try again.")

    return True

def main():
    global conn, cursor

    print("Starting Movie Database System...")

    try:
        conn, cursor = connect_to_db()
        print("Connected to DB Successfully!")

        running = True
        while running:
            choice = menu()

            if current_user:
                running = logged_in(choice)
            else:
                running = guest(choice)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Closing Application...")

if __name__ == "__main__":
    main()