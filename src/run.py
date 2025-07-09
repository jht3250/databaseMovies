import sys
from dbconn import connect_to_db
from user_queries import create_user, auth
from collection_queries import (
    create_collection, list_user_collections, 
    rename_collection, delete_collection, get_collection_stats
)

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
            manage_collections()
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

def manage_collections():
    while True:
        print("\n---COLLECTION MANAGEMENT---")
        print("1. View My Collections")
        print("2. Create New Collection")
        print("3. Rename Collection")
        print("4. Delete Collection")
        print("5. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        match choice:
            case "1":
                view_collections()
            case "2":
                create_new_collection()
            case "3":
                rename_collection()
            case "4":
                delete_collection()
            case "5":
                break
            case _:
                print("Invalid choice! Please try again.")

def view_collections():
    success, stats = get_collection_stats(cursor, current_user)
    
    if success:
        if stats:
            print("\nYour Collections:")
            print("-" * 70)
            print(f"{'ID':<5} {'Name':<30} {'Movies':<10} {'Total Runtime':<15}")
            print("-" * 70)
            for stat in stats:
                print(f"{stat['id']:<5} {stat['name']:<30} {stat['movie_count']:<10} {stat['runtime_formatted']:<15}")
            print("-" * 70)
        else:
            print("\nYou have no collections yet.")
    else:
        print(f"\nError: {stats}")
    
    input("\nPress Enter to continue...")

def create_new_collection():
    name = input("\nEnter collection name: ")
    
    if name.strip():
        success, message = create_collection(cursor, conn, current_user, name)
        print(f"\n{message}")
    else:
        print("\nCollection name cannot be empty!")
    
    input("\nPress Enter to continue...")

def rename_collection():
    # First show collections
    success, collections = list_user_collections(cursor, current_user)
    
    if success and collections:
        print("\nYour Collections:")
        for coll_id, coll_name in collections:
            print(f"ID: {coll_id} - {coll_name}")
        
        try:
            coll_id = int(input("\nEnter collection ID to rename: "))
            new_name = input("Enter new name: ")
            
            if new_name.strip():
                success, message = rename_collection(cursor, conn, coll_id, new_name)
                print(f"\n{message}")
            else:
                print("\nCollection name cannot be empty!")
        except ValueError:
            print("\nInvalid ID!")
    else:
        print("\nNo collections found!")
    
    input("\nPress Enter to continue...")

def delete_collection():
    # First show collections
    success, collections = list_user_collections(cursor, current_user)
    
    if success and collections:
        print("\nYour Collections:")
        for coll_id, coll_name in collections:
            print(f"ID: {coll_id} - {coll_name}")
        
        try:
            coll_id = int(input("\nEnter collection ID to delete: "))
            confirm = input(f"Are you sure you want to delete this collection? (y/n): ")
            
            if confirm.lower() == 'y':
                success, message = delete_collection(cursor, conn, coll_id)
                print(f"\n{message}")
            else:
                print("\nDeletion cancelled.")
        except ValueError:
            print("\nInvalid ID!")
    else:
        print("\nNo collections found!")
    
    input("\nPress Enter to continue...")

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