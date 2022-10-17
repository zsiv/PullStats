/*
prep_db.sql - Schema prep script for PullStats project
N. Schatz - 10/16/22
Version 1

--

Changelog:

10/16/22 - Initial script

--

To do:

- add tables for game data
*/

-- create db
-- option 1 - use 'createdb' command from a machine with psql installed, then connect to that db:
--    'createdb -U pullstatsadmin -h <rds hostname here> -p 5432 PullStats' (will prompt for password)
--    'psql -U pullstatsadmin -d PullStats -h <rds hostname here> -p 5432' (will prompt for password again)
-- option 2 - create db in psql with CREATE DATABASE command, then switch to it with \c
--    'CREATE DATABASE PullStats;'


-- run this script to create table/cols
CREATE TABLE IF NOT EXISTS gameindex (
    gamePk    INT PRIMARY KEY NOT NULL,
    gameDate  VARCHAR(50) NOT NULL
);

-- place an index on gameDate col
CREATE INDEX ix_gameDate
ON gameindex (gameDate);