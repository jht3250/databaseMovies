# social_queries.py
from datetime import datetime

def search_users_by_email(cursor, email_search, current_user):
    """Search for users by email (excluding current user)"""
    try:
        query = """
            SELECT 
                u.Username, 
                u.FirstName, 
                u.LastName,
                u.email,
                CASE 
                    WHEN f.FollowerUsername IS NOT NULL THEN TRUE 
                    ELSE FALSE 
                END as is_following
            FROM USERS u
            LEFT JOIN Follows f ON u.Username = f.FollowedUsername AND f.FollowerUsername = %s 
            WHERE LOWER(u.email) LIKE LOWER(%s) AND u.Username != %s
            ORDER BY u.Username
        """
        search_pattern = f"%{email_search}%"
        cursor.execute(query, (current_user, search_pattern, current_user))
        users = cursor.fetchall()
        return True, users
    except Exception as e:
        return False, f"Error searching users: {e}"

def follow_user(cursor, conn, follower_username, followed_username):
    """Follow another user"""
    try:
        cursor.execute("SELECT Username FROM USERS WHERE Username = %s", (followed_username,))
        if not cursor.fetchone():
            return False, "User not found!"
        
        if follower_username == followed_username:
            return False, "You cannot follow yourself!"
        
        query = """
            INSERT INTO Follows (FollowerUsername, FollowedUsername, FollowedDate) VALUES (%s, %s, %s)
        """
        cursor.execute(query, (follower_username, followed_username, datetime.now()))
        conn.commit()
        return True, f"You are now following {followed_username}!"
        
    except Exception as e:
        conn.rollback()
        if "duplicate key" in str(e).lower():
            return False, "You are already following this user!"
        return False, f"Error following user: {e}"

def unfollow_user(cursor, conn, follower_username, followed_username):
    """Unfollow a user"""
    try:
        query = """
            DELETE FROM Follows WHERE FollowerUsername = %s AND FollowedUsername = %s
        """
        cursor.execute(query, (follower_username, followed_username))
        
        if cursor.rowcount > 0:
            conn.commit()
            return True, f"You have unfollowed {followed_username}"
        else:
            return False, "You are not following this user!"
            
    except Exception as e:
        conn.rollback()
        return False, f"Error unfollowing user: {e}"

def get_followers(cursor, username):
    """Get list of users who follow this user"""
    try:
        query = """
            SELECT 
                f.FollowerUsername,
                u.FirstName,
                u.LastName,
                f.FollowedDate
            FROM Follows f
            JOIN USERS u ON f.FollowerUsername = u.Username WHERE f.FollowedUsername = %s
            ORDER BY f.FollowedDate DESC
        """
        cursor.execute(query, (username,))
        followers = cursor.fetchall()
        return True, followers
    except Exception as e:
        return False, f"Error fetching followers: {e}"

def get_following(cursor, username):
    """Get list of users this user follows"""
    try:
        query = """
            SELECT 
                f.FollowedUsername,
                u.FirstName,
                u.LastName,
                f.FollowedDate
            FROM Follows f
            JOIN USERS u ON f.FollowedUsername = u.Username WHERE f.FollowerUsername = %s
            ORDER BY f.FollowedDate DESC
        """
        cursor.execute(query, (username,))
        following = cursor.fetchall()
        return True, following
    except Exception as e:
        return False, f"Error fetching following list: {e}"

def get_following_activity(cursor, username, limit=20):
    """Get recent movie activity from users you follow"""
    try:
        query = """
            SELECT 
                w.Username,
                u.FirstName,
                u.LastName,
                m.Title,
                w.WatchDateTime,
                'watched' as activity_type
            FROM Follows f
            JOIN Watches w ON f.FollowedUsername = w.Username
            JOIN USERS u ON w.Username = u.Username
            JOIN MOVIES m ON w.MovieID = m.MovieID
            WHERE f.FollowerUsername = %s
            
            UNION ALL
            
            SELECT 
                r.Username,
                u.FirstName,
                u.LastName,
                m.Title,
                CURRENT_TIMESTAMP as activity_time,
                'rated ' || r.StarRating || ' stars' as activity_type
            FROM Follows f
            JOIN Rates r ON f.FollowedUsername = r.Username
            JOIN USERS u ON r.Username = u.Username
            JOIN MOVIES m ON r.MovieID = m.MovieID
            WHERE f.FollowerUsername = %s
            
            ORDER BY WatchDateTime DESC
            LIMIT %s
        """
        
        cursor.execute(query, (username, username, limit))
        activity = cursor.fetchall()
        return True, activity
    except Exception as e:
        return False, f"Error fetching activity: {e}"