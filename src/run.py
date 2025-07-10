import sys
from dbconn import connect_to_db
from user_queries import create_user, auth
from collection_queries import *
from movie_queries import search_movies, sort_movies, get_movie_details
from rating_queries import rate_movie, get_user_rating, list_user_ratings, remove_rating, get_top_rated_movies
from watch_queries import watch_movie, watch_collection, get_watch_history, get_user_watch_stats, get_recently_watched

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
            search_movies_menu()
        case "3":
            rate_watch_menu()
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

def search_movies_menu():
    """Movie search submenu"""
    search_results = []  # Store results for re-sorting
    
    while True:
        print("\n--- MOVIE SEARCH ---")
        print("1. Search by Title")
        print("2. Search by Cast Member")
        print("3. Search by Studio")
        print("4. Search by Genre")
        print("5. Search by Release Year")
        
        if search_results:
            print("\n--- Sort Options ---")
            print("6. Sort by Title")
            print("7. Sort by Studio")
            print("8. Sort by Genre")
            print("9. Sort by Year")
            print("10. View Movie Details")
        
        print("\n0. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        match choice:
            case "1" | "2" | "3" | "4" | "5":
                # Perform new search
                search_types = {
                    "1": ("title", "Enter movie title: "),
                    "2": ("cast", "Enter cast member name: "),
                    "3": ("studio", "Enter studio name: "),
                    "4": ("genre", "Enter genre: "),
                    "5": ("release_date", "Enter year (e.g., 2023): ")
                }
                
                search_type, prompt = search_types[choice]
                search_term = input(prompt)
                
                if search_term.strip():
                    success, results = search_movies(cursor, search_term, search_type)
                    if success:
                        search_results = results
                        display_movie_results(search_results)
                    else:
                        print(f"\nError: {results}")
                else:
                    print("\nSearch term cannot be empty!")
                    
            case "6" | "7" | "8" | "9":
                # Sort existing results
                if search_results:
                    sort_options = {
                        "6": "title",
                        "7": "studio", 
                        "8": "genre",
                        "9": "year"
                    }
                    sort_by = sort_options[choice]
                    
                    order = input("Sort order (asc/desc) [default: asc]: ").lower()
                    if order not in ['asc', 'desc']:
                        order = 'asc'
                    
                    search_results = sort_movies(search_results, sort_by, order)
                    display_movie_results(search_results)
                else:
                    print("\nNo results to sort!")
                    
            case "10":
                # View movie details
                if search_results:
                    try:
                        movie_id = int(input("\nEnter movie ID for details: "))
                        success, movie = get_movie_details(cursor, movie_id)
                        if success:
                            display_movie_details(movie)
                        else:
                            print(f"\nError: {movie}")
                    except ValueError:
                        print("\nInvalid movie ID!")
                else:
                    print("\nNo results to view!")
                    
            case "0":
                break
                
            case _:
                print("Invalid choice! Please try again.")
    
    input("\nPress Enter to continue...")

def display_movie_results(movies):
    """Display movie search results in a formatted table"""
    if not movies:
        print("\nNo movies found!")
        return
    
    print(f"\nFound {len(movies)} movie(s):")
    print("-" * 120)
    print(f"{'ID':<8} {'Title':<40} {'Year':<6} {'Rating':<6} {'Length':<8} {'User Rating':<12}")
    print("-" * 120)
    
    for movie in movies[:20]:  # Show max 20 results
        year = movie['release_date'][:4] if movie['release_date'] else 'N/A'
        length = f"{movie['length']} min" if movie['length'] else 'N/A'
        user_rating = f"{movie['avg_user_rating']}/5 ({movie['rating_count']})" if movie['rating_count'] > 0 else 'Not rated'
        
        print(f"{movie['movie_id']:<8} {movie['title'][:40]:<40} {year:<6} {movie['mpaa_rating']:<6} {length:<8} {user_rating:<12}")
    
    print("-" * 120)
    
    if len(movies) > 20:
        print(f"\nShowing first 20 results of {len(movies)} total.")
    
    # Show additional info
    print("\nAdditional Information (first 5 movies):")
    for movie in movies[:5]:
        print(f"\n{movie['title']}:")
        print(f"  Cast: {movie['cast_members']}")
        print(f"  Directors: {movie['directors']}")
        print(f"  Studios: {movie['studios']}")
        print(f"  Genres: {movie['genres']}")

def display_movie_details(movie):
    """Display detailed information about a single movie"""
    print("\n" + "="*80)
    print(f"MOVIE DETAILS: {movie['title']}")
    print("="*80)
    print(f"Movie ID: {movie['movie_id']}")
    print(f"Release Date: {movie['release_date'] or 'N/A'}")
    print(f"Length: {movie['length']} minutes" if movie['length'] else "Length: N/A")
    print(f"MPAA Rating: {movie['mpaa_rating']}")
    print(f"User Rating: {movie['avg_rating']}/5.0 ({movie['rating_count']} ratings)")
    print(f"\nCast Members: {movie['cast_members']}")
    print(f"Directors: {movie['directors']}")
    print(f"Studios: {movie['studios']}")
    print(f"Genres: {movie['genres']}")
    print(f"Platforms: {movie['platforms']}")
    print("="*80)

def rate_watch_menu():
    """Rate and watch movies submenu"""
    while True:
        print("\n--- RATE/WATCH MOVIES ---")
        print("1. Rate a Movie")
        print("2. View My Ratings")
        print("3. Remove a Rating")
        print("4. View Top Rated Movies")
        print("5. Watch a Movie")
        print("6. Watch Collection")
        print("7. View Watch History")
        print("8. View Watch Statistics")
        print("9. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        match choice:
            case "1":
                rate_movie_menu()
            case "2":
                view_my_ratings()
            case "3":
                remove_rating_menu()
            case "4":
                view_top_rated()
            case "5":
                watch_movie_menu()
            case "6":
                watch_collection_menu()
            case "7":
                view_watch_history()
            case "8":
                view_watch_statistics()
            case "9":
                break
            case _:
                print("Invalid choice! Please try again.")

def rate_movie_menu():
    """Rate a movie"""
    print("\n--- RATE A MOVIE ---")
    
    # Option to search for a movie first
    search_choice = input("Would you like to search for a movie first? (y/n): ").lower()
    
    if search_choice == 'y':
        search_term = input("Enter movie title to search: ")
        success, movies = search_movies(cursor, search_term, 'title')
        
        if success and movies:
            print("\nSearch Results:")
            print("-" * 70)
            print(f"{'ID':<8} {'Title':<50} {'Year':<6}")
            print("-" * 70)
            for movie in movies[:10]:  # Show max 10 results
                year = movie['release_date'][:4] if movie['release_date'] else 'N/A'
                print(f"{movie['movie_id']:<8} {movie['title'][:50]:<50} {year:<6}")
            print("-" * 70)
        else:
            print("\nNo movies found!")
            input("\nPress Enter to continue...")
            return
    
    try:
        movie_id = int(input("\nEnter movie ID to rate: "))
        
        # Show current rating if exists
        success, current_rating = get_user_rating(cursor, current_user, movie_id)
        if success and current_rating:
            print(f"Your current rating: {current_rating} stars")
        
        rating = int(input("Enter your rating (1-5 stars): "))
        
        if 1 <= rating <= 5:
            success, message = rate_movie(cursor, conn, current_user, movie_id, rating)
            print(f"\n{message}")
        else:
            print("\nRating must be between 1 and 5!")
            
    except ValueError:
        print("\nInvalid input!")
    
    input("\nPress Enter to continue...")

def view_my_ratings():
    """View all user's ratings"""
    success, ratings = list_user_ratings(cursor, current_user)
    
    if success:
        if ratings:
            print("\nYour Movie Ratings:")
            print("-" * 80)
            print(f"{'ID':<8} {'Title':<40} {'Rating':<10} {'Release Year':<12}")
            print("-" * 80)
            
            for movie_id, title, star_rating, release_date in ratings:
                year = release_date[:4] if release_date else 'N/A'
                stars = '★' * star_rating + '☆' * (5 - star_rating)
                print(f"{movie_id:<8} {title[:40]:<40} {stars:<10} {year:<12}")
            
            print("-" * 80)
            print(f"\nTotal movies rated: {len(ratings)}")
            
            # Calculate average rating
            avg_rating = sum(r[2] for r in ratings) / len(ratings)
            print(f"Your average rating: {avg_rating:.1f} stars")
        else:
            print("\nYou haven't rated any movies yet.")
    else:
        print(f"\nError: {ratings}")
    
    input("\nPress Enter to continue...")

def remove_rating_menu():
    """Remove a rating"""
    # First show user's ratings
    success, ratings = list_user_ratings(cursor, current_user)
    
    if success and ratings:
        print("\nYour Movie Ratings:")
        print("-" * 70)
        for movie_id, title, star_rating, _ in ratings:
            stars = '★' * star_rating
            print(f"ID: {movie_id} - {title} ({stars})")
        print("-" * 70)
        
        try:
            movie_id = int(input("\nEnter movie ID to remove rating: "))
            confirm = input("Are you sure you want to remove this rating? (y/n): ").lower()
            
            if confirm == 'y':
                success, message = remove_rating(cursor, conn, current_user, movie_id)
                print(f"\n{message}")
            else:
                print("\nRating removal cancelled.")
        except ValueError:
            print("\nInvalid movie ID!")
    else:
        print("\nYou haven't rated any movies yet.")
    
    input("\nPress Enter to continue...")

def view_top_rated():
    """View top rated movies"""
    print("\n--- TOP RATED MOVIES ---")
    
    try:
        limit = int(input("How many top movies to show? (default: 10): ") or "10")
        success, movies = get_top_rated_movies(cursor, limit)
        
        if success:
            if movies:
                print(f"\nTop {limit} Rated Movies:")
                print("-" * 80)
                print(f"{'Rank':<6} {'ID':<8} {'Title':<40} {'Avg Rating':<12} {'# Ratings':<10}")
                print("-" * 80)
                
                for rank, (movie_id, title, avg_rating, rating_count) in enumerate(movies, 1):
                    stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
                    print(f"{rank:<6} {movie_id:<8} {title[:40]:<40} {avg_rating:.1f} {stars:<8} {rating_count:<10}")
                
                print("-" * 80)
            else:
                print("\nNo rated movies found.")
        else:
            print(f"\nError: {movies}")
            
    except ValueError:
        print("\nInvalid input! Using default of 10.")
        view_top_rated()
        return
    
    input("\nPress Enter to continue...")

def watch_movie_menu():
    print("\n--- WATCH A MOVIE ---")
    
    choice = input("1. Enter Movie ID\n2. Search for Movie\n3. View Recently Watched\n\nChoice: ")
    
    movie_id = None
    
    if choice == "2":
        search_term = input("Enter movie title to search: ")
        success, movies = search_movies(cursor, search_term, 'title')
        
        if success and movies:
            print("\nSearch Results:")
            print("-" * 70)
            print(f"{'ID':<8} {'Title':<50} {'Year':<6}")
            print("-" * 70)
            for movie in movies[:10]:
                year = movie['release_date'][:4] if movie['release_date'] else 'N/A'
                print(f"{movie['movie_id']:<8} {movie['title'][:50]:<50} {year:<6}")
            print("-" * 70)
        else:
            print("\nNo movies found!")
            input("\nPress Enter to continue...")
            return
            
    elif choice == "3":
        success, recent = get_recently_watched(cursor, current_user, 10)
        if success and recent:
            print("\nRecently Watched:")
            print("-" * 70)
            print(f"{'ID':<8} {'Title':<40} {'Last Watched':<20}")
            print("-" * 70)
            for movie_id_rec, title, mpaa, length, last_watched in recent:
                print(f"{movie_id_rec:<8} {title[:40]:<40} {last_watched.strftime('%Y-%m-%d %H:%M'):<20}")
            print("-" * 70)
        else:
            print("\nNo recently watched movies!")
            input("\nPress Enter to continue...")
            return
    
    try:
        if not movie_id:
            movie_id = int(input("\nEnter movie ID to watch: "))
        
        success, message = watch_movie(cursor, conn, current_user, movie_id)
        print(f"\n{message}")
        
    except ValueError:
        print("\nInvalid movie ID!")
    
    input("\nPress Enter to continue...")

def watch_collection_menu():
    success, collections = list_user_collections(cursor, current_user)
    
    if success and collections:
        print("\n--- WATCH COLLECTION ---")
        print("\nYour Collections:")
        for coll_id, coll_name in collections:
            print(f"ID: {coll_id} - {coll_name}")
        
        try:
            coll_id = int(input("\nEnter collection ID to watch: "))
            
            success, movies = list_movies_in_collection(cursor, coll_id)
            if success and movies:
                print(f"\nThis will mark {len(movies)} movies as watched:")
                for movie in movies[:5]:
                    print(f"  - {movie[1]}")
                if len(movies) > 5:
                    print(f"  ... and {len(movies) - 5} more")
                
                confirm = input("\nContinue? (y/n): ").lower()
                if confirm == 'y':
                    success, message = watch_collection(cursor, conn, current_user, coll_id)
                    print(f"\n{message}")
                else:
                    print("\nWatch cancelled.")
            else:
                print("\nNo movies in this collection!")
                
        except ValueError:
            print("\nInvalid collection ID!")
    else:
        print("\nNo collections found!")
    
    input("\nPress Enter to continue...")

def view_watch_history():
    print("\n--- WATCH HISTORY ---")
    
    limit = input("How many entries to show? (default: 20): ") or "20"
    try:
        limit = int(limit)
    except ValueError:
        limit = 20
    
    success, history = get_watch_history(cursor, current_user, limit)
    
    if success:
        if history:
            print(f"\nYour Recent Watch History (last {limit} entries):")
            print("-" * 90)
            print(f"{'ID':<8} {'Title':<35} {'Watched':<20} {'Length':<10} {'Rating':<8}")
            print("-" * 90)
            
            for movie_id, title, watch_time, length, mpaa in history:
                length_str = f"{length} min" if length else "N/A"
                print(f"{movie_id:<8} {title[:35]:<35} {watch_time.strftime('%Y-%m-%d %H:%M'):<20} {length_str:<10} {mpaa:<8}")
            
            print("-" * 90)
        else:
            print("\nNo watch history found!")
    else:
        print(f"\nError: {history}")
    
    input("\nPress Enter to continue...")

def view_watch_statistics():
    print("\n---WATCH STATISTICS---")
    
    success, stats = get_user_watch_stats(cursor, current_user)
    
    if success:
        print(f"\nYour Watch Statistics:")
        print("-" * 50)
        print(f"Unique Movies Watched: {stats['unique_movies']}")
        print(f"Total Views: {stats['total_watches']}")
        print(f"Total Watch Time: {stats['total_hours']} hours {stats['total_minutes'] % 60} minutes")
        print(f"Watches This Week: {stats['recent_watches']}")
        
        if stats['most_watched']:
            movie_id, title, count = stats['most_watched']
            print(f"\nMost Watched Movie:")
            print(f"  '{title}' - watched {count} times")
        
        if stats['total_watches'] > 0:
            cursor.execute("""
                SELECT MIN(WatchDateTime) 
                FROM Watches 
                WHERE Username = %s
            """, (current_user,))
            first_watch = cursor.fetchone()[0]
            
            if first_watch:
                days_since_first = (datetime.now() - first_watch).days + 1
                avg_per_day = stats['total_watches'] / days_since_first
                print(f"\nAverage watches per day: {avg_per_day:.2f}")
        
        print("-" * 50)
    else:
        print(f"\nError: {stats}")
    
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