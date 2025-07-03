DROP TABLE IF EXISTS MOVIES;
DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS Collection;
DROP TABLE IF EXISTS Platform;
DROP TABLE IF EXISTS Person;
DROP TABLE IF EXISTS Studio;
DROP TABLE IF EXISTS Genre;

CREATE TABLE MOVIES(
    MovieID         int PRIMARY KEY,
    Length          int,
    Title           VARCHAR(50),
    MPAARating      varchar(2),
);

CREATE TABLE USERS(
    FirstName       VARCHAR(20),
    LastName        VARCHAR(20),
    Username        VARCHAR(20) PRIMARY KEY UNIQUE,
    Password        VARCHAR(20) NOT NULL,
    LastAccessed    DATE
);

CREATE TABLE Collection(
    CollectionID    int PRIMARY KEY,
    Username        VARCHAR(20) NOT NULL,
    CollectionName  VARCHAR(20)
);

CREATE TABLE Platform(
    PlatformID      int PRIMARY KEY,
    PlatformName    VARCHAR(20) NOT NULL
);

CREATE TABLE Person(
    PersonID        int PRIMARY KEY,
    Name            VARCHAR(20) NOT NULL
)

CREATE TABLE Studio(
    StudioID        int PRIMARY KEY,
    Name            VARCHAR(20) NOT NULL,
)

CREATE TABLE Genre(
    GenreID         int PRIMARY KEY,
    Name            VARCHAR(20) NOT NULL,
)