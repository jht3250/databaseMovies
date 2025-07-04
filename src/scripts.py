import pandas as pd
import random

def add_rating_to_csv():
    Ratings = ["G", "PG", "PG-13", "R"]
    ratings_lists = []

    with open("../data/tmdb_5000_movies.csv", "r") as file:
        sql_script = file.read()

        for line in sql_script.split("\n"):
            ratings_lists.append(random.choice(Ratings))

        ratings_lists = ratings_lists[:4803]
        #Pandas insert column
        df = pd.read_csv("../data/tmdb_5000_movies.csv")
        df["MMPA Rating"] = ratings_lists

        df.to_csv("../data/tmdb_5000_movies.csv", index=False)

def add_platform_to_csv():
    Studio = [
        {"name": "Netflix", "id":0},
        {"name": "Hulu", "id":1},
        {"name": "HBO Max", "id":2},
        {"name": "Tubi", "id":3},
        {"name": "Apple TV", "id":4},
        {"name": "Disney Plus", "id":5},
        {"name": "Prime Video", "id":6}]
    studio_lists = []

    with open("../data/tmdb_5000_movies.csv", "r") as file:
        sql_script = file.read()

        for line in sql_script.split("\n"):
            studio_lists.append(random.choice(Studio))

        ratings_lists = studio_lists[:4803]
        # Pandas insert column
        df = pd.read_csv("../data/tmdb_5000_movies.csv")
        df["Platform"] = ratings_lists

        df.to_csv("../data/tmdb_5000_movies.csv", index=False)

add_rating_to_csv()
add_platform_to_csv()