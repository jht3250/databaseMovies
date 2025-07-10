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
                where_clause = "WHERE m.ReleaseDate LIKE %s"
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
                STRING_AGG(DISTINCT plat.Name || ' (' || mp.ReleaseDate || ')', ', ' ORDER BY plat.Name) as platforms,
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