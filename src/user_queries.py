import hashlib
from datetime import datetime

def hashpass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(cursor, conn, username, password, first_name, last_name):
    try:
        hashedpass = hashpass(password)
        curr_date = datetime.now().date()

        query = """
            INSERT INTO USERS (Username, Password, FirstName, LastName, LastAccessed) VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (username, hashedpass, first_name, last_name, curr_date))
        conn.commit()
        return True, "Account created!"
    except Exception as e:
        conn.rollback()
        return False, f"Error creating account: {e}"

def auth(cursor, conn, username, password):
    try:
        hashedpass = hashpass(password)

        query = "SELECT Username FROM USERS WHERE Username = %s AND Password = %s"
        cursor.execute(query, (username, hashedpass))
        result = cursor.fetchone()

        if result:
            query = "UPDATE USERS SET LastAccessed = %s WHERE Username = %s"
            cursor.execute(query, (datetime.now().date(), username))
            conn.commit()
            return True, "Login successful!"
        else:
            return False, "Invalid username or password"
    except Exception as e:
        conn.rollback()
        return False, f"Error during login: {e}"