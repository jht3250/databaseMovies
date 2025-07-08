from dotenv import load_dotenv
from psycopg2._psycopg import cursor
from sshtunnel import SSHTunnelForwarder
import os
import psycopg2

def connect_to_db():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    username = os.getenv("USER")
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

print("Connecting to DB")
conn, curs = connect_to_db()
print("Success!")

