def create_collection(cursor, conn, username, collection_name):
    try:
        query = """
            SELECT MAX(CollectionID) FROM Collection WHERE username = %s
        """
        cursor.execute(query, (username,))
        max_id = cursor.fetchone()[0]
        if max_id is None:
            new_id = 1 
        else:
            max_id = max_id + 1
        
        query = """
            INSERT INTO Collection (CollectionID, Username, CollectionName) VALUES (%s, %s, %s)
        """
        if max_id is None:
            cursor.execute(query, (new_id, username, collection_name))
        else:
            cursor.execute(query, (max_id, username, collection_name))
        conn.commit()
        return True, "Collection created!"
    except Exception as e:
        conn.rollback()
        return False, f"Erorr creating collection: {e}"

def list_user_collections(cursor, username):
    try:
        query = """
            SELECT CollectionID, CollectionName FROM Collection WHERE Username = %s ORDER BY CollectionName ASC
        """
        cursor.execute(query, (username,))
        collections = cursor.fetchall()
        return True, collections
    except Exception as e:
        return False, f"Error fetching collections: {e}"
    
def rename_collection(cursor, conn, collection_id, new_name):
    try:
        query = """
            UPDATE Collection SET CollectionName = %s WHERE CollectionID = %s
        """
        cursor.execute(query, (new_name, collection_id))
        conn.commit()
        return True, "Collection renamed!"
    except Exception as e:
        conn.rollback()
        return False, f"Error deleting collection: {e}"
    
def delete_collection(cursor, conn, collection_id):
    try:
        query = "DELETE FROM Collection WHERE CollectionID = %s"
        cursor.execute(query, (collection_id,))
        conn.commit()
        return True, "Collection deleted!"
    except Exception as e:
        conn.rollback()
        return False, f"Error deleting collection: {e}"

def get_collection_stats(cursor, username):
    try:
        query = """
            SELECT
                c.CollectionID,
                c.CollectionName,
                COUNT(ct.MovieID) as movie_count,
                COALESCE(SUM(m.Length), 0) as total_runtime
            FROM Collection c
            LEFT JOIN Contains ct ON c.CollectionID = ct.CollectionID AND c.username = ct.username
            LEFT JOIN MOVIES m ON ct.MovieID = m.MovieID where c.username = %s
            GROUP BY c.CollectionID, c.CollectionName, c.username
            ORDER BY c.CollectionName ASC
        """
        cursor.execute(query, (username,))
        results = cursor.fetchall()
        
        stats = []
        for row in results:
            hours = row[3] // 60
            minutes = row[3] % 60
            stats.append({
                'id': row[0],
                'name': row[1],
                'movie_count': row[2],
                'total_runtime': row[3],
                'runtime_formatted': f"{hours}h {minutes}m"
            })
        
        return True, stats
    except Exception as e:
        return False, f"Error fetching collection stats: {e}"
    
def add_movie_to_collection(cursor, conn, collection_id, username, movie_id):
    try:
        query = """
            INSERT INTO Contains (CollectionID, username, MovieID) VALUES (%s, %s, %s)
        """
        cursor.execute(query, (collection_id, username, movie_id))
        conn.commit()
        return True, "Movie added to collection!"
    except Exception as e:
        conn.rollback()
        return False, f"Error adding movie: {e}"
    
def remove_movie_from_collection(cursor, conn, collection_id, movie_id):
    try:
        query = """
            DELETE FROM Contains WHERE CollectionID = %s AND MovieID = %s
        """
        cursor.execute(query, (collection_id, movie_id))

        if cursor.rowcount > 0:
            conn.commit()
            return True, "Movie removed from collection!"
        else: 
            return False, "Movie not found in collection!"
    except Exception as e:
        conn.rollback()
        return False, f"Erorr removing movie: {e}"

def list_movies_in_collection(cursor, collection_id, username):
    try:
        query = """
            SELECT m.MovieID, m.Title, m.Length, m.MMPA FROM MOVIES m 
            JOIN Contains c ON m.MovieID = c.MovieID WHERE c.CollectionID = %s AND username = %s
            ORDER BY m.Title
        """
        cursor.execute(query, (collection_id, username))
        movies = cursor.fetchall()
        return True, movies
    except Exception as e:
        return False, f"Error fetching movies: {e}"
    
def collection_auth(cursor, username, collection_id):
    try:
        query = """
            SELECT CollectionID 
            FROM Collection 
            WHERE CollectionID = %s AND Username = %s
        """
        cursor.execute(query, (collection_id, username))
        result = cursor.fetchone()
        return result is not None
    except:
        return False