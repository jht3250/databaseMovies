def rate_movie(cursor, conn, username, movie_id, star_rating):
    try:
        cursor.execute("SELECT MovieID FROM MOVIES WHERE MovieID = %s", (movie_id,))
        if not cursor.fetchone():
            return False, "Movie not found!"
        
        query = """
            INSERT INTO Rates (Username, MovieID, StarRating)
            VALUES (%s, %s, %s)
            ON CONFLICT (Username, MovieID) 
            DO UPDATE SET StarRating = %s
        """
        cursor.execute(query, (username, movie_id, star_rating, star_rating))
        conn.commit()
        return True, f"Movie rated {star_rating} stars!"
    except Exception as e:
        conn.rollback()
        return False, f"Error rating movie: {e}"

def get_user_rating(cursor, username, movie_id):
    try:
        query = """
            SELECT StarRating 
            FROM Rates 
            WHERE Username = %s AND MovieID = %s
        """
        cursor.execute(query, (username, movie_id))
        result = cursor.fetchone()
        if result:
            return True, result[0]
        else:
            return True, None 
    except Exception as e:
        return False, f"Error fetching rating: {e}"

def get_movie_average_rating(cursor, movie_id):
    try:
        query = """
            SELECT AVG(StarRating), COUNT(*) 
            FROM Rates 
            WHERE MovieID = %s
        """
        cursor.execute(query, (movie_id,))
        result = cursor.fetchone()
        if result[0]:
            return True, {'average': round(result[0], 1), 'count': result[1]}
        else:
            return True, {'average': 0.0, 'count': 0}
    except Exception as e:
        return False, f"Error fetching average rating: {e}"

def list_user_ratings(cursor, username):
    try:
        query = """
            SELECT r.MovieID, m.Title, r.StarRating, m.ReleaseDate
            FROM Rates r
            JOIN MOVIES m ON r.MovieID = m.MovieID
            WHERE r.Username = %s
            ORDER BY r.StarRating DESC, m.Title ASC
        """
        cursor.execute(query, (username,))
        ratings = cursor.fetchall()
        return True, ratings
    except Exception as e:
        return False, f"Error fetching user ratings: {e}"

def remove_rating(cursor, conn, username, movie_id):
    try:
        query = """
            DELETE FROM Rates 
            WHERE Username = %s AND MovieID = %s
        """
        cursor.execute(query, (username, movie_id))
        
        if cursor.rowcount > 0:
            conn.commit()
            return True, "Rating removed!"
        else:
            return False, "No rating found for this movie!"
    except Exception as e:
        conn.rollback()
        return False, f"Error removing rating: {e}"

def get_top_rated_movies(cursor, limit=10):
    try:
        query = """
            SELECT 
                m.MovieID, 
                m.Title, 
                AVG(r.StarRating) as avg_rating,
                COUNT(r.StarRating) as rating_count
            FROM MOVIES m
            JOIN Rates r ON m.MovieID = r.MovieID
            GROUP BY m.MovieID, m.Title
            HAVING COUNT(r.StarRating) >= 3
            ORDER BY avg_rating DESC, rating_count DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching top rated movies: {e}"