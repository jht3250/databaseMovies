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
DROP TABLE IF EXISTS Movie_Actor;
DROP TABLE IF EXISTS Movie_Director;


CREATE TABLE MOVIES(
    MovieID         int PRIMARY KEY,
    ReleaseDate     VARCHAR(100),
    Length          int,
    Title           VARCHAR(100),
    MMPA            varchar(10)
);

CREATE TABLE USERS(
    FirstName       VARCHAR(100),
    LastName        VARCHAR(100),
    Username        VARCHAR(100) PRIMARY KEY UNIQUE,
    Password        VARCHAR(100) NOT NULL,
    LastAccessed    DATE
);

CREATE TABLE Collection(
    CollectionID    int PRIMARY KEY ,
    Username        VARCHAR(100) NOT NULL,
    CollectionName  VARCHAR(100)
);

CREATE TABLE Platform(
    PlatformID      int PRIMARY KEY,
    Name    VARCHAR(100) NOT NULL
);

CREATE TABLE Person(
    PersonID        int PRIMARY KEY,
    Name            VARCHAR(100) NOT NULL
);

CREATE TABLE Studio(
    StudioID        int PRIMARY KEY,
    Name            VARCHAR(100) NOT NULL
);

CREATE TABLE Genre(
    GenreID         int PRIMARY KEY,
    Name            VARCHAR(100) NOT NULL
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
    PlatformID         int NOT NULL
);

CREATE TABLE Movie_Actor(
    MovieID         int NOT NULL,
    PersonID         int NOT NULL
);

CREATE TABLE Movie_Director(
    MovieID         int NOT NULL,
    PersonID         int NOT NULL
);