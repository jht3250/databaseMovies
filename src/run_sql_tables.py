from dotenv import load_dotenv
from psycopg2._psycopg import cursor
from sshtunnel import SSHTunnelForwarder
import os
import psycopg2
import csv
import ast

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
    title = title.replace("'", "''")
    query = f"INSERT INTO movies (MovieID, Title, Length, MMPA, ReleaseDate) VALUES ({movieID}, '{title}', {runtime}, '{mmpa}', {releasedDate});"
    return query

def insert_two_int_values(table, var1, var2, value1, value2):
    query = f"INSERT INTO {table} ({var1}, {var2}) VALUES ({value1}, {value2});"
    return query

def insert_two_values_with_str(table, var1, var2, value1, value2):
    value2 = value2.replace("'", "''")
    if isinstance(value2, str):
        value2 = f"'{value2}'"
    query = f"INSERT INTO {table} ({var1}, {var2}) VALUES ({value1}, {value2}) ON CONFLICT DO NOTHING;"
    return query

def mass_movie_insert():
    conn, cursor = connect_to_db()
    query = ""

    with open('../data/tmdb_5000_movies.csv', 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader)

        for line in csv_reader:
            movieID = line[1]
            if movieID == '' or movieID is None:
                continue
            title = line[6]
            runtime = line[5]
            release_date = line[4]
            platform = line[-1]
            mmpa = line[-2]
            genre = line[0] #THIS IS A LIST OF DICTIONARY {ID:0 , Name'adventure'}
            studio = line[3]    ##LIST OF studios {name: 'FOX', id:0}

            print(title, runtime, mmpa, release_date)

            query += insert_movie(movieID, title, runtime, mmpa, release_date)

            genre = ast.literal_eval(genre)
            for genreDict in genre:
                genreID = genreDict['id']
                genreName = genreDict['name']
                query += insert_two_values_with_str('Genre', 'GenreID', 'Name', genreID, genreName)
                query += insert_two_int_values('Movie_Genre', 'MovieID', 'GenreID', movieID, genreID)

            studio = ast.literal_eval(studio)
            for studioDict in studio:
                studioID = studioDict['id']
                studioName = studioDict['name']
                query += insert_two_values_with_str('Studio', 'StudioID', 'Name', studioID, studioName)
                query += insert_two_int_values('Movie_Studio', 'MovieID', 'StudioID', movieID, studioID)
            platform = ast.literal_eval(platform)
            query += insert_two_values_with_str('Platform', 'PlatformID', 'Name', platform['id'], platform['name'])
            query += insert_two_int_values('Movie_Platform', 'MovieID', 'PlatformID', movieID, platform['id'])

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()



def insert_person(id, name):
    name = name.replace("'", "''")
    query = f"INSERT INTO Person (PersonID, name) VALUES ({id}, '{name}') ON CONFLICT DO NOTHING;"
    return query

def insert_movie_person_director(table, movieID, personID):
    query = f"INSERT INTO {table} (MovieID, PersonID) VALUES ({movieID}, {personID});"
    return query

def mass_actor_insert():
    conn, cursor = connect_to_db()
    query = ""

    with open('../data/tmdb_5000_credits.csv', 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader)

        for line in csv_reader:
            movieID = line[0]
            title = line[1]
            cast = line[2]
            crew = line[3]

            cast = ast.literal_eval(cast)
            crew = ast.literal_eval(crew)
            if len(cast) > 3:
                cast = cast[:3]
            for castDict in cast:
                castID = castDict['id']
                name = castDict['name']
                query += insert_person(castID, name)
                query += insert_movie_person_director('Movie_Actor', movieID, castID)
                print(name, 'Actor')
            for crewDict in crew:
                if crewDict['job'] == 'Director':
                    crewID = crewDict['id']
                    name = crewDict['name']
                    query +=insert_person(crewID, name)
                    query += insert_movie_person_director('Movie_Director', movieID, crewID)
                    print(name, 'Director')

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    connect_and_setup()
    mass_movie_insert()
    mass_actor_insert()
