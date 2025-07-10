import sys
from dbconn import connect_to_db
from user_queries import create_user, auth
from collection_queries import *

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
        print("5. Add Movie to Collection")
        print("6. Remove Movie from Collection")
        print("7. View Movies in Collection")
        print("8. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        match choice:
            case "1":
                view_collections()
            case "2":
                create_new_collection()
            case "3":
                rename_col()
            case "4":
                delete_collection()
            case "5":
                add_movie_col()
            case "6":
                remove_movie_col()
            case "7":
                view_movies_col()
            case "8":
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

def rename_col():
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

def add_movie_col():
    success, collections = list_user_collections(cursor, current_user)
    
    if success and collections:
        print("\nYour Collections:")
        for coll_id, coll_name in collections:
            print(f"ID: {coll_id} - {coll_name}")
        
        try:
            coll_id = int(input("\nEnter collection ID: "))
            
            # Verify ownership
            if collection_auth(cursor, current_user, coll_id):
                movie_id = int(input("Enter movie ID to add: "))
                success, message = add_movie_to_collection(cursor, conn, coll_id, movie_id)
                print(f"\n{message}")
            else:
                print("\nCollection not found or you don't have permission!")
        except ValueError:
            print("\nInvalid ID!")
    else:
        print("\nNo collections found! Create a collection first.")
    
    input("\nPress Enter to continue...")

def remove_movie_col():
    success, collections = list_user_collections(cursor, current_user)
    
    if success and collections:
        print("\nYour Collections:")
        for coll_id, coll_name in collections:
            print(f"ID: {coll_id} - {coll_name}")
        
        try:
            coll_id = int(input("\nEnter collection ID: "))
            
            if collection_auth(cursor, current_user, coll_id):
                success, movies = list_movies_in_collection(cursor, coll_id)
                if success and movies:
                    print("\nMovies in this collection:")
                    for movie in movies:
                        print(f"ID: {movie[0]} - {movie[1]} ({movie[3]})")
                    
                    movie_id = int(input("\nEnter movie ID to remove: "))
                    success, message = remove_movie_from_collection(cursor, conn, coll_id, movie_id)
                    print(f"\n{message}")
                else:
                    print("\nNo movies in this collection!")
            else:
                print("\nCollection not found or you don't have permission!")
        except ValueError:
            print("\nInvalid ID!")
    else:
        print("\nNo collections found!")
    
    input("\nPress Enter to continue...")

def view_movies_col():
    success, collections = list_user_collections(cursor, current_user)
    
    if success and collections:
        print("\nYour Collections:")
        for coll_id, coll_name in collections:
            print(f"ID: {coll_id} - {coll_name}")
        
        try:
            coll_id = int(input("\nEnter collection ID to view: "))
            
            # Verify ownership
            if (cursor, current_user, coll_id):
                success, movies = list_movies_in_collection(cursor, coll_id)
                if success and movies:
                    print("\nMovies in this collection:")
                    print("-" * 70)
                    print(f"{'ID':<8} {'Title':<40} {'Length':<10} {'Rating':<8}")
                    print("-" * 70)
                    for movie in movies:
                        length_str = f"{movie[2]} min" if movie[2] else "N/A"
                        print(f"{movie[0]:<8} {movie[1][:40]:<40} {length_str:<10} {movie[3]:<8}")
                    print("-" * 70)
                else:
                    print("\nNo movies in this collection!")
            else:
                print("\nCollection not found or you don't have permission!")
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