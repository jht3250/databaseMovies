DROP TABLE IF EXISTS MOVIES;
DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS Collection;
DROP TABLE IF EXISTS Platform;
DROP TABLE IF EXISTS Person;
DROP TABLE IF EXISTS Studio;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Movie_Genre;
DROP TABLE IF EXISTS Movie_Studio;
DROP TABLE IF EXISTS Movie_Platform;
DROP TABLE IF EXISTS Movie_Person;

CREATE TABLE MOVIES(
    MovieID         int PRIMARY KEY,
    RelasedDate     VARCHAR(50),
    Length          int,
    Title           VARCHAR(50),
    MMPA            varchar(2)
);

CREATE TABLE USERS(
    FirstName       VARCHAR(50),
    LastName        VARCHAR(50),
    Username        VARCHAR(50) PRIMARY KEY UNIQUE,
    Password        VARCHAR(50) NOT NULL,
    LastAccessed    DATE
);

CREATE TABLE Collection(
    CollectionID    int PRIMARY KEY ,
    Username        VARCHAR(50) NOT NULL,
    CollectionName  VARCHAR(50)
);

CREATE TABLE Platform(
    PlatformID      int PRIMARY KEY,
    PlatformName    VARCHAR(50) NOT NULL
);

CREATE TABLE Person(
    PersonID        int PRIMARY KEY,
    Name            VARCHAR(50) NOT NULL
);

CREATE TABLE Studio(
    StudioID        int PRIMARY KEY,
    Name            VARCHAR(50) NOT NULL
);

CREATE TABLE Genre(
    GenreID         int PRIMARY KEY,
    Name            VARCHAR(50) NOT NULL
);

-- RELATIONSHIP TABLES

CREATE TABLE Movie_Genre(
    MovieID         int NOT NULL,
    GenreID         int NOT NULL
);

CREATE TABLE Movie_Studio(
    MovieID         int NOT NULL,
    StudioID        int NOT NULL
);

CREATE TABLE Movie_Platform(
    MovieID         int NOT NULL,
    GenreID         int NOT NULL
);

CREATE TABLE Movie_Person(
    MovieID         int NOT NULL,
    GenreID         int NOT NULL
);