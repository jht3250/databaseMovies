from datetime import datetime, timedelta

def watch_movie(cursor, conn, username, movie_id):
    try:
        cursor.execute("SELECT Title FROM MOVIES WHERE MovieID = %s", (movie_id,))
        movie = cursor.fetchone()
        if not movie:
            return False, "Movie not found!"
        
        query = """
            INSERT INTO Watches (Username, MovieID, WatchDateTime)
            VALUES (%s, %s, %s)
        """
        watch_time = datetime.now()
        cursor.execute(query, (username, movie_id, watch_time))
        conn.commit()
        
        return True, f"Recorded watch for '{movie[0]}' at {watch_time.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        conn.rollback()
        return False, f"Error recording watch: {e}"

def watch_collection(cursor, conn, username, collection_id):
    try:
        cursor.execute("""
            SELECT CollectionName 
            FROM Collection 
            WHERE CollectionID = %s AND Username = %s
        """, (collection_id, username))
        
        collection = cursor.fetchone()
        if not collection:
            return False, "Collection not found or you don't have permission!"
        
        cursor.execute("""
            SELECT m.MovieID, m.Title
            FROM MOVIES m
            JOIN Contains c ON m.MovieID = c.MovieID
            WHERE c.CollectionID = %s
        """, (collection_id,))
        
        movies = cursor.fetchall()
        if not movies:
            return False, "No movies in this collection!"
        
        watch_time = datetime.now()
        for movie_id, title in movies:
            query = """
                INSERT INTO Watches (Username, MovieID, WatchDateTime)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, movie_id, watch_time))
            watch_time = watch_time + timedelta(seconds=1)
        
        conn.commit()
        return True, f"Recorded watch for {len(movies)} movies from '{collection[0]}' collection"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error watching collection: {e}"

def get_watch_history(cursor, username, limit=50):
    try:
        query = """
            SELECT 
                w.MovieID,
                m.Title,
                w.WatchDateTime,
                m.Length,
                m.MMPA
            FROM Watches w
            JOIN MOVIES m ON w.MovieID = m.MovieID
            WHERE w.Username = %s
            ORDER BY w.WatchDateTime DESC
            LIMIT %s
        """
        cursor.execute(query, (username, limit))
        history = cursor.fetchall()
        return True, history
    except Exception as e:
        return False, f"Error fetching watch history: {e}"

def get_movie_watch_count(cursor, username, movie_id):
    try:
        query = """
            SELECT COUNT(*) 
            FROM Watches 
            WHERE Username = %s AND MovieID = %s
        """
        cursor.execute(query, (username, movie_id))
        count = cursor.fetchone()[0]
        return True, count
    except Exception as e:
        return False, f"Error fetching watch count: {e}"

def get_user_watch_stats(cursor, username):
    try:
        cursor.execute("""
            SELECT COUNT(DISTINCT MovieID) 
            FROM Watches 
            WHERE Username = %s
        """, (username,))
        unique_movies = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Watches 
            WHERE Username = %s
        """, (username,))
        total_watches = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COALESCE(SUM(m.Length), 0)
            FROM Watches w
            JOIN MOVIES m ON w.MovieID = m.MovieID
            WHERE w.Username = %s
        """, (username,))
        total_minutes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT m.MovieID, m.Title, COUNT(*) as watch_count
            FROM Watches w
            JOIN MOVIES m ON w.MovieID = m.MovieID
            WHERE w.Username = %s
            GROUP BY m.MovieID, m.Title
            ORDER BY watch_count DESC
            LIMIT 1
        """, (username,))
        most_watched = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM Watches
            WHERE Username = %s AND WatchDateTime >= %s
        """, (username, datetime.now() - timedelta(days=7)))
        recent_watches = cursor.fetchone()[0]
        
        stats = {
            'unique_movies': unique_movies,
            'total_watches': total_watches,
            'total_minutes': total_minutes,
            'total_hours': total_minutes // 60,
            'most_watched': most_watched,
            'recent_watches': recent_watches
        }
        
        return True, stats
    except Exception as e:
        return False, f"Error fetching watch stats: {e}"

def get_recently_watched(cursor, username, limit=10):
    try:
        query = """
            SELECT DISTINCT ON (m.MovieID)
                m.MovieID,
                m.Title,
                m.MMPA,
                m.Length,
                MAX(w.WatchDateTime) as last_watched
            FROM Watches w
            JOIN MOVIES m ON w.MovieID = m.MovieID
            WHERE w.Username = %s
            GROUP BY m.MovieID, m.Title, m.MMPA, m.Length
            ORDER BY m.MovieID, last_watched DESC
            LIMIT %s
        """
        
        cursor.execute(query, (username, limit))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching recently watched: {e}"

def get_watch_history_by_date(cursor, username, start_date, end_date):
    try:
        query = """
            SELECT 
                w.MovieID,
                m.Title,
                w.WatchDateTime,
                m.Length
            FROM Watches w
            JOIN MOVIES m ON w.MovieID = m.MovieID
            WHERE w.Username = %s 
                AND w.WatchDateTime >= %s 
                AND w.WatchDateTime <= %s
            ORDER BY w.WatchDateTime DESC
        """
        cursor.execute(query, (username, start_date, end_date))
        history = cursor.fetchall()
        return True, history
    except Exception as e:
        return False, f"Error fetching watch history by date: {e}"