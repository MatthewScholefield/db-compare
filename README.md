# Db Compare

*A small scale apples-to-oranges database benchmark*

Lots of real world database applicates don't actually require complex data
manipulation for the majority of all queries. Think logging in to a website,
listing content belonging to a user, etc. This is a simple benchmark to
compare database performance on small amounts of data (can fit in memory).

This tool also aims to compare apples to oranges by testing relational,
document-oriented, graph databases, and key value stores, all in the same
benchmark.

Currently this tool supports:

 - [MariaDB](https://mariadb.org/) (essentially [MySQL](https://www.mysql.com/))
 - [MongoDB](https://www.mongodb.com/)
 - [RedisGraph](https://oss.redislabs.com/redisgraph/)
 - [PostgreSQL](https://www.postgresql.org/)
 - [RukoDB](https://github.com/rukodb/ruko)

## Installation

Install via pip:

```bash
pip3 install git+https://github.com/MatthewScholefield/db-compare
```
## Usage

There are four stages ran by default:

 - `setup`: Starts the database server if not already running and create a fresh table
 - `insert`: Insert `-n` number of users into the table
 - `retrieve`: Retrieve `-t` number of randomly selected users by email
 - `cleanup`: Destroy the database table

You can use run specific stages or exclude specific stages with `--stage/-s`
and `--no-stage/-ns`. For example:

```bash
db-compare -s setup -s insert -n 1000 mariadb  # Sets up and inserts 1k users
db-compare -s retrieve -t 100 mariadb  # Retrieves 100 random users
db-compare -s insert -n 100 mariadb # Adds 100 more users
db-compare -s cleanup mariadb
db-compare -n 100 -t 10 mariadb  # Resets, creates 100 users, retrieves 10 users, cleans up
```
