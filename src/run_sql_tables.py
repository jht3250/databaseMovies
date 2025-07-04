from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import os
import psycopg2

def connect_to_db():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    ssh_server = SSHTunnelForwarder(
        ('starbug.cs.rit.edu', 22),
        ssh_username=username,
        ssh_password=password,
        remote_bind_address=("127.0.0.1", 5432),
    )
    ssh_server.start()

    # Connect to SQL server
    conn = psycopg2.connect(
        database='csci320_movies',
        user=username,
        password=password,
        host='127.0.0.1',
        port=ssh_server.local_bind_port,
    )
    cursor = conn.cursor()
    return conn, cursor

def connect_and_setup():

    conn, cursor = connect_to_db()

    with open('../database/tables.sql', 'r') as file:
        sql_script = file.read()

        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

    conn.commit()

    cursor.close()
    conn.close()

def insert_movie(movieID, title, runtime, mmpa, releasedDate):
    conn, cursor = connect_to_db()
    print(movieID)
    query = f"INSERT INTO movies (MovieID, Title, Length, MMPA, ReleasedDate) VALUES ({movieID}, {title}, {runtime}, {mmpa}, {releasedDate})"
    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()

def insert_two_values(table, var1, var2, value1, value2):
    conn, cursor = connect_to_db()
    query = f"INSERT INTO {table} ({var1}, {var2}) VALUES ({value1}, {value2})"
    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()

def mass_movie_insert():
    with open('../data/tmdb_5000_movies.csv', 'r') as file:
        sql_script = file.read()

        for line in sql_script.split('\n')[1:]:
            splitted = line.split(',')
            print(line)
            movieID = splitted[1]
            title = splitted[6]
            runtime = splitted[5]
            release_date = splitted[4]
            platform = splitted[-1]
            mmpa = splitted[-2]
            genre = splitted[0] #THIS IS A LIST OF DICTIONARY {ID:0 , Name'adventure'}
            studio = splitted[3]    ##LIST OF studios {name: 'FOX', id:0}

            insert_movie(movieID, title, runtime, mmpa, release_date)
            for genreID, genreName in genre:
                insert_two_values('Genre', 'GenreID', 'Name', genreID, genreName)
                insert_two_values('Movie_Genre', 'MovieID', 'GenreID', movieID, genreID)
            for studioName, studioID in studio:
                insert_two_values('Studio', 'StudioID', 'Name', studioID, studioName)
                insert_two_values('Movie_Studio', 'MovieID', 'StudioID', movieID, studioID)
            insert_two_values('Platform', 'PlatformID', 'Name', platform['id'], platform['name'])
            insert_two_values('Movie_Platform', 'MovieID', 'PlatformID', movieID, platform['id'])






if __name__ == "__main__":
    connect_and_setup()
    mass_movie_insert()
