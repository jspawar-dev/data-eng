# Imports

```
pip install requests
# Allows us to send HTTP requests

pip install beautifulsoup4
# Used for parsing HTML or XML to extract data.

pip install pandas
# Used for storing data to a .csv file

pip install psycopg2
# Used for storing data to a database.
```

# Files

**main.py** - Basic web scraper, gets all books on every page, Saves to .csv. No preprocessing, No saving to PostgreSQl

**commented.py** - Advanced web scraper, get all books on every page, preprocesses data before saving to .csv and PostgreSQL. (Fully commented to explain the logic and syntax)

**preprocessed.py** - Advanced web scraper, get all books on every page, preprocesses data before saving to .csv and PostgreSQL. (Same as commented.py but without extensive commenting)

**books.csv** - .csv file containing books scraped from amazon.
