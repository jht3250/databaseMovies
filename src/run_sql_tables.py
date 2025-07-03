from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import os
import psycopg2

def connect_and_setup():
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

    #Connect to SQL server
    conn = psycopg2.connect(
        database='csci320_movies',
        user=username,
        password=password,
        host='127.0.0.1',
        port=ssh_server.local_bind_port,
    )
    cursor = conn.cursor()

    with open('../database/tables.sql', 'r') as file:
        sql_script = file.read()

        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

    conn.commit()

    cursor.close()
    conn.close()


if __name__ == "__main__":
    connect_and_setup()
