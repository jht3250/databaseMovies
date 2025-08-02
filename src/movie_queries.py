def search_movies(cursor, search_term, search_type='title'):
    try:
        base_query = """
            SELECT DISTINCT
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.Length,
                m.MMPA,
                STRING_AGG(DISTINCT p_actor.Name, ', ' ORDER BY p_actor.Name) as cast_members,
                STRING_AGG(DISTINCT p_dir.Name, ', ' ORDER BY p_dir.Name) as directors,
                STRING_AGG(DISTINCT s.Name, ', ' ORDER BY s.Name) as studios,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                AVG(r.StarRating) as avg_user_rating,
                COUNT(DISTINCT r.Username) as rating_count
            FROM MOVIES m
            LEFT JOIN Movie_Actor ma ON m.MovieID = ma.MovieID
            LEFT JOIN Person p_actor ON ma.PersonID = p_actor.PersonID
            LEFT JOIN Movie_Director md ON m.MovieID = md.MovieID
            LEFT JOIN Person p_dir ON md.PersonID = p_dir.PersonID
            LEFT JOIN Movie_Studio ms ON m.MovieID = ms.MovieID
            LEFT JOIN Studio s ON ms.StudioID = s.StudioID
            LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
        """
        where_clause = ""
        search_param = f"%{search_term}%"

        match search_type:
            case 'title':
                where_clause = "WHERE LOWER(m.Title) LIKE LOWER(%s)"
            case 'cast':
                where_clause = "WHERE m.MovieID IN (SELECT ma2.MovieID FROM Movie_Actor ma2 JOIN Person p2 ON ma2.PersonID = p2.PersonID WHERE LOWER(p2.Name) LIKE LOWER(%s))"
            case 'studio':
                where_clause = "WHERE m.MovieID IN (SELECT ms2.MovieID FROM Movie_Studio ms2 JOIN Studio s2 ON ms2.StudioID = s2.StudioID WHERE LOWER(s2.Name) LIKE LOWER(%s))"
            case 'genre':
                where_clause = "WHERE m.MovieID IN (SELECT mg2.MovieID FROM Movie_Genre mg2 JOIN Genre g2 ON mg2.GenreID = g2.GenreID WHERE LOWER(g2.Name) LIKE LOWER(%s))"
            case 'release_date':
                where_clause = "WHERE EXTRACT(YEAR FROM m.ReleaseDate)::VARCHAR(4) LIKE %s"
                search_param = f"%{search_term}%"
            
        group_by = """
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Length, m.MMPA ORDER BY m.Title ASC, m.ReleaseDate ASC
        """

        full_query = base_query + " " + where_clause + " " + group_by

        cursor.execute(full_query, (search_param,))
        results = cursor.fetchall()
        
        movies = []
        for row in results:
            movies.append({
                'movie_id': row[0],
                'title': row[1],
                'release_date': row[2],
                'length': row[3],
                'mpaa_rating': row[4],
                'cast_members': row[5] or 'N/A',
                'directors': row[6] or 'N/A',
                'studios': row[7] or 'N/A',
                'genres': row[8] or 'N/A',
                'avg_user_rating': round(row[9], 1) if row[9] else 0.0,
                'rating_count': row[10]
            })
        return True, movies
    except Exception as e:
        return False, f"Error searching movies: {e}"

def sort_movies(movies, sort_by='title', order='asc'):
    sort_keys = {
        'title': lambda x: x['title'].lower() if x['title'] else '',
        'studio': lambda x: x['studios'].lower() if x['studios'] else '',
        'genre': lambda x: x['genres'].lower() if x['genres'] else '',
        'year': lambda x: int(x['release_date'][:4]) if x['release_date'] and len(x['release_date']) >= 4 else 0
    }
    
    key_func = sort_keys.get(sort_by, sort_keys['title'])
    
    reverse = (order == 'desc')
    sorted_movies = sorted(movies, key=key_func, reverse=reverse)
    
    return sorted_movies

def get_movie_details(cursor, movie_id):
    try:
        query = """
            SELECT 
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.Length,
                m.MMPA,
                STRING_AGG(DISTINCT p_actor.Name, ', ' ORDER BY p_actor.Name) as cast_members,
                STRING_AGG(DISTINCT p_dir.Name, ', ' ORDER BY p_dir.Name) as directors,
                STRING_AGG(DISTINCT s.Name, ', ' ORDER BY s.Name) as studios,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                STRING_AGG(DISTINCT plat.Name || ' (' || EXTRACT(YEAR FROM mp.ReleaseDate)::VARCHAR(4) || ')', ', ' ORDER BY plat.Name) as platforms,
                AVG(r.StarRating) as avg_rating,
                COUNT(DISTINCT r.Username) as rating_count
            FROM MOVIES m
            LEFT JOIN Movie_Actor ma ON m.MovieID = ma.MovieID
            LEFT JOIN Person p_actor ON ma.PersonID = p_actor.PersonID
            LEFT JOIN Movie_Director md ON m.MovieID = md.MovieID
            LEFT JOIN Person p_dir ON md.PersonID = p_dir.PersonID
            LEFT JOIN Movie_Studio ms ON m.MovieID = ms.MovieID
            LEFT JOIN Studio s ON ms.StudioID = s.StudioID
            LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Movie_Platform mp ON m.MovieID = mp.MovieID
            LEFT JOIN Platform plat ON mp.PlatformID = plat.PlatformID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
            WHERE m.MovieID = %s
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Length, m.MMPA
        """
        
        cursor.execute(query, (movie_id,))
        result = cursor.fetchone()
        
        if result:
            movie = {
                'movie_id': result[0],
                'title': result[1],
                'release_date': result[2],
                'length': result[3],
                'mpaa_rating': result[4],
                'cast_members': result[5] or 'N/A',
                'directors': result[6] or 'N/A',
                'studios': result[7] or 'N/A',
                'genres': result[8] or 'N/A',
                'platforms': result[9] or 'N/A',
                'avg_rating': round(result[10], 1) if result[10] else 0.0,
                'rating_count': result[11]
            }
            return True, movie
        else:
            return False, "Movie not found"
    
    except Exception as e:
        return False, f"Error fetching movie details: {e}"

def search_movies_simple(cursor, search_term):
    try:
        query = """
            SELECT MovieID, Title, ReleaseDate, MMPA
            FROM MOVIES
            WHERE LOWER(Title) LIKE LOWER(%s)
            ORDER BY Title
            LIMIT 20
        """
        cursor.execute(query, (f"%{search_term}%",))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error searching movies: {e}"

def get_top_20_popular_movies(cursor):
    try:
        query = """
            SELECT m.title, COUNT(*) as "count"
            FROM watches w
            INNER JOIN movies m ON w.movieid = m.movieid
            WHERE w.watchdatetime >= now() - INTERVAL '90 days'
            GROUP BY m.title
            ORDER BY count DESC
            LIMIT 20
        """
        cursor.execute(query)
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching top 20 movies: {e}"

def get_top_10_watched_movies_from_user(cursor, username):
    try:
        query = """
            SELECT m.title, COUNT(*) as "count"
            FROM watches w
            INNER JOIN movies m ON w.movieid = m.movieid
            WHERE w.username = %s
            GROUP BY m.title
            ORDER BY count DESC
            LIMIT 10
        """
        cursor.execute(query, (username,))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching top 10 movies: {e}"

def get_top_10_highly_rated_movies_from_user(cursor, username):
    try:
        query = """
            SELECT m.title, r.starrating
            FROM rates r
            INNER JOIN movies m ON r.movieid = m.movieid
            WHERE r.username = %s
            ORDER BY r.starrating DESC
            LIMIT 10
        """
        cursor.execute(query, (username,))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching top 10 movies: {e}"

def get_top_20_popular_movies_from_followed(cursor, username):
    try:
        query = """
            SELECT followedusername
            FROM follows
            WHERE followerusername = %s
        """
        cursor.execute(query, (username,))
        users = cursor.fetchall()
        
        if not users:
            return True, []  
        
        followed_usernames = [user[0] for user in users]

        query = """
            SELECT m.title, COUNT(*) as watch_count
            FROM watches w
            INNER JOIN movies m ON w.movieid = m.movieid
            WHERE w.username = ANY(%s)
            GROUP BY m.title
            ORDER BY watch_count DESC
            LIMIT 20
        """
        
        cursor.execute(query, (followed_usernames,))
        movies = cursor.fetchall()
        
        return True, movies
    except Exception as e:
        return False, f"Error fetching top movies from followed users: {e}"
    
def get_top_5_new_releases_this_month(cursor):
    try:
        query = """
            SELECT DISTINCT
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.MMPA,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                AVG(r.StarRating) as avg_rating,
                COUNT(DISTINCT r.Username) as rating_count
            FROM MOVIES m
            LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
            WHERE EXTRACT(MONTH FROM m.ReleaseDate) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM m.ReleaseDate) = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.MMPA
            ORDER BY m.ReleaseDate DESC
            LIMIT 5
        """
        cursor.execute(query)
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching new releases: {e}"

def get_recommended_movies_for_user(cursor, username, limit=10):
    try:
        genre_preference_query = """
            WITH user_genre_stats AS (
                SELECT 
                    g.GenreID,
                    g.Name as genre_name,
                    COUNT(DISTINCT w.MovieID) as watch_count,
                    AVG(r.StarRating) as avg_rating
                FROM Watches w
                JOIN Movie_Genre mg ON w.MovieID = mg.MovieID
                JOIN Genre g ON mg.GenreID = g.GenreID
                LEFT JOIN Rates r ON w.MovieID = r.MovieID AND w.Username = r.Username
                WHERE w.Username = %s
                GROUP BY g.GenreID, g.Name
                ORDER BY watch_count DESC, avg_rating DESC
                LIMIT 3
            )
            SELECT GenreID, genre_name FROM user_genre_stats
        """
        
        cursor.execute(genre_preference_query, (username,))
        favorite_genres = cursor.fetchall()
        
        if not favorite_genres:
            return get_top_rated_movies_general(cursor, limit)
        
        genre_ids = [g[0] for g in favorite_genres]
        
        recommendation_query = """
            SELECT DISTINCT
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.Length,
                m.MMPA,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                AVG(r.StarRating) as avg_rating,
                COUNT(DISTINCT r.Username) as rating_count,
                COUNT(DISTINCT mg.GenreID) FILTER (WHERE mg.GenreID = ANY(%s)) as matching_genres
            FROM MOVIES m
            JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
            WHERE m.MovieID NOT IN (
                SELECT MovieID FROM Watches WHERE Username = %s
            )
            AND mg.GenreID = ANY(%s)
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Length, m.MMPA
            HAVING AVG(r.StarRating) >= 3.5 OR COUNT(r.Username) < 3
            ORDER BY 
                matching_genres DESC,
                avg_rating DESC NULLS LAST,
                rating_count DESC
            LIMIT %s
        """
        
        cursor.execute(recommendation_query, (genre_ids, username, genre_ids, limit))
        recommendations = cursor.fetchall()
        
        if len(recommendations) < limit:
            additional_query = """
                SELECT DISTINCT
                    m.MovieID,
                    m.Title,
                    m.ReleaseDate,
                    m.Length,
                    m.MMPA,
                    STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                    AVG(r.StarRating) as avg_rating,
                    COUNT(DISTINCT r.Username) as rating_count,
                    0 as matching_genres
                FROM MOVIES m
                LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
                LEFT JOIN Genre g ON mg.GenreID = g.GenreID
                LEFT JOIN Rates r ON m.MovieID = r.MovieID
                WHERE m.MovieID NOT IN (
                    SELECT MovieID FROM Watches WHERE Username = %s
                )
                AND m.MovieID NOT IN (%s)
                GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Length, m.MMPA
                HAVING COUNT(r.Username) >= 5 AND AVG(r.StarRating) >= 4.0
                ORDER BY avg_rating DESC, rating_count DESC
                LIMIT %s
            """
            
            existing_ids = [r[0] for r in recommendations] or [-1]
            cursor.execute(additional_query, (username, tuple(existing_ids), limit - len(recommendations)))
            additional = cursor.fetchall()
            recommendations.extend(additional)
        
        return True, recommendations
        
    except Exception as e:
        return False, f"Error getting recommendations: {e}"

def get_recommended_movies_collaborative(cursor, username, limit=10):
    try:
        similar_users_query = """
            WITH user_ratings AS (
                SELECT MovieID, StarRating
                FROM Rates
                WHERE Username = %s AND StarRating >= 4
            ),
            similar_users AS (
                SELECT 
                    r.Username,
                    COUNT(DISTINCT r.MovieID) as common_movies,
                    AVG(ABS(r.StarRating - ur.StarRating)) as rating_difference
                FROM Rates r
                JOIN user_ratings ur ON r.MovieID = ur.MovieID
                WHERE r.Username != %s
                    AND r.StarRating >= 4
                GROUP BY r.Username
                HAVING COUNT(DISTINCT r.MovieID) >= 3
                ORDER BY common_movies DESC, rating_difference ASC
                LIMIT 10
            )
            SELECT Username FROM similar_users
        """
        
        cursor.execute(similar_users_query, (username, username))
        similar_users = cursor.fetchall()
        
        if not similar_users:
            return get_recommended_movies_for_user(cursor, username, limit)
        
        similar_usernames = [u[0] for u in similar_users]

        collaborative_query = """
            SELECT 
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.Length,
                m.MMPA,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                AVG(r.StarRating) as avg_rating_all,
                COUNT(DISTINCT r.Username) as total_ratings,
                AVG(r.StarRating) FILTER (WHERE r.Username = ANY(%s)) as avg_rating_similar,
                COUNT(DISTINCT r.Username) FILTER (WHERE r.Username = ANY(%s)) as similar_user_ratings
            FROM MOVIES m
            LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
            WHERE m.MovieID NOT IN (
                SELECT MovieID FROM Watches WHERE Username = %s
            )
            AND m.MovieID IN (
                SELECT MovieID FROM Rates 
                WHERE Username = ANY(%s) AND StarRating >= 4
            )
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Length, m.MMPA
            ORDER BY 
                similar_user_ratings DESC,
                avg_rating_similar DESC,
                avg_rating_all DESC
            LIMIT %s
        """
        
        cursor.execute(collaborative_query, 
                      (similar_usernames, similar_usernames, username, similar_usernames, limit))
        recommendations = cursor.fetchall()
        
        return True, recommendations
        
    except Exception as e:
        return False, f"Error getting collaborative recommendations: {e}"

def get_top_rated_movies_general(cursor, limit=10):
    try:
        query = """
            SELECT 
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.Length,
                m.MMPA,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                AVG(r.StarRating) as avg_rating,
                COUNT(DISTINCT r.Username) as rating_count,
                0 as matching_genres
            FROM MOVIES m
            LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.Length, m.MMPA
            HAVING COUNT(r.Username) >= 5
            ORDER BY avg_rating DESC, rating_count DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching top rated movies: {e}"
    
def get_top_20_movies_last_90_days(cursor):
    """Get top 20 most watched movies in the last 90 days"""
    try:
        query = """
            SELECT 
                m.MovieID,
                m.Title,
                m.ReleaseDate,
                m.MMPA,
                COUNT(w.MovieID) as watch_count,
                COUNT(DISTINCT w.Username) as unique_viewers,
                STRING_AGG(DISTINCT g.Name, ', ' ORDER BY g.Name) as genres,
                AVG(r.StarRating) as avg_rating,
                COUNT(DISTINCT r.Username) as rating_count
            FROM Watches w
            INNER JOIN MOVIES m ON w.MovieID = m.MovieID
            LEFT JOIN Movie_Genre mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genre g ON mg.GenreID = g.GenreID
            LEFT JOIN Rates r ON m.MovieID = r.MovieID
            WHERE w.WatchDateTime >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY m.MovieID, m.Title, m.ReleaseDate, m.MMPA
            ORDER BY watch_count DESC, unique_viewers DESC
            LIMIT 20
        """
        cursor.execute(query)
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching top movies from last 90 days: {e}"
