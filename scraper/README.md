# pre requisite

pip install requests
- Used for making HTTP requests

pip install beautifulsoup4
- Used for parsing through HTML or XML.

pip install pandas
- Used for writing to a csv file.

pip install psycopg2
- Used for connecting to a database.

Install PostgreSQL on your machine.
Login Password used is '1234', adjust code to establish a connection if your password is different.

\c amazon - connects to the amazon database


# Files

main.py - Basic web scraper, gets all books on every page, Saves to .csv. No preprocessing, No saving to PostgreSQl
commented.py - Advanced web scraper, get all books on every page, preprocesses data before saving to .csv and PostgreSQL. (Fully commented to explain the logic and syntax)
preprocessed.py - Advanced web scraper, get all books on every page, preprocesses data before saving to .csv and PostgreSQL. (Same as commented.py but without extensive commenting)
books.csv - .csv file containing books scraped from amazon.
