CREATE DATABASE recommandations;

\c recommandations

CREATE SEQUENCE user_id_sequence START WITH 162542;

CREATE TABLE IF NOT EXISTS "Users" (
    "UserId" SERIAL PRIMARY KEY,
    "Username" VARCHAR(255) NOT NULL,
    "Password" VARCHAR(256) NOT NULL
);

ALTER TABLE "Users" ALTER COLUMN "UserId" SET DEFAULT nextval('user_id_sequence');

CREATE TABLE "Movies" (
    "MovieId" SERIAL PRIMARY KEY,
    "Title" VARCHAR(255),
    "Genres" VARCHAR(255),
    "Year" INTEGER,
    "Synopsis" TEXT,
    "Affiche" TEXT
);

CREATE TABLE "Ratings" (
    "UserId" INTEGER,
    "MovieId" INTEGER,
    "Rating" NUMERIC(2, 1),
    PRIMARY KEY ("UserId", "MovieId"),
    FOREIGN KEY ("UserId") REFERENCES "Users" ("UserId"),
    FOREIGN KEY ("MovieId") REFERENCES "Movies" ("MovieId")
);

\c recommandations

COPY "Movies" FROM '/root/db_sql.csv' DELIMITER ',' CSV HEADER;
